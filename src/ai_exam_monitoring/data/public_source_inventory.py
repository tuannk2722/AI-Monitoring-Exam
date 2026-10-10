"""Snapshot metadata nguồn public hữu hạn, không tiếp nhận media/quyền train."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.provenance import sha256_file, write_json
from ai_exam_monitoring.data.v7_public_photo_gapfill import request
from ai_exam_monitoring.data.v7_r8_execution import fresh


def snapshot(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    cfg = load_yaml(config_path)
    raw = fresh(root, cfg["raw_output"], "data/raw")
    output = fresh(root, cfg["report_output"], "artifacts/reports")
    raw.mkdir(parents=True)
    output.mkdir(parents=True)
    receipts: list[dict[str, Any]] = []
    for index, source in enumerate(cfg["sources"], 1):
        receipt: dict[str, Any] = {"source_id": source["source_id"], "url": source["url"],
                                  "media_downloaded": False, "training_eligible": False}
        try:
            payload, http = request(source["url"], cfg["max_response_bytes"])
            path = raw / f"metadata-{index:03d}.response"
            path.write_bytes(payload)
            receipt.update(status="metadata_received", http=http,
                           response={"path": path.relative_to(root).as_posix(),
                                     "sha256": sha256_file(path)})
            if source.get("format") == "zenodo_json":
                data = json.loads(payload)
                metadata = data.get("metadata", {})
                receipt.update(title=metadata.get("title"), license=metadata.get("license"),
                    rights=metadata.get("rights"), access_right=metadata.get("access_right"),
                    files=[{"key": f.get("key"), "size": f.get("size"),
                            "checksum": f.get("checksum"), "links": f.get("links")}
                           for f in data.get("files", [])])
        except Exception as error:
            receipt.update(status="metadata_failed_preserved", reason=str(error))
        receipts.append(receipt)
        write_json(output / "source-receipts.json", receipts)
        print(f"Metadata {index}: {receipt['source_id']} {receipt['status']}", flush=True)
    summary = {"status": "metadata_only_not_source_acceptance", "requests": len(receipts),
               "received": sum(r["status"] == "metadata_received" for r in receipts),
               "media_downloaded": 0, "source_exhausted": False, "training_eligible": False,
               "config_sha256": sha256_file(config_path)}
    write_json(output / "summary.json", summary)
    write_json(raw / "receipt.json", {**summary, "sources": receipts})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(snapshot(args.config, Path.cwd()), ensure_ascii=False))


if __name__ == "__main__":
    main()
