"""Kiểm proposal geometry; không tạo nhãn hoặc approval canonical."""

import tempfile
import unittest
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_source_candidates import (
    _new_output,
    context_proposal,
    pixel_box,
)
from ai_exam_monitoring.data.yolo import YoloAnnotation


class SourceCandidateTests(unittest.TestCase):
    def test_device_container_is_only_ambiguous_hint(self):
        phone = YoloAnnotation(0, 0.5, 0.6, 0.02, 0.04)
        left = YoloAnnotation(1, 0.4, 0.5, 0.5, 0.8)
        right = YoloAnnotation(1, 0.6, 0.5, 0.5, 0.8)
        draft = context_proposal(phone, [left, right], 640, 480, 0.1)
        self.assertEqual(draft.containing_body_count, 2)
        self.assertEqual(draft.method, "body_container_hint")
        self.assertFalse(hasattr(draft, "phone_use"))
        self.assertFalse(hasattr(draft, "leakage_group_id"))

    def test_unrelated_person_not_assigned_to_device(self):
        phone = YoloAnnotation(0, 0.9, 0.5, 0.1, 0.1)
        person = YoloAnnotation(1, 0.2, 0.5, 0.2, 0.8)
        draft = context_proposal(phone, [person], 100, 100, 0)
        self.assertEqual(draft.box, pixel_box(phone, 100, 100))
        self.assertEqual(draft.containing_body_count, 0)
        self.assertEqual(draft.method, "source_anchor_hint")

    def test_padding_clips_edges_without_zero_area(self):
        a = YoloAnnotation(0, 0.5, 0.5, 1, 1)
        self.assertEqual(context_proposal(a, [], 31, 17, 1).box.xyxy, (0, 0, 31, 17))
        with self.assertRaises(DataContractError):
            context_proposal(a, [], 31, 17, -0.1)

    def test_existing_and_escaping_outputs_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "interim"
            root.mkdir()
            _new_output(root / "new", root)
            for p in [root, root / ".." / "elsewhere"]:
                with self.assertRaises(DataContractError):
                    _new_output(p, root)
            (root / "new").mkdir()
            with self.assertRaises(DataContractError):
                _new_output(root / "new", root)


if __name__ == "__main__":
    unittest.main()
