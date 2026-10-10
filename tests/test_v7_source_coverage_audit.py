"""Kiểm semantics funnel và chặn đọc media trong source metadata audit."""

import tempfile
import unittest
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.v7_source_coverage_audit import (
    public_csv_inventory,
    read_metadata,
    remaining_rows,
    selection_funnel,
)


class SourceCoverageAuditTests(unittest.TestCase):
    def test_nonselected_screening_does_not_become_rejected(self) -> None:
        screened = [{"screening_set": "rf", "sample_id": "one"},
                    {"screening_set": "rf", "sample_id": "two"}]
        crops = [{"screening_set": "rf", "screening_id": "one"} for _ in range(3)]
        result = selection_funnel(screened, crops)
        self.assertEqual(result["selected_screening_images"], 1)
        self.assertEqual(result["not_selected_images"], 1)
        self.assertEqual(result["draft_crops"], 3)
        self.assertEqual(result["accepted_crops_r7"], 0)
        self.assertNotIn("rejected_images", result)

    def test_metadata_reader_refuses_media_before_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(DataContractError, "JSON/JSONL"):
                read_metadata(Path(temp) / "historical-test.jpg")

    def test_unused_pool_excludes_parent_lineage_and_source_hint_absence(self) -> None:
        rows = [{"split": "train", "invalid": False, "sha256": str(i),
                 "path": f"train/images/n{i}.rf.export.jpg", "classes": ["phone"]}
                for i in range(7)]
        rows[4]["split"] = "test"
        rows[5]["invalid"] = True
        rows[6]["classes"] = ["unknown-class"]
        parent = [{"source": {"source_id": "s", "image_sha256": "0",
                              "image_relpath": "train/images/n1.rf.old.jpg"}}]
        result = remaining_rows(rows, parent, [{"source_image_sha256": "2"}], {"3"},
                                "s", {"phone"})
        self.assertEqual(result, [])

    def test_duplicate_screening_identity_is_not_silently_counted_twice(self) -> None:
        with self.assertRaisesRegex(DataContractError, "Trùng"):
            selection_funnel([{"screening_set": "rf", "sample_id": "one"}] * 2, [])

    def test_partial_bbox_excludes_whole_last_image_group(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            metadata, prefix = Path(temp) / "info.csv", Path(temp) / "prefix.csv"
            metadata.write_text("ImageID,Subset\na,train\nb,train\nc,train\n", encoding="utf8")
            prefix.write_text("ImageID,XMin\na,0\nb,0\nb,0.2\nc,\n", encoding="utf8")
            result = public_csv_inventory(metadata, prefix)
            self.assertEqual(result["total_available_images"], 3)
            self.assertEqual(result["annotation_index_scanned_images"], 2)
            self.assertEqual(result["bbox_prefix_annotation_rows_read"], 4)


if __name__ == "__main__":
    unittest.main()
