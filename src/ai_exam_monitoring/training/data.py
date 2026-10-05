"""Verified manifest selection and deterministic full-context transforms."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import torch
from PIL import Image
from torchvision.transforms import functional as TF

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_owner_groups import verify_payload
from ai_exam_monitoring.data.pilot_schema import PilotRecord, read_records, record_to_dict

from .config import ExperimentConfig


def verify_dataset(root: Path, config: ExperimentConfig) -> list[PilotRecord]:
    if sha256_file(root / "checksums.sha256") != config.payload_sha256:
        raise DataContractError("Dataset payload pin changed")
    verify_payload(root)
    records = read_records(root / "manifest.jsonl")
    release = json.loads((root / "release.json").read_text(encoding="utf-8"))
    freeze = release["test_freeze"]
    if release["status"] != "accepted" or freeze["status"] != "frozen":
        raise DataContractError("Dataset release/test freeze not accepted")
    for row in records:
        if (row.dataset_version != config.dataset_version
                or row.split_version != config.split_version
                or row.target_encoding_version != config.encoding_version
                or row.use_scope != "local_classifier_research"
                or row.usage not in {"train", "val", "test"}):
            raise DataContractError("Manifest version/scope/usage differs from config")
    for filename, key in (("manifest.jsonl", "manifest_sha256"),
                          ("split-assignment.jsonl", "split_assignment_sha256")):
        if sha256_file(root / filename) != freeze[key]:
            raise DataContractError("Frozen manifest/split hash changed")
    test = sorted((r for r in records if r.usage == "test"), key=lambda r: r.sample_id)
    encoded = "".join(json.dumps(record_to_dict(r), sort_keys=True, ensure_ascii=False,
                                 allow_nan=False) + "\n" for r in test).encode()
    if (hashlib.sha256(encoded).hexdigest() != freeze["test_manifest_sha256"]
            or [r.sample_id for r in test] != freeze["test_sample_ids"]):
        raise DataContractError("Frozen test identity changed")
    return records


def select_records(records: list[PilotRecord], split: str, *, final_test: bool = False
                   ) -> list[PilotRecord]:
    if split not in {"train", "val"} and not (split == "test" and final_test):
        raise DataContractError("Test is reserved for explicit final evaluation")
    selected = sorted((r for r in records if r.usage == split), key=lambda r: r.sample_id)
    if not selected:
        raise DataContractError(f"Empty {split} split")
    return selected


def letterbox(image: Image.Image, config: ExperimentConfig) -> Image.Image:
    image = image.convert("RGB")
    scale = config.image_size / max(image.size)
    size = tuple(max(1, min(config.image_size, round(v * scale))) for v in image.size)
    resized = image.resize(size, Image.Resampling.BILINEAR)
    result = Image.new("RGB", (config.image_size, config.image_size), tuple(config.fill))
    result.paste(resized, ((config.image_size - size[0]) // 2,
                          (config.image_size - size[1]) // 2))
    return result


def image_tensor(path: Path, config: ExperimentConfig) -> torch.Tensor:
    with Image.open(path) as image:
        image = letterbox(image, config)
    return TF.normalize(TF.to_tensor(image), config.mean, config.std)


def labels(records: list[PilotRecord]) -> tuple[torch.Tensor, torch.Tensor]:
    # Finite placeholder only in memory; mask retains unknown semantics.
    values = torch.tensor([[0 if v is None else v for v in r.target_values] for r in records],
                          dtype=torch.float32)
    mask = torch.tensor([r.target_mask for r in records], dtype=torch.bool)
    return values, mask


def crop_path(root: Path, row: PilotRecord) -> Path:
    if row.crop is None:
        raise DataContractError("Missing reviewed crop")
    path = (root / row.crop.crop_relpath).resolve()
    if not path.is_relative_to(root.resolve()) or sha256_file(path) != row.crop.crop_sha256:
        raise DataContractError("Crop escaped root or changed bytes")
    return path
