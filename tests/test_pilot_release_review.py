"""Kiểm chống rò rỉ và bảo toàn membership của gói review."""

import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_release_review import assemble_rows, propose_groups


def row(i, split, group=None, sha=None):
    return {
        "sample_id": i,
        "proposed_usage": split,
        "parent_group": group,
        "source_image_sha256": sha or i,
    }


def edge(*ids):
    return {"sample_ids": list(ids), "observation_vi": "Quan hệ cảnh được khai báo để review."}


class ReleaseReviewTests(unittest.TestCase):
    def parent_fixture(self, usage="review_only", phone="unknown"):
        parent = {
            "sample_id": "a",
            "usage": usage,
            "group": {"leakage_group_id": "old"},
            "source": {"source_id": "source", "image_sha256": "source-sha"},
            "crop": {
                "crop_relpath": "crops/a.png",
                "crop_sha256": "crop-sha",
                "context_box": {"xmin": 0, "ymin": 0, "xmax": 20, "ymax": 30},
            },
            "phone_use": {"state": phone},
            "looking_around": {"state": "unknown"},
            "work_context_review": {"state": "unknown"},
        }
        decisions = {
            "parent_package": "parent",
            "relations": [],
            "choices": [{"sample_id": "a", "proposed_usage": "train", "reason": "Đã xem."}],
            "target_overrides": [
                {
                    "sample_id": "a",
                    "phone_use": "positive",
                    "crop_sha256": "crop-sha",
                    "reason": "Thấy phone trong tay.",
                }
            ],
        }
        return parent, decisions

    def test_pending_parent_unknown_can_be_proposed_without_mutation(self):
        parent, decisions = self.parent_fixture()
        result = assemble_rows([parent], [], decisions)[0]
        self.assertEqual(result["proposed_target_mask"], [1, 0])
        self.assertEqual(parent["phone_use"]["state"], "unknown")
        self.assertFalse(result["training_eligible"])

    def test_pending_parent_review_must_match_crop(self):
        parent, decisions = self.parent_fixture()
        decisions["target_overrides"][0]["crop_sha256"] = "wrong"
        with self.assertRaisesRegex(DataContractError, "pin crop"):
            assemble_rows([parent], [], decisions)

    def test_known_parent_target_cannot_be_replaced(self):
        parent, decisions = self.parent_fixture(phone="negative")
        with self.assertRaisesRegex(DataContractError, "đã biết"):
            assemble_rows([parent], [], decisions)

    def test_used_parent_cannot_be_relabeled_or_moved(self):
        for usage in ("train", "val", "test"):
            parent, decisions = self.parent_fixture(usage=usage)
            with self.assertRaises(DataContractError):
                assemble_rows([parent], [], decisions)
            decisions["target_overrides"] = []
            with self.assertRaisesRegex(DataContractError, "freeze"):
                assemble_rows([parent], [], decisions)

    def test_transitive_scene_cannot_cross_split(self):
        rows = [row("a", "train"), row("b", "review_only"), row("c", "val")]
        with self.assertRaisesRegex(DataContractError, "nhiều split"):
            propose_groups(rows, [edge("a", "b"), edge("b", "c")])

    def test_exact_source_cannot_cross_split_without_explicit_edge(self):
        with self.assertRaisesRegex(DataContractError, "nhiều split"):
            propose_groups([row("a", "train", sha="same"), row("b", "test", sha="same")], [])

    def test_existing_group_is_preserved_when_new_frame_attached(self):
        rows = [row("a", "train", "old"), row("b", "review_only"), row("c", "train")]
        propose_groups(rows, [edge("a", "b"), edge("b", "c")])
        self.assertEqual({r["proposed_group_id"] for r in rows}, {"old"})

    def test_two_parent_groups_not_silently_merged(self):
        with self.assertRaisesRegex(DataContractError, "nhiều group v5"):
            propose_groups([row("a", "train", "old1"), row("b", "train", "old2")], [edge("a", "b")])

    def test_unknown_relation_id_rejected(self):
        with self.assertRaises(DataContractError):
            propose_groups([row("a", "train")], [edge("a", "absent")])

    def test_draft_membership_stays_draft(self):
        rows = [
            dict(row("a", "train"), status="draft_pending_owner_review", training_eligible=False)
        ]
        propose_groups(rows, [])
        self.assertFalse(rows[0]["training_eligible"])
        self.assertEqual(rows[0]["status"], "draft_pending_owner_review")

    def test_component_identity_stable_under_input_order(self):
        a = [row("a", "train"), row("b", "train")]
        b = [row("b", "train"), row("a", "train")]
        propose_groups(a, [edge("a", "b")])
        propose_groups(b, [edge("b", "a")])
        self.assertEqual(a[0]["proposed_group_id"], b[0]["proposed_group_id"])


if __name__ == "__main__":
    unittest.main()
