"""Frozen pretrained encoder and hash-bound split feature caches."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

import torch
from torch import nn
from torchvision.models import resnet18

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import PilotRecord

from .artifacts import code_identity, digest_json, save_checkpoint, write_json
from .config import ExperimentConfig
from .data import crop_path, image_tensor, labels


class FrozenEncoder(nn.Module):
    def __init__(self, weights: Path, expected_sha256: str):
        super().__init__()
        if sha256_file(weights) != expected_sha256:
            raise DataContractError("Pretrained weights SHA differs")
        self.network = resnet18(weights=None)
        self.network.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
        self.network.fc = nn.Identity()
        self.requires_grad_(False)
        self.eval()

    def train(self, mode: bool = True) -> FrozenEncoder:
        super().train(False)
        return self

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            return self.network(images)


@dataclass
class SplitFeatures:
    records: list[PilotRecord]
    features: torch.Tensor
    values: torch.Tensor
    mask: torch.Tensor
    fingerprint: str


def extract_features(encoder: FrozenEncoder, root: Path, records: list[PilotRecord],
                     config: ExperimentConfig, cache: Path) -> SplitFeatures:
    if not records or len({r.usage for r in records}) != 1:
        raise DataContractError("Feature extraction requires one nonempty split")
    # Validate bytes even when reusing a cache, never silently use stale features.
    paths = [crop_path(root, r) for r in records]
    identity = {"ids": [r.sample_id for r in records],
                "crop_sha256": [r.crop.crop_sha256 for r in records],
                "weights": config.weights_sha256, "code": code_identity()["sha256"],
                "transform": {k: config.to_dict()[k] for k in
                              ("image_size", "mean", "std", "fill", "transform")},
                "environment": {k: version(k) for k in ("torch", "torchvision", "Pillow")}}
    fingerprint = digest_json(identity)
    values, mask = labels(records)
    receipt = cache.with_suffix(".json")
    if cache.exists() or receipt.exists():
        import json

        if not cache.is_file() or not receipt.is_file():
            raise DataContractError("Incomplete feature cache")
        meta = json.loads(receipt.read_text(encoding="utf-8"))
        if meta["fingerprint"] != fingerprint or meta["sha256"] != sha256_file(cache):
            raise DataContractError("Stale/corrupt feature cache; use a new run/cache")
        payload = torch.load(cache, map_location="cpu", weights_only=True)
        features = payload["features"]
        if payload["fingerprint"] != fingerprint:
            raise DataContractError("Feature cache identity changed")
    else:
        cache.parent.mkdir(parents=True, exist_ok=True)
        batches = []
        encoder.eval()
        for start in range(0, len(paths), config.extraction_batch_size):
            inputs = torch.stack([image_tensor(p, config)
                                  for p in paths[start:start + config.extraction_batch_size]])
            batches.append(encoder(inputs).detach().cpu())
        features = torch.cat(batches)
        save_checkpoint(cache, {"features": features, "fingerprint": fingerprint})
        write_json(receipt, {"fingerprint": fingerprint, "sha256": sha256_file(cache),
                             "identity": identity})
    if features.shape != (len(records), 512) or not torch.isfinite(features).all():
        raise DataContractError("Invalid cached features")
    return SplitFeatures(records, features, values, mask, fingerprint)
