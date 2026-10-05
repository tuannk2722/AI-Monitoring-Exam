"""Generate SCB proposals or import an explicitly submitted owner batch approval."""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from collections import Counter
from dataclasses import asdict, dataclass, replace
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import git_commit, git_is_dirty, sha256_file, write_json

from .pilot_owner_groups import verify_payload
from .pilot_package import _preflight, build_pilot_package, coverage_report
from .pilot_schema import CropRef, PilotRecord, PixelBox, ReviewEvidence, TargetReview, read_records
from .yolo import YoloAnnotation


@dataclass(frozen=True)
class CropProposal:
    sample_id: str
    stratum: str
    source_class: str
    source_image_sha256: str
    source_label_sha256: str
    source_label_line_1based: int
    proposed_xyxy: tuple[int, int, int, int]
    crop_relpath: str
    crop_sha256: str
    proposed_looking_around: str
    proposed_phone_use: str = "unknown"
    proposed_work_context: str = "unknown"
    qa_note: str = "source_bbox_and_label_proposal_not_canonical_evidence"
    status: str = "draft_pending_owner_acceptance"


def anchor_bounds(selection: dict[str, Any], label: Path, size: tuple[int, int]) -> PixelBox:
    """Use the pinned source line, not an inferred full-body/person rectangle."""
    annotation = YoloAnnotation.parse(
        label.read_text(encoding="utf-8").splitlines()[selection["source_label_line_1based"] - 1]
    )
    if annotation.class_id != selection["source_class_id"]:
        raise DataContractError("Source class differs from frozen selection")
    width, height = size
    coordinates = (
        (annotation.x_center - annotation.width / 2) * width,
        (annotation.y_center - annotation.height / 2) * height,
        (annotation.x_center + annotation.width / 2) * width,
        (annotation.y_center + annotation.height / 2) * height,
    )
    if not (0 <= coordinates[0] < coordinates[2] <= width
            and 0 <= coordinates[1] < coordinates[3] <= height) or any(
        not math.isclose(a, b, rel_tol=0, abs_tol=1e-8)
        for a, b in zip(coordinates, selection["source_anchor_xyxy"], strict=True)
    ):
        raise DataContractError("Source anchor differs from pinned valid geometry")
    return PixelBox(math.floor(coordinates[0]), math.floor(coordinates[1]),
                    math.ceil(coordinates[2]), math.ceil(coordinates[3]))


def apply_batch_approval(
    records: list[PilotRecord], proposals: list[dict[str, Any]], approval: dict[str, Any],
    *, dataset_version: str, evidence_ref: str,
) -> list[PilotRecord]:
    """Approve only the submitted finite crop/looking batch; preserve all other gates."""
    if (approval.get("decision") != "approve_scb_crop_target_batch"
            or approval.get("exceptions") != [] or not approval.get("reviewer")
            or not evidence_ref or dataset_version == records[0].dataset_version):
        raise DataContractError("Explicit scoped batch approval and new dataset version required")
    date.fromisoformat(approval["reviewed_at"])
    pending = {row.sample_id: row for row in records if row.crop is None}
    ids = [row["sample_id"] for row in proposals]
    if len(ids) != 84 or len(set(ids)) != 84 or set(ids) != set(pending):
        raise DataContractError("Approval must match all frozen 84 SCB proposals")
    by_id = {row["sample_id"]: row for row in proposals}
    result = []
    for record in records:
        if record.sample_id not in pending:
            result.append(replace(record, dataset_version=dataset_version))
            continue
        row = by_id[record.sample_id]
        if (row["status"] != "draft_pending_owner_acceptance"
                or row["proposed_phone_use"] != "unknown"
                or row["source_image_sha256"] != record.source.image_sha256
                or row["source_label_sha256"] != record.source.label_sha256
                or row["source_label_line_1based"] != record.source.label_line_1based
                or row["crop_relpath"] != f"draft-crops/{record.sample_id}.png"):
            raise DataContractError("Approved proposal source identity or scope differs")
        evidence = ReviewEvidence(approval["reviewer"], approval["reviewed_at"],
                                  f"{evidence_ref}#{record.sample_id}", row["crop_sha256"])
        box = PixelBox(*row["proposed_xyxy"])
        result.append(replace(
            record, dataset_version=dataset_version,
            crop=CropRef("person-01", box, box, f"crops/{record.sample_id}.png",
                         row["crop_sha256"], evidence),
            looking_around=TargetReview(row["proposed_looking_around"],
                                       "owner_accepted_frozen_source_class_proposal", evidence),
            disposition="approved", owner_decision_ref=evidence.evidence_ref,
            ineligibility_reasons=tuple(reason for reason in record.ineligibility_reasons
                                       if reason != "person_crop_target_review_pending"),
        ))
    return result


def accept_batch(config_path: Path, output: Path) -> dict[str, Any]:
    workspace = Path(__file__).resolve().parents[3]
    config = load_yaml(config_path)
    parent, batch = workspace / config["parent_package"], workspace / config["approved_batch"]
    verify_payload(parent)
    verify_payload(batch)
    release = json.loads((parent / "release.json").read_text(encoding="utf-8"))
    parent_config, decision = workspace / config["parent_config"], workspace / config["approval"]
    if (config["status"] != "preparation_only"
            or sha256_file(parent_config) != release["config_sha256"]
            or sha256_file(parent / "checksums.sha256") != config["parent_checksums_sha256"]
            or sha256_file(batch / "checksums.sha256") != config["approved_batch_checksums_sha256"]
            or sha256_file(decision) != config["approval_sha256"]
            or (parent / "review-ledger.jsonl").read_bytes() != (
                batch / "review-ledger.jsonl").read_bytes()
            or (parent / "selection.jsonl").read_bytes() != (
                batch / "selection.jsonl").read_bytes()):
        raise DataContractError("Approved batch/parent/decision pins differ")
    approval = json.loads(decision.read_text(encoding="utf-8"))
    if approval["approved_batch_checksums_sha256"] != config["approved_batch_checksums_sha256"]:
        raise DataContractError("Owner decision references a different batch")
    proposals = [json.loads(line) for line in (batch / "proposals.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()]
    records = apply_batch_approval(
        read_records(parent / "review-ledger.jsonl"), proposals, approval,
        dataset_version=config["dataset_version"], evidence_ref=config["approval"],
    )
    source_config = load_yaml(parent_config)
    roots = {row["id"]: workspace / row["root"] for row in
             source_config["sources"] + [source_config["roboflow"]]}
    crops = {row["sample_id"]: batch / row["crop_relpath"] for row in proposals}
    crops.update({row.sample_id: parent / row.crop.crop_relpath for row in
                  read_records(parent / "review-ledger.jsonl") if row.crop})
    if not output.resolve().is_relative_to(workspace) or output.resolve().is_relative_to(
        batch.resolve()
    ) or output.resolve().is_relative_to(parent.resolve()):
        raise DataContractError("Accepted batch output must be a new workspace package")
    metadata = {**release, "dataset_version": config["dataset_version"],
                "config_sha256": sha256_file(config_path), "git_commit": git_commit(),
                "git_dirty": git_is_dirty(), "owner_scb_batch_approval": approval,
                "implementation_sha256": {
                    path.relative_to(workspace).as_posix(): sha256_file(path)
                    for path in sorted(Path(__file__).parent.glob("pilot_*.py"))
                },
                "parent_payload_checksums_sha256": config["parent_checksums_sha256"],
                "limitations": ["Frozen SCB anchor crops/looking labels owner accepted in batch",
                                "Source anchor extents retained; no padding/full body inferred",
                                "SCB phone/context remain unknown; no confirmed normal",
                                "Group independence/split/scope/config/release still pending",
                                "Automatic runtime crop remains a separate gate"]}
    selection = [json.loads(line) for line in (parent / "selection.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()]
    return build_pilot_package(records, output, roots, crops, selection, metadata,
                               expected_sample_ids=[row.sample_id for row in records])


def build_proposals(config_path: Path, output: Path) -> dict[str, Any]:
    config = load_yaml(config_path)
    workspace = Path(__file__).resolve().parents[3]
    package = (workspace / config["parent_package"]).resolve()
    parent_config = workspace / config["parent_config"]
    verify_payload(package)
    release = json.loads((package / "release.json").read_text(encoding="utf-8"))
    if (sha256_file(package / "checksums.sha256") != config["parent_checksums_sha256"]
            or sha256_file(parent_config) != release["config_sha256"]
            or config["status"] != "draft_proposals"
            or config["crop_rule"] != "source_anchor_outward_integer_bounds"):
        raise DataContractError("Proposal parent/config pin or draft policy mismatch")
    parent = load_yaml(parent_config)
    roots = {row["id"]: workspace / row["root"] for row in parent["sources"] + [parent["roboflow"]]}
    names = {row["id"]: row["source_names"] for row in parent["sources"]}
    records = read_records(package / "review-ledger.jsonl")
    selection = [json.loads(line) for line in (package / "selection.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()]
    pending = {row.sample_id: row for row in records if row.crop is None}
    if (len(records) != 112 or len(pending) != 84 or len(selection) != 84
            or {row["sample_id"] for row in selection} != set(pending)
            or Counter(row["stratum"] for row in selection) != {"turnhead": 28, "read": 28,
                                                                "write": 28}):
        raise DataContractError("Proposals require exact frozen 84 SCB + 28 RF membership")
    crops = {row.sample_id: package / row.crop.crop_relpath for row in records if row.crop}
    sources = _preflight(records, roots, crops)
    planned = []
    for row in sorted(selection, key=lambda row: row["sample_id"]):
        record = pending[row["sample_id"]]
        source_class = names[record.source.source_id][record.source.source_class_id]
        rule = config["source_class_rules"][row["stratum"]]
        if source_class != rule["source_class"]:
            raise DataContractError("Proposal rule differs from source taxonomy")
        if rule["looking_around"] not in {"positive", "negative", "unknown"}:
            raise DataContractError("Invalid proposed target state")
        box = anchor_bounds(row, roots[record.source.source_id] / record.source.label_relpath,
                            (record.source.image_width, record.source.image_height))
        planned.append((row, record, source_class, rule, box))
    output = output.resolve()
    if (not output.is_relative_to(workspace) or any(output.is_relative_to(path.resolve())
            for path in (package, workspace / "data/raw", *roots.values()))
            or output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise DataContractError("Proposal output must be a new safe workspace directory")
    (output / "draft-crops").mkdir(parents=True)
    (output / "reports").mkdir()
    shutil.copyfile(package / "review-ledger.jsonl", output / "review-ledger.jsonl")
    shutil.copyfile(package / "selection.jsonl", output / "selection.jsonl")
    for record in records:
        if record.crop:
            target = output / record.crop.crop_relpath
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(crops[record.sample_id], target)
    proposals = []
    sheets = {stratum: Image.new("RGB", (1680, 2100), "white") for stratum in
              ("turnhead", "read", "write")}
    positions: Counter[str] = Counter()
    for row, record, source_class, rule, box in planned:
        relative = f"draft-crops/{record.sample_id}.png"
        with Image.open(sources[record.sample_id]) as image:
            source = image.convert("RGB")
        crop = source.crop(box.xyxy)
        crop.save(output / relative)
        proposal = CropProposal(
            record.sample_id, row["stratum"], source_class, record.source.image_sha256,
            record.source.label_sha256, record.source.label_line_1based, box.xyxy, relative,
            sha256_file(output / relative), rule["looking_around"],
            proposed_work_context=rule["work_context"],
            qa_note=config.get("qa_notes", {}).get(
                record.sample_id, "source_bbox_and_label_proposal_not_canonical_evidence"
            ),
        )
        proposals.append(asdict(proposal))
        # Static audit images only; overlays never enter crop pixels.
        ImageDraw.Draw(source).rectangle(box.xyxy, outline="red", width=3)
        source.thumbnail((202, 240))
        crop.thumbnail((202, 240))
        index = positions[row["stratum"]]
        x, y = (index % 4) * 420, (index // 4) * 300
        sheet = sheets[row["stratum"]]
        sheet.paste(source, (x + 4, y + 48))
        sheet.paste(crop, (x + 214, y + 48))
        ImageDraw.Draw(sheet).text((x + 4, y + 4),
                                  f"DRAFT {record.sample_id}\n{source_class}: looking "
                                  f"{rule['looking_around']} / phone unknown", fill="black")
        positions[row["stratum"]] += 1
    for stratum, sheet in sheets.items():
        sheet.save(output / "reports" / f"{stratum}.png")
    (output / "proposals.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in proposals), encoding="utf-8",
        newline="\n",
    )
    with (output / "proposals.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(proposals[0]))
        writer.writeheader()
        writer.writerows(proposals)
    report = {
        "status": "draft_pending_owner_acceptance", "proposal_version": config["proposal_version"],
        "records": 112, "scb_draft_crops": 84, "rf_reviewed_crops_preserved": 28,
        "proposed_looking_around": dict(Counter(
            row["proposed_looking_around"] for row in proposals
        )),
        "proposed_phone_use": {"unknown": 84}, "proposed_normal": {"unknown": 84},
        "canonical_coverage": coverage_report(records)["all"],
        "parent_checksums_sha256": config["parent_checksums_sha256"],
        "config_sha256": sha256_file(config_path), "producer_sha256": sha256_file(Path(__file__)),
        "git_commit": git_commit(), "git_dirty": git_is_dirty(),
        "training_release_accepted": False, "split_assigned": False,
        "limitations": [
            "Source boxes may omit visible person parts or desk context; no body/padding inferred",
            "Source-class label suggestions are weak proposals, not reviewed target evidence",
            "Phone absence and normal cannot be inferred from SCB source classes",
            "Canonical ledger unchanged; owner may accept/reject proposals or list exceptions",
            "Grouping, split, scope and release gates remain unresolved",
        ],
        "flagged_for_acceptance": config.get("qa_notes", {}),
    }
    write_json(output / "reports" / "summary.json", report)
    (output / "REVIEW.md").write_text(
        "# SCB pilot proposals\n\n"
        "84 source-bbox crops + 28 unchanged reviewed Roboflow crops.\n\n"
        "View `reports/turnhead.png`, `reports/read.png`, `reports/write.png`: "
        "source on the left (red anchor), clean candidate crop on the right. "
        "Full crop bytes: `draft-crops/`. Coordinates/hashes/labels: `proposals.csv`.\n\n"
        "TurnHead suggests looking positive; read/write suggest looking negative. "
        "These are weak source-class proposals, NOT verified absence/presence. "
        "Phone and normal remain unknown. Source boxes may omit visible person/desk parts.\n\n"
        "Owner may accept/reject this batch or list sample IDs with exceptions. "
        "No drawing, HTML form, or manual crop export is required. "
        "See `reports/summary.json` for flagged cases and separate canonical coverage. "
        "Approval of proposals does not approve independent groups, split, or training release.\n",
        encoding="utf-8", newline="\n",
    )
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256_file(path)}  {path.relative_to(output).as_posix()}\n"
                for path in sorted(output.rglob("*")) if path.is_file()),
        encoding="utf-8", newline="\n",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--accept-batch", action="store_true")
    args = parser.parse_args()
    try:
        action = accept_batch if args.accept_batch else build_proposals
        report = action(Path(args.config), Path(args.output_dir))
    except (DataContractError, OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        parser.exit(2, f"SCB proposal error: {exc}\n")
    print(json.dumps({key: value for key, value in report.items()
                      if key not in {"canonical_coverage", "payload_checksums"}},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
