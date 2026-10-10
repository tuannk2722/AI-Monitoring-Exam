"""Nhập owner review125mục và dựng crop/staging mới, không tự release/split/train."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import textwrap
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json
from ai_exam_monitoring.data.v7_input_evidence import letterbox_rgb
from ai_exam_monitoring.data.v7_unapproved_pilot import fresh_output, pin, read_rows, safe_path


@dataclass(frozen=True)
class OwnerItemDecision:
    sample_id: str
    review_kind: str
    owner_feedback_verbatim: str | None
    approval_basis: str
    action: str
    source_or_existing_crop_approved: bool = True
    release_approved: bool = False
    split_assigned: bool = False
    training_approved: bool = False


def parent_correction_proposals(
    records: list[dict[str, Any]], decisions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Đề xuất delta v7 theo receipt cũ; không sửa parent hoặc test."""
    by_id = {r["sample_id"]: r for r in records}
    changes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        if decision["action"] == "retain_target":
            continue
        sid = decision["sample_id"]
        row = by_id[sid]
        if (row["split"] == "test" or row["split"] != decision["split"]
                or row["crop"]["crop_sha256"] != decision["crop_sha256"]
                or row["source"]["image_sha256"] != decision["source_sha256"]):
            raise DataContractError("Parent correction không pin đúng record hoặc đụng test")
        changes[sid].append(decision)
    proposals = []
    for sid, row in by_id.items():
        states = [row["phone_use"]["state"], row["looking_around"]["state"]]
        usage = row["usage"]
        domain = None
        for decision in changes[sid]:
            if decision["action"] == "exclude_record":
                usage = "excluded"
            elif decision["action"] == "relabel_target":
                target = ["phone_use", "looking_around"].index(decision["target"])
                if states[target] != decision["before"]:
                    raise DataContractError("Parent state không khớp receipt trước correction")
                states[target] = decision["after"]
            elif decision["action"] == "metadata_domain":
                domain = decision["domain"]
            else:
                raise DataContractError("Owner delta action chưa được hỗ trợ")
        if (usage != "excluded" and all(s == "unknown" for s in states)
                and usage in {"train", "val"}):
            usage = "review_only"
        proposals.append({"sample_id": sid, "parent_usage": row["usage"],
                          "proposed_usage": usage, "proposed_states": states,
                          "domain_note": domain, "decisions": changes[sid],
                          "original_crop_sha256": row["crop"]["crop_sha256"],
                          "source_sha256": row["source"]["image_sha256"],
                          "parent_mutated": False, "training_eligible": False,
                          "official_v7_assignment": False})
    return proposals


def parse_feedback(markdown: str, expected: set[str]) -> dict[str, str | None]:
    chunks = re.split(r"^### (V7-[A-Z0-9-]+)\s*$", markdown, flags=re.M)
    result: dict[str, str | None] = {}
    for offset in range(1, len(chunks), 2):
        sid, body = chunks[offset:offset + 2]
        if sid in result:
            raise DataContractError("Owner review trùng ID")
        match = re.search(r"^[*]*Kết quả review", body, re.M)
        result[sid] = body[match.start():].strip() if match else None
    if set(result) != expected:
        raise DataContractError("Owner review không đủ/đúng125item inventory đã pin")
    return result


def validate_plan(plan: dict[str, Any], items: dict[str, dict[str, Any]]) -> None:
    if plan["target_order"] != ["phone_use", "looking_around"]:
        raise DataContractError("Không thay target order")
    seen: set[str] = set()
    covered: set[str] = set()
    for spec in plan["crops"]:
        sid, parent = spec["sample_id"], spec["parent_item_id"]
        if (sid in seen or not re.fullmatch(r"V7-OE-S\d{3}-A\d{2}", sid)
                or parent not in items or items[parent]["review_kind"] != "source_review"):
            raise DataContractError("Crop mới trùng ID hoặc không từ source đã review")
        if (len(spec["states"]) != 2 or any(s not in {"P", "N", "U"} for s in spec["states"])
                or not spec["anchor"].strip() or not spec["reason"].strip()
                or spec["exact_new_crop_owner_approved"] is not False):
            raise DataContractError("Crop mới cần anchor/evidence và không suy exact crop approval")
        seen.add(sid)
        covered.add(parent)
    reserved = [r["parent_item_id"] for r in plan["reserved_sources"]]
    if (len(reserved) != len(set(reserved)) or set(reserved) & covered
            or any(not r["reason"] for r in plan["reserved_sources"])):
        raise DataContractError("Reserve/source crop overlap hoặc thiếu lý do")
    source_ids = {i for i, r in items.items() if r["review_kind"] == "source_review"}
    if covered | set(reserved) != source_ids:
        raise DataContractError("Phải disposition mọi source đã approve")
    updates = {r["sample_id"] for r in plan["label_updates"]}
    if (len(updates) != len(plan["label_updates"])
            or not updates.issubset(set(items) - source_ids)):
        raise DataContractError("Label update chỉ từ existing crop đã owner review")
    for update in plan["label_updates"]:
        if (len(update["states"]) != 2 or any(s not in {"P", "N", "U"}
                                               for s in update["states"])
                or not update["reason"].strip()):
            raise DataContractError("Owner correction cần PNU và evidence")


def crop_geometry(image_size: tuple[int, int], xyxy: list[int]) -> tuple[int, int, int, int]:
    width, height = image_size
    if (len(xyxy) != 4 or any(type(v) is not int for v in xyxy)
            or not 0 <= xyxy[0] < xyxy[2] <= width or not 0 <= xyxy[1] < xyxy[3] <= height):
        raise DataContractError("BBox không hợp lệ hoặc vượt source")
    left, top, right, bottom = xyxy
    return left, top, right, bottom


def must_link_groups(rows: list[dict[str, Any]], relations: list[dict[str, Any]]) -> list[
    dict[str, Any]
]:
    parents = {r["sample_id"]: r["sample_id"] for r in rows}
    if len(parents) != len(rows):
        raise DataContractError("Staging trùng sample ID")

    def find(sid: str) -> str:
        while parents[sid] != sid:
            parents[sid] = parents[parents[sid]]
            sid = parents[sid]
        return sid

    def join(ids: list[str]) -> None:
        for sid in ids[1:]:
            parents[find(sid)] = find(ids[0])

    by_source: dict[str, list[str]] = defaultdict(list)
    by_parent: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_source[row["source_sha256"]].append(row["sample_id"])
        by_parent[row["parent_item_id"]].append(row["sample_id"])
    for ids in list(by_source.values()) + list(by_parent.values()):
        join(ids)
    for relation in relations:
        if not relation.get("evidence_vi") or not relation["parent_item_ids"]:
            raise DataContractError("Must-link thiếu bằng chứng")
        ids = [sid for parent in relation["parent_item_ids"] for sid in by_parent.get(parent, [])]
        if ids:
            join(ids)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[find(row["sample_id"])].append(row)
    result = []
    for index, members in enumerate(sorted(groups.values(), key=lambda m: m[0]["sample_id"]), 1):
        gid = f"V7-OE-COMP-{index:03}"
        for row in members:
            row["must_link_component"] = gid
        result.append({"component_id": gid, "sample_ids": [r["sample_id"] for r in members],
                       "source_sha256": sorted({r["source_sha256"] for r in members}),
                       "independence_proven": False, "official_split": None})
    return result


def render_panel(row: dict[str, Any], root: Path, output: Path,
                 font: ImageFont.FreeTypeFont) -> Path:
    canvas = Image.new("RGB", (1500, 950), "white")
    draw = ImageDraw.Draw(canvas)
    title = ("Đã duyệt crop/nhãn" if row["owner_final_crop_approved"]
             else "Crop mới từ nguồn đã duyệt")
    draw.text((12, 10), f"{row['sample_id']} | {'/'.join(row['states'])} | {title}",
              font=font, fill="black")
    for kind, position, size in [("source", (10, 60), (780, 580)),
                                 ("crop", (810, 60), (450, 580))]:
        with Image.open(pin(root, row["media"][kind], media=True)) as im:
            canvas.paste(ImageOps.contain(im.convert("RGB"), size), position)
    with Image.open(pin(root, row["media"]["input224"], media=True)) as im:
        canvas.paste(im, (1266, 60))
    draw.text((1266, 300), "Input224 gốc", font=font, fill="black")
    message = row["reason"] + "\n" + row["anchor"] + "; không split/train."
    if row.get("attribution"):
        credit = row["attribution"]
        message += f"\n{credit.get('title')} — {credit.get('artist')} — {credit.get('license')}"
    lines = "\n".join(textwrap.fill(s, width=126) for s in message.splitlines())
    draw.multiline_text((12, 665), lines, font=font, fill="black", spacing=5)
    path = output / "panels" / f"{row['sample_id']}.png"
    canvas.save(path)
    return path


def build(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    config = load_yaml(config_path)
    output = fresh_output(root, config["output"])
    staging = safe_path(root, config["staging"])
    if staging.exists() or not staging.is_relative_to(root / "data/interim/pilot-b"):
        raise DataContractError("Staging phải version mới, không canonical release")
    if config["status"] != "owner_directions_execution_review_only":
        raise DataContractError("Không suy release từ execution")
    receipt = json.loads(pin(root, config["receipt"]).read_text(encoding="utf8"))
    original = read_rows(pin(root, config["input_items"]))
    by_id = {r["sample_id"]: r for r in original}
    if receipt["original_manifest"] != config["input_items"] or not receipt[
        "default_approve_unannotated_items"
    ]:
        raise DataContractError("Receipt không authorize inventory/default rule")
    feedback = parse_feedback(pin(root, receipt["owner_review_pin"]).read_text(encoding="utf8"),
                              set(by_id))
    if len(original) != receipt["expected_items"]:
        raise DataContractError("Receipt count không khớp inventory")
    plan = json.loads(pin(root, config["crop_plan"]).read_text(encoding="utf8"))
    validate_plan(plan, by_id)
    for relation in config["must_link_relations"]:
        if not set(relation["parent_item_ids"]).issubset(by_id):
            raise DataContractError("Must-link tham chiếu owner item chưa có")
    transform = load_yaml(pin(root, config["preprocessing"]))
    if transform["image_size"] != 224 or transform["transform"] != "rgb_letterbox_bilinear_v1":
        raise DataContractError("Không đổi preprocessing đã review")
    fill = transform["fill"]
    if len(fill) != 3:
        raise DataContractError("Fill phải RGB")
    for item in original:
        pin(root, {"path": item["source_original_path"], "sha256": item["source_sha256"]},
            media=True)
        for spec in item["media"].values():
            pin(root, spec, media=True)
    for spec in plan["crops"]:
        with Image.open(root / by_id[spec["parent_item_id"]]["source_original_path"]) as im:
            crop_geometry(ImageOps.exif_transpose(im).size, spec["xyxy"])
    updates = {r["sample_id"]: r for r in plan["label_updates"]}
    decisions = [OwnerItemDecision(
        sid, item["review_kind"], feedback[sid],
        "explicit_feedback" if feedback[sid] else "default_approve_user_instruction",
        "approve_source_analysis_and_execute_crops" if item["review_kind"] == "source_review"
        else "apply_owner_unknown_correction" if sid in updates else "approve_exact_crop_labels")
        for sid, item in by_id.items()]
    output.mkdir(parents=True)
    staging.mkdir(parents=True)
    for name in ["media", "panels", "sheets", "native224"]:
        (output / name).mkdir()
    records = []
    font = ImageFont.truetype(config["font"], 20)
    specs = [{"parent_item_id": sid, "sample_id": sid, "xyxy": item["xyxy"],
              "states": updates.get(sid, {}).get("states", item["proposed_states"]),
              "anchor": "Anchor nguyên crop đã duyệt",
              "reason": updates.get(sid, {}).get("reason", item["reason"]), "inherited": True}
             for sid, item in by_id.items() if item["review_kind"] != "source_review"]
    specs += plan["crops"]
    for spec in specs:
        item = by_id[spec["parent_item_id"]]
        folder = output / "media" / spec["sample_id"]
        folder.mkdir()
        media: dict[str, dict[str, str]] = {}
        inherited = spec.get("inherited", False)
        if inherited:
            for kind in ["source", "crop", "input224"]:
                dest = folder / f"{kind}.png"
                shutil.copyfile(pin(root, item["media"][kind], media=True), dest)
                media[kind] = {"path": dest.relative_to(root).as_posix(),
                               "sha256": sha256_file(dest)}
        else:
            with Image.open(root / item["source_original_path"]) as decoded:
                source = ImageOps.exif_transpose(decoded).convert("RGB")
            crop = source.crop(crop_geometry(source.size, spec["xyxy"]))
            input224 = letterbox_rgb(crop, 224, (fill[0], fill[1], fill[2]))
            annotated = source.copy()
            ImageDraw.Draw(annotated).rectangle(spec["xyxy"], outline="red", width=4)
            for kind, asset in [("source", annotated), ("crop", crop), ("input224", input224)]:
                dest = folder / f"{kind}.png"
                asset.save(dest)
                media[kind] = {"path": dest.relative_to(root).as_posix(),
                               "sha256": sha256_file(dest)}
        row = {"sample_id": spec["sample_id"], "parent_item_id": spec["parent_item_id"],
               "source_id": item["source_id"], "source_sha256": item["source_sha256"],
               "source_original_path": item["source_original_path"], "xyxy": spec["xyxy"],
               "states": spec["states"], "anchor": spec["anchor"], "reason": spec["reason"],
               "domain": item["domain"], "visual_family_hint": item["visual_family_hint"],
               "attribution": item["attribution"], "owner_feedback_verbatim": feedback[
                   spec["parent_item_id"]], "source_review_approved": True,
               "owner_final_crop_approved": inherited, "owner_receipt": config["receipt"],
               "canonical_targets": [None, None], "canonical_mask": [0, 0], "split": None,
               "training_eligible": False, "independence_proven": False, "media": media}
        panel = render_panel(row, root, output, font)
        media["panel"] = {"path": panel.relative_to(root).as_posix(), "sha256": sha256_file(panel)}
        records.append(row)
    groups = must_link_groups(records, config["must_link_relations"])
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    (output / "staging-crops.jsonl").write_text(payload, encoding="utf8")
    (staging / "review-ledger.jsonl").write_text(payload, encoding="utf8")
    (output / "owner-decisions.jsonl").write_text(
        "".join(json.dumps(asdict(d), ensure_ascii=False) + "\n" for d in decisions),
        encoding="utf8")
    write_json(output / "must-link-components.json", groups)
    write_json(output / "source-reserve.json", plan["reserved_sources"])
    sheets = []
    for start in range(0, len(records), 6):
        sheet = Image.new("RGB", (1800, 1740), "white")
        for j, row in enumerate(records[start:start + 6]):
            with Image.open(root / row["media"]["panel"]["path"]) as im:
                sheet.paste(ImageOps.contain(im, (900, 570)), ((j % 2) * 900, (j // 2) * 580))
        dest = output / "sheets" / f"sheet-{start // 6 + 1:03}.png"
        sheet.save(dest)
        sheets.append(dest.relative_to(output).as_posix())
    for start in range(0, len(records), 20):
        native = Image.new("RGB", (1350, 1160), "white")
        draw = ImageDraw.Draw(native)
        smallfont = ImageFont.truetype(config["font"], 15)
        for j, row in enumerate(records[start:start + 20]):
            x, y = (j % 5) * 270, (j // 5) * 290
            draw.text((x + 4, y + 4), row["sample_id"], font=smallfont, fill="black")
            draw.text((x + 4, y + 25), "/".join(row["states"]), font=smallfont, fill="black")
            with Image.open(root / row["media"]["input224"]["path"]) as im:
                native.paste(im, (x + 4, y + 49))
        native.save(output / "native224" / f"native-{start // 20 + 1:02}.png")
    md = ["# Thực hiện sau owner review", "", "29 crop đã review có receipt; crop mới từ nguồn "
          "đã approve cần kiểm đúng geometry/evidence. "
          "P/N/U theo phone/looking. Không split/train.",
          "", "## Bảng ảnh", ""]
    for sheet_path in sheets:
        md.extend([f"![Bảng ảnh]({sheet_path})", ""])
    for row in records:
        md.extend([f"## {row['sample_id']}", "", f"Nguồn: `{row['parent_item_id']}`; "
                   f"states `{'/'.join(row['states'])}`; component `{row['must_link_component']}`.",
                   "", f"![Panel](panels/{row['sample_id']}.png)", "", row["reason"], ""])
        if row["owner_feedback_verbatim"]:
            md.extend(["Phản hồi owner nguyên văn:", "", row["owner_feedback_verbatim"], ""])
        if row["attribution"]:
            a = row["attribution"]
            md.extend([f"Credit: {a.get('title')} — {a.get('artist')} — "
                       f"[{a.get('license')}]({a.get('license_url')}).", ""])
    (output / "REVIEW.md").write_text("\n".join(md), encoding="utf8")
    summary = {"status": "owner_directions_executed_review_only",
               "owner_input_items": len(decisions),
               "explicit_feedback": sum(bool(d.owner_feedback_verbatim) for d in decisions),
               "default_approve": sum(d.owner_feedback_verbatim is None for d in decisions),
               "existing_crop_approved": len(records) - len(plan["crops"]),
               "new_crop_proposals": len(plan["crops"]), "crop_records": len(records),
               "reserved_sources": len(plan["reserved_sources"]),
               "states": dict(Counter("/".join(r["states"]) for r in records)),
               "must_link_components": len(groups), "independent_groups_proven": 0,
               "label_updates": plan["label_updates"], "training_eligible": False,
               "official_split": None, "release_approved": False, "test_media_read": False,
               "html_files_created": 0}
    write_json(output / "summary.json", summary)
    for folder in [output, staging]:
        hashes = [f"{sha256_file(p)}  {p.relative_to(root).as_posix()}"
                  for p in sorted(folder.rglob("*")) if p.is_file()]
        (folder / "checksums.sha256").write_text("\n".join(hashes) + "\n", encoding="utf8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--workspace", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.workspace), ensure_ascii=False))


if __name__ == "__main__":
    main()
