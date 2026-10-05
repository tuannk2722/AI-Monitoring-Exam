"""Strict, resolved experiment variables for the approved CPU linear probe."""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import ConfigurationError


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str
    owner: str
    hypothesis: str
    approval_ref: str
    dataset: str
    dataset_version: str
    split_version: str
    encoding_version: str
    payload_sha256: str
    weights: str
    weights_sha256: str
    weights_url: str
    seed: int
    image_size: int
    mean: list[float]
    std: list[float]
    fill: list[int]
    extraction_batch_size: int
    threads: int
    learning_rate: float
    weight_decay: float
    max_epochs: int
    patience: int
    min_delta: float
    threshold: float
    model: str
    weights_id: str
    device: str
    optimizer: str
    loss: str
    transform: str
    target_order: list[str]
    run_kind: str

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ConfigurationError(f"Unresolved {field.name}")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", self.experiment_id):
            raise ConfigurationError("Unsafe experiment ID")
        fixed = {
            "model": "resnet18_frozen_linear", "weights_id": "IMAGENET1K_V1",
            "device": "cpu", "optimizer": "AdamW", "loss": "macro_masked_bce",
            "transform": "rgb_letterbox_bilinear_v1",
            "target_order": ["phone_use", "looking_around"],
        }
        for key, expected in fixed.items():
            if getattr(self, key) != expected:
                raise ConfigurationError(f"Unsupported {key}; expected {expected}")
        if self.run_kind not in {"smoke", "baseline"}:
            raise ConfigurationError("run_kind must be smoke or baseline")
        for key in ("image_size", "extraction_batch_size", "threads", "max_epochs", "patience"):
            value = getattr(self, key)
            if type(value) is not int or value <= 0:
                raise ConfigurationError(f"{key} must be a positive integer")
        if type(self.seed) is not int or not 0 <= self.seed < 2**32:
            raise ConfigurationError("seed must be a nonnegative 32-bit integer")
        for key in ("learning_rate", "weight_decay", "min_delta", "threshold"):
            value = getattr(self, key)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ConfigurationError(f"Invalid finite nonnegative {key}")
        if self.learning_rate == 0 or not 0 < self.threshold < 1:
            raise ConfigurationError("Invalid learning rate/threshold")
        for key in ("mean", "std", "fill"):
            value = getattr(self, key)
            if not isinstance(value, list) or len(value) != 3:
                raise ConfigurationError(f"{key} requires three channels")
            if any(type(v) not in (int, float) or not math.isfinite(v) for v in value):
                raise ConfigurationError(f"Invalid {key}")
        if any(v <= 0 for v in self.std):
            raise ConfigurationError("std must be positive")
        if any(type(v) is not int or not 0 <= v <= 255 for v in self.fill):
            raise ConfigurationError("fill must contain RGB byte values")
        for key in ("payload_sha256", "weights_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", getattr(self, key)):
                raise ConfigurationError(f"{key} must pin a SHA-256")

    def to_dict(self) -> dict:
        return asdict(self)


def load_config(path: str | Path) -> ExperimentConfig:
    payload = load_yaml(path)
    expected = {f.name for f in fields(ExperimentConfig)}
    if set(payload) != expected:
        raise ConfigurationError(f"Config keys differ: {set(payload) ^ expected}")
    return ExperimentConfig(**payload)


def verify_approval(config: ExperimentConfig, workspace: Path) -> None:
    from .artifacts import digest_json

    path = (workspace / config.approval_ref).resolve()
    if not path.is_relative_to(workspace.resolve()):
        raise ConfigurationError("Approval must be in the workspace")
    approval = json.loads(path.read_text(encoding="utf-8"))
    approved_hash = approval.get("configs", {}).get(config.experiment_id)
    if (approval.get("status") != "approved" or approval.get("owner") != config.owner
            or approval.get("scope") != "local_classifier_research"
            or approved_hash != digest_json(config.to_dict())):
        raise ConfigurationError("Experiment config does not match recorded owner approval")
