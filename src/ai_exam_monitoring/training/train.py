from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml, require, validate_training_config
from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.common.provenance import environment_metadata, write_json


def _as_serializable_metrics(result: Any) -> dict[str, float]:
    metrics = getattr(result, "results_dict", {}) or {}
    return {
        str(key): float(value)
        for key, value in metrics.items()
        if isinstance(value, (int, float)) or hasattr(value, "item")
    }


def train(config_path: str, experiment_id: str, owner: str) -> dict[str, Any]:
    if not experiment_id.strip() or owner.strip().upper() == "TBD":
        raise ConfigurationError("A real experiment ID and owner are required")
    config = load_yaml(config_path)
    validate_training_config(config)
    dataset_yaml = Path(str(require(config, "data.dataset_yaml")))
    if not dataset_yaml.is_file():
        raise ConfigurationError(
            f"Dataset config not found: {dataset_yaml}. Complete P1/P2 and run dvc pull first."
        )
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise ConfigurationError(
            "Install ML dependencies: pip install -r requirements/ml.txt"
        ) from exc

    artifact_root = Path(str(require(config, "artifacts.root")))
    model_dir = artifact_root / "models" / experiment_id
    metric_dir = artifact_root / "metrics" / experiment_id
    run_path = model_dir / "run.json"
    started_at = datetime.now(UTC).isoformat()
    run_record: dict[str, Any] = {
        "experiment_id": experiment_id,
        "owner": owner,
        "hypothesis": require(config, "experiment.hypothesis"),
        "status": "RUNNING",
        "started_at": started_at,
        "config_path": config_path,
        "resolved_config": config,
        "dataset_version": require(config, "data.dataset_version"),
        "split_version": require(config, "data.split_version"),
        "label_map_version": require(config, "data.label_map_version"),
        "environment": environment_metadata(),
    }
    write_json(run_path, run_record)

    logging = config.get("logging", {})
    if logging.get("enabled") and logging.get("backend") == "wandb":
        os.environ.setdefault("WANDB_PROJECT", str(logging.get("project", "ai-exam-monitoring")))
    else:
        os.environ["WANDB_MODE"] = "disabled"

    train_cfg = config["train"]
    device = train_cfg.get("device")
    if device == "auto":
        device = None
    model = YOLO(str(require(config, "model.checkpoint")))
    try:
        result = model.train(
            data=str(dataset_yaml),
            epochs=int(train_cfg["epochs"]),
            imgsz=int(train_cfg["imgsz"]),
            batch=int(train_cfg["batch"]),
            workers=int(train_cfg.get("workers", 2)),
            device=device,
            patience=int(train_cfg.get("patience", 20)),
            save_period=int(train_cfg.get("save_period", 5)),
            seed=int(require(config, "experiment.seed")),
            project=str(artifact_root / "models"),
            name=experiment_id,
            exist_ok=True,
        )
        metrics = _as_serializable_metrics(result)
        run_record.update(
            {
                "status": "FINISHED",
                "ended_at": datetime.now(UTC).isoformat(),
                "metrics": metrics,
                "model_directory": str(model_dir),
            }
        )
        write_json(metric_dir / "metrics.json", metrics)
        write_json(run_path, run_record)
        return run_record
    except Exception as exc:
        run_record.update(
            {
                "status": "FAILED",
                "ended_at": datetime.now(UTC).isoformat(),
                "failure_type": type(exc).__name__,
                "failure_message": str(exc),
            }
        )
        write_json(run_path, run_record)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one traceable Ultralytics baseline experiment"
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--owner", required=True)
    args = parser.parse_args()
    record = train(args.config, args.experiment_id, args.owner)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
