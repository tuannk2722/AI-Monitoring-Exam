from __future__ import annotations

from pathlib import Path

from .conversion import load_and_validate_source


def convert_scb(
    root: str | Path,
    class_mapping: dict[int, int],
    dataset_version: str,
    label_map_version: str,
):
    """Convert an audited SCB5 YOLO export using its reviewed source manifest.

    SCB5 variants can have different annotation layouts. This converter intentionally
    accepts only normalized YOLO labels plus an explicit mapping instead of guessing.
    """

    return load_and_validate_source(root, "scb5", class_mapping, dataset_version, label_map_version)
