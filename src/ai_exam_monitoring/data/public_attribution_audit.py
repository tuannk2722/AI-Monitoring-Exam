"""Lập attribution Draft từ metadata; tùy chọn kiểm trang Flickr công khai, không mở ảnh."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CC_BY_2 = "https://creativecommons.org/licenses/by/2.0/"
FLICKR_ALPHABET = "123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"
USER_AGENT = "ai-exam-monitoring-research/1.0 (public attribution metadata audit)"
MAX_METADATA_BYTES = 131072


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_license(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in {"creativecommons.org", "www.creativecommons.org"}:
        return url
    return "https://creativecommons.org" + parsed.path.rstrip("/") + "/"


def static_photo_id(url: str | None) -> str | None:
    parsed = urllib.parse.urlparse(url or "")
    host = parsed.hostname or ""
    if not (host.endswith(".staticflickr.com") or host.endswith(".static.flickr.com")):
        return None
    match = re.fullmatch(r"([0-9]+)_[A-Za-z0-9_]+\.[A-Za-z0-9]+", Path(parsed.path).name)
    return match[1] if match else None


def landing_photo_id(url: str | None) -> str | None:
    parsed = urllib.parse.urlparse(url or "")
    if parsed.hostname not in {"www.flickr.com", "flickr.com"}:
        return None
    match = re.fullmatch(r"/photos/[^/]+/([0-9]+)/?", parsed.path)
    return match[1] if match else None


def short_landing(photo_id: str) -> str:
    number = int(photo_id)
    if number <= 0:
        raise ValueError("Flickr photo ID phải dương")
    digits = []
    while number:
        number, remainder = divmod(number, 58)
        digits.append(FLICKR_ALPHABET[remainder])
    return "https://flic.kr/p/" + "".join(reversed(digits))


def enforce_flickr_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {
        "www.flickr.com", "flickr.com", "flic.kr"
    } or parsed.username or parsed.password or parsed.port not in {None, 443}:
        raise ValueError("Chỉ đọc metadata HTTPS trên Flickr/flic.kr")


class FlickrRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str,
                         headers: Any, newurl: str) -> urllib.request.Request | None:
        enforce_flickr_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def observe_flickr(seed: dict[str, Any]) -> dict[str, Any]:
    """Chỉ HEAD landing và GET JSON oEmbed; không gọi API có key hoặc tải media."""
    photo_id = seed["flickr_photo_id"]
    url = seed["landing_page_url"]
    observation: dict[str, Any] = {
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "flickr_photo_id": photo_id,
        "request_landing_url": url,
        "credentials_used": False,
        "media_downloaded": False,
        "status": "unverified",
    }
    try:
        enforce_flickr_url(url)
        opener = urllib.request.build_opener(FlickrRedirect())
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with opener.open(request, timeout=15) as response:
            resolved = response.geturl()
            enforce_flickr_url(resolved)
            observation.update({"landing_http_status": response.status,
                                "resolved_landing_url": resolved})
        if landing_photo_id(resolved) != photo_id:
            raise ValueError("Redirect landing không khớp Flickr photo ID")
        endpoint = "https://www.flickr.com/services/oembed/?" + urllib.parse.urlencode(
            {"format": "json", "url": resolved}
        )
        request = urllib.request.Request(endpoint, headers={"User-Agent": USER_AGENT,
                                                           "Accept": "application/json"})
        with opener.open(request, timeout=15) as response:
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                raise ValueError("oEmbed không trả JSON")
            payload = response.read(MAX_METADATA_BYTES + 1)
            if len(payload) > MAX_METADATA_BYTES:
                raise ValueError("oEmbed metadata vượt giới hạn bytes")
            document = json.loads(payload)
            observation.update({"oembed_request_url": endpoint,
                                "oembed_http_status": response.status,
                                "oembed_response_sha256": hashlib.sha256(payload).hexdigest()})
        if not isinstance(document, dict) or document.get("type") != "photo":
            raise ValueError("oEmbed không phải metadata một ảnh")
        if landing_photo_id(document.get("web_page")) != photo_id:
            raise ValueError("oEmbed web_page không khớp Flickr photo ID")
        observation.update({"status": "public_metadata_observed_not_rights_approval",
                            "public_metadata": {key: document.get(key) for key in (
                                "title", "author_name", "author_url", "web_page", "license",
                                "license_url", "license_id", "provider_name", "cache_age")}})
        # Receipt chỉ lưu trường cần dùng, không HTML embed/script, biography, GPS hoặc media.
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError) as error:
        observation.update({"status": "unverified_request_failed",
                            "error": f"{type(error).__name__}: {error}"})
    return observation


def public_seed(row: dict[str, Any], coco_images: dict[int, Any],
                coco_licenses: dict[int, Any]) -> dict[str, Any] | None:
    if row.get("source_original_split") == "train2017":
        image_id = int(row["source_image_id"])
        meta = coco_images[image_id]
        license_data = coco_licenses[meta["license"]]
        if row.get("flickr_url") != meta.get("flickr_url"):
            raise ValueError("COCO Flickr URL khác train metadata đã pin")
        if normalize_license(row.get("license", {}).get("url")) != normalize_license(
            license_data.get("url")
        ):
            raise ValueError("COCO image license khác train metadata đã pin")
        static_url = meta.get("flickr_url")
        photo_id = static_photo_id(static_url)
        return {"provider": "COCO train2017", "source_image_id": image_id,
                "creator": None, "creator_url": None, "title": None,
                "landing_page_url": short_landing(photo_id) if photo_id else None,
                "landing_origin": "derived_flickr_short_url_not_yet_resolved",
                "original_image_url": static_url,
                "provider_license_url": normalize_license(license_data.get("url")),
                "provider_license_name": license_data.get("name"),
                "flickr_photo_id": photo_id,
                "metadata_scope": "COCO train2017 images/licenses; caption không là title"}
    metadata = row.get("attribution_metadata")
    if metadata is None:
        return None
    if metadata.get("Subset") != "train" or row.get("source_original_split") != "train":
        raise ValueError("Open Images attribution chỉ từ train metadata")
    oi_image_id = str(row["source_image_id"])
    if metadata.get("ImageID") != oi_image_id:
        raise ValueError("Open Images source image ID khác attribution metadata")
    landing = metadata.get("OriginalLandingURL")
    original_landing = landing
    seed_blockers = []
    parsed = urllib.parse.urlparse(landing or "")
    if parsed.scheme == "http" and parsed.hostname in {"www.flickr.com", "flickr.com"}:
        # Chỉ nâng scheme của metadata; tuyệt đối không thực hiện request HTTP.
        landing = urllib.parse.urlunparse(parsed._replace(scheme="https"))
    photo_id = landing_photo_id(landing) or static_photo_id(metadata.get("OriginalURL"))
    if landing:
        try:
            enforce_flickr_url(landing)
        except ValueError:
            seed_blockers.append("landing ngoài HTTPS Flickr được phép; cần thẩm định riêng")
            landing = None
    if (landing_photo_id(landing) and static_photo_id(metadata.get("OriginalURL"))
            and landing_photo_id(landing) != static_photo_id(metadata.get("OriginalURL"))):
        seed_blockers.append("photo ID landing khác URL gốc; không chọn ID thay owner")
        landing = None
    return {"provider": "Open Images train metadata", "source_image_id": oi_image_id,
            "creator": metadata.get("Author") or None,
            "creator_url": metadata.get("AuthorProfileURL") or None,
            "title": metadata.get("Title") or None, "landing_page_url": landing,
            "original_landing_page_url": original_landing, "seed_blockers": seed_blockers,
            "landing_origin": "provider_metadata",
            "original_image_url": metadata.get("OriginalURL"),
            "provider_license_url": normalize_license(metadata.get("License")),
            "provider_license_name": "CC BY 2.0" if normalize_license(
                metadata.get("License")) == CC_BY_2 else None,
            "flickr_photo_id": photo_id, "metadata_scope": "Open Images image information"}


def attribution(row: dict[str, Any], seed: dict[str, Any],
                observation: dict[str, Any] | None) -> dict[str, Any]:
    live = (observation or {}).get("public_metadata", {})
    # Trường online chỉ lấy khi response đã kiểm đúng photo ID. Không bịa title/creator khi thiếu.
    result = {**seed, "candidate_id": row["candidate_id"], "crop_path": row["crop_path"],
              "crop_sha256": row["crop_sha256"],
              "source_image_sha256": row["source_image_sha256"],
              "screening_set": row["screening_set"], "screening_id": row["screening_id"],
              "xyxy": row["xyxy"], "public_landing_observation": observation,
              "creator": live.get("author_name") or seed["creator"],
              "creator_url": live.get("author_url") or seed["creator_url"],
              "title": live.get("title") if live.get("title") is not None else seed["title"],
              "landing_page_url": live.get("web_page") or seed["landing_page_url"],
              "current_observed_license_url": normalize_license(live.get("license_url")),
              "rights_status": "pending_individual_attribution_and_owner_review",
              "owner_review": "PENDING", "training_eligible": False,
              "other_rights_and_use_scope": "pending_owner_review_doc21",
              "annotation_license_url": "https://creativecommons.org/licenses/by/4.0/",
              "copyright_notices_status": "owner_review_landing_if_supplied_not_in_oembed",
              "changes_notice": f"Trích crop XYXY={row['xyxy']} từ nguồn; chuyển RGB, lưu PNG. "
                                "Nhãn hai target và nhóm là đề xuất riêng của repository."}
    result["missing_attribution_fields"] = [key for key in (
        "creator", "title", "landing_page_url", "provider_license_url"
    ) if not result.get(key)]
    blockers = list(seed.get("seed_blockers", []))
    if result["missing_attribution_fields"]:
        blockers.append("thiếu attribution; cần kiểm nguồn, không tự điền Unknown như tác giả")
    if (observation is None or
            observation.get("status") != "public_metadata_observed_not_rights_approval"):
        blockers.append("chưa kiểm được metadata trang từng ảnh công khai")
    elif result["current_observed_license_url"] != result["provider_license_url"]:
        blockers.append("license khác/thiếu so với metadata; owner cần giải quyết evidence")
    if result["provider_license_url"] != CC_BY_2:
        blockers.append("ngoài license CC BY2.0 đã shortlist; chưa có quyết định nhận license khác")
    result["rights_review_blockers"] = blockers
    parts = [result["title"] or "[title chưa kiểm]", "—",
             result["creator"] or "[creator chưa kiểm]",
             "—", result["landing_page_url"] or "[landing chưa kiểm]", "—",
             result["provider_license_url"] or "[license chưa kiểm]", "—", result["changes_notice"]]
    result["attribution_draft_text"] = " ".join(parts)
    return result


def render_review_html(rows: list[dict[str, Any]], records: list[dict[str, Any]],
                       candidates: Path, output: Path, workspace: Path) -> str:
    """Hiển thị crop đã có với credit từng ảnh; không đọc/tải media hoặc tạo approval."""
    credits = {r["candidate_id"]: r for r in records}
    cards = []
    for row in rows:
        cid = row["candidate_id"]
        if re.fullmatch(r"V7-[A-D]-[0-9]{3}", cid) is None:
            raise ValueError("Candidate ID không an toàn cho review HTML")
        panel = (candidates.parent / "review" / f"{cid}.jpg").resolve()
        if not panel.is_relative_to(workspace / "data/interim"):
            raise ValueError("Panel review phải trong interim")
        relative = Path(os.path.relpath(panel, output)).as_posix()
        credit = credits.get(cid)
        attribution_html = ""
        if credit:
            attribution_html = '<p class="credit">' + html.escape(
                credit["attribution_draft_text"]) + '</p><p>Quyền/phạm vi sử dụng: '
            attribution_html += html.escape(credit["rights_status"]) + '</p>'
            if credit["rights_review_blockers"]:
                attribution_html += '<p>Blocker: ' + html.escape(
                    "; ".join(credit["rights_review_blockers"])) + '</p>'
        cards.append(f'<article id="{cid}"><h2>{cid} — Draft</h2>'
                     f'<img loading="lazy" src="{html.escape(relative, quote=True)}">'
                     f'<p>{html.escape(row.get("observation", ""))}</p>' + attribution_html
                     + '</article>')
    original = Path(os.path.relpath(candidates.parent / "review/index.html", output)).as_posix()
    return ('<!doctype html><meta charset="utf-8"><title>Review v7 có attribution</title>'
            '<style>body{font-family:system-ui;max-width:1000px;margin:auto}img{width:100%}'
            'article{border-bottom:1px solid #bbb}.credit{overflow-wrap:anywhere}</style>'
            '<h1>Crop/nhãn v7 Draft — chưa accepted hoặc training</h1>'
            '<p>Preview JPEG thu nhỏ ảnh nguồn/crop và thêm khung đỏ đánh dấu crop. '
            'Ảnh crop dataset lưu RGB/PNG; credit dưới đây đi kèm từng ảnh public.</p>'
            f'<p><a href="{html.escape(original, quote=True)}">Mở thông tin unit, phenotype '
            'và matched pairs</a></p>' + ''.join(cards))


def build(args: argparse.Namespace) -> dict[str, Any]:
    workspace = args.workspace.resolve()
    candidates = (workspace / args.candidates).resolve()
    output = (workspace / args.output).resolve()
    if not candidates.is_relative_to(workspace / "data/interim"):
        raise ValueError("Chỉ đọc candidate Draft trong interim; không đọc release/evaluation")
    if not output.is_relative_to(workspace / "outputs") or output.exists():
        raise ValueError("Output phải version mới trong outputs; không ghi đè package/artifact cũ")
    rows = [json.loads(line) for line in candidates.read_text(encoding="utf8").splitlines()]
    if any(row.get("training_eligible") is not False or row.get("canonical_mask") != [0, 0]
           or row.get("canonical_targets") != [None, None] or row.get("split") is not None
           or row.get("usage") != "review_only" for row in rows):
        raise ValueError("Chỉ audit unknown-masked candidate Draft chưa training")
    coco_rows = [r for r in rows if r.get("source_original_split") == "train2017"]
    coco_images: dict[int, Any] = {}
    coco_licenses: dict[int, Any] = {}
    if coco_rows:
        archive = (workspace / args.coco_metadata).resolve()
        if not archive.is_relative_to(workspace / "data/raw/coco"):
            raise ValueError("COCO archive phải raw metadata đã pin")
        if sha256_file(archive) != args.coco_metadata_sha256:
            raise ValueError("COCO metadata SHA khác pin")
        with zipfile.ZipFile(archive) as reader:
            # Chỉ train JSON; không mở val/test JSON hoặc bất kỳ image member nào.
            with reader.open("annotations/captions_train2017.json") as stream:
                document = json.load(stream)
        needed = {int(r["source_image_id"]) for r in coco_rows}
        coco_images = {image["id"]: image for image in document["images"] if image["id"] in needed}
        coco_licenses = {license_data["id"]: license_data for license_data in document["licenses"]}
        del document
    public: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for row in rows:
        seed = public_seed(row, coco_images, coco_licenses)
        if seed is not None:
            public.append((row, seed))
    unique: dict[str, dict[str, Any]] = {}
    for _, seed in public:
        photo_id = seed["flickr_photo_id"]
        if photo_id and seed["landing_page_url"]:
            unique.setdefault(photo_id, seed)
    if args.max_network_images is not None and args.max_network_images < 0:
        raise ValueError("Giới hạn network không được âm")
    selected = list(unique.values())
    if args.max_network_images is not None:
        selected = selected[:args.max_network_images]
    observed: dict[str, dict[str, Any]] = {}
    cache_sha = None
    if args.receipt_cache:
        cache = (workspace / args.receipt_cache).resolve()
        if not cache.is_relative_to(workspace / "outputs") or not args.receipt_cache_sha256:
            raise ValueError("Receipt cache cần outputs path và SHA pin")
        cache_sha = sha256_file(cache)
        if cache_sha != args.receipt_cache_sha256:
            raise ValueError("Receipt cache SHA khác pin")
        cached = json.loads(cache.read_text(encoding="utf8"))
        for observation in cached:
            photo_id = observation["flickr_photo_id"]
            if photo_id not in unique:
                continue
            if observation.get("status") == "public_metadata_observed_not_rights_approval":
                live_id = landing_photo_id(observation["public_metadata"]["web_page"])
                if live_id != photo_id or observation.get("credentials_used") is not False:
                    raise ValueError("Receipt cache không khớp photo ID hoặc scope public")
                if observation.get("media_downloaded") is not False:
                    raise ValueError("Receipt cache đã tải media, ngoài scope audit metadata")
                observed[photo_id] = observation
    reused = len(observed)
    selected = [seed for seed in selected if seed["flickr_photo_id"] not in observed]
    attempted = 0
    if args.verify_public:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for observation in pool.map(observe_flickr, selected):
                observed[observation["flickr_photo_id"]] = observation
                attempted += 1
    records = [attribution(row, seed, observed.get(seed["flickr_photo_id"]))
               for row, seed in public]
    summary = {"status": "draft_pending_owner_review", "training_eligible": False,
               "candidate_sha256": sha256_file(candidates), "total_candidates": len(rows),
               "public_candidates": len(records), "unique_flickr_photo_ids": len(unique),
               "by_provider": dict(Counter(r["provider"] for r in records)),
               "public_network_requested": args.verify_public,
               "images_attempted": attempted, "images_reused_from_pinned_receipt": reused,
               "receipt_cache_sha256": cache_sha,
               "observations": dict(Counter(r["status"] for r in observed.values())),
               "crops_with_missing_fields": sum(bool(r["missing_attribution_fields"])
                                                 for r in records),
               "crops_with_rights_review_blockers": sum(bool(r["rights_review_blockers"])
                                                       for r in records),
               "crops_with_complete_metadata_still_pending_owner": sum(
                   not r["rights_review_blockers"] for r in records),
               "media_read_or_downloaded": False,
               "credentials_used": False,
               "coco_train_metadata_sha256": args.coco_metadata_sha256 if coco_rows else None}
    review_html = render_review_html(rows, records, candidates, output, workspace)
    output.mkdir(parents=True)
    (output / "attribution.jsonl").write_text("".join(json.dumps(
        r, ensure_ascii=False, sort_keys=True)
        + "\n" for r in records), encoding="utf8")
    (output / "flickr-observations.json").write_text(json.dumps(list(observed.values()),
        ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf8")
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True,
        indent=2) + "\n", encoding="utf8")
    (output / "review-index.html").write_text(review_html, encoding="utf8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--coco-metadata", type=Path, required=True)
    parser.add_argument("--coco-metadata-sha256", required=True)
    parser.add_argument("--verify-public", action="store_true")
    parser.add_argument("--max-network-images", type=int)
    parser.add_argument("--receipt-cache", type=Path)
    parser.add_argument("--receipt-cache-sha256")
    args = parser.parse_args()
    print(json.dumps(build(args), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
