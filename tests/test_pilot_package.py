import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from PIL import Image, PngImagePlugin

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_package import build_pilot_package, coverage_report
from ai_exam_monitoring.data.pilot_schema import (
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
)


class PilotPackageTests(unittest.TestCase):
    def make_record(self, root, sample_id, index, states=("positive", "unknown")):
        source_root = root / "source"
        image_path = source_root / "train" / "images" / f"{sample_id}.png"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (12, 10))
        image.putdata([(x * 15, y * 17, index * 30) for y in range(10) for x in range(12)])
        image.save(image_path)
        context = PixelBox(1, 0, 10, 9)
        crop_input = root / "input-crops" / f"{sample_id}.png"
        crop_input.parent.mkdir(parents=True, exist_ok=True)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("historical_snapshot", "Preserve approved crop bytes exactly")
        image.crop(context.xyxy).save(crop_input, pnginfo=pnginfo)
        crop_sha = sha256_file(crop_input)
        approval = ReviewEvidence("owner", "2026-10-04", "fixture-owner-review", crop_sha)
        targets = [
            TargetReview(state, "fixture visual review", approval)
            if state != "unknown"
            else TargetReview(state, "target not reviewed")
            for state in states
        ]
        record = PilotRecord(
            sample_id,
            "pilot-fixture-v1",
            "selection-fixture-v1",
            "reviewed-context-v1",
            SourceRef(
                "rf",
                "a" * 64,
                image_path.relative_to(source_root).as_posix(),
                sha256_file(image_path),
                12,
                10,
            ),
            targets[0],
            targets[1],
            ContextReview("unknown", "context not reviewed"),
            RightsReview("fixture-license", "fixture-attribution"),
            crop=CropRef(
                "person-01",
                PixelBox(2, 1, 7, 8),
                context,
                f"crops/{sample_id}.png",
                crop_sha,
                approval,
            ),
            disposition="approved",
            ineligibility_reasons=("group pending", "rights pending"),
            owner_decision_ref="historical-crop-owner-review",
        )
        return record, source_root, crop_input

    def fixture(self, root):
        reviewed, source_root, crop_input = self.make_record(root, "RF001-person-01", 1)
        pending_base, _, _ = self.make_record(root, "SCB001", 2)
        label = source_root / "train" / "labels" / "SCB001.txt"
        label.parent.mkdir(parents=True, exist_ok=True)
        label.write_text("1 0.5 0.5 0.5 0.6\n", encoding="utf-8")
        pending = replace(
            pending_base,
            source=replace(
                pending_base.source,
                source_id="scb",
                archive_sha256="b" * 64,
                label_relpath="train/labels/SCB001.txt",
                label_sha256=sha256_file(label),
                label_line_1based=1,
                source_class_id=1,
            ),
            crop=None,
            phone_use=TargetReview("unknown", "source label is not canonical"),
            looking_around=TargetReview("unknown", "source label is not canonical"),
            disposition="pending",
            owner_decision_ref=None,
            ineligibility_reasons=("person/crop/targets pending", "group pending"),
        )
        selection = [
            {
                "sample_id": pending.sample_id,
                "source_id": "scb",
                "archive_sha256": "b" * 64,
                "source_image_relpath": pending.source.image_relpath,
                "source_image_sha256": pending.source.image_sha256,
                "source_label_relpath": pending.source.label_relpath,
                "source_label_sha256": pending.source.label_sha256,
                "source_label_line_1based": 1,
                "source_class_id": 1,
                "source_anchor_xyxy": [3.0, 2.0, 9.0, 8.0],
                "stratum": "turnhead",
            }
        ]
        metadata = {
            "status": "prepared_pending_gates",
            "dataset_version": "pilot-fixture-v1",
            "git_commit": "fixture-git-commit",
            "expected_source_counts": {"rf": 1, "scb": 1},
            "expected_selection_count": 1,
            "limitations": ["Groups not supplied"],
        }
        return {
            "records": [reviewed, pending],
            "source_roots": {"rf": source_root, "scb": source_root},
            "crop_inputs": {reviewed.sample_id: crop_input},
            "selection_rows": selection,
            "metadata": metadata,
            "expected_sample_ids": [reviewed.sample_id, pending.sample_id],
        }

    def test_staging_preserves_unknown_exact_crops_and_review_ledger(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = self.fixture(root)
            result = build_pilot_package(output_dir=root / "package", **inputs)
            self.assertEqual((result["records"], result["reviewed_crops"]), (2, 1))
            ledger = read_records(root / "package" / "review-ledger.jsonl")
            self.assertEqual(ledger[0].target_values, (1, None))
            self.assertEqual(ledger[0].target_mask, (1, 0))
            self.assertEqual(ledger[1].target_values, (None, None))
            self.assertTrue(all(row.split is None and row.usage == "review_only" for row in ledger))
            for filename in ("manifest.jsonl", "split-assignment.jsonl"):
                self.assertFalse((root / "package" / filename).exists())
            crop = ledger[0].crop
            self.assertIsNotNone(crop)
            self.assertEqual(
                (root / "package" / crop.crop_relpath).read_bytes(),
                inputs["crop_inputs"][ledger[0].sample_id].read_bytes(),
            )
            self.assertFalse((root / "package" / "crops" / "SCB001.png").exists())
            report = json.loads((root / "package" / "reports" / "coverage.json").read_text())
            self.assertEqual(
                report["all"]["targets"]["phone_use"], {"positive": 1, "negative": 0, "unknown": 1}
            )

    def test_rebuild_is_byte_identical_with_reversed_inputs_and_different_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = self.fixture(root)
            first = build_pilot_package(output_dir=root / "first", **inputs)
            inputs["records"].reverse()
            inputs["expected_sample_ids"].reverse()
            second = build_pilot_package(output_dir=root / "second", **inputs)
            self.assertEqual(first["payload_checksums"], second["payload_checksums"])
            self.assertEqual(first["checksums_sha256"], second["checksums_sha256"])
            for relative in first["payload_checksums"]:
                self.assertEqual(
                    (root / "first" / relative).read_bytes(),
                    (root / "second" / relative).read_bytes(),
                )

    def test_mutated_source_crop_or_label_rejected_before_writing(self):
        for mutation in ("image", "crop", "label"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                inputs = self.fixture(root)
                record = inputs["records"][0 if mutation != "label" else 1]
                if mutation == "crop":
                    file = inputs["crop_inputs"][record.sample_id]
                else:
                    relative = (
                        record.source.image_relpath
                        if mutation == "image"
                        else (record.source.label_relpath)
                    )
                    file = inputs["source_roots"][record.source.source_id] / relative
                file.write_bytes(file.read_bytes() + b"changed")
                with self.assertRaises(DataContractError):
                    build_pilot_package(output_dir=root / "package", **inputs)
                self.assertFalse((root / "package").exists())

    def test_wrong_crop_rectangle_is_rejected_even_with_valid_bytes_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = self.fixture(root)
            row = inputs["records"][0]
            inputs["records"][0] = replace(
                row, crop=replace(row.crop, context_box=PixelBox(2, 0, 11, 9))
            )
            with self.assertRaisesRegex(DataContractError, "pixels"):
                build_pilot_package(output_dir=root / "package", **inputs)
            self.assertFalse((root / "package").exists())

    def test_exact_membership_selection_and_new_version_checks(self):
        for mutation in (
            "missing",
            "extra",
            "selection",
            "source_counts",
            "selection_count",
            "reuse",
            "source_output",
            "crop_path",
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                inputs = self.fixture(root)
                output = root / "package"
                if mutation == "missing":
                    inputs["records"].pop()
                elif mutation == "extra":
                    inputs["expected_sample_ids"].append("not-selected")
                elif mutation == "selection":
                    inputs["selection_rows"][0]["source_image_sha256"] = "c" * 64
                elif mutation == "source_counts":
                    inputs["metadata"]["expected_source_counts"]["scb"] = 2
                elif mutation == "selection_count":
                    inputs["metadata"]["expected_selection_count"] = 84
                elif mutation == "reuse":
                    output.mkdir()
                    (output / "existing-release.txt").write_text("preserve", encoding="utf-8")
                elif mutation == "source_output":
                    output = inputs["source_roots"]["rf"] / "new-output"
                else:
                    row = inputs["records"][0]
                    inputs["records"][0] = replace(
                        row, crop=replace(row.crop, crop_relpath="release.json")
                    )
                with self.assertRaises(DataContractError):
                    build_pilot_package(output_dir=output, **inputs)
                if mutation == "reuse":
                    self.assertEqual((output / "existing-release.txt").read_text(), "preserve")

    def accepted_fixture(self, root):
        rows, crops = [], {}
        for index, states in enumerate((("positive", "positive"), ("negative", "negative")), 1):
            row, source_root, crop_input = self.make_record(root, f"R{index:03}", index, states)
            evidence = ReviewEvidence("owner", "2026-10-04", "fixture-release-decision")
            row = replace(
                row,
                rights=RightsReview(
                    "fixture-license",
                    "fixture-attribution",
                    ("fixture_local_classifier",),
                    evidence,
                ),
                group=GroupReview(f"group-{index}", ("reviewed-independent-cluster",), evidence),
                release_review=evidence,
                split="train",
                usage="train",
                split_version="split-fixture-v1",
                ineligibility_reasons=(),
                use_scope="fixture_local_classifier",
            )
            if states == ("negative", "negative"):
                row = replace(
                    row,
                    work_context_review=ContextReview(
                        "confirmed_working", "reviewed visible work context", row.crop.review
                    ),
                )
            rows.append(row)
            crops[row.sample_id] = crop_input
        return {
            "records": rows,
            "source_roots": {"rf": source_root},
            "crop_inputs": crops,
            "selection_rows": [],
            "expected_sample_ids": [row.sample_id for row in rows],
            "metadata": {
                "status": "accepted",
                "dataset_version": "pilot-fixture-v1",
                "git_commit": "fixture-git-commit",
                "owner_decision_ref": "owner-release",
                "schema_config_review_ref": "owner-schema-config-review",
                "split_config_review_ref": "owner-split-config-review",
                "test_freeze_ref": "owner-test-freeze",
                "leakage_review_ref": "owner-leakage-review",
                "approved_use_scope": ["fixture_local_classifier"],
                "use_scope": "fixture_local_classifier",
                "config_sha256": "c" * 64,
            },
        }

    def test_accepted_export_requires_global_gate_evidence_and_known_training_pn(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = self.accepted_fixture(root)
            build_pilot_package(output_dir=root / "accepted", **inputs)
            ledger = read_records(root / "accepted" / "manifest.jsonl")
            self.assertEqual(ledger[0].target_values, (1, 1))
            self.assertEqual(ledger[1].normal_review, "confirmed_normal")
            self.assertTrue((root / "accepted" / "split-assignment.jsonl").is_file())
            self.assertEqual(
                coverage_report(ledger)["split_support"]["val"]["support"]["phone_use"][
                    "binary_metric_support"
                ],
                "unavailable_missing_positive_or_negative",
            )
            inputs["metadata"].pop("schema_config_review_ref")
            with self.assertRaisesRegex(DataContractError, "schema_config_review_ref"):
                build_pilot_package(output_dir=root / "unsigned", **inputs)
            inputs["metadata"]["schema_config_review_ref"] = "owner-config-review"
            negative = inputs["records"][1]
            inputs["records"][1] = replace(
                negative,
                looking_around=TargetReview("unknown", "unreviewed target"),
                work_context_review=ContextReview("unknown", "unreviewed context"),
            )
            with self.assertRaisesRegex(DataContractError, "P/N"):
                build_pilot_package(output_dir=root / "no-negative-support", **inputs)

    def test_pending_export_cannot_retain_train_assignments(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = self.accepted_fixture(root)
            inputs["metadata"]["status"] = "prepared_pending_gates"
            with self.assertRaisesRegex(DataContractError, "Pending package"):
                build_pilot_package(output_dir=root / "pending", **inputs)

    def test_accepted_export_cannot_change_reviewed_use_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = self.accepted_fixture(root)
            inputs["metadata"]["approved_use_scope"] = ["unapproved_distribution"]
            with self.assertRaisesRegex(DataContractError, "use scope"):
                build_pilot_package(output_dir=root / "broader-scope", **inputs)
            inputs["metadata"].pop("approved_use_scope")
            with self.assertRaisesRegex(DataContractError, "approved_use_scope"):
                build_pilot_package(output_dir=root / "missing-scope", **inputs)
            inputs["metadata"]["approved_use_scope"] = ["fixture_local_classifier"]
            inputs["metadata"]["use_scope"] = "unapproved_action"
            with self.assertRaisesRegex(DataContractError, "use_scope"):
                build_pilot_package(output_dir=root / "wrong-action", **inputs)


if __name__ == "__main__":
    unittest.main()
