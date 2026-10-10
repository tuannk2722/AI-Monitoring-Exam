"""Kiểm audit không biến hint thành group hoặc U thành negative."""

import unittest

from ai_exam_monitoring.data.v7_annotation_audit import (
    annotation_tables,
    audit_pairs,
    conservative_graph,
)


def sample(sample_id, states, unit="person", **extra):
    return {
        "sample_id": sample_id,
        "proposed_states": states,
        "source_id": "source",
        "domain": "classroom_or_exam_context",
        "group_id": None,
        "visual_family_hint": "scene-hint",
        "person_unit_hint": unit,
        **extra,
    }


def test_unknown_metadata_is_not_replaced_with_family_hint():
    tables = annotation_tables([sample("V7-C-001", ["U", "P"])], "R7")
    assert tables["summary"]["fully_known"] == 0
    assert tables["summary"]["registered_group_unknown"] == 1
    assert tables["summary"]["camera_unknown"] == 1
    assert tables["matrix"][1][0]["registered_group"] == "UNKNOWN"
    assert tables["looking"][1][0]["camera_id"] == "UNKNOWN"


def test_revised_unknown_invalidates_positive_pair():
    rows = [sample("V7-A-001", ["U", "N"]), sample("V7-A-002", ["N", "N"])]
    pairs = [{"positive_id": "V7-A-001", "negative_id": "V7-A-002", "bucket": "A"}]
    audited, added = audit_pairs(rows, pairs)
    assert not audited[0]["target_polarity_valid"]
    assert added == []


def test_same_image_pair_requires_distinct_known_units():
    rows = [
        sample("V7-A-001", ["P", "U"], source_pixel_sha256="pixels"),
        sample("V7-A-002", ["N", "N"], source_pixel_sha256="pixels"),
    ]
    assert audit_pairs(rows, [])[1] == []
    rows[1]["person_unit_hint"] = "second-person"
    assert len(audit_pairs(rows, [])[1]) == 1
    assert audit_pairs(rows, [])[1][0]["independent_group_gain"] == 0


def test_nearest_similarity_does_not_create_parent_component():
    row = sample(
        "V7-A-001",
        ["P", "U"],
        nearest_eval={"distance": 18, "sample_ids": ["historical-test"], "usages": ["test"]},
    )
    graph = conservative_graph([row], [], [])
    assert graph["components"][0]["historical_nodes"] == []
    assert not graph["unresolved_near_flags"][0]["graph_union"]


def test_parent_exact_link_keeps_evaluation_component_out_of_train():
    row = sample("V7-A-001", ["P", "U"], source_image_sha256="same")
    parent = {"sample_id": "parent", "source_image_sha256": "same", "split": "test"}
    graph = conservative_graph([row], [], [parent])
    assert graph["summary"]["evaluation_linked_components"] == 1
    assert graph["components"][0]["official_split"] is None
    assert graph["summary"]["independent_groups_proven"] == 0


class TestV7AnnotationAudit(unittest.TestCase):
    def test_explicit_parent_scene_hint_is_conservative_split_constraint(self):
        row = sample("V7-C-001", ["U", "P"], visual_family_hint="PARENT-TRAIN-known-group")
        parent = {"sample_id": "parent", "group": {"leakage_group_id": "known-group"},
                  "split": "train"}
        graph = conservative_graph([row], [], [parent])
        self.assertEqual(graph["summary"]["parent_linked_components_pending_review"], 1)
        self.assertIsNone(graph["components"][0]["official_split"])
        self.assertEqual(graph["edges"][0]["evidence_status"], "conservative_unproven_scene")

    def test_unknown_metadata(self):
        test_unknown_metadata_is_not_replaced_with_family_hint()

    def test_revised_unknown_pair(self):
        test_revised_unknown_invalidates_positive_pair()

    def test_same_image_distinct_units(self):
        test_same_image_pair_requires_distinct_known_units()

    def test_nearest_similarity(self):
        test_nearest_similarity_does_not_create_parent_component()

    def test_exact_evaluation_parent(self):
        test_parent_exact_link_keeps_evaluation_component_out_of_train()
