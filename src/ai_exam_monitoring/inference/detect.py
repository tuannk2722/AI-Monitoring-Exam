from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.common.provenance import sha256_file

from .detector import UltralyticsDetector, validate_fps


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run structured inference on image or recorded video"
    )
    parser.add_argument("--source", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--model-version", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--output", required=True, help="JSONL prediction output")
    parser.add_argument("--confidence", type=float, default=0.25)
    parser.add_argument(
        "--fps", type=float, required=True, help="Finite positive source FPS for video_time_ms"
    )
    args = parser.parse_args()
    try:
        validate_fps(args.fps)
    except ConfigurationError as exc:
        parser.error(str(exc))

    source = Path(args.source)
    checkpoint = Path(args.checkpoint)
    if not source.is_file() or not checkpoint.is_file():
        parser.error("source and checkpoint must exist")
    output = Path(args.output)
    if output.exists():
        parser.error("output must be a new file; existing inputs/artifacts are preserved")
    output.parent.mkdir(parents=True, exist_ok=True)
    detector = UltralyticsDetector(checkpoint, args.model_version, args.confidence)
    count = 0
    with output.open("x", encoding="utf-8") as handle:
        metadata = {
            "record_type": "metadata",
            "session_id": args.session_id,
            "source": str(source),
            "source_sha256": sha256_file(source),
            "checkpoint_sha256": sha256_file(checkpoint),
            "model_version": args.model_version,
            "fps": args.fps,
        }
        handle.write(json.dumps(metadata, ensure_ascii=False) + "\n")
        for prediction in detector.predict(source, args.session_id, args.fps):
            handle.write(json.dumps(prediction.to_dict(), ensure_ascii=False) + "\n")
            count += 1
    print(f"Predictions written: {count} -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
