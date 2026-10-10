"""Nhập approval đã pin và screening R8; không release/train/model holdout."""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import shutil
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .image_similarity import difference_hash
from .pilot_inputs import verify_pin
from .pilot_schema import PixelBox
from .pilot_targeted_expansion import TargetedHint, collect, lineage, nearest, validate_budget
from .targeted_review_package import _source
from .v7_input_evidence import letterbox_rgb


def pinned(root: Path, pin: dict[str, str]) -> Path:
    path = (root / pin["path"]).resolve()
    if not path.is_relative_to(root):
        raise DataContractError("Input pin thoát workspace")
    verify_pin(path, pin["sha256"])
    return path


def fresh(root: Path, relative: str, area: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root / area) or path.exists():
        raise DataContractError("Output phải mới trong area được phép")
    return path


def accept(config_path: Path, root: Path) -> dict[str, Any]:
    """Owner đã nói approve toàn bộ; unknown/evidence null không tự được điền."""
    root = root.resolve()
    config = load_yaml(config_path)
    pointer_path = pinned(root, config["approved_pointer"])
    pointer = json.loads(pointer_path.read_text(encoding="utf8"))
    proposals_path = pinned(root, pointer["review_proposals"])
    rows = [json.loads(line) for line in proposals_path.read_text(encoding="utf8").splitlines()]
    if len({r["sample_id"] for r in rows}) != len(rows) or not rows:
        raise DataContractError("Batch approved thiếu hoặc trùng ID")
    output = fresh(root, config["approval_output"], "artifacts/reports")
    decisions = []
    for row in rows:
        if row["training_eligible"] or row["split"] is not None:
            raise DataContractError("Review không còn preparation-only")
        decisions.append({
            "sample_id": row["sample_id"], "decision": "approve_final_crop_and_proposed_states",
            "approved_states": row["final_proposed_states"], "final_reason": row["final_reason"],
            "review_proposals_sha256": pointer["review_proposals"]["sha256"],
            "evidence": "owner-approval.json#" + row["sample_id"],
            "owner": "repository-owner", "reviewed_at": config["date"],
            "membership": "review_only" if row["final_proposed_states"] == ["U", "U"]
            else "conditional_pending_group_rights_usability_release_QA",
            "official_split": None, "training_eligible": False,
        })
    output.mkdir(parents=True)
    receipt = {
        "status": "owner_approved_review_and_conditional_execution",
        "date": config["date"], "owner": "repository-owner",
        "owner_message_verbatim": config["owner_message_verbatim"],
        "approved_pointer": config["approved_pointer"],
        "approved_proposals": pointer["review_proposals"], "approved_records": len(rows),
        "approved_policy": "Thực hiện các đề xuất R8 và constraints đã trình bày; "
                           "nghiệm thu crop/label/anchor R5, gồm U và các recrop.",
        "public_notices_decision": "Approve hồ sơ/credit đã review cho phạm vi nghiên cứu local "
                                  "hiện hành; 34 source images quarantine giữ nguyên.",
        "group_decision": "Approve conservative graph/proposal và split constraints; "
                          "không biến independence UNKNOWN thành đã chứng minh.",
        "r7_document_provenance": "Owner đã review/approve báo cáo có mismatch được công bố; "
                                  "acknowledge snapshot hiện hành, không xác định nguyên nhân.",
        "membership_split_decision": "Approve proposal có điều kiện; chưa có final assignment.",
        "r8_execution_authorized": True, "canonical_dataset_version": None,
        "training_executed": False, "holdout_model_executed": False,
        "release_materialized": False,
    }
    write_json(output / "owner-approval.json", receipt)
    (output / "accepted-r5-review-decisions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in decisions), encoding="utf8")
    return receipt


def select(hints: list[TargetedHint], previous: list[dict[str, Any]],
           limits: dict[str, dict[str, int]], distance_hint: int) -> tuple[
               list[TargetedHint], dict[str, Any]]:
    """Rank novel fingerprints; similarity chỉ quarantine hint, không independence gate."""
    validate_budget(distance_hint, "prior scene distance")
    if distance_hint > 64:
        raise DataContractError("Dhash distance vượt 64")
    used = {r["source_image_sha256"] for r in previous}
    old_names = {(r["source_id"], lineage(r["source_image_relpath"])) for r in previous
                 if r.get("source_image_relpath")}
    refs = [{"sha256": r["source_image_sha256"], "dhash": r["dhash"]} for r in previous]
    if not refs:
        raise DataContractError("Thiếu previous screening fingerprints")
    filtered = []
    exclusions: Counter[str] = Counter()
    nearest_old = {}
    for hint in hints:
        anchor = hint.anchor
        digest = anchor.source_image_sha256
        if digest in used or (anchor.source_id, lineage(anchor.source_image_relpath)) in old_names:
            exclusions["already_screened_sha_or_name_anchor_hints"] += 1
            continue
        if digest not in nearest_old:
            nearest_old[digest] = nearest(hint.dhash, refs)
        if nearest_old[digest]["distance"] <= distance_hint:
            exclusions["near_previous_screening_anchor_hints"] += 1
            continue
        filtered.append(hint)
    chosen = []
    for source, kinds in limits.items():
        for kind, limit in kinds.items():
            validate_budget(limit, "screening cap")
            pool = [h for h in filtered if h.anchor.source_id == source and h.kind == kind]
            pool.sort(key=lambda h: (
                -nearest_old[h.anchor.source_image_sha256]["distance"],
                -int(h.person_hint is not None), -h.body_count, h.anchor.rank_sha256))
            count = 0
            for hint in pool:
                digest = hint.anchor.source_image_sha256
                if digest in used or count >= limit:
                    continue
                chosen.append(hint)
                used.add(digest)
                count += 1
    return chosen, {"hint_exclusions": dict(exclusions),
                    "remaining_ranked_unique_sha": len({h.anchor.source_image_sha256
                                                        for h in filtered}),
                    "selected": len(chosen), "distance_is_not_independence": True}


def local(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    config = load_yaml(config_path)
    approval = json.loads(pinned(root, config["approval"]).read_text(encoding="utf8"))
    if not approval.get("r8_execution_authorized"):
        raise DataContractError("Thiếu approval R8")
    base = load_yaml(pinned(root, config["base_local_config"]))
    scb = load_yaml(pinned(root, config["base_scb_config"]))
    base["sources"] += scb["sources"]
    base["selection_version"] = config["selection_version"]
    output = fresh(root, config["output"], "data/interim")
    previous: list[dict[str, Any]] = []
    for pin in config["prior_screenings"]:
        previous.extend(json.loads(line) for line in pinned(root, pin).read_text(
            encoding="utf8").splitlines() if line)
    hints, statistics = collect(base, root)
    chosen, selection = select(hints, previous, config["source_screening_caps"],
                               config["near_prior_distance_hint"])
    output.mkdir(parents=True)
    (output / "review").mkdir()
    sources = {source["id"]: source for source in base["sources"]}
    rows = []
    font = ImageFont.load_default(size=16)
    for number, hint in enumerate(chosen, 1):
        anchor = hint.anchor
        source = sources[anchor.source_id]
        prefix = source.get("archive_prefix", "").strip("/")
        if not anchor.source_image_relpath.startswith(("train/", "images/train/")):
            raise DataContractError("R8 chỉ decode original train")
        with zipfile.ZipFile(source["archive"]) as archive:
            data = archive.read(f"{prefix}/{anchor.source_image_relpath}".lstrip("/"))
            labels = archive.read(f"{prefix}/{anchor.source_label_relpath}".lstrip("/"))
        if hashlib.sha256(data).hexdigest() != anchor.source_image_sha256:
            raise DataContractError("Source SHA lệch")
        if hashlib.sha256(labels).hexdigest() != anchor.source_label_sha256:
            raise DataContractError("Label SHA lệch")
        image = Image.open(io.BytesIO(data)).convert("RGB")
        if image.size != (anchor.width, anchor.height) or difference_hash(image) != hint.dhash:
            raise DataContractError("Source dimensions/fingerprint lệch")
        source_dir = output / "sources" / anchor.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        image_path = source_dir / f"{anchor.source_image_sha256}.jpg"
        label_path = source_dir / f"{anchor.source_image_sha256}.txt"
        image_path.write_bytes(data)
        label_path.write_bytes(labels)
        sid = f"V7-R8-SCREEN-{number:03d}"
        row = anchor.to_dict(sid)
        row.update({"source_local_image_path": image_path.relative_to(root).as_posix(),
                    "source_local_label_path": label_path.relative_to(root).as_posix(),
                    "source_root": source_dir.relative_to(root).as_posix(),
                    "hint_kind": hint.kind, "source_class_name": hint.class_name,
                    "source_classes": hint.source_classes, "body_count": hint.body_count,
                    "draft_xyxy": list(hint.context.xyxy), "dhash": hint.dhash,
                    "person_hint_xyxy": list(hint.person_hint.xyxy) if hint.person_hint else None,
                    "nearest_parent": hint.nearest_parent,
                    "nearest_evaluation": hint.nearest_evaluation,
                    "lineage_hint": lineage(anchor.source_image_relpath),
                    "status": "screening_only_pending_visual_review", "canonical_mask": [0, 0],
                    "canonical_targets": [None, None], "split": None,
                    "training_eligible": False, "independent_group_status": "UNPROVEN"})
        rows.append(row)
        drawn = image.copy()
        ImageDraw.Draw(drawn).rectangle(hint.context.xyxy, outline="red", width=3)
        panel = Image.new("RGB", (900, 590), "white")
        ImageDraw.Draw(panel).text((5, 5), f"{sid} {anchor.source_id} {hint.kind}",
                                  font=font, fill="black")
        panel.paste(ImageOps.contain(drawn, (550, 520)), (0, 65))
        panel.paste(ImageOps.contain(image.crop(hint.context.xyxy), (340, 520)), (558, 65))
        panel.save(output / "review" / f"{sid}.jpg")
    for start in range(0, len(rows), 6):
        sheet = Image.new("RGB", (2700, 1180), "white")
        for index, row in enumerate(rows[start:start + 6]):
            with Image.open(output / "review" / f"{row['sample_id']}.jpg") as panel:
                sheet.paste(panel, ((index % 3) * 900, (index // 3) * 590))
        sheet.save(output / "review" / f"sheet-{start // 6 + 1:03d}.jpg")
    (output / "screening.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n"
        for row in rows), encoding="utf8")
    statistics["r8_selection"] = selection
    write_json(output / "supply.json", statistics)
    summary = {"status": "screening_only_pending_visual_review", "records": len(rows),
               "by_source": dict(Counter(row["source_id"] for row in rows)),
               "screening_sha256": sha256_file(output / "screening.jsonl"),
               "config_sha256": sha256_file(config_path), "test_media_read": False,
               "model_executed": False, "training_eligible": False}
    write_json(output / "summary.json", summary)
    cards = "".join(f'<article><h2>{r["sample_id"]} {html.escape(r["source_id"])}</h2>'
                    f'<img src="{r["sample_id"]}.jpg"></article>' for r in rows)
    (output / "review/index.html").write_text('<!doctype html><meta charset="utf-8">'
        '<title>R8 screening</title><h1>Screening R8 — chưa nhãn/membership</h1>' + cards,
        encoding="utf8")
    return summary


def metadata(config_path: Path, root: Path) -> dict[str, Any]:
    """Nối prefix OI bằng range đã pin; raw version cũ bất biến, chưa exhaustive."""
    root = root.resolve()
    config = load_yaml(config_path)
    approval = json.loads(pinned(root, config["approval"]).read_text(encoding="utf8"))
    if not approval.get("r8_execution_authorized"):
        raise DataContractError("Thiếu approval R8")
    prefix = pinned(root, config["base_prefix"])
    url = config["url"]
    if url != "https://storage.googleapis.com/openimages/v6/oidv6-train-annotations-bbox.csv":
        raise DataContractError("Chỉ OI train metadata HTTPS đã xác định")
    extra = validate_budget(config["extra_bytes"], "metadata extra bytes", minimum=1)
    chunk = validate_budget(config["chunk_bytes"], "range chunk bytes", minimum=1)
    total = validate_budget(config["publisher_total_bytes"], "publisher total", minimum=1)
    start = prefix.stat().st_size
    if start + extra > total:
        raise DataContractError("Range vượt publisher size")
    output = fresh(root, config["output"], "data/raw")
    output.mkdir(parents=True)
    receipt: dict[str, Any] = {"status": "RUNNING", "base_prefix": config["base_prefix"],
                              "url": url, "range_parts": [], "full_inventory": False}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60) as res:
            etag = res.headers.get("ETag")
            if int(res.headers["Content-Length"]) != total or not etag:
                raise DataContractError("Publisher HEAD size/ETag chưa xác minh")
        receipt["publisher_etag"] = etag
        # Xác minh overlap cuối prefix để không nối nhầm payload/version.
        overlap_start = max(0, start - chunk)
        req = urllib.request.Request(url, headers={"Range": f"bytes={overlap_start}-{start-1}",
                                                   "If-Match": etag})
        with urllib.request.urlopen(req, timeout=60) as res:
            overlap = res.read(start - overlap_start + 1)
            if res.status != 206 or res.headers.get("Content-Range") != (
                f"bytes {overlap_start}-{start-1}/{total}"):
                raise DataContractError("Overlap HTTP Range không khớp")
        with prefix.open("rb") as stream:
            stream.seek(overlap_start)
            if stream.read() != overlap:
                raise DataContractError("Overlap publisher khác prefix cũ đã pin")
        receipt["overlap_bytes_verified"] = len(overlap)
        target = output / "bbox-train-prefix.csv"
        shutil.copyfile(prefix, target)
        with target.open("ab") as stream:
            for offset in range(start, start + extra, chunk):
                end = min(offset + chunk, start + extra) - 1
                req = urllib.request.Request(url, headers={"Range": f"bytes={offset}-{end}",
                                                           "If-Match": etag})
                with urllib.request.urlopen(req, timeout=60) as res:
                    data = res.read(end - offset + 2)
                    content_range = res.headers.get("Content-Range")
                    if (res.status != 206 or len(data) != end-offset+1
                            or content_range != f"bytes {offset}-{end}/{total}"
                            or res.headers.get("ETag") != etag):
                        raise DataContractError("Range byte count/ETag/Content-Range lệch")
                stream.write(data)
                receipt["range_parts"].append({"start": offset, "end": end,
                    "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
                print(f"OI metadata range {offset}-{end} received", flush=True)
        receipt.update(status="received_extended_prefix_pending_annotation_scan",
                       bytes=target.stat().st_size, sha256=sha256_file(target),
                       additional_bytes=extra,
                       coverage_bytes_fraction=target.stat().st_size / total,
                       note="Parser phải bỏ toàn image cuối; không coi prefix là exhaustive.")
    except Exception as error:
        receipt.update(status="FAILED_preserved_attempt", reason=str(error))
        write_json(output / "receipt.json", receipt)
        raise
    write_json(output / "receipt.json", receipt)
    return receipt


def validate_pairs(pairs: list[dict[str, Any]], rows: dict[str, dict[str, Any]]) -> None:
    """Same-image P/N phải đúng polarity và đúng source ở cả hai endpoint."""
    seen: set[str] = set()
    for pair in pairs:
        if pair["pair_id"] in seen or pair.get("owner_approved"):
            raise DataContractError("Pair trùng ID hoặc tự approve")
        seen.add(pair["pair_id"])
        target = {"phone_use": 0, "looking_around": 1}.get(pair["target"])
        positive, negative = pair["positive_id"], pair["negative_id"]
        if target is None or positive == negative or positive not in rows or negative not in rows:
            raise DataContractError("Pair target/endpoint không hợp lệ")
        pos, neg = rows[positive], rows[negative]
        if pos["states"][target] != "P" or neg["states"][target] != "N":
            raise DataContractError("Pair thiếu evidence P/N")
        if (pair["match_strength"] != "same_image"
                or pos["source_image_sha256"] != neg["source_image_sha256"]):
            raise DataContractError("Same-image pair khác source bytes")


def review_source(row: dict[str, Any], root: Path) -> Path:
    if row.get("source_original_split") != "unassigned_public_video":
        return Path(_source(row, root))
    if row.get("assigned_role") is not None or row.get("training_eligible") is not False:
        raise DataContractError("Public video đã assigned hoặc thiếu preparation-only guard")
    receipt = json.loads(pinned(root, row["video_receipt"]).read_text(encoding="utf8"))
    if (receipt["status"] != "received" or receipt["sha256"] != row["video_sha256"]
            or receipt["source_page"] != row["source_page"]):
        raise DataContractError("Public video source receipt lệch")
    relative = str(row["source_local_image_path"])
    path = (root / relative).resolve()
    if (not path.is_relative_to(root / "data/interim")
            or {"test", "val", "valid", "holdout"}.intersection(path.relative_to(root).parts)):
        raise DataContractError("Public frame không thuộc interim development proposal")
    verify_pin(path, row["source_image_sha256"])
    return path


def review(config_path: Path, root: Path) -> dict[str, Any]:
    """R8 labels là Draft mới; không dùng approval R5 để duyệt crop tương lai."""
    root = root.resolve()
    config = load_yaml(config_path)
    selection = json.loads(pinned(root, config["selection"]).read_text(encoding="utf8"))
    registry: dict[tuple[str, str], dict[str, Any]] = {}
    for group, pin in config["screenings"].items():
        rows = [json.loads(line) for line in pinned(root, pin).read_text(
            encoding="utf8").splitlines() if line]
        registry.update({(group, row["sample_id"]): row for row in rows})
    transform = load_yaml(pinned(root, config["preprocessing"]))
    if transform["transform"] != "rgb_letterbox_bilinear_v1" or transform["image_size"] != 224:
        raise DataContractError("Không đổi preprocessing E003")
    proposals = selection["proposals"]
    if len({item["sample_id"] for item in proposals}) != len(proposals):
        raise DataContractError("Trùng proposal ID")
    for item in proposals:
        if re.fullmatch(r"V7-R8-[A-D]-\d{3}", item["sample_id"]) is None:
            raise DataContractError("ID R8 không an toàn")
        if (len(item["states"]) != 2 or any(s not in {"P", "N", "U"} for s in item["states"])
                or item.get("known_evaluation_family") or not item["reason"]):
            raise DataContractError("Target/evidence/evaluation-family không hợp lệ")
        source = registry[(item["screening_set"], item["screening_id"])]
        if source.get("attribution") and not item.get("source_title"):
            raise DataContractError("Public source thiếu tên tác phẩm trong credit")
        review_source(source, root)
        box = PixelBox(*item["xyxy"])
        if box.xmax > source["width"] or box.ymax > source["height"]:
            raise DataContractError("Crop thoát source")
    endpoints = {item["sample_id"]: {**item, "source_image_sha256":
        registry[(item["screening_set"], item["screening_id"])]["source_image_sha256"]}
        for item in proposals}
    if config.get("approved_external_review"):
        approval = json.loads(pinned(root, config["approval"]).read_text(encoding="utf8"))
        external_pin = config["approved_external_review"]
        if external_pin != approval["approved_proposals"]:
            raise DataContractError("External endpoint không thuộc batch owner đã approve")
        for line in pinned(root, external_pin).read_text(encoding="utf8").splitlines():
            row = json.loads(line)
            if row["sample_id"] in endpoints:
                raise DataContractError("R8 ID trùng external approved ID")
            endpoints[row["sample_id"]] = {"states": row["final_proposed_states"],
                "source_image_sha256": row["source_sha256"]}
    validate_pairs(selection["pairs"], endpoints)
    output = fresh(root, config["output"], "outputs")
    output.mkdir(parents=True)
    (output / "media").mkdir()
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
    records, cards = [], []
    for item in proposals:
        sid = item["sample_id"]
        source = registry[(item["screening_set"], item["screening_id"])]
        original = review_source(source, root)
        with Image.open(original) as decoded:
            image = decoded.convert("RGB")
        if image.size != (source["width"], source["height"]):
            raise DataContractError("Source size thay đổi")
        crop = image.crop(tuple(item["xyxy"]))
        fill = transform["fill"]
        native = letterbox_rgb(crop, 224, (fill[0], fill[1], fill[2]))
        marked = image.copy()
        ImageDraw.Draw(marked).rectangle(item["xyxy"], outline="red", width=3)
        media = {}
        for suffix, asset in [("source", marked), ("crop", crop), ("input224", native)]:
            path = output / "media" / f"{sid}-{suffix}.png"
            asset.save(path)
            media[suffix] = {"path": path.relative_to(root).as_posix(),
                             "sha256": sha256_file(path)}
        record = {**item, "source_id": source["source_id"],
                  "bucket": item["sample_id"].split("-")[2],
                  "final_proposed_states": item["states"], "final_reason": item["reason"],
                  "source_image_sha256": source["source_image_sha256"],
                  "source_image_relpath": source.get("source_image_relpath"),
                  "source_original_path": original.relative_to(root).as_posix(),
                  "source_pixel_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
                  "attribution": source.get("attribution"),
                  "source_page": source.get("source_page"),
                  "video_sha256": source.get("video_sha256"),
                  "timestamp_seconds": source.get("timestamp_seconds"),
                  "media": media, "owner_approved": False, "canonical_targets": [None, None],
                  "canonical_mask": [0, 0], "split": None, "training_eligible": False,
                  "new_independent_group_gain": 0,
                  "group_status": "proposal_owner_pending_not_independence_proof"}
        records.append(record)
        panel = Image.new("RGB", (1600, 800), "white")
        ImageDraw.Draw(panel).text((10, 6), f"{sid} {'/'.join(item['states'])} Draft", font=font,
                                  fill="black")
        panel.paste(ImageOps.contain(marked, (660, 700)), (0, 70))
        panel.paste(ImageOps.contain(crop, (420, 700)), (680, 70))
        panel.paste(native, (1120, 70))
        panel.paste(native.resize((448, 448), Image.Resampling.NEAREST), (1120, 310))
        panel.save(output / f"{sid}.png")
        images = "".join(f'<figure><figcaption>{name}</figcaption><img class="{name}" '
                         f'src="media/{sid}-{name}.png"></figure>'
                         for name in ["source", "crop", "input224"])
        credit = source.get("attribution")
        credit_html = (f'<p>Nguồn: <a href="{html.escape(source["source_page"])}">'
                       f'{html.escape(item["source_title"])}</a>; '
                       f'{html.escape(credit["artist"])}; '
                       f'<a href="{html.escape(credit["license_url"])}">'
                       f'{html.escape(credit["license"])}</a>. '
                       'Thay đổi: trích frame, đánh dấu bbox, crop và letterbox224.</p>'
                       if credit else '')
        cards.append(f'<article id="{sid}"><h2>{sid} {"/".join(item["states"])}</h2>'
                     f'<p>{html.escape(item["reason"])}</p><p>Anchor: '
                     f'{html.escape(item["person_unit_hint"])}</p><div class="images">'
                     f'{images}</div><p>Group proposal: {html.escape(item["visual_family_hint"])}; '
                     f'chưa split/training.</p>{credit_html}</article>')
    (output / "review-proposals.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False)
        + "\n" for row in records), encoding="utf8")
    (output / "review-index.html").write_text(
        '<!doctype html><html lang="vi"><meta charset="utf-8">'
        '<title>R8 owner review</title>'
        '<style>body{font-family:system-ui;max-width:1550px;margin:auto}'
        '.images{display:flex;gap:15px}figure{flex:1;margin:0}img{max-width:100%;max-height:650px}'
        'img.input224{width:224px;height:224px;max-width:none}</style>'
        '<h1>Crop mới R8 — Draft, chưa được approval R5 bao phủ</h1>' + "".join(cards)
        + '<h2>Matched pairs</h2><ul>' + ''.join(
            f'<li>{html.escape(p["pair_id"])}: {html.escape(p["positive_id"])} / '
            f'{html.escape(p["negative_id"])} — {html.escape(p["target"])}; same image</li>'
            for p in selection["pairs"]) + '</ul></html>',
        encoding="utf8")
    write_json(output / "pairs.json", selection["pairs"])
    summary = {"status": "draft_pending_owner_review", "records": len(records),
               "fully_known": sum("U" not in row["states"] for row in records),
               "combinations": dict(Counter("".join(row["states"]) for row in records)),
               "by_source": dict(Counter(row["source_id"] for row in records)),
               "pairs": len(selection["pairs"]), "new_independent_group_gain": 0,
               "training_eligible": False, "test_media_read": False, "model_executed": False,
               "config_sha256": sha256_file(config_path)}
    write_json(output / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["accept", "local", "metadata", "review"])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    commands = {"accept": accept, "local": local, "metadata": metadata, "review": review}
    result = commands[args.command](args.config, args.workspace)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
