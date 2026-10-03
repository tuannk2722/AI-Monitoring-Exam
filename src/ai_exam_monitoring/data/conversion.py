from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .manifest import ManifestRow, read_manifest
from .yolo import read_yolo_file, remap_annotations


def load_and_validate_source(
    source_root: str | Path,
    source_id: str,
    class_mapping: dict[int, int],
    dataset_version: str,
    label_map_version: str,
) -> list[tuple[ManifestRow, Path, Path, str]]:
    """Validate one source manifest and return immutable conversion records.

    Required file: ``<source_root>/source_manifest.csv``. Paths inside the manifest
    are relative to source_root. Group metadata is mandatory to prevent frame leakage.
    """

    root = Path(source_root)
    manifest_path = root / "source_manifest.csv"
    if not manifest_path.is_file():
        raise DataContractError(
            f"{source_id}: missing {manifest_path}. Create it after source audit; "
            "do not infer video/person groups from filenames silently."
        )
    if not class_mapping:
        raise DataContractError(
            f"{source_id}: label_mapping is empty; audit exact source IDs first"
        )

    records: list[tuple[ManifestRow, Path, Path, str]] = []
    for row in read_manifest(manifest_path):
        if row.source and row.source != source_id:
            raise DataContractError(f"{source_id}: manifest row has source={row.source!r}")
        if not row.group_id:
            raise DataContractError(f"{source_id}/{row.sample_id}: group_id is required")
        image_path = (root / row.image_path).resolve()
        label_path = (root / row.label_path).resolve()
        if root.resolve() not in image_path.parents or root.resolve() not in label_path.parents:
            raise DataContractError(f"{row.sample_id}: manifest path escapes source root")
        if not image_path.is_file() or not label_path.is_file():
            raise DataContractError(f"{row.sample_id}: image or label file is missing")

        annotations = remap_annotations(read_yolo_file(label_path), class_mapping)
        label_text = "\n".join(item.serialize() for item in annotations)
        if label_text:
            label_text += "\n"
        canonical = replace(
            row,
            source=source_id,
            dataset_version=dataset_version,
            label_map_version=label_map_version,
            sha256=sha256_file(image_path),
        )
        records.append((canonical, image_path, label_path, label_text))
    return records
