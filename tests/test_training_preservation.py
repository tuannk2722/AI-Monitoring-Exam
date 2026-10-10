"""Regression v4/v5 và các trường hợp thay đổi evidence phải bị từ chối."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ML_AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("torch", "torchvision"))
if ML_AVAILABLE:
    from test_pilot_schema import evidence, usable_record
    from test_training import config

    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.data.pilot_schema import PixelBox, TargetReview, record_to_dict
    from ai_exam_monitoring.training.data import verify_dataset


@unittest.skipUnless(ML_AVAILABLE, "Cần môi trường classifier CPU để kiểm loader")
class PreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.parent = self.workspace / "data/parent"
        self.current = self.workspace / "data/current"
        self.evidence_dir = self.workspace / "evidence"
        self.evidence_dir.mkdir()
        for name in ("parent-approval.json", "membership.json", "groups.json", "proposal.yaml"):
            (self.evidence_dir / name).write_text("{}", encoding="utf-8")
        self.old = [self.row("old-train", "train"), self.row("val", "val"),
                    self.row("test", "test")]
        self.parent_release = {"status": "accepted", "test_freeze": {"status": "frozen",
            "owner_decision_ref": "evidence/parent-approval.json",
            "owner_decision_sha256": sha256_file(self.evidence_dir / "parent-approval.json")}}
        self.write_package(self.parent, self.old, self.parent_release, inline=True)
        self.new = [replace(r, dataset_version="current", split_version="current-split")
                    for r in self.old] + [self.row("new-train", "train", current=True)]
        self.approval = {"decision": "approve_pilot_b_v5_release", "reviewer": "owner",
            "reviewed_at": "2026-10-07", "approved_counts": {"train": 2, "val": 1, "test": 1},
            "membership": self.pin(self.evidence_dir / "membership.json"),
            "groups": self.pin(self.evidence_dir / "groups.json"),
            "proposal_config": self.pin(self.evidence_dir / "proposal.yaml")}
        self.write_json(self.evidence_dir / "owner-approval.json", self.approval)
        self.preservation = {"status": "owner_approved_preservation",
            "test_already_evaluated_in_e001": True, "new_test_inference_authorized": False,
            "owner_approval": self.pin(self.evidence_dir / "owner-approval.json"),
            "parent": {"package": "data/parent",
                "checksums": self.pin(self.parent / "checksums.sha256"),
                "ledger": self.pin(self.parent / "review-ledger.jsonl")},
            "records": [{"sample_id": r.sample_id, "split": r.split,
                "source_image_sha256": r.source.image_sha256, "crop_sha256": r.crop.crop_sha256,
                "phone_use": r.phone_use.state, "looking_around": r.looking_around.state,
                "target_mask": list(r.target_mask), "leakage_group_id": r.group.leakage_group_id,
                "original_test_freeze_ref": r.test_freeze_ref}
                for r in self.old if r.split in {"val", "test"}]}
        self.release = {"status": "accepted", "test_freeze_ref": "evidence/preservation.json"}
        self.update_evidence()

    @staticmethod
    def write_json(path, payload):
        path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n",
                        encoding="utf-8")

    def pin(self, path):
        return {"path": path.relative_to(self.workspace).as_posix(), "sha256": sha256_file(path)}

    def row(self, sample_id, split, *, current=False):
        digest = hashlib.sha256(sample_id.encode()).hexdigest()
        row = usable_record(sample_id, split=split, image_sha=digest)
        crop_sha = hashlib.sha256((sample_id + "-crop").encode()).hexdigest()
        review = evidence(crop_sha)
        return replace(row, dataset_version="current" if current else "parent",
            split_version="current-split" if current else "parent-split",
            use_scope="local_classifier_research",
            rights=replace(row.rights, approved_use_scope=("local_classifier_research",)),
            group=replace(row.group, leakage_group_id="group-" + split),
            crop=replace(row.crop, crop_sha256=crop_sha, review=review),
            phone_use=TargetReview("positive", "Nhãn fixture đã review", review),
            test_freeze_ref="release.json#test_freeze" if split == "test" else None)

    def seal(self, folder):
        files = sorted(p for p in folder.rglob("*") if p.is_file() and p.name != "checksums.sha256")
        (folder / "checksums.sha256").write_text("".join(
            sha256_file(p) + "  " + p.relative_to(folder).as_posix() + "\n" for p in files),
            encoding="utf-8")

    def write_package(self, folder, rows, release, *, inline=False):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "crops").mkdir(exist_ok=True)
        text = "".join(json.dumps(record_to_dict(r), sort_keys=True, ensure_ascii=False) + "\n"
                       for r in rows)
        for filename in ("manifest.jsonl", "review-ledger.jsonl"):
            (folder / filename).write_text(text, encoding="utf-8")
        assignments = [{"sample_id": r.sample_id, "split": r.split,
            "split_version": r.split_version, "leakage_group_id": r.group.leakage_group_id,
            "test_freeze_ref": r.test_freeze_ref} for r in rows]
        (folder / "split-assignment.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in assignments), encoding="utf-8")
        for row in rows:
            (folder / row.crop.crop_relpath).write_bytes((row.sample_id + "-crop").encode())
        if inline:
            test = sorted((r for r in rows if r.split == "test"), key=lambda r: r.sample_id)
            encoded = "".join(json.dumps(record_to_dict(r), sort_keys=True, ensure_ascii=False,
                                        allow_nan=False) + "\n" for r in test).encode()
            release["test_freeze"].update(
                manifest_sha256=sha256_file(folder / "manifest.jsonl"),
                split_assignment_sha256=sha256_file(folder / "split-assignment.jsonl"),
                test_manifest_sha256=hashlib.sha256(encoded).hexdigest(),
                test_sample_ids=[r.sample_id for r in test])
        self.write_json(folder / "release.json", release)
        self.seal(folder)

    def update_evidence(self):
        path = self.evidence_dir / "preservation.json"
        self.write_json(path, self.preservation)
        self.release.update(test_freeze=self.pin(path),
                            owner_approval=self.preservation["owner_approval"])
        self.write_package(self.current, self.new, self.release)

    def current_config(self):
        return replace(config(), dataset="data/current", dataset_version="current",
            split_version="current-split",
            payload_sha256=sha256_file(self.current / "checksums.sha256"))

    def assert_rejected(self):
        with self.assertRaises(DataContractError):
            verify_dataset(self.current, self.current_config())

    def test_v4_inline_and_v5_preservation_are_verified(self):
        parent_config = replace(config(), dataset="data/parent", dataset_version="parent",
            split_version="parent-split",
            payload_sha256=sha256_file(self.parent / "checksums.sha256"))
        self.assertEqual(len(verify_dataset(self.parent, parent_config)), 3)
        self.assertEqual(len(verify_dataset(self.current, self.current_config())), 4)

    def test_changed_or_missing_pointer_bytes_fail(self):
        path = self.evidence_dir / "preservation.json"
        path.write_text("{}", encoding="utf-8")
        self.assert_rejected()
        path.unlink()
        self.assert_rejected()

    def test_pointer_paths_cannot_escape_workspace(self):
        before = copy.deepcopy(self.release)
        for bad in ("../outside.json", "/absolute.json", "C:/outside.json", "evidence\\file.json"):
            with self.subTest(path=bad):
                self.release = copy.deepcopy(before)
                self.release["test_freeze"]["path"] = bad
                self.release["test_freeze_ref"] = bad
                self.write_package(self.current, self.new, self.release)
                self.assert_rejected()

    def test_preservation_status_scope_and_id_support_are_required(self):
        before = copy.deepcopy(self.preservation)
        changes = [{"status": "draft"}, {"new_test_inference_authorized": True},
                   {"test_already_evaluated_in_e001": False}, {"records": []},
                   {"records": before["records"][:1] * 2}]
        for change in changes:
            with self.subTest(change=change):
                self.preservation = {**copy.deepcopy(before), **change}
                self.update_evidence()
                self.assert_rejected()

    def test_owner_approval_identity_decision_and_counts_are_required(self):
        before = copy.deepcopy(self.approval)
        for change in ({"decision": "draft"}, {"reviewer": ""}, {"approved_counts": {}}):
            with self.subTest(change=change):
                self.write_json(self.evidence_dir / "owner-approval.json", {**before, **change})
                self.preservation["owner_approval"] = self.pin(
                    self.evidence_dir / "owner-approval.json")
                self.update_evidence()
                self.assert_rejected()
        self.write_json(self.evidence_dir / "owner-approval.json", before)
        self.preservation["owner_approval"] = self.pin(self.evidence_dir / "owner-approval.json")
        self.update_evidence()
        self.release["owner_approval"] = self.pin(self.evidence_dir / "groups.json")
        self.write_package(self.current, self.new, self.release)
        self.assert_rejected()

    def test_val_target_geometry_or_group_drift_fails_even_with_resigned_payload(self):
        before = list(self.new)
        row = next(r for r in before if r.sample_id == "val")
        mutations = [replace(row, looking_around=TargetReview(
            "negative", "Đổi nhãn", row.crop.review)),
            replace(row, crop=replace(row.crop, person_box=PixelBox(21, 10, 60, 70))),
            replace(row, group=replace(row.group, leakage_group_id="changed-val-group"))]
        for changed in mutations:
            with self.subTest(row=changed):
                self.new = [changed if r.sample_id == "val" else r for r in before]
                self.write_package(self.current, self.new, self.release)
                self.assert_rejected()

    def test_preservation_record_hash_or_mask_drift_is_rejected(self):
        before = copy.deepcopy(self.preservation)
        for change in ({"crop_sha256": "f" * 64}, {"target_mask": [1, 1]},
                       {"original_test_freeze_ref": "changed"}):
            with self.subTest(change=change):
                self.preservation = copy.deepcopy(before)
                self.preservation["records"][0].update(change)
                self.update_evidence()
                self.assert_rejected()

    def test_manifest_ledger_or_split_mismatch_fails(self):
        path = self.current / "split-assignment.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        rows[0]["split"] = "val"
        path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        self.seal(self.current)
        self.assert_rejected()
        self.write_package(self.current, self.new, self.release)
        path = self.current / "manifest.jsonl"
        path.write_text("\n".join(path.read_text(encoding="utf-8").splitlines()[1:]) + "\n",
                        encoding="utf-8")
        self.seal(self.current)
        self.assert_rejected()

    def test_changed_parent_bytes_or_unfrozen_parent_fail(self):
        (self.parent / "crops/test.png").write_bytes(b"changed")
        self.assert_rejected()
        self.write_package(self.parent, self.old, self.parent_release, inline=True)
        self.parent_release["test_freeze"]["status"] = "draft"
        self.write_package(self.parent, self.old, self.parent_release, inline=True)
        self.preservation["parent"]["checksums"] = self.pin(self.parent / "checksums.sha256")
        self.update_evidence()
        self.assert_rejected()

    def test_malformed_or_unknown_freeze_format_is_contract_error(self):
        for malformed in ({}, [], {"path": "evidence/preservation.json"}):
            with self.subTest(freeze=malformed):
                self.release["test_freeze"] = malformed
                self.write_package(self.current, self.new, self.release)
                self.assert_rejected()
