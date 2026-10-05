"""Create a structured, local review-only pilot package from frozen inputs."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

from PIL import Image

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import git_commit, git_is_dirty, sha256_file

from .pilot_inputs import rf_label_path, verify_archive_member, verify_pin
from .pilot_package import build_pilot_package
from .pilot_schema import (
    TARGET_ENCODING_VERSION,
    ContextReview,
    CropRef,
    GroupReview,
    PilotRecord,
    PixelBox,
    ReviewEvidence,
    RightsReview,
    SourceRef,
    TargetReview,
)
from .pilot_selection import source_file


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def create_ledger(
    selection: list[dict[str, Any]], rf_rows: list[dict[str, Any]],
    configuration: dict[str, Any], workspace: Path,
) -> tuple[list[PilotRecord], dict[str, Path], dict[str, Path]]:
    """Import only actual historic approvals; selected SCB rows remain unknown."""
    version_fields = {
        key: configuration[key]
        for key in ("dataset_version", "selection_version", "crop_policy_version")
    }
    roots = {row["id"]: workspace / row["root"] for row in configuration["sources"]}
    rf_config = configuration["roboflow"]
    roots[rf_config["id"]] = workspace / rf_config["root"]
    records = []
    crop_inputs = {}
    scb_rights = RightsReview(
        license_id="owner-confirmed-source-permission",
        attribution_ref="docs/data/candidates/SCB5-supplied-20261003.md",
        approved_use_scope=("local-preparation",),
        review=ReviewEvidence(
            reviewer="repository_owner", reviewed_at="2026-10-04",
            evidence_ref="docs/data/candidates/SCB5-supplied-20261003.md",
        ),
    )
    for row in selection:
        records.append(PilotRecord(
            sample_id=row["sample_id"], **version_fields,
            source=SourceRef(
                source_id=row["source_id"], archive_sha256=row["archive_sha256"],
                image_relpath=row["source_image_relpath"], image_sha256=row["source_image_sha256"],
                image_width=row["width"], image_height=row["height"],
                label_relpath=row["source_label_relpath"], label_sha256=row["source_label_sha256"],
                label_line_1based=row["source_label_line_1based"],
                source_class_id=row["source_class_id"], original_split="train",
                aliases=tuple(row["exact_aliases"]),
            ),
            phone_use=TargetReview("unknown", "SCB_target_not_reviewed"),
            looking_around=TargetReview("unknown", "SCB_target_not_reviewed"),
            work_context_review=ContextReview("unknown", "work_context_not_reviewed"),
            rights=scb_rights, group=GroupReview(),
            ineligibility_reasons=(
                "person_crop_target_review_pending", "group_review_pending", "split_config_pending",
                "schema_config_membership_review_pending", "release_review_pending",
            ),
        ))
    rf_rights = RightsReview(
        license_id="CC-BY-4.0-source-declaration",
        attribution_ref="docs/data/candidates/Roboflow-phone-use-20261004.md",
    )
    for row in rf_rows:
        if any(row[target] not in {"owner_approved_positive", "unknown"}
               for target in ("phone_use", "looking_around")):
            raise DataContractError("Unsupported RF state; preserve only pinned P/U approvals")
        image_path = source_file(roots[rf_config["id"]], row["source_image"])
        verify_pin(image_path, row["image_sha256"])
        with Image.open(image_path) as image:
            width, height = image.size
        crop_path = source_file(workspace, row["crop_path"])
        verify_pin(crop_path, row["crop_sha256"])
        evidence = ReviewEvidence(
            reviewer="repository_owner", reviewed_at="2026-10-04",
            evidence_ref=f"{rf_config['review_bundle']}#current_person_crops/{row['id']}",
            crop_sha256=row["crop_sha256"],
        )
        label_relative = rf_label_path(row["source_image"])
        label_path = source_file(roots[rf_config["id"]], label_relative)
        with zipfile.ZipFile(rf_config["archive"]) as archive:
            label_sha = verify_archive_member(archive, label_relative, label_path)
        targets = {
            key: TargetReview(
                "positive", "explicit_owner_approved_positive", evidence,
            ) if row[key] == "owner_approved_positive" else TargetReview(
                "unknown", "target_not_approved_in_RF_snapshot",
            )
            for key in ("phone_use", "looking_around")
        }
        records.append(PilotRecord(
            sample_id=row["id"], **version_fields,
            source=SourceRef(
                source_id=rf_config["id"], archive_sha256=rf_config["archive_sha256"],
                image_relpath=row["source_image"], image_sha256=row["image_sha256"],
                image_width=width, image_height=height, label_relpath=label_relative,
                label_sha256=label_sha, original_split="train",
            ),
            crop=CropRef(
                person_id=row["id"], person_box=PixelBox(*row["person_xyxy"]),
                context_box=PixelBox(*row["context_crop_xyxy"]),
                crop_relpath=f"crops/{row['id']}.png",
                crop_sha256=row["crop_sha256"], review=evidence,
            ),
            phone_use=targets["phone_use"], looking_around=targets["looking_around"],
            work_context_review=ContextReview("unknown", "work_context_not_reviewed"),
            rights=rf_rights, group=GroupReview(), disposition="approved",
            owner_decision_ref=evidence.evidence_ref,
            ineligibility_reasons=(
                "group_review_pending", "split_config_pending", "release_review_pending",
                "schema_config_membership_review_pending", "RF_training_scope_review_pending",
            ),
        ))
        crop_inputs[row["id"]] = crop_path
    return records, roots, crop_inputs


def prepare_package(
    config_path: str | Path, *, inputs_dir: str | Path, output_dir: str | Path,
) -> dict[str, Any]:
    workspace = Path(__file__).resolve().parents[3]
    config_path = Path(config_path).resolve()
    configuration = load_yaml(config_path)
    inputs_dir = Path(inputs_dir).resolve()
    pins = json.loads((inputs_dir / "input-pins.json").read_text(encoding="utf-8"))
    verify_pin(config_path, pins["config_sha256"])
    if (
        configuration.get("formulation") != "B"
        or configuration.get("status") != "preparation_only"
        or configuration.get("target_encoding_version") != TARGET_ENCODING_VERSION
    ):
        raise DataContractError("Unsupported pilot preparation formulation/status/target encoding")
    selection_path = inputs_dir / "selection.jsonl"
    verify_pin(selection_path, pins["selection_sha256"])
    selection = _read_jsonl(selection_path)
    rf_rows = _read_jsonl(inputs_dir / "roboflow-inputs.jsonl")
    if len(selection) != 84 or len(rf_rows) != 28:
        raise DataContractError("Pilot requires exactly 84 SCB selection rows and 28 RF records")
    # Re-import the pinned canonical RF snapshot, not an editable preparation summary.
    rf_config = configuration["roboflow"]
    verify_pin(Path(rf_config["archive"]), rf_config["archive_sha256"])
    review_path = workspace / rf_config["review_bundle"]
    verify_pin(review_path, rf_config["review_bundle_sha256"])
    canonical = json.loads(review_path.read_text(encoding="utf-8"))["current_person_crops"]
    if sorted(rf_rows, key=lambda row: row["id"]) != sorted(canonical, key=lambda row: row["id"]):
        raise DataContractError("RF input records differ from pinned canonical approvals")
    records, source_roots, crop_inputs = create_ledger(selection, rf_rows, configuration, workspace)
    expected_ids = [row["sample_id"] for row in selection] + rf_config["expected_ids"]
    metadata = {
        "status": "prepared_pending_gates", "dataset_version": configuration["dataset_version"],
        "git_commit": git_commit(), "config_sha256": sha256_file(config_path), "input_pins": pins,
        "git_dirty": git_is_dirty(),
        "implementation_sha256": {
            path.relative_to(workspace).as_posix(): sha256_file(path)
            for path in sorted(Path(__file__).parent.glob("pilot_*.py"))
        },
        "build_environment": {
            "python": sys.version,
            "Pillow": importlib.metadata.version("Pillow"),
            "PyYAML": importlib.metadata.version("PyYAML"),
        },
        "expected_source_counts": {"scb_head": 28, "scb_hrw": 56, "roboflow_v1": 28},
        "expected_selection_count": 84,
        "limitations": [
            "SCB source anchors are not approved person/crop/target labels",
            "No group metadata: cluster proposals require owner review; no independent split",
            "RF 28 approved crops retain 27 partial targets; no reviewed negatives/normal",
            "Schema/config/membership and release gates remain pending owner review",
            "Crop runtime policy is a separate gate before baseline B end-to-end",
        ],
    }
    return build_pilot_package(
        records, output_dir=Path(output_dir), source_roots=source_roots, crop_inputs=crop_inputs,
        selection_rows=selection, metadata=metadata, expected_sample_ids=expected_ids,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build local pilot B staging; never auto-accept data"
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--inputs-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    try:
        report = prepare_package(
            args.config, inputs_dir=args.inputs_dir, output_dir=args.output_dir,
        )
    except (DataContractError, OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"Pilot staging error: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
