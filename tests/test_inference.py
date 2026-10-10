import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.inference.detect import main
from ai_exam_monitoring.inference.detector import UltralyticsDetector


class InferenceTests(unittest.TestCase):
    def detector(self):
        detector = UltralyticsDetector.__new__(UltralyticsDetector)
        detector._model = Mock()
        detector.model_version = "fixture-model"
        detector.confidence = 0.5
        return detector

    def test_invalid_fps_fails_before_model_prediction(self):
        for fps in (None, 0, -1, float("nan"), float("inf"), float("-inf")):
            detector = self.detector()
            with self.subTest(fps=fps), self.assertRaises(ConfigurationError):
                list(detector.predict("fixture.mp4", "fixture-session", fps))
            detector._model.predict.assert_not_called()

    def test_timestamps_follow_frame_index_including_empty_frames(self):
        detector = self.detector()
        box = SimpleNamespace(cls=Mock(), conf=Mock(), xyxy=[Mock()])
        box.cls.item.return_value = 0
        box.conf.item.return_value = 0.8
        box.xyxy[0].tolist.return_value = [1, 2, 10, 20]
        detector._model.predict.return_value = [
            SimpleNamespace(names={0: "person"}, boxes=None),
            SimpleNamespace(names={0: "person"}, boxes=[box]),
        ]
        rows = list(detector.predict("fixture.mp4", "fixture-session", 25))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].frame.frame_index, 1)
        self.assertEqual(rows[0].frame.video_time_ms, 40)

    def test_cli_preserves_existing_output_before_loading_model(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.mp4"
            checkpoint = Path(directory) / "weights.pt"
            source.write_bytes(b"software fixture")
            checkpoint.write_bytes(b"software fixture")
            args = ["detect", "--source", str(source), "--checkpoint", str(checkpoint),
                    "--model-version", "fixture", "--session-id", "fixture",
                    "--output", str(source), "--fps", "25"]
            with patch("sys.argv", args), contextlib.redirect_stderr(io.StringIO()), patch(
                "ai_exam_monitoring.inference.detect.UltralyticsDetector"
            ) as model, self.assertRaises(SystemExit) as raised:
                main()
            self.assertEqual(raised.exception.code, 2)
            model.assert_not_called()
            self.assertEqual(source.read_bytes(), b"software fixture")

    def test_malformed_detector_geometry_is_rejected(self):
        for coordinates in ([1, 2, 3], [1, 2, 3, 4, 5]):
            detector = self.detector()
            box = SimpleNamespace(cls=Mock(), conf=Mock(), xyxy=[Mock()])
            box.cls.item.return_value = 0
            box.xyxy[0].tolist.return_value = coordinates
            detector._model.predict.return_value = [
                SimpleNamespace(names={0: "person"}, boxes=[box])]
            with self.subTest(coordinates=coordinates), self.assertRaises(ConfigurationError):
                list(detector.predict("fixture.mp4", "fixture", 25))


if __name__ == "__main__":
    unittest.main()
