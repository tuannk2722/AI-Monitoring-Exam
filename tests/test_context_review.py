import unittest
from copy import deepcopy

from ai_exam_monitoring.data.review import validate_context_plan


class ContextReviewTests(unittest.TestCase):
    def fixture(self):
        base = [{"id": "a", "image_id": "im", "person_xyxy": [2, 2, 6, 6]}]
        row = {"id": "a", "person_xyxy": [2, 2, 6, 6],
               "context_crop_xyxy": [1, 1, 8, 8], "phone_use": "owner_approved_positive",
               "looking_around": "unknown", "owner_review": "pending", "training_eligible": False}
        return {"items": [row], "additional_people": [], "dataset_accepted": False}, base

    def test_unknown_remains_unknown_and_geometry_unchanged(self):
        plan, base = self.fixture()
        original = deepcopy(plan)
        validate_context_plan(plan, base, {"im": (10, 10)})
        self.assertEqual(plan, original)

    def test_reject_clipped_person_invalid_bounds_changed_box_and_promotions(self):
        for case in ("clipped", "bounds", "nan", "changed", "negative", "approved", "eligible"):
            plan, base = self.fixture()
            row = plan["items"][0]
            if case == "clipped":
                row["context_crop_xyxy"] = [3, 1, 8, 8]
            elif case == "bounds":
                row["context_crop_xyxy"] = [1, 1, 11, 8]
            elif case == "nan":
                row["context_crop_xyxy"][0] = float("nan")
            elif case == "changed":
                row["person_xyxy"][0] = 3
            elif case == "negative":
                row["looking_around"] = "negative"
            elif case == "approved":
                row["owner_review"] = "approved"
            else:
                row["training_eligible"] = True
            with self.subTest(case=case), self.assertRaises(ValueError):
                validate_context_plan(plan, base, {"im": (10, 10)})

    def test_exact_coverage_and_new_person_cannot_inherit_phone_positive(self):
        plan, base = self.fixture()
        extra = deepcopy(plan["items"][0])
        extra.update(id="b", image_id="im")
        plan["additional_people"] = [extra]
        with self.assertRaises(ValueError):
            validate_context_plan(plan, base, {"im": (10, 10)})
        extra["phone_use"] = "unknown"
        validate_context_plan(plan, base, {"im": (10, 10)})
        plan["items"] = []
        with self.assertRaises(ValueError):
            validate_context_plan(plan, base, {"im": (10, 10)})
