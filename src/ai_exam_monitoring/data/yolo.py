from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError


@dataclass(frozen=True, slots=True)
class YoloAnnotation:
    class_id: int
    x_center: float
    y_center: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.class_id < 0:
            raise DataContractError("YOLO class_id must be non-negative")
        values = (self.x_center, self.y_center, self.width, self.height)
        if any(value < 0 or value > 1 for value in values):
            raise DataContractError(f"YOLO coordinates must be within [0, 1]: {values}")
        if self.width <= 0 or self.height <= 0:
            raise DataContractError("YOLO width/height must be positive")
        if self.x_center - self.width / 2 < 0 or self.x_center + self.width / 2 > 1:
            raise DataContractError("YOLO box exceeds horizontal image bounds")
        if self.y_center - self.height / 2 < 0 or self.y_center + self.height / 2 > 1:
            raise DataContractError("YOLO box exceeds vertical image bounds")

    @classmethod
    def parse(cls, line: str) -> YoloAnnotation:
        parts = line.strip().split()
        if len(parts) != 5:
            raise DataContractError(f"Expected 5 YOLO fields, got {len(parts)}: {line!r}")
        try:
            return cls(int(parts[0]), *(float(value) for value in parts[1:]))
        except ValueError as exc:
            raise DataContractError(f"Invalid YOLO annotation: {line!r}") from exc

    def serialize(self) -> str:
        return (
            f"{self.class_id} {self.x_center:.8f} {self.y_center:.8f} "
            f"{self.width:.8f} {self.height:.8f}"
        )


def read_yolo_file(path: str | Path) -> list[YoloAnnotation]:
    label_path = Path(path)
    annotations: list[YoloAnnotation] = []
    for line_number, line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            annotations.append(YoloAnnotation.parse(line))
        except DataContractError as exc:
            raise DataContractError(f"{label_path}:{line_number}: {exc}") from exc
    return annotations


def remap_annotations(
    annotations: list[YoloAnnotation], class_mapping: dict[int, int]
) -> list[YoloAnnotation]:
    remapped: list[YoloAnnotation] = []
    for annotation in annotations:
        if annotation.class_id not in class_mapping:
            raise DataContractError(f"No mapping for source class id {annotation.class_id}")
        remapped.append(
            YoloAnnotation(
                class_id=class_mapping[annotation.class_id],
                x_center=annotation.x_center,
                y_center=annotation.y_center,
                width=annotation.width,
                height=annotation.height,
            )
        )
    return remapped
