"""Kiểm nghiệm thu giữ đúng parent và chỉ nhập quyết định owner đã duyệt."""

import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_review_acceptance import materialize_records
from ai_exam_monitoring.data.pilot_schema import (
    ContextReview,
    CropRef,
    GroupReview,
    PilotRecord,
    PixelBox,
    ReviewEvidence,
    RightsReview,
    SourceRef,
    TargetReview,
)


class AcceptanceTests(unittest.TestCase):
    def fixture(self, usage="train"):
        e = ReviewEvidence("owner", "2026-10-07", "approval.json", "a" * 64)
        used = usage in {"train", "val", "test"}
        r = PilotRecord(
            sample_id="A",
            dataset_version="old",
            selection_version="old",
            crop_policy_version="old",
            source=SourceRef("source", "b" * 64, "a.jpg", "c" * 64, 20, 20),
            phone_use=TargetReview(
                "positive" if used else "unknown", "Quan sát.", e if used else None
            ),
            looking_around=TargetReview("unknown", "Chưa rõ."),
            work_context_review=ContextReview("unknown", "Chưa rõ."),
            rights=RightsReview(
                "owner-permission", "rights.json", ("local_classifier_research",), e
            ),
            crop=CropRef(
                "A", PixelBox(0, 0, 20, 20), PixelBox(0, 0, 20, 20), "crops/A.png", "a" * 64, e
            ),
            group=GroupReview("G", ("group.json",), e),
            disposition="approved",
            usage=usage,
            split=usage if used else None,
            split_version="old" if used else None,
            owner_decision_ref="old.json",
            release_review=e,
            use_scope="local_classifier_research",
            test_freeze_ref="old-test" if usage == "test" else None,
            ineligibility_reasons=() if used else ("Nhãn chưa rõ.",),
        )
        a = dict(
            sample_id="A",
            source_image_sha256="c" * 64,
            crop_sha256="a" * 64,
            proposed_usage=usage,
            proposed_group_id="G",
            phone_use=r.phone_use.state,
            looking_around="unknown",
            work_context_review="unknown",
            observation="Đã nghiệm thu.",
        )
        c = dict(
            approval=dict(path="new.json"),
            dataset_version="new",
            selection_version="new",
            crop_policy_version="new",
            split_version="new",
            assignment=dict(path="assignment.jsonl"),
            approved_use_scope=["local_classifier_research"],
        )
        approval = dict(
            decision="approve_pilot_b_v6_release",
            reviewer="owner",
            reviewed_at="2026-10-07",
            approved_counts={usage: 1},
        )
        return r, a, c, approval

    def test_used_evidence_geometry_and_test_freeze_are_preserved(self):
        for use in ["train", "val", "test"]:
            old, a, c, p = self.fixture(use)
            new = materialize_records([old], [a], c, p)[0]
            for k in [
                "source",
                "crop",
                "phone_use",
                "looking_around",
                "work_context_review",
                "rights",
                "group",
                "test_freeze_ref",
                "usage",
            ]:
                self.assertEqual(getattr(new, k), getattr(old, k))
            self.assertEqual(new.dataset_version, "new")
            self.assertEqual(new.split_version, "new")

    def test_reject_changed_used_label_group_or_split(self):
        for key, value in [
            ("phone_use", "negative"),
            ("proposed_group_id", "G2"),
            ("proposed_usage", "val"),
        ]:
            old, a, c, p = self.fixture()
            a[key] = value
            with self.assertRaises(DataContractError):
                materialize_records([old], [a], c, p)

    def test_unknown_pending_can_become_approved_training_label(self):
        old, a, c, p = self.fixture("review_only")
        a.update(proposed_usage="train", phone_use="negative")
        p["approved_counts"] = {"train": 1}
        new = materialize_records([old], [a], c, p)[0]
        self.assertEqual(new.target_mask, (1, 0))
        self.assertEqual(new.phone_use.review.crop_sha256, old.crop.crop_sha256)
        self.assertEqual(old.phone_use.state, "unknown")

    def test_reject_different_crop_or_source(self):
        for key in ["crop_sha256", "source_image_sha256"]:
            old, a, c, p = self.fixture()
            a[key] = "f" * 64
            with self.assertRaises(DataContractError):
                materialize_records([old], [a], c, p)

    def test_missing_duplicate_parent_and_wrong_counts_rejected(self):
        old, a, c, p = self.fixture()
        for assignments in [[], [a, a]]:
            with self.assertRaises(DataContractError):
                materialize_records([old], assignments, c, p)
        p["approved_counts"] = {"train": 2}
        with self.assertRaises(DataContractError):
            materialize_records([old], [a], c, p)

    def test_source_approval_is_not_release_approval(self):
        old, a, c, p = self.fixture()
        p["decision"] = "source_rights_only"
        with self.assertRaises(DataContractError):
            materialize_records([old], [a], c, p)


if __name__ == "__main__":
    unittest.main()
