"""Import explicit owner must-link decisions without declaring split independence."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import git_commit, git_is_dirty, sha256_file

from .pilot_package import build_pilot_package
from .pilot_schema import GroupReview, PilotRecord, ReviewEvidence, read_records
from .pilot_selection import source_file


def verify_payload(folder: Path) -> None:
    expected = {}
    for line in (folder / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        if relative in expected or sha256_file(source_file(folder, relative)) != digest:
            raise DataContractError("Pinned package/review payload differs")
        expected[relative] = digest
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob("*")
              if p.is_file() and p.relative_to(folder).as_posix() != "checksums.sha256"}
    if set(expected) != actual:
        raise DataContractError("Pinned package/review file inventory differs")


def import_group_decisions(
    records: list[PilotRecord], draft: dict[str, Any], template: dict[str, Any],
    proposals: dict[str, Any], *, reviewer: str, evidence_ref: str,
) -> tuple[list[PilotRecord], dict[str, Any]]:
    """A caller must supply evidence of the user's submission, not trust a file as intent."""
    if not reviewer.strip() or not evidence_ref.strip():
        raise DataContractError("Owner role and submission evidence are required")
    if set(draft) != set(template):
        raise DataContractError("Owner draft fields differ from the pinned review template")
    for key in ("schema_version", "status", "ledger_sha256", "selection_sha256",
                "training_release_accepted"):
        if draft[key] != template[key]:
            raise DataContractError(f"Owner draft pin differs: {key}")
    if draft["training_release_accepted"] is not False:
        raise DataContractError("Group review cannot accept a training release")
    try:
        date.fromisoformat(draft["reviewed_at"])
    except (TypeError, ValueError) as exc:
        raise DataContractError("Owner review requires an ISO review date") from exc
    original_images = {row["image_sha256"]: row for row in template["images"]}
    observed = draft["images"]
    if len(observed) != len(original_images):
        raise DataContractError("Owner draft image inventory differs")
    seen = set()
    notes = []
    for row in observed:
        digest = row["image_sha256"]
        if digest in seen or digest not in original_images:
            raise DataContractError("Owner draft has duplicate/unknown source image")
        seen.add(digest)
        original = original_images[digest]
        if set(row) != set(original) or row["sample_ids"] != original["sample_ids"]:
            raise DataContractError("Owner draft source membership differs")
        if row["proposed_group"] or row["evidence"] or row["uncertainty"] != "unknown":
            notes.append(row)
    by_id = {row.sample_id: row for row in records}
    inventory = {digest: sorted(r.sample_id for r in records
                               if r.source.image_sha256 == digest) for digest in original_images}
    if inventory != {digest: row["sample_ids"] for digest, row in original_images.items()}:
        raise DataContractError("Review template differs from the ledger source inventory")
    groups = {row["proposal_id"]: row for row in proposals["groups"]}
    expected_ids = {row["proposal_id"] for row in template["scene_decisions"]}
    decisions = draft["scene_decisions"]
    if (len(decisions) != len(groups) or set(groups) != expected_ids
            or {row["proposal_id"] for row in decisions} != expected_ids):
        raise DataContractError("Owner decisions must match every pinned proposal exactly once")
    parent = {digest: digest for digest in original_images}

    def find(node: str) -> str:
        while parent[node] != node:
            node = parent[node]
        return node

    edges = []
    approved_nodes = set()
    for decision in sorted(decisions, key=lambda row: row["proposal_id"]):
        if set(decision) != {"proposal_id", "decision", "reason"}:
            raise DataContractError("Unknown owner scene decision field")
        if decision["decision"] not in {"keep_together", "needs_change", "unresolved"}:
            raise DataContractError("Unsupported owner scene decision")
        reason = decision["reason"]
        if reason is not None and (not isinstance(reason, str) or not reason.strip()):
            raise DataContractError("Owner reason must be nonempty text or null")
        if decision["decision"] == "needs_change" and not reason:
            raise DataContractError("Changed groups require an explicit owner explanation")
        group = groups[decision["proposal_id"]]
        if not set(group["sample_ids"]).issubset(by_id):
            raise DataContractError("Proposal contains an unknown sample")
        if decision["decision"] != "keep_together":
            continue
        digests = sorted({by_id[sample].source.image_sha256 for sample in group["sample_ids"]})
        approved_nodes.update(digests)
        for other in digests[1:]:
            left, right = find(digests[0]), find(other)
            parent[max(left, right)] = min(left, right)
            edges.append({"left_sha256": digests[0], "right_sha256": other,
                          "proposal_id": group["proposal_id"], "owner_reason": reason})
    components: dict[str, list[str]] = defaultdict(list)
    for digest in sorted(approved_nodes):
        components[find(digest)].append(digest)
    assignment = {}
    component_rows = []
    for digests in sorted(components.values()):
        group_id = "PB-G-" + hashlib.sha256(
            ("pilot-b-owner-group-v1|" + "|".join(digests)).encode("utf-8")
        ).hexdigest()[:20]
        sample_ids = sorted(row.sample_id for row in records
                            if row.source.image_sha256 in digests)
        refs = [evidence_ref + "#" + key for key, group in sorted(groups.items())
                if any(sample in sample_ids for sample in group["sample_ids"])
                and next(row for row in decisions if row["proposal_id"] == key)["decision"]
                == "keep_together"]
        review = ReviewEvidence(reviewer, draft["reviewed_at"], evidence_ref)
        reviewed_group = GroupReview(group_id, tuple(refs), review)
        assignment.update(dict.fromkeys(sample_ids, reviewed_group))
        component_rows.append({"leakage_group_id": group_id, "image_sha256": digests,
                               "sample_ids": sample_ids, "independence_confirmed": False})
    updated = []
    for row in records:
        if row.split is not None or row.usage != "review_only":
            raise DataContractError("Group ingestion requires a review-only preparation ledger")
        reasons = tuple(reason for reason in row.ineligibility_reasons
                        if reason != "group_review_pending")
        reasons += ("group_boundary_independence_review_pending",)
        if row.sample_id in assignment:
            updated.append(replace(row, group=assignment[row.sample_id],
                                   ineligibility_reasons=reasons))
        else:
            updated.append(row)
    return updated, {
        "schema_version": "pilot-b-owner-groups-v1", "status": "owner_must_links_imported",
        "reviewer": reviewer, "reviewer_normalization": "explicit owner submission role",
        "reviewed_at": draft["reviewed_at"], "submission_evidence_ref": evidence_ref,
        "decision_counts": dict(Counter(row["decision"] for row in decisions)),
        "components": component_rows, "must_link_edges": edges,
        "group_assigned_records": len(assignment), "group_assigned_images": len(approved_nodes),
        "unresolved_sample_ids": sorted(set(by_id) - set(assignment)),
        "image_notes_pending_interpretation": notes,
        "inter_group_independence_confirmed": False,
        "possible_cross_component_relations": "Review deck uncertainty remains unresolved",
        "video_session_room_ids_inferred": False, "split_assigned": False,
        "training_release_accepted": False,
    }


def ingest_owner_groups(
    config: Path, package: Path, review_deck: Path, owner_file: Path,
    output: Path, evidence_dir: Path, *, reviewer: str, submission_ref: str,
) -> dict[str, Any]:
    workspace = Path(__file__).resolve().parents[3]
    package, review_deck = package.resolve(), review_deck.resolve()
    output, evidence_dir = output.resolve(), evidence_dir.resolve()
    verify_payload(package)
    verify_payload(review_deck)
    configuration = load_yaml(config)
    release = json.loads((package / "release.json").read_text(encoding="utf-8"))
    parent_config = workspace / configuration["parent_config"]["path"]
    if sha256_file(parent_config) != release["config_sha256"] or (
        configuration["parent_config"]["sha256"] != release["config_sha256"]
    ):
        raise DataContractError("Owner import parent configuration changed")
    original_config = load_yaml(parent_config)
    allowed = {"dataset_version", "output_dir", "parent_config"}
    if {k: v for k, v in configuration.items() if k not in allowed} != {
        k: v for k, v in original_config.items() if k not in allowed
    } or configuration["dataset_version"] == release["dataset_version"]:
        raise DataContractError("Group revision requires new version and unchanged source policy")
    records = read_records(package / "review-ledger.jsonl")
    template = json.loads((review_deck / "owner-review-draft.json").read_text(encoding="utf-8"))
    if (template["ledger_sha256"] != sha256_file(package / "review-ledger.jsonl")
            or template["selection_sha256"] != sha256_file(package / "selection.jsonl")):
        raise DataContractError("Review deck does not match the input package")
    owner_bytes = owner_file.read_bytes()
    draft = json.loads(owner_bytes.decode("utf-8-sig"))
    proposals = json.loads((review_deck / "scene-proposals.json").read_text(encoding="utf-8"))
    updated, report = import_group_decisions(
        records, draft, template, proposals, reviewer=reviewer, evidence_ref=submission_ref,
    )
    updated = [replace(row, dataset_version=configuration["dataset_version"]) for row in updated]
    sources = configuration["sources"] + [configuration["roboflow"]]
    roots = {source["id"]: workspace / source["root"] for source in sources}
    for destination in (output, evidence_dir):
        if not destination.is_relative_to(workspace) or any(destination.is_relative_to(path)
                for path in (package, review_deck, workspace / "data/raw", *roots.values())):
            raise DataContractError("Owner import output must be a new safe workspace artifact")
        if destination.exists() and any(destination.iterdir()):
            raise DataContractError("Owner import never overwrites an existing artifact")
    if output == evidence_dir or output.is_relative_to(evidence_dir) or evidence_dir.is_relative_to(
        output
    ):
        raise DataContractError("Evidence and package output must be separate directories")
    report.update({
        "owner_file_sha256": hashlib.sha256(owner_bytes).hexdigest(),
        "input_ledger_sha256": template["ledger_sha256"],
        "input_selection_sha256": template["selection_sha256"],
        "proposal_payload_sha256": sha256_file(review_deck / "scene-proposals.json"),
        "raw_owner_file": submission_ref,
    })
    crops = {row.sample_id: package / row.crop.crop_relpath for row in records if row.crop}
    selection = [json.loads(line) for line in (package / "selection.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()]
    fields = ("schema_version", "selection_version", "target_encoding_version",
              "crop_policy_version", "ledger_records", "reviewed_crops", "split_versions",
              "expected_sample_ids", "media_uploaded", "runtime_crop_ready")
    metadata = {key: value for key, value in release.items() if key not in fields}
    metadata.update({
        "git_commit": git_commit(), "git_dirty": git_is_dirty(),
        "dataset_version": configuration["dataset_version"], "config_sha256": sha256_file(config),
        "parent_config_sha256": release["config_sha256"],
        "implementation_sha256": {path.relative_to(workspace).as_posix(): sha256_file(path)
                                  for path in sorted(Path(__file__).parent.glob("pilot_*.py"))},
        "owner_group_review": report,
        "parent_payload_checksums_sha256": sha256_file(package / "checksums.sha256"),
    })
    result = build_pilot_package(
        updated, output, roots, crops, selection, metadata,
        expected_sample_ids=[row.sample_id for row in records],
    )
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "owner-review.json").write_bytes(owner_bytes)
    (evidence_dir / "group-decisions.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8",
        newline="\n",
    )
    return {"package": {key: value for key, value in result.items() if key != "payload_checksums"},
            "group_review": report}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for argument in ("config", "package", "review-deck", "owner-file", "output-dir",
                     "evidence-dir", "reviewer", "submission-ref"):
        parser.add_argument("--" + argument, required=True)
    args = parser.parse_args()
    try:
        result = ingest_owner_groups(
            Path(args.config), Path(args.package), Path(args.review_deck), Path(args.owner_file),
            Path(args.output_dir), Path(args.evidence_dir), reviewer=args.reviewer,
            submission_ref=args.submission_ref,
        )
    except (DataContractError, OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Owner group import error: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
