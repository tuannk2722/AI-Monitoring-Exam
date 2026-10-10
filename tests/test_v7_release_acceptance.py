"""Kiểm release v7: ký cụ thể, masked unknown, parent/test và intake deterministic."""

import copy
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import SourceRef
from ai_exam_monitoring.data.v7_release_acceptance import materialize_records, prepare_sources
from tests import test_pilot_review_acceptance as fixtures


class V7AcceptanceTests(unittest.TestCase):
    def fixture(self, usage="train"):
        old, _, config, _ = fixtures.AcceptanceTests().fixture(usage)
        config.update(whole_family={"path": "groups.json"}, rights={"path": "rights.jsonl"})
        approval = dict(decision="approve_pilot_b_v7_local_release", reviewer="owner",
                        reviewed_at="2026-10-10", exceptions=[], training_run_approved=False,
                        media_upload_approved=False, use_scope="local_classifier_research",
                        approved_counts={usage: 1})
        row = dict(sample_id="A", proposed_usage=usage, proposed_group_id="V7-G",
                   proposed_states=[old.phone_use.state, old.looking_around.state],
                   source_sha256=old.source.image_sha256, crop_sha256=old.crop.crop_sha256,
                   canonical_split=None, training_eligible=False, release_accepted=False,
                   blockers=[], parent_delta=None)
        return old, row, config, approval

    def test_test_identity_evidence_and_access_preserved(self):
        old, row, config, approval = self.fixture("test")
        new = materialize_records([old], [row], {}, {}, config, approval)[0]
        for name in ["source", "crop", "phone_use", "looking_around", "work_context_review",
                     "rights", "test_freeze_ref", "usage"]:
            self.assertEqual(getattr(old, name), getattr(new, name))
        self.assertEqual(new.dataset_version, "new")
        self.assertEqual(new.group.leakage_group_id, "V7-G")
        row["proposed_states"] = ["unknown", "unknown"]
        with self.assertRaises(DataContractError):
            materialize_records([old], [row], {}, {}, config, approval)

    def test_parent_correction_requires_pin_and_keeps_unknown_mask(self):
        old, row, config, approval = self.fixture()
        before = copy.deepcopy(old)
        row.update(proposed_usage="review_only", proposed_states=["unknown", "unknown"])
        approval["approved_counts"] = {"review_only": 1}
        with self.assertRaises(DataContractError):
            materialize_records([old], [row], {}, {}, config, approval)
        row["parent_delta"] = dict(decisions=[{"action": "relabel_target"}],
            proposed_usage="review_only", proposed_states=["unknown", "unknown"],
            original_crop_sha256=old.crop.crop_sha256, source_sha256=old.source.image_sha256)
        new = materialize_records([old], [row], {}, {}, config, approval)[0]
        self.assertEqual(old, before)
        self.assertEqual(new.target_values, (None, None))
        self.assertEqual(new.target_mask, (0, 0))
        self.assertEqual(new.usage, "review_only")

    def test_direction_approval_not_release_and_rights_blocker_not_train(self):
        old, row, config, approval = self.fixture()
        approval["decision"] = "owner_approved_local_direction_and_release_preparation"
        with self.assertRaises(DataContractError):
            materialize_records([old], [row], {}, {}, config, approval)
        approval["decision"] = "approve_pilot_b_v7_local_release"
        row["sample_id"] = "NEW"
        row["blockers"] = ["rights_unverified"]
        source = SourceRef("s", "b" * 64, "a.jpg", "c" * 64, 20, 20)
        with self.assertRaises(DataContractError):
            materialize_records([], [row], {"NEW": source}, {"NEW": {}}, config, approval)

    def test_intake_exact_bytes_and_zip_deterministic(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            file = root / "data/raw/a.png"
            file.parent.mkdir(parents=True)
            Image.new("RGB", (4, 4), "red").save(file)
            source = dict(sample_id="NEW", source_id="s", original_source={
                "path": "data/raw/a.png", "sha256": sha256_file(file)}, exif_orientation=1,
                size=[4, 4], label=None, original_provider_record={})
            first, roots1, _ = prepare_sources(root, root / "outputs/cache1", [source])
            second, _, _ = prepare_sources(root, root / "outputs/cache2", [source])
            self.assertEqual(first, second)
            self.assertEqual((roots1["s"] / first["NEW"].image_relpath).read_bytes(),
                             file.read_bytes())
            with self.assertRaises(DataContractError):
                prepare_sources(root, root / "outputs/cache1", [source])


if __name__ == "__main__":
    unittest.main()
