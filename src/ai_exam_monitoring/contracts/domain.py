from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class BoundingBox:
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    coordinate_space: Literal["pixel", "normalized"] = "pixel"

    def __post_init__(self) -> None:
        values = (self.xmin, self.ymin, self.xmax, self.ymax)
        if self.coordinate_space not in {"pixel", "normalized"}:
            raise ValueError("coordinate_space must be pixel or normalized")
        if not all(isfinite(value) for value in values):
            raise ValueError(f"BBox coordinates must be finite: {values}")
        if self.xmin >= self.xmax or self.ymin >= self.ymax:
            raise ValueError(f"Invalid bbox ordering: {values}")
        if self.coordinate_space == "normalized" and any(v < 0 or v > 1 for v in values):
            raise ValueError(f"Normalized bbox must be within [0, 1]: {values}")
        if self.coordinate_space == "pixel" and any(v < 0 for v in values):
            raise ValueError(f"Pixel bbox cannot contain negative values: {values}")


@dataclass(frozen=True, slots=True)
class FrameRef:
    session_id: str
    frame_index: int
    video_time_ms: int
    source_uri: str | None = None

    def __post_init__(self) -> None:
        if self.frame_index < 0 or self.video_time_ms < 0:
            raise ValueError("frame_index and video_time_ms must be non-negative")


@dataclass(frozen=True, slots=True)
class Prediction:
    prediction_id: str
    frame: FrameRef
    model_version: str
    task: str
    label: str
    confidence: float
    bbox: BoundingBox
    class_id: int | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be within [0, 1]")
        if self.label in {"cheating", "cheater", "no_cheating", "suspicious_person"}:
            raise ValueError("Prediction label must describe an observable behavior")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TrackObservation:
    session_id: str
    track_id: int
    frame: FrameRef
    bbox: BoundingBox
    source_prediction_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BehaviorEvent:
    event_id: str
    session_id: str
    track_id: int
    behavior: str
    start_frame: int
    end_frame: int
    start_time_ms: int
    end_time_ms: int
    aggregated_confidence: float
    model_version: str
    rule_version: str
    source_prediction_ids: tuple[str, ...]
    status: Literal["candidate", "confirmed", "dismissed"] = "candidate"

    def __post_init__(self) -> None:
        if self.end_frame < self.start_frame or self.end_time_ms < self.start_time_ms:
            raise ValueError("Event end cannot precede its start")
        if not 0 <= self.aggregated_confidence <= 1:
            raise ValueError("aggregated_confidence must be within [0, 1]")
