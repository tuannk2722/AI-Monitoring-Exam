"""Validate visual-review proposals without promoting them to training annotations."""

from collections.abc import Mapping
from math import isfinite

from .yolo import YoloAnnotation


def validate_review_plan(plan: dict, remaining: set[str], approved: set[str],
                         sizes: Mapping[str, tuple[int, int]]) -> None:
    if plan.get("training_eligible") is not False or plan.get("dataset_accepted") is not False:
        raise ValueError("Review plan cannot accept data for training")
    if remaining & approved:
        raise ValueError("Remaining and approved image IDs overlap")
    for key, expected in (("items", remaining), ("approved_image_completeness", approved)):
        rows = plan[key]
        ids = [row["id"] for row in rows]
        if len(ids) != len(set(ids)) or set(ids) != expected:
            raise ValueError(f"{key} must cover the exact reviewed image set once")
        for row in rows:
            if not isinstance(row.get("observation"), str) or not row["observation"].strip():
                raise ValueError("Review observation required")
            if key != "items":
                if not row.get("unresolved"):
                    raise ValueError("Completeness blockers must remain explicit")
                continue
            if not row.get("blockers"):
                raise ValueError("Unapproved review requires explicit blockers")
            width, height = sizes[row["id"]]
            for field in ("boxes", "regions"):
                for rectangle in row[field]:
                    if len(rectangle) != 4:
                        raise ValueError("Expected xyxy rectangle")
                    if not all(type(v) in (int, float) and isfinite(v) for v in rectangle):
                        raise ValueError("Review coordinates must be finite numbers")
                    x1, y1, x2, y2 = rectangle
                    YoloAnnotation(2, (x1 + x2) / (2 * width), (y1 + y2) / (2 * height),
                                   (x2 - x1) / width, (y2 - y1) / height)

def apply_owner_review(queue: list[dict], approved: list[dict], proposals: list[dict],
                       decisions: list[dict]) -> tuple[list[dict], list[dict]]:
    """Apply explicit bbox/hold decisions without accepting incomplete images."""
    from copy import deepcopy

    def indexed(rows):
        result = {row["id"]: row for row in rows}
        if len(result) != len(rows):
            raise ValueError("Duplicate review IDs")
        return result

    by_queue, by_proposal = indexed(queue), indexed(proposals)
    by_decision, by_approved = indexed(decisions), indexed(approved)
    pending = {key for key, row in by_queue.items()
               if row["disposition"] == "pending_manual_QA"}
    if set(by_proposal) != pending or set(by_decision) != pending:
        raise ValueError("Decisions must cover exactly the pending proposals")
    if pending & set(by_approved):
        raise ValueError("Cannot replace previously approved boxes")
    result, boxes = deepcopy(queue), deepcopy(approved)
    for row in result:
        if row["id"] not in pending:
            continue
        proposal, decision = by_proposal[row["id"]], by_decision[row["id"]]
        if (not row["source_image"].startswith("train/")
                or any(row[k] != proposal[k] for k in ("source_image", "image_sha256"))):
            raise ValueError("Proposal source identity differs")
        if not decision.get("answer_verbatim", "").strip():
            raise ValueError("Owner answer required")
        action = decision["action"]
        if action == "approve_bbox_only":
            if not proposal["boxes"]:
                raise ValueError("Cannot approve an empty positive proposal")
            boxes.append({
                "id": row["id"], "source_image": row["source_image"],
                "image_sha256": row["image_sha256"],
                "boxes": [{"label": "phone_use", "xyxy": deepcopy(b)}
                          for b in proposal["boxes"]],
                "status": "bbox_approved_completeness_pending",
                "training_eligible": False, "owner_answer": decision["answer_verbatim"],
                "note": proposal["observation"],
                "prior_qa_blockers": deepcopy(proposal["blockers"]),
            })
            row["disposition"] = "bbox_approved_completeness_pending"
        elif action == "hold_outside_train":
            row["disposition"] = "held_outside_train_by_owner"
        elif action != "keep_pending":
            raise ValueError("Unknown owner action")
        row["owner_action"] = action
        row["owner_answer"] = decision["answer_verbatim"]
        row["visual_qa"] = row["disposition"]
        row["training_eligible"] = False
    return result, boxes
