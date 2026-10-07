"""Kiểm các ranh giới leakage và proposal của tuyển candidate mở rộng."""

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_expansion import (
    ReviewImage,
    _new_directory,
    diverse_shortlist,
    nearest_evidence,
    unique_anchors,
)
from ai_exam_monitoring.data.pilot_selection import CandidateAnchor
from ai_exam_monitoring.data.yolo import YoloAnnotation


def anchor(digest: str, rank: str, width: float = .2) -> CandidateAnchor:
    return CandidateAnchor(
        "scb_hrw", "a" * 64, f"images/train/{digest}.jpg", digest,
        f"labels/train/{digest}.txt", "b" * 64, 1, 1, 100, 100, "read",
        YoloAnnotation(1, .5, .5, width, .2), rank,
    )


class ExpansionTests(unittest.TestCase):
    def test_parent_aliases_excluded_across_sources_and_largest_anchor_kept(self):
        old = anchor("parent-test", "01")
        candidates = [old, replace(old, source_id="scb_head"),
                      anchor("new", "02"), anchor("new", "03", .4)]
        chosen = unique_anchors(candidates, {"parent-test"})
        self.assertEqual(len(chosen), 1)
        self.assertEqual(chosen[0].source_image_sha256, "new")
        self.assertEqual(chosen[0].source_anchor_yolo.width, .4)
        self.assertEqual(chosen, unique_anchors(list(reversed(candidates)), {"parent-test"}))

    def test_diversity_is_deterministic_bounded_and_not_class_quota(self):
        rows = [ReviewImage(anchor("one", "01"), 0),
                ReviewImage(anchor("two", "02"), 1),
                ReviewImage(anchor("three", "03"), (1 << 64) - 1)]
        chosen = diverse_shortlist(rows, 2)
        self.assertEqual([r.anchor.source_image_sha256 for r in chosen], ["one", "three"])
        self.assertEqual(chosen, diverse_shortlist(list(reversed(rows)), 2))
        self.assertEqual(len(diverse_shortlist(rows, 10)), 3)
        for budget in (0, -1, True, 1.5):
            with self.assertRaises(DataContractError):
                diverse_shortlist(rows, budget)
        with self.assertRaises(DataContractError):
            diverse_shortlist(rows + [rows[0]], 2)

    def test_hash_collision_is_neighbor_evidence_not_group_assignment(self):
        rows = [{"image_sha256": "other", "dhash": 0, "sample_ids": ["A"]},
                {"image_sha256": "self", "dhash": 0, "sample_ids": ["B"]}]
        neighbors = nearest_evidence(0, "self", rows, 3)
        self.assertEqual(neighbors, [{"image_sha256": "other", "sample_ids": ["A"],
                                      "distance": 0}])
        self.assertNotIn("leakage_group_id", neighbors[0])

    def test_output_cannot_overwrite_or_escape_artifact_root(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "interim"
            root.mkdir()
            _new_directory(root / "new", root)
            for path in (root, root / ".." / "escape"):
                with self.assertRaises(DataContractError):
                    _new_directory(path, root)
            (root / "exists").mkdir()
            with self.assertRaises(DataContractError):
                _new_directory(root / "exists", root)


if __name__ == "__main__":
    unittest.main()
