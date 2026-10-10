"""Regression cho payload/pins/test freeze dùng chung sau khi nghỉ launcher."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from test_pilot_schema import usable_record

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.integrity import (
    pin,
    read_rows,
    safe_path,
    source_file,
    test_freeze_attestation,
    verify_payload,
)
from ai_exam_monitoring.data.pilot_schema import record_to_dict


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.file = self.root / "data/raw/a.jsonl"
        self.file.parent.mkdir(parents=True)
        self.file.write_text('{"id": 1}\n\n', encoding="utf-8")

    def test_pin_rows_and_source_path(self):
        value = {"path": "data/raw/a.jsonl", "sha256": sha256_file(self.file)}
        self.assertEqual(pin(self.root, value, media=True), self.file)
        self.assertEqual(read_rows(self.file), [{"id": 1}])
        self.assertEqual(source_file(self.root, value["path"]), self.file)
        self.file.write_text("changed", encoding="utf-8")
        with self.assertRaises(DataContractError):
            pin(self.root, value)

    def test_escape_and_evaluation_media_rejected(self):
        for relative in ["../outside", "data/raw/../test/a", "data/processed/a.png",
                         "outputs/val/a.png", "data/raw/val2017/a.png"]:
            with self.subTest(relative=relative), self.assertRaises(DataContractError):
                safe_path(self.root, relative, media=True)
        for relative in ["../outside", "C:/outside", "data\\raw\\a.jsonl", "missing"]:
            with self.subTest(relative=relative), self.assertRaises(DataContractError):
                source_file(self.root, relative)

    def test_payload_rejects_tamper_extra_and_duplicate_inventory(self):
        package = self.file.parent
        checksum = package / "checksums.sha256"
        line = f"{sha256_file(self.file)}  a.jsonl\n"
        checksum.write_text(line, encoding="utf-8")
        verify_payload(package)
        checksum.write_text(line * 2, encoding="utf-8")
        with self.assertRaises(DataContractError):
            verify_payload(package)
        checksum.write_text(line, encoding="utf-8")
        extra = package / "extra"
        extra.write_bytes(b"extra")
        with self.assertRaises(DataContractError):
            verify_payload(package)
        extra.unlink()
        self.file.write_bytes(b"changed")
        with self.assertRaises(DataContractError):
            verify_payload(package)

    def test_freeze_serialization_order_and_test_identity(self):
        train, test = usable_record("B"), usable_record("A", split="test")
        result = test_freeze_attestation([train, test], config_sha256="c" * 64,
            approval_sha256="d" * 64, owner_decision_ref="approval", commit="commit",
            approval={"recorded_at": "2026-10-10", "reviewer": "owner"}, protocol="locked")
        expected = json.dumps(record_to_dict(test), ensure_ascii=False, sort_keys=True,
                              allow_nan=False) + "\n"
        self.assertEqual(result["test_manifest_sha256"],
                         hashlib.sha256(expected.encode()).hexdigest())
        self.assertEqual(result["test_sample_ids"], ["A"])
        self.assertEqual(result["owner_decision_sha256"], "d" * 64)
        self.assertEqual(result["status"], "frozen")
