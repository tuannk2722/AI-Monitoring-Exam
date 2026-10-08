"""Đóng release từ assignment đã được owner nghiệm thu, không chọn lại dữ liệu."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .pilot_inputs import verify_pin
from .pilot_owner_groups import verify_payload
from .pilot_package import build_pilot_package
from .pilot_release_proposals import test_freeze_attestation
from .pilot_schema import (
    ContextReview,
    CropRef,
    GroupReview,
    PilotRecord,
    PixelBox,
    ReviewEvidence,
    RightsReview,
    SourceRef,
    TargetReview,
    read_records,
    validate_records,
)


def materialize_records(
    parents: list[PilotRecord],
    assignment: list[dict[str, Any]],
    config: dict[str, Any],
    approval: dict[str, Any],
) -> list[PilotRecord]:
    """Chuyển đúng nhãn/usage được duyệt; bảo vệ những mẫu parent đang dùng."""
    if approval["decision"] != "approve_pilot_b_v6_release":
        raise DataContractError("Thiếu approval đóng release v6")
    before = {r.sample_id: r for r in parents}
    evidence_ref = config["approval"]["path"]
    evidence = ReviewEvidence(approval["reviewer"], approval["reviewed_at"], evidence_ref)
    result = []
    if len({a["sample_id"] for a in assignment}) != len(assignment):
        raise DataContractError("Assignment trùng ID")
    if not set(before).issubset({a["sample_id"] for a in assignment}):
        raise DataContractError("Assignment thiếu parent")
    for a in assignment:
        i = a["sample_id"]
        old = before.get(i)
        usage = a["proposed_usage"]
        crop_evidence = replace(evidence, crop_sha256=a["crop_sha256"])
        if old:
            if a["source_image_sha256"] != old.source.image_sha256 or a["crop_sha256"] != (
                old.crop.crop_sha256 if old.crop else None
            ):
                raise DataContractError("Không đổi source/crop parent")
            if old.usage in {"train", "val", "test"} and (
                usage != old.usage
                or old.group is None
                or a["proposed_group_id"] != old.group.leakage_group_id
                or any(
                    a[k] != getattr(old, k).state
                    for k in ("phone_use", "looking_around", "work_context_review")
                )
            ):
                raise DataContractError("Không đổi membership/nhãn/group parent đã dùng")
            changes: dict[str, Any] = {}
            for key in ("phone_use", "looking_around", "work_context_review"):
                value = getattr(old, key)
                if a[key] != value.state:
                    if old.usage != "review_only" or value.state != "unknown":
                        raise DataContractError("Chỉ điền unknown của parent review_only đã duyệt")
                    model = ContextReview if key == "work_context_review" else TargetReview
                    changes[key] = model(a[key], a["observation"], crop_evidence)
            record = replace(old, **changes)
        else:
            p = a["source_provenance"]
            source = SourceRef(
                p["source_id"],
                p["archive_sha256"],
                p["source_image_relpath"],
                p["source_image_sha256"],
                p["width"],
                p["height"],
                p["source_label_relpath"],
                p["source_label_sha256"],
                p["source_label_line_1based"],
                p["source_class_id"],
                "train",
            )
            box = PixelBox(**a["context_box"])
            crop = CropRef(i, box, box, f"crops/{i}.png", a["crop_sha256"], crop_evidence)
            record = PilotRecord(
                sample_id=i,
                dataset_version=config["dataset_version"],
                selection_version=config["selection_version"],
                crop_policy_version=config["crop_policy_version"],
                source=source,
                phone_use=TargetReview(a["phone_use"], a["observation"], crop_evidence),
                looking_around=TargetReview(a["looking_around"], a["observation"], crop_evidence),
                work_context_review=ContextReview(
                    a["work_context_review"], a["observation"], crop_evidence
                ),
                rights=RightsReview(
                    "CC-BY-4.0",
                    config["rights_attribution"]["path"],
                    tuple(config["approved_use_scope"]),
                    evidence,
                ),
                crop=crop,
                ineligibility_reasons=("Đang materialize quyết định đã duyệt.",),
            )
        group = record.group
        if not group or group.leakage_group_id != a["proposed_group_id"]:
            group = GroupReview(a["proposed_group_id"], (config["assignment"]["path"],), evidence)
        used = usage in {"train", "val", "test"}
        rights = record.rights
        if used and rights.approved_use_scope != tuple(config["approved_use_scope"]):
            if old and old.usage in {"train", "val", "test"}:
                raise DataContractError("Không đổi scope parent đang dùng")
            if not rights.license_id or not rights.attribution_ref:
                raise DataContractError("Thiếu metadata quyền nguồn đã kiểm")
            rights = replace(
                rights, approved_use_scope=tuple(config["approved_use_scope"]), review=evidence
            )
        record = replace(
            record,
            rights=rights,
            dataset_version=config["dataset_version"],
            selection_version=config["selection_version"],
            crop_policy_version=config["crop_policy_version"],
            disposition="excluded" if usage == "excluded" else "approved",
            usage=usage,
            split=usage if used else None,
            split_version=config["split_version"] if used else None,
            group=group,
            owner_decision_ref=evidence_ref,
            release_review=evidence,
            ineligibility_reasons=(a["observation"],) if usage == "review_only" else (),
            exclusion_reason=a["observation"] if usage == "excluded" else None,
            use_scope=config["approved_use_scope"][0] if used else record.use_scope,
        )
        result.append(record)
    if dict(Counter(r.usage for r in result)) != approval["approved_counts"]:
        raise DataContractError("Counts khác approval")
    validate_records(result)
    return result


def finalize_new_package(output: Path, workspace: Path) -> dict[str, str]:
    """Hoàn thiện tài liệu trước khi phát hành pointer lần đầu; không dùng cho release cũ."""
    release = json.loads((output / "release.json").read_text(encoding="utf8"))
    records = read_records(output / "review-ledger.jsonl")
    counts = Counter(r.usage for r in records)
    card = (
        f"# Pilot B — {release['dataset_version']}\n\n"
        f"Trạng thái: accepted. {len(records)} record; {release['reviewed_crops']} crop. "
        f"Manifest: {counts['train']} train / {counts['val']} val / {counts['test']} test.\n\n"
        "Chỉ dùng `manifest.jsonl` cho nghiên cứu classifier local. Ledger/crops còn chứa "
        f"{counts['review_only']} review_only; {counts['excluded']} excluded chỉ giữ metadata. "
        "Không lấy toàn bộ thư mục crops làm tập train.\n\n"
        "Hai target `[phone_use, looking_around]`; unknown = null/mask 0. "
        "Giữ crop/source/nhãn/group của 104 mẫu v5 đang dùng, gồm 13 val lịch sử và 11 test. "
        "Val mở rộng không so trực tiếp metric E002. Hash manifest mới phản ánh version "
        "đóng gói; không mở quyền inference test mới.\n\n"
        "Evidence: `review-ledger.jsonl`, `release.json`; QA/coverage/leakage trong `reports/`. "
        "Attribution: " + ", ".join(release["source_attribution_refs"]) + ".\n\n"
        "Rectangle người/ngữ cảnh mới là crop đã nghiệm thu; chưa chốt crop runtime. "
        "Nhóm thị giác không chứng minh độc lập subject/session hoặc tổng quát ở phòng thi "
        "thực tế. Không suy ý định/vi phạm từ ảnh tĩnh.\n\n"
        "Không train, tính metric model hoặc upload dữ liệu khi đóng release này.\n"
    )
    (output / "dataset-card.md").write_text(card, encoding="utf8")
    release["implementation_sha256"][Path(__file__).relative_to(workspace).as_posix()] = (
        sha256_file(Path(__file__))
    )
    write_json(output / "release.json", release)
    checksums = {
        p.relative_to(output).as_posix(): sha256_file(p)
        for p in sorted(output.rglob("*"))
        if p.is_file() and p.name != "checksums.sha256"
    }
    (output / "checksums.sha256").write_text(
        "".join(f"{h}  {name}\n" for name, h in sorted(checksums.items())), encoding="utf8"
    )
    return checksums


def accept_review(config_path: Path, workspace: Path) -> dict[str, Any]:
    """Kiểm tất cả pin trước khi ghi release và dùng canonical exporter hiện có."""
    c = load_yaml(config_path)
    workspace = workspace.resolve()
    if c["status"] != "accepted" or c["formulation"] != "B":
        raise DataContractError("Config chưa accepted/B")
    for key in (
        "approval",
        "proposal_config",
        "assignment",
        "parent_checksums",
        "rights_attribution",
    ):
        verify_pin(workspace / c[key]["path"], c[key]["sha256"])
    approval = json.loads((workspace / c["approval"]["path"]).read_text(encoding="utf8"))
    for pin in approval["approved_artifacts"].values():
        verify_pin(workspace / pin["path"], pin["sha256"])
    if approval["approved_artifacts"]["assignment"] != c["assignment"]:
        raise DataContractError("Assignment khác gói owner đã duyệt")
    parent = workspace / c["parent_package"]
    review = workspace / c["review_package"]
    if workspace / c["parent_checksums"]["path"] != parent / "checksums.sha256":
        raise DataContractError("Parent checksum pointer không đúng package")
    verify_payload(parent)
    verify_payload(review)
    verify_pin(
        review / "checksums.sha256", approval["approved_artifacts"]["review_checksums"]["sha256"]
    )
    parents = read_records(parent / "review-ledger.jsonl")
    assignments = [
        json.loads(x)
        for x in (workspace / c["assignment"]["path"]).read_text(encoding="utf8").splitlines()
    ]
    records = materialize_records(parents, assignments, c, approval)
    roots = {k: workspace / v for k, v in c["source_roots"].items()}
    # Nguồn mới nằm ở nhiều snapshot; gom bản sao có checksum vào cache local riêng.
    for a in assignments:
        if a["origin"] != "new_candidate":
            continue
        p = a["source_provenance"]
        dest_root = roots[p["source_id"]]
        if not dest_root.resolve().is_relative_to(workspace / "outputs"):
            raise DataContractError("Cache nguồn mới phải nằm trong outputs local")
        for path_key, sha_key in [
            ("source_image_relpath", "source_image_sha256"),
            ("source_label_relpath", "source_label_sha256"),
        ]:
            source = workspace / p["source_root"] / p[path_key]
            target = dest_root / p[path_key]
            verify_pin(source, p[sha_key])
            if target.exists():
                verify_pin(target, p[sha_key])
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
    crop_inputs = {
        a["sample_id"]: workspace / a["crop_path"] for a in assignments if a["crop_path"]
    }
    selection = []
    for r in records:
        p = r.source
        selection.append(
            dict(
                sample_id=r.sample_id,
                source_id=p.source_id,
                archive_sha256=p.archive_sha256,
                source_image_relpath=p.image_relpath,
                source_image_sha256=p.image_sha256,
                source_label_relpath=p.label_relpath,
                source_label_sha256=p.label_sha256,
                source_label_line_1based=p.label_line_1based,
                source_class_id=p.source_class_id,
            )
        )
    freeze = test_freeze_attestation(
        records,
        config_sha256=sha256_file(config_path),
        approval_sha256=c["approval"]["sha256"],
        owner_decision_ref=c["approval"]["path"],
        approval=approval,
        commit=c["git_commit"],
        protocol=c["test_protocol"],
    )
    freeze["preserved_parent"] = c["parent_package"]
    freeze["new_test_inference_authorized"] = False
    metadata = dict(
        status="accepted",
        dataset_version=c["dataset_version"],
        git_commit=c["git_commit"],
        git_dirty=True,
        config_sha256=sha256_file(config_path),
        owner_decision_ref=c["approval"]["path"],
        owner_approval=c["approval"],
        schema_config_review_ref=c["approval"]["path"],
        split_config_review_ref=c["approval"]["path"],
        leakage_review_ref=c["approval"]["path"],
        test_freeze_ref="release.json#test_freeze",
        test_freeze=freeze,
        approved_use_scope=c["approved_use_scope"],
        use_scope=c["approved_use_scope"][0],
        parent_checksums=c["parent_checksums"],
        approved_assignment=c["assignment"],
        expected_source_counts=dict(Counter(r.source.source_id for r in records)),
        expected_selection_count=len(selection),
        source_attribution_refs=sorted(
            {r.rights.attribution_ref for r in records if r.rights.attribution_ref}
        ),
        crop_policy_review_notes=c["crop_policy_review_notes"],
        limitations=c["limitations"],
        implementation_sha256={
            Path(__file__).relative_to(workspace).as_posix(): sha256_file(Path(__file__))
        },
    )
    output = (workspace / c["package"]).resolve()
    if not output.is_relative_to(workspace / "data/processed") or output.exists():
        raise DataContractError("Release output phải là version mới trong data/processed")
    result = build_pilot_package(
        records, output, roots, crop_inputs, selection, metadata, [r.sample_id for r in records]
    )
    result["payload_checksums"] = finalize_new_package(output, workspace)
    result["checksums_sha256"] = sha256_file(output / "checksums.sha256")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    result = accept_review(args.config, Path.cwd())
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "payload_checksums"}, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
