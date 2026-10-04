import unittest
from copy import deepcopy

from ai_exam_monitoring.data.review import apply_group_choices, verify_reviewed_proposals


class ReviewIdentityTests(unittest.TestCase):
    def setUp(self):
        self.proposals = [{"id": "P1", "source_image": "train/images/a.jpg",
                           "image_sha256": "software-fixture-hash",
                           "boxes": [{"label": "phone_use", "xyxy": [1, 2, 8, 9]}]}]
        self.decisions = [{**deepcopy(self.proposals[0]),
                           "action": "approve_proposed_boxes_only"}]

    def test_exact_proposal_passes(self):
        verify_reviewed_proposals(self.decisions, self.proposals)

    def test_changed_identity_geometry_or_scope_fails_closed(self):
        for key, value in [("source_image", "test/images/a.jpg"), ("image_sha256", "other"),
                           ("boxes", []), ("action", "accept_dataset")]:
            decisions = deepcopy(self.decisions)
            decisions[0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_reviewed_proposals(decisions, self.proposals)
        for decisions in ([], self.decisions * 2):
            with self.assertRaises(ValueError):
                verify_reviewed_proposals(decisions, self.proposals)

    def test_group_deferral_is_distinct_from_exclusion_and_keeps_input(self):
        queue = [{"id": "P1", "source_image": "train/images/1.jpg",
                  "disposition": "pending_manual_QA"},
                 {"id": "P2", "source_image": "train/images/2.jpg",
                  "disposition": "pending_manual_QA"}]
        updated = apply_group_choices(queue, [
            {"action": "exclude_image_noise", "ids": ["P1"]},
            {"action": "defer_from_initial_subset", "ids": ["P2"]}])
        self.assertEqual([r["disposition"] for r in updated],
                         ["excluded_owner_noise", "deferred_initial_subset"])
        self.assertTrue(all(not r["training_eligible"] for r in updated))
        self.assertEqual(queue[0]["disposition"], "pending_manual_QA")

    def test_group_decisions_reject_duplicate_or_already_reviewed_samples(self):
        queue = [{"id": "P1", "source_image": "train/images/1.jpg",
                  "disposition": "pending_manual_QA"}]
        group = {"action": "exclude_image_noise", "ids": ["P1"]}
        with self.assertRaises(ValueError):
            apply_group_choices(queue, [group, group])
        queue[0]["disposition"] = "bbox_approved_completeness_pending"
        with self.assertRaises(ValueError):
            apply_group_choices(queue, [group])
