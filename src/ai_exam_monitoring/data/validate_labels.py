from __future__ import annotations

import argparse
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError

from .source_layout import label_files
from .yolo import read_yolo_file


def validate_label_tree(root: str | Path, allowed_class_ids: set[int]) -> list[str]:
    failures: list[str] = []
    directory = Path(root)
    if not directory.is_dir():
        return [f"Label directory not found: {directory}"]
    if not allowed_class_ids or any(
        type(value) is not int or value < 0 for value in allowed_class_ids
    ):
        return ["Allowed class IDs must be non-empty, non-negative integers"]
    paths = label_files(directory)
    if not paths:
        return [f"No label files found: {directory} (empty label files are valid)"]
    for path in paths:
        try:
            read_yolo_file(path, allowed_class_ids)
        except (DataContractError, OSError, UnicodeError) as exc:
            failures.append(f"{path}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate normalized YOLO label files")
    parser.add_argument("--labels", required=True)
    parser.add_argument("--class-ids", required=True, help="Comma-separated IDs, e.g. 0,1,2")
    args = parser.parse_args()
    try:
        class_ids = {int(value) for value in args.class_ids.split(",")}
    except ValueError:
        parser.error("--class-ids must contain comma-separated integers")
    failures = validate_label_tree(args.labels, class_ids)
    for failure in failures:
        print(failure)
    print(f"Validation complete; failures={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
