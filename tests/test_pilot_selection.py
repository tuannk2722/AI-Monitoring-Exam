import hashlib
import tempfile
import unittest
import zipfile
from dataclasses import replace
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_selection import (
    CandidateAnchor,
    inventory_anchors,
    select_round_robin,
    source_file,
)
from ai_exam_monitoring.data.yolo import YoloAnnotation


def anchor(source: str, image: str, rank: str, line: int = 1) -> CandidateAnchor:
    return CandidateAnchor(
        source_id=source, archive_sha256=source * 64,
        source_image_relpath=f"images/train/{image}.jpg",
        source_image_sha256=image, source_label_relpath=f"labels/train/{image}.txt",
        source_label_sha256="0" * 64, source_label_line_1based=line, source_class_id=1,
        width=100, height=80, stratum=source, source_anchor_yolo=YoloAnnotation(1, .5, .5, .2, .2),
        rank_sha256=rank,
    )


class PilotSelectionTests(unittest.TestCase):
    def test_expansion_layout_is_explicit_train_only(self) -> None:
        for prefix in ("", "images/val/", "test/images/"):
            with self.assertRaisesRegex(DataContractError, "upstream train"):
                inventory_anchors(
                    {"schema_version": 2, "samples": []}, source_id="rf",
                    source_root=Path.cwd(), archive_sha256="a" * 64,
                    strata_by_class={1: "candidate"}, rank_namespace="draft",
                    image_prefix=prefix,
                )

    def test_dedup_across_strata_and_order_independence(self) -> None:
        candidates = [
            anchor("a", "shared", "01"), anchor("a", "a2", "05"),
            anchor("b", "shared", "02"), anchor("b", "b1", "03"), anchor("b", "b2", "04"),
            anchor("a", "shared", "09", line=2),
        ]
        options = {"stratum_order": ("a", "b"), "quota_per_stratum": 2}
        first = select_round_robin(candidates, **options)
        self.assertEqual(first, select_round_robin(list(reversed(candidates)), **options))
        self.assertEqual(
            [row["source_image_sha256"] for row in first], ["shared", "b1", "a2", "b2"]
        )
        self.assertTrue(all(row["annotation_status"].startswith("source_anchor") for row in first))

    def test_shortage_does_not_transfer_or_add_candidates(self) -> None:
        with self.assertRaisesRegex(DataContractError, "shortage for b"):
            select_round_robin(
                [anchor("a", "shared", "01"), anchor("b", "shared", "02")],
                stratum_order=("a", "b"), quota_per_stratum=1,
            )

    def test_identity_collision_and_unreviewed_stratum_rejected(self) -> None:
        row = anchor("a", "x", "01")
        for rows in ([row, replace(row, rank_sha256="02")], [row]):
            with self.assertRaises(DataContractError):
                select_round_robin(rows, stratum_order=("b",), quota_per_stratum=1)

    def test_true_label_line_number_and_rank_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "images/train").mkdir(parents=True)
            (root / "labels/train").mkdir(parents=True)
            Image.new("RGB", (40, 30), "red").save(root / "images/train/a.jpg")
            label = root / "labels/train/a.txt"
            label.write_text("\n0 .5 .5 .2 .2\n\n1 .5 .5 .3 .3\n", encoding="utf-8")
            report = {"schema_version": 2, "samples": [{
                "image": "images/train/a.jpg", "label": "labels/train/a.txt", "width": 40,
                "height": 30, "annotations": [
                    {"class_id": 0, "x_center": .5, "y_center": .5, "width": .2, "height": .2},
                    {"class_id": 1, "x_center": .5, "y_center": .5, "width": .3, "height": .3},
                ],
            }]}
            rows = inventory_anchors(
                report, source_id="head", source_root=root, archive_sha256="a" * 64,
                strata_by_class={1: "turnhead"}, rank_namespace="pilot-b-selection-v1",
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].source_label_line_1based, 4)
            expected = "|".join((
                "pilot-b-selection-v1", "a" * 64, rows[0].source_image_sha256,
                "labels/train/a.txt", "4",
            ))
            self.assertEqual(rows[0].rank_sha256, hashlib.sha256(expected.encode()).hexdigest())
            label.write_text("1 .5 .5 .3 .3\n", encoding="utf-8")
            with self.assertRaisesRegex(DataContractError, "differs from audit"):
                inventory_anchors(
                    report, source_id="head", source_root=root, archive_sha256="a" * 64,
                    strata_by_class={1: "turnhead"}, rank_namespace="pilot-b-selection-v1",
                )

    def test_traversal_and_validation_sources_are_not_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in ("../other.txt", "C:/other.txt", "images\\a.jpg"):
                with self.assertRaises(DataContractError):
                    source_file(root, relative)
            self.assertEqual(inventory_anchors(
                {"schema_version": 2, "samples": [{"image": "images/val/a.jpg", "label": "x"}]},
                source_id="head", source_root=root, archive_sha256="a" * 64,
                strata_by_class={1: "turnhead"}, rank_namespace="pilot-b-selection-v1",
            ), [])

    def test_extracted_bytes_must_match_pinned_zip_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "images/train").mkdir(parents=True)
            (root / "labels/train").mkdir(parents=True)
            image = root / "images/train/a.jpg"
            Image.new("RGB", (10, 10), "red").save(image)
            label = root / "labels/train/a.txt"
            label.write_text("1 .5 .5 .2 .2\n", encoding="utf-8")
            archive_path = root / "source.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.write(image, "source/images/train/a.jpg")
                archive.write(label, "source/labels/train/a.txt")
            report = {"schema_version": 2, "samples": [{
                "image": "images/train/a.jpg", "label": "labels/train/a.txt", "width": 10,
                "height": 10, "annotations": [{
                    "class_id": 1, "x_center": .5, "y_center": .5, "width": .2, "height": .2,
                }],
            }]}
            options = {
                "source_id": "head", "source_root": root, "archive_sha256": "a" * 64,
                "strata_by_class": {1: "turnhead"}, "rank_namespace": "pilot-b-selection-v1",
                "archive_path": archive_path, "archive_prefix": "source",
            }
            self.assertEqual(len(inventory_anchors(report, **options)), 1)
            Image.new("RGB", (10, 10), "blue").save(image)
            with self.assertRaisesRegex(DataContractError, "differs from pinned ZIP"):
                inventory_anchors(report, **options)


if __name__ == "__main__":
    unittest.main()
