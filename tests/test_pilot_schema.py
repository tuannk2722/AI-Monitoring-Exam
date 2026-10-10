from __future__ import annotations

import copy
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_schema import (
    TARGET_ORDER,
    ContextReview,
    CropRef,
    GroupReview,
    PilotRecord,
    PixelBox,
    ReviewEvidence,
    RightsReview,
    SourceRef,
    TargetReview,
    read_records,
    record_from_dict,
    record_to_dict,
    validate_records,
    write_records,
)


def evidence(crop_sha: str | None = None) -> ReviewEvidence:
    return ReviewEvidence("owner", "2026-10-04", "review-v1#decision", crop_sha)


def pending_record(sample_id: str = "SCB-001", image_sha: str = "b" * 64) -> PilotRecord:
    return PilotRecord(
        sample_id=sample_id,
        dataset_version="pilot-b-prep-v1",
        selection_version="pilot-b-selection-v1",
        crop_policy_version="pilot-b-reviewed-context-v1",
        source=SourceRef(
            "scb_head",
            "a" * 64,
            "images/train/img01.jpg",
            image_sha,
            100,
            80,
            label_relpath="labels/train/img01.txt",
            label_sha256="d" * 64,
            label_line_1based=1,
            source_class_id=1,
            original_split="train",
        ),
        phone_use=TargetReview("unknown", "Owner review pending"),
        looking_around=TargetReview("unknown", "Source class is not a reviewed target"),
        work_context_review=ContextReview("unknown", "Context has not been reviewed"),
        rights=RightsReview(None, None),
        ineligibility_reasons=("crop_review_pending", "group_evidence_pending"),
    )


def reviewed_record(sample_id: str = "RF-001", image_sha: str = "b" * 64) -> PilotRecord:
    record = pending_record(sample_id, image_sha)
    crop_review = evidence("c" * 64)
    crop = CropRef(
        "person-01",
        PixelBox(20, 10, 60, 70),
        PixelBox(10, 0, 80, 80),
        f"crops/{sample_id}.png",
        "c" * 64,
        crop_review,
    )
    return replace(
        record,
        crop=crop,
        phone_use=TargetReview("positive", "Phone interaction reviewed", crop_review),
        disposition="approved",
        owner_decision_ref="review-v1#person-and-crop",
    )


def usable_record(
    sample_id: str = "RF-001", *, split: str = "train", image_sha: str = "b" * 64
) -> PilotRecord:
    return replace(
        reviewed_record(sample_id, image_sha),
        rights=RightsReview("owner-permission", "source-card-v1", ("local_pilot",), evidence()),
        use_scope="local_pilot",
        group=GroupReview("group-01", ("group-review-v1#component-01",), evidence()),
        usage=split,
        split=split,
        split_version="pilot-b-split-v1",
        release_review=evidence(),
        test_freeze_ref="freeze-v1#test" if split == "test" else None,
        ineligibility_reasons=(),
    )


class PilotSchemaTests(unittest.TestCase):
    def test_pending_scb_is_unknown_and_has_no_crop_or_split(self) -> None:
        record = pending_record()
        self.assertIsNone(record.crop)
        self.assertIsNone(record.split)
        self.assertEqual(record.target_values, (None, None))
        self.assertEqual(record.target_mask, (0, 0))
        self.assertEqual(record.normal_review, "unknown")

    def test_partial_label_retains_null_and_masks_unknown(self) -> None:
        record = usable_record()
        self.assertEqual(TARGET_ORDER, ("phone_use", "looking_around"))
        self.assertEqual(record.target_values, (1, None))
        self.assertEqual(record.target_mask, (1, 0))
        self.assertEqual(record.normal_review, "not_normal")

    def test_cooccurrence_preserves_both_positives(self) -> None:
        record = reviewed_record()
        record = replace(
            record,
            looking_around=TargetReview("positive", "Gaze reviewed", evidence("c" * 64)),
        )
        self.assertEqual(record.target_values, (1, 1))
        self.assertEqual(record.target_mask, (1, 1))
        self.assertEqual(record.normal_review, "not_normal")

    def test_two_negatives_need_confirmed_work_context_for_normal(self) -> None:
        record = replace(
            reviewed_record(),
            phone_use=TargetReview("negative", "Absence reviewed", evidence("c" * 64)),
            looking_around=TargetReview("negative", "Absence reviewed", evidence("c" * 64)),
        )
        self.assertEqual(record.target_values, (0, 0))
        self.assertEqual(record.normal_review, "unknown")
        record = replace(
            record,
            work_context_review=ContextReview(
                "confirmed_working", "Working reviewed", evidence("c" * 64)
            ),
        )
        self.assertEqual(record.normal_review, "confirmed_normal")
        other = replace(
            record,
            work_context_review=ContextReview(
                "confirmed_other", "Other context reviewed", evidence("c" * 64)
            ),
        )
        self.assertEqual(other.normal_review, "not_normal")

    def test_known_target_requires_owner_evidence_and_crop_binding(self) -> None:
        for review in (None, evidence()):
            with self.subTest(review=review), self.assertRaises(DataContractError):
                TargetReview("negative", "Claimed absence", review)
        with self.assertRaises(DataContractError):
            replace(
                reviewed_record(),
                phone_use=TargetReview("positive", "Old crop evidence", evidence("d" * 64)),
            )
        with self.assertRaises(DataContractError):
            replace(
                pending_record(),
                phone_use=TargetReview("positive", "No crop", evidence("c" * 64)),
            )

    def test_unknown_requires_reason_and_invalid_state_is_rejected(self) -> None:
        with self.assertRaises(DataContractError):
            TargetReview("unknown", "")
        with self.assertRaises(DataContractError):
            TargetReview("unlabeled", "Invalid state")
        with self.assertRaises(DataContractError):
            ContextReview("confirmed_working", "No review")

    def test_pixel_boxes_are_integer_half_open_and_contained(self) -> None:
        self.assertEqual(PixelBox(0, 0, 10, 10).xyxy, (0, 0, 10, 10))
        for coords in ((0.1, 0, 10, 10), (True, 0, 10, 10), (-1, 0, 10, 10), (0, 0, 0, 1)):
            with self.subTest(coords=coords), self.assertRaises(DataContractError):
                PixelBox(*coords)
        with self.assertRaises(DataContractError):
            CropRef("p1", PixelBox(0, 0, 10, 10), PixelBox(1, 1, 10, 10), "c.png", "c" * 64)
        record = reviewed_record()
        assert record.crop is not None
        with self.assertRaises(DataContractError):
            replace(record, crop=replace(record.crop, context_box=PixelBox(0, 0, 101, 80)))

    def test_crop_approval_cannot_refer_to_other_bytes(self) -> None:
        record = reviewed_record()
        assert record.crop is not None
        with self.assertRaises(DataContractError):
            replace(record.crop, review=evidence("d" * 64))

    def test_source_paths_hashes_and_anchor_provenance_are_checked(self) -> None:
        source = pending_record().source
        for path in ("../image.jpg", "C:/image.jpg", "/image.jpg", "images\\image.jpg"):
            with self.subTest(path=path), self.assertRaises(DataContractError):
                replace(source, image_relpath=path)
        with self.assertRaises(DataContractError):
            replace(source, image_sha256="not-a-hash")
        with self.assertRaises(DataContractError):
            replace(source, label_line_1based=0)
        with self.assertRaises(DataContractError):
            replace(source, label_relpath=None)
        with self.assertRaises(DataContractError):
            replace(source, source_class_id=1, label_line_1based=None)

    def test_review_only_never_has_split_or_omits_blockers(self) -> None:
        for updates in ({"split": "train"}, {"split_version": "v1"}, {"ineligibility_reasons": ()}):
            with self.subTest(updates=updates), self.assertRaises(DataContractError):
                replace(pending_record(), **updates)

    def test_usage_requires_independent_rights_group_and_release_gates(self) -> None:
        record = usable_record()
        for updates in (
            {"rights": RightsReview(None, None)},
            {"use_scope": None},
            {"use_scope": "public_distribution"},
            {"group": None},
            {"release_review": None},
            {"split_version": None},
            {"split": "val"},
            {"ineligibility_reasons": ("pending",)},
            {"disposition": "pending"},
        ):
            with self.subTest(updates=updates), self.assertRaises(DataContractError):
                replace(record, **updates)

    def test_both_unknown_cannot_be_promoted_to_supervision(self) -> None:
        record = usable_record()
        with self.assertRaises(DataContractError):
            replace(record, phone_use=TargetReview("unknown", "Evidence unclear"))

    def test_group_cannot_be_assigned_without_evidence_and_owner_review(self) -> None:
        with self.assertRaises(DataContractError):
            GroupReview("group-01")
        with self.assertRaises(DataContractError):
            GroupReview("group-01", ("hash-only",))
        with self.assertRaises(DataContractError):
            RightsReview("license", "card", ("local_pilot",))

    def test_test_split_requires_freeze_evidence(self) -> None:
        record = usable_record(split="test")
        with self.assertRaises(DataContractError):
            replace(record, test_freeze_ref=None)

    def test_exclusion_is_separate_from_unknown_and_needs_decision(self) -> None:
        record = replace(
            pending_record(),
            disposition="excluded",
            usage="excluded",
            exclusion_reason="Anchor cannot identify one person",
            owner_decision_ref="review-v1#exclusion",
        )
        self.assertEqual(record.phone_use.state, "unknown")
        with self.assertRaises(DataContractError):
            replace(record, exclusion_reason=None)
        with self.assertRaises(DataContractError):
            replace(record, owner_decision_ref=None)
        with self.assertRaises(DataContractError):
            replace(record, usage="review_only")

    def test_versioned_codec_round_trips_pending_and_reviewed_records(self) -> None:
        for record in (pending_record(), reviewed_record(), usable_record(split="test")):
            with self.subTest(sample=record.sample_id, usage=record.usage):
                self.assertEqual(record_from_dict(record_to_dict(record)), record)

    def test_codec_rejects_unknown_to_negative_and_mask_or_normal_corruption(self) -> None:
        payload = record_to_dict(reviewed_record())
        for field, value in (
            ("target_values", [1, 0]),
            ("target_mask", [1, 1]),
            ("target_order", ["looking_around", "phone_use"]),
            ("normal_review", "confirmed_normal"),
            ("target_values", [True, None]),
            ("target_mask", [True, False]),
        ):
            corrupt = copy.deepcopy(payload)
            corrupt[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(DataContractError):
                record_from_dict(corrupt)

    def test_codec_rejects_missing_version_and_unknown_fields(self) -> None:
        payload = record_to_dict(pending_record())
        for field in ("schema_version", "target_encoding_version", "target_mask"):
            corrupt = copy.deepcopy(payload)
            corrupt.pop(field)
            with self.subTest(field=field), self.assertRaises(DataContractError):
                record_from_dict(corrupt)
        corrupt = copy.deepcopy(payload)
        corrupt["schema_version"] = "future-schema"
        with self.assertRaises(DataContractError):
            record_from_dict(corrupt)
        corrupt = copy.deepcopy(payload)
        corrupt["source"]["invented_session_id"] = "filename-session"
        with self.assertRaises(DataContractError):
            record_from_dict(corrupt)

    def test_duplicate_sample_and_source_identity_are_rejected(self) -> None:
        first = pending_record()
        with self.assertRaises(DataContractError):
            validate_records([first, first])
        with self.assertRaises(DataContractError):
            validate_records([first, replace(first, sample_id="SCB-002")])

    def test_package_and_split_versions_cannot_be_mixed(self) -> None:
        first = pending_record()
        second = pending_record("SCB-002", "e" * 64)
        for field in ("dataset_version", "selection_version", "crop_policy_version"):
            with self.subTest(field=field), self.assertRaises(DataContractError):
                validate_records([first, replace(second, **{field: "another-version"})])
        train = usable_record()
        other = usable_record("RF-002", image_sha="e" * 64)
        with self.assertRaises(DataContractError):
            validate_records([train, replace(other, split_version="another-split-version")])

    def test_group_image_and_crop_leakage_are_each_rejected(self) -> None:
        first = usable_record("RF-001")
        second = usable_record("RF-002", split="val", image_sha="e" * 64)
        assert second.crop is not None
        second = replace(
            second,
            crop=replace(second.crop, person_id="person-02"),
        )
        # Different images/candidates in the same reviewed group cannot cross splits.
        with self.assertRaises(DataContractError):
            validate_records([first, second])
        second = replace(
            second,
            group=GroupReview("group-02", ("group-review-v1#component-02",), evidence()),
        )
        # A shared crop SHA also blocks splitting, even with different group IDs.
        with self.assertRaises(DataContractError):
            validate_records([first, second])
        assert second.crop is not None
        second = replace(
            second,
            crop=replace(second.crop, crop_sha256="f" * 64, review=evidence("f" * 64)),
            phone_use=TargetReview("positive", "New crop reviewed", evidence("f" * 64)),
        )
        validate_records([first, second])
        second = replace(second, source=replace(second.source, image_sha256="b" * 64))
        with self.assertRaises(DataContractError):
            validate_records([first, second])

    def test_jsonl_payload_is_independent_of_input_order(self) -> None:
        records = [pending_record("SCB-002", "e" * 64), pending_record("SCB-001")]
        with tempfile.TemporaryDirectory() as temporary:
            left, right = Path(temporary) / "left.jsonl", Path(temporary) / "right.jsonl"
            write_records(left, records)
            write_records(right, list(reversed(records)))
            self.assertEqual(left.read_bytes(), right.read_bytes())
            self.assertEqual(read_records(left), sorted(records, key=lambda item: item.sample_id))
            left.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(DataContractError, "line 1"):
                read_records(left)


if __name__ == "__main__":
    unittest.main()
