"""Explicit source paths and source class names; no canonical mapping or group inference."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

from ai_exam_monitoring.common.errors import DataContractError

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def is_label(path: Path) -> bool:
    return (
        path.suffix.lower() == ".txt"
        and path.stem.lower() != "classes"
        and not path.stem.lower().startswith("readme")
    )


def label_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and is_label(path))


def validate_source_names(names: dict[int, str]) -> None:
    if not names or any(
        type(key) is not int
        or key < 0
        or not isinstance(value, str)
        or not value.strip()
        or "\n" in value
        or "\r" in value
        for key, value in names.items()
    ):
        raise DataContractError("Source names must map non-negative integer IDs to non-empty names")


def load_source_names(path: str | Path) -> dict[int, str]:
    def unique_pairs(pairs: list[tuple[object, object]]) -> dict[object, object]:
        result: dict[object, object] = {}
        for key, value in pairs:
            if key in result:
                raise DataContractError(f"Duplicate source ID: {key}")
            result[key] = value
        return result

    class UniqueLoader(yaml.SafeLoader):
        pass

    def unique_yaml_mapping(loader: UniqueLoader, node: yaml.MappingNode) -> dict[object, object]:
        return unique_pairs(loader.construct_pairs(node, deep=True))

    UniqueLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_yaml_mapping
    )
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    if source.suffix.lower() in {".yaml", ".yml"}:
        try:
            document = yaml.load(text, Loader=UniqueLoader)
        except (yaml.YAMLError, TypeError) as exc:
            raise DataContractError(f"Invalid source names YAML: {exc}") from exc
        raw = document.get("names") if isinstance(document, dict) else None
    else:
        raw = json.loads(text, object_pairs_hook=unique_pairs)
    if not isinstance(raw, dict):
        raise DataContractError(
            "Provide a JSON ID/name object or YAML with a names ID/name mapping"
        )
    names = {}
    for key, value in raw.items():
        if type(key) is not int and (
            not isinstance(key, str) or not key.isascii() or not key.isdecimal()
        ):
            raise DataContractError(f"Invalid source ID: {key!r}")
        class_id = int(key)
        if class_id in names:
            raise DataContractError(f"Duplicate source ID: {key}")
        names[class_id] = value
    validate_source_names(names)
    return names


@dataclass(frozen=True)
class SourceLayout:
    root: Path
    images: Path
    labels: Path

    @classmethod
    def create(cls, root: str | Path, images: str, labels: str) -> SourceLayout:
        source = Path(root).resolve()
        if not source.is_dir():
            raise DataContractError(f"Dataset directory not found: {source}")
        directories = []
        for relative in (images, labels):
            directory = (source / relative).resolve()
            if Path(relative).is_absolute() or not directory.is_relative_to(source):
                raise DataContractError("Image/label directories must be relative to dataset root")
            if not directory.is_dir():
                raise DataContractError(f"Source directory not found: {directory}")
            directories.append(directory)
        return cls(source, *directories)

    def inventory(self) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
        images: dict[str, list[Path]] = defaultdict(list)
        labels: dict[str, list[Path]] = defaultdict(list)
        for path in sorted(self.images.rglob("*")):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                images[path.relative_to(self.images).with_suffix("").as_posix()].append(path)
        for path in label_files(self.labels):
            labels[path.relative_to(self.labels).with_suffix("").as_posix()].append(path)
        for paths in (*images.values(), *labels.values()):
            for path in paths:
                if not path.resolve().is_relative_to(self.root):
                    raise DataContractError(f"Source file escapes dataset root: {path}")
        return dict(images), dict(labels)


def validate_output(output: str | Path, source: Path) -> Path:
    destination = Path(output).resolve()
    raw = Path(__file__).resolve().parents[3] / "data" / "raw"
    if destination.is_relative_to(source) or destination.is_relative_to(raw.resolve()):
        raise DataContractError("Output must be outside the source dataset and repository data/raw")
    return destination
