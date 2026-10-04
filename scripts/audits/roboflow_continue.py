"""Apply reviewed pilot decisions and render the next proposals, never training labels."""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from scripts.audits.roboflow_pilot import ROOT, validate_proposal, write_json


def apply_decisions(queue: list[dict], decisions: list[dict]) -> list[dict]:
    result = deepcopy(queue)
    by_id = {row["id"]: row for row in result}
    if len(by_id) != len(result) or len({d["id"] for d in decisions}) != len(decisions):
        raise ValueError("Duplicate sample decisions or queue IDs")
    for decision in decisions:
        row = by_id[decision["id"]]
        if not row["source_image"].startswith("train/"):
            raise ValueError("Review decisions must be train only")
        if row["disposition"].startswith("excluded"):
            raise ValueError("Cannot override an existing exclusion")
        if decision["action"] == "exclude_image_noise":
            row["disposition"] = "excluded_owner_noise"
        elif decision["action"] == "approve_proposed_boxes_only":
            row["disposition"] = "bbox_approved_completeness_pending"
        else:
            raise ValueError("Unknown owner action")
        row["training_eligible"] = False
    return result


def run(base: Path, output: Path) -> dict:
    evidence = ROOT / "artifacts/reports/roboflow-20261004"
    summary = json.loads((evidence / "pilot-summary.json").read_text(encoding="utf-8"))
    for name, digest in summary["artifact_sha256"].items():
        if hashlib.sha256((base / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Changed base artifact: {name}")
    review = json.loads((evidence / "pilot-owner-review.json").read_text(encoding="utf-8"))
    if review["base_pilot_plan_sha256"] != summary["pilot_plan_sha256"]:
        raise ValueError("Decisions refer to a different pilot plan")
    plan = json.loads((evidence / "batch2-plan.json").read_text(encoding="utf-8"))
    queue = apply_decisions(json.loads((base / "queue.json").read_text()), review["items"])
    by_id = {row["id"]: row for row in queue}
    old = json.loads((base / "proposals.json").read_text())
    approved = []
    for proposal in old:
        if by_id[proposal["id"]]["disposition"] == "bbox_approved_completeness_pending":
            decision = next(d for d in review["items"] if d["id"] == proposal["id"])
            approved.append({**proposal, "status": "bbox_approved_completeness_pending",
                             "note": decision.get("corrected_evidence", proposal["note"]),
                             "owner_answer": decision["answer_verbatim"]})
    output = output.resolve()
    if not output.is_relative_to(ROOT / "outputs") or output.exists():
        raise ValueError("Use a new output directory under repository outputs/")
    # Validate source identity and geometry before writing anything.
    for proposal in plan["proposals"]:
        row = by_id[proposal["id"]]
        if row["disposition"].startswith("excluded"):
            raise ValueError("Excluded image in next batch")
        blob = (base / f"images/{row['id']}.jpg").read_bytes()
        if hashlib.sha256(blob).hexdigest() != row["image_sha256"]:
            raise ValueError("Image differs from pinned queue")
        with Image.open(base / f"images/{row['id']}.jpg") as image:
            for box in proposal["boxes"]:
                validate_proposal(box, *image.size)
    output.mkdir(parents=True)
    font = ImageFont.load_default(size=16)
    for proposal in plan["proposals"]:
        with Image.open(base / f"images/{proposal['id']}.jpg") as original:
            image = original.convert("RGB")
        canvas = Image.new("RGB", (max(640, image.width), image.height + 55), "white")
        canvas.paste(image)
        draw = ImageDraw.Draw(canvas)
        for index, box in enumerate(proposal["boxes"], 1):
            x1, y1, x2, y2 = box["xyxy"]
            draw.rectangle((x1, y1, min(x2, image.width - 1), min(y2, image.height - 1)),
                           outline="lime", width=3)
            draw.text((x1 + 2, y1 + 2), f"{index}: phone_use", fill="black", font=font,
                      stroke_width=2, stroke_fill="white")
        draw.text((5, image.height + 4), f"{proposal['id']} - NEW PROPOSAL, NOT OWNER APPROVED",
                  fill="black", font=font)
        draw.text((5, image.height + 28), "Incomplete labels - NOT TRAINING DATA",
                  fill="red", font=font)
        canvas.save(output / f"{proposal['id']}.png")
    write_json(output / "queue.json", queue)
    write_json(output / "approved-boxes.json", approved)
    write_json(output / "new-proposals.json", [
        {**p, "source_image": by_id[p["id"]]["source_image"],
         "image_sha256": by_id[p["id"]]["image_sha256"], "training_eligible": False}
        for p in plan["proposals"]
    ])
    result = {
        "queue_images": len(queue),
        "excluded_images": sum(r["disposition"].startswith("excluded") for r in queue),
        "approved_bbox_images": len(approved),
        "approved_boxes": sum(len(r["boxes"]) for r in approved),
        "new_proposal_images": len(plan["proposals"]),
        "new_proposal_boxes": sum(len(r["boxes"]) for r in plan["proposals"]),
        "training_eligible_images": 0, "base": base.resolve().as_posix(),
        "input_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         [evidence / "pilot-owner-review.json", evidence / "batch2-plan.json",
                          Path(__file__)]},
        "output_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(output.iterdir()) if p.is_file()},
    }
    write_json(output / "summary.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.base, args.output), indent=2))
