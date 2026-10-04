import unittest
from copy import deepcopy

from ai_exam_monitoring.data.review import apply_context_decisions


class ContextDecisionTests(unittest.TestCase):
    def fixture(self):
        rows = [{"id": str(i), "source_image": "train/images/fixture.jpg",
                 "person_xyxy": [1, 1, 5, 5], "context_crop_xyxy": [0, 0, 6, 6],
                 "owner_review": "pending", "training_eligible": False,
                 "phone_use": "unknown" if i == 2 else "owner_approved_positive",
                 "looking_around": "unknown" if i == 1 else "proposed_positive"}
                for i in range(3)]
        decisions = {"dataset_accepted": False, "answers_verbatim": {"R": "fixture approval"},
                     "items": [{"id": str(i), "approve_person_and_crop": True,
                                "approve_looking_around": i != 1, "answer_ids": ["R"]}
                               for i in range(3)]}
        return rows, decisions

    def test_cooccurrence_unknown_and_geometry_preserved(self):
        rows, decisions = self.fixture()
        original = deepcopy(rows)
        result = apply_context_decisions(rows, decisions)
        self.assertEqual(rows, original)
        self.assertEqual(result[0]["phone_use"], "owner_approved_positive")
        self.assertEqual(result[0]["looking_around"], "owner_approved_positive")
        self.assertEqual(result[1]["looking_around"], "unknown")
        self.assertEqual(result[2]["phone_use"], "unknown")
        for before, after in zip(rows, result, strict=True):
            for key in ("person_xyxy", "context_crop_xyxy"):
                self.assertEqual(before[key], after[key])
            self.assertIs(after["training_eligible"], False)

    def test_incomplete_duplicate_unproposed_or_unsupported_reviews_fail(self):
        for case in ("missing", "duplicate", "invented", "evidence", "accept", "test"):
            rows, decisions = self.fixture()
            if case == "missing":
                decisions["items"].pop()
            elif case == "duplicate":
                decisions["items"].append(decisions["items"][0])
            elif case == "invented":
                decisions["items"][1]["approve_looking_around"] = True
            elif case == "evidence":
                decisions["answers_verbatim"] = {}
            elif case == "accept":
                decisions["dataset_accepted"] = True
            else:
                rows[0]["source_image"] = "test/images/fixture.jpg"
            with self.subTest(case=case), self.assertRaises(ValueError):
                apply_context_decisions(rows, decisions)
