"""Giữ approval scoped, raw bất biến và Range đúng byte; không gọi mạng thật."""

import hashlib
import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import yaml

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.v7_r8_execution import (
    accept,
    fresh,
    metadata,
    review_source,
    validate_pairs,
)


class Response(BytesIO):
    def __init__(self, body, status, headers):
        super().__init__(body)
        self.status = status
        self.headers = headers


class R8ExecutionTests(unittest.TestCase):
    def test_public_video_cannot_read_processed_or_assigned_holdout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = {"status": "received", "sha256": "video", "source_page": "publisher"}
            receipt_path = root / "receipt.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf8")
            frame = root / "data/interim/frame.png"
            frame.parent.mkdir(parents=True)
            frame.write_bytes(b"frame")
            row = {"source_original_split": "unassigned_public_video", "assigned_role": None,
                   "training_eligible": False, "video_receipt": {"path": "receipt.json",
                   "sha256": sha256_file(receipt_path)}, "video_sha256": "video",
                   "source_page": "publisher", "source_local_image_path": "data/interim/frame.png",
                   "source_image_sha256": sha256_file(frame)}
            self.assertEqual(review_source(row, root), frame)
            row["assigned_role"] = "holdout"
            with self.assertRaises(DataContractError):
                review_source(row, root)
            row["assigned_role"] = None
            row["source_local_image_path"] = "data/processed/holdout/frame.png"
            with self.assertRaises(DataContractError):
                review_source(row, root)

    def test_same_image_pair_requires_known_polarity_and_same_bytes(self) -> None:
        pair = {"pair_id": "pair1", "target": "looking_around", "positive_id": "a",
                "negative_id": "b", "match_strength": "same_image", "owner_approved": False}
        rows = {"a": {"states": ["U", "P"], "source_image_sha256": "same"},
                "b": {"states": ["U", "N"], "source_image_sha256": "same"}}
        validate_pairs([pair], rows)
        rows["b"]["source_image_sha256"] = "other"
        with self.assertRaises(DataContractError):
            validate_pairs([pair], rows)
        rows["b"]["source_image_sha256"] = "same"
        rows["b"]["states"] = ["U", "U"]
        with self.assertRaises(DataContractError):
            validate_pairs([pair], rows)

    def test_output_cannot_overwrite_or_escape_area(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "data/interim/existing").mkdir(parents=True)
            for relative in ["data/interim/existing", "data/raw/new", "../escape"]:
                with self.assertRaises(DataContractError):
                    fresh(root, relative, "data/interim")

    def test_approval_does_not_promote_unknown_or_assign_split(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            rows = root / "proposals.jsonl"
            rows.write_text(json.dumps({"sample_id": "sample", "training_eligible": False,
                "split": None, "final_proposed_states": ["U", "U"],
                "final_reason": "Thiếu evidence"}) + "\n", encoding="utf8")
            pointer = root / "pointer.json"
            pointer.write_text(json.dumps({"review_proposals": {"path": "proposals.jsonl",
                "sha256": hashlib.sha256(rows.read_bytes()).hexdigest()}}), encoding="utf8")
            config = root / "config.yaml"
            config.write_text(yaml.safe_dump({"approved_pointer": {"path": "pointer.json",
                "sha256": hashlib.sha256(pointer.read_bytes()).hexdigest()},
                "approval_output": "artifacts/reports/acceptance", "date": "2026-10-09",
                "owner_message_verbatim": "Approve toàn bộ"}), encoding="utf8")
            accept(config, root)
            result = json.loads((root / "artifacts/reports/acceptance/"
                                 "accepted-r5-review-decisions.jsonl").read_text(encoding="utf8"))
            self.assertEqual(result["approved_states"], ["U", "U"])
            self.assertEqual(result["membership"], "review_only")
            self.assertFalse(result["training_eligible"])
            self.assertIsNone(result["official_split"])

    def test_range_extension_checks_overlap_and_preserves_old_raw(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            prefix = root / "old.csv"
            prefix.write_bytes(b"abcd")
            approval = root / "approval.json"
            approval.write_text('{"r8_execution_authorized":true}', encoding="utf8")
            def pin(path):
                return {"path": path.name,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            config = root / "config.yaml"
            config.write_text(yaml.safe_dump({"approval": pin(approval), "base_prefix": pin(prefix),
                "url": "https://storage.googleapis.com/openimages/v6/oidv6-train-annotations-bbox.csv",
                "extra_bytes": 4, "chunk_bytes": 4, "publisher_total_bytes": 8,
                "output": "data/raw/new"}), encoding="utf8")
            responses = [Response(b"", 200, {"Content-Length": "8", "ETag": "same"}),
                         Response(b"abcd", 206, {"Content-Range": "bytes 0-3/8"}),
                         Response(b"efgh", 206, {"Content-Range": "bytes 4-7/8", "ETag": "same"})]
            with patch("urllib.request.urlopen", side_effect=responses):
                receipt = metadata(config, root)
            self.assertEqual(prefix.read_bytes(), b"abcd")
            self.assertEqual((root / "data/raw/new/bbox-train-prefix.csv").read_bytes(),
                             b"abcdefgh")
            self.assertEqual(receipt["coverage_bytes_fraction"], 1)
            self.assertFalse(receipt["full_inventory"])


if __name__ == "__main__":
    unittest.main()
