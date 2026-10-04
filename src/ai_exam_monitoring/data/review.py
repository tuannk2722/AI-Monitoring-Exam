"""Reusable review validation and explicit owner decisions; never training approval."""

import json
from collections.abc import Mapping
from copy import deepcopy
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


def validate_context_plan(plan, base_rows, sizes):
    base = {r["id"]: r for r in base_rows}
    rows = plan["items"] + plan["additional_people"]
    if plan.get("dataset_accepted") is not False:
        raise ValueError("Review cannot accept a dataset")
    if len(base) != len(base_rows) or len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate crop identity")
    if {r["id"] for r in plan["items"]} != set(base):
        raise ValueError("Must cover all existing targets exactly")
    for row in rows:
        if row["owner_review"] != "pending" or row["training_eligible"] is not False:
            raise ValueError("Proposals must stay pending")
        if row["looking_around"] not in {"unknown", "proposed_positive"}:
            raise ValueError("No automatic negative labels")
        if row["id"] in base:
            ref = base[row["id"]]
            if row["person_xyxy"] != ref["person_xyxy"]:
                raise ValueError("Approved person geometry changed")
            if row["phone_use"] != "owner_approved_positive":
                raise ValueError("Existing positive must be preserved")
            image_id = ref["image_id"]
        else:
            image_id = row["image_id"]
            if row["phone_use"] != "unknown":
                raise ValueError("New person phone requires separate review")
        width, height = sizes[image_id]
        for key in ("person_xyxy", "context_crop_xyxy"):
            rect = row[key]
            if len(rect) != 4 or not all(type(v) is int and isfinite(v) for v in rect):
                raise ValueError("Integer pixel coordinates required")
            x1, y1, x2, y2 = rect
            if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
                raise ValueError("Rectangle outside source")
        p, c = row["person_xyxy"], row["context_crop_xyxy"]
        if not (c[0] <= p[0] and c[1] <= p[1] and c[2] >= p[2] and c[3] >= p[3]):
            raise ValueError("Context crop must contain the person bbox")


def apply_context_decisions(proposals, decisions):
    if decisions.get("dataset_accepted") is not False:
        raise ValueError("Crop review cannot accept a dataset")
    by_id = {r["id"]: r for r in proposals}
    choices = {r["id"]: r for r in decisions["items"]}
    if (len(by_id) != len(proposals) or len(choices) != len(decisions["items"])
            or set(choices) != set(by_id)):
        raise ValueError("Owner review must cover each proposed target exactly once")
    result = deepcopy(proposals)
    for row in result:
        choice = choices[row["id"]]
        if (row["owner_review"] != "pending" or row["training_eligible"] is not False
                or not row["source_image"].startswith("train/")):
            raise ValueError("Only pending train proposals may be reviewed")
        if choice["approve_person_and_crop"] is not True:
            raise ValueError("This review requires explicit person/crop approval")
        if not choice["answer_ids"] or any(
            not decisions["answers_verbatim"].get(key, "").strip() for key in choice["answer_ids"]
        ):
            raise ValueError("Verbatim owner evidence required")
        if row["phone_use"] not in {"unknown", "owner_approved_positive"}:
            raise ValueError("Unsupported phone status")
        looking = row["looking_around"]
        if looking not in {"unknown", "proposed_positive"}:
            raise ValueError("Unsupported looking status")
        if type(choice["approve_looking_around"]) is not bool:
            raise ValueError("Explicit boolean required")
        if choice["approve_looking_around"]:
            if looking != "proposed_positive":
                raise ValueError("Cannot approve an unproposed looking label")
            row["looking_around"] = "owner_approved_positive"
        else:
            row["looking_around"] = "unknown"
        row["owner_review"] = "approved_person_crop_and_explicit_targets"
        row["person_status"] = "owner_approved"
        row["crop_status"] = "owner_approved"
        row["owner_answers"] = {
            key: decisions["answers_verbatim"][key] for key in choice["answer_ids"]
        }
        # Approval is not a completeness, split or dataset acceptance gate.
        row["training_eligible"] = False
    return result


def validate_proposal(box: dict, width: int, height: int) -> None:
    if box["label"] != "phone_use":
        raise ValueError("Pilot proposals only cover reviewed phone_use semantics")
    x1, y1, x2, y2 = box["xyxy"]
    YoloAnnotation(2, (x1 + x2) / (2 * width), (y1 + y2) / (2 * height),
                   (x2 - x1) / width, (y2 - y1) / height)


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
