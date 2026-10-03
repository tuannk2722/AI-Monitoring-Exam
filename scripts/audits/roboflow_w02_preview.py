"""Owner-authorized W02 geometry preview only; never a canonical dataset build."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from ai_exam_monitoring.data.overlay import export_overlays
from ai_exam_monitoring.data.yolo import YoloAnnotation

ARCHIVE_SHA256 = "70060bfe7d65dedcca6a72aaac423c95f402369eec08563b24ae8d962e666eed"
STEM = "20220525_171742_jpg.rf.a0e7341937542f69dd48b4b086258c2d"
EXPECTED = "0 0.9547836538461538 0.5697115384615384 0.09045673076923078 0.6394230769230769"


def repair_w02(raw: bytes) -> bytes:
    """Change only the explicitly reviewed fourth row, preserving all other bytes."""
    lines = raw.splitlines(keepends=True)
    if len(lines) < 4 or lines[3].rstrip(b"\r\n").decode("utf-8") != EXPECTED:
        raise ValueError("W02 row differs from owner-reviewed input")
    _, x, y, w, h = EXPECTED.split()
    x, y, w, h = map(float, (x, y, w, h))
    left, right = max(0.0, x - w / 2), min(1.0, x + w / 2)
    updated = f"0 {(left + right) / 2:.17g} {y:.17g} {right - left:.17g} {h:.17g}"
    YoloAnnotation.parse(updated)  # strict original validator, no epsilon
    ending = lines[3][len(lines[3].rstrip(b"\r\n")) :]
    lines[3] = updated.encode("utf-8") + ending
    return b"".join(lines)


def create_preview(archive: Path, output: Path) -> dict:
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA256:
        raise ValueError("Archive checksum differs from reviewed Roboflow v1")
    output = output.resolve()
    repo_outputs = Path(__file__).resolve().parents[2] / "outputs"
    if not output.is_relative_to(repo_outputs) or output == repo_outputs or output.exists():
        raise ValueError(
            "Use a new directory under repository outputs/; never raw or existing data"
        )
    label_member = f"train/labels/{STEM}.txt"
    image_member = f"train/images/{STEM}.jpg"
    with ZipFile(archive) as source:
        original = source.read(label_member)
        image = source.read(image_member)
    repaired = repair_w02(original)
    for row in repaired.decode("utf-8").splitlines():
        if row.strip():
            annotation = YoloAnnotation.parse(row)
            if annotation.class_id not in {0, 1, 2}:
                raise ValueError("Unknown source ID")
    for folder in ("input/images", "input/labels", "original"):
        (output / folder).mkdir(parents=True, exist_ok=True)
    (output / "original/W02.txt").write_bytes(original)
    (output / "input/images/W02.jpg").write_bytes(image)
    (output / "input/labels/W02.txt").write_bytes(repaired)
    overlay = export_overlays(
        output / "input",
        images_dir="images",
        labels_dir="labels",
        source_names={0: "Looking around", 1: "No cheating", 2: "Phone use"},
        output_dir=output / "review",
        limit=1,
    )
    assert len(overlay["exported"]) == 1 and not overlay["audit_has_errors"]
    report = {
        "status": "geometry_preview_only_semantic_QA_pending",
        "archive_sha256": digest,
        "source_label": label_member,
        "source_image": image_member,
        "changed_lines": [4],
        "original_label_sha256": hashlib.sha256(original).hexdigest(),
        "derived_label_sha256": hashlib.sha256(repaired).hexdigest(),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "before": EXPECTED,
        "after": repaired.decode().splitlines()[3],
        "strict_geometry_pass": True,
        "source_ids_preserved": True,
        "W01_untouched": True,
        "raw_untouched": True,
        "dataset_accepted": False,
        "output": output.as_posix(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (output / "repair.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(create_preview(args.archive, args.output), indent=2))
