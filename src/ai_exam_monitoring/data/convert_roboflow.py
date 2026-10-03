from __future__ import annotations

from pathlib import Path

from .conversion import load_and_validate_source


def convert_roboflow(
    root: str | Path,
    class_mapping: dict[int, int],
    dataset_version: str,
    label_map_version: str,
):
    """Convert an audited Roboflow YOLO export with explicit provenance/mapping."""

    return load_and_validate_source(
        root, "roboflow_exam", class_mapping, dataset_version, label_map_version
    )
