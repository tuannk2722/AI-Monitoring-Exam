"""Ảnh input224 và provenance Draft; chỉ PIL, không load model hoặc inference."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .pilot_inputs import verify_pin
from .targeted_review_package import _source


@dataclass(frozen=True)
class InputEvidence:
    candidate_id: str
    bucket: str
    source_path: str
    source_sha256: str
    crop_path: str
    crop_sha256: str
    input_path: str
    input_sha256: str
    input_pixel_sha256: str
    crop_size: tuple[int, int]
    resized_size: tuple[int, int]
    pad_left_top: tuple[int, int]
    input_scale: float
    proposed_states: tuple[str, str]
    source_id: str
    visual_family_hint: str


@dataclass(frozen=True)
class VisualEvidenceFinding:
    """Nhận xét từng ảnh, không là TargetReview/approval/acceptance threshold."""

    sample_id: str
    source_evidence: str
    crop_evidence: str
    input224_evidence: str
    final_reason: str
    phone_roi_input224_xyxy: tuple[int, int, int, int] | None = None

    def __post_init__(self) -> None:
        if (any(v not in {"clear", "ambiguous", "lost"} for v in
                (self.source_evidence, self.crop_evidence, self.input224_evidence))
                or not self.sample_id or not self.final_reason.strip()):
            raise DataContractError("Nhận xét evidence phải rõ trạng thái và lý do")
        if self.phone_roi_input224_xyxy is not None:
            left, top, right, bottom = self.phone_roi_input224_xyxy
            if not (0 <= left < right <= 224 and 0 <= top < bottom <= 224):
                raise DataContractError("Phone ROI mô tả phải nằm trong native224")


def summarize_findings(findings: list[VisualEvidenceFinding],
                       expected_ids: set[str]) -> dict[str, Any]:
    ids = [finding.sample_id for finding in findings]
    if len(set(ids)) != len(ids) or set(ids) != expected_ids:
        raise DataContractError("Visual QA thiếu, trùng hoặc thêm ID ngoài scope")
    return {
        "records": len(findings),
        "source": dict(Counter(f.source_evidence for f in findings)),
        "crop": dict(Counter(f.crop_evidence for f in findings)),
        "input224": dict(Counter(f.input224_evidence for f in findings)),
        "roi_recorded": sum(f.phone_roi_input224_xyxy is not None for f in findings),
        "interpretation": "clear/ambiguous/lost là nhận xét qualitative, không metric/gate mới.",
        "owner_approved": False,
    }


def write_findings(workspace: Path, observations: Path, evidence_file: Path,
                   candidates: Path, report: Path) -> dict[str, Any]:
    """Ghép QA đã xem với pins; không suy qualitative thành target label/approval."""
    workspace = workspace.resolve()
    report = report.resolve()
    observations, evidence_file, candidates = (p.resolve() for p in
                                                (observations, evidence_file, candidates))
    if not report.is_relative_to(workspace / "artifacts/reports"):
        raise DataContractError("Report phải nằm trong artifacts/reports")
    value = json.loads(observations.read_text(encoding="utf8"))
    raw_rows = [json.loads(line) for line in candidates.read_text(encoding="utf8").splitlines()]
    selected = {row["candidate_id"]: row for row in raw_rows if row["bucket"] in {"B", "D"}}
    rois = value["manual_roi_input224"]
    findings = [VisualEvidenceFinding(row[0], row[1], row[2], row[3], row[4],
                tuple(rois[row[0]]) if row[0] in rois else None)
                for row in value["observations"]]
    summary = summarize_findings(findings, set(selected))
    evidence = {row["candidate_id"]: row for row in
                json.loads(evidence_file.read_text(encoding="utf8"))}
    for sid, row in selected.items():
        _source(row, workspace)
        pinned = evidence[sid]
        for kind, root in (("crop", "data/interim"), ("input", "outputs")):
            path = _inside(workspace, pinned[f"{kind}_path"], root)
            verify_pin(path, pinned[f"{kind}_sha256"])
        if (pinned["source_sha256"] != row["source_image_sha256"]
                or pinned["crop_sha256"] != row["crop_sha256"]):
            raise DataContractError("Evidence source/crop SHA khác candidate R7")
    outputs = [report / name for name in
               ("input224-findings.json", "input224-summary.json", "input224-audit.md",
                "ownership-findings.json", "ownership-audit.md")]
    if any(path.exists() for path in outputs):
        raise DataContractError("Report findings phải mới; không ghi đè phiên bản đã xuất")
    report.mkdir(parents=True, exist_ok=True)
    rows = []
    for finding in findings:
        source = selected[finding.sample_id]
        rows.append({**asdict(finding), "bucket": source["bucket"],
                     "source_id": source["source_id"], "domain": source["domain"],
                     "person_unit_hint_r7": source["person_unit_hint"],
                     "r7_proposed_states": source["proposed_states"],
                     "owner_approved": False, "canonical_mask": [0, 0],
                     "training_eligible": False, "evidence_pins": evidence[finding.sample_id]})
    summary["by_bucket_and_r7_phone_polarity"] = {
        bucket: {state: summarize_findings(sub := [f for f in findings
                 if selected[f.sample_id]["bucket"] == bucket and
                 selected[f.sample_id]["proposed_states"][0] == state], {f.sample_id for f in sub})
                 for state in ("P", "N", "U")}
        for bucket in ("B", "D")}
    summary["input_pins"] = {p.relative_to(workspace).as_posix(): sha256_file(p)
                             for p in (observations, evidence_file, candidates, Path(__file__))}
    summary["review_completed"] = value["review_completed"]
    write_json(outputs[0], {"status": value["status"], "findings": rows})
    write_json(outputs[1], summary)
    counts = Counter(row["bucket"] for row in rows)
    lines = ["# Kiểm evidence sau preprocessing224 — R7 Draft", "",
             f"Đã xem {counts['B']} B và{counts['D']} D qua sheets đã ghi trong JSON "
             "gồm source/crop/native224/nearest448. "
             "Một số device/visibility flags đã xem thêm source gốc như ghi từng hàng. "
             "Dùng RGB/BILINEAR letterbox224/fill[124,116,104] từ E003 đã pin; PNG trước "
             "normalize, không inference. Nearest448 không thêm thông tin. Clear/ambiguous/lost "
             "là nhận xét qualitative, không threshold hoặc acceptance gate mới.", "",
             "R7 crop/nhãn giữ bất biến. Source label proposal và input224 usability là hai "
             "vấn đề khác nhau: ambiguity224 không tự downgrade P nguồn rõ. Ca source thiếu "
             "device/own-workarea evidence cần owner review. Supplemental delta chỉ là Draft; "
             "root final recrop/owner overrides có precedence và cần xem ảnh mới.", "",
             "| ID | R7 phone/looking | Source/crop/224 | Lý do cuối cho QA |",
             "|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['sample_id']} | {'/'.join(row['r7_proposed_states'])} | "
                     f"{row['source_evidence']}/{row['crop_evidence']}/"
                     f"{row['input224_evidence']} | {row['final_reason']} |")
    outputs[2].write_text("\n".join(lines) + "\n", encoding="utf8")
    crowded = [row for row in rows if row["bucket"] == "D"]
    ownership_overrides = value["ownership_evidence_overrides"]
    cooccurrence_ids = value["visible_cooccurrence_proposal_ids"]
    crowded_ids = {row["sample_id"] for row in crowded}
    if (not set(ownership_overrides).issubset(crowded_ids)
            or not set(cooccurrence_ids).issubset(crowded_ids)):
        raise DataContractError("Ownership/đồng dương nhận xét ngoài ID crowded được xem")
    visibility_u_ids = {row["sample_id"] for row in crowded if row["r7_proposed_states"][0] == "U"}
    for row in crowded:
        sid = row["sample_id"]
        row["ownership_evidence"] = ownership_overrides.get(sid, (
            "ownership_or_observation_unknown_retained" if sid in visibility_u_ids else
            "direct_hand_or_own_desk_lap_link_visible"))
        row["cooccurrence_visible_support"] = (
            "phone_and_away_from_visible_own_workarea_proposal_pending_owner"
            if sid in cooccurrence_ids else "not_proven_both_positive")
    ownership_summary = {
        "status": "draft_visual_ownership_review_not_approval", "records": len(crowded),
        "r7_combinations": dict(Counter("/".join(row["r7_proposed_states"]) for row in crowded)),
        "ownership_evidence": dict(Counter(row["ownership_evidence"] for row in crowded)),
        "visible_cooccurrence_proposal_ids": cooccurrence_ids,
        "owner_approved_actual_cooccurrence_count": 0,
        "interpretation": "39 crowded không là39 co-occurrence; P/P nguồn vẫn Draft/task review.",
        "findings": crowded,
    }
    write_json(outputs[3], ownership_summary)
    lines = [f"# Crowded ownership/co-occurrence —{len(crowded)} R7 Draft", "",
             f"Đã xem source/crop/native224/nearest448 từng{len(crowded)} D. "
             "Chỉ D009/D021 có cả mobile "
             "gắn anchor và hướng nhìn ngoài vùng bài nhìn được; đây là visible support "
             "cho P/P proposal, chưa owner chốt task/gaze, không phải2 co-occurrence Accepted. "
             "Các crop nhiều người/phone không tự thành đồng dương. D050 là phone P/looking N.", "",
             "D006/D025/D033 cần device review; D010 cần explicit unit, D026 phone ở teacher "
             "khác writer, D027 cần recrop để giữ device. Root final override/recrop sẽ thay "
             "proposal mới, không sửa R7. Các phone U về ownership/visibility vẫn U. "
             "D044/D046 source P rõ hơn224, lựa chọn usability cần owner; "
             "không đặt ngưỡng mới.", "",
             "| ID | R7 | Attribution/evidence | Nhận xét |", "|---|---|---|---|"]
    for row in crowded:
        lines.append(f"| {row['sample_id']} | {'/'.join(row['r7_proposed_states'])} | "
                     f"{row['ownership_evidence']} | {row['final_reason']} |")
    outputs[4].write_text("\n".join(lines) + "\n", encoding="utf8")
    return summary


def letterbox_geometry(size: tuple[int, int], image_size: int
                       ) -> tuple[tuple[int, int], tuple[int, int]]:
    """Đúng phép round/min/max và padding của training.data.letterbox."""
    if type(image_size) is not int or image_size <= 0 or any(v <= 0 for v in size):
        raise DataContractError("Kích thước letterbox phải dương")
    scale = image_size / max(size)
    resized = tuple(max(1, min(image_size, round(v * scale))) for v in size)
    width, height = resized
    return (width, height), ((image_size - width) // 2, (image_size - height) // 2)


def letterbox_rgb(image: Image.Image, image_size: int,
                  fill: tuple[int, int, int]) -> Image.Image:
    """RGB/BILINEAR/full-context, parity với transform trainer đã pin."""
    if len(fill) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in fill):
        raise DataContractError("Fill phải gồm ba RGB byte")
    resized, offset = letterbox_geometry(image.size, image_size)
    result = Image.new("RGB", (image_size, image_size), fill)
    result.paste(image.convert("RGB").resize(resized, Image.Resampling.BILINEAR), offset)
    return result


def _inside(workspace: Path, relative: str, root: str) -> Path:
    path = (workspace / relative).resolve()
    if not path.is_relative_to(workspace / root):
        raise DataContractError(f"Path phải nằm trong {root}")
    return path


def _panel(workspace: Path, row: dict[str, Any], evidence: InputEvidence,
           panel_size: tuple[int, int], source_width: int, crop_width: int,
           nearest_scale: int, font: ImageFont.FreeTypeFont | ImageFont.ImageFont
           ) -> Image.Image:
    width, height = panel_size
    panel = Image.new("RGB", panel_size, "white")
    draw = ImageDraw.Draw(panel)
    draw.text((12, 6), f"{evidence.candidate_id} | {evidence.source_id} | "
              f"R7 {evidence.proposed_states[0]}/{evidence.proposed_states[1]}",
              fill="black", font=font)
    draw.text((12, 30), "SOURCE / CROP / INPUT224 native / INPUT224 nearest x2",
              fill="black", font=font)
    with Image.open(workspace / evidence.source_path) as original:
        source = original.convert("RGB")
    box = row["xyxy"]
    ImageDraw.Draw(source).rectangle(box, outline="red", width=max(2, max(source.size) // 180))
    with Image.open(workspace / evidence.crop_path) as original:
        crop = original.convert("RGB")
    with Image.open(workspace / evidence.input_path) as original:
        model_input = original.convert("RGB")
    y = 62
    area_height = height - y - 8
    source = ImageOps.contain(source, (source_width, area_height), Image.Resampling.BILINEAR)
    crop = ImageOps.contain(crop, (crop_width, area_height), Image.Resampling.BILINEAR)
    panel.paste(source, (10, y + (area_height - source.height) // 2))
    panel.paste(crop, (source_width + 24, y + (area_height - crop.height) // 2))
    input_x = source_width + crop_width + 42
    panel.paste(model_input, (input_x, y))
    nearest = model_input.resize((model_input.width * nearest_scale,
                                 model_input.height * nearest_scale), Image.Resampling.NEAREST)
    panel.paste(nearest, (input_x + model_input.width + 18, y))
    draw.rectangle((0, 0, width - 1, height - 1), outline="#777777")
    return panel


def build(config_path: Path, workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    config = load_yaml(config_path)
    if config["status"] != "draft_visual_evidence_only" or config["training_eligible"] is not False:
        raise DataContractError("Chỉ audit Draft, không training/release")
    for key in ("candidates", "package_checksums", "preprocessing_config", "preprocessing_code"):
        pin = config[key]
        verify_pin(workspace / pin["path"], pin["sha256"])
    preprocessing = load_yaml(workspace / config["preprocessing_config"]["path"])
    if preprocessing["transform"] != "rgb_letterbox_bilinear_v1":
        raise DataContractError("Transform chưa được hỗ trợ bởi audit")
    image_size = preprocessing["image_size"]
    fill = tuple(preprocessing["fill"])
    output = _inside(workspace, config["output"], "outputs")
    if output.exists():
        raise DataContractError("Output phải là version mới, không ghi đè")
    rows = [json.loads(line) for line in (workspace / config["candidates"]["path"])
            .read_text(encoding="utf8").splitlines()]
    ids = [r["candidate_id"] for r in rows]
    if len(set(ids)) != len(rows):
        raise DataContractError("Candidate IDs trùng")
    # Preflight mọi source/crop trước mutation; không đọc processed/evaluation media.
    for row in rows:
        if (row.get("known_evaluation_family") is not False or row["training_eligible"] is not False
                or row["canonical_mask"] != [0, 0] or row["split"] is not None):
            raise DataContractError("Audit chỉ dùng candidate Draft ngoài evaluation")
        _source(row, workspace)
        crop_file = _inside(workspace, row["crop_path"], "data/interim")
        verify_pin(crop_file, row["crop_sha256"])
    output.mkdir(parents=True)
    (output / "input224").mkdir()
    (output / "panels").mkdir()
    evidence_rows: list[InputEvidence] = []
    for row in sorted(rows, key=lambda r: r["candidate_id"]):
        source_path = _source(row, workspace)
        with Image.open(source_path) as original:
            source = original.convert("RGB")
        with Image.open(workspace / row["crop_path"]) as original:
            crop = original.convert("RGB")
        expected = source.crop(row["xyxy"])
        if expected.size != crop.size or expected.tobytes() != crop.tobytes():
            raise DataContractError("Crop không khớp source/xyxy đã pin")
        model_input = letterbox_rgb(crop, image_size, fill)
        path = output / "input224" / f"{row['candidate_id']}.png"
        model_input.save(path)
        resized, offset = letterbox_geometry(crop.size, image_size)
        evidence_rows.append(InputEvidence(
            row["candidate_id"], row["bucket"], source_path.relative_to(workspace).as_posix(),
            row["source_image_sha256"], row["crop_path"], row["crop_sha256"],
            path.relative_to(workspace).as_posix(), sha256_file(path),
            hashlib.sha256(model_input.tobytes()).hexdigest(), crop.size, resized, offset,
            image_size / max(crop.size), tuple(row["proposed_states"]), row["source_id"],
            row["visual_family_hint"]))
    lookup = {r["candidate_id"]: r for r in rows}
    font = ImageFont.load_default(size=config["panel_font_size"])
    panel_paths = []
    panel_size = tuple(config["panel_size"])
    for bucket in config["panel_buckets"]:
        selected = [e for e in evidence_rows if e.bucket == bucket]
        for start in range(0, len(selected), config["rows_per_sheet"]):
            batch = selected[start:start + config["rows_per_sheet"]]
            sheet = Image.new("RGB", (panel_size[0], panel_size[1] * len(batch)), "white")
            for index, evidence in enumerate(batch):
                panel = _panel(workspace, lookup[evidence.candidate_id], evidence,
                               panel_size, config["source_width"], config["crop_width"],
                               config["nearest_scale"], font)
                sheet.paste(panel, (0, index * panel_size[1]))
            path = output / "panels" / f"{bucket}-{start // config['rows_per_sheet'] + 1:03}.png"
            sheet.save(path)
            panel_paths.append({"path": path.relative_to(workspace).as_posix(),
                                "sha256": sha256_file(path),
                                "candidate_ids": [e.candidate_id for e in batch]})
    summary: dict[str, Any] = {
        "status": "draft_visual_evidence_only", "training_eligible": False,
        "inference_executed": False, "test_media_read": False, "records": len(evidence_rows),
        "preprocessing": {key: preprocessing[key] for key in
                          ("transform", "image_size", "fill", "mean", "std")},
        "display_note": "PNG là RGB trước normalize; native224 và nearest448 không thêm evidence.",
        "input_pins": {key: config[key] for key in
                       ("candidates", "package_checksums", "preprocessing_config",
                        "preprocessing_code")},
        "audit_code": {"path": Path(__file__).resolve().relative_to(workspace).as_posix(),
                       "sha256": sha256_file(Path(__file__))},
        "panels": panel_paths,
        "qualitative_findings": "PENDING_VISUAL_REVIEW",
    }
    write_json(output / "input-evidence.json", [asdict(r) for r in evidence_rows])
    write_json(output / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Dựng ảnh QA input224, không inference")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    summary = build(args.config, args.workspace)
    print(json.dumps({"status": summary["status"], "records": summary["records"]}))


if __name__ == "__main__":
    main()
