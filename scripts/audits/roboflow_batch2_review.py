"""Consolidate batch 2 approval without creating a training dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from scripts.audits.roboflow_continue import apply_decisions
from scripts.audits.roboflow_pilot import ROOT, write_json


def apply_group_choices(queue: list[dict], groups: list[dict]) -> list[dict]:
    result = json.loads(json.dumps(queue))
    by_id = {row["id"]: row for row in result}
    seen = set()
    for group in groups:
        action = group["action"]
        if action not in {"exclude_image_noise", "defer_from_initial_subset"}:
            raise ValueError("Unknown grouped decision")
        for sample_id in group["ids"]:
            if sample_id in seen or sample_id not in by_id:
                raise ValueError("Duplicate or missing grouped sample")
            seen.add(sample_id)
            row = by_id[sample_id]
            if row["disposition"] != "pending_manual_QA":
                raise ValueError("Group decision would override an existing reviewed status")
            if not row["source_image"].startswith("train/"):
                raise ValueError("Only train images can enter this subset review")
            row["disposition"] = ("excluded_owner_noise" if action == "exclude_image_noise"
                                  else "deferred_initial_subset")
            row["training_eligible"] = False
    return result


def verify_reviewed_proposals(decisions: list[dict], proposals: list[dict]) -> None:
    by_id = {p["id"]: p for p in proposals}
    if len(by_id) != len(proposals) or len({d["id"] for d in decisions}) != len(decisions):
        raise ValueError("Duplicate proposal/review IDs")
    if set(by_id) != {d["id"] for d in decisions}:
        raise ValueError("Review must cover exactly the batch proposals")
    for decision in decisions:
        proposal = by_id[decision["id"]]
        for key in ("source_image", "image_sha256", "boxes"):
            if decision[key] != proposal[key]:
                raise ValueError(f"Reviewed {key} differs for {decision['id']}")
        if decision["action"] != "approve_proposed_boxes_only":
            raise ValueError("This batch contains only explicit bbox approvals")


def run(base: Path, output: Path, group_review: Path | None = None) -> dict:
    evidence = ROOT / "artifacts/reports/roboflow-20261004"
    decision_path = evidence / "batch2-owner-review.json"
    review = json.loads(decision_path.read_text(encoding="utf-8"))
    summary_bytes = (base / "summary.json").read_bytes()
    if hashlib.sha256(summary_bytes).hexdigest() != review["base_summary_sha256"]:
        raise ValueError("Base summary differs from owner-reviewed batch")
    summary = json.loads(summary_bytes)
    for name, digest in summary["output_sha256"].items():
        if Path(name).name != name:
            raise ValueError("Expected flat batch artifact paths")
        if hashlib.sha256((base / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Base artifact changed: {name}")
    proposals = json.loads((base / "new-proposals.json").read_text(encoding="utf-8"))
    verify_reviewed_proposals(review["items"], proposals)
    queue = apply_decisions(
        json.loads((base / "queue.json").read_text(encoding="utf-8")), review["items"]
    )
    if group_review is not None:
        groups = json.loads(group_review.read_text(encoding="utf-8"))["groups"]
        queue = apply_group_choices(queue, groups)
    approved = json.loads((base / "approved-boxes.json").read_text(encoding="utf-8"))
    if {p["id"] for p in approved} & {p["id"] for p in proposals}:
        raise ValueError("Would approve a sample twice")
    for proposal in proposals:
        decision = next(d for d in review["items"] if d["id"] == proposal["id"])
        approved.append({**proposal, "status": "bbox_approved_completeness_pending",
                         "owner_answer": decision["answer_verbatim"]})
    remaining = [r for r in queue if r["disposition"] == "pending_manual_QA"]
    images = Path(summary["base"]) / "images"
    for row in remaining:
        if Path(row["id"]).name != row["id"] or not row["source_image"].startswith("train/"):
            raise ValueError("Invalid train review identity")
        image_digest = hashlib.sha256((images / f"{row['id']}.jpg").read_bytes()).hexdigest()
        if image_digest != row["image_sha256"]:
            raise ValueError(f"Source image changed: {row['id']}")
    output = output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "outputs"):
        raise ValueError("Use a new repository outputs/ directory")
    output.mkdir(parents=True)
    font = ImageFont.load_default(size=18)
    for start in range(0, len(remaining), 12):
        sheet = Image.new("RGB", (1280, 810), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, row in enumerate(remaining[start:start + 12]):
            x, y = offset % 4 * 320, offset // 4 * 270
            with Image.open(images / f"{row['id']}.jpg") as original:
                thumbnail = original.convert("RGB")
                thumbnail.thumbnail((316, 235))
                sheet.paste(thumbnail, (x, y))
            draw.text((x + 4, y + 239), row["id"] + " - remaining QA", fill="black", font=font)
        sheet.save(output / f"remaining-{start // 12 + 1:02d}.png")
    write_json(output / "queue.json", queue)
    write_json(output / "approved-boxes.json", approved)
    write_json(output / "remaining.json", remaining)
    result = {
        "queue_images": len(queue),
        "excluded_images": sum(r["disposition"].startswith("excluded") for r in queue),
        "bbox_approved_images": len(approved),
        "bbox_approved_count": sum(len(p["boxes"]) for p in approved),
        "remaining_without_bbox_approval": len(remaining),
        "deferred_initial_subset": sum(r["disposition"] == "deferred_initial_subset"
                                       for r in queue),
        "group_review_sha256": hashlib.sha256(group_review.read_bytes()).hexdigest()
        if group_review is not None else None,
        "training_eligible_images": 0, "dataset_accepted": False,
        "base_summary_sha256": review["base_summary_sha256"],
        "decision_sha256": hashlib.sha256(decision_path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "outputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(output.iterdir())},
    }
    write_json(output / "summary.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--group-review", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.base, args.output, args.group_review), indent=2))
