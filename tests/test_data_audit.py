import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures.make_audit_fixture import SOURCE_NAMES, make_fixture
from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.audit import audit_dataset
from ai_exam_monitoring.data.overlay import export_overlays
from ai_exam_monitoring.data.source_layout import load_source_names
from ai_exam_monitoring.data.validate_labels import validate_label_tree
from ai_exam_monitoring.data.yolo import YoloAnnotation, read_yolo_file


class DataAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "source"
        make_fixture(self.root)

    def audit(self):
        return audit_dataset(
            self.root, images_dir="images", labels_dir="labels", source_names=SOURCE_NAMES
        )

    def test_missing_directory_no_labels_and_empty_labels_are_distinct(self) -> None:
        self.assertIn("not found", validate_label_tree(self.base / "absent", {0})[0])
        empty = self.base / "empty"
        empty.mkdir()
        self.assertIn("No label files", validate_label_tree(empty, {0})[0])
        (empty / "classes.txt").write_text("metadata", encoding="utf-8")
        self.assertIn("No label files", validate_label_tree(empty, {0})[0])
        (empty / "negative.txt").write_text(" \n", encoding="utf-8")
        self.assertEqual(validate_label_tree(empty, {0}), [])
        self.assertTrue(validate_label_tree(empty, set()))
        with self.assertRaises(FileNotFoundError):
            read_yolo_file(empty / "missing.txt")

    def test_nonfinite_and_invalid_geometry(self) -> None:
        for token in ["nan", "NaN", "inf", "-inf", "Infinity", "1e999"]:
            for position in range(1, 5):
                fields = ["0", "0.5", "0.5", "0.2", "0.2"]
                fields[position] = token
                with self.subTest(token=token, position=position):
                    with self.assertRaises(DataContractError):
                        YoloAnnotation.parse(" ".join(fields))
        for line in [
            "-1 0.5 0.5 0.2 0.2",
            "1.5 0.5 0.5 0.2 0.2",
            "0 0.5 0.5 0 0.2",
            "0 0.5 0.5 -0.1 0.2",
            "0 0.9 0.5 0.4 0.2",
            "0 0.5 0.5 0.2",
            "text",
        ]:
            with self.subTest(line=line), self.assertRaises(DataContractError):
                YoloAnnotation.parse(line)
        self.assertEqual(YoloAnnotation.parse("0 0.5 0.5 1 1").width, 1)

    def test_valid_pairing_metadata_counts_and_bbox_sizes(self) -> None:
        result = self.audit()
        self.assertFalse(result["has_errors"])
        self.assertEqual(result["image_count"], 2)
        self.assertEqual(result["label_file_count"], 2)
        self.assertEqual(result["annotation_count_by_class_id"], {0: 1, 7: 0})
        self.assertEqual(result["empty_label_files"], ["labels/b/same.txt"])
        self.assertEqual(len(result["ignored_metadata"]), 2)
        self.assertEqual(result["bbox_sizes"]["width_pixels"]["mean"], 40)
        self.assertEqual(result["bbox_sizes"]["area_pixels"]["mean"], 1600)
        self.assertIn("near_duplicates", result["checks"]["not_checked"])

    def test_same_basename_does_not_hide_missing_pair(self) -> None:
        (self.root / "labels/a/same.txt").unlink()
        result = self.audit()
        self.assertEqual(result["missing_labels"], ["images/a/same.png"])
        self.assertEqual(len(result["samples"]), 1)

    def test_ambiguous_extensions_not_arbitrarily_paired(self) -> None:
        Image.new("RGB", (100, 80)).save(self.root / "images/a/same.jpg")
        result = self.audit()
        self.assertEqual(result["ambiguous_pairs"][0]["key"], "a/same")
        self.assertEqual(len(result["samples"]), 1)
        self.assertEqual(result["bbox_sizes"]["width_pixels"]["count"], 0)

    def test_broken_fixture_and_exact_duplicate_members(self) -> None:
        self.root = self.base / "broken"
        make_fixture(self.root, broken=True)
        result = self.audit()
        self.assertTrue(result["has_errors"])
        self.assertEqual(result["missing_labels"], ["images/a/missing.png"])
        self.assertIn("labels/b/missing.txt", result["orphan_labels"])
        self.assertEqual(result["invalid_images"][0]["file"], "images/b/corrupt.png")
        self.assertEqual(len(result["invalid_labels"]), 2)
        self.assertEqual(
            result["exact_duplicate_groups"][0]["files"], ["images/a/same.png", "images/b/copy.png"]
        )
        self.assertEqual(result["duplicate_file_copies"], 1)
        self.assertEqual(result["annotation_count_by_class_id"], {0: 1, 7: 1})

    def test_bad_label_file_is_not_partially_counted(self) -> None:
        label = self.root / "labels/a/same.txt"
        label.write_text("0 0.5 0.5 0.2 0.2\n99 0.5 0.5 0.2 0.2\n", encoding="utf-8")
        result = self.audit()
        self.assertEqual(result["annotation_count_by_class_id"][0], 0)
        self.assertIn(":2:", result["invalid_labels"][0]["error"])
        self.assertTrue(validate_label_tree(self.root / "labels", {0, 7}))
        label.write_bytes(b"\xff\xfe")
        self.assertEqual(len(self.audit()["invalid_labels"]), 1)

    def test_source_names_are_explicit_and_validated(self) -> None:
        path = self.base / "names.json"
        for content in [
            "{}",
            "[]",
            '{"-1":"bad"}',
            '{"0":""}',
            '{"0":1}',
            '{"0":"a","0":"b"}',
            '{"0":"a","00":"b"}',
        ]:
            path.write_text(content, encoding="utf-8")
            with self.subTest(content=content), self.assertRaises(DataContractError):
                load_source_names(path)
        self.assertEqual(load_source_names(self.root / "source-names.json"), SOURCE_NAMES)

    def test_generated_dataset_yaml_names_and_duplicate_yaml_ids(self) -> None:
        path = self.base / "dataset.yaml"
        path.write_text(
            "path: .\nnames:\n  0: fixture_rectangle\n  7: fixture_marker\n", encoding="utf-8"
        )
        self.assertEqual(load_source_names(path), SOURCE_NAMES)
        for content in [
            "names: [one, two]",
            "names: {0: a, 0: b}",
            "names: {true: name}",
            "names: {-1: name}",
            "names: {0: a, '00': b}",
        ]:
            path.write_text(content, encoding="utf-8")
            with self.subTest(content=content), self.assertRaises(DataContractError):
                load_source_names(path)

    def test_empty_source_is_reported_without_nan_statistics(self) -> None:
        root = self.base / "empty-source"
        (root / "images").mkdir(parents=True)
        (root / "labels").mkdir()
        report = audit_dataset(
            root, images_dir="images", labels_dir="labels", source_names=SOURCE_NAMES
        )
        self.assertEqual(len(report["errors"]), 2)
        self.assertEqual(
            report["bbox_sizes"]["width_pixels"],
            {"count": 0, "min": None, "max": None, "mean": None},
        )
        json.dumps(report, allow_nan=False)

    def test_overlay_broken_source_skips_bad_pairs_and_cli_signals_failure(self) -> None:
        self.root = self.base / "broken-overlay-source"
        make_fixture(self.root, broken=True)
        output = self.base / "broken-overlays"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_exam_monitoring.data.overlay",
                "--dataset",
                str(self.root),
                "--images",
                "images",
                "--labels",
                "labels",
                "--source-names",
                str(self.root / "source-names.json"),
                "--output-dir",
                str(output),
                "--limit",
                "10",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(len(manifest["exported"]), 3)
        self.assertTrue(manifest["audit_has_errors"])
        self.assertFalse(manifest["representative_sample"])

    def test_output_raw_limit_and_unicode_font_guards(self) -> None:
        for output, limit, names in [
            (Path("data/raw/s1-forbidden-output"), 2, SOURCE_NAMES),
            (self.base / "no-output", 0, SOURCE_NAMES),
            (self.base / "unicode-output", 1, {0: "\u0111\u1ed3 v\u1eadt"}),
        ]:
            with self.subTest(output=output), self.assertRaises(DataContractError):
                export_overlays(
                    self.root,
                    images_dir="images",
                    labels_dir="labels",
                    source_names=names,
                    output_dir=output,
                    limit=limit,
                )
            self.assertFalse(output.exists())

    def test_missing_or_escaping_source_layout_fails(self) -> None:
        for root, images in [
            (self.base / "absent", "images"),
            (self.root, "missing"),
            (self.root, "../"),
            (self.root, str(self.root / "images")),
        ]:
            with self.subTest(images=images), self.assertRaises(DataContractError):
                audit_dataset(
                    root, images_dir=images, labels_dir="labels", source_names=SOURCE_NAMES
                )

    def test_overlay_pixels_legend_provenance_and_source_immutability(self) -> None:
        before = {
            p.relative_to(self.root): sha256_file(p) for p in self.root.rglob("*") if p.is_file()
        }
        output = self.base / "overlays"
        result = export_overlays(
            self.root,
            images_dir="images",
            labels_dir="labels",
            source_names=SOURCE_NAMES,
            output_dir=output,
            limit=2,
        )
        self.assertEqual(len(result["exported"]), 2)
        self.assertIn("ID 0 | fixture_rectangle", result["exported"][0]["legend"][0])
        self.assertEqual(result["exported"][0]["image"], "images/a/same.png")
        with Image.open(output / "0001.png") as image:
            self.assertEqual(image.getpixel((30, 45)), (255, 0, 0))
        after = {
            p.relative_to(self.root): sha256_file(p) for p in self.root.rglob("*") if p.is_file()
        }
        self.assertEqual(before, after)
        with self.assertRaises(DataContractError):
            export_overlays(
                self.root,
                images_dir="images",
                labels_dir="labels",
                source_names=SOURCE_NAMES,
                output_dir=output,
                limit=2,
            )
        with self.assertRaises(DataContractError):
            export_overlays(
                self.root,
                images_dir="images",
                labels_dir="labels",
                source_names=SOURCE_NAMES,
                output_dir=self.root / "out",
                limit=2,
            )

    def test_cli_writes_report_and_returns_failure_for_bad_input(self) -> None:
        (self.root / "labels/a/same.txt").unlink()
        report = self.base / "report.json"
        args = [
            sys.executable,
            "-m",
            "ai_exam_monitoring.data.audit",
            "--dataset",
            str(self.root),
            "--images",
            "images",
            "--labels",
            "labels",
            "--source-names",
            str(self.root / "source-names.json"),
            "--output",
            str(report),
        ]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(json.loads(report.read_text())["has_errors"])
        args[-1] = str(self.root / "report.json")
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "report.json").exists())


if __name__ == "__main__":
    unittest.main()
