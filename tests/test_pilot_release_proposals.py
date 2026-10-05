import copy
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import test_pilot_package as fixtures

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_release_proposals import (
    apply_release_approval,
    propose_rows,
    test_freeze_attestation,
)
from ai_exam_monitoring.data.pilot_schema import (
    GroupReview,
    ReviewEvidence,
    TargetReview,
    record_to_dict,
    write_records,
)


class ReleaseProposalTests(unittest.TestCase):
    def approval(self):
        return {
            "decision": "approve_pilot_b_release", "reviewer": "repository_owner",
            "reviewed_at": "2026-10-05", "recorded_at": "2026-10-05T04:01:07+07:00",
            "owner_message": "approve release proposal", "exceptions": [],
            "use_scope": "local_classifier_research",
            "approved_items": ["phone_context", "group_boundaries", "split_config",
                               "schema_config", "local_use_scope", "release", "test_freeze"],
        }

    def fixture(self, root):
        records = [fixtures.PilotPackageTests().make_record(
            root, f"SCB-read-{i:03d}", i, states=("unknown", "negative")
        )[0] for i in range(1, 6)]
        review = ReviewEvidence("owner", "2026-10-05", "approved-must-link")
        records[:2] = [replace(r, group=GroupReview(
            "approved", ("approved-must-link",), review
        )) for r in records[:2]]
        config = {
            "status": "draft_pending_owner_acceptance",
            "proposed_use_scope": "local_classifier_research",
            "groups": [{"proposal_id": "merged", "parent_group_ids": ["approved"],
                        "additional_sample_ids": [records[2].sample_id],
                        "proposed_split": "train", "visual_evidence": "related layout"},
                       {"proposal_id": "other", "parent_group_ids": [],
                        "additional_sample_ids": [r.sample_id for r in records[3:]],
                        "proposed_split": "test", "visual_evidence": "different furniture"}],
            "phone_negative_proposals": [{
                "sample_id": records[0].sample_id, "crop_sha256": records[0].crop.crop_sha256,
                "proposed_phone_use": "negative", "proposed_work_context": "confirmed_working",
                "observation": "Both hands on visible pen/paper, visible working desk",
            }],
        }
        return records, config

    def test_proposals_preserve_unknowns_owner_must_links_and_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            records, config = self.fixture(Path(tmp))
            original = copy.deepcopy(records)
            rows = propose_rows(records, config)
            self.assertEqual(rows, propose_rows(list(reversed(records)), config))
            self.assertEqual(records, original)
            self.assertEqual([r["proposed_phone_use"] for r in rows],
                             ["negative", "unknown", "unknown", "unknown", "unknown"])
            self.assertEqual([r["proposed_split"] for r in rows],
                             ["train", "train", "train", "test", "test"])
            self.assertTrue(rows[0]["proposed_confirmed_normal"])
            self.assertFalse(rows[1]["proposed_confirmed_normal"])
            with self.assertRaises(DataContractError):
                propose_rows(records, {**config, "groups": config["groups"][1:]})
            wrong_sha = copy.deepcopy(config)
            wrong_sha["phone_negative_proposals"][0]["crop_sha256"] = "a" * 64
            with self.assertRaises(DataContractError):
                propose_rows(records, wrong_sha)

    def test_same_source_cannot_cross_split_or_enter_as_unassigned(self):
        with tempfile.TemporaryDirectory() as tmp:
            records, config = self.fixture(Path(tmp))
            records[3] = replace(records[3], source=records[0].source)
            with self.assertRaises(DataContractError):
                propose_rows(records, config)
            with self.assertRaises(DataContractError):
                propose_rows(records, {**config, "groups": config["groups"][:1]})

    def test_release_approval_preserves_existing_reviews_and_review_only_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            records, config = self.fixture(Path(tmp))
            extra = fixtures.PilotPackageTests().make_record(
                Path(tmp), "RF-extra", 6, states=("positive", "unknown")
            )[0]
            records.append(extra)
            original = copy.deepcopy(records)
            accepted = apply_release_approval(
                records, config, self.approval(), dataset_version="release-v2",
                split_version="split-v1", evidence_ref="owner-approval.json",
            )
            self.assertEqual(original, records)
            for before, after in zip(records, accepted, strict=True):
                self.assertEqual(before.crop, after.crop)
                self.assertEqual(before.source, after.source)
                self.assertEqual(before.looking_around, after.looking_around)
            self.assertEqual(accepted[0].target_values, (0, 0))
            self.assertEqual(accepted[0].normal_review, "confirmed_normal")
            self.assertEqual(accepted[1].target_mask, (0, 1))
            self.assertEqual(accepted[3].test_freeze_ref, "release.json#test_freeze")
            self.assertEqual(accepted[-1].usage, "review_only")
            self.assertIsNone(accepted[-1].split)
            self.assertEqual(accepted[-1].rights, extra.rights)
            self.assertEqual(accepted[-1].phone_use, extra.phone_use)
            self.assertIsNone(accepted[-1].release_review)
            self.assertIsNone(accepted[0].group.session_id)

    def test_release_rejects_missing_scope_approval_or_changes_to_known_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            records, config = self.fixture(Path(tmp))
            for mutation in ("scope", "partial_approval", "reuse_version", "known_phone"):
                with self.subTest(mutation=mutation):
                    rows, approval = copy.deepcopy(records), self.approval()
                    version = "release-v2"
                    if mutation == "scope":
                        approval["use_scope"] = "external_upload"
                    elif mutation == "partial_approval":
                        approval["approved_items"].remove("group_boundaries")
                    elif mutation == "reuse_version":
                        version = rows[0].dataset_version
                    else:
                        rows[0] = replace(rows[0], phone_use=TargetReview(
                            "positive", "previously approved", rows[0].crop.review
                        ))
                    with self.assertRaises(DataContractError):
                        apply_release_approval(
                            rows, config, approval, dataset_version=version,
                            split_version="split-v1", evidence_ref="owner-approval.json",
                        )

    def test_freeze_hashes_match_manifest_serializer_and_detect_label_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records, config = self.fixture(root)
            rows = apply_release_approval(
                records, config, self.approval(), dataset_version="release-v2",
                split_version="split-v1", evidence_ref="owner-approval.json",
            )
            args = {"config_sha256": "a" * 64, "approval_sha256": "b" * 64,
                    "owner_decision_ref": "owner-approval.json", "approval": self.approval(),
                    "commit": "fixture-commit", "protocol": "No test tuning"}
            freeze = test_freeze_attestation(rows, **args)
            write_records(root / "manifest.jsonl", rows)
            self.assertEqual(freeze["manifest_sha256"], hashlib.sha256(
                (root / "manifest.jsonl").read_bytes()
            ).hexdigest())
            test_bytes = "".join(json.dumps(record_to_dict(r), sort_keys=True) + "\n"
                                 for r in sorted(rows, key=lambda r: r.sample_id)
                                 if r.split == "test").encode()
            self.assertEqual(freeze["test_manifest_sha256"], hashlib.sha256(test_bytes).hexdigest())
            changed = list(rows)
            changed[3] = replace(changed[3], phone_use=TargetReview(
                "negative", "new review", changed[3].crop.review
            ))
            self.assertNotEqual(freeze["test_manifest_sha256"],
                                test_freeze_attestation(changed, **args)["test_manifest_sha256"])


if __name__ == "__main__":
    unittest.main()
