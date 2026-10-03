from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .yolo import read_yolo_file

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def audit_dataset(dataset_root: str | Path) -> dict[str, Any]:
    root = Path(dataset_root)
    if not root.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {root}")

    images = sorted(path for path in root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)
    label_files = sorted(root.rglob("*.txt"))
    image_stems = {path.stem for path in images}
    label_stems = {path.stem for path in label_files}
    class_counts: Counter[int] = Counter()
    resolutions: Counter[str] = Counter()
    invalid_images: list[dict[str, str]] = []
    invalid_labels: list[dict[str, str]] = []
    file_hashes: Counter[str] = Counter()

    for image_path in images:
        try:
            with Image.open(image_path) as image:
                image.verify()
            with Image.open(image_path) as image:
                resolutions[f"{image.width}x{image.height}"] += 1
            file_hashes[sha256_file(image_path)] += 1
        except (OSError, UnidentifiedImageError) as exc:
            invalid_images.append({"file": str(image_path.relative_to(root)), "error": str(exc)})

    for label_path in label_files:
        try:
            for annotation in read_yolo_file(label_path):
                class_counts[annotation.class_id] += 1
        except Exception as exc:  # keep auditing other files and report all failures
            invalid_labels.append({"file": str(label_path.relative_to(root)), "error": str(exc)})

    duplicate_groups = sum(count - 1 for count in file_hashes.values() if count > 1)
    return {
        "dataset_root": str(root),
        "image_count": len(images),
        "label_file_count": len(label_files),
        "annotation_count_by_class_id": dict(sorted(class_counts.items())),
        "resolution_counts": dict(resolutions.most_common()),
        "missing_label_stems": sorted(image_stems - label_stems)[:500],
        "orphan_label_stems": sorted(label_stems - image_stems)[:500],
        "invalid_images": invalid_images,
        "invalid_labels": invalid_labels,
        "duplicate_file_copies": duplicate_groups,
        "notes": [
            "Stem-based pairing is only a structural signal; review duplicate "
            "filenames across folders.",
            "Near-duplicate and video-group leakage require manifest metadata "
            "and a dedicated review.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a YOLO-style dataset without mutating it")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = audit_dataset(args.dataset)
    write_json(args.output, report)
    print(f"Audit written to {args.output}; images={report['image_count']}")
    return 1 if report["invalid_images"] or report["invalid_labels"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
