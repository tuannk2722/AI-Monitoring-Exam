"""Tuyển batch mở rộng để review, không tạo nhãn hoặc split được chấp thuận."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import git_commit, sha256_file, write_json

from .image_similarity import difference_hash
from .pilot_inputs import verify_pin
from .pilot_owner_groups import verify_payload
from .pilot_schema import read_records
from .pilot_selection import CandidateAnchor, inventory_anchors, source_file, write_selection


@dataclass(frozen=True)
class ReviewImage:
    anchor: CandidateAnchor
    dhash: int


def unique_anchors(
    candidates: list[CandidateAnchor], excluded_images: set[str],
) -> list[CandidateAnchor]:
    """Một anchor lớn nhất mỗi ảnh; loại exact overlap với toàn bộ ledger parent."""
    images: dict[str, list[CandidateAnchor]] = defaultdict(list)
    for row in candidates:
        if row.source_image_sha256 not in excluded_images:
            images[row.source_image_sha256].append(row)
    result = []
    for rows in images.values():
        result.append(min(rows, key=lambda r: (
            -r.source_anchor_yolo.width * r.source_anchor_yolo.height,
            r.rank_sha256, r.identity,
        )))
    return sorted(result, key=lambda r: (r.rank_sha256, r.identity))


def diverse_shortlist(images: list[ReviewImage], budget: int) -> list[ReviewImage]:
    """Farthest-first dHash: chỉ ưu tiên review, không ngưỡng chấp nhận/nhóm cảnh."""
    if type(budget) is not int or budget <= 0:
        raise DataContractError("Budget review phải là số nguyên dương")
    hashes = [r.anchor.source_image_sha256 for r in images]
    if len(set(hashes)) != len(hashes):
        raise DataContractError("Pool phải exact-dedup trước khi shortlist")
    remaining = sorted(images, key=lambda r: (r.anchor.rank_sha256, r.anchor.identity))
    selected: list[ReviewImage] = []
    minimum = {r.anchor.source_image_sha256: 64 for r in remaining}
    while remaining and len(selected) < budget:
        row = min(remaining, key=lambda r: (
            -minimum[r.anchor.source_image_sha256], r.anchor.rank_sha256, r.anchor.identity,
        ))
        selected.append(row)
        remaining.remove(row)
        for other in remaining:
            key = other.anchor.source_image_sha256
            minimum[key] = min(minimum[key], (row.dhash ^ other.dhash).bit_count())
    return selected


def nearest_evidence(query_hash: int, query_sha: str, fingerprints: list[dict],
                     count: int) -> list[dict]:
    """Khoảng cách là đầu mối QA; không tự tạo group hoặc kết luận độc lập."""
    neighbors = []
    for row in fingerprints:
        if row["image_sha256"] == query_sha:
            continue
        neighbors.append({
            "image_sha256": row["image_sha256"],
            "sample_ids": row["sample_ids"],
            "distance": (query_hash ^ row["dhash"]).bit_count(),
        })
    return sorted(neighbors, key=lambda r: (r["distance"], r["image_sha256"]))[:count]


def _new_directory(path: Path, allowed_root: Path) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(allowed_root.resolve()) or resolved == allowed_root.resolve():
        raise DataContractError("Output phải thuộc thư mục artifact được phép")
    if path.exists():
        raise DataContractError("Output đã tồn tại; dùng revision mới")


def build_expansion(config_path: Path, workspace: Path) -> dict[str, Any]:
    config = load_yaml(config_path)
    if config.get("status") != "draft_proposals" or config.get("formulation") != "B":
        raise DataContractError("Chỉ nhận config proposal B, không accepted/training")
    approval_path = workspace / config["continuation_approval"]
    verify_pin(approval_path, config["continuation_approval_sha256"])
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if approval.get("decision") != "approve_reviewed_changes_and_continue_expansion":
        raise DataContractError("Thiếu approval tiếp tục proposal")
    selection = config["selection"]
    if (selection["algorithm"] != "dhash_farthest_first"
            or selection["anchor_rule"] != "largest_source_box_per_exact_image"
            or selection["canonical_targets"] != "unknown"
            or type(selection["review_budget"]) is not int or selection["review_budget"] <= 0
            or type(selection["nearest_count"]) is not int or selection["nearest_count"] <= 0):
        raise DataContractError("Config selection ngoài phạm vi implementation")
    output = workspace / config["output_dir"]
    report_dir = workspace / config["report_dir"]
    _new_directory(output, workspace / "data/interim")
    _new_directory(report_dir, workspace / "artifacts/reports")
    parent = workspace / config["parent_package"]
    verify_pin(parent / "checksums.sha256", config["parent_checksums_sha256"])
    verify_payload(parent)
    parent_records = read_records(parent / "review-ledger.jsonl")
    old_images = {r.source.image_sha256 for r in parent_records}
    fp_path = workspace / config["parent_fingerprints"]
    verify_pin(fp_path, config["parent_fingerprints_sha256"])
    fingerprints = json.loads(fp_path.read_text(encoding="utf-8"))
    if ({r["image_sha256"] for r in fingerprints} != old_images
            or len(fingerprints) != len(old_images)):
        raise DataContractError("Fingerprint cache không khớp ảnh parent")
    old_by_id = {r.sample_id: r for r in parent_records}
    for row in fingerprints:
        expected_ids = sorted(r.sample_id for r in parent_records
                              if r.source.image_sha256 == row["image_sha256"])
        if sorted(row["sample_ids"]) != expected_ids:
            raise DataContractError("Fingerprint cache không khớp membership parent")
    candidates: list[CandidateAnchor] = []
    roots = {}
    source_pins = {}
    for source in config["sources"]:
        if source["id"] not in {"scb_head", "scb_hrw", "roboflow_v1"}:
            raise DataContractError("Chỉ dùng SCB Head/HRW hoặc RF v1; Discuss bị loại")
        verify_pin(Path(source["archive"]), source["archive_sha256"])
        audit_path = workspace / source["audit"]
        verify_pin(audit_path, source["audit_sha256"])
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        if {int(k): v for k, v in audit["source_names"].items()} != source["source_names"]:
            raise DataContractError("Namespace class khác source đã pin")
        roots[source["id"]] = workspace / source["root"]
        anchors = inventory_anchors(
            audit, source_id=source["id"], source_root=roots[source["id"]],
            archive_sha256=source["archive_sha256"], strata_by_class=source["strata_by_class"],
            rank_namespace=selection["rank_namespace"], archive_path=Path(source["archive"]),
            archive_prefix=source["archive_prefix"],
            image_prefix=source.get("image_prefix", "images/train/"),
        )
        candidates.extend(anchors)
        source_pins[source["id"]] = {
            "archive_sha256": source["archive_sha256"], "audit_sha256": source["audit_sha256"],
            "strict_train_anchors": len(anchors),
        }
        print(f"{source['id']}: {len(anchors)} anchors đã kiểm ZIP", flush=True)
    aliases: dict[str, set[str]] = defaultdict(set)
    for row in candidates:
        aliases[row.source_image_sha256].add(f"{row.source_id}:{row.source_image_relpath}")
    unique = unique_anchors(candidates, old_images)
    images = []
    for row in unique:
        with Image.open(source_file(roots[row.source_id], row.source_image_relpath)) as image:
            if image.size != (row.width, row.height):
                raise DataContractError("Kích thước ảnh khác audit")
            images.append(ReviewImage(row, difference_hash(image)))
    chosen = diverse_shortlist(images, selection["review_budget"])
    output.mkdir(parents=True)
    report_dir.mkdir(parents=True)
    (output / "crops").mkdir()
    (output / "review").mkdir()
    write_selection(output / "pool.jsonl", [
        {"source_id": r.anchor.source_id, "image_sha256": r.anchor.source_image_sha256,
         "image_relpath": r.anchor.source_image_relpath, "dhash": r.dhash,
         "exact_aliases": sorted(aliases[r.anchor.source_image_sha256])} for r in images
    ])
    proposals = []
    panels = []
    for number, item in enumerate(chosen, 1):
        anchor = item.anchor
        sample_id = f"{config.get('sample_id_prefix', 'EXP-SCB')}-{number:03d}"
        row = anchor.to_dict(sample_id)
        xyxy = row["source_anchor_xyxy"]
        bounds = [math.floor(xyxy[0]), math.floor(xyxy[1]),
                  math.ceil(xyxy[2]), math.ceil(xyxy[3])]
        crop_path = output / "crops" / f"{sample_id}.png"
        with Image.open(source_file(roots[anchor.source_id], anchor.source_image_relpath)) as im:
            source = im.convert("RGB")
            source.crop(bounds).save(crop_path)
            drawn = source.copy()
            ImageDraw.Draw(drawn).rectangle(bounds, outline="red", width=4)
            panel = Image.new("RGB", (600, 420), "white")
            panel.paste(ImageOps.contain(drawn, (600, 370)), (0, 35))
            ImageDraw.Draw(panel).text((8, 8), f"{sample_id} | {anchor.stratum}", fill="black")
            panel.save(output / "review" / f"{sample_id}.jpg")
            panels.append(panel)
        row.update({
            "selection_reason": "draft_dhash_diversity_largest_anchor_no_target_mapping",
            "exact_aliases": sorted(aliases[anchor.source_image_sha256]),
            "status": "draft_pending_owner_acceptance", "usage": "review_only", "split": None,
            "leakage_group_id": None, "training_eligible": False,
            "phone_use": "unknown", "looking_around": "unknown",
            "target_values": [None, None], "target_mask": [0, 0],
            "proposed_xyxy": bounds, "crop_path": crop_path.relative_to(workspace).as_posix(),
            "crop_sha256": sha256_file(crop_path), "dhash": item.dhash,
            "nearest_parent_images": nearest_evidence(
                item.dhash, anchor.source_image_sha256, fingerprints, selection["nearest_count"],
            ),
            "qa_status": "pending_visual_review",
        })
        proposals.append(row)
    for offset in range(0, len(panels), 6):
        sheet = Image.new("RGB", (1800, 840), "white")
        for index, panel in enumerate(panels[offset:offset + 6]):
            sheet.paste(panel, ((index % 3) * 600, (index // 3) * 420))
        sheet.save(output / "review" / f"sheet-{offset // 6 + 1:02d}.jpg")
    pending_groups = []
    for record in parent_records:
        if record.usage != "review_only":
            continue
        fingerprint = next(r for r in fingerprints
                           if r["image_sha256"] == record.source.image_sha256)
        neighbors = nearest_evidence(fingerprint["dhash"], record.source.image_sha256,
                                     fingerprints, selection["nearest_count"])
        for neighbor in neighbors:
            neighbor["parent_usages"] = sorted({old_by_id[s].usage
                                                for s in neighbor["sample_ids"]})
            neighbor["parent_groups"] = sorted({old_by_id[s].group.leakage_group_id
                                                 for s in neighbor["sample_ids"]
                                                 if old_by_id[s].group is not None
                                                 and old_by_id[s].group.leakage_group_id})
        pending_groups.append({"sample_id": record.sample_id,
                               "status": "draft_relation_triage_not_group_approval",
                               "nearest_parent_images": neighbors})
    write_json(report_dir / "candidates.json", proposals)
    write_json(report_dir / "existing-group-triage.json", pending_groups)
    summary = {
        "status": "draft_pending_owner_acceptance", "git_commit": git_commit(),
        "config_sha256": sha256_file(config_path), "source_pins": source_pins,
        "parent_checksums_sha256": config["parent_checksums_sha256"],
        "parent_fingerprints_sha256": config["parent_fingerprints_sha256"],
        "source_anchor_count": len(candidates),
        "unique_source_images": len(aliases),
        "exact_parent_overlap_images": len(set(aliases) & old_images),
        "unique_new_pool_images": len(unique), "review_budget": selection["review_budget"],
        "selected_count": len(proposals), "selected_source_counts": dict(Counter(
            r["source_id"] for r in proposals)),
        "selected_stratum_counts": dict(Counter(r["stratum"] for r in proposals)),
        "pool_sha256": sha256_file(output / "pool.jsonl"),
        "candidates_sha256": sha256_file(report_dir / "candidates.json"),
        "group_triage_sha256": sha256_file(report_dir / "existing-group-triage.json"),
        "training_eligible": False, "canonical_mutation": False,
        "test_handling": (
            "Chỉ dùng fingerprint cache cũ cho QA leakage; không đọc ảnh test hoặc metrics."
        ),
        "limitations": ["Budget là khối lượng review đề xuất, không quota nhãn hoặc gate model.",
                        "dHash không chứng minh near-duplicate hoặc độc lập cảnh.",
                        "Anchor nguồn chưa phải bbox person/context được duyệt.",
                        "Mọi target mới unknown; đề xuất thị giác cần owner nghiệm thu."],
    }
    write_json(report_dir / "summary.json", summary)
    write_json(output / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parents[3]
    print(json.dumps(build_expansion(args.config, workspace), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
