"""Research ảnh public classroom có pin/licensing; chỉ tạo screening và proposal."""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
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
from .pilot_targeted_expansion import nearest
from .v7_input_evidence import letterbox_rgb
from .v7_r8_execution import fresh, pinned, validate_pairs


def plain(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def request(url: str, max_bytes: int) -> tuple[bytes, dict[str, Any]]:
    if urllib.parse.urlsplit(url).scheme != "https":
        raise DataContractError("Chỉ tiếp nhận HTTPS public")
    req = urllib.request.Request(url, headers={
        "User-Agent": "ClassroomDatasetResearch/1.0 (local finite metadata/media audit)"})
    with urllib.request.urlopen(req, timeout=90) as response:
        length = int(response.headers.get("Content-Length", "0"))
        if response.status != 200 or length > max_bytes:
            raise DataContractError("HTTP status/Content-Length ngoài budget")
        payload = response.read(max_bytes+1)
        if len(payload) > max_bytes or (length and len(payload) != length):
            raise DataContractError("Payload thiếu hoặc vượt byte cap")
        return payload, {"status": response.status, "bytes": len(payload),
                         "etag": response.headers.get("ETag")}


def eligible_pages(pages: dict[str, dict[str, Any]], config: dict[str, Any]) -> tuple[
        list[dict[str, Any]], Counter[str]]:
    accepted: list[dict[str, Any]] = []
    exclusions: Counter[str] = Counter()
    for page in sorted(pages.values(), key=lambda p: p["title"]):
        info = page.get("imageinfo", [{}])[0]
        meta = info.get("extmetadata", {})
        license_name = meta.get("LicenseShortName", {}).get("value")
        category = meta.get("Categories", {}).get("value", "").lower()
        if info.get("mime") not in {"image/jpeg", "image/png", "image/webp"}:
            exclusions["not_raster_photo"] += 1
        elif license_name not in config["allowed_licenses"]:
            exclusions["license_not_in_research_whitelist"] += 1
        elif any(flag in category for flag in config["blocked_categories"]):
            exclusions["publisher_rights_dispute_or_no_consent_flag"] += 1
        elif info.get("size", 0) > config["max_image_bytes"]:
            exclusions["original_above_byte_budget"] += 1
        elif min(info.get("width", 0), info.get("height", 0)) < config["min_dimension"]:
            exclusions["small_original"] += 1
        else:
            accepted.append({"publisher_page_id": page["pageid"], "title": page["title"],
                "source_page": info["descriptionurl"], "url": info["url"],
                "thumb_url": info.get("thumburl"), "publisher_sha1": info["sha1"],
                "original_bytes": info["size"], "original_size": [info["width"], info["height"]],
                "license": license_name, "license_url": meta.get("LicenseUrl", {}).get("value"),
                "artist": plain(meta.get("Artist", {}).get("value", "")),
                "description": plain(meta.get("ImageDescription", {}).get("value", "")),
                "date_metadata": plain(meta.get("DateTimeOriginal", {}).get("value", "")),
                "credit": plain(meta.get("Credit", {}).get("value", "")),
                "categories": meta.get("Categories", {}).get("value", ""),
                "restrictions": meta.get("Restrictions", {}).get("value"),
                "discovery_queries": page["discovery_queries"],
                "official_split": None, "training_eligible": False})
    return accepted, exclusions


def recover(config_path: Path, root: Path) -> dict[str, Any]:
    """Khôi phục response đã nhận trước429 ở report mới, không tải lại/sửa raw."""
    root = root.resolve()
    config = load_yaml(config_path)
    original = load_yaml(pinned(root, config["discovery_config"]))
    pages = {}
    for pin in config["metadata_inputs"]:
        payload = json.loads(pinned(root, pin).read_text(encoding="utf8"))
        for page in payload.get("query", {}).get("pages", {}).values():
            if page.get("imageinfo"):
                pages[page["title"]] = {**page, "discovery_queries": [pin["path"]]}
    accepted, exclusions = eligible_pages(pages, original)
    output = fresh(root, config["output"], "artifacts/reports")
    output.mkdir(parents=True)
    write_json(output / "eligible-photo-metadata.json", accepted)
    summary = {"status": "metadata_recovered_from_verified_raw_responses_no_new_requests",
               "unique_pages": len(pages), "eligible_metadata_rows": len(accepted),
               "exclusions": dict(exclusions), "metadata_inputs": config["metadata_inputs"],
               "incomplete_discovery_due_to_429": True, "full_source_exhausted": False}
    write_json(output / "summary.json", summary)
    return summary


def discover(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    config = load_yaml(config_path)
    raw = fresh(root, config["raw_metadata"], "data/raw")
    output = fresh(root, config["discovery_output"], "artifacts/reports")
    if not 0 < config["limit_per_query"] <= 50 or len(config["queries"]) > 20:
        raise DataContractError("Search vượt finite cap")
    raw.mkdir(parents=True)
    output.mkdir(parents=True)
    pages: dict[str, dict[str, Any]] = {}
    queries = []
    base = {"action": "query", "prop": "imageinfo", "format": "json",
            "iiprop": "url|size|sha1|mime|extmetadata", "iiurlwidth": str(config["thumb_width"])}
    rate_limited = False
    for index, query in enumerate(config["queries"], 1):
        time.sleep(config.get("interval_seconds", 2))
        params = {**base, "generator": "search", "gsrnamespace": "6", "gsrsearch": query,
                  "gsrlimit": str(config["limit_per_query"])}
        url = config["api"] + "?" + urllib.parse.urlencode(params)
        try:
            data, http = request(url, config["max_metadata_bytes"])
            payload = json.loads(data)
            if payload.get("error"):
                raise DataContractError(str(payload["error"]))
            path = raw / f"search-{index:03d}.json"
            path.write_bytes(data)
            result = payload.get("query", {}).get("pages", {})
            for page in result.values():
                key = page["title"]
                if key not in pages:
                    pages[key] = {**page, "discovery_queries": []}
                pages[key]["discovery_queries"].append(query)
            queries.append({"query": query, "returned_pages": len(result), "url": url,
                            "metadata": {"path": path.relative_to(root).as_posix(),
                                         "sha256": sha256_file(path)}, "http": http,
                            "has_more": "continue" in payload})
            print(f"Commons query {index}: {len(result)} pages", flush=True)
        except Exception as error:
            queries.append({"query": query, "status": "FAILED_preserved", "reason": str(error)})
            if isinstance(error, urllib.error.HTTPError) and error.code == 429:
                rate_limited = True
                break
    seeds = [] if rate_limited else config.get("seed_titles", [])
    for index, title in enumerate(seeds, 1):
        time.sleep(config.get("interval_seconds", 2))
        url = config["api"] + "?" + urllib.parse.urlencode({**base, "titles": title})
        try:
            data, http = request(url, config["max_metadata_bytes"])
        except Exception as error:
            queries.append({"seed_title": title, "status": "FAILED_preserved",
                            "reason": str(error)})
            if isinstance(error, urllib.error.HTTPError) and error.code == 429:
                break
            continue
        payload = json.loads(data)
        path = raw / f"seed-{index:03d}.json"
        path.write_bytes(data)
        for page in payload.get("query", {}).get("pages", {}).values():
            if page.get("imageinfo"):
                pages.setdefault(page["title"], {**page, "discovery_queries": ["seed title"]})
        queries.append({"seed_title": title, "url": url, "http": http,
                        "metadata_sha256": sha256_file(path)})
    accepted, exclusions = eligible_pages(pages, config)
    write_json(output / "eligible-photo-metadata.json", accepted)
    summary = {"status": "metadata_candidates_not_visual_or_owner_acceptance",
               "unique_pages": len(pages), "eligible_metadata_rows": len(accepted),
               "exclusions": dict(exclusions), "queries": queries,
               "full_source_exhausted": False, "test_media_read": False}
    write_json(output / "summary.json", summary)
    write_json(raw / "receipt.json", {**summary, "config_sha256": sha256_file(config_path)})
    return summary


def screen(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    config = load_yaml(config_path)
    metadata = json.loads(pinned(root, config["metadata"]).read_text(encoding="utf8"))
    whitelist = config.get("title_allowlist")
    selected_metadata = [row for row in metadata if whitelist is None or row["title"] in whitelist]
    raw = fresh(root, config["raw_images"], "data/raw")
    output = fresh(root, config["output"], "data/interim")
    if not 0 < config["image_cap"] <= 100 or config["asset_mode"] not in {"thumbnail", "original"}:
        raise DataContractError("Screening asset/cap không hợp lệ")
    previous: list[dict[str, Any]] = []
    for pin in config["prior_screenings"]:
        previous.extend(json.loads(line) for line in pinned(root, pin).read_text(
            encoding="utf8").splitlines() if line)
    refs = [{"dhash": row["dhash"], "sha256": row["source_image_sha256"]}
            for row in previous if "dhash" in row]
    known_sha = {r["source_image_sha256"] for r in previous if "source_image_sha256" in r}
    raw.mkdir(parents=True)
    output.mkdir(parents=True)
    (output / "panels").mkdir()
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    consumed = 0
    for item in selected_metadata[:config["image_cap"]]:
        if item["license"] not in config["allowed_licenses"] or not item["license_url"]:
            raise DataContractError("Metadata license không khớp screening whitelist")
        original = config["asset_mode"] == "original"
        url = item["url"] if original else item["thumb_url"]
        try:
            time.sleep(config.get("interval_seconds", 2))
            payload, http = request(url, config["max_image_bytes"])
            if consumed + len(payload) > config["max_total_bytes"]:
                failures.append({"title": item["title"], "reason": "total_byte_cap_reached"})
                break
            consumed += len(payload)
            if original and hashlib.sha1(payload).hexdigest() != item["publisher_sha1"]:
                raise DataContractError("Original SHA1 khác publisher")
            digest = hashlib.sha256(payload).hexdigest()
            if digest in known_sha:
                failures.append({"title": item["title"], "reason": "prior_exact_source_duplicate"})
                continue
            image = ImageOps.exif_transpose(Image.open(io.BytesIO(payload))).convert("RGB")
            image.info.clear()
            path = raw / f"{digest}.image"
            if not path.exists():
                path.write_bytes(payload)
            sid = f"V7-PUBLIC-SCREEN-{config['id_offset']+len(rows)+1:03d}"
            dhash = difference_hash(image)
            row = {**item, "sample_id": sid, "source_id": "commons_classroom_gapfill",
                "source_local_image_path": path.relative_to(root).as_posix(),
                "source_image_sha256": digest, "source_pixel_sha256":
                hashlib.sha256(image.tobytes()).hexdigest(), "width": image.width,
                "height": image.height, "dhash": dhash,
                "source_original_split": "unassigned_public_photo", "asset_is_original": original,
                "nearest_previous_screening": nearest(dhash, refs) if refs else None,
                "independence_proven": False, "domain": None, "http": http,
                "rights_status": "metadata_license_verified_owner_use_scope_pending",
                "owner_approved": False, "official_split": None, "training_eligible": False}
            rows.append(row)
            panel = Image.new("RGB", (1600, 1000), "white")
            ImageDraw.Draw(panel).text((10, 10), sid, fill="black")
            panel.paste(ImageOps.contain(image, (1580, 950)), (10, 40))
            panel.save(output / "panels" / f"{sid}.jpg", quality=95)
            print(f"Received {sid}", flush=True)
        except Exception as error:
            failures.append({"title": item["title"], "url": url, "reason": str(error)})
            if isinstance(error, urllib.error.HTTPError) and error.code == 429:
                failures[-1]["retry_after"] = error.headers.get("Retry-After")
                failures[-1]["remaining_batch_deferred"] = True
                break
    for start in range(0, len(rows), 6):
        sheet = Image.new("RGB", (2400, 1500), "white")
        for offset, row in enumerate(rows[start:start+6]):
            x, y = (offset % 3)*800, (offset // 3)*750
            with Image.open(output / "panels" / f"{row['sample_id']}.jpg") as panel:
                sheet.paste(ImageOps.contain(panel, (790, 740)), (x, y))
        sheet.save(output / f"sheet-{start//6+1:03d}.jpg", quality=95)
    (output / "screening.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n"
        for r in rows), encoding="utf8")
    summary = {"status": "screening_pending_visual_QA", "records": len(rows),
               "eligible_metadata_rows": len(metadata),
               "not_selected_by_title_scope": len(metadata)-len(selected_metadata),
               "attempted_metadata_rows": min(config["image_cap"], len(selected_metadata)),
               "download_bytes": consumed, "asset_mode": config["asset_mode"],
               "failures": failures, "training_eligible": False, "test_media_read": False,
               "config_sha256": sha256_file(config_path)}
    write_json(output / "summary.json", summary)
    write_json(raw / "receipt.json", summary)
    return summary


def review(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    config = load_yaml(config_path)
    selection = json.loads(pinned(root, config["selection"]).read_text(encoding="utf8"))
    sources = {}
    for pin in config["screenings"]:
        sources.update({r["sample_id"]: r for r in [json.loads(line) for line in
            pinned(root, pin).read_text(encoding="utf8").splitlines() if line]})
    transform = load_yaml(pinned(root, config["preprocessing"]))
    if transform["image_size"] != 224 or transform["transform"] != "rgb_letterbox_bilinear_v1":
        raise DataContractError("Preprocessing khác E003")
    ids: set[str] = set()
    endpoints = {}
    for item in selection["proposals"]:
        sid = item["sample_id"]
        if re.fullmatch(r"V7-PF-[A-D]-\d{3}", sid) is None or sid in ids:
            raise DataContractError("Proposal ID sai hoặc trùng")
        ids.add(sid)
        source = sources[item["screening_id"]]
        path = (root / str(source["source_local_image_path"])).resolve()
        if (not path.is_relative_to(root / "data/raw")
                or source["source_original_split"] != "unassigned_public_photo"
                or (not source["asset_is_original"] and not config["allow_publisher_thumbnail"])):
            raise DataContractError("Review cần raw public asset được khai rõ original/thumbnail")
        verify_pin(path, source["source_image_sha256"])
        with Image.open(path) as opened_asset:
            decoded = ImageOps.exif_transpose(opened_asset).convert("RGB")
            if (decoded.size != (source["width"], source["height"])
                    or hashlib.sha256(decoded.tobytes()).hexdigest()
                    != source["source_pixel_sha256"]):
                raise DataContractError("Decoded pixels/geometry khác screening đã pin")
        box = PixelBox(*item["xyxy"])
        if (box.xmax > source["width"] or box.ymax > source["height"]
                or len(item["states"]) != 2 or any(s not in {"P", "N", "U"}
                                                 for s in item["states"])):
            raise DataContractError("Geometry/state không hợp lệ")
        endpoints[sid] = {**item, "source_image_sha256": source["source_image_sha256"]}
    validate_pairs(selection["pairs"], endpoints)
    output = fresh(root, config["output"], "outputs")
    output.mkdir(parents=True)
    (output / "media").mkdir()
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
    records, cards = [], []
    for item in selection["proposals"]:
        sid = item["sample_id"]
        source = sources[item["screening_id"]]
        path = root / source["source_local_image_path"]
        image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        image.info.clear()
        crop = image.crop(tuple(item["xyxy"]))
        fill = transform["fill"]
        native = letterbox_rgb(crop, 224, (fill[0], fill[1], fill[2]))
        marked = image.copy()
        ImageDraw.Draw(marked).rectangle(item["xyxy"], outline="red", width=8)
        media = {}
        for suffix, asset in [("source", marked), ("crop", crop), ("input224", native)]:
            target = output / "media" / f"{sid}-{suffix}.png"
            asset.save(target)
            media[suffix] = {"path": target.relative_to(root).as_posix(),
                             "sha256": sha256_file(target)}
        record = {**item, "final_proposed_states": item["states"], "final_reason": item["reason"],
            "source_image_sha256": source["source_image_sha256"],
            "source_page": source["source_page"],
            "source_original_path": source["source_local_image_path"], "publisher_sha1":
            source["publisher_sha1"], "media": media, "attribution": {
                "title": source["title"], "artist": source["artist"], "license": source["license"],
                "license_url": source["license_url"], "changes_notice":
                "EXIF orientation, RGB, bbox, crop và letterbox bilinear224 theo E003. "
                + ("Nguồn là original." if source["asset_is_original"] else
                   "Nguồn là thumbnail do publisher resize, không phải original.")},
            "canonical_targets": [None, None], "canonical_mask": [0, 0], "split": None,
            "owner_approved": False, "training_eligible": False,
            "independence_proven": False, "source_restrictions": source["restrictions"]}
        record.update(source_asset_is_original=source["asset_is_original"],
                      decoded_source_size=[source["width"], source["height"]],
                      publisher_original_size=source["original_size"],
                      source_asset_url=source["url"] if source["asset_is_original"]
                      else source["thumb_url"])
        records.append(record)
        panel = Image.new("RGB", (1600, 950), "white")
        ImageDraw.Draw(panel).text((10, 10), sid+" "+"/".join(item["states"])+" Draft",
                                  font=font, fill="black")
        panel.paste(ImageOps.contain(marked, (670, 860)), (0, 60))
        panel.paste(ImageOps.contain(crop, (420, 860)), (680, 60))
        panel.paste(native, (1120, 60))
        panel.paste(native.resize((448, 448), Image.Resampling.NEAREST), (1120, 300))
        panel.save(output / f"{sid}.png")
        credit = (f'<a href="{html.escape(source["source_page"])}">'
                  f'{html.escape(source["title"])}</a>; {html.escape(source["artist"])}; '
                  f'<a href="{html.escape(source["license_url"])}">'
                  f'{html.escape(source["license"])}</a>. '
                  f'{html.escape(record["attribution"]["changes_notice"])}')
        figures = ''.join(f'<figure><figcaption>{name}</figcaption><img class="{name}" '
                          f'src="media/{sid}-{name}.png"></figure>'
                          for name in ["source", "crop", "input224"])
        cards.append(f'<article id="{sid}"><h2>{sid} {"/".join(item["states"])}</h2>'
                     f'<p>Anchor: {html.escape(item["person_unit_hint"])}</p>'
                     f'<p>{html.escape(item["reason"])}</p><div class="images">{figures}</div>'
                     f'<p>{credit}</p><p>Family: {html.escape(item["visual_family_hint"])}; '
                     'chưa group independence/split/training.</p></article>')
    (output / "review-proposals.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n"
        for r in records), encoding="utf8")
    pair_links = ''.join(
        f'<li>{html.escape(p["pair_id"])} {html.escape(p["target"])}: '
        f'<a href="#{p["positive_id"]}">{p["positive_id"]} P</a> / '
        f'<a href="#{p["negative_id"]}">{p["negative_id"]} N</a> (same-image Draft)</li>'
        for p in selection["pairs"])
    scene_links = ''.join(
        f'<li>{html.escape(p["pair_id"])}: '
        f'<a href="#{p["positive_id"]}">{p["positive_id"]}</a> / '
        f'<a href="#{p["negative_id"]}">{p["negative_id"]}</a>. '
        f'{html.escape(p["evidence"])} Chưa owner approve/session-camera ID.</li>'
        for p in selection.get("scene_pair_proposals", []))
    (output / "review-index.html").write_text(
        '<!doctype html><html lang="vi"><meta charset="utf-8">'
        '<title>Public classroom follow-up</title><style>body{font-family:system-ui;'
        'max-width:1600px;margin:auto}.images{display:flex;gap:15px}figure{flex:1;margin:0}'
        'img{max-width:100%;max-height:680px}img.input224{width:224px;height:224px;max-width:none}'
        '</style><h1>Public follow-up — Draft, chưa owner approve</h1>'
        '<p>Thứ tự nhãn: phone_use / looking_around. U là chưa đủ evidence. '
        'Source/crop/input224 bên dưới; input224 hiển thị đúng224px. '
        'Các nhãn mới chưa dùng train, split còn null.</p>'
        '<h2>Pairs cùng ảnh</h2><ul>'+pair_links+'</ul>'
        '<h2>Đề xuất pair cùng cảnh/buổi học</h2><ul>'+scene_links+'</ul>'+''.join(cards)+'</html>',
        encoding="utf8")
    write_json(output / "pairs.json", selection["pairs"])
    write_json(output / "scene-pair-proposals.json", selection.get("scene_pair_proposals", []))
    summary = {"status": "draft_pending_owner_review", "records": len(records),
        "fully_known": sum("U" not in r["states"] for r in records),
        "combinations": dict(Counter(''.join(r["states"]) for r in records)),
        "states": {target: dict(Counter(r["states"][index] for r in records))
                   for index, target in enumerate(["phone_use", "looking_around"])},
        "pairs": len(selection["pairs"]), "independent_groups_proven": 0,
        "canonical_dataset_version": None, "training_eligible": False,
        "test_media_read": False, "model_executed": False,
        "config_sha256": sha256_file(config_path)}
    write_json(output / "summary.json", summary)
    return summary


def report(config_path: Path, root: Path) -> dict[str, Any]:
    """Đo union/funnel/coverage Draft; unknown và chưa approve giữ nguyên."""
    root = root.resolve()
    config = load_yaml(config_path)
    pages = {}
    for pin in config["metadata_responses"]:
        payload = json.loads(pinned(root, pin).read_text(encoding="utf8"))
        for page in payload.get("query", {}).get("pages", {}).values():
            if page.get("imageinfo"):
                pages[page["title"]] = {**page, "discovery_queries": [pin["path"]]}
    eligible, exclusions = eligible_pages(pages, load_yaml(pinned(root, config["eligibility"])))
    rows, batches = [], []
    for pins in config["screenings"]:
        cfg = load_yaml(pinned(root, pins["config"]))
        summary = json.loads(pinned(root, pins["summary"]).read_text(encoding="utf8"))
        batch = [json.loads(s) for s in pinned(root, pins["ledger"]).read_text(
            encoding="utf8").splitlines() if s]
        rows.extend(batch)
        batches.append({"cap": cfg["image_cap"], "batch": cfg["output"], **summary})
    observations = [json.loads(s) for s in pinned(root, config["observations"]).read_text(
        encoding="utf8").splitlines() if s]
    if (len(observations) != len(rows)
            or {r["sample_id"] for r in rows} != {r["screening_id"] for r in observations}
            or any(r["visually_screened"] is not True for r in observations)):
        raise DataContractError("Observations chưa phủ toàn bộ screening")
    proposals = [json.loads(s) for s in pinned(root, config["review_proposals"]).read_text(
        encoding="utf8").splitlines() if s]
    if any(p["training_eligible"] or p["owner_approved"] or p["split"] is not None
           or p["canonical_mask"] != [0, 0] for p in proposals):
        raise DataContractError("Report mới chỉ cho phép Draft chưa dùng train")
    output = fresh(root, config["output"], "artifacts/reports")
    output.mkdir(parents=True)
    matrix: Counter[tuple[str, str, str, str]] = Counter()
    for p in proposals:
        for i, target in enumerate(["phone_use", "looking_around"]):
            matrix[(p["domain"], p["visual_family_hint"], target, p["states"][i])] += 1
    write_json(output / "matrix.json", [{"source": "Wikimedia Commons", "domain": d,
        "group_hint": g, "target": t, "state": s, "count": n,
        "group_independence_proven": False} for (d, g, t, s), n in sorted(matrix.items())])
    groups = [{"group_hint": g, "sample_ids": [p["sample_id"] for p in proposals
               if p["visual_family_hint"] == g], "camera_id": None, "split": None,
               "independence_proven": False}
              for g in sorted({p["visual_family_hint"] for p in proposals})]
    write_json(output / "group-constraints.json", groups)
    strict = [p for p in proposals if p["domain"] == config["strict_classroom_domain"]]
    summary = {"status": "measured_followup_draft_pending_owner_review",
        "unique_metadata_pages_scanned": len(pages), "eligible_metadata_union": len(eligible),
        "metadata_exclusions": dict(exclusions), "total_source_available_pool": None,
        "total_pool_measurement": "unknown", "source_exhausted": False,
        "screening_batches": batches, "images_downloaded": len(rows),
        "visually_screened": len(observations),
        "download_bytes": sum(b["download_bytes"] for b in batches),
        "download_failed_attempts": sum(len(b["failures"]) for b in batches),
        "original_images": sum(r["asset_is_original"] for r in rows),
        "publisher_thumbnail_images": sum(not r["asset_is_original"] for r in rows),
        "source_sha_duplicates_within_followup": len(rows)-len({r["source_image_sha256"]
                                                                   for r in rows}),
        "pixel_duplicates_within_followup": len(rows)-len({r["source_pixel_sha256"]
                                                              for r in rows}),
        "metadata_eligible_not_downloaded": len({r["title"] for r in eligible}
                                                - {r["title"] for r in rows}),
        "remaining_visually_eligible_pool": None, "remaining_pool_measurement": "unknown",
        "images_shortlisted_for_crop_review": len({p["source_image_sha256"] for p in proposals}),
        "images_not_shortlisted": len(rows)-len({p["source_image_sha256"] for p in proposals}),
        "crop_proposals": len(proposals), "owner_accepted_new_crops": 0,
        "owner_rejected_new_crops": 0,
        "states": {t: {s: sum(p["states"][i] == s for p in proposals) for s in ["P", "N", "U"]}
                   for i, t in enumerate(["phone_use", "looking_around"])},
        "fully_known": sum("U" not in p["states"] for p in proposals),
        "four_combinations": {s: sum(''.join(p["states"]) == s for p in proposals)
                              for s in ["PP", "PN", "NP", "NN"]},
        "domain_counts": dict(Counter(p["domain"] for p in proposals)),
        "strict_classroom_desk": {s: sum(p["states"][0] == s and any(
            flag in p["phenotypes"] for flag in ["desk_phone", "desk_phone_negative"])
            for p in strict) for s in ["P", "N", "U"]},
        "strict_classroom_states": {t: {s: sum(p["states"][i] == s for p in strict)
                                         for s in ["P", "N", "U"]}
                                    for i, t in enumerate(["phone_use", "looking_around"])},
        "visual_families_in_proposals": len(groups),
        "largest_family_crop_count": max((len(g["sample_ids"]) for g in groups), default=0),
        "independent_groups_proven": 0, "training_eligible_new_crops": 0,
        "config_sha256": sha256_file(config_path)}
    write_json(output / "measurement-summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["discover", "recover", "screen", "review", "report"])
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    result = {"discover": discover, "recover": recover, "screen": screen,
              "review": review, "report": report}[args.command](
        args.config, Path.cwd())
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
