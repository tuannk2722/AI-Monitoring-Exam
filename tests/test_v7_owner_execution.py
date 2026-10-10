"""Owner feedback không tự tạo release/labels cho source thiếu evidence."""

import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.v7_owner_execution import (
    crop_geometry,
    must_link_groups,
    parent_correction_proposals,
    parse_feedback,
    validate_plan,
)


class OwnerExecutionTests(unittest.TestCase):
    def test_default_approval_only_exact_inventory(self):
        md = "### V7-A-001\n\nẢnh\n### V7-A-002\n*Kết quả review của onwer**: chưa rõ mắt."
        feedback = parse_feedback(md, {"V7-A-001", "V7-A-002"})
        self.assertIsNone(feedback["V7-A-001"])
        self.assertIn("chưa rõ", feedback["V7-A-002"])
        with self.assertRaises(DataContractError):
            parse_feedback(md, {"V7-A-001"})
        with self.assertRaises(DataContractError):
            parse_feedback(md + "\n### V7-A-001\n", {"V7-A-001", "V7-A-002"})

    def test_source_approval_cannot_approve_invented_exact_crop(self):
        item = {"V7-S-001": {"review_kind": "source_review"}}
        plan = {"target_order": ["phone_use", "looking_around"], "crops": [{
            "sample_id": "V7-OE-S001-A01", "parent_item_id": "V7-S-001", "states": ["P", "U"],
            "anchor": "người cầm phone", "reason": "ownership",
            "exact_new_crop_owner_approved": False}],
            "reserved_sources": [], "label_updates": []}
        validate_plan(plan, item)
        plan["crops"][0]["exact_new_crop_owner_approved"] = True
        with self.assertRaises(DataContractError):
            validate_plan(plan, item)

    def test_every_approved_source_needs_disposition(self):
        plan = {"target_order": ["phone_use", "looking_around"], "crops": [],
                "reserved_sources": [], "label_updates": []}
        with self.assertRaises(DataContractError):
            validate_plan(plan, {"V7-S-001": {"review_kind": "source_review"}})

    def test_bbox_source_boundaries_and_boolean_coordinates(self):
        self.assertEqual(crop_geometry((20, 30), [0, 1, 20, 30]), (0, 1, 20, 30))
        for box in [[0, 0, 21, 30], [False, 0, 20, 30], [5, 0, 4, 10]]:
            with self.assertRaises(DataContractError):
                crop_geometry((20, 30), box)

    def test_same_source_and_family_join_without_independence_or_split(self):
        records = [{"sample_id": sid, "parent_item_id": parent, "source_sha256": sha}
                   for sid, parent, sha in [("a", "S1", "one"), ("b", "S1", "one"),
                                            ("c", "S2", "two")]]
        groups = must_link_groups(records, [{"parent_item_ids": ["S1", "S2"],
                                            "evidence_vi": "cùng series"}])
        self.assertEqual(len(groups), 1)
        self.assertFalse(groups[0]["independence_proven"])
        self.assertIsNone(groups[0]["official_split"])

    def test_owner_correction_requires_states_and_evidence(self):
        plan = {"target_order": ["phone_use", "looking_around"], "crops": [],
                "reserved_sources": [], "label_updates": [{"sample_id": "V7-C-001",
                "states": ["U", "U"], "reason": "owner chưa rõ gaze"}]}
        items = {"V7-C-001": {"review_kind": "inherited_crop"}}
        validate_plan(plan, items)
        plan["label_updates"][0]["states"] = ["N", "invalid"]
        with self.assertRaises(DataContractError):
            validate_plan(plan, items)

    def test_parent_unknown_correction_never_turns_into_negative(self):
        records = [{"sample_id": "parent", "split": "val", "usage": "val",
                    "crop": {"crop_sha256": "crop"}, "source": {"image_sha256": "image"},
                    "phone_use": {"state": "positive"}, "looking_around": {"state": "unknown"}}]
        decisions = [{"sample_id": "parent", "split": "val", "crop_sha256": "crop",
                      "source_sha256": "image", "target": "phone_use", "before": "positive",
                      "after": "unknown", "action": "relabel_target"}]
        proposal = parent_correction_proposals(records, decisions)[0]
        self.assertEqual(proposal["proposed_states"], ["unknown", "unknown"])
        self.assertEqual(proposal["proposed_usage"], "review_only")
        self.assertEqual(records[0]["phone_use"]["state"], "positive")

    def test_parent_test_or_crop_mismatch_correction_is_blocked(self):
        record = {"sample_id": "parent", "split": "test", "usage": "test",
                  "crop": {"crop_sha256": "crop"}, "source": {"image_sha256": "image"}}
        decision = {"sample_id": "parent", "split": "test", "crop_sha256": "crop",
                    "source_sha256": "image", "action": "exclude_record"}
        with self.assertRaises(DataContractError):
            parent_correction_proposals([record], [decision])
