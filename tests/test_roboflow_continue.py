import unittest

from scripts.audits.roboflow_continue import apply_decisions


class OwnerDecisionTests(unittest.TestCase):
    def test_exclusion_and_bbox_approval_never_accept_training(self):
        original = [{"id": "P1", "source_image": "train/images/1.jpg",
                     "disposition": "pending_manual_QA", "training_eligible": False}]
        for action, expected in [("exclude_image_noise", "excluded_owner_noise"),
                                 ("approve_proposed_boxes_only",
                                  "bbox_approved_completeness_pending")]:
            result = apply_decisions(original, [{"id": "P1", "action": action}])
            self.assertEqual(result[0]["disposition"], expected)
            self.assertFalse(result[0]["training_eligible"])
            self.assertEqual(original[0]["disposition"], "pending_manual_QA")

    def test_rejects_unknown_actions_duplicate_decisions_and_test_samples(self):
        queue = [{"id": "P1", "source_image": "train/images/1.jpg",
                  "disposition": "pending_manual_QA"}]
        decision = {"id": "P1", "action": "approve_proposed_boxes_only"}
        for decisions in ([decision, decision], [{"id": "P1", "action": "accept_dataset"}]):
            with self.assertRaises(ValueError):
                apply_decisions(queue, decisions)
        queue[0]["source_image"] = "test/images/1.jpg"
        with self.assertRaises(ValueError):
            apply_decisions(queue, [decision])
        queue[0].update(source_image="train/images/1.jpg", disposition="excluded_by_owner")
        with self.assertRaises(ValueError):
            apply_decisions(queue, [decision])
