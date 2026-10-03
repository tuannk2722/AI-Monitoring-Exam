from __future__ import annotations

import sys
from pathlib import Path

REQUIRED = {
    "README.md",
    "AGENTS.md",
    "docs/00-INDEX.md",
    "docs/25-interface-and-data-contracts.md",
    "configs/baseline.yaml",
    "configs/datasets/exam_v0.1.yaml",
    "src/ai_exam_monitoring/data/build_dataset.py",
    "src/ai_exam_monitoring/training/train.py",
    "src/ai_exam_monitoring/evaluation/evaluate.py",
}
FORBIDDEN_TRACKED_SUFFIXES = {".pt", ".pth", ".mp4", ".avi", ".mov", ".env"}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures: list[str] = []
    for relative in sorted(REQUIRED):
        if not (root / relative).is_file():
            failures.append(f"missing required file: {relative}")
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() in FORBIDDEN_TRACKED_SUFFIXES:
            failures.append(f"large/sensitive file present in repository: {path.relative_to(root)}")
    index = root / "docs/00-INDEX.md"
    if index.is_file():
        index_text = index.read_text(encoding="utf-8")
        for number in range(1, 26):
            marker = f"{number:02d}-"
            if marker not in index_text:
                failures.append(f"documentation index does not reference {marker}*")
    for failure in failures:
        print(f"ERROR: {failure}")
    print(f"Repository check complete; failures={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
