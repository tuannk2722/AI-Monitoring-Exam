from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigurationError


def load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.is_file():
        raise ConfigurationError(f"Config not found: {config_path}")
    try:
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in {config_path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ConfigurationError(f"Top-level YAML value must be a mapping: {config_path}")
    return loaded


def require(config: dict[str, Any], dotted_key: str) -> Any:
    value: Any = config
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise ConfigurationError(f"Missing required config key: {dotted_key}")
        value = value[part]
    if value is None or value == "" or (isinstance(value, str) and value.startswith("TBD")):
        raise ConfigurationError(f"Config key is unresolved: {dotted_key}")
    return value


def validate_training_config(config: dict[str, Any]) -> None:
    if config.get("formulation") == "B":
        raise ConfigurationError(
            "Formulation B trainer/evaluator is not implemented; "
            "legacy YOLO detection training is not a multi-label baseline."
        )
    for key in (
        "data.dataset_yaml",
        "data.dataset_version",
        "data.split_version",
        "data.label_map_version",
        "model.family",
        "model.checkpoint",
        "model.task",
        "train.epochs",
        "train.imgsz",
        "train.batch",
        "experiment.seed",
        "artifacts.root",
    ):
        require(config, key)

    if int(require(config, "train.epochs")) <= 0:
        raise ConfigurationError("train.epochs must be positive")
    if int(require(config, "train.imgsz")) <= 0:
        raise ConfigurationError("train.imgsz must be positive")
    if int(require(config, "train.batch")) == 0:
        raise ConfigurationError("train.batch cannot be zero")
