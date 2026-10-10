"""Audit subset original train Open Images; nguồn/nhãn/group chưa được nghiệm thu."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .image_similarity import difference_hash
from .pilot_inputs import verify_pin
from .pilot_schema import PixelBox
from .pilot_targeted_expansion import nearest, validate_budget, validate_fingerprints


def inventory(prefix: Path, classes: Path, config: dict[str, Any]) -> tuple[
    dict[str, list[dict[str, Any]]], dict[str, Any]
]:
    """Loại toàn image cuối của prefix, không suy label nguồn thiếu thành N."""
    with classes.open(encoding="utf8", newline="") as stream:
        names = dict(csv.reader(stream))
    wanted = set(config["person_classes"] + config["context_classes"] + [config["phone_class"]])
    objects: dict[str, list[dict[str, Any]]] = defaultdict(list)
    counts: Counter[str] = Counter()
    last, bad = None, 0
    with prefix.open(encoding="utf8", newline="") as stream:
        for raw in csv.DictReader(stream):
            last = raw["ImageID"]
            if any(raw.get(k) is None for k in ("XMin", "XMax", "YMin", "YMax", "IsInside")):
                bad += 1
                continue
            name = names[raw["LabelName"]]
            if name not in wanted or raw["IsDepiction"] != "0" or raw["IsGroupOf"] != "0":
                continue
            xmin, xmax, ymin, ymax = (float(raw[k]) for k in ("XMin", "XMax", "YMin", "YMax"))
            if (not all(math.isfinite(v) for v in (xmin, xmax, ymin, ymax))
                    or not 0 <= xmin < xmax <= 1 or not 0 <= ymin < ymax <= 1):
                raise DataContractError("BBox Open Images vượt [0,1] hoặc zero-area")
            row = {**raw, "class_name": name, "normalized_xyxy": [xmin, ymin, xmax, ymax]}
            objects[raw["ImageID"]].append(row)
            counts[name] += 1
    if last is not None:
        objects.pop(last, None)
    return dict(objects), {"counts": dict(counts), "excluded_last_image_id": last,
                           "incomplete_tail_rows": bad, "complete_source_inventory": False}


def shortlisted(objects: dict[str, list[dict[str, Any]]],
                metadata: Path, config: dict[str, Any],
                excluded: set[str] | None = None) -> list[dict[str, Any]]:
    for kind, budget in config["screening_budgets"].items():
        validate_budget(budget, f"screening budget {kind}")
    hints = []
    seen: set[str] = set()
    with metadata.open(encoding="utf8", newline="") as stream:
        for info in csv.DictReader(stream):
            rows = objects.get(info["ImageID"])
            if rows:
                if info["ImageID"] in seen:
                    raise DataContractError("Open Images metadata ImageID trùng")
                seen.add(info["ImageID"])
            if (not rows or info["Subset"] != "train"
                    or info["ImageID"] in (excluded or set())
                    or info["Rotation"] not in config["allowed_rotations"]
                    or info["License"] not in config["allowed_license_urls"]):
                continue
            people = [r for r in rows if r["class_name"] in config["person_classes"]]
            phones = [r for r in rows if r["class_name"] == config["phone_class"]]
            work = [r for r in rows if r["class_name"] in config["work_classes"]]
            tables = [r for r in rows if r["class_name"] in config["table_classes"]]
            title_hint = any(word.casefold() in info.get("Title", "").casefold()
                             for word in config.get("phone_title_keywords", []))
            if not people and not (phones and title_hint):
                continue
            rank = hashlib.sha256((config["selection_version"] + info["ImageID"]).encode()
                                  ).hexdigest()
            if phones:
                phone = min(phones, key=lambda r: (r["normalized_xyxy"][2] -
                    r["normalized_xyxy"][0]) * (r["normalized_xyxy"][3] -
                                                r["normalized_xyxy"][1]))
                x1, y1, x2, y2 = phone["normalized_xyxy"]
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                table_hint = any(t["normalized_xyxy"][0] <= cx <= t["normalized_xyxy"][2]
                                 and t["normalized_xyxy"][1] <= cy <= t["normalized_xyxy"][3]
                                 for t in tables)
                score = (int(bool(work)) * config["work_rank_weight"] +
                         int(table_hint) * config["table_rank_weight"])
                kind = "desk_context_hint" if table_hint and work else "held_partial_phone_hint"
                if kind == "held_partial_phone_hint":
                    score += int(phone["IsOccluded"] == "1" or phone["IsTruncated"] == "1")
                if title_hint and config.get("phone_title_keywords"):
                    kind = "title_phone_context_hint"
            elif work:
                phone, score, kind = None, 0, "work_without_phone_annotation_hint"
                score = max(config.get("work_hint_rank_weights", {}).get(r["class_name"], 0)
                            for r in work)
            else:
                continue
            hints.append({"image_metadata": info, "objects": rows, "people": people,
                          "phone_hint": phone, "rank": rank, "score_hint": score, "kind": kind})
    result = []
    for kind, budget in config["screening_budgets"].items():
        ranked = sorted((r for r in hints if r["kind"] == kind),
                        key=lambda r: (-r["score_hint"], r["rank"]))
        result.extend(ranked[:budget])
    return result


def pixel_box(row: dict[str, Any], width: int, height: int) -> PixelBox:
    x1, y1, x2, y2 = row["normalized_xyxy"]
    return PixelBox(math.floor(x1 * width), math.floor(y1 * height),
                    math.ceil(x2 * width), math.ceil(y2 * height))


def build(config_path: Path, workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    config = load_yaml(config_path)
    if config["status"] != "draft_public_source_audit":
        raise DataContractError("Không phải source audit Draft")
    validate_budget(config["max_image_bytes"], "max_image_bytes", minimum=1)
    for kind, budget in config["screening_budgets"].items():
        validate_budget(budget, f"screening budget {kind}")
    if validate_budget(config["quarantine_distance_hint"], "quarantine_distance_hint") > 64:
        raise DataContractError("Quarantine distance vượt 64-bit dhash")
    if config["image_endpoint"] != "https://open-images-dataset.s3.amazonaws.com/train":
        raise DataContractError("Open Images source audit chỉ tải endpoint HTTPS original train")
    for key in ("bbox_prefix", "classes", "image_metadata", "scope_approval",
                "parent_fingerprints"):
        pin = config[key]
        verify_pin(workspace / pin["path"], pin["sha256"])
    scope = json.loads((workspace / config["scope_approval"]["path"]).read_text(encoding="utf8"))
    if scope["decision"] != "continue_public_training_source_audit":
        raise DataContractError("Thiếu scope owner audit public")
    raw, output = ((workspace / config[key]).resolve() for key in ("raw_output", "output"))
    if (not raw.is_relative_to(workspace / "data/raw") or raw.exists()
            or not output.is_relative_to(workspace / "data/interim") or output.exists()):
        raise DataContractError("Raw/interim phải là version mới")
    objects, stats = inventory(workspace / config["bbox_prefix"]["path"],
                               workspace / config["classes"]["path"], config)
    excluded: set[str] = set()
    for pin in config.get("exclude_screenings", []):
        path = workspace / pin["path"]
        verify_pin(path, pin["sha256"])
        excluded.update(json.loads(line)["source_image_id"]
                        for line in path.read_text(encoding="utf8").splitlines())
    selected = shortlisted(objects, workspace / config["image_metadata"]["path"], config,
                           excluded)
    del objects
    reference_path = workspace / config["parent_fingerprints"]["path"]
    refs = json.loads(reference_path.read_text(encoding="utf8"))
    evaluation = validate_fingerprints(refs)
    parent_sha = {r["sha256"] for r in refs}
    for candidate in selected:
        image_id = candidate["image_metadata"]["ImageID"]
        if len(image_id) != 16 or any(c not in "0123456789abcdef" for c in image_id):
            raise DataContractError("Open Images ID không hợp lệ")
    raw.mkdir(parents=True)
    output.mkdir(parents=True)
    for directory in ("crops", "review"):
        (output / directory).mkdir()
    rows, failures, quarantine = [], [], []
    font = ImageFont.load_default(size=16)
    for index, candidate in enumerate(selected, 1):
        info = candidate["image_metadata"]
        image_id = info["ImageID"]
        if len(image_id) != 16 or any(c not in "0123456789abcdef" for c in image_id):
            raise DataContractError("Open Images ID không hợp lệ")
        url = config["image_endpoint"] + "/" + image_id + ".jpg"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read(config["max_image_bytes"] + 1)
                etag = response.headers.get("ETag", "").strip('"')
                content_length = response.headers.get("Content-Length")
            if len(content) > config["max_image_bytes"]:
                raise DataContractError("Vượt image byte budget")
            if content_length is not None and int(content_length) != len(content):
                raise DataContractError("Image thiếu bytes so Content-Length")
            if len(etag) == 32 and hashlib.md5(content).hexdigest() != etag:
                raise DataContractError("Image server MD5 lệch")
            digest = hashlib.sha256(content).hexdigest()
            if digest in parent_sha:
                reference = next(r for r in refs if r["sha256"] == digest)
                (raw / (image_id + ".jpg")).write_bytes(content)
                quarantine.append({"image_id": image_id, "source_sha256": digest,
                    "nearest_evaluation": nearest(reference["dhash"], evaluation),
                    "reason": "exact_parent_sha_before_decode", "media_decoded": False})
                continue
            with Image.open(io.BytesIO(content)) as decoded:
                image = decoded.convert("RGB")
        except Exception as error:
            failures.append({"image_id": image_id, "url": url, "reason": str(error)})
            continue
        source_path = raw / (image_id + ".jpg")
        source_path.write_bytes(content)
        fingerprint = difference_hash(image)
        near_eval = nearest(fingerprint, evaluation)
        if near_eval["distance"] <= config["quarantine_distance_hint"]:
            quarantine.append({"image_id": image_id, "source_sha256": digest,
                               "nearest_evaluation": near_eval})
            continue
        people = candidate["people"]
        phone = candidate["phone_hint"]
        person = max(people, key=lambda r: (r["normalized_xyxy"][2] -
            r["normalized_xyxy"][0]) * (r["normalized_xyxy"][3] - r["normalized_xyxy"][1])) \
            if people else None
        person_box = pixel_box(person, *image.size) if person else PixelBox(
            0, 0, image.width, image.height)
        context = person_box
        if phone:
            phone_box = pixel_box(phone, *image.size)
            context = PixelBox(min(context.xmin, phone_box.xmin), min(context.ymin, phone_box.ymin),
                               max(context.xmax, phone_box.xmax), max(context.ymax, phone_box.ymax))
        sid = f"V7-OI-SCREEN-{index:03d}"
        crop = image.crop(context.xyxy)
        crop_path = output / "crops" / (sid + ".png")
        crop.save(crop_path)
        row = {"sample_id": sid, "source_id": "openimages_train_prefix",
               "source_image_id": image_id, "source_image_relpath": "images/train/" +
               image_id + ".jpg", "source_local_image_path": source_path
               .relative_to(workspace).as_posix(), "source_image_sha256": digest,
               "source_original_split": "train", "source_url": url,
               "source_rights_status": "public_pending_attribution_and_owner_review",
               "attribution_metadata": info, "rotation_applied": 0,
               "license_status": "provider_metadata_pending_individual_verification",
               "kind": candidate["kind"], "score_hint": candidate["score_hint"],
               "person_annotation_hint": person, "phone_annotation_hint": phone,
               "object_annotations": candidate["objects"], "width": image.width,
               "height": image.height, "dhash": fingerprint,
               "draft_xyxy": list(context.xyxy), "crop_path": crop_path
               .relative_to(workspace).as_posix(), "crop_sha256": sha256_file(crop_path),
               "nearest_parent": nearest(fingerprint, refs), "nearest_evaluation": near_eval,
               "canonical_targets": [None, None], "canonical_mask": [0, 0],
               "split": None, "leakage_group_id": None, "training_eligible": False,
               "status": "draft_public_source_audit", "domain": "auxiliary_pending_visual_review",
               "note": "Object/geometry/title chỉ hint; thiếu person bbox dùng full image, "
               "largest person không chứng minh ownership, "
               "thiếu annotation không N, metadata license chưa phê duyệt source."}
        rows.append(row)
        drawn = image.copy()
        draw = ImageDraw.Draw(drawn)
        draw.rectangle(person_box.xyxy, outline="red", width=3)
        if phone:
            draw.rectangle(pixel_box(phone, *image.size).xyxy, outline="cyan", width=3)
        panel = Image.new("RGB", (900, 590), "white")
        ImageDraw.Draw(panel).text((5, 5), f"{sid} {candidate['kind']} | " + image_id,
                                  font=font, fill="black")
        panel.paste(ImageOps.contain(drawn, (550, 520)), (0, 65))
        panel.paste(ImageOps.contain(crop, (340, 520)), (558, 65))
        panel.save(output / "review" / (sid + ".jpg"))
        if index % 20 == 0:
            print(f"Open Images {index}/{len(selected)}", flush=True)
    for start in range(0, len(rows), 6):
        sheet = Image.new("RGB", (2700, 1180), "white")
        for index, row in enumerate(rows[start:start + 6]):
            with Image.open(output / "review" / (row["sample_id"] + ".jpg")) as panel:
                sheet.paste(panel, ((index % 3) * 900, (index // 3) * 590))
        sheet.save(output / "review" / f"sheet-{start // 6 + 1:03d}.jpg")
    (output / "screening.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False,
        sort_keys=True)
        + "\n" for r in rows), encoding="utf8")
    summary = {"status": "draft_public_source_audit", "screening_records": len(rows),
               "screening_budgets": config["screening_budgets"], "supply": stats,
               "failures": failures, "quarantine": quarantine, "test_media_read": False,
               "training_eligible": False, "complete_source_inventory": False,
               "config_sha256": sha256_file(config_path)}
    write_json(output / "summary.json", summary)
    write_json(raw / "receipt.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.workspace), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
