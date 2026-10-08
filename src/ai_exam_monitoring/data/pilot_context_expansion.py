"""Tạo thêm đề xuất người khác trong ảnh đã kiểm; mọi target vẫn unknown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .pilot_inputs import verify_pin
from .pilot_source_candidates import _new_output, context_proposal, pixel_box
from .yolo import YoloAnnotation


def intersection_over_smaller(a: list[int], b: list[int]) -> float:
    intersection = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(
        0, min(a[3], b[3]) - max(a[1], b[1])
    )
    denominator = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return intersection / denominator if denominator > 0 else 0.0


def build_contexts(config_path: Path, workspace: Path) -> dict[str, Any]:
    c = load_yaml(config_path)
    output = workspace / c["output"]
    _new_output(output, workspace / "data/interim")
    p = workspace / c["candidate_path"]
    verify_pin(p, c["candidate_sha256"])
    all_rows = [json.loads(line) for line in p.read_text(encoding="utf8").splitlines()]
    selected = [r for r in all_rows if r["sample_id"] in c["anchor_ids"]]
    if len(selected) != len(c["anchor_ids"]):
        raise ValueError("Anchor selection phải đầy đủ/không trùng ID")
    output.mkdir(parents=True)
    (output / "crops").mkdir()
    (output / "review").mkdir()
    rows: list[dict[str, Any]] = []
    panels = []
    for r in selected:
        source_root = workspace / r["source_root"]
        source = source_root / r["source_image_relpath"]
        label = source_root / r["source_label_relpath"]
        verify_pin(source, r["source_image_sha256"])
        verify_pin(label, r["source_label_sha256"])
        image = Image.open(source).convert("RGB")
        proposals = []
        for number, line in enumerate(label.read_text(encoding="utf8").splitlines(), 1):
            if not line.strip():
                continue
            ann = YoloAnnotation.parse(line)
            if ann.class_id not in c["body_class_ids"]:
                continue
            box = list(context_proposal(ann, [], *image.size, c["padding"]).box.xyxy)
            if box[2] - box[0] < c["review_min_width"] or box[3] - box[1] < c["review_min_height"]:
                continue
            if intersection_over_smaller(box, r["draft_xyxy"]) > c["same_person_overlap_hint"]:
                continue
            proposals.append((number, ann, box))
        proposals.sort(key=lambda v: -(v[2][2] - v[2][0]) * (v[2][3] - v[2][1]))
        retained: list[list[int]] = []
        for number, ann, box in proposals:
            if any(
                intersection_over_smaller(box, other) > c["same_person_overlap_hint"]
                for other in retained
            ):
                continue
            i = c["prefix"] + f"-{len(rows) + 1:03d}"
            crop = image.crop((box[0], box[1], box[2], box[3]))
            path = output / "crops" / (i + ".png")
            crop.save(path)
            new = {k: v for k, v in r.items() if k != "visual_proposal"}
            new.update(
                sample_id=i,
                source_label_line_1based=number,
                source_class_id=ann.class_id,
                source_anchor_yolo={
                    "class_id": ann.class_id,
                    "x_center": ann.x_center,
                    "y_center": ann.y_center,
                    "width": ann.width,
                    "height": ann.height,
                },
                draft_xyxy=box,
                crop_path=path.relative_to(workspace).as_posix(),
                crop_sha256=sha256_file(path),
                parent_anchor_id=r["sample_id"],
                selection_reason="additional_body_anchor_different_person_draft",
                stratum="same_scene_contrast_candidate",
                draft_crop_method="body_anchor_with_context_proposal",
            )
            # Anchor geometry là provenance của annotation được chọn, không phải box người đã duyệt.
            new["source_anchor_xyxy"] = list(pixel_box(ann, *image.size).xyxy)
            rows.append(new)
            drawn = image.copy()
            ImageDraw.Draw(drawn).rectangle(box, outline="red", width=3)
            panel = Image.new("RGB", (640, 440), "white")
            panel.paste(ImageOps.contain(drawn, (370, 395)), (0, 35))
            panel.paste(ImageOps.contain(crop, (255, 395)), (380, 35))
            ImageDraw.Draw(panel).text((5, 5), i + " | " + r["sample_id"], fill="black")
            panel.save(output / "review" / (i + ".jpg"))
            panels.append(panel)
            retained.append(box)
            if len(retained) >= c["max_people_per_image"]:
                break
    for start in range(0, len(panels), 6):
        sheet = Image.new("RGB", (1920, 880), "#ddd")
        for j, panel in enumerate(panels[start : start + 6]):
            sheet.paste(panel, ((j % 3) * 640, (j // 3) * 440))
        sheet.save(output / "review" / f"sheet-{start // 6 + 1:02d}.jpg")
    (output / "proposals.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
        encoding="utf8",
    )
    result = {
        "status": "draft_pending_owner_review",
        "records": len(rows),
        "config_sha256": sha256_file(config_path),
        "proposals_sha256": sha256_file(output / "proposals.jsonl"),
        "training_eligible": False,
        "note": "Nhiều người cùng ảnh vẫn chung group; "
        "hình học chỉ tạo hàng đợi, không gán target.",
    }
    write_json(output / "summary.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_contexts(args.config, Path.cwd()), ensure_ascii=False))


if __name__ == "__main__":
    main()
