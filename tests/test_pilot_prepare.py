import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_inputs import validate_rf_inputs
from ai_exam_monitoring.data.pilot_prepare import create_ledger, prepare_package


class PilotPrepareTests(unittest.TestCase):
    def fixture(self, root):
        source = root / "source"
        image = source / "train/images/image.png"
        label = source / "train/labels/image.txt"
        image.parent.mkdir(parents=True)
        label.parent.mkdir(parents=True)
        Image.new("RGB", (16, 12), (30, 100, 200)).save(image)
        label.write_text("0 0.5 0.5 0.6 0.7\n")
        crop = root / "crop.png"
        with Image.open(image) as canvas:
            canvas.crop((1, 1, 15, 11)).save(crop)
        archive = root / "archive.zip"
        with zipfile.ZipFile(archive, "w") as handle:
            handle.write(image, "train/images/image.png")
            handle.write(label, "train/labels/image.txt")
        rows = [{
            "id": f"P{index:03d}-person-01", "training_eligible": False,
            "person_status": "owner_approved", "crop_status": "owner_approved",
            "owner_answers": {"fixture": "approved"}, "source_image": "train/images/image.png",
            "image_sha256": sha256_file(image), "crop_path": "crop.png",
            "crop_sha256": sha256_file(crop), "person_xyxy": [2, 2, 10, 10],
            "context_crop_xyxy": [1, 1, 15, 11],
            "phone_use": "owner_approved_positive" if index < 24 else "unknown",
            "looking_around": "owner_approved_positive" if index == 0 or index >= 24
            else "unknown",
        } for index in range(28)]
        review = root / "review.json"
        review.write_text(json.dumps({"current_person_crops": rows}))
        audit = root / "audit.json"
        audit.write_text("{}")
        config = {
            "dataset_version": "pilot-fixture-v1", "selection_version": "selection-v1",
            "crop_policy_version": "crop-v1", "sources": [],
            "roboflow": {
                "id": "rf", "root": "source", "archive": str(archive),
                "archive_sha256": sha256_file(archive), "review_bundle": "review.json",
                "review_bundle_sha256": sha256_file(review), "audit_bundle": "audit.json",
                "audit_bundle_sha256": sha256_file(audit),
                "expected_ids": [row["id"] for row in rows],
            },
        }
        return rows, config, label

    def test_preserve_rf_approvals_masks_and_review_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows, config, _ = self.fixture(root)
            validated, pins = validate_rf_inputs(config["roboflow"], root)
            ledger, _, _ = create_ledger([], validated, config, root)
            self.assertEqual(pins["crop_count"], 28)
            self.assertEqual(ledger[0].target_values, (1, 1))
            self.assertEqual(ledger[1].target_mask, (1, 0))
            self.assertEqual(ledger[24].target_values, (None, 1))
            self.assertTrue(all(row.split is None and row.usage == "review_only" for row in ledger))
            self.assertEqual(ledger[0].crop.crop_sha256, rows[0]["crop_sha256"])

    def test_extracted_label_tamper_rejected_by_both_entry_points(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows, config, label = self.fixture(root)
            label.write_text("2 0.5 0.5 0.1 0.1\n")
            with self.assertRaises(DataContractError):
                validate_rf_inputs(config["roboflow"], root)
            with self.assertRaises(DataContractError):
                create_ledger([], rows, config, root)

    def test_invalid_target_state_rejected_in_importer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows, config, _ = self.fixture(root)
            rows[0]["phone_use"] = "negative"
            with self.assertRaisesRegex(DataContractError, "Unsupported RF state"):
                create_ledger([], rows, config, root)

    def test_config_and_selection_pin_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.yaml"
            config_path.write_text(
                "formulation: B\nstatus: preparation_only\n"
                "target_encoding_version: pilot-b-targets-v1\n"
            )
            inputs = root / "inputs"
            inputs.mkdir()
            selection = inputs / "selection.jsonl"
            selection.write_text("{}\n")
            pins = {"config_sha256": "a" * 64, "selection_sha256": "b" * 64}
            (inputs / "input-pins.json").write_text(json.dumps(pins))
            with self.assertRaises(DataContractError):
                prepare_package(config_path, inputs_dir=inputs, output_dir=root / "output")
            pins["config_sha256"] = sha256_file(config_path)
            (inputs / "input-pins.json").write_text(json.dumps(pins))
            with self.assertRaises(DataContractError):
                prepare_package(config_path, inputs_dir=inputs, output_dir=root / "output")
            self.assertFalse((root / "output").exists())

    def test_preparation_rejects_ignored_encoding_or_wrong_formulation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.yaml"
            inputs = root / "inputs"
            inputs.mkdir()
            for config in (
                "formulation: B\nstatus: preparation_only\ntarget_encoding_version: future-v2\n",
                "formulation: A\nstatus: preparation_only\n"
                "target_encoding_version: pilot-b-targets-v1\n",
                "formulation: B\nstatus: accepted\ntarget_encoding_version: pilot-b-targets-v1\n",
            ):
                config_path.write_text(config)
                (inputs / "input-pins.json").write_text(json.dumps({
                    "config_sha256": sha256_file(config_path),
                }))
                with self.assertRaisesRegex(DataContractError, "target encoding"):
                    prepare_package(config_path, inputs_dir=inputs, output_dir=root / "output")
            self.assertFalse((root / "output").exists())


if __name__ == "__main__":
    unittest.main()
