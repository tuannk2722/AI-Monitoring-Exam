from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError

MANIFEST_FIELDS = (
    "sample_id",
    "image_path",
    "label_path",
    "source",
    "video_id",
    "session_id",
    "room_id",
    "subject_id",
    "group_id",
    "split",
    "dataset_version",
    "label_map_version",
    "license_id",
    "sha256",
)


@dataclass(frozen=True, slots=True)
class ManifestRow:
    sample_id: str
    image_path: str
    label_path: str
    source: str
    video_id: str = ""
    session_id: str = ""
    room_id: str = ""
    subject_id: str = ""
    group_id: str = ""
    split: str = ""
    dataset_version: str = ""
    label_map_version: str = ""
    license_id: str = ""
    sha256: str = ""


def read_manifest(path: str | Path) -> list[ManifestRow]:
    manifest_path = Path(path)
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(MANIFEST_FIELDS) - set(reader.fieldnames or ())
        if missing:
            raise DataContractError(f"Manifest missing columns: {sorted(missing)}")
        return [
            ManifestRow(**{field: row.get(field, "") for field in MANIFEST_FIELDS})
            for row in reader
        ]


def write_manifest(path: str | Path, rows: list[ManifestRow]) -> None:
    manifest_path = Path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def validate_split_integrity(rows: list[ManifestRow]) -> None:
    group_splits: dict[str, set[str]] = {}
    sample_ids: set[str] = set()
    for row in rows:
        if row.sample_id in sample_ids:
            raise DataContractError(f"Duplicate sample_id: {row.sample_id}")
        sample_ids.add(row.sample_id)
        if row.split not in {"train", "val", "test"}:
            raise DataContractError(f"Invalid split for {row.sample_id}: {row.split!r}")
        if not row.group_id:
            raise DataContractError(
                f"Missing group_id for {row.sample_id}; unsafe to split by frame"
            )
        group_splits.setdefault(row.group_id, set()).add(row.split)
    leaked = {group: splits for group, splits in group_splits.items() if len(splits) > 1}
    if leaked:
        preview = dict(list(leaked.items())[:10])
        raise DataContractError(f"Group leakage across splits: {preview}")
