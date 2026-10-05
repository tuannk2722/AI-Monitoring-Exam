"""Report finite proposals or build a release from an explicitly submitted owner approval."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import (
    git_commit,
    git_is_dirty,
    sha256_file,
    write_json,
)

from .pilot_owner_groups import verify_payload
from .pilot_package import build_pilot_package, coverage_report
from .pilot_schema import (
    ContextReview,
    GroupReview,
    PilotRecord,
    ReviewEvidence,
    TargetReview,
    read_records,
    record_to_dict,
    validate_records,
)
from .source_layout import validate_output


def propose_rows(records: list[PilotRecord], config: dict[str, Any]) -> list[dict[str, Any]]:
    """Keep proposals plain data: proposed states are never canonical ReviewEvidence."""
    if config["status"] != "draft_pending_owner_acceptance":
        raise DataContractError("Only an unapproved draft may be produced")
    by_id = {r.sample_id: r for r in records}
    parent_groups: dict[str, set[str]] = defaultdict(set)
    for r in records:
        if r.group and r.group.leakage_group_id:
            parent_groups[r.group.leakage_group_id].add(r.sample_id)
    assignments, consumed_groups, proposal_ids = {}, set(), set()
    for group in config["groups"]:
        name, split = group["proposal_id"], group["proposed_split"]
        if name in proposal_ids or split not in {"train", "val", "test"}:
            raise DataContractError("Duplicate proposal group or invalid split")
        proposal_ids.add(name)
        members = set(group["additional_sample_ids"])
        for old in group["parent_group_ids"]:
            if old not in parent_groups or old in consumed_groups:
                raise DataContractError("Unknown or repeated approved group")
            consumed_groups.add(old)
            members.update(parent_groups[old])
        if len(members) < 2 or not group["visual_evidence"].strip():
            raise DataContractError("Proposal requires a conservative cluster and evidence")
        for sample_id in members:
            if sample_id not in by_id or sample_id in assignments:
                raise DataContractError("Unknown or overlapping proposal member")
            assignments[sample_id] = (name, split)
    if consumed_groups != set(parent_groups):
        raise DataContractError("Every approved must-link group must be preserved")
    negatives = {}
    for proposal in config["phone_negative_proposals"]:
        sample_id = proposal["sample_id"]
        r = by_id.get(sample_id)
        if (r is None or r.crop is None or sample_id in negatives
                or not sample_id.startswith("SCB-") or r.phone_use.state != "unknown"
                or r.looking_around.state != "negative"
                or r.work_context_review.state != "unknown"
                or proposal["crop_sha256"] != r.crop.crop_sha256
                or proposal["proposed_phone_use"] != "negative"
                or proposal["proposed_work_context"] != "confirmed_working"
                or not proposal["observation"].strip()):
            raise DataContractError("Phone proposal differs from the exact unknown crop/evidence")
        negatives[sample_id] = proposal
    rows = []
    identity_assignments: dict[
        tuple[str, str], set[tuple[str | None, str | None]]
    ] = defaultdict(set)
    for r in sorted(records, key=lambda item: item.sample_id):
        if r.crop is None or r.split is not None or r.usage != "review_only":
            raise DataContractError("Expected reviewed, unsplit preparation inputs")
        group_id, split = assignments.get(r.sample_id, (None, None))
        phone = "negative" if r.sample_id in negatives else r.phone_use.state
        work = ("confirmed_working" if r.sample_id in negatives
                else r.work_context_review.state)
        rows.append({
            "status": "draft_pending_owner_acceptance", "sample_id": r.sample_id,
            "source_id": r.source.source_id, "image_sha256": r.source.image_sha256,
            "crop_sha256": r.crop.crop_sha256, "parent_crop_relpath": r.crop.crop_relpath,
            "canonical_phone_use": r.phone_use.state, "proposed_phone_use": phone,
            "looking_around_unchanged": r.looking_around.state,
            "proposed_work_context": work,
            "proposed_confirmed_normal": (phone == r.looking_around.state == "negative"
                                          and work == "confirmed_working"),
            "proposed_group_id": group_id, "proposed_split": split,
            "proposed_usage": split or "review_only",
            "phone_observation": negatives.get(r.sample_id, {}).get("observation"),
        })
        for kind, digest in (("image", r.source.image_sha256), ("crop", r.crop.crop_sha256)):
            identity_assignments[kind, digest].add((group_id, split))
    if any(len(values) > 1 for values in identity_assignments.values()):
        raise DataContractError("Same image/crop cannot cross proposed groups or usage")
    return rows


def counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    states = {
        target: {state: sum(row[field] == state for row in rows)
                 for state in ("positive", "negative", "unknown")}
        for target, field in (("phone_use", "proposed_phone_use"),
                              ("looking_around", "looking_around_unchanged"))
    }
    return {
        "records": len(rows), "targets": states,
        "proposed_confirmed_normal": sum(r["proposed_confirmed_normal"] for r in rows),
        "cooccurrence": sum(r["proposed_phone_use"] == r["looking_around_unchanged"]
                            == "positive" for r in rows),
        "fully_labeled": sum(r["proposed_phone_use"] != "unknown"
                             and r["looking_around_unchanged"] != "unknown" for r in rows),
        "partially_labeled": sum((r["proposed_phone_use"] != "unknown")
                                 != (r["looking_around_unchanged"] != "unknown") for r in rows),
        "fully_unknown": sum(r["proposed_phone_use"] == r["looking_around_unchanged"]
                             == "unknown" for r in rows),
        "binary_target_support": {t: bool(s["positive"] and s["negative"])
                                  for t, s in states.items()},
    }


def apply_release_approval(
    records: list[PilotRecord], proposal: dict[str, Any], approval: dict[str, Any],
    *, dataset_version: str, split_version: str, evidence_ref: str,
) -> list[PilotRecord]:
    """Caller must have evidence of owner submission; a file alone is not authorization."""
    required = {"phone_context", "group_boundaries", "split_config", "schema_config",
                "local_use_scope", "release", "test_freeze"}
    if (approval.get("decision") != "approve_pilot_b_release"
            or set(approval.get("approved_items", [])) != required
            or approval.get("exceptions") != [] or not approval.get("owner_message")
            or not approval.get("reviewer") or not evidence_ref or not split_version
            or dataset_version in {r.dataset_version for r in records}
            or approval.get("use_scope") != proposal["proposed_use_scope"]
            or approval["use_scope"] != "local_classifier_research"):
        raise DataContractError("Explicit scoped release approval and new version required")
    rows = propose_rows(records, proposal)
    by_id = {r["sample_id"]: r for r in rows}
    group_specs = {g["proposal_id"]: g for g in proposal["groups"]}
    group_images: dict[str, set[str]] = defaultdict(set)
    old_evidence: dict[str, set[str]] = defaultdict(set)
    for r in records:
        name = by_id[r.sample_id]["proposed_group_id"]
        if name is not None:
            group_images[name].add(r.source.image_sha256)
            if r.group:
                old_evidence[name].update(r.group.evidence_refs)
    release_review = ReviewEvidence(
        approval["reviewer"], approval["reviewed_at"], evidence_ref
    )
    result = []
    for r in records:
        row = by_id[r.sample_id]
        changes: dict[str, Any] = {"dataset_version": dataset_version}
        if row["phone_observation"]:
            review = replace(release_review,
                             evidence_ref=f"{evidence_ref}#phone_context/{r.sample_id}",
                             crop_sha256=row["crop_sha256"])
            changes.update(
                phone_use=TargetReview("negative", row["phone_observation"], review),
                work_context_review=ContextReview(
                    "confirmed_working", row["phone_observation"], review
                ),
            )
        name, split = row["proposed_group_id"], row["proposed_split"]
        if name is None:
            changes["ineligibility_reasons"] = ("group_evidence_insufficient_for_release",)
        else:
            digest = hashlib.sha256("|".join(sorted(group_images[name])).encode()).hexdigest()
            group_ref = f"{evidence_ref}#group_boundaries/{name}"
            changes.update(
                group=GroupReview(
                    f"PB-G-{digest[:20]}",
                    tuple(sorted(old_evidence[name] | {group_ref})),
                    replace(release_review, evidence_ref=group_ref),
                ),
                rights=replace(r.rights, approved_use_scope=(approval["use_scope"],),
                               review=release_review),
                usage=split, split=split, split_version=split_version,
                ineligibility_reasons=(), owner_decision_ref=evidence_ref,
                release_review=release_review, use_scope=approval["use_scope"],
                test_freeze_ref="release.json#test_freeze" if split == "test" else None,
            )
            # The full visual evidence remains in the pinned approved proposal config.
            if not group_specs[name]["visual_evidence"].strip():
                raise DataContractError("Approved group requires visual evidence")
        result.append(replace(r, **changes))
    validate_records(result)
    return result


def test_freeze_attestation(
    records: list[PilotRecord], *, config_sha256: str, approval_sha256: str,
    owner_decision_ref: str, approval: dict[str, Any], commit: str, protocol: str,
) -> dict[str, Any]:
    """Pin serializer-exact hashes without a cycle through release.json/checksums."""
    used = sorted((r for r in records if r.split), key=lambda r: r.sample_id)

    def digest(rows: list[dict[str, Any]]) -> str:
        payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True,
                                     allow_nan=False) + "\n" for row in rows)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return {
        "status": "frozen", "frozen_at": approval["recorded_at"],
        "reviewer": approval["reviewer"], "owner_decision_ref": owner_decision_ref,
        "owner_decision_sha256": approval_sha256, "config_sha256": config_sha256,
        "git_commit": commit, "split_version": used[0].split_version,
        "manifest_sha256": digest([record_to_dict(r) for r in used]),
        "split_assignment_sha256": digest([
            {"sample_id": r.sample_id, "split": r.split,
             "leakage_group_id": r.group.leakage_group_id if r.group else None,
             "split_version": r.split_version, "test_freeze_ref": r.test_freeze_ref}
            for r in used
        ]),
        "test_manifest_sha256": digest([record_to_dict(r) for r in used if r.split == "test"]),
        "test_sample_ids": [r.sample_id for r in used if r.split == "test"],
        "protocol": protocol,
    }


def accept_release(config_path: Path, output: Path) -> dict[str, Any]:
    workspace = Path(__file__).resolve().parents[3]
    config = load_yaml(config_path)
    if config["status"] != "accepted" or config["formulation"] != "B":
        raise DataContractError("Expected an explicitly approved Formulation B release config")
    for field in ("proposal_config", "approval", "source_config", "parent_config"):
        path = workspace / config[field]
        if sha256_file(path) != config[f"{field}_sha256"]:
            raise DataContractError(f"Approved release pin differs: {field}")
    proposal = load_yaml(workspace / config["proposal_config"])
    approval = json.loads((workspace / config["approval"]).read_text(encoding="utf-8"))
    parent = workspace / proposal["parent_package"]
    batch = workspace / config["approved_proposal"]
    verify_payload(parent)
    verify_payload(batch)
    if (sha256_file(parent / "checksums.sha256") != proposal["parent_checksums_sha256"]
            or sha256_file(batch / "checksums.sha256") != approval["proposal_payload_sha256"]
            or sha256_file(batch / "proposed-assignment.jsonl") != approval["assignment_sha256"]
            or sha256_file(workspace / approval["report"]) != approval["report_sha256"]
            or config["proposal_config_sha256"] != approval["proposal_config_sha256"]):
        raise DataContractError("Owner-approved report/package/assignment pins differ")
    previous = json.loads((parent / "release.json").read_text(encoding="utf-8"))
    if config["parent_config_sha256"] != previous["config_sha256"]:
        raise DataContractError("Parent derivation config differs from parent release")
    records = read_records(parent / "review-ledger.jsonl")
    pinned_rows = [json.loads(line) for line in (batch / "proposed-assignment.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()]
    if len(records) != 112 or propose_rows(records, proposal) != pinned_rows:
        raise DataContractError("Recomputed proposal differs from the approved exact 112 rows")
    accepted = apply_release_approval(
        records, proposal, approval, dataset_version=config["dataset_version"],
        split_version=config["split_version"], evidence_ref=config["approval"],
    )
    source_config = load_yaml(workspace / config["source_config"])
    roots = {r["id"]: workspace / r["root"]
             for r in source_config["sources"] + [source_config["roboflow"]]}
    if not output.resolve().is_relative_to(workspace) or any(
        output.resolve().is_relative_to(p.resolve()) for p in (parent, batch)
    ):
        raise DataContractError("Release destination must be a new workspace package")
    commit = git_commit()
    freeze = test_freeze_attestation(
        accepted, config_sha256=sha256_file(config_path), approval_sha256=config["approval_sha256"],
        owner_decision_ref=config["approval"], approval=approval, commit=commit,
        protocol=proposal["split_policy"]["test_access"],
    )
    metadata = {
        **previous, "status": "accepted", "dataset_version": config["dataset_version"],
        "config_sha256": sha256_file(config_path), "git_commit": commit,
        "git_dirty": git_is_dirty(), "owner_decision_ref": config["approval"],
        "owner_release_approval": approval,
        "owner_release_approval_sha256": config["approval_sha256"],
        "schema_config_review_ref": config["approval"] + "#schema_config",
        "split_config_review_ref": config["approval"] + "#split_config",
        "leakage_review_ref": config["approval"] + "#group_boundaries",
        "test_freeze_ref": "release.json#test_freeze", "test_freeze": freeze,
        "approved_use_scope": [approval["use_scope"]], "use_scope": approval["use_scope"],
        "split_policy": {**proposal["split_policy"], "version": config["split_version"],
                         "independence_status": "owner_accepted_visual_boundaries_for_local_pilot",
                         "test_freeze_status": "frozen"},
        "schema_policy": proposal["schema_policy"],
        "use_scope_limits": proposal["use_scope_limits"],
        "parent_payload_checksums_sha256": proposal["parent_checksums_sha256"],
        "parent_config_sha256": config["parent_config_sha256"],
        "source_config_sha256": config["source_config_sha256"],
        "approved_proposal_payload_sha256": approval["proposal_payload_sha256"],
        "source_attribution_refs": sorted({r.rights.attribution_ref for r in records}),
        "crop_policy_review_notes": (
            "RF28 reviewed person/context coordinates preserved exactly. SCB84 owner accepted "
            "the frozen source-anchor rectangles as person/context coordinates for this batch; "
            "no full-body or additional desk context inferred, no runtime padding approved."
        ),
        "implementation_sha256": {
            p.relative_to(workspace).as_posix(): sha256_file(p)
            for p in sorted(Path(__file__).parent.glob("pilot_*.py"))
        },
        "limitations": [
            "Reviewed crop release only; automatic runtime context crop gate remains pending",
            "Owner accepted conservative visual leakage boundaries for this local research pilot; "
            "video/session/room/person metadata remains unknown",
            "28 group-unresolved records retained review_only, outside the usage manifest",
            "Phone positives in RF and negatives in SCB are source-confounded",
            "Validation has one phone negative; test has only four known phone labels",
            "No model metrics, real-exam generalization or real-world holdout demonstrated",
            "No external upload/distribution authorized; DVC remote round-trip not performed",
        ],
        "remote_round_trip": "not_performed_local_only_scope",
    }
    selection = [json.loads(line) for line in (parent / "selection.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()]
    report = build_pilot_package(
        accepted, output, roots, {r.sample_id: parent / r.crop.crop_relpath
                                 for r in records if r.crop}, selection, metadata,
        expected_sample_ids=[r.sample_id for r in records],
    )
    if (sha256_file(output / "manifest.jsonl") != freeze["manifest_sha256"]
            or sha256_file(output / "split-assignment.jsonl") != freeze["split_assignment_sha256"]):
        raise DataContractError("Exported manifest/split differs from approved test freeze")
    return report


def build_proposals(config_path: Path, output: Path) -> dict[str, Any]:
    workspace = Path(__file__).resolve().parents[3]
    config = load_yaml(config_path)
    parent = workspace / config["parent_package"]
    pinned = config["parent_checksums_sha256"]
    if sha256_file(parent / "checksums.sha256") != pinned:
        raise DataContractError("Parent package checksum pin differs")
    verify_payload(parent)
    records = read_records(parent / "review-ledger.jsonl")
    if len(records) != 112:
        raise DataContractError("Pilot proposal must retain the exact 112-record parent")
    rows = propose_rows(records, config)
    output = validate_output(output, parent)
    if output.exists() and any(output.iterdir()):
        raise DataContractError("Proposal destination must be new/empty")
    output.mkdir(parents=True, exist_ok=True)
    (output / "proposed-assignment.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8",
        newline="\n",
    )
    slices = defaultdict(list)
    for row in rows:
        slices[row["source_id"], row["proposed_usage"], row["proposed_group_id"]].append(row)
    split_counts = {s: counts([r for r in rows if r["proposed_usage"] == s])
                    for s in ("train", "val", "test", "review_only")}
    used = sum(split_counts[s]["records"] for s in ("train", "val", "test"))
    report = {
        "status": config["status"], "proposal_version": config["proposal_version"],
        "parent_checksums_sha256": pinned, "config_sha256": sha256_file(config_path),
        "producer_sha256": sha256_file(Path(__file__)), "git_commit": git_commit(),
        "canonical_mutated": False, "training_release_accepted": False, "test_frozen": False,
        "canonical_coverage": coverage_report(records)["all"],
        "proposed_coverage": counts(rows), "proposed_split_support": split_counts,
        "proposed_groups": len(config["groups"]), "proposed_used_records": used,
        "actual_proposed_ratios": {s: split_counts[s]["records"] / used
                                   for s in ("train", "val", "test")},
        "review_only_ids": [r["sample_id"] for r in rows if r["proposed_split"] is None],
        "slices": [{"source_id": key[0], "proposed_usage": key[1], "proposed_group_id": key[2],
                    **counts(value)} for key, value in sorted(
                        slices.items(), key=lambda item: tuple(str(x) for x in item[0]))],
        "qa": config["qa"], "split_policy": config["split_policy"],
        "proposed_use_scope": config["proposed_use_scope"],
        "limitations": config["limitations"],
    }
    write_json(output / "summary.json", report)
    sheet = Image.new("RGB", (1080, 310 * max(
        1, (len(config["phone_negative_proposals"]) + 2) // 3
    )), "white")
    for index, proposal in enumerate(config["phone_negative_proposals"]):
        row = next(r for r in rows if r["sample_id"] == proposal["sample_id"])
        with Image.open(parent / row["parent_crop_relpath"]) as original:
            crop = original.convert("RGB")
        crop.thumbnail((350, 270))
        x, y = index % 3 * 360, index // 3 * 310
        sheet.paste(crop, (x + 5, y + 32))
        ImageDraw.Draw(sheet).text((x + 5, y + 5), f"DRAFT N: {row['sample_id']}", fill="black")
    sheet.save(output / "phone-negative-proposals.png")
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.relative_to(output).as_posix()}\n"
                for p in sorted(output.rglob("*")) if p.is_file()),
        encoding="utf-8", newline="\n",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--accept-release", action="store_true")
    args = parser.parse_args()
    try:
        action = accept_release if args.accept_release else build_proposals
        report = action(Path(args.config), Path(args.output_dir))
    except (DataContractError, OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Release proposal error: {exc}\n")
    print(json.dumps({k: v for k, v in report.items() if k in {
        "status", "proposed_used_records", "proposed_groups", "proposed_split_support",
        "records", "reviewed_crops", "checksums_sha256",
    }}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
