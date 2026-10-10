"""Review version mới từ R7 bất biến, không materialize dataset/approval."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.targeted_review_package import _source
from ai_exam_monitoring.data.v7_input_evidence import letterbox_rgb


def letterbox_preview(image: Image.Image, size: int, fill: list[int]) -> Image.Image:
    """Cùng RGB/round/bilinear/fill với training.data.letterbox, trước normalize."""
    return letterbox_rgb(image, size, (fill[0], fill[1], fill[2]))


def validate_overrides(rows: list[dict[str, Any]], overrides: list[dict[str, Any]]) -> None:
    by_id = {r["sample_id"]: r for r in rows}
    ids = [o["sample_id"] for o in overrides]
    if len(ids) != len(set(ids)) or not set(ids) <= set(by_id):
        raise DataContractError("Override trùng hoặc ID ngoài R7")
    for override in overrides:
        row = by_id[override["sample_id"]]
        states = override["final_proposed_states"]
        if len(states) != 2 or any(s not in {"P", "N", "U"} for s in states):
            raise DataContractError("Proposal cần hai target P/N/U")
        box = override.get("final_xyxy", row["draft_xyxy"])
        if (len(box) != 4 or any(type(v) is not int for v in box)
                or not 0 <= box[0] < box[2] <= row["width"]
                or not 0 <= box[1] < box[3] <= row["height"]):
            raise DataContractError("Recrop vượt source hoặc sai geometry")
        if not override.get("final_reason") or override.get("owner_approved") is not False:
            raise DataContractError("Cần reason và proposal chưa owner approve")


def pinned(workspace: Path, pin: dict[str, str]) -> Path:
    path = (workspace / pin["path"]).resolve()
    if not path.is_relative_to(workspace) or sha256_file(path) != pin["sha256"]:
        raise DataContractError("Input path/SHA thay đổi")
    return path


def inherited_reason(observation: str) -> str:
    """Bỏ tên vòng QA khỏi reason kế thừa; giữ nguyên evidence, không suy nhãn mới."""
    return re.sub(r"QA(?: R\d+| cuối)?(?: đổi hypothesis)?:\s*", "", observation)


def merge_overrides(rows: list[dict[str, Any]],
                    payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changes: dict[str, dict[str, Any]] = {}
    for payload in payloads:
        validate_overrides(rows, payload["overrides"])
        allowed = set(payload.get("supersedes_ids_from_root_r1", []))
        overlap = {r["sample_id"] for r in payload["overrides"]} & set(changes)
        if overlap != allowed:
            raise DataContractError("Override conflict cần supersession IDs chính xác")
        changes.update({r["sample_id"]: r for r in payload["overrides"]})
    return list(changes.values())


def build(config_path: Path, workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    config = load_yaml(config_path)
    if config["status"] != "draft_owner_review_only" or config["training_eligible"] is not False:
        raise DataContractError("Không dựng accepted dataset")
    candidate_path = pinned(workspace, config["r7_candidates"])
    if not candidate_path.is_relative_to(workspace / "data/interim"):
        raise DataContractError("Review chỉ đọc candidates interim")
    rows = [json.loads(line) for line in candidate_path.read_text(encoding="utf8").splitlines()]
    if len({r["sample_id"] for r in rows}) != len(rows):
        raise DataContractError("Candidate ID trùng")
    for row in rows:
        if (row["training_eligible"] is not False or row["split"] is not None
                or row["canonical_targets"] != [None, None] or row["canonical_mask"] != [0, 0]):
            raise DataContractError("Chỉ đọc proposal Draft")
        _source(row, workspace)
        crop_path = (workspace / row["crop_path"]).resolve()
        if (not crop_path.is_relative_to(workspace / "data/interim")
                or sha256_file(crop_path) != row["crop_sha256"]):
            raise DataContractError("R7 crop path/SHA thay đổi")
    payload = (json.loads(pinned(workspace, config["overrides"]).read_text(encoding="utf8"))
               if config.get("overrides") else {"overrides": []})
    payloads = [payload] + [json.loads(pinned(workspace, pin).read_text(encoding="utf8"))
                           for pin in config.get("supplemental_overrides", [])]
    overrides = merge_overrides(rows, payloads)
    changes = {o["sample_id"]: o for o in overrides}
    findings = {}
    if config.get("evidence_observations"):
        observations = json.loads(pinned(workspace, config["evidence_observations"])
                                  .read_text(encoding="utf8"))["observations"]
        expected = {r["sample_id"] for r in rows if r["bucket"] in {"B", "D"}}
        if len(observations) != len(expected) or {r[0] for r in observations} != expected:
            raise DataContractError("Evidence observations thiếu/trùng/ngoài B/D")
        findings = {r[0]: {"source": r[1], "r7_crop": r[2], "r7_input224": r[3],
                          "reason": r[4]} for r in observations}
    transform = load_yaml(pinned(workspace, config["preprocessing_config"]))
    if transform["transform"] != "rgb_letterbox_bilinear_v1" or transform["image_size"] != 224:
        raise DataContractError("Cần preprocessing E003 input224")
    credits = [json.loads(line) for line in pinned(workspace, config["attribution"])
               .read_text(encoding="utf8").splitlines()]
    attribution = {r["candidate_id"]: r for r in credits}
    output = (workspace / config["output"]).resolve()
    if not output.is_relative_to(workspace / "outputs") or output.exists():
        raise DataContractError("Review output phải version mới dưới outputs")
    output.mkdir(parents=True)
    (output / "media").mkdir()
    records, cards = [], []
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
    for row in rows:
        sid = row["sample_id"]
        change = changes.get(sid, {})
        states = change.get("final_proposed_states", row["proposed_states"])
        box = change.get("final_xyxy", row["draft_xyxy"])
        finding = findings.get(sid, {})
        reason = change.get("final_reason", finding.get("reason",
                            inherited_reason(row["observation"])))
        with Image.open(_source(row, workspace)) as decoded:
            source = decoded.convert("RGB")
        if source.size != (row["width"], row["height"]):
            raise DataContractError("Source dimensions khác metadata đã pin")
        crop = source.crop(box)
        input_image = letterbox_preview(crop, transform["image_size"], transform["fill"])
        marked = source.copy()
        ImageDraw.Draw(marked).rectangle(box, outline="red", width=3)
        media = {}
        for suffix, asset in (("source", marked), ("crop", crop), ("input224", input_image)):
            path = output / "media" / f"{sid}-{suffix}.png"
            asset.save(path)
            media[suffix] = {"path": path.relative_to(workspace).as_posix(),
                             "sha256": sha256_file(path)}
        if sid in config.get("panel_ids", []):
            panel = Image.new("RGB", (1600, 800), "white")
            draw = ImageDraw.Draw(panel)
            draw.text((8, 8), f'{sid}  {"/".join(states)}  {row["screening_set"]}:'
                      f'{row["screening_id"]}', font=font, fill="black")
            draw.text((8, 38), "Nguồn / crop / input224 native + nearest2x",
                      font=font, fill="black")
            panel.paste(ImageOps.contain(marked, (660, 720)), (8, 72))
            panel.paste(ImageOps.contain(crop, (430, 720)), (678, 72))
            panel.paste(input_image, (1130, 76))
            panel.paste(input_image.resize((448, 448), Image.Resampling.NEAREST), (1130, 320))
            panel.save(output / f"{sid}.png")
        record = {"sample_id": sid, "source_id": row["source_id"], "domain": row["domain"],
                  "bucket": row["bucket"], "r7_proposed_states": row["proposed_states"],
                  "final_proposed_states": states, "final_reason": reason,
                  "r7_crop_sha256": row["crop_sha256"],
                  "source_sha256": row["source_image_sha256"], "final_xyxy": box,
                  "source_original_path": _source(row, workspace).relative_to(workspace).as_posix(),
                  "source_pixel_sha256": row["source_pixel_sha256"],
                  "r7_xyxy": row["draft_xyxy"], "media": media,
                  "owner_feedback": change.get("owner_feedback"),
                  "qa_disposition": change.get("qa_disposition", "retain_r7_proposal"),
                  "person_unit_hint": change.get("person_unit_hint", row["person_unit_hint"]),
                  "visual_family_hint": row["visual_family_hint"],
                  "canonical_targets": [None, None], "canonical_mask": [0, 0],
                  "split": None, "training_eligible": False, "owner_approved": False,
                  "status": "final_proposal_pending_owner_review"}
        records.append(record)
        credit = attribution.get(sid)
        if credit:
            credit = {key: credit.get(key) for key in (
                "creator", "title", "creator_url", "landing_page_url",
                "current_observed_license_url", "provider_license_url", "annotation_license_url",
                "flickr_photo_id", "copyright_notices_status", "other_rights_and_use_scope",
                "rights_review_blockers", "rights_status",
            )}
            credit.update({"changes_notice": f"Crop đề xuất XYXY={box}; chuyển RGB/PNG; "
                           "input224 letterbox bilinear/fill theo E003; không upload.",
                           "proposed_crop": media["crop"], "owner_review": "PENDING"})
        record["attribution"] = credit
        record["reason_origin"] = "audit_current" if change or finding else "r7_inherited"
        record["r7_input_evidence"] = finding or None
        evidence_html = ('<p>Evidence R7: source ' + html.escape(finding["source"]) +
                         ' / crop ' + html.escape(finding["r7_crop"]) + ' / input224 ' +
                         html.escape(finding["r7_input224"]) +
                         '; recrop mới phải xem riêng tại ảnh trên.</p>') if finding else ""
        credit_html = ('<details><summary>Credit / quyền còn chờ owner</summary><pre>' +
                       html.escape(json.dumps(credit, ensure_ascii=False, indent=2)) +
                       '</pre></details>') if credit else ""
        historical = ('<details><summary>R7 lịch sử, không phải reason cuối</summary><p>' +
                      html.escape(row["observation"]) + '</p></details>')
        images = "".join(f'<figure><figcaption>{label}</figcaption>'
                         f'<a href="media/{sid}-{suffix}.png"><img loading="lazy" '
                         f'class="{suffix}" src="media/{sid}-{suffix}.png"></a></figure>'
                         for suffix, label in (("source", "Nguồn + bbox đề xuất"),
                                               ("crop", "Crop cuối đề xuất"),
                                               ("input224", "Input224 native")))
        cards.append(f'<article id="{sid}"><h2>{sid} — phone {states[0]} / looking {states[1]}</h2>'
                     f'<p class="reason">{html.escape(reason)}</p><p>Proposal chưa accepted.</p>'
                     '<p><a href="' + html.escape(os.path.relpath(_source(row, workspace), output)
                                                  .replace("\\", "/"), quote=True) +
                     '">Ảnh nguồn nguyên bản local</a></p>'
                     f'<div class="images">{images}</div><p>Anchor: '
                     f'{html.escape(record["person_unit_hint"])}; group hint chưa độc lập: '
                     f'{html.escape(row["visual_family_hint"])}.</p>{evidence_html}'
                     f'{historical}{credit_html}'
                     '</article>')
    (output / "review-proposals.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False,
        sort_keys=True) + "\n" for r in records), encoding="utf8")
    nav = " ".join(f'<a href="#{sid}">{sid}</a>' for sid in config.get("panel_ids", []))
    (output / "review-index.html").write_text('<!doctype html><html lang="vi">'
        '<meta charset="utf-8"><title>V7 final owner proposal sau R7</title><style>'
        'body{font-family:system-ui;margin:24px auto;max-width:1500px}article{border-top:2px solid '
        '#bbb;padding:20px 0}.images{display:flex;align-items:flex-start;gap:16px}figure{margin:0;'
        'flex:1}img{max-width:100%;max-height:650px}img.input224{width:224px;height:224px;'
        'max-width:none}pre{white-space:pre-wrap}nav{line-height:2}.reason{font-size:18px}</style>'
        '<h1>Final proposal sau R7 — chờ owner, chưa release/train</h1>'
        '<p>Thứ tự phone_use / looking_around; input224 trước normalize. Click ảnh để xem native. '
        'QA cũ chỉ nằm trong lịch sử. Review feedback không tự tạo batch approval.</p>'
        f'<nav>{nav}</nav>' + "".join(cards) + '</html>', encoding="utf8")
    summary = {"records": len(records), "overrides": len(changes), "training_eligible": False,
               "output": config["output"], "config_sha256": sha256_file(config_path),
               "test_media_read": False, "inference_executed": False,
               "review_proposals_sha256": sha256_file(output / "review-proposals.jsonl")}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf8")
    return summary


def verify_review(output: Path, workspace: Path) -> dict[str, Any]:
    """Kiểm proposal/media và pair validity; không đọc media historical test."""
    workspace, output = workspace.resolve(), output.resolve()
    if not output.is_relative_to(workspace / "outputs"):
        raise DataContractError("Review phải dưới outputs")
    rows = [json.loads(line) for line in (output / "review-proposals.jsonl")
            .read_text(encoding="utf8").splitlines()]
    by_id = {r["sample_id"]: r for r in rows}
    if len(by_id) != len(rows):
        raise DataContractError("Review ID trùng")
    hashes = set()
    media_verified = 0
    for row in rows:
        if (row["canonical_targets"] != [None, None] or row["canonical_mask"] != [0, 0]
                or row["split"] is not None or row["training_eligible"] is not False
                or row["owner_approved"] is not False):
            raise DataContractError("Review tự tạo approval/training target")
        for pin in row["media"].values():
            path = pinned(workspace, pin)
            if not path.is_relative_to(output / "media"):
                raise DataContractError("Media path thoát package review")
            media_verified += 1
        digest = row["media"]["crop"]["sha256"]
        if digest in hashes:
            raise DataContractError("Final crop pixels trùng")
        hashes.add(digest)
        with Image.open(workspace / row["media"]["input224"]["path"]) as image:
            if image.size != (224, 224):
                raise DataContractError("Input không đúng224")
    pairs = json.loads((workspace /
        "data/interim/pilot-b/v7-targeted-review-20261008-r7/pairs.json").read_text(encoding="utf8"))
    valid: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for pair in pairs:
        target = int(pair["bucket"] == "C")
        states = [by_id[pair[key]]["final_proposed_states"][target]
                  for key in ("positive_id", "negative_id")]
        (valid if states == ["P", "N"] else invalid).append({**pair, "final_target_states": states})
    return {"status": "PASS_draft_review_integrity", "records": len(rows),
            "media_hashes_verified": media_verified,
            "fully_known_proposed": sum("U" not in r["final_proposed_states"] for r in rows),
            "all_unknown_proposed_review_only": sum(r["final_proposed_states"] == ["U", "U"]
                                                    for r in rows),
            "by_combination": dict(Counter("/".join(r["final_proposed_states"]) for r in rows)),
            "by_bucket": {b: {"records": len(sub := [r for r in rows if r["bucket"] == b]),
                               "phone": dict(Counter(r["final_proposed_states"][0] for r in sub)),
                               "looking": dict(Counter(r["final_proposed_states"][1] for r in sub))}
                          for b in "ABCD"},
            "r7_pairs_valid_under_final_proposals": valid,
            "r7_pairs_invalid_under_final_proposals": invalid,
            "pair_validity_is_not_scene_match_or_owner_acceptance": True,
            "training_eligible": False, "test_media_read": False, "inference_executed": False}


def verify_historical_metadata(workspace: Path) -> dict[str, Any]:
    """Kiểm pins lịch sử sẵn có, không hash/decode crop evaluation v4–v6."""
    workspace = workspace.resolve()
    r7_root = workspace / "artifacts/reports/pilot-b-v7-targeted-20261008"
    report_files = []
    report_mismatches = []
    for line in (r7_root / "checksums-final.sha256").read_text(encoding="utf8").splitlines():
        digest, relative = line.split("  ", 1)
        path = (r7_root / relative).resolve()
        if not path.is_relative_to(r7_root):
            raise DataContractError("R7 historical checksum path thoát report")
        actual = sha256_file(path)
        if actual != digest:
            report_mismatches.append({"path": path.relative_to(workspace).as_posix(),
                                      "expected": digest, "actual": actual})
            continue
        report_files.append(relative)
    pointer = json.loads((r7_root / "review-pointer-final.json").read_text(encoding="utf8"))
    pointer_files = []
    for value in pointer.values():
        pins = value if isinstance(value, list) else [value]
        for pin in pins:
            if isinstance(pin, dict) and set(pin) == {"path", "sha256"}:
                pinned(workspace, pin)
                pointer_files.append(pin["path"])
    metadata_counts, history_pins = {}, {}
    for version, name in ((4, "pilot-b-20261005-v4"), (5, "pilot-b-20261007-v5"),
                          (6, "pilot-b-20261007-v6")):
        package = workspace / "data/processed/pilot-b" / name
        count = 0
        for line in (package / "checksums.sha256").read_text(encoding="utf8").splitlines():
            digest, relative = line.split("  ", 1)
            path = (package / relative).resolve()
            if not path.is_relative_to(package):
                raise DataContractError("Historical checksum path thoát package")
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".pt", ".npy"}:
                continue
            if sha256_file(path) != digest:
                raise DataContractError("Metadata release v4–v6 thay đổi")
            history_pins[path.relative_to(workspace).as_posix()] = digest
            count += 1
        metadata_counts[f"v{version}"] = count
        history_pins[(package / "checksums.sha256").relative_to(workspace).as_posix()] = (
            sha256_file(package / "checksums.sha256"))
    # Lịch sử E001–E003 trong Git: kiểm bytes file tracked so với HEAD mà không sửa file.
    import subprocess

    changed = subprocess.run(["git", "diff", "--name-only", "HEAD", "--",
        "artifacts/reports/E001", "artifacts/reports/E002", "artifacts/reports/E003",
        "artifacts/reports/E001-execution-20261006", "artifacts/reports/E002-execution-20261007",
        "artifacts/reports/E003-execution-20261008", "docs/experiments/E001-results.md",
        "docs/experiments/E002-results.md", "docs/experiments/E003-results.md"],
        cwd=workspace, capture_output=True, text=True, check=True).stdout.splitlines()
    if changed:
        raise DataContractError("Historical experiment files tracked khác HEAD")
    return {"status": "PASS_dataset_pins_WITH_historical_report_mismatch" if report_mismatches
            else "PASS_historical_metadata_and_r7_pins",
            "r7_report_files_verified": len(report_files),
            "r7_pointer_pins_verified": pointer_files,
            "r7_report_mismatches_preserved_not_rewritten": report_mismatches,
            "release_metadata_files_verified": metadata_counts, "history_pins": history_pins,
            "historical_experiment_tracked_diff": changed,
            "historical_test_crop_bytes_read": False, "historical_crop_integrity_rehashed": False,
            "limitation": "Không đọc lại media test; bảo toàn media bằng phạm vi mutations và pins "
                          "metadata. Không tuyên bố rehash mọi pixel v4–v6."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.workspace), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
