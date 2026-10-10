"""Tiếp nhận video public có metadata/license và trích storyboard local hữu hạn."""

from __future__ import annotations

import argparse
import json
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .v7_r8_execution import fresh, pinned


def audit(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    config = load_yaml(config_path)
    metadata = json.loads(pinned(root, config["metadata"]).read_text(encoding="utf8"))
    page = next(iter(metadata["query"]["pages"].values()))
    video = page["videoinfo"][0]
    if video["extmetadata"]["LicenseShortName"]["value"] != config["license"]:
        raise DataContractError("Publisher license khác config")
    derivative = next(d for d in video["derivatives"]
                      if d.get("transcodekey") == config["transcodekey"])
    raw = fresh(root, config["raw_output"], "data/raw")
    output = fresh(root, config["output"], "data/interim")
    codec = pinned(root, config["codec"])
    timestamps = config["timestamps_seconds"]
    if (not timestamps or len(timestamps) > config["frame_cap"]
            or len(set(timestamps)) != len(timestamps)
            or any(t < 0 or t >= video["duration"] for t in timestamps)):
        raise DataContractError("Timestamp/cap không hợp lệ")
    raw.mkdir(parents=True)
    receipt: dict[str, Any] = {
        "status": "pending", "source_page": video["descriptionurl"],
        "url": derivative["src"], "license": config["license"],
        "attribution": video["extmetadata"]["Attribution"]["value"],
        "license_url": video["extmetadata"]["LicenseUrl"]["value"],
        "metadata_sha256": config["metadata"]["sha256"],
        "original_sha1": video["sha1"], "original_bytes": video["size"],
        "download_is_derivative_not_original": True,
        "rights_release_approved": False, "training_eligible": False,
        "config_sha256": sha256_file(config_path),
    }
    target = raw / "publisher-480p.webm"
    try:
        req = urllib.request.Request(derivative["src"], headers={
            "User-Agent": "ClassroomDatasetResearch/1.0 (local research audit)"})
        with urllib.request.urlopen(req, timeout=90) as response, target.open("xb") as stream:
            expected = int(response.headers.get("Content-Length", "0"))
            if response.status != 200 or not 0 < expected <= config["max_bytes"]:
                raise DataContractError("Video length/status ngoài budget")
            received = 0
            while block := response.read(4 * 1024 * 1024):
                received += len(block)
                if received > config["max_bytes"]:
                    raise DataContractError("Video vượt byte cap")
                stream.write(block)
            if received != expected:
                raise DataContractError("Video thiếu bytes")
            receipt.update(bytes=received, etag=response.headers.get("ETag"),
                           sha256=sha256_file(target), status="received")
    except Exception as error:
        receipt.update(status="FAILED_preserved_attempt", reason=str(error))
        write_json(raw / "receipt.json", receipt)
        raise
    write_json(raw / "receipt.json", receipt)
    output.mkdir(parents=True)
    (output / "frames").mkdir()
    rows = []
    for index, timestamp in enumerate(timestamps, 1):
        frame = output / "frames" / f"PUBLIC-VIDEO-{index:03d}.png"
        subprocess.run([str(codec), "-hide_banner", "-loglevel", "error", "-nostdin",
                        "-ss", str(timestamp), "-i", str(target), "-frames:v", "1",
                        "-threads", "1", str(frame)], check=True, timeout=60,
                       capture_output=True)
        with Image.open(frame) as image:
            width, height = image.size
        rows.append({"sample_id": f"PUBLIC-VIDEO-{index:03d}",
                     "timestamp_seconds": timestamp, "width": width, "height": height,
                     "frame_path": frame.relative_to(root).as_posix(),
                     "frame_sha256": sha256_file(frame),
                     "video_sha256": receipt["sha256"], "camera_session": None,
                     "group_proposal": config["conservative_family"],
                     "independence_proven": False, "training_eligible": False})
        if index % 10 == 0:
            print(f"Storyboard {index}/{len(timestamps)}", flush=True)
    for start in range(0, len(rows), 12):
        sheet = Image.new("RGB", (1800, 1280), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, row in enumerate(rows[start:start+12]):
            x, y = (offset % 3)*600, (offset // 3)*320
            draw.text((x+5, y+5), f"{row['sample_id']} t={row['timestamp_seconds']}s",
                      fill="black")
            with Image.open(root / row["frame_path"]) as decoded_frame:
                sheet.paste(ImageOps.contain(decoded_frame, (590, 280)), (x+5, y+30))
        sheet.save(output / f"sheet-{start//12+1:03d}.jpg", quality=94)
    (output / "screening.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n"
        for r in rows), encoding="utf8")
    summary = {**receipt, "status": "storyboard_pending_visual_QA", "frames": len(rows),
               "codec_sha256": config["codec"]["sha256"],
               "transform": "publisher transcode; frame extraction, no model",
               "test_media_read": False, "model_executed": False}
    write_json(output / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(audit(args.config, args.workspace), ensure_ascii=False))


if __name__ == "__main__":
    main()
