"""Chuẩn bị membership/whole-family có điều kiện; không ký release hoặc train."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import write_json

from .pilot_schema import read_records, validate_records
from .v7_unapproved_pilot import fresh_output, pin, read_rows, safe_path

STATES = {"P": "positive", "N": "negative", "U": "unknown"}
VALUES = {"positive": 1, "negative": 0, "unknown": None}


def prepare_assignments(
    parent: list[dict[str, Any]], pool: list[dict[str, Any]],
    corrections: list[dict[str, Any]], components: list[dict[str, Any]],
    relations: list[dict[str, Any]], rights: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Bảo toàn parent và unknown; chỉ xuất proposed role sau các gate cơ học."""
    originals = {r["sample_id"]: r for r in parent}
    candidates = {r["sample_id"]: r for r in pool}
    if (len(originals) != len(parent) or len(candidates) != len(pool)
            or set(originals) & set(candidates)):
        raise DataContractError("ID parent/pool trùng")
    deltas = {r["sample_id"]: r for r in corrections}
    by_rights = {r["sample_id"]: r for r in rights}
    if (len(deltas) != len(corrections) or not set(deltas).issubset(originals)
            or len(by_rights) != len(rights) or set(by_rights) != set(candidates)):
        raise DataContractError("Correction/rights inventory không khớp")
    nodes = {sid: sid for sid in originals.keys() | candidates.keys()}

    def find(sid: str) -> str:
        while nodes[sid] != sid:
            nodes[sid] = nodes[nodes[sid]]
            sid = nodes[sid]
        return sid

    def join(ids: list[str]) -> None:
        if not ids or not set(ids).issubset(nodes):
            raise DataContractError("Quan hệ whole-family có ID thiếu/lạ")
        for sid in ids[1:]:
            nodes[find(sid)] = find(ids[0])

    parent_groups: dict[str, list[str]] = defaultdict(list)
    exact_sources: dict[str, list[str]] = defaultdict(list)
    for sid, r in originals.items():
        gid = (r.get("group") or {}).get("leakage_group_id")
        if gid:
            parent_groups[gid].append(sid)
        exact_sources[r["source"]["image_sha256"]].append(sid)
    for sid, r in candidates.items():
        exact_sources[r["source_sha256"]].append(sid)
    for ids in list(parent_groups.values()) + list(exact_sources.values()):
        join(ids)
    covered: list[str] = []
    for component in components:
        ids = component["sample_ids"]
        if not set(ids).issubset(candidates):
            raise DataContractError("Component ngoài pool")
        covered.extend(ids)
        join(ids)
    if len(covered) != len(set(covered)) or set(covered) != set(candidates):
        raise DataContractError("Component phải partition toàn pool")
    for relation in relations:
        if not relation.get("reason") or not relation.get("evidence_ref"):
            raise DataContractError("Must-link cần reason và evidence")
        join(relation["sample_ids"])
    proposed: dict[str, dict[str, Any]] = {}
    for sid, r in originals.items():
        states = [r["phone_use"]["state"], r["looking_around"]["state"]]
        usage = r["usage"]
        delta = deltas.get(sid)
        if delta:
            if (delta["source_sha256"] != r["source"]["image_sha256"]
                    or delta["original_crop_sha256"] != r["crop"]["crop_sha256"]
                    or delta["parent_usage"] != usage):
                raise DataContractError("Parent delta khác SHA/usage đã pin")
            if usage == "test" and (
                delta["proposed_usage"] != usage or delta["proposed_states"] != states
                or delta.get("decisions")
            ):
                raise DataContractError("Không sửa test freeze")
            usage, states = delta["proposed_usage"], delta["proposed_states"]
        proposed[sid] = {
            "sample_id": sid, "origin": "parent_v6", "source_id": r["source"]["source_id"],
            "source_sha256": r["source"]["image_sha256"],
            "crop_sha256": (r.get("crop") or {}).get("crop_sha256"),
            "proposed_usage": usage, "proposed_states": states,
            "parent_usage": r["usage"], "parent_delta": delta,
            "blockers": [], "parent_record": r,
        }
    for sid, r in candidates.items():
        states = [STATES[s] for s in r["states"]]
        if r["official_split"] is not None or r["training_eligible"]:
            raise DataContractError("Pool phải còn staging chưa assignment")
        usage = "train"
        blockers = list(by_rights[sid]["blockers"])
        if r["eligibility_proposal"] == "quarantine_no_train_evaluation_family":
            usage = "excluded"
            blockers.append("evaluation_family_quarantine_preserved")
        elif all(s == "unknown" for s in states):
            usage = "review_only"
            blockers.append("both_targets_unknown")
        elif blockers:
            usage = "review_only"
        proposed[sid] = {
            "sample_id": sid, "origin": r["origin"],
            "source_sha256": r["source_sha256"],
            "crop_sha256": r["media"]["crop"]["sha256"],
            "proposed_usage": usage, "proposed_states": states,
            "owner_exact_crop_label_approved": r["owner_exact_crop_label_approved"],
            "blockers": blockers, "rights": by_rights[sid], "candidate_record": r,
        }
    grouped: dict[str, list[str]] = defaultdict(list)
    for sid in nodes:
        grouped[find(sid)].append(sid)
    whole = []
    for ids in sorted((sorted(v) for v in grouped.values()), key=lambda v: v[0]):
        parent_used = {proposed[s]["proposed_usage"] for s in ids if s in originals
                       and proposed[s]["proposed_usage"] in {"train", "val", "test"}}
        if len(parent_used) > 1:
            raise DataContractError("Quan hệ mới nối parent qua nhiều split; cần quyết định riêng")
        evaluation_family = bool(parent_used & {"val", "test"})
        gid = "V7-G-" + hashlib.sha256("|".join(ids).encode()).hexdigest()[:20]
        for sid in ids:
            row = proposed[sid]
            if sid in candidates and evaluation_family and row["proposed_usage"] == "train":
                row["proposed_usage"] = "review_only"
                row["blockers"].append("evaluation_family_or_boundary_pending")
            states = row["proposed_states"]
            if any(s not in VALUES for s in states):
                raise DataContractError("Target state ngoài PNU")
            if row["proposed_usage"] in {"train", "val", "test"} and all(
                s == "unknown" for s in states
            ):
                raise DataContractError("U/U không được vào proposed supervision")
            row.update(
                proposed_group_id=gid, proposed_target_values=[VALUES[s] for s in states],
                proposed_target_mask=[int(s != "unknown") for s in states],
                canonical_split=None, training_eligible=False, release_accepted=False,
                independence_proven=False, status="prepared_pending_owner_release_acceptance",
            )
        roles = {proposed[s]["proposed_usage"] for s in ids
                 if proposed[s]["proposed_usage"] in {"train", "val", "test"}}
        if len(roles) > 1:
            raise DataContractError("Whole-family đi qua nhiều proposed split")
        whole.append({"proposed_group_id": gid, "sample_ids": ids,
                      "proposed_used_roles": sorted(roles),
                      "evaluation_boundary_quarantine": evaluation_family,
                      "independence_proven": False, "owner_release_accepted": False})
    return [proposed[s] for s in sorted(proposed)], whole


def build(config_path: Path, root: Path) -> dict[str, Any]:
    config = load_yaml(config_path)
    if config["status"] != "owner_authorized_local_preparation_not_release_acceptance":
        raise DataContractError("Config chỉ cho phép preparation")
    builder_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if config.get("builder_sha256", builder_sha) != builder_sha:
        raise DataContractError("Builder khác source SHA đã pin")
    for spec in config.get("provenance_pins", []):
        pin(root, spec)
    paths = {key: pin(root, spec) for key, spec in config["inputs"].items()}
    validate_records(read_records(paths["parent_ledger"]))
    data: dict[str, Any] = {
        key: (read_rows(path) if path.suffix == ".jsonl" else
              json.loads(path.read_text(encoding="utf8"))) for key, path in paths.items()
    }
    if (data["authorization"].get("status")
            != "owner_approved_local_direction_and_release_preparation"
            or data["authorization"].get("release_acceptance_signed") is not False
            or data["authorization"].get("training_run_approved") is not False):
        raise DataContractError("Receipt phải chốt đúng preparation, không giả release/train")
    ledger, groups = prepare_assignments(data["parent_ledger"], data["pool"],
                                        data["parent_corrections"], data["components"],
                                        data["relations"], data["rights"])
    counts = dict(Counter(r["proposed_usage"] for r in ledger))
    if counts != config["expected_counts"]:
        raise DataContractError(f"Actual proposed counts khác config: {counts}")
    output = fresh_output(root, config["output"])
    output.mkdir(parents=True)
    for name, rows in [("proposed-ledger.jsonl", ledger), ("proposed-assignment.jsonl", [
        {key: r[key] for key in ("sample_id", "proposed_usage", "proposed_group_id",
                               "proposed_target_values", "proposed_target_mask", "blockers",
                               "canonical_split", "training_eligible", "release_accepted")}
        for r in ledger
    ])]:
        (output / name).write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True)
                                            + "\n" for r in rows), encoding="utf8")
    write_json(output / "whole-family-proposal.json", groups)
    summary = {"status": "prepared_pending_owner_release_acceptance", "ledger_records": len(ledger),
               "proposed_counts": counts, "whole_components": len(groups),
               "parent_versions_unchanged": True, "test11_metadata_preserved": True,
               "new_independence_proven": 0, "canonical_release_materialized": False,
               "training_started": False, "config": {
                   "path": config_path.relative_to(root).as_posix(),
                   "sha256": hashlib.sha256(config_path.read_bytes()).hexdigest()},
               "builder_sha256": builder_sha,
               "input_pins": config["inputs"],
               "provenance_pins": config.get("provenance_pins", []),
               "coverage": {usage: dict(Counter("/".join(r["proposed_states"])
                            for r in ledger if r["proposed_usage"] == usage)) for usage in counts},
               "held_candidates": [{"sample_id": r["sample_id"], "blockers": r["blockers"]}
                                   for r in ledger if r["origin"] != "parent_v6" and r["blockers"]]
               }
    write_json(output / "summary.json", summary)
    lines = ["# V7 local — bản chuẩn bị release", "",
             f"{len(ledger)} quyết định đề xuất; chưa ký release hoặc chạy training.",
             "",
             f"Phương án sau kiểm gate: {counts}. Whole-family: {len(groups)} thành phần.", "",
             "Nhãn/rectangle mới cần nghiệm thu batch cùng rights/whole-family và split cụ thể. "
             "Giữ nguyên parent v6 và test11; U/U ngoài supervision. "
             "Phần sử dụng dự kiến chỉ có trong proposed-assignment.jsonl.", "",
             "Ảnh/crop/input224 R3 và R5 được trỏ nguyên SHA trong proposed-ledger.jsonl. "
             "Không tạo manifest sử dụng/copy media val/test trong bước preparation.", ""]
    (output / "REVIEW.md").write_text("\n".join(lines), encoding="utf8")
    files = sorted(p for p in output.rglob("*") if p.is_file())
    (output / "checksums.sha256").write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}\n"
        for p in files), encoding="utf8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.workspace.resolve()
    summary = build(safe_path(root, str(args.config)), root)
    print(json.dumps({k: summary[k] for k in ("status", "ledger_records", "proposed_counts",
                                             "whole_components")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
