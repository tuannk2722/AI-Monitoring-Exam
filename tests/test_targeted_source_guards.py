"""Kiểm source audit hữu hạn, train-only và thất bại trước mutation/media."""

import csv
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import yaml
from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data import coco_targeted_candidates as coco
from ai_exam_monitoring.data import openimages_targeted_candidates as oi
from ai_exam_monitoring.data.pilot_targeted_expansion import (
    diverse_hints,
    validate_fingerprints,
)
from ai_exam_monitoring.data.targeted_review_package import ReviewProposal, _source, build


class Response:
    def __init__(self, payload, headers):
        self.stream = io.BytesIO(payload)
        self.headers = headers
        self.requested_bytes = None

    def read(self, size):
        self.requested_bytes = size
        return self.stream.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stream.close()


class AuditFixture:
    """Metadata/payload nhỏ tự tạo; không mở dữ liệu test thật."""

    def __init__(self, root, source):
        self.root = root
        self.source = source
        self.module = coco if source == "coco" else oi
        self.config = dict(status="draft_public_source_audit", training_eligible=False,
            selection_version="fixture", raw_output="data/raw/new-audit",
            output="data/interim/new-audit", max_image_bytes=1000000,
            quarantine_distance_hint=4, allowed_license_urls=["allowed"])
        scope = root / "scope.json"
        scope.write_text(json.dumps({"decision": "continue_public_training_source_audit"}))
        self.config["scope_approval"] = self.pin(scope)
        self.set_references([dict(sha256="f" * 64, dhash=(1 << 64) - 1, usages=["val", "test"])])
        buffer = io.BytesIO()
        Image.new("RGB", (24, 20), "red").save(buffer, format="JPEG")
        self.payload = buffer.getvalue()
        if source == "coco":
            self.config.update(phone_context_budget=0, negative_context_budget=1,
                work_keywords=["read"], horizontal_ratio_hint=1.3, minimum_context_score_hint=0,
                image_endpoint="https://s3.amazonaws.com/images.cocodataset.org/train2017")
            instances = dict(categories=[dict(id=1, name="person"), dict(id=2, name="book")],
                licenses=[dict(id=1, url="allowed")],
                images=[dict(id=1, license=1, file_name="000000000001.jpg", width=24, height=20)],
                annotations=[dict(id=1, category_id=1, iscrowd=0, image_id=1, bbox=[0, 0, 12, 20]),
                             dict(id=2, category_id=2, iscrowd=0, image_id=1, bbox=[0, 0, 8, 12])])
            metadata = root / "metadata.zip"
            with zipfile.ZipFile(metadata, "w") as archive:
                archive.writestr("annotations/instances_train2017.json", json.dumps(instances))
                archive.writestr("annotations/captions_train2017.json", json.dumps(
                    {"annotations": [dict(image_id=1, caption="reading")]}))
            self.config["metadata"] = self.pin(metadata)
        else:
            self.config.update(person_classes=["Person"], context_classes=["Book"],
                work_classes=["Book"], table_classes=[], phone_class="Mobile phone",
                allowed_rotations=["0"],
                screening_budgets={"work_without_phone_annotation_hint": 1},
                image_endpoint="https://open-images-dataset.s3.amazonaws.com/train")
            classes = root / "classes.csv"
            classes.write_text("person,Person\nbook,Book\n", encoding="utf8")
            self.config["classes"] = self.pin(classes)
            prefix = root / "prefix.csv"
            fields = ["ImageID", "LabelName", "XMin", "XMax", "YMin", "YMax", "IsInside",
                      "IsDepiction", "IsGroupOf"]
            with prefix.open("w", newline="", encoding="utf8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                for image_id, name in [("0000000000000001", "person"),
                                       ("0000000000000001", "book"),
                                       ("0000000000000002", "person")]:
                    writer.writerow(dict(ImageID=image_id, LabelName=name, XMin=0, XMax=1,
                        YMin=0, YMax=1, IsInside=0, IsDepiction=0, IsGroupOf=0))
            self.config["bbox_prefix"] = self.pin(prefix)
            metadata = root / "metadata.csv"
            metadata.write_text("ImageID,Subset,Rotation,License\n"
                                "0000000000000001,train,0,allowed\n", encoding="utf8")
            self.config["image_metadata"] = self.pin(metadata)
        self.config_path = root / "config.yaml"

    def pin(self, path):
        return dict(path=path.relative_to(self.root).as_posix(), sha256=sha256_file(path))

    def set_references(self, rows):
        path = self.root / "references.json"
        path.write_text(json.dumps(rows))
        self.config["parent_fingerprints"] = self.pin(path)

    def write_config(self):
        self.config_path.write_text(yaml.safe_dump(self.config), encoding="utf8")

    def build(self):
        self.write_config()
        return self.module.build(self.config_path, self.root)


class PublicAuditGuardTests(unittest.TestCase):
    def test_bad_limits_and_non_train_endpoint_fail_without_mutation(self):
        for source in ["coco", "oi"]:
            budget_key = "negative_context_budget" if source == "coco" else "screening_budgets"
            changes = [dict(max_image_bytes=value) for value in [-1, 0, True, 2.5]]
            changes += [dict(quarantine_distance_hint=value) for value in [-1, 65, True]]
            changes += [dict(image_endpoint="https://example.org/val")]
            changes += [{budget_key: -1 if source == "coco" else
                         {"work_without_phone_annotation_hint": -1}}]
            for change in changes:
                with self.subTest(source=source, change=change), tempfile.TemporaryDirectory() as d:
                    fixture = AuditFixture(Path(d).resolve(), source)
                    fixture.config.update(change)
                    with patch("urllib.request.urlopen") as request, \
                         patch("PIL.Image.open") as read:
                        with self.assertRaises(DataContractError):
                            fixture.build()
                        request.assert_not_called()
                        read.assert_not_called()
                    self.assertFalse((fixture.root / "data").exists())

    def test_missing_evaluation_cache_fails_before_download_or_media(self):
        for source in ["coco", "oi"]:
            with self.subTest(source=source), tempfile.TemporaryDirectory() as d:
                fixture = AuditFixture(Path(d).resolve(), source)
                fixture.set_references([dict(sha256="f" * 64, dhash=0, usages=["train"])])
                with patch("urllib.request.urlopen") as request, patch("PIL.Image.open") as read:
                    with self.assertRaisesRegex(DataContractError, "cached fingerprint evaluation"):
                        fixture.build()
                    request.assert_not_called()
                    read.assert_not_called()
                self.assertFalse((fixture.root / "data").exists())

    def test_overflow_bytes_md5_and_short_transfer_are_rejected_before_decode(self):
        for source in ["coco", "oi"]:
            for reason in ["bytes", "md5", "length"]:
                with self.subTest(source=source, reason=reason), tempfile.TemporaryDirectory() as d:
                    fixture = AuditFixture(Path(d).resolve(), source)
                    if reason == "bytes":
                        fixture.config["max_image_bytes"] = len(fixture.payload) - 1
                    headers = {"ETag": '"' + hashlib.md5(fixture.payload).hexdigest() + '"',
                               "Content-Length": str(len(fixture.payload))}
                    if reason == "md5":
                        headers["ETag"] = '"' + "0" * 32 + '"'
                    if reason == "length":
                        headers["Content-Length"] = str(len(fixture.payload) + 1)
                    response = Response(fixture.payload, headers)
                    with patch("urllib.request.urlopen", return_value=response), \
                         patch("PIL.Image.open") as read:
                        result = fixture.build()
                        read.assert_not_called()
                    self.assertEqual(result["screening_records"], 0)
                    self.assertEqual(len(result["failures"]), 1)
                    self.assertEqual(response.requested_bytes,
                                     fixture.config["max_image_bytes"] + 1)
                    self.assertEqual(list((fixture.root / "data/raw/new-audit").glob("*.jpg")), [])

    def test_valid_payload_keeps_unknown_and_existing_version_immutable(self):
        for source in ["coco", "oi"]:
            with self.subTest(source=source), tempfile.TemporaryDirectory() as d:
                fixture = AuditFixture(Path(d).resolve(), source)
                response = Response(fixture.payload,
                    {"ETag": hashlib.md5(fixture.payload).hexdigest(),
                     "Content-Length": str(len(fixture.payload))})
                with patch("urllib.request.urlopen", return_value=response):
                    result = fixture.build()
                self.assertEqual(result["screening_records"], 1)
                self.assertEqual(result["failures"], [])
                screening = fixture.root / "data/interim/new-audit/screening.jsonl"
                row = json.loads(screening.read_text(encoding="utf8"))
                self.assertEqual(row["canonical_targets"], [None, None])
                self.assertEqual(row["canonical_mask"], [0, 0])
                self.assertIsNone(row["split"])
                self.assertFalse(row["training_eligible"])
                self.assertIsNone(row["phone_annotation_hint"])
                with patch("urllib.request.urlopen") as request:
                    with self.assertRaises(DataContractError):
                        fixture.build()
                    request.assert_not_called()

    def test_exact_parent_bytes_quarantined_without_image_decode(self):
        for source in ["coco", "oi"]:
            with self.subTest(source=source), tempfile.TemporaryDirectory() as d:
                fixture = AuditFixture(Path(d).resolve(), source)
                digest = hashlib.sha256(fixture.payload).hexdigest()
                fixture.set_references([dict(sha256=digest, dhash=0, usages=["test"])])
                response = Response(fixture.payload,
                    {"ETag": hashlib.md5(fixture.payload).hexdigest(),
                     "Content-Length": str(len(fixture.payload))})
                with patch("urllib.request.urlopen", return_value=response), \
                     patch("PIL.Image.open") as decode:
                    result = fixture.build()
                    decode.assert_not_called()
                self.assertEqual(result["screening_records"], 0)
                self.assertEqual(result["failures"], [])
                self.assertEqual(len(result["quarantine"]), 1)
                self.assertEqual(result["quarantine"][0]["reason"],
                                 "exact_parent_sha_before_decode")
                self.assertFalse(result["quarantine"][0]["media_decoded"])

    def test_coco_followup_excludes_before_quota(self):
        instances = dict(categories=[dict(id=1, name="person"), dict(id=2, name="book")],
            licenses=[dict(id=1, url="allowed")],
            images=[dict(id=i, license=1) for i in range(1, 4)],
            annotations=[dict(id=i * 2 + cat, category_id=cat, iscrowd=0, image_id=i)
                         for i in range(1, 4) for cat in [1, 2]])
        config = dict(allowed_license_urls=["allowed"], selection_version="fixed",
                      work_keywords=["read"], phone_context_budget=0, negative_context_budget=1)
        captions = {i: "reading" for i in range(1, 4)}
        first, _ = coco.shortlist(instances, captions, config)
        second, _ = coco.shortlist(instances, captions, config, {first[0]["image"]["id"]})
        self.assertEqual(len(second), 1)
        self.assertNotEqual(first[0]["image"]["id"], second[0]["image"]["id"])

    def test_openimages_title_phone_without_person_keeps_full_image_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            fixture = AuditFixture(Path(d).resolve(), "oi")
            fixture.config.update(phone_title_keywords=["office"], work_rank_weight=1,
                table_rank_weight=1, screening_budgets={"title_phone_context_hint": 1})
            classes = fixture.root / "classes.csv"
            classes.write_text("phone,Mobile phone\n", encoding="utf8")
            fixture.config["classes"] = fixture.pin(classes)
            prefix = fixture.root / "prefix.csv"
            prefix.write_text("ImageID,LabelName,XMin,XMax,YMin,YMax,IsInside,IsDepiction,"
                              "IsGroupOf,IsOccluded,IsTruncated\n"
                              "0000000000000001,phone,0.5,0.7,0.5,0.7,0,0,0,0,0\n"
                              "0000000000000002,phone,0.5,0.7,0.5,0.7,0,0,0,0,0\n",
                              encoding="utf8")
            fixture.config["bbox_prefix"] = fixture.pin(prefix)
            metadata = fixture.root / "metadata.csv"
            metadata.write_text("ImageID,Subset,Rotation,License,Title\n"
                                "0000000000000001,train,0,allowed,Office desk\n", encoding="utf8")
            fixture.config["image_metadata"] = fixture.pin(metadata)
            response = Response(fixture.payload,
                {"ETag": hashlib.md5(fixture.payload).hexdigest()})
            with patch("urllib.request.urlopen", return_value=response):
                result = fixture.build()
            self.assertEqual(result["screening_records"], 1)
            row = json.loads((fixture.root / "data/interim/new-audit/screening.jsonl")
                             .read_text(encoding="utf8"))
            self.assertIsNone(row["person_annotation_hint"])
            self.assertEqual(row["draft_xyxy"], [0, 0, 24, 20])
            self.assertEqual(row["canonical_mask"], [0, 0])
            self.assertEqual(row["canonical_targets"], [None, None])

    def test_cached_hash_and_negative_slice_rejected(self):
        for budget in [-1, 1.5, True]:
            with self.assertRaises(DataContractError):
                diverse_hints([], budget, set())
        for dhash in [-1, 1 << 64, True]:
            with self.assertRaises(DataContractError):
                validate_fingerprints([dict(dhash=dhash, sha256="f" * 64, usages=["test"])])
        for box in [[1e308, 0, 1e308, 1], [0, 1e308, 1, 1e308]]:
            with self.assertRaises(DataContractError):
                coco.bbox({"bbox": box}, 24, 20)


class TargetedPreflightGuardTests(unittest.TestCase):
    def test_original_split_and_local_evaluation_path_rejected_before_hash_read(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            row = dict(source_image_relpath="images/train/source.jpg",
                       source_local_image_path="data/raw/source.jpg",
                       source_image_sha256="unread")
            changes = [dict(source_original_split="test"),
                       dict(source_image_relpath="images/train/../test/source.jpg"),
                       dict(source_image_relpath="images/train\\source.jpg"),
                       dict(source_local_image_path="data/raw/images/test/source.jpg"),
                       dict(source_original_split="train2017",
                            source_image_path="data/raw/val2017/source.jpg")]
            for change in changes:
                with self.subTest(change=change), \
                     patch("ai_exam_monitoring.data.targeted_review_package.verify_pin") as read:
                    with self.assertRaises(DataContractError):
                        _source({**row, **change}, root)
                    read.assert_not_called()

    def test_missing_or_exceeded_bucket_stops_before_source_read(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            scope, parent, selection, config_path = (
                root / p for p in ["scope.json", "parent.sha", "selection.json", "config.yaml"])
            scope.write_text(json.dumps({"decision": "approve_v7_targeted_preparation_only"}))
            parent.write_text("unchanged parent")
            # D context không cần pair; source không tồn tại để chứng minh preflight quota trước.
            selection.write_text(json.dumps({"proposals": [dict(candidate_id="V7-D-001",
                screening_set="not-read", screening_id="not-read", bucket="D", role="context",
                states=["P", "U"], xyxy=[0, 0, 10, 10], visual_family_hint="scene",
                observation="Phone trong cảnh đông người.", phenotypes=["crowded"],
                person_unit_hint="left")], "pairs": []}), encoding="utf8")
            def pin(path):
                return dict(path=path.relative_to(root).as_posix(), sha256=sha256_file(path))
            for budgets in [{}, {"D": 0}, {"D": -1}, {"D": True}]:
                config = dict(status="draft_targeted_review_package", training_eligible=False,
                    scope_approval=pin(scope), parent_checksums=pin(parent),
                    selection=pin(selection), output="data/interim/review", screenings=[],
                    budgets=budgets, require_person_units=True)
                config_path.write_text(yaml.safe_dump(config), encoding="utf8")
                with self.subTest(budgets=budgets), \
                     patch("ai_exam_monitoring.data.targeted_review_package._source") as read:
                    with self.assertRaises(DataContractError):
                        build(config_path, root)
                    read.assert_not_called()
                self.assertFalse((root / "data").exists())

    def test_direct_list_unknown_states_cannot_bypass_targeted_selection(self):
        with self.assertRaises(DataContractError):
            ReviewProposal(candidate_id="V7-D-001", screening_set="fixture", screening_id="one",
                bucket="D", role="context", states=["U", "U"], xyxy=(0, 0, 10, 10),
                visual_family_hint="scene", observation="Không đủ bằng chứng.",
                phenotypes=("crowded",))


if __name__ == "__main__":
    unittest.main()
