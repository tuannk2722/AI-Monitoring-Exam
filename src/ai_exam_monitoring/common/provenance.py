from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "UNAVAILABLE"


def git_is_dirty() -> bool | None:
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, check=False
    )
    return bool(result.stdout.strip()) if result.returncode == 0 else None


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def environment_metadata() -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": git_commit(),
        "git_dirty": git_is_dirty(),
    }
    for package in ("torch", "ultralytics", "wandb"):
        try:
            module = __import__(package)
            metadata[package] = getattr(module, "__version__", "unknown")
        except ImportError:
            metadata[package] = None
    if metadata["torch"] is not None:
        import torch

        metadata["cuda_available"] = torch.cuda.is_available()
        metadata["cuda_version"] = torch.version.cuda
        metadata["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    return metadata


def write_json(path: str | Path, payload: dict[str, Any] | list[Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
