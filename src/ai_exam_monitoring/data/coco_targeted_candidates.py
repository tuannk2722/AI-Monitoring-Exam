"""Audit subset COCO train để review desk/phone; nhãn dự án vẫn unknown."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import urllib.request
import zipfile
from collections import defaultdict
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


def bbox(annotation: dict[str, Any], width: int, height: int) -> PixelBox:
    x, y, w, h = annotation["bbox"]
    if any(not math.isfinite(v) for v in (x, y, w, h)) or w <= 0 or h <= 0:
        raise DataContractError("COCO bbox không hợp lệ")
    if not math.isfinite(x + w) or not math.isfinite(y + h):
        raise DataContractError("COCO bbox overflow")
    # Proposal clip phải được công bố, không thay annotation raw.
    return PixelBox(max(0, math.floor(x)), max(0, math.floor(y)),
                    min(width, math.ceil(x + w)), min(height, math.ceil(y + h)))


def inside(box: list[float], x: float, y: float) -> bool:
    return box[0] <= x <= box[0] + box[2] and box[1] <= y <= box[1] + box[3]


def shortlist(annotations: dict[str, Any], captions: dict[int, str],
              config: dict[str, Any], excluded: set[int] | None = None
              ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    for name in ("phone_context_budget", "negative_context_budget"):
        validate_budget(config[name], name)
    names = {a["id"]: a["name"] for a in annotations["categories"]}
    licenses = {a["id"]: a for a in annotations["licenses"]}
    objects: dict[int, list[dict[str, Any]]] = defaultdict(list)
    wanted = {"person", "cell phone", "dining table", "laptop", "book", "keyboard"}
    for row in annotations["annotations"]:
        if names[row["category_id"]] in wanted and not row["iscrowd"]:
            objects[row["image_id"]].append(row)
    positives, negatives = [], []
    stats = {"train_images": len(annotations["images"]), "eligible_phone_context": 0,
             "desk_geometry_hints": 0, "read_work_negative_hints": 0}
    for image in annotations["images"]:
        if image["id"] in (excluded or set()):
            continue
        license_row = licenses[image["license"]]
        if license_row["url"] not in config["allowed_license_urls"]:
            continue
        rows = objects[image["id"]]
        people = [a for a in rows if names[a["category_id"]] == "person"]
        phones = [a for a in rows if names[a["category_id"]] == "cell phone"]
        context = [a for a in rows if names[a["category_id"]] in wanted - {"person", "cell phone"}]
        if not people or not context:
            continue
        work_text = any(w in captions.get(image["id"], "") for w in config["work_keywords"])
        rank = hashlib.sha256((config["selection_version"] + "|" +
                               str(image["id"])).encode()).hexdigest()
        if phones:
            stats["eligible_phone_context"] += 1
            scored = []
            for phone in phones:
                x, y, width, height = phone["bbox"]
                if (any(not math.isfinite(v) for v in (x, y, width, height))
                        or width <= 0 or height <= 0):
                    raise DataContractError("Phone annotation COCO không hợp lệ")
                center = x + width / 2, y + height / 2
                on_table_hint = any(inside(a["bbox"], *center) for a in context
                                    if names[a["category_id"]] == "dining table")
                horizontal_hint = width / height >= config["horizontal_ratio_hint"]
                scored.append((int(on_table_hint) + int(horizontal_hint) + int(work_text),
                               width * height, phone))
            score, _, phone = max(scored, key=lambda r: (r[0], r[1], -r[2]["id"]))
            if score >= config["minimum_context_score_hint"]:
                stats["desk_geometry_hints"] += 1
                positives.append({"image": image, "objects": rows, "phone_hint": phone,
                                  "context_score_hint": score, "rank": rank,
                                  "license": license_row, "kind": "phone_context_hint"})
        elif work_text:
            stats["read_work_negative_hints"] += 1
            negatives.append({"image": image, "objects": rows, "phone_hint": None,
                              "context_score_hint": 0, "rank": rank, "license": license_row,
                              "kind": "no_phone_annotation_work_hint"})
    positives.sort(key=lambda r: (-r["context_score_hint"], r["rank"]))
    negatives.sort(key=lambda r: r["rank"])
    return (positives[:config["phone_context_budget"]] +
            negatives[:config["negative_context_budget"]]), stats


def build(config_path: Path, workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    config = load_yaml(config_path)
    if config["status"] != "draft_public_source_audit":
        raise DataContractError("Không phải release/train config")
    validate_budget(config["max_image_bytes"], "max_image_bytes", minimum=1)
    for name in ("phone_context_budget", "negative_context_budget"):
        validate_budget(config[name], name)
    if validate_budget(config["quarantine_distance_hint"], "quarantine_distance_hint") > 64:
        raise DataContractError("Quarantine distance vượt 64-bit dhash")
    if config["image_endpoint"] != "https://s3.amazonaws.com/images.cocodataset.org/train2017":
        raise DataContractError("COCO source audit chỉ tải endpoint HTTPS original train2017")
    for key in ("metadata", "scope_approval", "parent_fingerprints"):
        pin = config[key]
        verify_pin(workspace / pin["path"], pin["sha256"])
    scope = json.loads((workspace / config["scope_approval"]["path"]).read_text(encoding="utf8"))
    if scope["decision"] != "continue_public_training_source_audit":
        raise DataContractError("Thiếu chỉ thị owner thẩm định nguồn public")
    raw = (workspace / config["raw_output"]).resolve()
    output = (workspace / config["output"]).resolve()
    if (not raw.is_relative_to(workspace / "data/raw") or raw.exists()
            or not output.is_relative_to(workspace / "data/interim") or output.exists()):
        raise DataContractError("Raw và interim phải là version mới, không ghi đè")
    with zipfile.ZipFile(workspace / config["metadata"]["path"]) as archive:
        annotations = json.loads(archive.read("annotations/instances_train2017.json"))
        caption_data = json.loads(archive.read("annotations/captions_train2017.json"))
    captions: dict[int, str] = defaultdict(str)
    for row in caption_data["annotations"]:
        captions[row["image_id"]] += " " + row["caption"].lower()
    previous: set[int] = set()
    if config.get("exclude_screening"):
        pin = config["exclude_screening"]
        path = workspace / pin["path"]
        verify_pin(path, pin["sha256"])
        previous = {json.loads(line)["source_image_id"] for line in
                    path.read_text(encoding="utf8").splitlines()}
    selected, stats = shortlist(annotations, captions, config, previous)
    stats["excluded_previously_screened_images"] = len(previous)
    category_ids = {a["name"]: a["id"] for a in annotations["categories"]}
    del annotations, caption_data, captions
    reference_path = workspace / config["parent_fingerprints"]["path"]
    refs = json.loads(reference_path.read_text(encoding="utf8"))
    evaluation = validate_fingerprints(refs)
    parent_sha = {r["sha256"] for r in refs}
    filenames: set[str] = set()
    for candidate in selected:
        info = candidate["image"]
        filename = info["file_name"]
        if (type(info["id"]) is not int or info["id"] < 0
                or filename != f"{info['id']:012d}.jpg" or filename in filenames):
            raise DataContractError("COCO filename/identity không hợp lệ hoặc trùng")
        filenames.add(filename)
    raw.mkdir(parents=True)
    output.mkdir(parents=True)
    (output / "review").mkdir()
    (output / "crops").mkdir()
    font = ImageFont.load_default(size=16)
    rows, failures, quarantine = [], [], []
    for count, candidate in enumerate(selected, 1):
        info = candidate["image"]
        filename = info["file_name"]
        if Path(filename).name != filename or not filename.endswith(".jpg"):
            raise DataContractError("COCO filename không an toàn")
        url = config["image_endpoint"] + "/" + filename
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read(config["max_image_bytes"] + 1)
                etag = response.headers.get("ETag", "").strip('"')
                content_length = response.headers.get("Content-Length")
            if len(content) > config["max_image_bytes"]:
                raise DataContractError("Ảnh vượt byte budget")
            if content_length is not None and int(content_length) != len(content):
                raise DataContractError("Ảnh thiếu bytes so Content-Length")
            if len(etag) == 32 and hashlib.md5(content).hexdigest() != etag:
                raise DataContractError("Ảnh lệch server MD5")
            digest = hashlib.sha256(content).hexdigest()
            if digest in parent_sha:
                reference = next(r for r in refs if r["sha256"] == digest)
                (raw / filename).write_bytes(content)
                quarantine.append({"image_id": info["id"], "sha256": digest,
                    "nearest_evaluation": nearest(reference["dhash"], evaluation),
                    "reason": "exact_parent_sha_before_decode", "media_decoded": False})
                continue
            image = Image.open(io.BytesIO(content)).convert("RGB")
            if image.size != (info["width"], info["height"]):
                raise DataContractError("Ảnh lệch metadata dimension")
        except Exception as error:
            failures.append({"image_id": info["id"], "url": url, "reason": str(error)})
            continue
        image_path = raw / filename
        image_path.write_bytes(content)
        fingerprint = difference_hash(image)
        near_eval = nearest(fingerprint, evaluation)
        if near_eval["distance"] <= config["quarantine_distance_hint"]:
            quarantine.append({"image_id": info["id"], "sha256": digest,
                               "nearest_evaluation": near_eval})
            continue
        people = [a for a in candidate["objects"]
                  if a["category_id"] == category_ids["person"]]
        phone = candidate["phone_hint"]
        # Crop lớn đủ ngữ cảnh khi association chưa chốt; không gán phone nearest-person.
        person = max(people, key=lambda a: a["bbox"][2] * a["bbox"][3])
        person_box = bbox(person, *image.size)
        context = person_box
        if phone:
            phone_box = bbox(phone, *image.size)
            context = PixelBox(min(context.xmin, phone_box.xmin), min(context.ymin, phone_box.ymin),
                               max(context.xmax, phone_box.xmax), max(context.ymax, phone_box.ymax))
        sample_id = f"V7-COCO-SCREEN-{count:03d}"
        crop = image.crop(context.xyxy)
        crop_path = output / "crops" / f"{sample_id}.png"
        crop.save(crop_path)
        row = {"sample_id": sample_id, "source_id": "coco_2017_train",
               "source_image_id": info["id"], "source_image_path": image_path
               .relative_to(workspace).as_posix(), "source_image_sha256": digest,
               "source_original_split": "train2017", "width": image.width, "height": image.height,
               "source_url": url, "flickr_url": info.get("flickr_url"),
               "license": candidate["license"],
               "license_status": "provider_metadata_pending_review",
               "kind": candidate["kind"], "context_score_hint": candidate["context_score_hint"],
               "person_annotation": person, "phone_annotation_hint": phone,
               "object_annotations": candidate["objects"], "dhash": fingerprint,
               "nearest_parent": nearest(fingerprint, refs), "nearest_evaluation": near_eval,
               "draft_xyxy": list(context.xyxy), "crop_path": crop_path
               .relative_to(workspace).as_posix(), "crop_sha256": sha256_file(crop_path),
               "canonical_targets": [None, None], "canonical_mask": [0, 0], "split": None,
               "training_eligible": False, "status": "draft_public_source_audit",
               "domain": "auxiliary_out_of_exam_pending_review",
               "note": "Object labels/geometry chỉ hint; không phone attribution, "
               "không suy thiếu box là N; metadata license không là source release approval."}
        rows.append(row)
        drawn = image.copy()
        draw = ImageDraw.Draw(drawn)
        draw.rectangle(person_box.xyxy, outline="red", width=3)
        if phone:
            draw.rectangle(bbox(phone, *image.size).xyxy, outline="cyan", width=3)
        panel = Image.new("RGB", (900, 590), "white")
        ImageDraw.Draw(panel).text((5, 5), f"{sample_id} {candidate['kind']} | COCO "
                                  f"{info['id']} | CC metadata", font=font, fill="black")
        panel.paste(ImageOps.contain(drawn, (550, 520)), (0, 65))
        panel.paste(ImageOps.contain(crop, (340, 520)), (558, 65))
        panel.save(output / "review" / f"{sample_id}.jpg")
        if count % 20 == 0:
            print(f"COCO audit {count}/{len(selected)}", flush=True)
    for start in range(0, len(rows), 6):
        sheet = Image.new("RGB", (2700, 1180), "white")
        for index, row in enumerate(rows[start:start + 6]):
            with Image.open(output / "review" / f"{row['sample_id']}.jpg") as panel:
                sheet.paste(panel, ((index % 3) * 900, (index // 3) * 590))
        sheet.save(output / "review" / f"sheet-{start // 6 + 1:03d}.jpg")
    (output / "screening.jsonl").write_text("".join(
        json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf8")
    receipt = {"status": "draft_public_source_audit", "downloaded_images": len(rows)
               + len(quarantine), "screening_records": len(rows), "supply": stats,
               "failures": failures, "quarantine": quarantine,
               "config_sha256": sha256_file(config_path), "test_media_read": False,
               "metadata_license_does_not_approve_source": True, "training_eligible": False}
    write_json(raw / "receipt.json", receipt)
    write_json(output / "summary.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.workspace), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
