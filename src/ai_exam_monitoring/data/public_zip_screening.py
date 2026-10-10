"""Audit ZIP public bằng Range hữu hạn; không đọc whole archive hoặc chọn split."""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json
from ai_exam_monitoring.data.image_similarity import difference_hash
from ai_exam_monitoring.data.v7_input_evidence import letterbox_rgb
from ai_exam_monitoring.data.v7_r8_execution import fresh, pinned


def fetch_range(url: str, start: int, stop: int, size: int) -> bytes:
    if not url.startswith("https://") or not 0 <= start < stop <= size:
        raise DataContractError("Range HTTPS/bounds sai")
    req = urllib.request.Request(url, headers={
        "User-Agent": "ClassroomDatasetResearch/1.0 (finite local research)",
        "Range": f"bytes={start}-{stop-1}"})
    with urllib.request.urlopen(req, timeout=40) as response:
        if (response.status != 206 or response.headers.get("Content-Range")
                != f"bytes {start}-{stop-1}/{size}"):
            raise DataContractError("Server không trả exact Range206")
        data = bytes(response.read(stop-start+1))
        if len(data) != stop-start:
            raise DataContractError("Range thiếu/vượt bytes")
        return data


class PublicZipReader:
    def __init__(self, url: str, size: int, budget: int) -> None:
        self.url, self.size, self.budget = url, size, budget
        self.position, self.consumed = 0, 0
        self.receipts: list[dict[str, Any]] = []

    def tell(self) -> int:
        return self.position

    def seekable(self) -> bool:
        return True

    def seek(self, offset: int, whence: int = 0) -> int:
        target = offset if whence == 0 else (
            self.position+offset if whence == 1 else self.size+offset)
        if whence not in {0, 1, 2} or not 0 <= target <= self.size:
            raise DataContractError("ZIP seek ngoài bounds")
        self.position = target
        return target

    def read(self, amount: int = -1) -> bytes:
        count = self.size-self.position if amount < 0 else min(amount, self.size-self.position)
        if count == 0:
            return b""
        if self.consumed+count > self.budget:
            raise DataContractError("ZIP Range vượt finite byte budget")
        start = self.position
        data = fetch_range(self.url, start, start+count, self.size)
        self.receipts.append({"start": start, "stop_exclusive": start+count,
                              "sha256": hashlib.sha256(data).hexdigest()})
        self.consumed += len(data)
        self.position += len(data)
        return data


def run(config_path: Path, root: Path, inventory_only: bool) -> dict[str, Any]:
    root = root.resolve()
    cfg = load_yaml(config_path)
    metadata = json.loads(pinned(root, cfg["metadata"]).read_text(encoding="utf8"))
    if (metadata["metadata"].get("license", {}).get("id") != cfg["license_id"]
            or metadata["metadata"].get("access_right") != "open"):
        raise DataContractError("Publisher license/open chưa khớp config")
    matches = [f for f in metadata["files"] if f["key"] == cfg["archive_key"]]
    if len(matches) != 1:
        raise DataContractError("Archive key không xác định duy nhất")
    file = matches[0]
    output = fresh(root, cfg["report_output"], "artifacts/reports")
    raw = fresh(root, cfg["raw_output"], "data/raw")
    output.mkdir(parents=True)
    raw.mkdir(parents=True)
    panels = fresh(root, cfg["screen_output"], "outputs") if not inventory_only else output
    if not inventory_only:
        panels.mkdir(parents=True)
    reader = PublicZipReader(file["links"]["self"], file["size"], cfg["max_range_bytes"])
    rows: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(reader) as archive:
            entries = archive.infolist()
            inventory = [{"index": i, "member_name": e.filename, "crc32": e.CRC,
                "uncompressed_bytes": e.file_size, "compressed_bytes": e.compress_size,
                "is_directory": e.is_dir()} for i, e in enumerate(entries)]
            write_json(raw / "inventory.json", inventory)
            for index in cfg.get("metadata_member_indices", []):
                entry = entries[index]
                if (Path(entry.filename).suffix.lower() not in {".yaml", ".txt"}
                        or entry.file_size > cfg["max_member_bytes"]):
                    raise DataContractError("Metadata member không đủ suffix/byte guard")
                (raw / f"metadata-member-{index:05d}.text").write_bytes(archive.read(entry))
            if not inventory_only:
                indices = cfg["member_indices"]
                if len(indices) > cfg["image_cap"] or len(set(indices)) != len(indices):
                    raise DataContractError("Screening cap/indices sai")
                for index in indices:
                    entry = entries[index]
                    if (Path(entry.filename).suffix.lower() not in {".jpg", ".jpeg", ".png"}
                            or entry.file_size > cfg["max_member_bytes"]
                            or any(p.lower() in {"test", "val", "valid", "validation"}
                                   for p in Path(entry.filename).parts)):
                        raise DataContractError("Chỉ screening image unsplit/train đủ byte cap")
                    payload = archive.read(entry)  # zipfile kiểm CRC sau decompress
                    image = ImageOps.exif_transpose(Image.open(io.BytesIO(payload))).convert("RGB")
                    image.info.clear()
                    digest = hashlib.sha256(payload).hexdigest()
                    path = raw / f"{digest}.image"
                    path.write_bytes(payload)
                    sid = f"V7-ONLINE-SCREEN-{len(rows)+1:03d}"
                    row = {"sample_id": sid, "archive_member_index": index,
                        "member_name_sha256": hashlib.sha256(entry.filename.encode()).hexdigest(),
                        "member_crc32_verified": True, "source_id": cfg["source_id"],
                        "source_image_sha256": digest, "source_pixel_sha256":
                        hashlib.sha256(image.tobytes()).hexdigest(), "source_local_image_path":
                        path.relative_to(root).as_posix(), "width": image.width,
                        "height": image.height, "dhash": difference_hash(image),
                        "source_page": cfg["source_page"],
                        "publisher_archive_md5": file["checksum"],
                        "whole_archive_md5_verified": False, "license_id": cfg["license_id"],
                        "domain": "auxiliary_online_exam", "official_split": None,
                        "training_eligible": False, "owner_approved": False}
                    rows.append(row)
                    panel = Image.new("RGB", (800, 700), "white")
                    ImageDraw.Draw(panel).text((10, 5), sid, fill="black")
                    panel.paste(ImageOps.contain(image, (780, 650)), (10, 30))
                    panel.save(panels / f"{sid}.jpg", quality=95)
                    (output / "screening.jsonl").write_text(''.join(json.dumps(r,
                        ensure_ascii=False)+"\n" for r in rows), encoding="utf8")
                    print(f"Received {sid}", flush=True)
        for start in range(0, len(rows), 6):
            sheet = Image.new("RGB", (2400, 1400), "white")
            for offset, row in enumerate(rows[start:start+6]):
                with Image.open(panels / f"{row['sample_id']}.jpg") as panel:
                    sheet.paste(panel, ((offset % 3)*800, (offset // 3)*700))
            sheet.save(panels / f"sheet-{start//6+1:03d}.jpg", quality=95)
        result = {"status": "inventory_only" if inventory_only else "screening_visual_QA_pending",
                  "entries": len(entries), "images_received": len(rows),
                  "range_bytes_received": reader.consumed, "range_receipts": reader.receipts,
                  "whole_archive_md5_verified": False, "official_split": None,
                  "training_eligible": False, "config_sha256": sha256_file(config_path)}
    except Exception as error:
        result = {"status": "FAILED_preserved", "reason": str(error),
                  "images_received": len(rows), "range_bytes_received": reader.consumed,
                  "range_receipts": reader.receipts, "training_eligible": False}
    write_json(raw / "receipt.json", result)
    write_json(output / "summary.json", result)
    return result


def render_qa(config_path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    cfg = load_yaml(config_path)
    rows = {r["sample_id"]: r for r in (json.loads(s) for s in pinned(root,
        cfg["screening"]).read_text(encoding="utf8").splitlines() if s)}
    transform = load_yaml(pinned(root, cfg["preprocessing"]))
    if transform["image_size"] != 224 or transform["transform"] != "rgb_letterbox_bilinear_v1":
        raise DataContractError("QA preprocessing khác E003")
    output = fresh(root, cfg["output"], "outputs")
    output.mkdir(parents=True)
    records, cards = [], []
    for case in cfg["cases"]:
        row = rows[case["screening_id"]]
        path = (root / row["source_local_image_path"]).resolve()
        if not path.is_relative_to(root / "data/raw") or sha256_file(path) != row[
                "source_image_sha256"]:
            raise DataContractError("QA source path/pin sai")
        image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        image.info.clear()
        fill = transform["fill"]
        native = letterbox_rgb(image, 224, (fill[0], fill[1], fill[2]))
        assets = {}
        for role, asset in [("source", image), ("crop", image), ("input224", native)]:
            target = output / f"{case['case_id']}-{role}.png"
            asset.save(target)
            assets[role] = {"path": target.relative_to(root).as_posix(),
                            "sha256": sha256_file(target)}
        records.append({**case, "media": assets, "source": row, "canonical_targets": [None, None],
                        "canonical_mask": [0, 0], "owner_approved": False, "split": None,
                        "training_eligible": False, "is_dataset_addition": False})
        figures = ''.join(f'<figure>{role}<br><img src="{case["case_id"]}-{role}.png" '
                          f'{"width=224 height=224" if role == "input224" else "width=600"}>'
                          '</figure>' for role in ["source", "crop", "input224"])
        cards.append(f'<article><h2>{case["case_id"]}: '
                     f'{"/".join(case["proposed_states"])}</h2><p>'
                     f'{html.escape(case["reason"])}</p>{figures}</article>')
    (output / "qa-cases.jsonl").write_text(''.join(json.dumps(r, ensure_ascii=False)+"\n"
                                               for r in records), encoding="utf8")
    (output / "review-index.html").write_text(
        '<!doctype html><html lang="vi"><meta charset="utf-8"><title>Online exam QA</title>'
        '<h1>Ví dụ QA review-only, không là dataset addition</h1><p>Thứ tự: phone/looking. '
        'Crop bằng source vì publisher đã cắt cận mặt; không thể recrop lấy bàn bị mất.</p>'
        f'<p>{html.escape(cfg["credit"])}; '
        f'<a href="{cfg["source_page"]}">Nguồn</a>; '
        '<a href="https://creativecommons.org/licenses/by/4.0/">CC BY4</a>. '
        'Thay đổi: EXIF/RGB/letterbox224 theo E003.</p>'+''.join(cards)+'</html>', encoding="utf8")
    return {"status": "QA_only_not_dataset_addition", "cases": len(records)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument("--qa-only", action="store_true")
    args = parser.parse_args()
    result = render_qa(args.config, Path.cwd()) if args.qa_only else run(
        args.config, Path.cwd(), args.inventory_only)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
