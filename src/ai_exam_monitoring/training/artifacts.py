"""Atomic local artifacts and provenance; never uploads media."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import torch

from ai_exam_monitoring.common.provenance import git_commit, git_is_dirty, sha256_file


def now() -> str:
    return datetime.now(UTC).isoformat()


def digest_json(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")
    os.replace(temp, path)


def save_checkpoint(path: Path, payload: dict) -> None:
    temp = path.with_suffix(".tmp")
    torch.save(payload, temp)
    os.replace(temp, path)


def code_identity() -> dict:
    package = Path(__file__).resolve().parents[1]
    # Git normalizes line endings; identity must survive Windows/Linux checkout.
    files = {p.relative_to(package).as_posix(): hashlib.sha256(
                 p.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
             for p in sorted(package.rglob("*.py"))}
    return {"sha256": digest_json(files), "files": files, "normalization": "UTF-8 LF"}


def environment() -> dict:
    packages = {name: version(name) for name in ("torch", "torchvision", "numpy", "Pillow",
                                                "PyYAML")}
    return {"python": sys.version, "platform": platform.platform(), "packages": packages,
            "device": "cpu", "cuda_available": torch.cuda.is_available(),
            "threads": torch.get_num_threads(), "git_commit": git_commit(),
            "git_dirty": git_is_dirty(), "command": sys.argv,
            "pip_freeze": subprocess.run([sys.executable, "-m", "pip", "freeze"],
                                         capture_output=True, text=True, check=True).stdout}


@dataclass
class RunRecord:
    experiment_id: str
    owner: str
    hypothesis: str
    config_sha256: str
    code_sha256: str
    environment: dict
    dataset_version: str
    split_version: str
    encoding_version: str
    payload_sha256: str
    weights_sha256: str
    status: str = "RUNNING"
    started_at: str = field(default_factory=now)
    ended_at: str | None = None
    best_epoch: int | None = None
    completed_epochs: int = 0
    elapsed_seconds: float = 0.0
    peak_rss_bytes: int | None = None
    observation: str = "Pending"
    decision: str = "pending"
    error: str | None = None
    resumed_at: list[str] = field(default_factory=list)

    def write(self, output: Path) -> None:
        write_json(output / "run.json", asdict(self))


def checksum_artifacts(output: Path) -> None:
    files = {p.relative_to(output).as_posix(): sha256_file(p)
             for p in sorted(output.rglob("*")) if p.is_file()
             and p.name != "checksums.json" and not p.name.endswith(".tmp")}
    write_json(output / "checksums.json", files)
