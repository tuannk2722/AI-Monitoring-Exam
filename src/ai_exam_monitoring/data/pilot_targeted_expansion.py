"""Hàng đợi targeted có provenance; không tự gán nhãn, split hoặc release."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .image_similarity import difference_hash
from .pilot_inputs import verify_pin
from .pilot_schema import PixelBox, read_records
from .pilot_selection import CandidateAnchor, source_file
from .pilot_source_candidates import context_proposal, pixel_box
from .yolo import YoloAnnotation


def validate_budget(value: Any, name: str, *, minimum: int = 0) -> int:
    """Chặn slice âm, bool/float và read(-1) trước khi tạo version mới."""
    if type(value) is not int or value < minimum:
        raise DataContractError(f"{name} phải là integer >= {minimum}")
    return int(value)


def validate_fingerprints(references: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Chỉ dùng cache metadata; thiếu evaluation phải dừng trước download/media."""
    for row in references:
        value = validate_budget(row["dhash"], "cached dhash")
        if value >= 1 << 64 or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None:
            raise DataContractError("Cached fingerprint không hợp lệ")
    evaluation = [r for r in references if {"val", "test"}.intersection(r["usages"])]
    if not evaluation:
        raise DataContractError("Thiếu cached fingerprint evaluation; không đọc media để bù")
    return evaluation


def lineage(relative: str) -> str:
    """Tên gốc chỉ dùng cách ly re-export, không gọi là session/person."""
    return Path(relative).stem.split(".rf.")[0].lower()


@dataclass(frozen=True)
class TargetedHint:
    anchor: CandidateAnchor
    class_name: str
    kind: str
    context: PixelBox
    person_hint: PixelBox | None
    method: str
    dhash: int
    body_count: int
    source_classes: tuple[str, ...]
    nearest_parent: dict[str, Any]
    nearest_evaluation: dict[str, Any]


def parse_owner_cells(text: str) -> list[dict[str, str]]:
    """Nhập cột quyết định theo đúng cell; chỉ riêng row phone008 cần lời làm rõ."""
    result = []
    for line in text.splitlines():
        columns = [p.strip() for p in line.split("|")[1:-1]]
        if len(columns) != 7:
            continue
        match = re.fullmatch(r"(train|val) / `([^`]+)` / (phone_use|looking_around) (FN|FP)",
                             columns[0])
        if match is None:
            continue
        decision = columns[-1]
        if not re.match(r"^(P|N|U|excluded)(\b|\s|/)", decision):
            raise DataContractError("Quyết định owner phải P/N/U/excluded rõ")
        split, sid, target, outcome = match.groups()
        result.append({"sample_id": sid, "split": split, "target": target,
                       "old_outcome": outcome, "decision": decision})
    if not result or len({(r["sample_id"], r["target"]) for r in result}) != len(result):
        raise DataContractError("Owner review rỗng hoặc trùng cell")
    return result


def nearest(query: int, references: list[dict[str, Any]]) -> dict[str, Any]:
    if not references:
        raise DataContractError("Thiếu fingerprint reference; không chứng minh độc lập")
    row = min(references, key=lambda r: ((query ^ r["dhash"]).bit_count(), r["sha256"]))
    return {**row, "distance": (query ^ row["dhash"]).bit_count()}


def diverse_hints(hints: list[TargetedHint], budget: int,
                  excluded: set[str]) -> list[TargetedHint]:
    """Một ảnh mỗi lượt; farthest-first chỉ là rank screening, không gate Accepted."""
    validate_budget(budget, "image budget")
    remaining = sorted((h for h in hints if h.anchor.source_image_sha256 not in excluded),
                       key=lambda h: (h.anchor.rank_sha256, h.anchor.identity))
    best_per_image: dict[str, TargetedHint] = {}
    for hint in remaining:
        best_per_image.setdefault(hint.anchor.source_image_sha256, hint)
    remaining = list(best_per_image.values())
    selected: list[TargetedHint] = []
    distance = {h.anchor.source_image_sha256: 64 for h in remaining}
    while remaining and len(selected) < budget:
        hint = min(remaining, key=lambda h: (-distance[h.anchor.source_image_sha256],
                                            h.anchor.rank_sha256, h.anchor.identity))
        selected.append(hint)
        remaining.remove(hint)
        for other in remaining:
            key = other.anchor.source_image_sha256
            distance[key] = min(distance[key], (hint.dhash ^ other.dhash).bit_count())
    return selected


def local_inventory(source: dict[str, Any], workspace: Path, old_sha: set[str],
                    old_lineages: set[tuple[str, str]]) -> list[dict[str, Any]]:
    """Reuse strict SCB audit; chỉ fingerprint ảnh train chưa nằm trong parent."""
    pin = source["local_audit"]
    path = workspace / pin["path"]
    verify_pin(path, pin["sha256"])
    audit = json.loads(path.read_text(encoding="utf8"))
    names = {int(k): v for k, v in audit["source_names"].items()}
    if names != {int(k): v for k, v in source["classes"].items()}:
        raise DataContractError("SCB namespace khác audit đã pin")
    result = []
    for row in audit["samples"]:
        relative = row["image"]
        if not relative.startswith("images/train/"):
            continue
        if (source["id"], lineage(relative)) in old_lineages:
            continue
        image_path = source_file(workspace / source["root"], relative)
        digest = sha256_file(image_path)
        if digest in old_sha:
            continue
        with Image.open(image_path) as image:
            if image.size != (row["width"], row["height"]):
                raise DataContractError("SCB audit dimensions lệch")
            fingerprint = difference_hash(image)
        result.append({"source": source["id"], "split": "train", "invalid": False,
                       "path": relative, "label_path": row["label"], "sha256": digest,
                       "width": row["width"], "height": row["height"], "dhash": fingerprint,
                       "classes": sorted({names[a["class_id"]] for a in row["annotations"]})})
    return result


def collect(config: dict[str, Any], workspace: Path) -> tuple[list[TargetedHint], dict[str, Any]]:
    parent = read_records(workspace / config["parent_package"] / "review-ledger.jsonl")
    old_sha = {r.source.image_sha256 for r in parent}
    old_lineages = {(r.source.source_id, lineage(r.source.image_relpath)) for r in parent}
    evaluated_sha = {r.source.image_sha256 for r in parent if r.usage in {"val", "test"}}
    metadata = {}
    for pin in config["fingerprint_inputs"]:
        path = workspace / pin["path"]
        verify_pin(path, pin["sha256"])
        for row in json.loads(path.read_text(encoding="utf8")):
            digest = row.get("image_sha256", row.get("sha256"))
            metadata[digest] = int(row["dhash"])
    inventory_path = workspace / config["inventory"]["path"]
    verify_pin(inventory_path, config["inventory"]["sha256"])
    inventory = json.loads(inventory_path.read_text(encoding="utf8"))
    for row in inventory:
        metadata[row["sha256"]] = int(row["dhash"])
    if not evaluated_sha <= set(metadata):
        raise DataContractError("Thiếu cached fingerprint evaluation; không đọc test ảnh để bù")
    # Có thể tính fingerprint train/review-only thiếu; tuyệt đối không decode test/val để bù.
    roots = load_yaml(workspace / config["parent_source_config"]["path"])["source_roots"]
    for row in parent:
        if row.source.image_sha256 not in metadata:
            if row.usage in {"val", "test"}:
                raise DataContractError("Thiếu metadata evaluation")
            path = source_file(workspace / roots[row.source.source_id], row.source.image_relpath)
            verify_pin(path, row.source.image_sha256)
            with Image.open(path) as image:
                metadata[row.source.image_sha256] = difference_hash(image)
    references: list[dict[str, Any]] = []
    for digest in sorted(old_sha):
        rows = [r for r in parent if r.source.image_sha256 == digest]
        references.append({"sha256": digest, "dhash": metadata[digest],
                           "sample_ids": sorted(r.sample_id for r in rows),
                           "usages": sorted({r.usage for r in rows}),
                           "groups": sorted({r.group.leakage_group_id for r in rows
                                             if r.group and r.group.leakage_group_id})})
    evaluation = [r for r in references if {"val", "test"}.intersection(r["usages"])]
    hints = []
    counts: Counter[str] = Counter()
    quarantined = []
    for source in config["sources"]:
        archive = Path(source["archive"])
        verify_pin(archive, source["archive_sha256"])
        names = {int(k): v for k, v in source["classes"].items()}
        sid = source["id"]
        if sid not in roots or sid in {"fpi_det", "scb_discuss"}:
            raise DataContractError("Nguồn ngoài whitelist hiện hành")
        pool = (local_inventory(source, workspace, old_sha, old_lineages)
                if "local_audit" in source else
                [r for r in inventory if r["source"] == source.get("inventory_id", sid)
                 and r["split"] == "train" and not r["invalid"]])
        with zipfile.ZipFile(archive) as zip_source:
            for row in sorted(pool, key=lambda r: r["path"]):
                counts[f"{sid}:strict_train_images"] += 1
                if row["sha256"] in old_sha or (sid, lineage(row["path"])) in old_lineages:
                    counts[f"{sid}:parent_or_lineage"] += 1
                    continue
                near_eval = nearest(row["dhash"], evaluation)
                if near_eval["distance"] <= config["screening"]["evaluation_quarantine_distance"]:
                    counts[f"{sid}:evaluation_quarantine"] += 1
                    quarantined.append({"source_id": sid, "path": row["path"],
                                        "sha256": row["sha256"], "reference": near_eval,
                                        "reason": "similarity_review_flag_not_proven_duplicate"})
                    continue
                label_relative = row.get("label_path") or (
                    row["path"].replace("/images/", "/labels/").rsplit(".", 1)[0] + ".txt")
                prefix = source.get("archive_prefix", "").strip("/")
                label_member = f"{prefix}/{label_relative}".lstrip("/")
                label_bytes = zip_source.read(label_member)
                try:
                    annotations = [(i, YoloAnnotation.parse(line)) for i, line in enumerate(
                        label_bytes.decode("utf8").splitlines(), 1) if line.strip()]
                except DataContractError:
                    counts[f"{sid}:invalid_label"] += 1
                    continue
                if any(a.class_id not in names for _, a in annotations):
                    raise DataContractError("Namespace nguồn thay đổi")
                bodies = [a for _, a in annotations if names[a.class_id] in source["body_classes"]]
                near_parent = nearest(row["dhash"], references)
                for number, annotation in annotations:
                    name = names[annotation.class_id]
                    kind = next((k for k, classes in source["hint_classes"].items()
                                 if name in classes), None)
                    if kind is None:
                        continue
                    draft = context_proposal(annotation, bodies, row["width"], row["height"],
                                             config["screening"]["draft_padding"])
                    rank = hashlib.sha256((config["selection_version"] + "|" + sid + "|" +
                                           row["sha256"] + "|" + str(number)).encode()).hexdigest()
                    anchor = CandidateAnchor(sid, source["archive_sha256"], row["path"],
                                             row["sha256"], label_relative,
                                             hashlib.sha256(label_bytes).hexdigest(), number,
                                             annotation.class_id, row["width"], row["height"],
                                             kind, annotation, rank)
                    person = context_proposal(annotation, bodies, row["width"], row["height"], 0)
                    hints.append(TargetedHint(anchor, name, kind, draft.box,
                                              person.box if person.method == "body_container_hint"
                                              else None, draft.method, row["dhash"], len(bodies),
                                              tuple(sorted(set(row["classes"]))), near_parent,
                                              near_eval))
                    counts[f"{sid}:{kind}_anchors"] += 1
    return hints, {"counts": dict(sorted(counts.items())), "quarantine": quarantined,
                   "parent_fingerprints": references, "test_media_read": False}


def build_screening(config_path: Path, workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    config = load_yaml(config_path)
    if config["status"] != "draft_targeted_preparation" or config["formulation"] != "B":
        raise DataContractError("Chỉ preparation Draft, không Accepted/train")
    for kind, budget in config["screening"]["image_budgets"].items():
        validate_budget(budget, f"image budget {kind}")
    distance = validate_budget(config["screening"]["evaluation_quarantine_distance"],
                               "evaluation quarantine distance")
    if distance > 64:
        raise DataContractError("Evaluation quarantine distance vượt 64-bit dhash")
    for key in ("scope_approval", "parent_checksums", "parent_source_config"):
        pin = config[key]
        verify_pin(workspace / pin["path"], pin["sha256"])
    approval = json.loads((workspace / config["scope_approval"]["path"]).read_text(encoding="utf8"))
    if approval["decision"] != "approve_v7_targeted_preparation_only":
        raise DataContractError("Không kế thừa approval v6/E003")
    output = (workspace / config["screening_output"]).resolve()
    if not output.is_relative_to(workspace / "data/interim") or output.exists():
        raise DataContractError("Screening output phải mới trong interim")
    hints, statistics = collect(config, workspace)
    used: set[str] = set()
    selected = []
    for kind, budget in config["screening"]["image_budgets"].items():
        chosen = diverse_hints([h for h in hints if h.kind == kind], budget, used)
        selected.extend(chosen)
        used.update(h.anchor.source_image_sha256 for h in chosen)
    output.mkdir(parents=True)
    (output / "crops").mkdir()
    (output / "review").mkdir()
    font = ImageFont.load_default(size=16)
    sources = {s["id"]: s for s in config["sources"]}
    rows = []
    for number, hint in enumerate(selected, 1):
        anchor = hint.anchor
        sid = f"V7-SCREEN-{number:03d}"
        prefix = sources[anchor.source_id].get("archive_prefix", "").strip("/")
        with zipfile.ZipFile(sources[anchor.source_id]["archive"]) as archive:
            data = archive.read(f"{prefix}/{anchor.source_image_relpath}".lstrip("/"))
            labels = archive.read(f"{prefix}/{anchor.source_label_relpath}".lstrip("/"))
        if (hashlib.sha256(data).hexdigest() != anchor.source_image_sha256
                or hashlib.sha256(labels).hexdigest() != anchor.source_label_sha256):
            raise DataContractError("Inventory/ZIP bytes lệch")
        image = Image.open(io.BytesIO(data)).convert("RGB")
        if image.size != (anchor.width, anchor.height) or difference_hash(image) != hint.dhash:
            raise DataContractError("Fingerprint/kích thước source lệch")
        source_dir = output / "sources" / anchor.source_id
        local_image = f"images/{anchor.source_image_sha256}.jpg"
        local_label = f"labels/{anchor.source_image_sha256}.txt"
        for relative, payload in [(local_image, data), (local_label, labels)]:
            path = (source_dir / relative).resolve()
            if not path.is_relative_to(source_dir.resolve()):
                raise DataContractError("Path ZIP không an toàn")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        crop_path = output / "crops" / f"{sid}.png"
        crop = image.crop(hint.context.xyxy)
        crop.save(crop_path)
        row = anchor.to_dict(sid)
        row.update({"status": "screening_not_membership", "hint_kind": hint.kind,
                    "source_class_name": hint.class_name, "source_classes": hint.source_classes,
                    "source_root": source_dir.relative_to(workspace).as_posix(),
                    "source_local_image_path": (source_dir / local_image)
                    .relative_to(workspace).as_posix(),
                    "source_local_label_path": (source_dir / local_label)
                    .relative_to(workspace).as_posix(),
                    "source_materialization_note": "Tên local theo SHA để tránh MAX_PATH; "
                    "source_image/label_relpath vẫn giữ nguyên provenance ZIP.",
                    "lineage_hint": lineage(anchor.source_image_relpath), "dhash": hint.dhash,
                    "draft_xyxy": list(hint.context.xyxy), "draft_method": hint.method,
                    "body_count": hint.body_count,
                    "person_hint_xyxy": list(hint.person_hint.xyxy) if hint.person_hint else None,
                    "crop_path": crop_path.relative_to(workspace).as_posix(),
                    "crop_sha256": sha256_file(crop_path), "nearest_parent": hint.nearest_parent,
                    "nearest_evaluation": hint.nearest_evaluation,
                    "canonical_targets": [None, None], "canonical_mask": [0, 0],
                    "usage": "review_only", "split": None, "leakage_group_id": None,
                    "training_eligible": False})
        rows.append(row)
        drawn = image.copy()
        draw = ImageDraw.Draw(drawn)
        draw.rectangle(hint.context.xyxy, outline="red", width=3)
        draw.rectangle(pixel_box(anchor.source_anchor_yolo, *image.size).xyxy,
                       outline="cyan", width=2)
        panel = Image.new("RGB", (900, 590), "white")
        ImageDraw.Draw(panel).text((5, 5), f"{sid} {hint.kind} {anchor.source_id}",
                                  font=font, fill="black")
        ImageDraw.Draw(panel).text((5, 28), f"{hint.class_name} | nearest "
                                  f"eval {hint.nearest_evaluation['distance']} / "
                                  f"parent {hint.nearest_parent['distance']} | {hint.method}",
                                  font=font, fill="black")
        panel.paste(ImageOps.contain(drawn, (550, 520)), (0, 65))
        panel.paste(ImageOps.contain(crop, (340, 520)), (558, 65))
        panel.save(output / "review" / f"{sid}.jpg")
    # Mỗi sheet6panel, đọc raw/crop riêng khi cần detail; không gửi media ra ngoài.
    for start in range(0, len(rows), 6):
        sheet = Image.new("RGB", (2700, 1180), "white")
        for i, row in enumerate(rows[start:start + 6]):
            with Image.open(output / "review" / f"{row['sample_id']}.jpg") as panel:
                sheet.paste(panel, ((i % 3) * 900, (i // 3) * 590))
        sheet.save(output / "review" / f"sheet-{start // 6 + 1:03d}.jpg")
    (output / "screening.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf8")
    write_json(output / "supply.json", statistics)
    result = {"status": "screening_not_membership", "records": len(rows),
              "by_kind": dict(Counter(r["hint_kind"] for r in rows)),
              "config_sha256": sha256_file(config_path),
              "screening_sha256": sha256_file(output / "screening.jsonl"),
              "training_eligible": False, "test_media_read": False}
    write_json(output / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(build_screening(args.config, args.workspace), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
