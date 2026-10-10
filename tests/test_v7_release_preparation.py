"""Kiểm gate membership draft: không leak evaluation hoặc biến U thành âm."""

import copy
import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.v7_release_preparation import prepare_assignments


def parent(sid: str, usage: str, gid: str) -> dict:
    return {"sample_id": sid, "usage": usage,
            "phone_use": {"state": "positive"}, "looking_around": {"state": "unknown"},
            "group": {"leakage_group_id": gid},
            "source": {"image_sha256": sid + "-source", "source_id": "fixture"},
            "crop": {"crop_sha256": sid + "-crop"}}


def candidate(sid: str, states: list[str]) -> dict:
    return {"sample_id": sid, "origin": "owner_execution", "source_sha256": sid + "-source",
            "states": states, "official_split": None, "training_eligible": False,
            "eligibility_proposal": "new_crop_final_annotation_review_pending",
            "owner_exact_crop_label_approved": False,
            "media": {"crop": {"sha256": sid + "-crop"}}}


class ReleasePreparationTests(unittest.TestCase):
    def test_evaluation_family_quarantines_new_and_preserves_parent(self):
        original = [parent("VAL", "val", "g"), parent("WAIT", "review_only", "g")]
        before = copy.deepcopy(original)
        pool = [candidate("NEW", ["P", "U"])]
        rows, groups = prepare_assignments(original, pool, [], [{"sample_ids": ["NEW"]}],
            [{"sample_ids": ["NEW", "WAIT"], "reason": "boundary pending", "evidence_ref": "ref"}],
            [{"sample_id": "NEW", "blockers": []}])
        by_id = {r["sample_id"]: r for r in rows}
        self.assertEqual(original, before)
        self.assertEqual(by_id["VAL"]["proposed_usage"], "val")
        self.assertEqual(by_id["NEW"]["proposed_usage"], "review_only")
        self.assertIn("evaluation_family_or_boundary_pending", by_id["NEW"]["blockers"])
        self.assertEqual(by_id["NEW"]["proposed_target_values"], [1, None])
        self.assertEqual(by_id["NEW"]["proposed_target_mask"], [1, 0])
        self.assertTrue(all(r["canonical_split"] is None and not r["training_eligible"]
                            and not r["release_accepted"] for r in rows))
        self.assertEqual(len(groups), 1)

    def test_rights_and_unknown_keep_out_of_supervision(self):
        pool = [candidate("RIGHTS", ["N", "N"]), candidate("UU", ["U", "U"])]
        rows, _ = prepare_assignments([], pool, [], [{"sample_ids": ["RIGHTS", "UU"]}], [],
            [{"sample_id": "RIGHTS", "blockers": ["license_unverified"]},
             {"sample_id": "UU", "blockers": []}])
        self.assertEqual({r["proposed_usage"] for r in rows}, {"review_only"})
        uu = next(r for r in rows if r["sample_id"] == "UU")
        self.assertEqual(uu["proposed_target_values"], [None, None])
        self.assertEqual(uu["proposed_target_mask"], [0, 0])

    def test_cross_parent_split_and_test_delta_blocked(self):
        p = [parent("TRAIN", "train", "a"), parent("TEST", "test", "b")]
        with self.assertRaises(DataContractError):
            prepare_assignments(p, [], [], [],
                [{"sample_ids": ["TRAIN", "TEST"], "reason": "bad edge", "evidence_ref": "r"}], [])
        delta = {"sample_id": "TEST", "source_sha256": "TEST-source",
                 "original_crop_sha256": "TEST-crop", "parent_usage": "test",
                 "proposed_usage": "train", "proposed_states": ["positive", "unknown"],
                 "decisions": [{"action": "change"}]}
        with self.assertRaises(DataContractError):
            prepare_assignments(p, [], [delta], [], [], [])

    def test_exact_component_and_rights_inventory_required(self):
        pool = [candidate("NEW", ["P", "N"])]
        with self.assertRaises(DataContractError):
            prepare_assignments([], pool, [], [], [], [{"sample_id": "NEW", "blockers": []}])
        with self.assertRaises(DataContractError):
            prepare_assignments([], pool, [], [{"sample_ids": ["NEW"]}], [], [])


if __name__ == "__main__":
    unittest.main()
