import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.manifest import ManifestRow, validate_split_integrity
from ai_exam_monitoring.data.split import assign_grouped_splits


def row(sample_id: str, group_id: str, split: str = "") -> ManifestRow:
    return ManifestRow(
        sample_id=sample_id,
        image_path=f"{sample_id}.jpg",
        label_path=f"{sample_id}.txt",
        source="fixture",
        group_id=group_id,
        split=split,
    )


class SplitTests(unittest.TestCase):
    def test_nonfinite_ratios_are_rejected(self) -> None:
        for key in ("train", "val", "test"):
            for value in (float("nan"), float("inf"), float("-inf")):
                ratios = {"train": 0.7, "val": 0.15, "test": 0.15}
                ratios[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(DataContractError):
                    assign_grouped_splits([row("a1", "video-a")], ratios, 42)

    def test_same_group_never_crosses_splits(self) -> None:
        rows = [row("a1", "video-a"), row("a2", "video-a"), row("b1", "video-b")]
        result = assign_grouped_splits(rows, {"train": 0.7, "val": 0.15, "test": 0.15}, 42)
        a_splits = {item.split for item in result if item.group_id == "video-a"}
        self.assertEqual(len(a_splits), 1)
        validate_split_integrity(result)

    def test_leakage_is_rejected(self) -> None:
        with self.assertRaises(DataContractError):
            validate_split_integrity([row("a1", "video-a", "train"), row("a2", "video-a", "test")])

    def test_split_is_deterministic(self) -> None:
        rows = [row(f"s{i}", f"g{i}") for i in range(20)]
        first = assign_grouped_splits(rows, {"train": 0.7, "val": 0.15, "test": 0.15}, 42)
        second = assign_grouped_splits(
            list(reversed(rows)), {"train": 0.7, "val": 0.15, "test": 0.15}, 42
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
