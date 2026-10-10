"""Đóng release v7 local từ batch/assignment được owner nghiệm thu cụ thể."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .integrity import pin, read_rows, safe_path, test_freeze_attestation, verify_payload
from .pilot_package import build_pilot_package
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
    parents: list[PilotRecord], ledger: list[dict[str, Any]],
    sources: dict[str, SourceRef], provenance: dict[str, dict[str, Any]],
    config: dict[str, Any], approval: dict[str, Any],
) -> list[PilotRecord]:
    """Áp dụng đúng version được ký; không nâng records có blocker vào train."""
    if (approval.get("decision") != "approve_pilot_b_v7_local_release"
            or approval.get("training_run_approved") is not False
            or approval.get("media_upload_approved") is not False
            or approval.get("exceptions") != []):
        raise DataContractError("Cần owner nghiệm thu v7 local đúng phạm vi")
    before = {r.sample_id: r for r in parents}
    by_id = {r["sample_id"]: r for r in ledger}
    new_ids = set(by_id) - set(before)
    if (len(before) != len(parents) or len(by_id) != len(ledger)
            or not set(before).issubset(by_id) or new_ids != set(sources)
            or new_ids != set(provenance)):
        raise DataContractError("Inventory release không khớp parent/newsource")
    evidence_ref = config["approval"]["path"]
    review = ReviewEvidence(approval["reviewer"], approval["reviewed_at"], evidence_ref)
    scope = tuple(config["approved_use_scope"])
    if scope != (approval["use_scope"],):
        raise DataContractError("Scope release khác approval")
    records = []
    for sid, row in sorted(by_id.items()):
        usage = row["proposed_usage"]
        used = usage in {"train", "val", "test"}
        states = row["proposed_states"]
        if (row["canonical_split"] is not None or row["training_eligible"]
                or row["release_accepted"] or len(states) != 2
                or any(s not in {"positive", "negative", "unknown"} for s in states)):
            raise DataContractError("Ledger phải đúng proposal có hai target PNU")
        old = before.get(sid)
        crop_sha = row["crop_sha256"]
        crop_review = replace(review, crop_sha256=crop_sha)
        if old:
            if (old.crop is None or crop_sha != old.crop.crop_sha256
                    or row["source_sha256"] != old.source.image_sha256):
                raise DataContractError("Không đổi source/crop parent")
            delta = row.get("parent_delta")
            original_states = [old.phone_use.state, old.looking_around.state]
            if old.usage == "test" and (usage != "test" or states != original_states
                                       or (delta and delta.get("decisions"))):
                raise DataContractError("Không sửa test freeze")
            if (usage != old.usage or states != original_states) and (
                not delta or not delta.get("decisions")
                or usage != delta["proposed_usage"] or states != delta["proposed_states"]
                or delta["original_crop_sha256"] != crop_sha
                or delta["source_sha256"] != old.source.image_sha256
            ):
                raise DataContractError("Parent thay đổi thiếu correction đã duyệt/pin")
            reason = "Correction parent đã owner review; chỉ áp dụng trong version v7."
            targets = [getattr(old, name) if state == getattr(old, name).state else
                       TargetReview(state, reason, crop_review)
                       for name, state in zip(("phone_use", "looking_around"), states, strict=True)]
            source, crop = old.source, old.crop
            context, rights = old.work_context_review, old.rights
        else:
            if used and row["blockers"]:
                raise DataContractError("Không release train/eval candidate có blocker")
            p = provenance[sid]
            source = sources[sid]
            if (source.image_sha256 != row["source_sha256"]
                    or p["crop"]["sha256"] != crop_sha):
                raise DataContractError("Source/crop mới khác assignment đã duyệt")
            box = PixelBox(*p["xyxy"])
            crop = CropRef(sid, box, box, f"crops/{sid}.png", crop_sha, crop_review)
            targets = [TargetReview(state, p["reason"], crop_review) for state in states]
            context = ContextReview("unknown", "Chưa chốt work-context riêng; không suy normal.")
            credit = row["rights"]["attribution"]
            license_id = (credit.get("license_url") or credit.get("provider_license_url")
                          or credit.get("license_id"))
            rights = RightsReview(license_id, config["rights"]["path"] + "#" + sid,
                                  scope if used else (), review if used else None)
        used_scope = scope if used else rights.approved_use_scope
        if used and (rights.review is None or rights.approved_use_scope != scope):
            if not rights.license_id or not rights.attribution_ref:
                raise DataContractError("Nguồn sử dụng thiếu license/attribution")
            rights = replace(rights, approved_use_scope=used_scope, review=review)
        old_evidence = old.group.evidence_refs if old and old.group else ()
        group = GroupReview(row["proposed_group_id"], tuple(sorted(set(old_evidence) | {
            config["whole_family"]["path"], evidence_ref + "#whole_family"})), review)
        blockers = tuple(row["blockers"])
        if usage == "review_only" and not blockers:
            blockers = ("Bảo toàn quyết định review-only parent, ngoài manifest sử dụng.",)
        exclusion = None
        if usage == "excluded":
            exclusion = (old.exclusion_reason if old and old.usage == "excluded" else
                         "Owner duyệt exclude correction hoặc evaluation-family quarantine.")
        versions = dict(dataset_version=config["dataset_version"],
                        selection_version=config["selection_version"],
                        crop_policy_version=config["crop_policy_version"])
        record = PilotRecord(
            sample_id=sid, **versions, source=source, crop=crop,
            phone_use=targets[0], looking_around=targets[1], work_context_review=context,
            rights=rights, group=group,
            disposition="excluded" if usage == "excluded" else "approved",
            usage=usage, split=usage if used else None,
            split_version=config["split_version"] if used else None,
            ineligibility_reasons=blockers if usage == "review_only" else (),
            exclusion_reason=exclusion, owner_decision_ref=evidence_ref, release_review=review,
            test_freeze_ref=old.test_freeze_ref if old and usage == "test" else None,
            use_scope=scope[0] if used else (old.use_scope if old else None),
        )
        records.append(record)
    if dict(Counter(r.usage for r in records)) != approval["approved_counts"]:
        raise DataContractError("Actual counts khác final approval")
    validate_records(records)
    return records


def _copy_exact(source: Path, target: Path, expected: str) -> None:
    if sha256_file(source) != expected:
        raise DataContractError("Input SHA thay đổi trước copy")
    if target.exists():
        if sha256_file(target) != expected:
            raise DataContractError("Cache source khác SHA")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def prepare_sources(
    root: Path, cache: Path, provenance: list[dict[str, Any]],
) -> tuple[dict[str, SourceRef], dict[str, Path], list[dict[str, Any]]]:
    """Intake ZIP local deterministic; giữ original upstream provenance riêng."""
    if not cache.is_relative_to(root / "outputs") or cache.exists():
        raise DataContractError("Source cache phải version mới trong outputs")
    cache.mkdir(parents=True)
    datasets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in provenance:
        datasets[p["source_id"]].append(p)
    sources: dict[str, SourceRef] = {}
    roots: dict[str, Path] = {}
    receipts = []
    for source_id, rows in sorted(datasets.items()):
        source_root = cache / "sources" / source_id
        roots[source_id] = source_root
        members: dict[str, bytes] = {}
        operational: dict[str, tuple[str, str | None]] = {}
        for p in rows:
            original = pin(root, p["original_source"], media=True)
            if p["exif_orientation"] != 1:
                raise DataContractError("EXIF nonidentity cần source transform version riêng")
            image_rel = f"v7-new/images/{p['original_source']['sha256']}{original.suffix}"
            _copy_exact(original, source_root / image_rel, p["original_source"]["sha256"])
            members[image_rel] = original.read_bytes()
            label_rel = None
            if p["label"]:
                label = pin(root, p["label"], media=True)
                label_rel = f"v7-new/labels/{p['label']['sha256']}.txt"
                _copy_exact(label, source_root / label_rel, p["label"]["sha256"])
                members[label_rel] = label.read_bytes()
            operational[p["sample_id"]] = image_rel, label_rel
        members["provenance.jsonl"] = "".join(
            json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n"
            for p in sorted(rows, key=lambda p: p["sample_id"])
        ).encode("utf8")
        archive = cache / "intake" / f"{source_id}.zip"
        archive.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as stream:
            for name, payload in sorted(members.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.external_attr = 0o100644 << 16
                stream.writestr(info, payload)
        archive_sha = sha256_file(archive)
        for p in rows:
            image_rel, label_rel = operational[p["sample_id"]]
            raw = p["original_provider_record"]
            line = raw.get("source_label_line_1based") if label_rel else None
            sources[p["sample_id"]] = SourceRef(
                source_id, archive_sha, image_rel, p["original_source"]["sha256"],
                p["size"][0], p["size"][1],
                label_rel, p["label"]["sha256"] if label_rel else None, line,
                raw.get("source_class_id") if line else None, raw.get("source_original_split"),
            )
        receipts.append({"source_id": source_id, "intake_archive": {
            "path": archive.relative_to(root).as_posix(), "sha256": archive_sha},
            "unique_members": len(members), "record_count": len(rows),
            "scope": "ZIP intake local của source đã pin; không phải upstream archive mới tải."})
    return sources, roots, receipts


def accept(config_path: Path, root: Path) -> dict[str, Any]:
    config = load_yaml(config_path)
    if config["status"] != "accepted" or config["formulation"] != "B":
        raise DataContractError("Config chưa Accepted/B")
    if config["builder_sha256"] != sha256_file(Path(__file__)):
        raise DataContractError("Builder không khớp source pin")
    paths = {key: pin(root, config[key]) for key in (
        "approval", "ledger", "assignment", "whole_family", "rights", "source_provenance",
        "parent_checksums", "parent_config", "review_pointer",
    )}
    approval = json.loads(paths["approval"].read_text(encoding="utf8"))
    for spec in approval["approved_artifacts"].values():
        pin(root, spec)
    if approval["approved_artifacts"]["assignment"] != config["assignment"]:
        raise DataContractError("Assignment khác final owner receipt")
    parent = safe_path(root, config["parent_package"])
    verify_payload(parent)
    parents = read_records(parent / "review-ledger.jsonl")
    ledger = read_rows(paths["ledger"])
    provenance = read_rows(paths["source_provenance"])
    by_provenance = {r["sample_id"]: r for r in provenance}
    cache = safe_path(root, config["source_cache"])
    sources, roots, receipts = prepare_sources(root, cache, provenance)
    parent_config = load_yaml(paths["parent_config"])
    for row in parents:
        source = row.source
        source_root = roots.setdefault(source.source_id, cache / "sources" / source.source_id)
        old_root = safe_path(root, parent_config["source_roots"][source.source_id])
        _copy_exact(old_root / source.image_relpath, source_root / source.image_relpath,
                    source.image_sha256)
        if source.label_relpath:
            assert source.label_sha256
            _copy_exact(old_root / source.label_relpath, source_root / source.label_relpath,
                        source.label_sha256)
    records = materialize_records(parents, ledger, sources, by_provenance, config, approval)
    crop_inputs = {r.sample_id: parent / r.crop.crop_relpath for r in parents
                   if r.crop and r.disposition != "excluded"}
    crop_inputs.update({p["sample_id"]: pin(root, p["crop"], media=True) for p in provenance})
    selection = []
    for record in records:
        s = record.source
        selection.append(dict(sample_id=record.sample_id, source_id=s.source_id,
            archive_sha256=s.archive_sha256, source_image_relpath=s.image_relpath,
            source_image_sha256=s.image_sha256, source_label_relpath=s.label_relpath,
            source_label_sha256=s.label_sha256, source_label_line_1based=s.label_line_1based,
            source_class_id=s.source_class_id,
            original_provenance=by_provenance.get(record.sample_id),
            parent_correction=next(r.get("parent_delta") for r in ledger
                                   if r["sample_id"] == record.sample_id)))
    freeze = test_freeze_attestation(records, config_sha256=sha256_file(config_path),
        approval_sha256=config["approval"]["sha256"], owner_decision_ref=config["approval"]["path"],
        approval=approval, commit=config["git_commit"], protocol=config["test_protocol"])
    freeze.update(preserved_parent=config["parent_package"], new_test_inference_authorized=False)
    metadata = dict(status="accepted", dataset_version=config["dataset_version"],
        git_commit=config["git_commit"], git_dirty=True, config_sha256=sha256_file(config_path),
        owner_decision_ref=config["approval"]["path"], owner_approval=config["approval"],
        schema_config_review_ref=config["approval"]["path"],
        split_config_review_ref=config["approval"]["path"],
        leakage_review_ref=config["approval"]["path"], test_freeze_ref="release.json#test_freeze",
        test_freeze=freeze, approved_use_scope=config["approved_use_scope"],
        use_scope=config["approved_use_scope"][0], parent_checksums=config["parent_checksums"],
        approved_assignment=config["assignment"], expected_selection_count=len(selection),
        expected_source_counts=dict(Counter(r.source.source_id for r in records)),
        source_attribution_refs=sorted({r.rights.attribution_ref for r in records
                                       if r.rights.attribution_ref}),
        source_intakes=receipts, source_cache=config["source_cache"],
        source_roots={k: p.relative_to(root).as_posix() for k, p in roots.items()},
        limitations=config["limitations"], crop_policy_review_notes=config["crop_policy_notes"],
        new_independent_groups_proven=0, training_run_approved=False,
        implementation_sha256={Path(__file__).relative_to(root).as_posix():
                               sha256_file(Path(__file__))})
    output = safe_path(root, config["package"])
    if not output.is_relative_to(root / "data/processed") or output.exists():
        raise DataContractError("Release output phải version mới trong processed")
    result = build_pilot_package(records, output, roots, crop_inputs, selection, metadata,
                                [r.sample_id for r in records])
    (output / "dataset-card.md").write_text(
        f"# Pilot B — {config['dataset_version']}\n\n"
        "Trạng thái: accepted local_classifier_research. 900 quyết định; "
        "manifest749 =689train/49val/11test;122review-only/29excluded.\n\n"
        "Chỉ dùng manifest.jsonl cho loss/metric; không lấy toàn thư mục crops. "
        "Hai target phone_use/looking_around; U=null/mask0. Các crop mới đã owner nghiệm thu.\n\n"
        "Parent source/crop giữ nguyên byte; correction9record chỉ trong v7. "
        "Test11 giữ identity/source/crop/target/evidence và protocol integrity-only; "
        "không inference mới. Val49 khác cohort/target support E003 nên không so BCE trực tiếp.\n\n"
        "449 conservative components không chứng minh độc lập subject/session. "
        "Quyền/credit/change notice: selection.jsonl, review-ledger.jsonl và rights receipt. "
        "Intake ZIP là snapshot local deterministic, không thay upstream provenance.\n\n"
        "4crop rights blocker vàS080boundaryhold ngoài train; U/U ngoài supervision. "
        "Runtime crop/independent holdout/E004 recipe/metrics là gate riêng. "
        "Không training, upload hoặc remote DVC trong release này.\n", encoding="utf8")
    release = json.loads((output / "release.json").read_text(encoding="utf8"))
    release["owner_accepted_local_group_boundaries"] = True
    write_json(output / "release.json", release)
    files = sorted(p for p in output.rglob("*") if p.is_file() and p.name != "checksums.sha256")
    (output / "checksums.sha256").write_text("".join(
        f"{sha256_file(p)}  {p.relative_to(output).as_posix()}\n" for p in files), encoding="utf8")
    return {"status": "accepted", "package": config["package"],
            "ledger_records": len(records), "counts": dict(Counter(r.usage for r in records)),
            "reviewed_crops": result["reviewed_crops"] if "reviewed_crops" in result else
                              len(list((output / "crops").glob("*.png"))),
            "checksums_sha256": sha256_file(output / "checksums.sha256")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.workspace.resolve()
    print(json.dumps(accept(safe_path(root, str(args.config)), root), ensure_ascii=False))


if __name__ == "__main__":
    main()
