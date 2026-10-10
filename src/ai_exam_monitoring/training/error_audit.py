"""Kiểm toán lỗi từ predictions đã lưu; không inference, sửa nhãn hoặc mở test."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import TARGET_ORDER, read_records


@dataclass(frozen=True)
class ErrorKey:
    split: str
    sample_id: str
    target: str
    outcome: str


@dataclass(frozen=True)
class VisualFinding:
    split: str
    sample_id: str
    target: str
    outcome: str
    factors: list[str]
    observation: str
    hypothesis: str
    confidence: str
    label_review: str
    acquisition: str

    def __post_init__(self) -> None:
        if (self.split not in {"train", "val"} or self.target not in TARGET_ORDER
                or self.outcome not in {"FN", "FP"} or not self.sample_id
                or not self.factors or len(set(self.factors)) != len(self.factors)
                or self.confidence not in {"cao", "vừa", "thấp"}
                or self.label_review not in {"không thấy mâu thuẫn", "cần owner rà lại"}
                or any(not isinstance(v, str) or not v.strip() for v in
                       [*self.factors, self.observation, self.hypothesis, self.acquisition])):
            raise DataContractError("Nhận xét thị giác không hợp lệ; không tự phê duyệt nhãn")

    @property
    def key(self) -> ErrorKey:
        return ErrorKey(self.split, self.sample_id, self.target, self.outcome)


def prediction_errors(rows: list[dict[str, Any]], split: str,
                      threshold: float) -> list[dict[str, Any]]:
    """Kiểm known/mask/decision và tái lập lỗi đúng ngưỡng của run, không tuning."""
    if split not in {"train", "val"} or not 0 < threshold < 1 or not rows:
        raise DataContractError("Audit chỉ cho phép predictions train/val không rỗng")
    ids: set[str] = set()
    errors = []
    for row in rows:
        sid = row["sample_id"]
        if not isinstance(sid, str) or not sid or sid in ids or row["split"] != split:
            raise DataContractError("Prediction trùng ID hoặc sai split")
        ids.add(sid)
        arrays = [row[k] for k in ("scores", "targets", "mask", "decisions")]
        if any(not isinstance(a, list) or len(a) != 2 for a in arrays):
            raise DataContractError("Prediction phải giữ đúng hai target")
        for index, target in enumerate(TARGET_ORDER):
            score, value, known, decision = (a[index] for a in arrays)
            if (type(score) not in {int, float} or not math.isfinite(score)
                    or not 0 <= score <= 1 or type(known) is not int or known not in {0, 1}
                    or type(decision) is not bool or decision != (score >= threshold)
                    or (known == 0 and value is not None)
                    or (known == 1 and (type(value) is not int or value not in {0, 1}))):
                raise DataContractError("Score/known/mask/decision không khớp hợp đồng")
            if known and decision != bool(value):
                errors.append({**row, "target": target,
                               "outcome": "FN" if value else "FP", "score": score})
    return errors


def validate_findings(findings: list[VisualFinding],
                      errors: dict[str, list[dict[str, Any]]]) -> None:
    """Mọi FN hai split và mọi FP val phải có đúng một nhận xét có provenance."""
    expected = {ErrorKey(s, e["sample_id"], e["target"], e["outcome"])
                for s, rows in errors.items() for e in rows
                if e["outcome"] == "FN" or s == "val"}
    actual = [f.key for f in findings]
    if len(set(actual)) != len(actual) or set(actual) != expected:
        raise DataContractError("Audit thiếu, trùng hoặc thêm lỗi ngoài phạm vi đã định")


def support(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    result = {}
    for i, target in enumerate(TARGET_ORDER):
        counts: Counter[str] = Counter()
        for row in rows:
            if not row["mask"][i]:
                counts["unknown"] += 1
                continue
            positive = row["targets"][i] == 1
            predicted = row["scores"][i] >= threshold
            counts["positive" if positive else "negative"] += 1
            counts[("TP" if predicted else "FN") if positive else
                   ("FP" if predicted else "TN")] += 1
        result[target] = {k: counts[k] for k in
                          ("positive", "negative", "unknown", "TP", "FP", "FN", "TN")}
    return result


def build_audit(workspace: Path, run: Path, package: Path, error_file: Path,
                finding_file: Path, source_config: Path, output: Path) -> dict[str, Any]:
    from ai_exam_monitoring.common.config import load_yaml

    workspace = workspace.resolve()
    run, package, error_file, finding_file, source_config = (
        p.resolve() for p in (run, package, error_file, finding_file, source_config))
    output = output.resolve()
    if (not output.is_relative_to(workspace / "artifacts/reports") or output.exists()):
        raise DataContractError("Output phải mới, nằm trong artifacts/reports; không ghi đè")
    config = json.loads((run / "resolved-config.json").read_text(encoding="utf8"))
    record = json.loads((run / "run.json").read_text(encoding="utf8"))
    if (record["status"] != "FINISHED"
            or package.resolve() != (workspace / config["dataset"]).resolve()
            or sha256_file(package / "checksums.sha256") != config["payload_sha256"]):
        raise DataContractError("Run/dataset pin không khớp")
    for name, digest in json.loads((run / "checksums.json").read_text(encoding="utf8")).items():
        path = (run / name).resolve()
        if not path.is_relative_to(run.resolve()) or sha256_file(path) != digest:
            raise DataContractError("Artifact run thay đổi")
    manifests = read_records(package / "manifest.jsonl")
    if any(r.group is None for r in manifests):
        raise DataContractError("Manifest thiếu group đã review")
    manifest = {r.sample_id: r for r in manifests}
    if len(manifest) != len(manifests):
        raise DataContractError("Manifest trùng ID")
    errors = json.loads(error_file.read_text(encoding="utf8"))
    if set(errors) != {"train", "val"}:
        raise DataContractError("Error artifact phải chỉ chứa train/val")
    review = json.loads(finding_file.read_text(encoding="utf8"))
    if review["status"] != "draft_pending_owner_review":
        raise DataContractError("Audit không có quyền tự accept/relabel")
    findings = [VisualFinding(**r) for r in review["findings"]]
    validate_findings(findings, errors)
    source_roots = load_yaml(source_config)["source_roots"]
    predictions = {}
    summary = {}
    pins = {}
    for split in ("train", "val"):
        path = run / f"predictions-{split}.json"
        rows = json.loads(path.read_text(encoding="utf8"))
        rebuilt = prediction_errors(rows, split, config["threshold"])
        def key(e: dict[str, Any]) -> tuple[str, str, str]:
            return e["sample_id"], e["target"], e["outcome"]

        if sorted(rebuilt, key=key) != sorted(errors[split], key=key):
            raise DataContractError("Danh sách lỗi không tái lập từ predictions")
        if {r["sample_id"] for r in rows} != {
                r.sample_id for r in manifests if r.usage == split}:
            raise DataContractError("Prediction membership khác manifest")
        for row in rows:
            r = manifest[row["sample_id"]]
            if r.group is None:
                raise DataContractError("Prediction thiếu group")
            if (row["targets"] != list(r.target_values) or row["mask"] != list(r.target_mask)
                    or row["source_id"] != r.source.source_id
                    or row["group_id"] != r.group.leakage_group_id):
                raise DataContractError("Prediction nhãn/source/group khác manifest")
        sources = sorted({r["source_id"] for r in rows})
        groups = sorted({r["group_id"] for r in rows})
        summary[split] = {
            "records": len(rows), "groups": len(groups),
            "targets": support(rows, config["threshold"]),
            "by_source": {s: {"records": len(sub := [r for r in rows if r["source_id"] == s]),
                              "groups": len({r["group_id"] for r in sub}),
                              "targets": support(sub, config["threshold"])} for s in sources},
            "by_group": {g: {"records": len(sub := [r for r in rows if r["group_id"] == g]),
                             "targets": support(sub, config["threshold"])} for g in groups},
        }
        predictions[split] = {r["sample_id"]: r for r in rows}
        pins[path.relative_to(workspace).as_posix()] = sha256_file(path)
    audit = []
    # Chỉ decode source/crop của những ID đã được nhận xét; không mở media test.
    dimensions = {}
    for finding in findings:
        r = manifest[finding.sample_id]
        if r.usage != finding.split or r.crop is None or r.group is None:
            raise DataContractError("Không mở ảnh ngoài split train/val đã pin")
        paths = [package / r.crop.crop_relpath,
                 workspace / source_roots[r.source.source_id] / r.source.image_relpath]
        expected = [r.crop.crop_sha256, r.source.image_sha256]
        for path, digest in zip(paths, expected, strict=True):
            if not path.resolve().is_relative_to(workspace) or sha256_file(path) != digest:
                raise DataContractError("Source/crop path hoặc SHA thay đổi")
        with Image.open(paths[0]) as image:
            width, height = image.size
        with Image.open(paths[1]) as image:
            if image.size != (r.source.image_width, r.source.image_height):
                raise DataContractError("Source dimension khác manifest")
            box = r.crop.context_box
            crop_pixels = image.convert("RGB").crop((box.xmin, box.ymin, box.xmax, box.ymax))
            with Image.open(paths[0]) as cropped:
                if crop_pixels.size != cropped.size or crop_pixels.tobytes() != (
                        cropped.convert("RGB").tobytes()):
                    raise DataContractError("Crop pixels không khớp source/context box")
        dimensions[r.sample_id] = [width, height]
        row = predictions[finding.split][r.sample_id]
        audit.append({**asdict(finding), "score": row["scores"][TARGET_ORDER.index(finding.target)],
                      "source_id": r.source.source_id, "group_id": r.group.leakage_group_id,
                      "crop_size": [width, height], "input_scale": config["image_size"] /
                      max(width, height), "source_path": paths[1].relative_to(workspace).as_posix(),
                      "crop_path": paths[0].relative_to(workspace).as_posix(),
                      "source_sha256": expected[1], "crop_sha256": expected[0],
                      "existing_label_reason": getattr(r, finding.target).reason})
    for path in [error_file, finding_file, source_config, package / "manifest.jsonl",
                 package / "review-ledger.jsonl", package / "release.json",
                 package / "checksums.sha256", run / "resolved-config.json", run / "run.json"]:
        pins[path.relative_to(workspace).as_posix()] = sha256_file(path)
    summary["visual_audit"] = {
        "error_cells": len(audit), "unique_images": len(dimensions),
        "fn_cells": sum(r["outcome"] == "FN" for r in audit),
        "label_recheck_cells": sum(r["label_review"] == "cần owner rà lại" for r in audit),
        "factor_counts": dict(sorted(Counter(f for r in audit for f in r["factors"]).items())),
        "test_media_read": False, "inference_executed": False,
    }
    output.mkdir(parents=True, exist_ok=False)
    payload = {"status": "draft_pending_owner_review", "experiment_id": config["experiment_id"],
               "threshold": config["threshold"], "image_size": config["image_size"],
               "observation_not_causal_proof": True, "input_pins": pins, "findings": audit}
    for name, value in [("audit.json", payload), ("summary.json", summary)]:
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                             allow_nan=False) + "\n", encoding="utf8")
    lines = ["# Kiểm toán từng lỗi E003 — nhận xét Draft", "",
             f"Đã xem crop, ảnh gốc và input{config['image_size']}. "
             "Nhận xét không chứng minh nguyên nhân nhân quả; "
             "không tự đổi nhãn accepted. Factor không liệt kê nghĩa là chưa khẳng định, "
             "không đồng nghĩa đã chứng minh vắng mặt. Test media không mở.", "",
             "| Split / ID / target | Score | Crop | Quan sát | Giả thuyết / ảnh cần bổ sung | "
             "Độ tin cậy / rà nhãn |", "|---|---:|---|---|---|---|"]
    for row in audit:
        observation = row["observation"].replace("|", "/")
        hypothesis = (row["hypothesis"] + " " + row["acquisition"]).replace("|", "/")
        lines.append(f"| {row['split']} / `{row['sample_id']}` / {row['target']} {row['outcome']} "
                     f"| {row['score']:.6f} | {row['crop_size'][0]}×{row['crop_size'][1]} "
                     f"| {observation} | {hypothesis} | {row['confidence']} / "
                     f"{row['label_review']} |")
    (output / "fn-audit.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    return summary


def render_review(workspace: Path, audit_file: Path, run: Path, output: Path) -> dict[str, str]:
    """Bảng ảnh local có source, crop và input ở kích thước thật; không upload."""
    workspace, output = workspace.resolve(), output.resolve()
    if not output.is_relative_to(workspace / "outputs") or output.exists():
        raise DataContractError("Media output phải mới, nằm trong outputs/")
    audit = json.loads(audit_file.read_text(encoding="utf8"))
    config = json.loads((run / "resolved-config.json").read_text(encoding="utf8"))
    if config["image_size"] != audit["image_size"] or not 0 < config["image_size"] <= 512:
        raise DataContractError("Review layout chỉ hỗ trợ input tối đa512, không đổi config")
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for finding in audit["findings"]:
        if finding["split"] not in {"train", "val"}:
            raise DataContractError("Review không mở test media")
        unique.setdefault((finding["split"], finding["sample_id"]), finding)
    output.mkdir(parents=True, exist_ok=False)
    font = ImageFont.load_default(size=17)
    for split in ("val", "train"):
        rows = [r for (s, _), r in unique.items() if s == split]
        for page, start in enumerate(range(0, len(rows), 4), 1):
            sheet = Image.new("RGB", (1600, 1680), "white")
            draw = ImageDraw.Draw(sheet)
            for index, row in enumerate(rows[start:start + 4]):
                top = index * 420
                draw.text((8, top + 5), f"{split} {row['sample_id']} | source / crop / "
                          f"input {config['image_size']} (native pixels)", font=font, fill="black")
                source_path, crop_path = (workspace / row[k] for k in ("source_path", "crop_path"))
                for path, key in ((source_path, "source_sha256"), (crop_path, "crop_sha256")):
                    if not path.resolve().is_relative_to(workspace) or (
                            sha256_file(path) != row[key]):
                        raise DataContractError("Review media path/SHA khác audit")
                with Image.open(source_path) as image:
                    source = ImageOps.contain(image.convert("RGB"), (600, 375))
                with Image.open(crop_path) as image:
                    cropped = image.convert("RGB")
                sheet.paste(source, (8, top + 40))
                sheet.paste(ImageOps.contain(cropped, (420, 375)), (628, top + 40))
                scale = config["image_size"] / max(cropped.size)
                size = tuple(max(1, min(config["image_size"], round(v * scale)))
                             for v in cropped.size)
                model_input = Image.new("RGB", (config["image_size"], config["image_size"]),
                                        tuple(config["fill"]))
                model_input.paste(cropped.resize(size, Image.Resampling.BILINEAR),
                                  ((config["image_size"] - size[0]) // 2,
                                   (config["image_size"] - size[1]) // 2))
                sheet.paste(model_input, (1072, top + 48))
            sheet.save(output / f"{split}-review-{page:02}.png")
    receipt = {p.relative_to(workspace).as_posix(): sha256_file(p)
               for p in sorted(output.glob("*.png"))}
    (output / "media-checksums.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run", "package", "errors", "findings", "source-config", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--media-output", type=Path)
    args = parser.parse_args()
    summary = build_audit(args.workspace, args.run, args.package, args.errors,
                          args.findings, args.source_config, args.output)
    if args.media_output:
        render_review(args.workspace, args.output / "audit.json", args.run, args.media_output)
    print(json.dumps({"output": str(args.output), "coverage": summary["visual_audit"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
