"""Pin local inputs and freeze the finite SCB selection/RF identity set for pilot B."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops

from ai_exam_monitoring.common.config import load_yaml, require
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import git_commit, sha256_file

from .pilot_selection import inventory_anchors, select_round_robin, source_file, write_selection
from .source_layout import validate_output


def verify_pin(path: Path, expected: str) -> str:
    actual = sha256_file(path)
    if actual != expected:
        raise DataContractError(f"Input SHA differs from pinned contract/config: {path.name}")
    return actual


def read_bundle(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    for key, record in payload.get("records", {}).items():
        actual = hashlib.sha256(record["text"].encode("utf-8")).hexdigest()
        if actual != record["sha256"]:
            raise DataContractError(f"Historical evidence SHA differs: {key}")
    return payload


def rf_label_path(image_relative: str) -> str:
    if "/images/" not in image_relative:
        raise DataContractError("RF source image must belong to an images directory")
    return image_relative.replace("/images/", "/labels/").rsplit(".", 1)[0] + ".txt"


def verify_archive_member(archive: zipfile.ZipFile, relative: str, file: Path) -> str:
    """Check extracted provenance bytes without interpreting source labels as targets."""
    try:
        expected = hashlib.sha256(archive.read(relative)).hexdigest()
    except KeyError as exc:
        raise DataContractError(f"Source member is absent from pinned archive: {relative}") from exc
    return verify_pin(file, expected)


def validate_rf_inputs(
    configuration: dict[str, Any], workspace: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    archive_path = Path(require(configuration, "archive"))
    verify_pin(archive_path, str(require(configuration, "archive_sha256")))
    review_path = workspace / str(require(configuration, "review_bundle"))
    verify_pin(review_path, str(require(configuration, "review_bundle_sha256")))
    audit_path = workspace / str(require(configuration, "audit_bundle"))
    verify_pin(audit_path, str(require(configuration, "audit_bundle_sha256")))
    bundle = read_bundle(review_path)
    read_bundle(audit_path)
    crops = bundle["current_person_crops"]
    expected = configuration["expected_ids"]
    ids = [row["id"] for row in crops]
    if len(ids) != 28 or len(set(ids)) != 28 or set(ids) != set(expected) or len(expected) != 28:
        raise DataContractError("RF membership must be exactly the 28 approved contract IDs")
    root = workspace / str(require(configuration, "root"))
    with zipfile.ZipFile(archive_path) as archive:
        for row in crops:
            if row["training_eligible"] is not False:
                raise DataContractError("Historical RF snapshot must remain outside training")
            if row["person_status"] != "owner_approved" or row["crop_status"] != "owner_approved":
                raise DataContractError("RF person/crop approval differs from historical snapshot")
            if not row.get("owner_answers"):
                raise DataContractError("RF owner review evidence is required")
            image_path = source_file(root, row["source_image"])
            verify_pin(image_path, row["image_sha256"])
            if hashlib.sha256(archive.read(row["source_image"])).hexdigest() != row["image_sha256"]:
                raise DataContractError("RF source image differs from pinned archive")
            label_relative = rf_label_path(row["source_image"])
            verify_archive_member(archive, label_relative, source_file(root, label_relative))
            crop_path = source_file(workspace, row["crop_path"])
            verify_pin(crop_path, row["crop_sha256"])
            with Image.open(image_path) as source, Image.open(crop_path) as crop:
                expected_crop = source.convert("RGB").crop(row["context_crop_xyxy"])
                actual_crop = crop.convert("RGB")
                if expected_crop.size != actual_crop.size or ImageChops.difference(
                    expected_crop, actual_crop
                ).getbbox() is not None:
                    raise DataContractError(
                        f"RF crop pixels differ from approved rectangle: {row['id']}"
                    )
            states = (row["phone_use"], row["looking_around"])
            if any(state not in {"owner_approved_positive", "unknown"} for state in states):
                raise DataContractError(
                    "Unexpected RF target state; no automatic negatives allowed"
                )
    counts = {
        target: Counter(row[target] for row in crops)
        for target in ("phone_use", "looking_around")
    }
    if (
        counts["phone_use"]["owner_approved_positive"] != 24
        or counts["looking_around"]["owner_approved_positive"] != 5
        or sum(row["phone_use"] == row["looking_around"] == "owner_approved_positive"
               for row in crops) != 1
    ):
        raise DataContractError("RF target coverage differs from reviewed contract")
    return sorted(crops, key=lambda row: row["id"]), {
        "archive_sha256": configuration["archive_sha256"],
        "review_bundle_sha256": configuration["review_bundle_sha256"],
        "audit_bundle_sha256": configuration["audit_bundle_sha256"],
        "crop_count": len(crops), "image_count": len({row["image_sha256"] for row in crops}),
        "target_counts": {key: dict(value) for key, value in counts.items()},
        "approved_crop_hashes": {row["id"]: row["crop_sha256"] for row in crops},
    }


def freeze_inputs(config_path: str | Path, *, output_dir: str | Path | None = None) -> dict:
    config_path = Path(config_path).resolve()
    workspace = Path(__file__).resolve().parents[3]
    configuration = load_yaml(config_path)
    if configuration.get("formulation") != "B" or configuration.get("status") != "preparation_only":
        raise DataContractError("This command requires a preparation-only Formulation B config")
    selection = require(configuration, "selection")
    if (
        selection.get("rank_namespace") != "pilot-b-selection-v1"
        or selection.get("stratum_order") != ["turnhead", "read", "write"]
        or selection.get("quota_per_stratum") != 28
    ):
        raise DataContractError("Selection policy differs from the owner-reviewed pilot B contract")
    audit_bundle = configuration["scb_audit_bundle"]
    verify_pin(workspace / audit_bundle["path"], audit_bundle["sha256"])
    read_bundle(workspace / audit_bundle["path"])
    duplicate_path = workspace / configuration["scb_duplicates"]
    duplicate_report = json.loads(duplicate_path.read_text(encoding="utf-8"))
    aliases = {
        row["sha256"]: tuple(sorted(f"{member['source']}:{member['image']}"
                                     for member in row["members"]))
        for row in duplicate_report["groups"]
    }
    candidates = []
    source_pins = {}
    for source in configuration["sources"]:
        archive_path = Path(source["archive"])
        verify_pin(archive_path, source["archive_sha256"])
        report_path = workspace / source["audit"]
        verify_pin(report_path, source["audit_sha256"])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        names = {int(key): value for key, value in report["source_names"].items()}
        if names != source["source_names"]:
            raise DataContractError("Source namespace differs from pinned source names")
        source_root = workspace / source["root"]
        source_candidates = inventory_anchors(
            report, source_id=source["id"], source_root=source_root,
            archive_sha256=source["archive_sha256"], strata_by_class=source["strata_by_class"],
            rank_namespace=selection["rank_namespace"], aliases_by_sha=aliases,
            archive_path=archive_path, archive_prefix=source["archive_prefix"],
        )
        candidates.extend(source_candidates)
        source_pins[source["id"]] = {
            "archive_sha256": source["archive_sha256"], "audit_sha256": source["audit_sha256"],
            "verified_anchor_count": len(source_candidates),
            "verified_image_count": len({row.source_image_sha256 for row in source_candidates}),
        }
    selected = select_round_robin(
        candidates, stratum_order=tuple(selection["stratum_order"]),
        quota_per_stratum=selection["quota_per_stratum"],
    )
    rf_rows, rf_pins = validate_rf_inputs(configuration["roboflow"], workspace)
    destination = Path(output_dir or workspace / configuration["output_dir"]).resolve()
    for source in configuration["sources"] + [configuration["roboflow"]]:
        validate_output(destination, (workspace / source["root"]).resolve())
    if destination.exists() and any(destination.iterdir()):
        raise DataContractError(
            "Preparation output is not empty; use a new version, never overwrite"
        )
    destination.mkdir(parents=True, exist_ok=True)
    write_selection(destination / "selection.jsonl", selected)
    write_selection(destination / "roboflow-inputs.jsonl", rf_rows)
    report = {
        "schema_version": 1, "status": "selected_pending_owner_review",
        "dataset_version": configuration["dataset_version"],
        "selection_version": configuration["selection_version"],
        "contract_id": configuration["contract_id"], "git_commit": git_commit(),
        "config_sha256": sha256_file(config_path), "source_pins": source_pins,
        "scb_audit_bundle_sha256": audit_bundle["sha256"],
        "duplicate_report_sha256": sha256_file(duplicate_path), "roboflow": rf_pins,
        "selection_sha256": sha256_file(destination / "selection.jsonl"),
        "scb_selected": len(selected),
        "stratum_counts": dict(Counter(row["stratum"] for row in selected)),
        "scb_unique_image_sha": len({row["source_image_sha256"] for row in selected}),
        "ledger_input_count": len(selected) + len(rf_rows),
        "owner_selection_review": "pending", "dataset_accepted": False,
        "group_metadata": "not_supplied; visual_cluster_review_required",
    }
    (destination / "input-pins.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze finite pilot B inputs; no labels/split approval"
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    try:
        report = freeze_inputs(args.config, output_dir=args.output_dir)
    except (DataContractError, OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"Pilot preparation error: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
