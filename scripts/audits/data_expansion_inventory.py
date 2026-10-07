"""Tạo kiểm kê metadata chỉ đọc và hàng đợi owner review cho việc mở rộng dữ liệu."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.provenance import git_commit, sha256_file
from ai_exam_monitoring.data.pilot_schema import read_records


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _counter(states: Counter[str]) -> dict[str, int]:
    return {state: states.get(state, 0) for state in ("positive", "negative", "unknown")}


def build_inventory(workspace: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    version = "pilot-b-20261005-v4"
    dataset = workspace / "data/processed/pilot-b" / version
    manifest_path = dataset / "manifest.jsonl"
    ledger_path = dataset / "review-ledger.jsonl"
    checksum_path = dataset / "checksums.sha256"
    config_path = workspace / "configs/datasets/pilot_b_release_v4.yaml"
    approval_path = (
        workspace
        / "artifacts/reports/pilot-b-release-acceptance-20261005/owner-approval.json"
    )
    report_path = (
        workspace
        / "artifacts/reports/pilot-b-release-acceptance-20261005/verification.json"
    )

    records = read_records(ledger_path)
    manifest = read_records(manifest_path)
    config = load_yaml(config_path)
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    verification = json.loads(report_path.read_text(encoding="utf-8"))
    ledger_ids = {record.sample_id for record in records}
    if len(records) != 112 or len(manifest) != 84 or not {
        record.sample_id for record in manifest
    } <= ledger_ids:
        raise ValueError("The pinned pilot-v4 inventory shape has changed")
    if (
        config.get("status") != "accepted"
        or config.get("dataset_version") != version
        or config.get("split_version") != manifest[0].split_version
        or config.get("approval_sha256") != sha256_file(approval_path)
        or verification.get("dataset_version") != version
        or verification.get("config_sha256") != sha256_file(config_path)
        or verification.get("owner_approval_sha256") != sha256_file(approval_path)
        or verification.get("checksums_sha256") != sha256_file(checksum_path)
        or approval.get("decision") != "approve_pilot_b_release"
    ):
        raise ValueError("The accepted dataset/config/approval hashes do not agree")

    by_source: dict[str, dict[str, Any]] = {}
    by_source_split: dict[str, dict[str, Any]] = {}
    groups: dict[str, list[Any]] = defaultdict(list)
    for record in records:
        source = record.source.source_id
        source_row = by_source.setdefault(
            source,
            {
                "records": 0,
                "unique_source_images": set(),
                "unique_crops": set(),
                "phone_use": Counter(),
                "looking_around": Counter(),
                "usage": Counter(),
            },
        )
        source_row["records"] += 1
        source_row["unique_source_images"].add(record.source.image_sha256)
        if record.crop:
            source_row["unique_crops"].add(record.crop.crop_sha256)
        source_row["phone_use"][record.phone_use.state] += 1
        source_row["looking_around"][record.looking_around.state] += 1
        source_row["usage"][record.usage] += 1

        split = record.usage if record.usage in {"train", "val", "test"} else "review_only"
        slice_key = f"{source}/{split}"
        slice_row = by_source_split.setdefault(
            slice_key,
            {"records": 0, "phone_use": Counter(), "looking_around": Counter()},
        )
        slice_row["records"] += 1
        slice_row["phone_use"][record.phone_use.state] += 1
        slice_row["looking_around"][record.looking_around.state] += 1

        group_id = record.group.leakage_group_id if record.group else None
        if group_id and record.usage in {"train", "val", "test"}:
            groups[group_id].append(record)

    serialized_sources = {}
    for source, row in sorted(by_source.items()):
        serialized_sources[source] = {
            "records": row["records"],
            "unique_source_images": len(row["unique_source_images"]),
            "unique_crops": len(row["unique_crops"]),
            "phone_use": _counter(row["phone_use"]),
            "looking_around": _counter(row["looking_around"]),
            "usage": dict(sorted(row["usage"].items())),
        }
    serialized_slices = {}
    for key, row in sorted(by_source_split.items()):
        serialized_slices[key] = {
            "records": row["records"],
            "phone_use": _counter(row["phone_use"]),
            "looking_around": _counter(row["looking_around"]),
        }

    group_slices = []
    for group_id, members in sorted(groups.items()):
        group_slices.append(
            {
                "group_id": group_id,
                "source_id": members[0].source.source_id,
                "split": members[0].usage,
                "records": len(members),
                "phone_use": _counter(Counter(r.phone_use.state for r in members)),
                "looking_around": _counter(
                    Counter(r.looking_around.state for r in members)
                ),
            }
        )

    review_queue: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: item.sample_id):
        if record.usage != "review_only":
            continue
        review_queue.append(
            {
                "sample_id": record.sample_id,
                "source_id": record.source.source_id,
                "source_image_sha256": record.source.image_sha256,
                "crop_sha256": record.crop.crop_sha256 if record.crop else None,
                "leakage_group_id": (
                    record.group.leakage_group_id if record.group else None
                ),
                "phone_use_state": record.phone_use.state,
                "looking_around_state": record.looking_around.state,
                "ineligibility_reasons": list(record.ineligibility_reasons),
                "next_review": "resolve_scene_group_then_owner_release_review",
                "training_eligible": False,
            }
        )

    source_image_ids: dict[str, list[str]] = defaultdict(list)
    for record in records:
        source_image_ids[record.source.image_sha256].append(record.sample_id)
    repeated_sources = [
        {"source_image_sha256": digest, "sample_ids": sorted(ids)}
        for digest, ids in sorted(source_image_ids.items())
        if len(ids) > 1
    ]

    overall_phone = Counter(record.phone_use.state for record in records)
    overall_looking = Counter(record.looking_around.state for record in records)
    overall_usage = Counter(record.usage for record in records)
    metadata_unknown = {
        field: sum(
            getattr(record.group, field) is None if record.group else True
            for record in records
        )
        for field in ("video_id", "session_id", "room_id", "subject_id")
    }

    evidence = {
        "schema_version": 1,
        "kind": "metadata_only_dataset_expansion_inventory",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": git_commit(),
        "dataset_version": version,
        "split_version": manifest[0].split_version,
        "target_encoding_version": records[0].target_encoding_version,
        "dataset_payload_checksum_list_sha256": hashlib.sha256(
            checksum_path.read_bytes()
        ).hexdigest(),
        "input_sha256": {
            path.relative_to(workspace).as_posix(): sha256_file(path)
            for path in (
                manifest_path,
                ledger_path,
                checksum_path,
                config_path,
                approval_path,
                report_path,
            )
        },
        "counts": {
            "ledger_records": len(records),
            "usage_records": len(manifest),
            "usage": dict(sorted(overall_usage.items())),
            "unique_source_images": len(source_image_ids),
            "unique_crops": len({r.crop.crop_sha256 for r in records if r.crop}),
            "reviewed_leakage_groups_in_usage": len(groups),
            "review_only_records": len(review_queue),
            "phone_use": _counter(overall_phone),
            "looking_around": _counter(overall_looking),
            "nonnull_group_metadata_records": {
                field: len(records) - missing
                for field, missing in metadata_unknown.items()
            },
        },
        "source_summary": serialized_sources,
        "source_usage_target_summary": serialized_slices,
        "group_summary": group_slices,
        "repeated_source_images": repeated_sources,
        "review_queue_count": len(review_queue),
        "test_handling": (
            "Only parsed test labels/IDs while validating the pinned manifest; "
            "test media was not inspected or used to select candidates."
        ),
    }
    return evidence, review_queue


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/reports/data-expansion-20261006"),
    )
    arguments = parser.parse_args()
    workspace = arguments.workspace.resolve()
    output = (workspace / arguments.output_dir).resolve()
    evidence, queue = build_inventory(workspace)
    _write_json(output / "inventory.json", evidence)
    _write_json(
        output / "review-queue.json",
        {"status": "proposal_pending_owner_review", "records": queue},
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "ledger_records": evidence["counts"]["ledger_records"],
                "usage_records": evidence["counts"]["usage_records"],
                "review_queue": len(queue),
                "output_dir": output.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
