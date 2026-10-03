from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml, require, validate_training_config
from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.common.provenance import sha256_file, write_json


def evaluate(config_path: str, experiment_id: str, use_test: bool = False) -> dict[str, Any]:
    config = load_yaml(config_path)
    validate_training_config(config)
    artifact_root = Path(str(require(config, "artifacts.root")))
    checkpoint = artifact_root / "models" / experiment_id / "weights" / "best.pt"
    if not checkpoint.is_file():
        raise ConfigurationError(f"Promotable checkpoint not found: {checkpoint}")
    if use_test:
        confirmation = config.get("evaluation", {}).get("allow_test_set", False)
        if not confirmation:
            raise ConfigurationError(
                "Test-set evaluation is locked. Set evaluation.allow_test_set=true "
                "in a reviewed final config."
            )
    split = "test" if use_test else str(config.get("validation", {}).get("split", "val"))
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise ConfigurationError(
            "Install ML dependencies: pip install -r requirements/ml.txt"
        ) from exc

    model = YOLO(str(checkpoint))
    result = model.val(
        data=str(require(config, "data.dataset_yaml")),
        split=split,
        imgsz=int(require(config, "train.imgsz")),
        batch=int(require(config, "train.batch")),
        conf=float(config.get("validation", {}).get("confidence_threshold", 0.25)),
        iou=float(config.get("validation", {}).get("iou_threshold", 0.70)),
        project=str(artifact_root / "plots"),
        name=experiment_id,
        exist_ok=True,
        plots=True,
    )
    raw_metrics = getattr(result, "results_dict", {}) or {}
    metrics = {
        str(key): float(value)
        for key, value in raw_metrics.items()
        if isinstance(value, (int, float)) or hasattr(value, "item")
    }
    report = {
        "experiment_id": experiment_id,
        "evaluated_at": datetime.now(UTC).isoformat(),
        "split": split,
        "dataset_version": require(config, "data.dataset_version"),
        "split_version": require(config, "data.split_version"),
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": sha256_file(checkpoint),
        "metrics": metrics,
    }
    write_json(artifact_root / "metrics" / experiment_id / "evaluation.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a traceable model checkpoint")
    parser.add_argument("--config", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--test", action="store_true", help="Locked final test-set evaluation")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.config, args.experiment_id, args.test), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
