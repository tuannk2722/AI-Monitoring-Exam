"""Tổng hợp measured yield R8 và membership constraints; không materialize split."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.provenance import write_json

from .v7_r8_execution import fresh, pinned


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines() if line]


def summarize(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    config = load_yaml(config_path)
    approval = json.loads(pinned(root, config["approval"]).read_text(encoding="utf8"))
    approved = rows(pinned(root, approval["approved_proposals"]))
    r7 = {r["sample_id"]: r for r in rows(pinned(root, config["r7_candidates"]))}
    review = rows(pinned(root, config["review_proposals"]))
    components = json.loads(pinned(root, config["components"]).read_text(encoding="utf8"))
    graph = {sid: c for c in components for sid in c["candidate_ids"]}
    source_audit = json.loads(pinned(root, config["source_audit"]).read_text(encoding="utf8"))
    observations: list[dict[str, Any]] = []
    screens_by_source: Counter[str] = Counter()
    new_selections: Counter[str] = Counter()
    selected = {(r["screening_set"], r["screening_id"]) for r in review}
    for name, pin in config["screenings"].items():
        for row in rows(pinned(root, pin)):
            source = row.get("source_id", "wmf_knowledge_everyone")
            screens_by_source[source] += 1
            chosen = (name, row["sample_id"]) in selected
            if chosen:
                new_selections[source] += 1
            key = name + ":" + row["sample_id"]
            observations.append({"screening_set": name, "sample_id": row["sample_id"],
                "source_id": source, "visually_screened": True,
                "source_sha256": row.get("source_image_sha256", row.get("frame_sha256")),
                "disposition": "shortlisted_draft" if chosen else "not_shortlisted_this_pass",
                "owner_accepted_new_crop": False,
                "reason": config["specific_observations"].get(key,
                    "Đã xem trong targeted screening; không chọn vào batch này khi chưa đủ "
                    "kết hợp target evidence, own-workarea và diversity/lineage. Không xác "
                    "nhận target N, owner reject hay toàn nguồn exhausted."),
                "independent_group_proven": False})
    membership = []
    for row in approved:
        sid, states = row["sample_id"], row["final_proposed_states"]
        parent = graph[sid]
        original = r7[sid]
        text = original.get("source_image_relpath", "").lower()
        green = any(prefix in text for prefix in config["evaluation_filename_prefixes"])
        evaluation = (green or original.get("known_evaluation_family", False)
                      or bool({"val", "test"}.intersection(parent["historical_split_hints"])))
        usage = ("quarantine_no_train_evaluation_family" if evaluation else
                 "review_only_all_unknown" if states == ["U", "U"] else
                 "conditional_pending_group_rights_input224_QA")
        membership.append({"sample_id": sid, "owner_crop_label_approved": True,
            "approved_states": states, "component_id": parent["component_id"],
            "historical_split_hints": parent["historical_split_hints"],
            "membership_proposal": usage, "official_split": None, "training_eligible": False,
            "reason": "RF-GREEN filename lineage thuộc validation v6 đã Accepted"
            if green else parent["proposal"],
            "owner_approval_receipt": config["approval"],
            "does_not_change_approved_crop_or_labels": True})
    sources = []
    for old in source_audit["records"]:
        sid = old["source_id"]
        sources.append({"source_id": sid,
            "prior_audit": old, "r8_screened_images": screens_by_source[sid],
            "cumulative_screened_images": old["screened_images"] + screens_by_source[sid],
            "r8_selected_new_source_images": new_selections[sid],
            "r8_crop_proposals": sum(r["source_id"] == sid for r in review),
            "r5_owner_approved_crop_label_records": sum(r["source_id"] == sid for r in approved),
            "new_independent_groups_proven": 0, "remaining_useful_independent_groups": None,
            "exhausted_whole_source": False})
    matrix: Counter[tuple[str, ...]] = Counter()
    for row in review:
        for target, state in zip(["phone_use", "looking_around"], row["states"], strict=True):
            matrix[(row["source_id"], row["domain"], target, state,
                    row["visual_family_hint"])] += 1
    bbox = pinned(root, config["oi_prefix"])
    count, complete_groups, last = 0, 0, None
    with bbox.open(encoding="utf8", newline="") as stream:
        for item in csv.DictReader(stream):
            count += 1
            if last is not None and item["ImageID"] != last:
                complete_groups += 1
            last = item["ImageID"]
    summary = {"status": "r8_measured_yield_new_labels_owner_pending", "date": config["date"],
        "approved_r5_records": len(approved), "new_screened_eight_source_images":
        sum(screens_by_source[s["source_id"]] for s in source_audit["records"]),
        "new_public_video_frames_screened": screens_by_source["wmf_knowledge_everyone"],
        "r8_new_crop_proposals": len(review), "r8_owner_approved_crop_records": 0,
        "r8_combination_counts": dict(Counter("".join(r["states"]) for r in review)),
        "fully_known": sum("U" not in r["states"] for r in review),
        "four_target_combinations": {c: sum("".join(r["states"]) == c for r in review)
                                     for c in ["PP", "PN", "NP", "NN"]},
        "new_independent_groups_proven": 0,
        "new_visual_family_lead_not_independence_proof": 1,
        "desk_phone_training_proposal_yield": 0,
        "membership_proposal_counts": dict(Counter(r["membership_proposal"] for r in membership)),
        "oi_prefix": {"bytes": bbox.stat().st_size, "annotation_rows_scanned": count,
                      "complete_image_groups": complete_groups,
                      "excluded_last_image_id": last, "exhausted_full_source": False},
        "test_media_read": False, "training_executed": False, "release_materialized": False}
    output = fresh(root, config["output"], "artifacts/reports")
    output.mkdir(parents=True)
    for name, records in [("screening-observations.jsonl", observations),
                          ("approved-r5-membership-constraints.jsonl", membership)]:
        (output / name).write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in records),
                                  encoding="utf8")
    write_json(output / "source-funnel-r8.json", sources)
    write_json(output / "annotation-matrix-r8.json", [
        dict(zip(["source", "domain", "target", "state", "group"], key, strict=True), count=value)
        for key, value in sorted(matrix.items())])
    write_json(output / "concentration-r8.json", dict(Counter(
        r["visual_family_hint"] for r in review)))
    write_json(output / "yield-summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(summarize(args.config, Path.cwd()), ensure_ascii=False))


if __name__ == "__main__":
    main()
