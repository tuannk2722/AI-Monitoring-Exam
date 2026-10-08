"""Tạo crop nháp từ nguồn YOLO đã pin; không suy nhãn, nhóm hoặc approval."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .image_similarity import difference_hash
from .pilot_expansion import ReviewImage, diverse_shortlist
from .pilot_inputs import verify_pin
from .pilot_owner_groups import verify_payload
from .pilot_schema import PixelBox, read_records
from .pilot_selection import CandidateAnchor
from .yolo import YoloAnnotation


@dataclass(frozen=True)
class DraftBox:
    box: PixelBox
    method: str
    containing_body_count: int


def pixel_box(a: YoloAnnotation, width: int, height: int) -> PixelBox:
    return PixelBox(
        max(0, math.floor((a.x_center - a.width / 2) * width)),
        max(0, math.floor((a.y_center - a.height / 2) * height)),
        min(width, math.ceil((a.x_center + a.width / 2) * width)),
        min(height, math.ceil((a.y_center + a.height / 2) * height)),
    )


def context_proposal(
    anchor: YoloAnnotation, bodies: list[YoloAnnotation], width: int, height: int, padding: float
) -> DraftBox:
    """Vùng chứa chỉ là gợi ý hình học, không khẳng định phone thuộc người nào."""
    if not 0 <= padding <= 1:
        raise DataContractError("Padding nháp phải trong [0,1]")
    containers = [
        a
        for a in bodies
        if a.x_center - a.width / 2 <= anchor.x_center <= a.x_center + a.width / 2
        and a.y_center - a.height / 2 <= anchor.y_center <= a.y_center + a.height / 2
        and a.width * a.height >= anchor.width * anchor.height
    ]
    selected = (
        min(containers, key=lambda a: (a.width * a.height, a.class_id)) if containers else anchor
    )
    b = pixel_box(selected, width, height)
    dx, dy = math.ceil((b.xmax - b.xmin) * padding), math.ceil((b.ymax - b.ymin) * padding)
    return DraftBox(
        PixelBox(
            max(0, b.xmin - dx),
            max(0, b.ymin - dy),
            min(width, b.xmax + dx),
            min(height, b.ymax + dy),
        ),
        "body_container_hint" if containers else "source_anchor_hint",
        len(containers),
    )


def _new_output(path: Path, root: Path) -> None:
    if (
        not path.resolve().is_relative_to(root.resolve())
        or path.resolve() == root.resolve()
        or path.exists()
    ):
        raise DataContractError("Output phải mới và nằm trong data/interim")


def build_candidates(config_path: Path, workspace: Path) -> dict[str, Any]:
    c = load_yaml(config_path)
    if c["status"] != "draft_preparation" or c["formulation"] != "B":
        raise DataContractError("Chỉ tạo draft B")
    out = workspace / c["output"]
    _new_output(out, workspace / "data/interim")
    for field in ["approval", "inventory", "payload_audit"]:
        verify_pin(workspace / c[field], c[field + "_sha256"])
    approval = json.loads((workspace / c["approval"]).read_text(encoding="utf8"))
    if approval["decision"] != "approve_v6_source_plan_and_continue_preparation":
        raise DataContractError("Thiếu approval phương án nguồn")
    parent = workspace / c["parent_package"]
    verify_payload(parent)
    records = read_records(parent / "review-ledger.jsonl")
    used_sha = {r.source.image_sha256 for r in records}
    inv = json.loads((workspace / c["inventory"]).read_text(encoding="utf8"))
    audits = json.loads((workspace / c["payload_audit"]).read_text(encoding="utf8"))
    chosen = []
    stats: dict[str, Any] = {}
    seen_lineages = set()
    for previous in c.get("previous_candidates", []):
        previous_path = workspace / previous["path"]
        verify_pin(previous_path, previous["sha256"])
        for line in previous_path.read_text(encoding="utf8").splitlines():
            previous_row = json.loads(line)
            used_sha.add(previous_row["source_image_sha256"])
            seen_lineages.add((previous_row["source_id"], previous_row["lineage_hint"]))
    # Mỗi strata chọn ảnh đa dạng; budgets chỉ giới hạn review, không quota train/nhãn.
    for source in c["sources"]:
        sid = source["id"]
        p = Path(source["archive"])
        audit = audits[sid]
        verify_pin(p, audit["sha256"])
        names = {int(k): v for k, v in audit["classes"].items()}
        source_rows = []
        with zipfile.ZipFile(p) as z:
            for r in inv:
                if r["source"] != sid or r["split"] != "train" or r["invalid"]:
                    continue
                if r["sha256"] in used_sha:
                    continue
                n = r["path"]
                lab = n.replace("/images/", "/labels/").rsplit(".", 1)[0] + ".txt"
                label_bytes = z.read(lab)
                annotations = []
                for number, line in enumerate(label_bytes.decode("utf8").splitlines(), 1):
                    if not line.strip():
                        continue
                    a = YoloAnnotation.parse(line)
                    if a.class_id not in names:
                        raise DataContractError("Class ID ngoài namespace")
                    annotations.append((number, a))
                source_rows.append((r, lab, label_bytes, annotations))
            stats[sid] = {"strict_train_images_not_exact_parent": len(source_rows), "strata": {}}
            for stratum in source["strata"]:
                images = []
                lookup = {}
                for r, lab, lb, annotations in source_rows:
                    if r["sha256"] in used_sha or (sid, r["lineage_hint"]) in seen_lineages:
                        continue
                    matching = [
                        (num, a)
                        for num, a in annotations
                        if names[a.class_id] in stratum["classes"]
                    ]
                    if not matching:
                        continue
                    num, a = max(matching, key=lambda item: item[1].width * item[1].height)
                    rank = hashlib.sha256(
                        (c["selection_version"] + "|" + sid + "|" + r["sha256"]).encode()
                    ).hexdigest()
                    anchor = CandidateAnchor(
                        sid,
                        audit["sha256"],
                        r["path"],
                        r["sha256"],
                        lab,
                        hashlib.sha256(lb).hexdigest(),
                        num,
                        a.class_id,
                        r["width"],
                        r["height"],
                        stratum["id"],
                        a,
                        rank,
                    )
                    # Metadata được kiểm lại với bytes khi render selected crop phía dưới.
                    key = r["sha256"]
                    if key not in lookup:
                        images.append(ReviewImage(anchor, r["dhash"]))
                        lookup[key] = (r, annotations)
                selected = diverse_shortlist(images, stratum["review_budget"]) if images else []
                stats[sid]["strata"][stratum["id"]] = {"pool": len(images), "selected": 0}
                for item in selected:
                    selected_anchor = item.anchor
                    r, annotations = lookup[selected_anchor.source_image_sha256]
                    if r["sha256"] in used_sha or (sid, r["lineage_hint"]) in seen_lineages:
                        continue
                    b = z.read(selected_anchor.source_image_relpath)
                    if hashlib.sha256(b).hexdigest() != selected_anchor.source_image_sha256:
                        raise DataContractError("Inventory khác ảnh ZIP")
                    im = Image.open(io.BytesIO(b)).convert("RGB")
                    if (
                        im.size != (selected_anchor.width, selected_anchor.height)
                        or difference_hash(im) != item.dhash
                    ):
                        raise DataContractError("Kích thước/fingerprint inventory sai")
                    bodies = [
                        ann
                        for _, ann in annotations
                        if names[ann.class_id] in source["body_classes"]
                    ]
                    draft = context_proposal(
                        selected_anchor.source_anchor_yolo,
                        bodies,
                        selected_anchor.width,
                        selected_anchor.height,
                        c["draft_padding"],
                    )
                    chosen.append(
                        (
                            source["prefix"],
                            selected_anchor,
                            r,
                            draft,
                            b,
                            z.read(selected_anchor.source_label_relpath),
                        )
                    )
                    used_sha.add(r["sha256"])
                    seen_lineages.add((sid, r["lineage_hint"]))
                    stats[sid]["strata"][stratum["id"]]["selected"] += 1
    out.mkdir(parents=True)
    (out / "crops").mkdir()
    (out / "review").mkdir()
    proposals = []
    panels = []
    counters: dict[str, int] = {}
    for prefix, selected_anchor, r, draft, b, lb in chosen:
        counters[prefix] = counters.get(prefix, 0) + 1
        sample_id = f"{prefix}-{counters[prefix]:03d}"
        source_dir = out / "sources" / selected_anchor.source_id
        for relative, data in [
            (selected_anchor.source_image_relpath, b),
            (selected_anchor.source_label_relpath, lb),
        ]:
            target = (source_dir / relative).resolve()
            if not target.is_relative_to(source_dir.resolve()):
                raise DataContractError("Đường dẫn không an toàn")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        im = Image.open(io.BytesIO(b)).convert("RGB")
        crop = im.crop(draft.box.xyxy)
        cp = out / "crops" / f"{sample_id}.png"
        crop.save(cp)
        row = selected_anchor.to_dict(sample_id)
        row.update(
            {
                "status": "draft_pending_owner_review",
                "selection_reason": (
                    "largest_stratum_anchor_then_dhash_farthest_first_unique_lineage"
                ),
                "usage": "review_only",
                "split": None,
                "leakage_group_id": None,
                "training_eligible": False,
                "phone_use": "unknown",
                "looking_around": "unknown",
                "target_values": [None, None],
                "target_mask": [0, 0],
                "lineage_hint": r["lineage_hint"],
                "dhash": r["dhash"],
                "draft_xyxy": list(draft.box.xyxy),
                "draft_crop_method": draft.method,
                "containing_body_count": draft.containing_body_count,
                "crop_path": cp.relative_to(workspace).as_posix(),
                "crop_sha256": sha256_file(cp),
                "note": (
                    "BBox/crop gợi ý; chưa là visible-person crop đã duyệt, "
                    "không map nhãn từ nguồn."
                ),
            }
        )
        proposals.append(row)
        drawn = im.copy()
        ImageDraw.Draw(drawn).rectangle(draft.box.xyxy, outline="red", width=3)
        panel = Image.new("RGB", (640, 520), "white")
        panel.paste(ImageOps.contain(drawn, (390, 455)), (0, 45))
        panel.paste(ImageOps.contain(crop, (235, 455)), (400, 45))
        ImageDraw.Draw(panel).text(
            (5, 5), f"{sample_id} | {selected_anchor.stratum} | {draft.method}", fill="black"
        )
        panel.save(out / "review" / f"{sample_id}.jpg")
        panels.append(panel)
    for start in range(0, len(panels), 6):
        sheet = Image.new("RGB", (1920, 1040), "#ddd")
        for i, panel in enumerate(panels[start : start + 6]):
            sheet.paste(panel, ((i % 3) * 640, (i // 3) * 520))
        sheet.save(out / "review" / f"sheet-{start // 6 + 1:02d}.jpg")
    (out / "proposals.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in proposals),
        encoding="utf8",
    )
    summary = {
        "status": "draft_pending_owner_review",
        "records": len(proposals),
        "sources": stats,
        "config_sha256": sha256_file(config_path),
        "parent_checksums_sha256": sha256_file(parent / "checksums.sha256"),
        "proposals_sha256": sha256_file(out / "proposals.jsonl"),
        "training_eligible": False,
    }
    write_json(out / "summary.json", summary)
    return summary


def render_visual_revision(
    parent: Path, observations_path: Path, output: Path, workspace: Path
) -> dict[str, Any]:
    """Dựng revision crop mới từ proposal đã pin; không tạo approval canonical."""
    workspace = workspace.resolve()
    parent = parent.resolve()
    output = output.resolve()
    observations_path = observations_path.resolve()
    _new_output(output, workspace / "data/interim")
    rows = [
        json.loads(line)
        for line in (parent / "proposals.jsonl").read_text(encoding="utf8").splitlines()
    ]
    observations = json.loads(observations_path.read_text(encoding="utf8"))["rows"]
    notes = {row["sample_id"]: row for row in observations}
    if len(notes) != len(observations) or set(notes) != {r["sample_id"] for r in rows}:
        raise DataContractError("Review phải bao phủ đúng selection, không trùng ID")
    prepared = []
    for row in rows:
        n = notes[row["sample_id"]]
        if (
            n["source_image_sha256"] != row["source_image_sha256"]
            or n["r1_crop_sha256"] != row["crop_sha256"]
        ):
            raise DataContractError("Review khác identity/crop đã pin")
        source_root = (
            workspace / row["source_root"]
            if row.get("source_root")
            else parent / "sources" / row["source_id"]
        )
        source = source_root / row["source_image_relpath"]
        verify_pin(source, row["source_image_sha256"])
        verify_pin(workspace / row["crop_path"], row["crop_sha256"])
        box = PixelBox(*row["draft_xyxy"])
        unit = n.get("context_normalized_source")
        relative = n.get("context_relative_to_r1_crop")
        if unit is not None and relative is not None:
            raise DataContractError("Không được có hai cách sửa crop")
        if unit is not None or relative is not None:
            coords = unit if unit is not None else relative
            if len(coords) != 4 or any(not 0 <= v <= 1 for v in coords):
                raise DataContractError("Tọa độ crop proposal không hợp lệ")
            x, y, w, h = (
                (0, 0, row["width"], row["height"])
                if unit is not None
                else (box.xmin, box.ymin, box.xmax - box.xmin, box.ymax - box.ymin)
            )
            box = PixelBox(
                x + math.floor(coords[0] * w),
                y + math.floor(coords[1] * h),
                x + math.ceil(coords[2] * w),
                y + math.ceil(coords[3] * h),
            )
        prepared.append((row, n, box, source))
    output.mkdir(parents=True)
    (output / "crops").mkdir()
    (output / "review").mkdir()
    result = []
    panels = []
    for row, n, box, source in prepared:
        im = Image.open(source).convert("RGB")
        crop = im.crop(box.xyxy)
        cp = output / "crops" / (row["sample_id"] + ".png")
        crop.save(cp)
        new = {
            **row,
            "draft_xyxy": list(box.xyxy),
            "crop_path": cp.relative_to(workspace).as_posix(),
            "crop_sha256": sha256_file(cp),
            "visual_proposal": n,
            "source_root": source.parents[len(Path(row["source_image_relpath"]).parts) - 1]
            .relative_to(workspace)
            .as_posix(),
            "revision_note": "Crop/nhãn đề xuất; canonical targets vẫn unknown, usage review_only.",
        }
        result.append(new)
        if n["recommendation"] == "redraw":
            panel = Image.new("RGB", (600, 500), "white")
            panel.paste(ImageOps.contain(crop, (590, 450)), (5, 35))
            ImageDraw.Draw(panel).text((5, 5), row["sample_id"], fill="black")
            panels.append(panel)
    for i in range(0, len(panels), 6):
        sheet = Image.new("RGB", (1800, 1000), "#ddd")
        for j, panel in enumerate(panels[i : i + 6]):
            sheet.paste(panel, ((j % 3) * 600, (j // 3) * 500))
        sheet.save(output / "review" / f"redraw-{i // 6 + 1:02d}.jpg")
    (output / "proposals.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in result),
        encoding="utf8",
    )
    summary = {
        "status": "draft_pending_owner_review",
        "records": len(result),
        "redrawn": len(panels),
        "parent_proposals_sha256": sha256_file(parent / "proposals.jsonl"),
        "visual_proposals_sha256": sha256_file(observations_path),
        "proposals_sha256": sha256_file(output / "proposals.jsonl"),
        "training_eligible": False,
    }
    write_json(output / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_candidates(args.config, Path.cwd()), ensure_ascii=False))


if __name__ == "__main__":
    main()
