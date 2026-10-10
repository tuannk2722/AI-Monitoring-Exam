from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from test_pilot_schema import evidence, usable_record

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import write_records
from ai_exam_monitoring.training.error_audit import (
    VisualFinding,
    build_audit,
    prediction_errors,
    support,
    validate_findings,
)


def prediction(split="val"):
    return {"sample_id": "fixture", "split": split, "source_id": "fixture",
            "group_id": "fixture", "scores": [.5, .9], "targets": [1, None],
            "mask": [1, 0], "decisions": [True, True]}


class ErrorAuditTests(unittest.TestCase):
    def test_unknown_not_negative_and_threshold_tie_is_positive(self):
        row = prediction()
        self.assertEqual(prediction_errors([row], "val", .5), [])
        counts = support([row], .5)
        self.assertEqual(counts["phone_use"]["TP"], 1)
        self.assertEqual(counts["looking_around"]["unknown"], 1)
        self.assertEqual(counts["looking_around"]["FP"], 0)

    def test_invalid_predictions_and_test_are_rejected(self):
        changes = [{"scores": [float("nan"), .9]}, {"mask": [True, 0]},
                   {"targets": [1, 0]}, {"decisions": [False, True]},
                   {"split": "test"}, {"scores": [1.1, .9]}, {"targets": [True, None]}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(DataContractError):
                prediction_errors([{**prediction(), **change}], "val", .5)
        with self.assertRaises(DataContractError):
            prediction_errors([prediction("test")], "test", .5)
        with self.assertRaises(DataContractError):
            prediction_errors([prediction(), prediction()], "val", .5)

    def test_fn_and_fp_reconstructed_from_saved_scores(self):
        rows = [{**prediction(), "scores": [.2, .9], "targets": [1, 0],
                 "mask": [1, 1], "decisions": [False, True]}]
        errors = prediction_errors(rows, "val", .5)
        self.assertEqual([(e["target"], e["outcome"]) for e in errors],
                         [("phone_use", "FN"), ("looking_around", "FP")])

    def test_coverage_requires_each_target_cell_and_rejects_duplicate_review(self):
        errors = {"train": [], "val": [
            {"sample_id": "fixture", "target": "phone_use", "outcome": "FN"},
            {"sample_id": "fixture", "target": "looking_around", "outcome": "FP"}]}
        one = VisualFinding("val", "fixture", "phone_use", "FN", ["small_evidence"],
                            "Quan sát fixture", "Giả thuyết fixture", "vừa",
                            "cần owner rà lại", "Đề xuất fixture")
        two = replace(one, target="looking_around", outcome="FP")
        validate_findings([one, two], errors)
        for findings in ([one], [one, two, one], [one, replace(two, split="train")]):
            with self.assertRaises(DataContractError):
                validate_findings(findings, errors)

    def test_review_cannot_silently_approve_labels(self):
        with self.assertRaises(DataContractError):
            VisualFinding("val", "fixture", "phone_use", "FN", ["small_evidence"],
                          "Quan sát", "Giả thuyết", "cao", "accepted", "Bổ sung")

    def test_manifest_integration_never_opens_test_media_and_preserves_output(self):
        # Fixture phần mềm: test crop cố ý không tồn tại, không là metric production.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            package, run = root / "data/fixture", root / "outputs/fixture"
            package.mkdir(parents=True)
            run.mkdir(parents=True)
            records, errors, findings = [], {"train": [], "val": []}, []
            for split, color in (("train", "red"), ("val", "blue")):
                row = usable_record(split, split=split)
                source = root / "sources" / f"{split}.png"
                source.parent.mkdir(exist_ok=True)
                image = Image.new("RGB", (100, 80), color)
                image.save(source)
                crop = package / row.crop.crop_relpath
                crop.parent.mkdir(exist_ok=True)
                image.crop((10, 0, 80, 80)).save(crop)
                digest = sha256_file(crop)
                row = replace(row, source=replace(row.source, image_relpath=f"{split}.png",
                              image_sha256=sha256_file(source)),
                              crop=replace(row.crop, crop_sha256=digest, review=evidence(digest)),
                              phone_use=replace(row.phone_use, review=evidence(digest)),
                              group=replace(row.group, leakage_group_id=split))
                records.append(row)
                pred = {**prediction(split), "sample_id": split, "source_id": "scb_head",
                        "group_id": split, "scores": [.2, .9], "decisions": [False, True]}
                (run / f"predictions-{split}.json").write_text(json.dumps([pred]))
                errors[split] = prediction_errors([pred], split, .5)
                finding = VisualFinding(split, split, "phone_use", "FN", ["small_evidence"],
                                        "Quan sát fixture", "Giả thuyết fixture", "vừa",
                                        "không thấy mâu thuẫn", "Đề xuất fixture")
                findings.append(asdict(finding))
            test = usable_record("unopened-test", split="test", image_sha="9" * 64)
            records.append(replace(test, group=replace(test.group, leakage_group_id="test")))
            write_records(package / "manifest.jsonl", records)
            write_records(package / "review-ledger.jsonl", records)
            (package / "release.json").write_text("{}")
            (package / "checksums.sha256").write_text("fixture\n")
            config = {"dataset": "data/fixture", "image_size": 224, "threshold": .5,
                      "experiment_id": "fixture", "payload_sha256": sha256_file(
                          package / "checksums.sha256")}
            (run / "resolved-config.json").write_text(json.dumps(config))
            (run / "run.json").write_text(json.dumps({"status": "FINISHED"}))
            (run / "checksums.json").write_text(json.dumps({
                p.name: sha256_file(p) for p in run.iterdir()}))
            error_file, finding_file = root / "errors.json", root / "findings.json"
            error_file.write_text(json.dumps(errors))
            finding_file.write_text(json.dumps({"status": "draft_pending_owner_review",
                                                "findings": findings}, ensure_ascii=False),
                                    encoding="utf8")
            source_config = root / "sources.yaml"
            source_config.write_text("source_roots:\n  scb_head: sources\n")
            output = root / "artifacts/reports/audit"
            opened = []
            original_open = Image.open

            def observed_open(path, *args, **kwargs):
                opened.append(str(path))
                self.assertNotIn("unopened-test", str(path))
                return original_open(path, *args, **kwargs)

            with patch("PIL.Image.open", side_effect=observed_open):
                result = build_audit(root, run, package, error_file, finding_file,
                                     source_config, output)
            self.assertEqual(result["visual_audit"]["fn_cells"], 2)
            self.assertTrue(opened)
            before = sha256_file(output / "audit.json")
            with self.assertRaises(DataContractError):
                build_audit(root, run, package, error_file, finding_file, source_config, output)
            self.assertEqual(before, sha256_file(output / "audit.json"))


if __name__ == "__main__":
    unittest.main()
