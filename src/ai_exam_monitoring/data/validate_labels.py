from __future__ import annotations

import argparse
from pathlib import Path

from .yolo import read_yolo_file


def validate_label_tree(root: str | Path, allowed_class_ids: set[int]) -> list[str]:
    failures: list[str] = []
    for path in sorted(Path(root).rglob("*.txt")):
        try:
            annotations = read_yolo_file(path)
            unknown = sorted({item.class_id for item in annotations} - allowed_class_ids)
            if unknown:
                failures.append(f"{path}: unknown class ids {unknown}")
        except Exception as exc:
            failures.append(str(exc))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate normalized YOLO label files")
    parser.add_argument("--labels", required=True)
    parser.add_argument("--class-ids", required=True, help="Comma-separated IDs, e.g. 0,1,2")
    args = parser.parse_args()
    failures = validate_label_tree(args.labels, {int(value) for value in args.class_ids.split(",")})
    for failure in failures:
        print(failure)
    print(f"Validation complete; failures={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
