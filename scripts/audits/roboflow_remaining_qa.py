"""Render full remaining-image review and preserve existing owner-approved boxes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.data.review_plan import validate_review_plan

ROOT = Path(__file__).resolve().parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(base: Path, images: Path, output: Path) -> dict:
    evidence = ROOT / "artifacts/reports/roboflow-20261004"
    base_evidence = evidence / "remaining-reviewed-summary.json"
    reference = json.loads(base_evidence.read_text(encoding="utf-8"))
    for name, checksum in reference["outputs_sha256"].items():
        if Path(name).name != name or digest(base / name) != checksum:
            raise ValueError(f"Base artifact differs: {name}")
    queue = json.loads((base / "queue.json").read_text(encoding="utf-8"))
    approved_boxes = json.loads((base / "approved-boxes.json").read_text(encoding="utf-8"))
    remaining = {row["id"] for row in queue if row["disposition"] == "pending_manual_QA"}
    approved = {row["id"] for row in approved_boxes}
    plan_path = evidence / "remaining-qa-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    sizes = {}
    by_id = {row["id"]: row for row in queue}
    for sample_id in remaining | approved:
        row = by_id[sample_id]
        if Path(sample_id).name != sample_id or not row["source_image"].startswith("train/"):
            raise ValueError("Only explicit train review IDs are permitted")
        image_path = images / f"{sample_id}.jpg"
        if digest(image_path) != row["image_sha256"]:
            raise ValueError(f"Image differs from reviewed source: {sample_id}")
        with Image.open(image_path) as image:
            image.load()
            sizes[sample_id] = image.size
    validate_review_plan(plan, remaining, approved, sizes)
    rejections = []
    for rejection in plan.get("source_rejections", []):
        sample_id = rejection["id"]
        if sample_id not in remaining:
            raise ValueError("Rejection must refer to a remaining review sample")
        label_path = images.parent / "source-labels" / f"{sample_id}.txt"
        if digest(label_path) != by_id[sample_id]["label_sha256"]:
            raise ValueError("Source label differs from pinned queue")
        rows = label_path.read_text(encoding="utf-8").splitlines()
        if rows[rejection["line"] - 1] != rejection["expected"]:
            raise ValueError("Rejected source row differs from owner-reviewed box")
        rejections.append({**rejection, "source_label": by_id[sample_id]["source_label"],
                           "label_sha256": by_id[sample_id]["label_sha256"]})
    output = output.resolve()
    if (output.exists() or not output.is_relative_to(ROOT / "outputs")
            or output.is_relative_to(base.resolve()) or output.is_relative_to(images.resolve())):
        raise ValueError("Use a new repository outputs/ directory")
    output.mkdir(parents=True)
    (output / "overlays").mkdir()
    (output / "details").mkdir()
    font = ImageFont.load_default(size=17)
    results = []
    for item in plan["items"]:
        sample_id = item["id"]
        with Image.open(images / f"{sample_id}.jpg") as original:
            image = original.convert("RGB")
        width, height = image.size
        canvas = Image.new("RGB", (max(760, width), height + 78), "white")
        canvas.paste(image)
        draw = ImageDraw.Draw(canvas)
        for color, field, prefix in (("lime", "boxes", "P"), ("orange", "regions", "E")):
            for index, (x1, y1, x2, y2) in enumerate(item[field], 1):
                draw.rectangle((x1, y1, min(x2, width - 1), min(y2, height - 1)),
                               outline=color, width=3 if field == "boxes" else 2)
                draw.text((x1 + 2, y1 + 2), f"{prefix}{index}", font=font,
                          fill="black", stroke_fill="white", stroke_width=2)
        state = "proposed_boxes_pending_owner" if item["boxes"] else "hold_evidence_unresolved"
        lines = [f"{sample_id}: {state}",
                 "GREEN = person phone_use proposal; ORANGE = evidence region, NOT label",
                 "Incomplete labels. NOT TRAINING DATA. Missing box does NOT mean normal."]
        for index, line in enumerate(lines):
            draw.text((5, height + 4 + 23 * index), line, font=font, fill="black")
        canvas.save(output / "overlays" / f"{sample_id}.png")
        if item["regions"]:
            detail = Image.new("RGB", (360 * len(item["regions"]), 390), "white")
            for index, region in enumerate(item["regions"]):
                crop = image.crop(tuple(region))
                scale = min(350 / crop.width, 345 / crop.height)
                crop = crop.resize((max(1, round(crop.width * scale)),
                                    max(1, round(crop.height * scale))), Image.Resampling.NEAREST)
                detail.paste(crop, (index * 360, 0))
                ImageDraw.Draw(detail).text((index * 360 + 4, 352),
                                           f"{sample_id} E{index + 1}: enlarged pixels",
                                           font=font, fill="black")
            detail.save(output / "details" / f"{sample_id}.png")
        results.append({**item, "review_state": state,
                        "source_image": by_id[sample_id]["source_image"],
                        "image_sha256": by_id[sample_id]["image_sha256"],
                        "training_eligible": False})
    # Preserve approved geometry/answers byte for byte; completeness is a separate sidecar.
    (output / "approved-boxes.json").write_bytes((base / "approved-boxes.json").read_bytes())
    write_json(output / "review.json", results)
    write_json(output / "completeness.json", plan["approved_image_completeness"])
    write_json(output / "source-rejections.json", rejections)
    write_json(output / "queue.json", [
        {**row, "visual_qa": next((r["review_state"] for r in results if r["id"] == row["id"]),
                                  "completeness_reviewed_pending_labels" if row["id"] in approved
                                  else "not_in_this_review")}
        for row in queue
    ])
    report = {
        "remaining_images_reviewed": len(results),
        "images_with_proposed_boxes": sum(bool(r["boxes"]) for r in results),
        "proposed_boxes": sum(len(r["boxes"]) for r in results),
        "held_images": sum(not r["boxes"] for r in results),
        "previously_approved_images_reviewed_for_completeness": len(approved),
        "existing_approved_boxes_unchanged": True,
        "training_eligible_images": 0, "dataset_accepted": False,
        "input_sha256": {p.name: digest(p) for p in
                         [plan_path, base_evidence, Path(__file__),
                          ROOT / "src/ai_exam_monitoring/data/review_plan.py"]},
        "output_sha256": {p.relative_to(output).as_posix(): digest(p)
                          for p in sorted(output.rglob("*")) if p.is_file()},
        "output": output.as_posix(),
    }
    write_json(output / "summary.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.base, args.images, args.output)
    concise = {key: value for key, value in result.items() if key != "output_sha256"}
    print(json.dumps(concise, indent=2))
