"""Guards cho gói review chưa duyệt và source nhiều người."""

import tempfile
import unittest
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.v7_unapproved_pilot import (
    PilotReviewItem,
    check_unapproved,
    fresh_output,
    safe_path,
    source_fields,
)


def item(kind: str = "source_review") -> PilotReviewItem:
    return PilotReviewItem("V7-NEW-001", kind, "source", "sha", "data/raw/source.jpg",
                           "Chọn đúng người trước nhãn", "classroom", None, None, {}, None,
                           "UNPROVEN")


class UnapprovedPilotTests(unittest.TestCase):
    def test_source_review_cannot_invent_anchor_labels(self):
        record = item()
        record.validate()
        record.proposed_states = ["N", "N"]
        with self.assertRaises(DataContractError):
            record.validate()

    def test_approval_filter_uses_exact_crop_and_id(self):
        record = item()
        with self.assertRaises(DataContractError):
            check_unapproved([record], {record.sample_id}, set())
        record.media = {"crop": {"path": "crop.png", "sha256": "approved"}}
        with self.assertRaises(DataContractError):
            check_unapproved([record], set(), {"approved"})
        check_unapproved([record], set(), {"different"})

    def test_duplicate_and_training_promotion_rejected(self):
        record = item()
        with self.assertRaises(DataContractError):
            check_unapproved([record, record], set(), set())
        record.canonical_mask = [1, 1]
        with self.assertRaises(DataContractError):
            record.validate()

    def test_no_processed_or_evaluation_media_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for path in ["data/processed/x.png", "data/raw/test/x.png", "../escape.png",
                         "data/raw/val2017/x.jpg", "outputs/holdout/x.png"]:
                with self.assertRaises(DataContractError):
                    safe_path(root, path, media=True)
            safe_path(root, "data/interim/source/x.jpg", media=True)

    def test_registry_adapters_keep_original_split_guard(self):
        for path_field, sha_field in [("source_image_path", "source_image_sha256"),
                                     ("source_local_image_path", "source_image_sha256"),
                                     ("frame_path", "frame_sha256")]:
            self.assertEqual(source_fields({path_field: "source", sha_field: "sha"}),
                             ("source", "sha"))
        with self.assertRaises(DataContractError):
            source_fields({"source_image_path": "source", "source_image_sha256": "sha",
                           "source_original_split": "valid"})

    def test_fresh_version_and_output_containment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "outputs/old").mkdir(parents=True)
            for relative in ["outputs/old", "data/raw/new", "../escape"]:
                with self.assertRaises(DataContractError):
                    fresh_output(root, relative)
            fresh_output(root, "outputs/new")


if __name__ == "__main__":
    unittest.main()
