import unittest

from ai_exam_monitoring.contracts import BoundingBox, FrameRef, Prediction


class ContractTests(unittest.TestCase):
    def test_bbox_uses_named_xyxy_order(self) -> None:
        box = BoundingBox(1, 2, 10, 20)
        self.assertEqual((box.xmin, box.ymin, box.xmax, box.ymax), (1, 2, 10, 20))

    def test_invalid_bbox_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BoundingBox(10, 2, 1, 20)

    def test_nonfinite_coordinates_are_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            for index in range(4):
                coordinates = [1, 2, 10, 20]
                coordinates[index] = value
                with self.subTest(value=value, index=index), self.assertRaises(ValueError):
                    BoundingBox(*coordinates)

    def test_unknown_coordinate_space_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BoundingBox(1, 2, 10, 20, coordinate_space="unknown")

    def test_disciplinary_label_is_rejected(self) -> None:
        for label in ("cheating", "cheater", "no_cheating", "suspicious_person"):
            with self.assertRaises(ValueError):
                Prediction(
                    prediction_id="p1",
                    frame=FrameRef("s1", 0, 0),
                    model_version="m1",
                    task="detection",
                    label=label,
                    confidence=0.9,
                    bbox=BoundingBox(1, 2, 10, 20),
                )


if __name__ == "__main__":
    unittest.main()
