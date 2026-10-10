"""Guard targeted audit: original train, unknown, pair và person-unit không nhân count."""

import csv
import json
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch

import yaml
from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.coco_targeted_candidates import bbox, shortlist
from ai_exam_monitoring.data.openimages_targeted_candidates import inventory, shortlisted
from ai_exam_monitoring.data.pilot_targeted_expansion import nearest, parse_owner_cells
from ai_exam_monitoring.data.targeted_review_package import (
    ReviewProposal,
    _source,
    build,
    check_pairs,
)


def proposal(cid="V7-A-001", **kwargs):
    return ReviewProposal(candidate_id=cid, screening_set="fixture", screening_id="screen-1",
        bucket="A", role="positive", states=("P", "U"), xyxy=(0, 0, 12, 20),
        visual_family_hint="scene-hint", observation="Phone trên bàn của đúng người.",
        phenotypes=("desk_phone",), pair_id="pair-1", person_unit_hint="left", **kwargs)


class TargetedOwnerTests(unittest.TestCase):
    def test_owner_parser_keeps_each_target_and_rejects_duplicate(self):
        text = "| train / `sid` / phone_use FN | a | b | c | d | e | U |\n"
        text += "| train / `sid` / looking_around FN | a | b | c | d | e | P / domain |"
        rows = parse_owner_cells(text)
        self.assertEqual([r["target"] for r in rows], ["phone_use", "looking_around"])
        self.assertEqual(rows[0]["decision"], "U")
        for value in [text + "\n" + text, text.replace("| U |", "| maybe |"), "none"]:
            with self.assertRaises(DataContractError):
                parse_owner_cells(value)

    def test_missing_fingerprint_not_independence(self):
        with self.assertRaises(DataContractError):
            nearest(12, [])
        rows = [{"dhash": 1, "sha256": "b"}, {"dhash": 2, "sha256": "a"}]
        self.assertEqual(nearest(0, rows)["sha256"], "a")
        self.assertEqual(nearest(0, rows)["distance"], 1)


class TargetedProposalTests(unittest.TestCase):
    def test_invalid_unknown_or_evaluation_proposal_rejected(self):
        for kwargs in [dict(states=("U", "U")), dict(known_evaluation_family=True),
                       dict(xyxy=(-1, 0, 2, 3)), dict(states=("N", "U")),
                       dict(candidate_id="../escape")]:
            with self.assertRaises(DataContractError):
                replace(proposal(), **kwargs)

    def test_shared_negative_declared_once(self):
        p = proposal()
        n = replace(p, candidate_id="V7-B-001", bucket="B", role="negative",
                    states=("N", "U"), person_unit_hint="right", xyxy=(12, 0, 24, 20))
        pair = dict(pair_id="pair-1", bucket="A", positive_id=p.candidate_id,
                    negative_id=n.candidate_id, match_strength="same_image",
                    matching_basis="Hai người cùng camera.")
        with self.assertRaises(DataContractError):
            check_pairs([p, n], [pair])
        check_pairs([p, n], [{**pair, "shared_negative_primary_bucket": "B"}])

    def test_same_image_and_scene_claims_need_evidence(self):
        p = proposal()
        n = replace(p, candidate_id="V7-A-002", role="negative", states=("N", "U"),
                    screening_id="screen-2", visual_family_hint="different-scene")
        pair = dict(pair_id="pair-1", bucket="A", positive_id=p.candidate_id,
                    negative_id=n.candidate_id, matching_basis="Draft", match_strength="same_image")
        for strength in ["same_image", "same_scene"]:
            with self.assertRaises(DataContractError):
                check_pairs([p, n], [{**pair, "match_strength": strength}])
        check_pairs([p, n], [{**pair, "match_strength": "source_context"}])

    def test_pair_reference_must_include_this_candidate(self):
        p = proposal()
        n = replace(p, candidate_id="V7-A-002", role="negative", states=("N", "U"))
        orphan = replace(p, candidate_id="V7-A-003", pair_id="pair-1")
        pair = dict(pair_id="pair-1", bucket="A", positive_id=p.candidate_id,
                    negative_id=n.candidate_id, matching_basis="Draft",
                    match_strength="source_context")
        with self.assertRaisesRegex(DataContractError, "đúng crop"):
            check_pairs([p, n, orphan], [pair])
        for changes in [dict(bucket="D"), dict(negative_id="missing")]:
            with self.assertRaises(DataContractError):
                check_pairs([p, n], [{**pair, **changes}])

    def test_eval_or_processed_path_rejected_before_image_read(self):
        with tempfile.TemporaryDirectory() as d:
            w = Path(d).resolve()
            base = dict(source_image_relpath="images/train/source.jpg",
                        source_local_image_path="data/processed/source.jpg",
                        source_image_sha256="not-read")
            for changes in [dict(), dict(source_image_relpath="images/test/source.jpg"),
                            dict(source_image_relpath="images/valid/source.jpg"),
                            dict(source_local_image_path="../escape.jpg")]:
                with patch("PIL.Image.open") as read_image:
                    with self.assertRaises(DataContractError):
                        _source({**base, **changes}, w)
                    read_image.assert_not_called()

    def test_bundle_is_review_only_and_rejects_repeat_person(self):
        with tempfile.TemporaryDirectory() as d:
            w = Path(d).resolve()
            path = w / "data/raw/source.jpg"
            path.parent.mkdir(parents=True)
            Image.new("RGB", (24, 20), "red").save(path)
            screening = w / "screening.jsonl"
            row = dict(sample_id="screen-1", source_original_split="train",
                source_image_relpath="images/train/source.jpg",
                source_local_image_path="data/raw/source.jpg",
                source_image_sha256=sha256_file(path), width=24, height=20,
                source_rights_status="public_pending_attribution_and_owner_review")
            screening.write_text(json.dumps(row) + "\n", encoding="utf8")
            scope, parent, selection = (w / p for p in ["scope.json", "parent.sha",
                                                       "selection.json"])
            scope.write_text(json.dumps({"decision": "approve_v7_targeted_preparation_only"}))
            parent.write_text("parent-checksum-snapshot")
            p = proposal()
            n = replace(p, candidate_id="V7-A-002", role="negative", states=("N", "U"),
                        person_unit_hint="right", xyxy=(12, 0, 24, 20))
            pairs = [dict(pair_id="pair-1", bucket="A", positive_id=p.candidate_id,
                          negative_id=n.candidate_id, match_strength="same_image",
                          matching_basis="Hai person cùng ảnh, không hai groups.")]
            def pin(f):
                return {"path": f.relative_to(w).as_posix(), "sha256": sha256_file(f)}
            config = w / "config.yaml"
            def configure(output, second):
                selection.write_text(json.dumps({"proposals": [asdict(p), asdict(second)],
                                                "pairs": pairs}), encoding="utf8")
                c = dict(status="draft_targeted_review_package", training_eligible=False,
                    scope_approval=pin(scope), selection=pin(selection),
                    parent_checksums=pin(parent),
                    screenings=[{"id": "fixture", **pin(screening)}], output=output,
                    require_person_units=True, budgets={"A": 2})
                config.write_text(yaml.safe_dump(c), encoding="utf8")
            # Hai crop khác geometry của cùng person phải bị chặn, trước PNG duplicate guard.
            configure("data/interim/bad", replace(n, person_unit_hint="left", xyxy=(12, 0, 23, 20)))
            with self.assertRaisesRegex(DataContractError, "person unit"):
                build(config, w)
            # Different pixels để độc lập với exact-crop hash guard.
            im = Image.new("RGB", (24, 20), "red")
            im.paste("blue", (12, 0, 24, 20))
            im.save(path)
            row["source_image_sha256"] = sha256_file(path)
            screening.write_text(json.dumps(row) + "\n", encoding="utf8")
            configure("data/interim/good", n)
            result = build(config, w)
            self.assertEqual(result["records"], 2)
            self.assertFalse(result["test_media_read"])
            rows = [json.loads(s) for s in (w / "data/interim/good/candidates.jsonl")
                    .read_text(encoding="utf8").splitlines()]
            for r in rows:
                self.assertEqual(r["canonical_targets"], [None, None])
                self.assertEqual(r["canonical_mask"], [0, 0])
                self.assertIsNone(r["split"])
                self.assertIsNone(r["leakage_group_id"])
                self.assertFalse(r["training_eligible"])
                self.assertTrue(r["source_rights_status"].startswith("public_pending"))
            with self.assertRaises(DataContractError):
                build(config, w)


class PublicCandidateTests(unittest.TestCase):
    def test_coco_absence_is_only_hint_not_negative(self):
        annotations = dict(categories=[{"id": 19, "name": "person"},
                            {"id": 29, "name": "book"}],
            licenses=[{"id": 2, "url": "allowed"}], images=[{"id": 1, "license": 2}],
            annotations=[{"id": 1, "category_id": 19, "iscrowd": 0, "image_id": 1},
                         {"id": 2, "category_id": 29, "iscrowd": 0, "image_id": 1}])
        c = dict(allowed_license_urls=["allowed"], selection_version="fixed",
                 work_keywords=["read"],
                 phone_context_budget=10, negative_context_budget=10)
        rows, _ = shortlist(annotations, {1: "reading"}, c)
        self.assertEqual(rows[0]["kind"], "no_phone_annotation_work_hint")
        self.assertIsNone(rows[0]["phone_hint"])
        self.assertNotIn("phone_use", rows[0])
        c["allowed_license_urls"] = ["not-allowed"]
        self.assertEqual(shortlist(annotations, {1: "reading"}, c)[0], [])

    def test_coco_invalid_and_clipped_geometry(self):
        self.assertEqual(bbox({"bbox": [-1, -2, 8, 9]}, 10, 10).xyxy, (0, 0, 7, 7))
        for box in [[0, 0, 0, 1], [0, 0, float("nan"), 1], [20, 20, 1, 1]]:
            with self.assertRaises(DataContractError):
                bbox({"bbox": box}, 10, 10)

    def test_openimages_discards_entire_tail_image(self):
        with tempfile.TemporaryDirectory() as d:
            w = Path(d)
            classes, prefix = w / "classes.csv", w / "prefix.csv"
            classes.write_text("dynamic-person,Person\ndynamic-phone,Mobile phone\n",
                               encoding="utf8")
            fields = ["ImageID", "LabelName", "XMin", "XMax", "YMin", "YMax", "IsDepiction",
                      "IsGroupOf", "IsInside"]
            with prefix.open("w", encoding="utf8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                base = dict(XMin=0, XMax=1, YMin=0, YMax=1, IsDepiction=0, IsGroupOf=0, IsInside=0)
                for image_id, name in [("one", "dynamic-person"), ("last", "dynamic-person"),
                                       ("last", "dynamic-phone")]:
                    writer.writerow(dict(base, ImageID=image_id, LabelName=name))
                f.write("last,dynamic-phone,0,1,0")
            c = dict(person_classes=["Person"], context_classes=[], phone_class="Mobile phone")
            rows, stats = inventory(prefix, classes, c)
            self.assertEqual(set(rows), {"one"})
            self.assertEqual(stats["excluded_last_image_id"], "last")
            self.assertEqual(stats["incomplete_tail_rows"], 1)
            self.assertFalse(stats["complete_source_inventory"])

    def test_openimages_train_rotation_license_and_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "metadata.csv"
            objects = {str(i): [dict(class_name="Person"), dict(class_name="Book")]
                       for i in range(4)}
            p.write_text("ImageID,Subset,Rotation,License\n0,train,0.0,allowed\n"
                         "1,test,0.0,allowed\n2,train,90,allowed\n3,train,0.0,denied\n",
                         encoding="utf8")
            c = dict(person_classes=["Person"], work_classes=["Book"], table_classes=[],
                phone_class="Mobile phone", allowed_rotations=["0.0"],
                allowed_license_urls=["allowed"], selection_version="fixed",
                screening_budgets={"work_without_phone_annotation_hint": 10})
            rows = shortlisted(objects, p, c)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["image_metadata"]["ImageID"], "0")
            self.assertEqual(rows[0]["kind"], "work_without_phone_annotation_hint")
            self.assertNotIn("canonical_targets", rows[0])

    def test_title_hint_without_person_and_previously_screened_exclusion(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "metadata.csv"
            p.write_text("ImageID,Subset,Rotation,License,Title\n"
                         "one,train,0,allowed,Office desk\n"
                         "two,train,0,allowed,Product\n"
                         "eval,test,0,allowed,Office desk\n", encoding="utf8")
            phone = dict(class_name="Mobile phone", normalized_xyxy=[0, 0, 1, 1],
                         IsOccluded="0", IsTruncated="0")
            c = dict(person_classes=["Person"], work_classes=["Desk"], table_classes=[],
                phone_class="Mobile phone", allowed_rotations=["0"],
                allowed_license_urls=["allowed"], selection_version="fixed",
                phone_title_keywords=["office"], work_rank_weight=1, table_rank_weight=1,
                screening_budgets={"title_phone_context_hint": 10})
            objects = {key: [phone] for key in ["one", "two", "eval"]}
            rows = shortlisted(objects, p, c)
            self.assertEqual([r["image_metadata"]["ImageID"] for r in rows], ["one"])
            self.assertEqual(rows[0]["people"], [])
            self.assertNotIn("canonical_targets", rows[0])
            self.assertEqual(shortlisted(objects, p, c, {"one"}), [])


if __name__ == "__main__":
    unittest.main()
