import copy
import unittest
from dataclasses import replace

from test_pilot_schema import pending_record

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_owner_groups import import_group_decisions


class OwnerGroupsTests(unittest.TestCase):
    def fixture(self):
        first = pending_record("A", "a" * 64)
        second = pending_record("B", "b" * 64)
        third = pending_record("C", "c" * 64)
        extra = replace(first, sample_id="A-extra", source=replace(
            first.source, label_line_1based=2,
        ))
        remaining = pending_record("D", "d" * 64)
        records = [first, second, third, extra, remaining]
        template = {
            "schema_version": "pilot-b-group-review-draft-v1", "status": "pending_owner_review",
            "ledger_sha256": "e" * 64, "selection_sha256": "f" * 64,
            "reviewer": None, "reviewed_at": None, "training_release_accepted": False,
            "images": [{"image_sha256": digest * 64, "sample_ids": ids,
                        "proposed_group": None, "evidence": None, "uncertainty": "unknown"}
                       for digest, ids in (("a", ["A", "A-extra"]), ("b", ["B"]),
                                           ("c", ["C"]), ("d", ["D"]))],
            "scene_decisions": [{"proposal_id": key, "decision": "unresolved", "reason": None}
                                for key in ("one", "two")],
        }
        draft = copy.deepcopy(template)
        draft["reviewed_at"] = "2026-10-05"
        for row in draft["scene_decisions"]:
            row["decision"] = "keep_together"
        proposals = {"groups": [{"proposal_id": "one", "sample_ids": ["A", "B"]},
                                {"proposal_id": "two", "sample_ids": ["B", "C"]}]}
        return records, draft, template, proposals

    def run_import(self, values):
        return import_group_decisions(*values, reviewer="repository_owner",
                                      evidence_ref="fixture-explicit-owner-submission")

    def test_transitive_must_links_shared_image_and_no_independence(self):
        values = self.fixture()
        rows, report = self.run_import(values)
        self.assertEqual(report["group_assigned_records"], 4)
        self.assertEqual(report["group_assigned_images"], 3)
        self.assertEqual(len(report["components"]), 1)
        self.assertEqual(report["unresolved_sample_ids"], ["D"])
        self.assertTrue(all(row.group.leakage_group_id == rows[0].group.leakage_group_id
                            for row in rows[:4]))
        self.assertIsNone(rows[4].group)
        self.assertTrue(all(row.split is None and row.usage == "review_only" for row in rows))
        self.assertFalse(report["inter_group_independence_confirmed"])
        values[0].reverse()
        values[1]["scene_decisions"].reverse()
        _, second = self.run_import(values)
        self.assertEqual(report["components"], second["components"])

    def test_unresolved_is_preserved_and_changed_group_is_not_interpreted(self):
        values = self.fixture()
        values[1]["scene_decisions"][0]["decision"] = "unresolved"
        values[1]["scene_decisions"][1].update(decision="needs_change", reason="needs owner fix")
        rows, report = self.run_import(values)
        self.assertEqual(report["group_assigned_records"], 0)
        self.assertTrue(all(row.group is None for row in rows))

    def test_rejects_pins_missing_duplicate_decisions_and_inventory_tampering(self):
        for mutation in ("hash", "missing", "duplicate", "sample", "image", "approval", "date"):
            with self.subTest(mutation=mutation):
                values = self.fixture()
                draft = values[1]
                if mutation == "hash":
                    draft["ledger_sha256"] = "0" * 64
                elif mutation == "missing":
                    draft["scene_decisions"].pop()
                elif mutation == "duplicate":
                    draft["scene_decisions"][1] = copy.deepcopy(draft["scene_decisions"][0])
                elif mutation == "sample":
                    draft["images"][0]["sample_ids"] = ["unknown"]
                elif mutation == "image":
                    draft["images"][1] = copy.deepcopy(draft["images"][0])
                elif mutation == "approval":
                    draft["training_release_accepted"] = True
                else:
                    draft["reviewed_at"] = None
                with self.assertRaises(DataContractError):
                    self.run_import(values)


if __name__ == "__main__":
    unittest.main()
