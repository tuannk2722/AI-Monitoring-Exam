"""Gom pilot chưa duyệt bằng Markdown/PNG; không split, train hoặc HTML."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import textwrap
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json
from ai_exam_monitoring.data.v7_input_evidence import letterbox_rgb


@dataclass
class PilotReviewItem:
    sample_id: str
    review_kind: str
    source_id: str
    source_sha256: str
    source_original_path: str
    reason: str
    domain: str
    proposed_states: list[str] | None
    xyxy: list[int] | None
    provenance: dict[str, Any]
    attribution: dict[str, Any] | None
    visual_family_hint: str
    media: dict[str, dict[str, str]] = field(default_factory=dict)
    owner_approved: bool = False
    training_eligible: bool = False
    canonical_targets: list[None] = field(default_factory=lambda: [None, None])
    canonical_mask: list[int] = field(default_factory=lambda: [0, 0])
    split: None = None
    independence_proven: bool = False

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Z0-9-]+", self.sample_id) or not self.reason.strip():
            raise DataContractError("ID hoặc lý do review không hợp lệ")
        if (self.owner_approved or self.training_eligible or self.split is not None
                or self.canonical_targets != [None, None] or self.canonical_mask != [0, 0]):
            raise DataContractError("Pilot phải giữ Draft, không supervision/split")
        if self.review_kind == "source_review":
            if self.proposed_states is not None or self.xyxy is not None:
                raise DataContractError("Ảnh nguồn nhiều người không tự có nhãn/crop của anchor")
        elif self.review_kind in {"inherited_crop", "recovered_crop"}:
            if (self.proposed_states is None or len(self.proposed_states) != 2
                    or any(s not in {"P", "N", "U"} for s in self.proposed_states)
                    or self.xyxy is None):
                raise DataContractError("Crop cần hai state Draft và bbox")
        else:
            raise DataContractError("Loại review không hợp lệ")


def safe_path(root: Path, relative: str, *, media: bool = False) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or ".." in Path(relative).parts:
        raise DataContractError("Path thoát workspace")
    if media and (not (path.is_relative_to(root / "data/raw")
                       or path.is_relative_to(root / "data/interim")
                       or path.is_relative_to(root / "outputs"))
                  or any(p.lower() in {"val", "valid", "validation", "test", "holdout",
                                       "val2017", "test2017", "data/processed"}
                         for p in path.relative_to(root).parts)):
        raise DataContractError("Không đọc processed/evaluation media")
    return path


def pin(root: Path, value: dict[str, str], *, media: bool = False) -> Path:
    path = safe_path(root, value["path"], media=media)
    if sha256_file(path) != value["sha256"]:
        raise DataContractError(f"SHA thay đổi: {value['path']}")
    return path


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines()
            if line.strip()]


def source_fields(row: dict[str, Any]) -> tuple[str, str]:
    path = (row.get("source_local_image_path") or row.get("source_image_path")
            or row.get("frame_path") or row.get("source_original_path"))
    sha = (row.get("source_image_sha256") or row.get("frame_sha256")
           or row.get("source_sha256"))
    if not isinstance(path, str) or not isinstance(sha, str):
        raise DataContractError("Nguồn thiếu path/SHA")
    if row.get("source_original_split") in {"test", "valid", "val", "val2017", "test2017"}:
        raise DataContractError("Nguồn evaluation không được mở")
    return path, sha


def fresh_output(root: Path, relative: str) -> Path:
    path = safe_path(root, relative)
    if not path.is_relative_to(root / "outputs") or path.exists():
        raise DataContractError("Output phải mới và thuộc outputs")
    return path


def check_unapproved(items: list[PilotReviewItem], approved_ids: set[str],
                     approved_crop_shas: set[str]) -> None:
    seen: set[str] = set()
    crops: set[str] = set()
    for item in items:
        item.validate()
        if item.sample_id in approved_ids | seen:
            raise DataContractError("ID đã approve hoặc trùng pilot")
        seen.add(item.sample_id)
        crop = item.media.get("crop", {}).get("sha256")
        if crop:
            if crop in approved_crop_shas | crops:
                raise DataContractError("Crop đã approve hoặc trùng pixels/file")
            crops.add(crop)


def draw_panel(item: PilotReviewItem, output: Path, root: Path,
               font: ImageFont.FreeTypeFont) -> Path:
    canvas = Image.new("RGB", (1500, 950), "white")
    draw = ImageDraw.Draw(canvas)
    states = "/".join(item.proposed_states) if item.proposed_states else "Chọn anchor trước nhãn"
    draw.text((18, 10), f"{item.sample_id} | {states} | Chưa duyệt", font=font, fill="black")
    source = pin(root, item.media["source"], media=True)
    with Image.open(source) as im:
        canvas.paste(ImageOps.contain(im.convert("RGB"), (780, 650)), (10, 62))
    if "crop" in item.media:
        with Image.open(pin(root, item.media["crop"], media=True)) as im:
            canvas.paste(ImageOps.contain(im.convert("RGB"), (450, 620)), (810, 62))
        with Image.open(pin(root, item.media["input224"], media=True)) as im:
            canvas.paste(im.convert("RGB"), (1266, 62))
        draw.text((1266, 300), "Input 224 gốc", font=font, fill="black")
    else:
        draw.multiline_text((810, 62), "Ảnh nguồn đáng review\nChưa chốt người/bbox/nhãn\n"
                            "Không tính như crop có target.", font=font, fill="black", spacing=10)
    description = f"{item.reason}\nNguồn: {item.source_id}. Family: {item.visual_family_hint}."
    if item.attribution:
        description += (f"\n{item.attribution.get('title', '')} — "
                        f"{item.attribution.get('artist', '')} — "
                        f"{item.attribution.get('license', '')}")
    wrapped = "\n".join(textwrap.fill(s, width=116) for s in description.splitlines())
    draw.multiline_text((18, 724), wrapped, font=font, fill="black", spacing=6)
    path = output / "panels" / f"{item.sample_id}.png"
    canvas.save(path)
    return path


def build(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    config = load_yaml(config_path)
    output = fresh_output(root, config["output"])
    if config["status"] != "draft_unapproved_review_only":
        raise DataContractError("Không tạo release từ pilot review")
    receipt = json.loads(pin(root, config["approval_receipt"]).read_text(encoding="utf8"))
    approved_path = pin(root, config["approved_review"])
    if receipt["approved_proposals"] != config["approved_review"]:
        raise DataContractError("Receipt không pin batch đã approve")
    approved = read_rows(approved_path)
    decisions = read_rows(pin(root, config["approved_decisions"]))
    if ({r["sample_id"] for r in approved} != {r["sample_id"] for r in decisions}
            or any(r["decision"] != "approve_final_crop_and_proposed_states" for r in decisions)):
        raise DataContractError("Approval IDs/decisions không khớp")
    approved_ids = {r["sample_id"] for r in approved}
    approved_crops = {r["media"]["crop"]["sha256"] for r in approved}
    approved_sources = {r["source_sha256"] for r in approved}
    parents = json.loads(pin(root, config["parent_fingerprints"]).read_text(encoding="utf8"))
    approved_sources.update(r["sha256"] for r in parents)
    registry: dict[tuple[str, str], dict[str, Any]] = {}
    for spec in config["screenings"]:
        for row in read_rows(pin(root, spec)):
            registry[(spec["path"], row["sample_id"])] = row
    selection = json.loads(pin(root, config["selection"]).read_text(encoding="utf8"))
    items = []
    for spec in config["pending_reviews"]:
        for row in read_rows(pin(root, spec)):
            path, sha = source_fields(row)
            for media_pin in row["media"].values():
                pin(root, media_pin, media=True)
            box = row.get("final_xyxy", row.get("xyxy"))
            if not box:
                raise DataContractError("Crop kế thừa thiếu bbox")
            items.append(PilotReviewItem(
                row["sample_id"], "inherited_crop",
                row.get("source_id", "commons_classroom_gapfill"),
                sha, path,
                row["final_reason"], row["domain"], row["final_proposed_states"], box,
                {"review_pin": spec, "original_record": row}, row.get("attribution"),
                row["visual_family_hint"], row["media"]))
    blocked = []
    chosen_source_shas = {item.source_sha256 for item in items}
    for proposed in selection["items"]:
        row = registry[(proposed["registry"], proposed["screening_id"])]
        path, sha = source_fields(row)
        if proposed.get("blocked_reason"):
            blocked.append({**proposed, "source_sha256": sha, "source_path": path})
            continue
        if sha in approved_sources:
            blocked.append({**proposed, "blocked_reason": "Nguồn đã có crop approved/parent",
                            "source_sha256": sha})
            continue
        if proposed["review_kind"] == "source_review" and sha in chosen_source_shas:
            blocked.append({**proposed, "blocked_reason": "Đã có nguồn trong crop review",
                            "source_sha256": sha})
            continue
        original = pin(root, {"path": path, "sha256": sha}, media=True)
        with Image.open(original) as im:
            width, height = im.size
        box = proposed.get("xyxy")
        if box is not None and (len(box) != 4 or any(type(v) is not int for v in box)
                                or not 0 <= box[0] < box[2] <= width
                                or not 0 <= box[1] < box[3] <= height):
            raise DataContractError("BBox vượt ảnh nguồn")
        items.append(PilotReviewItem(
            proposed["sample_id"], proposed["review_kind"], row.get("source_id", "public_video"),
            sha, path, proposed["reason"], proposed["domain"], proposed.get("states"), box,
            {"screening_registry": proposed["registry"], "screening_id": row["sample_id"],
             "source_record": row, "selection": proposed}, proposed.get("attribution"),
            proposed["visual_family_hint"]))
        chosen_source_shas.add(sha)
    items.sort(key=lambda item: item.review_kind == "source_review")
    check_unapproved(items, approved_ids, approved_crops)
    transform = load_yaml(pin(root, config["preprocessing"]))
    if transform["transform"] != "rgb_letterbox_bilinear_v1" or transform["image_size"] != 224:
        raise DataContractError("Không đổi preprocessing E003")
    fill = tuple(transform["fill"])
    if len(fill) != 3:
        raise DataContractError("Fill RGB sai")
    output.mkdir(parents=True)
    for folder_name in ["media", "panels", "sheets"]:
        (output / folder_name).mkdir()
    font = ImageFont.truetype(config["font"], 22)
    for item in items:
        folder = output / "media" / item.sample_id
        folder.mkdir()
        if item.review_kind == "inherited_crop":
            copied = {}
            for kind, spec in item.media.items():
                dest = folder / f"{kind}.png"
                shutil.copyfile(pin(root, spec, media=True), dest)
                copied[kind] = {"path": dest.relative_to(root).as_posix(),
                                "sha256": sha256_file(dest)}
            item.media = copied
        else:
            with Image.open(safe_path(root, item.source_original_path, media=True)) as decoded:
                image = ImageOps.exif_transpose(decoded).convert("RGB")
            images = {"source": image.copy()}
            if item.xyxy is not None:
                left, top, right, bottom = item.xyxy
                crop = image.crop((left, top, right, bottom))
                images["crop"] = crop
                images["input224"] = letterbox_rgb(crop, 224, (fill[0], fill[1], fill[2]))
                ImageDraw.Draw(images["source"]).rectangle(item.xyxy, outline="red", width=4)
            for kind, asset in images.items():
                dest = folder / f"{kind}.png"
                asset.save(dest)
                item.media[kind] = {"path": dest.relative_to(root).as_posix(),
                                    "sha256": sha256_file(dest)}
        panel = draw_panel(item, output, root, font)
        item.media["panel"] = {"path": panel.relative_to(root).as_posix(),
                               "sha256": sha256_file(panel)}
    check_unapproved(items, approved_ids, approved_crops)
    sheets: list[dict[str, Any]] = []
    for offset in range(0, len(items), 6):
        sheet_image = Image.new("RGB", (1800, 1740), "white")
        for j, item in enumerate(items[offset:offset + 6]):
            with Image.open(root / item.media["panel"]["path"]) as im:
                sheet_image.paste(ImageOps.contain(im, (900, 570)),
                                  ((j % 2) * 900, (j // 2) * 580))
        dest = output / "sheets" / f"sheet-{offset // 6 + 1:03}.png"
        sheet_image.save(dest)
        sheets.append({"path": dest.relative_to(root).as_posix(), "sha256": sha256_file(dest),
                       "sample_ids": [i.sample_id for i in items[offset:offset + 6]]})
    rows = [asdict(item) for item in items]
    (output / "review-items.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf8")
    template = [{"sample_id": i.sample_id, "crop_decision": None, "phone_use": None,
                 "looking_around": None, "notes": None} for i in items]
    write_json(output / "owner-review-template.json", {"status": "pending", "items": template})
    summary = {"status": "draft_unapproved_review_only", "items": len(items),
               "review_kinds": dict(Counter(i.review_kind for i in items)),
               "source_images": len({i.source_sha256 for i in items}),
               "sources": dict(Counter(i.source_id for i in items)),
               "blocked_selection_items": len(blocked), "sheets": sheets,
               "approved_ids_in_pilot": 0, "approved_crop_hashes_in_pilot": 0,
               "html_files_created": 0, "training_eligible": False, "test_media_read": False,
               "independent_groups_proven": 0, "canonical_dataset_version": None}
    write_json(output / "summary.json", summary)
    write_json(output / "selection-blockers.json", blocked)
    md = ["# Pilot ảnh/crop chưa được duyệt", "", "Mỗi panel ghi nguồn, crop và input224 nếu đã "
          "có anchor. P/N/U là đề xuất; ảnh nguồn chưa có nhãn. Không HTML, không split/train.", "",
          "## Bảng ảnh tổng hợp", ""]
    for sheet in sheets:
        relative = Path(sheet["path"]).relative_to(Path(config["output"])).as_posix()
        md.extend([f"![{', '.join(sheet['sample_ids'])}]({relative})", ""])
    for title, kinds in [("Crop để nghiệm thu", {"inherited_crop", "recovered_crop"}),
                         ("Ảnh nguồn cần chọn anchor", {"source_review"})]:
        md.extend([f"## {title}", ""])
        for item in items:
            if item.review_kind not in kinds:
                continue
            md.extend([f"### {item.sample_id}", "",
                       f"![{item.sample_id}](panels/{item.sample_id}.png)", "", item.reason, "",
                       f"Nguồn: `{item.source_id}`. "
                       f"Family đề xuất: `{item.visual_family_hint}`.", ""])
            if item.attribution:
                a = item.attribution
                md.extend([f"Credit: {a.get('title')} — {a.get('artist')} — "
                           f"[{a.get('license')}]({a.get('license_url')}). "
                           f"{a.get('changes_notice', '')}", ""])
    (output / "REVIEW.md").write_text("\n".join(md), encoding="utf8")
    checksums = [f"{sha256_file(p)}  {p.relative_to(root).as_posix()}"
                 for p in sorted(output.rglob("*")) if p.is_file()]
    (output / "checksums.sha256").write_text("\n".join(checksums) + "\n", encoding="utf8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--workspace", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.workspace), ensure_ascii=False))


if __name__ == "__main__":
    main()
