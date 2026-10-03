"""Synthetic software fixtures; no dataset/model quality claims."""

import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.yolo import YoloAnnotation
from scripts.audits.roboflow_w02_preview import EXPECTED, repair_w02


class W02PreviewTests(unittest.TestCase):
    def test_only_reviewed_row_changes_and_left_edge_is_preserved(self):
        good = b"2 0.5 0.5 0.2 0.2\r\n"
        raw = good * 3 + EXPECTED.encode() + b"\r\n" + good
        with self.assertRaises(DataContractError):
            YoloAnnotation.parse(EXPECTED)
        result = repair_w02(raw)
        before, after = raw.splitlines(keepends=True), result.splitlines(keepends=True)
        self.assertEqual(
            [i + 1 for i, pair in enumerate(zip(before, after, strict=True)) if pair[0] != pair[1]],
            [4],
        )
        box = YoloAnnotation.parse(after[3].decode())
        self.assertEqual(box.class_id, 0)
        self.assertAlmostEqual(
            box.x_center - box.width / 2, 0.9547836538461538 - 0.09045673076923078 / 2
        )
        self.assertEqual(box.x_center + box.width / 2, 1.0)
        self.assertTrue(after[3].endswith(b"\r\n"))

    def test_rejects_unreviewed_rows_including_nonfinite(self):
        for row in (
            "0 nan 0.5 0.1 0.1",
            "0 inf 0.5 0.1 0.1",
            EXPECTED.replace("0.954", "0.955"),
            "1 0.5 0.5 0.1 0.1",
        ):
            with self.subTest(row=row), self.assertRaises(ValueError):
                repair_w02(("\n" * 3 + row).encode())
        with self.assertRaises(ValueError):
            repair_w02(b"")
