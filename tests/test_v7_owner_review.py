"""Kiểm ranh giới review proposal, unknown và recrop không tự approve."""

import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.v7_owner_review import (
    inherited_reason,
    merge_overrides,
    validate_overrides,
)


class OwnerReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [{"sample_id": "V7-B-080", "width": 765, "height": 1024,
                      "draft_xyxy": [0, 77, 549, 1024]}]
        self.override = {"sample_id": "V7-B-080", "final_proposed_states": ["U", "U"],
                         "final_reason": "Thiết bị chưa xác minh mobile", "owner_approved": False}

    def test_unknown_quarantine_is_allowed_without_negative_conversion(self) -> None:
        validate_overrides(self.rows, [self.override])
        self.assertEqual(self.override["final_proposed_states"], ["U", "U"])

    def test_approval_or_invalid_geometry_is_rejected(self) -> None:
        for change in ({"owner_approved": True}, {"final_xyxy": [0, 0, 800, 1024]},
                       {"sample_id": "V7-B-079"}):
            with self.subTest(change=change), self.assertRaises(DataContractError):
                validate_overrides(self.rows, [{**self.override, **change}])

    def test_reason_drops_revision_marker_without_changing_evidence(self) -> None:
        self.assertEqual(inherited_reason("QA R5: Mobile chưa rõ; phone U."),
                         "Mobile chưa rõ; phone U.")

    def test_supersession_cannot_silently_replace_label_proposal(self) -> None:
        first = {"overrides": [self.override]}
        second = {"overrides": [{**self.override, "final_proposed_states": ["P", "U"]}]}
        with self.assertRaises(DataContractError):
            merge_overrides(self.rows, [first, second])
        merged = merge_overrides(self.rows, [first, {
            **second, "supersedes_ids_from_root_r1": ["V7-B-080"]}])
        self.assertEqual(merged[0]["final_proposed_states"], ["P", "U"])


if __name__ == "__main__":
    unittest.main()
