"""Prepare a train-only review queue and similarity triage from the pinned v1 ZIP."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.data.image_similarity import difference_hash, nearest_by_split
from ai_exam_monitoring.data.yolo import YoloAnnotation

ROOT = Path(__file__).resolve().parents[2]
SHA256 = "70060bfe7d65dedcca6a72aaac423c95f402369eec08563b24ae8d962e666eed"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_proposal(box: dict, width: int, height: int) -> None:
    if box["label"] != "phone_use":
        raise ValueError("Pilot proposals only cover reviewed phone_use semantics")
    x1, y1, x2, y2 = box["xyxy"]
    YoloAnnotation(2, (x1 + x2) / (2 * width), (y1 + y2) / (2 * height),
                   (x2 - x1) / width, (y2 - y1) / height)


def prepare(archive: Path, output: Path) -> dict:
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Archive does not match owner-supplied v1")
    output = output.resolve()
    if not output.is_relative_to(ROOT / "outputs") or output.exists():
        raise ValueError("Use a new directory under repository outputs/")
    evidence = ROOT / "artifacts/reports/roboflow-20261004"
    decisions_path = evidence / "owner-decisions.json"
    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))["items"]
    plan_path = evidence / "pilot-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    by_image = {item["source_image"]: item for item in decisions}
    excluded = {"R10", "R11", "R14", "R16"}
    font = ImageFont.load_default(size=16)
    output.mkdir(parents=True)
    for folder in ("images", "source-labels", "contact-sheets", "proposals"):
        (output / folder).mkdir()
    records, fingerprints = [], []
    with ZipFile(archive) as source:
        if len(source.namelist()) != len(set(source.namelist())):
            raise ValueError("Duplicate ZIP member paths")
        phone_paths = set()
        for path in sorted(source.namelist()):
            if path.startswith("train/labels/") and path.endswith(".txt"):
                rows = source.read(path).decode("utf-8").splitlines()
                if any(row.split() and row.split()[0] == "2" for row in rows):
                    phone_paths.add(path.replace("/labels/", "/images/")[:-4] + ".jpg")
        selected = sorted(phone_paths | set(by_image))
        if any(not path.startswith("train/images/") for path in selected):
            raise ValueError("Review queue must contain train images only")
        for path in sorted(source.namelist()):
            if not path.endswith(".jpg") or "/images/" not in path:
                continue
            blob = source.read(path)
            with Image.open(io.BytesIO(blob)) as image:
                image.load()
                fingerprints.append({"path": path, "split": path.split("/")[0],
                                     "dhash": difference_hash(image),
                                     "sha256": hashlib.sha256(blob).hexdigest()})
        for index, path in enumerate(selected, 1):
            sample_id = f"P{index:03d}"
            item = by_image.get(path)
            label_path = path.replace("/images/", "/labels/")[:-4] + ".txt"
            blob, label = source.read(path), source.read(label_path)
            (output / f"images/{sample_id}.jpg").write_bytes(blob)
            (output / f"source-labels/{sample_id}.txt").write_bytes(label)
            records.append({
                "id": sample_id, "source_image": path, "source_label": label_path,
                "image_sha256": hashlib.sha256(blob).hexdigest(),
                "label_sha256": hashlib.sha256(label).hexdigest(),
                "has_source_phone_class": path in phone_paths,
                "owner_review_id": item["id"] if item else None,
                "owner_action": item["action"] if item else None,
                "disposition": "excluded_by_owner" if item and item["id"] in excluded
                else "excluded_UI_subtitle_policy"
                if sample_id in plan["exclude_ui_or_subtitle_ids"] else "pending_manual_QA",
                "group_id": None, "training_eligible": False,
            })
    proposals = []
    for proposal in plan["proposals"]:
        record = next(row for row in records if row["id"] == proposal["id"])
        if record["owner_review_id"] != proposal["owner_review_id"]:
            raise ValueError("Proposal sample identity mismatch")
        if record["disposition"].startswith("excluded"):
            raise ValueError("Cannot propose excluded image")
        with Image.open(output / f"images/{record['id']}.jpg") as original:
            image = original.convert("RGB")
        if list(image.size) != proposal["size"]:
            raise ValueError("Proposal image dimensions mismatch")
        canvas = Image.new("RGB", (max(640, image.width), image.height + 55), "white")
        canvas.paste(image)
        draw = ImageDraw.Draw(canvas)
        for number, box in enumerate(proposal["boxes"], 1):
            validate_proposal(box, image.width, image.height)
            x1, y1, x2, y2 = box["xyxy"]
            draw.rectangle((x1, y1, min(x2, image.width - 1), min(y2, image.height - 1)),
                           outline="lime", width=3)
            draw.text((x1 + 3, y1 + 3), f"{number}: phone_use", font=font,
                      fill="black", stroke_fill="white", stroke_width=2)
        draw.text((5, image.height + 5), f"{record['id']} MANUAL PROPOSAL - OWNER REVIEW PENDING",
                  fill="black", font=font)
        draw.text((5, image.height + 29), "Incomplete labels - NOT TRAINING DATA",
                  fill="red", font=font)
        canvas.save(output / f"proposals/{record['id']}.png")
        proposals.append({**proposal, "source_image": record["source_image"],
                          "image_sha256": record["image_sha256"], "training_eligible": False})
    write_json(output / "proposals.json", proposals)
    # Source thumbnails are for triage; no canonical predictions/labels are implied.
    for start in range(0, len(records), 12):
        sheet = Image.new("RGB", (4 * 320, 3 * 270), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, record in enumerate(records[start:start + 12]):
            x, y = offset % 4 * 320, offset // 4 * 270
            with Image.open(output / f"images/{record['id']}.jpg") as source_image:
                thumb = source_image.convert("RGB")
                thumb.thumbnail((316, 230))
                sheet.paste(thumb, (x, y))
            title = record["id"] + " " + (record["owner_review_id"] or "unreviewed")
            draw.text((x + 2, y + 232), title, fill="black", font=font)
            draw.text((x + 2, y + 251), record["disposition"], fill="black", font=font)
        sheet.save(output / f"contact-sheets/{start // 12 + 1:02d}.png")
    fingerprints_by_path = {item["path"]: item for item in fingerprints}
    nearest = [{"id": row["id"], "source_image": row["source_image"],
                "nearest": nearest_by_split(fingerprints_by_path[row["source_image"]],
                                            fingerprints)} for row in records]
    pairs = sorted({tuple(sorted((row["source_image"], row["nearest"]["train"]["path"])))
                    for row in nearest})
    pairs.sort(key=lambda pair: ((fingerprints_by_path[pair[0]]["dhash"] ^
                                 fingerprints_by_path[pair[1]]["dhash"]).bit_count(), pair))
    # Render only train/train pairs; valid/test similarity evidence remains numeric.
    with ZipFile(archive) as source:
        for index, pair in enumerate(pairs[:6], 1):
            sheet = Image.new("RGB", (832, 452), "white")
            for side, path in enumerate(pair):
                with Image.open(io.BytesIO(source.read(path))) as image:
                    thumb = image.convert("RGB")
                    thumb.thumbnail((416, 416))
                    sheet.paste(thumb, (side * 416, 0))
            distance = (fingerprints_by_path[pair[0]]["dhash"] ^
                        fingerprints_by_path[pair[1]]["dhash"]).bit_count()
            ImageDraw.Draw(sheet).text((5, 421), f"Train pair {index}, distance {distance}/64",
                                       fill="black", font=font)
            sheet.save(output / f"contact-sheets/pair-{index:02d}.png")
    summary = {
        "archive_sha256": SHA256,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "similarity_code_sha256": hashlib.sha256(
            (ROOT / "src/ai_exam_monitoring/data/image_similarity.py").read_bytes()
        ).hexdigest(),
        "owner_decisions_sha256": hashlib.sha256(decisions_path.read_bytes()).hexdigest(),
        "pilot_plan_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        "manual_proposal_images": len(proposals),
        "manual_proposal_boxes": sum(len(row["boxes"]) for row in proposals),
        "source_phone_train_images": len(phone_paths), "queue_images": len(records),
        "dispositions": dict(Counter(row["disposition"] for row in records)),
        "fingerprinted_images_by_split": dict(Counter(row["split"] for row in fingerprints)),
        "similarity_scope": "each queue train image versus every other RF v1 image, per split",
        "similarity_method": "64-bit horizontal difference hash, grayscale 9x8 LANCZOS",
        "automatic_duplicate_threshold": None, "groups_inferred": False,
        "limitations": ["Fingerprint collisions and false negatives possible",
                        "Ranking is not duplicate confirmation or session metadata",
                        "No SCB perceptual comparison in this run",
                        "No valid/test images rendered for policy review",
                        "Queue is not a completed relabel or training dataset"],
        "train_pair_previews": [{"left": a, "right": b} for a, b in pairs[:6]],
        "output": output.as_posix(),
    }
    write_json(output / "queue.json", records)
    write_json(output / "similarity.json", nearest)
    write_json(output / "fingerprints.json", fingerprints)
    write_json(output / "summary.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.archive, args.output), indent=2))
