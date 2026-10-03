"""Generate software-test images only. No people, dataset semantics or model evidence."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image

SOURCE_NAMES = {0: "fixture_rectangle", 7: "fixture_marker"}


def make_fixture(root: Path, *, broken: bool = False) -> None:
    if root.exists() and any(root.iterdir()):
        raise ValueError("Fixture directory must be new or empty")
    for directory in ("images/a", "images/b", "labels/a", "labels/b"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (100, 80), "navy").save(root / "images/a/same.png")
    Image.new("RGB", (200, 100), "ivory").save(root / "images/b/same.png")
    (root / "labels/a/same.txt").write_text("0 0.5 0.5 0.4 0.5\n", encoding="utf-8")
    (root / "labels/b/same.txt").write_text("", encoding="utf-8")
    (root / "source-names.json").write_text(json.dumps(SOURCE_NAMES), encoding="utf-8")
    (root / "labels/classes.txt").write_text("metadata, not YOLO", encoding="utf-8")
    (root / "labels/README.txt").write_text("SOFTWARE FIXTURE ONLY", encoding="utf-8")
    if broken:
        shutil.copyfile(root / "images/a/same.png", root / "images/b/copy.png")
        (root / "labels/b/copy.txt").write_text("7 0.5 0.5 0.2 0.2\n", encoding="utf-8")
        Image.new("RGB", (60, 60)).save(root / "images/a/missing.png")
        (root / "labels/b/missing.txt").write_text("", encoding="utf-8")
        (root / "images/b/corrupt.png").write_bytes(b"broken image fixture")
        (root / "labels/b/corrupt.txt").write_text("", encoding="utf-8")
        (root / "labels/a/invalid.txt").write_text("0 nan 0.5 0.2 0.2\n", encoding="utf-8")
        (root / "labels/a/unknown.txt").write_text("99 0.5 0.5 0.2 0.2\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--broken", action="store_true")
    args = parser.parse_args()
    make_fixture(Path(args.output), broken=args.broken)
