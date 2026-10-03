from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from statistics import fmean
from typing import Any

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .source_layout import (
    SourceLayout,
    is_label,
    load_source_names,
    validate_output,
    validate_source_names,
)
from .yolo import read_yolo_file


def size_summary(values: list[float]) -> dict[str, float | int | None]:
    return {
        "count": len(values),
        "min": min(values) if values else None,
        "max": max(values) if values else None,
        "mean": fmean(values) if values else None,
    }


def audit_dataset(
    dataset_root: str | Path,
    *,
    images_dir: str,
    labels_dir: str,
    source_names: dict[int, str],
) -> dict[str, Any]:
    validate_source_names(source_names)
    layout = SourceLayout.create(dataset_root, images_dir, labels_dir)
    images, labels = layout.inventory()

    def relative(path: Path) -> str:
        return path.relative_to(layout.root).as_posix()

    report: dict[str, Any] = {
        "schema_version": 2,
        "dataset_root": str(layout.root),
        "source_layout": {
            "images": images_dir,
            "labels": labels_dir,
            "pairing": "exact relative path without extension; case-sensitive",
        },
        "source_names": source_names,
        "image_count": sum(map(len, images.values())),
        "label_file_count": sum(map(len, labels.values())),
        "ignored_metadata": sorted(
            relative(p)
            for p in layout.labels.rglob("*")
            if p.is_file() and p.suffix.lower() == ".txt" and not is_label(p)
        ),
        "missing_labels": [
            relative(p) for k in sorted(images.keys() - labels.keys()) for p in images[k]
        ],
        "orphan_labels": [
            relative(p) for k in sorted(labels.keys() - images.keys()) for p in labels[k]
        ],
        "ambiguous_pairs": [
            {
                "key": k,
                "images": [relative(p) for p in images.get(k, [])],
                "labels": [relative(p) for p in labels.get(k, [])],
            }
            for k in sorted(images.keys() | labels.keys())
            if len(images.get(k, [])) > 1 or len(labels.get(k, [])) > 1
        ],
        "invalid_images": [],
        "invalid_labels": [],
        "empty_label_files": [],
        "samples": [],
        "checks": {
            "automatic": [
                "relative_path_pairing",
                "image_decode",
                "yolo_geometry",
                "allowed_source_class_ids",
                "bbox_sizes",
                "exact_file_sha256",
            ],
            "not_checked": [
                "near_duplicates",
                "group_or_split_leakage",
                "label_semantics",
                "annotation_completeness",
                "license_consent",
                "canonical_mapping",
            ],
            "human_review_required": [
                "bbox alignment and annotation unit",
                "wrong/missing labels",
                "source class semantics and proposed canonical mapping",
                "empty labels really indicate no annotated objects",
                "near duplicates, provenance and group metadata",
            ],
        },
        "statistics_scope": {
            "classes_and_normalized_boxes": "all fully valid label files, including orphan labels",
            "pixel_boxes": "unique pairs with a decodable image and fully valid labels",
            "exact_duplicates": "identical file bytes (also corrupt files); not pixels",
        },
    }
    hashes: dict[str, list[str]] = defaultdict(list)
    dimensions: dict[Path, tuple[int, int]] = {}
    resolutions: Counter[str] = Counter()
    for paths in images.values():
        for path in paths:
            try:
                hashes[sha256_file(path)].append(relative(path))
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    image.load()
                    dimensions[path] = image.size
                    resolutions[f"{image.width}x{image.height}"] += 1
            except (OSError, ValueError, Image.DecompressionBombError) as exc:
                report["invalid_images"].append({"file": relative(path), "error": str(exc)})

    counts: Counter[int] = Counter({key: 0 for key in source_names})
    sizes: dict[str, list[float]] = {
        key: []
        for key in (
            "width_normalized",
            "height_normalized",
            "area_normalized",
            "width_pixels",
            "height_pixels",
            "area_pixels",
        )
    }
    for key, paths in labels.items():
        for path in paths:
            try:
                annotations = read_yolo_file(path, set(source_names))
            except (DataContractError, OSError, UnicodeError) as exc:
                report["invalid_labels"].append({"file": relative(path), "error": str(exc)})
                continue
            if not annotations:
                report["empty_label_files"].append(relative(path))
            for box in annotations:
                counts[box.class_id] += 1
                sizes["width_normalized"].append(box.width)
                sizes["height_normalized"].append(box.height)
                sizes["area_normalized"].append(box.width * box.height)
            paired = images.get(key, [])
            if len(paired) != 1 or len(paths) != 1 or paired[0] not in dimensions:
                continue
            width, height = dimensions[paired[0]]
            for box in annotations:
                sizes["width_pixels"].append(box.width * width)
                sizes["height_pixels"].append(box.height * height)
                sizes["area_pixels"].append(box.width * width * box.height * height)
            report["samples"].append(
                {
                    "image": relative(paired[0]),
                    "label": relative(path),
                    "width": width,
                    "height": height,
                    "annotations": [asdict(box) for box in annotations],
                }
            )

    report["annotation_count_by_class_id"] = dict(sorted(counts.items()))
    report["resolution_counts"] = dict(sorted(resolutions.items()))
    report["bbox_sizes"] = {key: size_summary(values) for key, values in sizes.items()}
    report["exact_duplicate_groups"] = [
        {"sha256": digest, "files": sorted(files)}
        for digest, files in sorted(hashes.items())
        if len(files) > 1
    ]
    report["duplicate_file_copies"] = sum(
        len(g["files"]) - 1 for g in report["exact_duplicate_groups"]
    )
    report["errors"] = []
    if not images:
        report["errors"].append("No images found")
    if not labels:
        report["errors"].append("No label files found (empty label files are valid)")
    report["has_errors"] = bool(
        report["errors"]
        or any(
            report[field]
            for field in (
                "missing_labels",
                "orphan_labels",
                "ambiguous_pairs",
                "invalid_images",
                "invalid_labels",
            )
        )
    )
    return report


def add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--images", required=True, help="Image subtree relative to dataset root")
    parser.add_argument("--labels", required=True, help="Label subtree relative to dataset root")
    parser.add_argument(
        "--source-names", required=True, help="JSON ID/name object or YAML names mapping"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only YOLO source audit; no dataset approval")
    add_source_arguments(parser)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        output = validate_output(args.output, Path(args.dataset).resolve())
        report = audit_dataset(
            args.dataset,
            images_dir=args.images,
            labels_dir=args.labels,
            source_names=load_source_names(args.source_names),
        )
        write_json(output, report)
    except (DataContractError, OSError, ValueError) as exc:
        parser.exit(2, f"Audit input/output error: {exc}\n")
    print(f"Audit written to {output}; images={report['image_count']}")
    return int(report["has_errors"])


if __name__ == "__main__":
    raise SystemExit(main())
