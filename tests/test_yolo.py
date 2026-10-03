import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.yolo import YoloAnnotation, remap_annotations


class YoloTests(unittest.TestCase):
    def test_parse_valid_annotation(self) -> None:
        annotation = YoloAnnotation.parse("2 0.5 0.5 0.2 0.4")
        self.assertEqual(annotation.class_id, 2)

    def test_out_of_bounds_annotation_is_rejected(self) -> None:
        with self.assertRaises(DataContractError):
            YoloAnnotation.parse("0 0.1 0.1 0.4 0.4")

    def test_unmapped_class_fails_closed(self) -> None:
        annotation = YoloAnnotation.parse("4 0.5 0.5 0.2 0.2")
        with self.assertRaises(DataContractError):
            remap_annotations([annotation], {0: 0})


if __name__ == "__main__":
    unittest.main()
