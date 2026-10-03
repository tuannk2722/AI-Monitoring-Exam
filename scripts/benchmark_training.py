from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

import yaml

from ai_exam_monitoring.common.config import load_yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a 1-3 epoch training smoke benchmark")
    parser.add_argument("--config", default="configs/baseline.yaml")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--epochs", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args()
    config = load_yaml(args.config)
    config["train"]["epochs"] = args.epochs
    config["train"]["patience"] = args.epochs
    with tempfile.TemporaryDirectory() as directory:
        smoke_config = Path(directory) / "smoke.yaml"
        smoke_config.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        command = [
            "python",
            "-m",
            "ai_exam_monitoring.training.train",
            "--config",
            str(smoke_config),
            "--experiment-id",
            args.experiment_id,
            "--owner",
            args.owner,
        ]
        return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
