from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

from ai_exam_monitoring.common.config import load_yaml, require
from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError

from .convert_roboflow import convert_roboflow
from .convert_scb import convert_scb
from .manifest import ManifestRow, validate_split_integrity, write_manifest
from .split import assign_grouped_splits

CONVERTERS = {"scb": convert_scb, "roboflow_yolo": convert_roboflow}


def _parse_class_mapping(raw: dict[str, Any], canonical: dict[str, int]) -> dict[int, int]:
    mapping: dict[int, int] = {}
    for source_id, target in raw.items():
        target_id = canonical.get(str(target), target if isinstance(target, int) else None)
        if target_id is None:
            raise ConfigurationError(f"Unknown canonical target label: {target!r}")
        mapping[int(source_id)] = int(target_id)
    return mapping


def build_dataset(config_path: str | Path) -> dict[str, Any]:
    config = load_yaml(config_path)
    if config.get("formulation") == "B":
        raise DataContractError(
            "Formulation B requires a reviewed multi-label crop exporter; "
            "the legacy YOLO detection builder cannot export it."
        )
    dataset_version = str(require(config, "dataset_version"))
    split_version = str(require(config, "split_version"))
    label_map_version = str(require(config, "label_map_version"))
    output_dir = Path(str(require(config, "output_dir")))
    if output_dir.exists() and any(output_dir.iterdir()):
        raise DataContractError(
            f"Output directory is not empty: {output_dir}. "
            "Archive/version or remove it deliberately before rebuilding; stale files are unsafe."
        )
    seed = int(require(config, "seed"))
    ratios = {key: float(value) for key, value in require(config, "split_ratios").items()}
    canonical_labels = require(config, "canonical_labels")
    canonical = {str(item["name"]): int(item["id"]) for item in canonical_labels}
    mappings = require(config, "label_mapping")

    conversion_records: list[tuple[ManifestRow, Path, Path, str]] = []
    for source in require(config, "sources"):
        source_id = str(source["id"])
        if source.get("status") != "accepted":
            raise DataContractError(
                f"Source {source_id} is {source.get('status')!r}; mark accepted "
                "only after audit/license review"
            )
        converter_name = str(source["converter"])
        if converter_name not in CONVERTERS:
            raise ConfigurationError(f"Unsupported converter: {converter_name}")
        class_mapping = _parse_class_mapping(mappings.get(source_id, {}), canonical)
        conversion_records.extend(
            CONVERTERS[converter_name](
                source["root"], class_mapping, dataset_version, label_map_version
            )
        )

    if not conversion_records:
        raise DataContractError("No samples available after source conversion")
    sample_ids = [record[0].sample_id for record in conversion_records]
    if len(sample_ids) != len(set(sample_ids)):
        raise DataContractError("sample_id must be globally unique across sources")

    split_rows = assign_grouped_splits([record[0] for record in conversion_records], ratios, seed)
    split_by_id = {row.sample_id: row.split for row in split_rows}
    final_rows: list[ManifestRow] = []

    for row, image_path, _label_path, label_text in conversion_records:
        split = split_by_id[row.sample_id]
        image_target = output_dir / "images" / split / f"{row.sample_id}{image_path.suffix.lower()}"
        label_target = output_dir / "labels" / split / f"{row.sample_id}.txt"
        image_target.parent.mkdir(parents=True, exist_ok=True)
        label_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image_path, image_target)
        label_target.write_text(label_text, encoding="utf-8")
        final_rows.append(
            replace(
                row,
                image_path=str(image_target),
                label_path=str(label_target),
                split=split,
            )
        )

    validate_split_integrity(final_rows)
    write_manifest(output_dir / "manifest.csv", final_rows)
    dataset_yaml = {
        "path": str(output_dir.resolve()),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": {item["id"]: item["name"] for item in canonical_labels},
    }
    (output_dir / "dataset.yaml").write_text(
        yaml.safe_dump(dataset_yaml, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    (output_dir / "label_map.yaml").write_text(
        yaml.safe_dump(
            {
                "version": label_map_version,
                "canonical": dataset_yaml["names"],
                "source_mapping": mappings,
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    summary = {
        "dataset_version": dataset_version,
        "split_version": split_version,
        "label_map_version": label_map_version,
        "samples": len(final_rows),
        "split_counts": {
            split: sum(row.split == split for row in final_rows)
            for split in ("train", "val", "test")
        },
        "sources": sorted({row.source for row in final_rows}),
    }
    (output_dir / "dataset_report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the canonical grouped-split dataset")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    print(json.dumps(build_dataset(args.config), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
