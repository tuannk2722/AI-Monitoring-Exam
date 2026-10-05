import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import test_pilot_package as fixtures
import yaml
from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json
from ai_exam_monitoring.data.pilot_owner_groups import verify_payload
from ai_exam_monitoring.data.pilot_package import build_pilot_package
from ai_exam_monitoring.data.pilot_scb_proposals import (
    accept_batch,
    anchor_bounds,
    apply_batch_approval,
    build_proposals,
)
from ai_exam_monitoring.data.pilot_schema import TargetReview, read_records


class ScbProposalTests(unittest.TestCase):
    def unique_record(self, root, sample_id, index):
        record, source, crop = fixtures.PilotPackageTests().make_record(root, sample_id, index)
        image_path = source / record.source.image_relpath
        with Image.open(image_path) as original:
            image = original.convert("RGB")
        # Distinct fixture source bytes outside the historical crop rectangle.
        image.putpixel((11, 9), tuple(hashlib.sha256(sample_id.encode()).digest()[:3]))
        image.save(image_path)
        record = replace(
            record, source=replace(record.source, image_sha256=sha256_file(image_path))
        )
        return record, source, crop

    def fixture(self, root):
        workspace = Path(__file__).resolve().parents[1]
        records, crops, selection = [], {}, []
        for index in range(28):
            record, source, crop = self.unique_record(root, f"RF{index:03d}", index)
            records.append(record)
            crops[record.sample_id] = crop
        sources, rules = [], {}
        for stratum, class_id, source_id, name in (
            ("turnhead", 1, "head", "TurnHead"), ("read", 1, "hrw", "read"),
            ("write", 2, "hrw", "write"),
        ):
            rules[stratum] = {"source_class": name,
                              "looking_around": "positive" if stratum == "turnhead" else "negative",
                              "work_context": "unknown"}
            for index in range(28):
                record, source, _ = self.unique_record(root, f"SCB-{stratum}-{index:03d}", index)
                label = source / "labels" / f"{record.sample_id}.txt"
                label.parent.mkdir(exist_ok=True)
                label.write_text(f"{class_id} 0.5 0.5 0.5 0.6\n", encoding="utf-8")
                record = replace(record, crop=None, disposition="pending", owner_decision_ref=None,
                                 phone_use=TargetReview("unknown", "pending"),
                                 looking_around=TargetReview("unknown", "pending"),
                                 source=replace(record.source, source_id=source_id,
                                                label_relpath=label.relative_to(source).as_posix(),
                                                label_sha256=sha256_file(label),
                                                label_line_1based=1, source_class_id=class_id))
                records.append(record)
                selection.append({
                    "sample_id": record.sample_id, "stratum": stratum,
                    "source_id": source_id, "source_image_sha256": record.source.image_sha256,
                    "archive_sha256": record.source.archive_sha256,
                    "source_image_relpath": record.source.image_relpath,
                    "source_label_relpath": record.source.label_relpath,
                    "source_label_sha256": record.source.label_sha256,
                    "source_label_line_1based": 1, "source_class_id": class_id,
                    "source_anchor_xyxy": [3.0, 2.0, 9.0, 8.0],
                })
        source_path = source.relative_to(workspace).as_posix()
        sources = [{"id": "head", "root": source_path, "source_names": {1: "TurnHead"}},
                   {"id": "hrw", "root": source_path, "source_names": {1: "read", 2: "write"}}]
        parent_config = root / "parent.yaml"
        parent_config.write_text(yaml.safe_dump({
            "sources": sources, "roboflow": {"id": "rf", "root": source_path}
        }), encoding="utf-8")
        package = root / "parent"
        build_pilot_package(records, package, {key: source for key in ("head", "hrw", "rf")},
                            crops, selection, {"status": "prepared_pending_gates",
                                               "dataset_version": "pilot-fixture-v1",
                                               "git_commit": "fixture-commit",
                                               "config_sha256": sha256_file(parent_config)},
                            [row.sample_id for row in records])
        config = root / "proposal.json"
        write_json(config, {"status": "draft_proposals", "proposal_version": "fixture-v1",
                            "parent_package": package.relative_to(workspace).as_posix(),
                            "parent_config": parent_config.relative_to(workspace).as_posix(),
                            "parent_checksums_sha256": sha256_file(package / "checksums.sha256"),
                            "crop_rule": "source_anchor_outward_integer_bounds",
                            "source_class_rules": rules})
        return config, package

    def test_deterministic_combined_bundle_preserves_canonical_and_rf(self):
        workspace = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=workspace / "outputs") as temporary:
            root = Path(temporary)
            config, parent = self.fixture(root)
            first, second = root / "first", root / "second"
            report = build_proposals(config, first)
            build_proposals(config, second)
            verify_payload(first)
            self.assertEqual((first / "checksums.sha256").read_bytes(),
                             (second / "checksums.sha256").read_bytes())
            self.assertEqual((first / "review-ledger.jsonl").read_bytes(),
                             (parent / "review-ledger.jsonl").read_bytes())
            for crop in (parent / "crops").glob("*.png"):
                self.assertEqual(crop.read_bytes(), (first / "crops" / crop.name).read_bytes())
            self.assertEqual(report["proposed_looking_around"], {"positive": 28, "negative": 56})
            self.assertFalse(report["training_release_accepted"])
            self.assertEqual(len(list((first / "draft-crops").glob("*.png"))), 84)
            self.assertFalse(list(first.rglob("*.html")))
            with self.assertRaises(DataContractError):
                build_proposals(config, first)
            (parent / "selection.jsonl").write_text("tampered", encoding="utf-8")
            with self.assertRaises(DataContractError):
                build_proposals(config, root / "bad")

    def test_rounding_uses_original_source_line_and_rejects_geometry_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            label = Path(temporary) / "label.txt"
            label.write_text("1 0.5 0.5 0.5 0.6\n", encoding="utf-8")
            row = {"source_label_line_1based": 1, "source_class_id": 1,
                   "source_anchor_xyxy": [2.75, 2.2, 8.25, 8.8]}
            self.assertEqual(anchor_bounds(row, label, (11, 11)).xyxy, (2, 2, 9, 9))
            row["source_anchor_xyxy"][0] = -1
            with self.assertRaises(DataContractError):
                anchor_bounds(row, label, (11, 11))

    def test_owner_approval_preserves_unknown_rf_and_release_gates(self):
        workspace = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=workspace / "outputs") as temporary:
            root = Path(temporary)
            proposal_config, parent = self.fixture(root)
            batch = root / "batch"
            build_proposals(proposal_config, batch)
            approval = {"decision": "approve_scb_crop_target_batch", "reviewer": "owner",
                        "reviewed_at": "2026-10-05", "exceptions": [],
                        "approved_batch_checksums_sha256": sha256_file(batch / "checksums.sha256")}
            decision = root / "decision.json"
            write_json(decision, approval)
            config = root / "accepted.json"
            write_json(config, {
                "status": "preparation_only", "dataset_version": "fixture-approved-v2",
                "parent_package": parent.relative_to(workspace).as_posix(),
                "parent_config": (root / "parent.yaml").relative_to(workspace).as_posix(),
                "parent_checksums_sha256": sha256_file(parent / "checksums.sha256"),
                "approved_batch": batch.relative_to(workspace).as_posix(),
                "approved_batch_checksums_sha256": approval["approved_batch_checksums_sha256"],
                "approval": decision.relative_to(workspace).as_posix(),
                "approval_sha256": sha256_file(decision),
            })
            output = root / "approved"
            result = accept_batch(config, output)
            self.assertEqual(result["reviewed_crops"], 112)
            old = {row.sample_id: row for row in read_records(parent / "review-ledger.jsonl")}
            for row in read_records(output / "review-ledger.jsonl"):
                self.assertIsNone(row.split)
                self.assertEqual(row.usage, "review_only")
                self.assertEqual(row.phone_use, old[row.sample_id].phone_use)
                self.assertEqual(row.group, old[row.sample_id].group)
                self.assertEqual(row.work_context_review, old[row.sample_id].work_context_review)
                if old[row.sample_id].crop:
                    self.assertEqual(row.crop, old[row.sample_id].crop)
                else:
                    self.assertEqual(row.target_mask, (0, 1))
                    self.assertEqual(
                        row.crop.review.crop_sha256, row.looking_around.review.crop_sha256
                    )
                    self.assertNotEqual(row.normal_review, "confirmed_normal")
            proposals = [json.loads(line) for line in (batch / "proposals.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()]
            with self.assertRaises(DataContractError):
                apply_batch_approval(list(old.values()), proposals,
                                     {**approval, "exceptions": ["x"]},
                                     dataset_version="new", evidence_ref="fixture")
            proposals[0]["proposed_phone_use"] = "negative"
            with self.assertRaises(DataContractError):
                apply_batch_approval(list(old.values()), proposals, approval,
                                     dataset_version="new", evidence_ref="fixture")
            decision.write_text("tampered", encoding="utf-8")
            with self.assertRaises(DataContractError):
                accept_batch(config, root / "tampered")


if __name__ == "__main__":
    unittest.main()
