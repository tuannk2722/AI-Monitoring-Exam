"""QA transform parity và guard; không mở dữ liệu thật/model."""

from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.v7_input_evidence import (
    VisualEvidenceFinding,
    _inside,
    letterbox_geometry,
    letterbox_rgb,
    summarize_findings,
)


class InputEvidenceTests(unittest.TestCase):
    def test_parity_with_training_letterbox_on_odd_dimensions_and_modes(self) -> None:
        from ai_exam_monitoring.training.data import letterbox

        config = SimpleNamespace(image_size=224, fill=[124, 116, 104])
        for size in [(175, 308), (221, 292), (1001, 111), (1, 300), (224, 224), (333, 1001)]:
            for mode in ["RGB", "L", "RGBA"]:
                image = Image.new(mode, size)
                for x in range(size[0]):
                    image.putpixel((x, x % size[1]), x % 251)
                expected = letterbox(image, config)  # type: ignore[arg-type]
                actual = letterbox_rgb(image, 224, (124, 116, 104))
                self.assertEqual(actual.mode, "RGB")
                self.assertEqual(actual.size, expected.size)
                self.assertEqual(actual.tobytes(), expected.tobytes())

    def test_geometry_preserves_full_context_and_padded_center(self) -> None:
        self.assertEqual(letterbox_geometry((175, 308), 224), ((127, 224), (48, 0)))
        self.assertEqual(letterbox_geometry((1001, 111), 224), ((224, 25), (0, 99)))
        image = Image.new("RGB", (1, 300), (1, 2, 3))
        actual = letterbox_rgb(image, 224, (124, 116, 104))
        self.assertEqual(actual.getpixel((111, 0)), (1, 2, 3))
        self.assertEqual(actual.getpixel((110, 0)), (124, 116, 104))

    def test_invalid_geometry_fill_and_output_escape_rejected(self) -> None:
        for size in [0, -1, True]:
            with self.assertRaises(DataContractError):
                letterbox_geometry((10, 10), size)
        with self.assertRaises(DataContractError):
            letterbox_rgb(Image.new("RGB", (10, 10)), 224, (-1, 0, 0))
        workspace = Path.cwd().resolve()
        with self.assertRaises(DataContractError):
            _inside(workspace, "outputs/../../test.png", "outputs")

    def test_visual_review_coverage_and_roi_guard(self) -> None:
        row = VisualEvidenceFinding("V7-B-001", "clear", "clear", "ambiguous", "Đã xem")
        self.assertEqual(summarize_findings([row], {row.sample_id})["records"], 1)
        for rows, expected in [([row, row], {row.sample_id}), ([row], {"V7-B-003"})]:
            with self.assertRaises(DataContractError):
                summarize_findings(rows, expected)
        with self.assertRaises(DataContractError):
            VisualEvidenceFinding("V7-B-003", "clear", "clear", "clear", "Phone",
                                  (0, 0, 225, 20))


if __name__ == "__main__":
    unittest.main()
