"""Local annotation overlays for human review, never model predictions."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import write_json

from .audit import add_source_arguments, audit_dataset
from .source_layout import load_source_names, validate_output


def export_overlays(
    dataset_root: str | Path,
    *,
    images_dir: str,
    labels_dir: str,
    source_names: dict[int, str],
    output_dir: str | Path,
    limit: int,
    font_path: str | None = None,
) -> dict[str, Any]:
    if limit <= 0:
        raise DataContractError("Overlay limit must be positive")
    source = Path(dataset_root).resolve()
    output = validate_output(output_dir, source)
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise DataContractError("Overlay output must be new or empty; existing files are preserved")
    if font_path is None and any(not name.isascii() for name in source_names.values()):
        raise DataContractError("Provide --font with a Unicode TrueType font for non-ASCII names")
    font = ImageFont.truetype(font_path, 16) if font_path else ImageFont.load_default(size=16)
    report = audit_dataset(
        source, images_dir=images_dir, labels_dir=labels_dir, source_names=source_names
    )
    samples = sorted(report["samples"], key=lambda sample: sample["image"])[:limit]
    output.mkdir(parents=True, exist_ok=True)
    exported = []
    for index, sample in enumerate(samples, 1):
        with Image.open(source / sample["image"]) as original:
            image = original.convert("RGB")  # raw pixel orientation, same as YOLO coordinates
        boxes = sample["annotations"]
        legend = [
            f"#{n} | ID {box['class_id']} | {source_names[box['class_id']]}"
            for n, box in enumerate(boxes, 1)
        ]
        lines = ["SOURCE ANNOTATIONS - human review required", *legend]
        if not boxes:
            lines.append("EMPTY LABEL - verify absence of annotations visually")
        width = max(image.width, int(max(font.getlength(line) for line in lines)) + 16)
        canvas = Image.new("RGB", (width, image.height + 24 * len(lines) + 16), "white")
        canvas.paste(image, (0, 0))
        draw = ImageDraw.Draw(canvas)
        for n, box in enumerate(boxes, 1):
            x1 = max(0, (box["x_center"] - box["width"] / 2) * image.width)
            y1 = max(0, (box["y_center"] - box["height"] / 2) * image.height)
            x2 = min(image.width - 1, (box["x_center"] + box["width"] / 2) * image.width)
            y2 = min(image.height - 1, (box["y_center"] + box["height"] / 2) * image.height)
            # Subpixel boxes still get a visible one-pixel marker, without changing the annotation.
            x1, y1 = min(x1, x2), min(y1, y2)
            draw.rectangle((x1, y1, x2, y2), outline="red", width=2)
            draw.text(
                (x1, y1),
                f"#{n} ID {box['class_id']}",
                fill="red",
                font=font,
                stroke_width=1,
                stroke_fill="white",
            )
        for n, line in enumerate(lines):
            draw.text((8, image.height + 8 + n * 24), line, fill="black", font=font)
        filename = f"{index:04d}.png"
        canvas.save(output / filename)
        exported.append(
            {
                "output": filename,
                "image": sample["image"],
                "label": sample["label"],
                "legend": legend,
            }
        )
    manifest = {
        "schema_version": 1,
        "selection": "first valid unique pairs sorted by image path",
        "representative_sample": False,
        "requested_limit": limit,
        "eligible_count": len(report["samples"]),
        "exported": exported,
        "source_names": source_names,
        "audit_has_errors": report["has_errors"],
        "audit_report": "audit.json",
        "notes": [
            "Invalid, missing and ambiguous pairs excluded; see audit.json",
            "Review all classes/conditions separately; this is not stratified sampling",
            "Labels are source annotations, not model predictions or canonical mapping",
        ],
    }
    write_json(output / "audit.json", report)
    write_json(output / "manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Export local source-label overlays for review")
    add_source_arguments(parser)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--limit", required=True, type=int)
    parser.add_argument("--font", help="TrueType font with glyphs for the supplied source names")
    args = parser.parse_args()
    try:
        result = export_overlays(
            args.dataset,
            images_dir=args.images,
            labels_dir=args.labels,
            source_names=load_source_names(args.source_names),
            output_dir=args.output_dir,
            limit=args.limit,
            font_path=args.font,
        )
    except (DataContractError, OSError, ValueError) as exc:
        parser.exit(2, f"Overlay input/output error: {exc}\n")
    print(f"Exported {len(result['exported'])} overlays to {args.output_dir}")
    return int(result["audit_has_errors"] or not result["exported"])


if __name__ == "__main__":
    raise SystemExit(main())
