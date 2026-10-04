"""Consolidation protects owner evidence and fails closed for formulation B."""
import hashlib
import json
import unittest
from pathlib import Path

from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.evaluation.evaluate import evaluate
from ai_exam_monitoring.training.train import train

ROOT = Path(__file__).resolve().parents[1]


class AuditConsolidationTests(unittest.TestCase):
    def test_all_historical_text_checksums_and_final_labels_are_preserved(self):
        count = 0
        for path in (ROOT / "artifacts/reports").glob("*-2026100*/audit.json"):
            bundle = json.loads(path.read_text(encoding="utf-8"))
            for record in bundle["records"].values():
                self.assertEqual(hashlib.sha256(record["text"].encode()).hexdigest(),
                                 record["sha256"])
                json.loads(record["text"])
                count += 1
        review = json.loads((ROOT / "artifacts/reports/roboflow-20261004/review.json")
                            .read_text(encoding="utf-8"))
        for record in review["records"].values():
            self.assertEqual(hashlib.sha256(record["text"].encode()).hexdigest(), record["sha256"])
            json.loads(record["text"])
            count += 1
        self.assertEqual(count, 54)
        for record in review["retired_files"].values():
            self.assertEqual(hashlib.sha256(record["text"].encode()).hexdigest(), record["sha256"])
        rows = review["current_person_crops"]
        self.assertEqual(len(rows), 28)
        self.assertEqual(sum(r["phone_use"] == "owner_approved_positive" for r in rows), 24)
        self.assertEqual(sum(r["looking_around"] == "owner_approved_positive" for r in rows), 5)
        self.assertEqual(sum("unknown" in (r["phone_use"], r["looking_around"]) for r in rows), 27)
        self.assertTrue(all(r["training_eligible"] is False for r in rows))
        self.assertFalse(review["dataset_accepted"])

    def test_legacy_train_and_evaluate_reject_b_before_loading_weights(self):
        with self.assertRaisesRegex(ConfigurationError, "Formulation B"):
            train("configs/baseline.yaml", "validation-only", "owner")
        with self.assertRaisesRegex(ConfigurationError, "Formulation B"):
            evaluate("configs/baseline.yaml", "validation-only")
