from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.contracts import BoundingBox, FrameRef, Prediction


class UltralyticsDetector:
    def __init__(self, checkpoint: str | Path, model_version: str, confidence: float = 0.25):
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be within [0, 1]")
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ConfigurationError(
                "Install ML dependencies: pip install -r requirements/ml.txt"
            ) from exc
        self._model = YOLO(str(checkpoint))
        self.model_version = model_version
        self.confidence = confidence

    def predict(
        self, source: str | Path, session_id: str, fps: float | None = None
    ) -> Iterator[Prediction]:
        for frame_index, result in enumerate(
            self._model.predict(
                source=str(source), conf=self.confidence, stream=True, verbose=False
            )
        ):
            video_time_ms = round(frame_index * 1000 / fps) if fps else 0
            frame = FrameRef(
                session_id=session_id,
                frame_index=frame_index,
                video_time_ms=video_time_ms,
                source_uri=str(source),
            )
            names = result.names
            if result.boxes is None:
                continue
            for detection_index, box in enumerate(result.boxes):
                class_id = int(box.cls.item())
                label = str(names[class_id])
                coordinates = [float(value) for value in box.xyxy[0].tolist()]
                prediction_id = str(
                    uuid5(
                        NAMESPACE_URL,
                        f"{session_id}:{frame_index}:{detection_index}:{self.model_version}",
                    )
                )
                yield Prediction(
                    prediction_id=prediction_id,
                    frame=frame,
                    model_version=self.model_version,
                    task="detection",
                    label=label,
                    confidence=float(box.conf.item()),
                    bbox=BoundingBox(*coordinates, coordinate_space="pixel"),
                    class_id=class_id,
                )
