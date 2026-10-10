"""Đếm funnel từ metadata đã pin; không mở media hoặc quyết định nhãn/split."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json


def read_metadata(path: Path) -> Any:
    """Whitelist định dạng metadata; đường dẫn ảnh không thể được đọc bằng helper này."""
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf8"))
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines()]
    raise DataContractError("Source audit chỉ đọc JSON/JSONL metadata")


def selection_funnel(screened: list[dict[str, Any]],
                     candidates: list[dict[str, Any]]) -> dict[str, int]:
    """Không đổi không được tuyển thành rejected hay accepted."""
    chosen = {(r["screening_set"], r["screening_id"]) for r in candidates}
    keys = {(r["screening_set"], r["sample_id"]) for r in screened}
    if len(keys) != len(screened):
        raise DataContractError("Trùng screening identity")
    selected = sum((r["screening_set"], r["sample_id"]) in chosen for r in screened)
    return {"screened_images": len(screened), "selected_screening_images": selected,
            "not_selected_images": len(screened) - selected, "draft_crops": len(candidates),
            "accepted_crops_r7": 0, "training_eligible_crops_r7": 0}


def remaining_rows(rows: list[dict[str, Any]], parent: list[dict[str, Any]],
                   screened: list[dict[str, Any]], excluded_sha: set[str],
                   source_id: str, hint_classes: set[str]) -> list[dict[str, Any]]:
    """Chỉ còn metadata hints; tên/ảnh unique không chứng minh useful hoặc độc lập."""
    old_sha = {r["source"]["image_sha256"] for r in parent}
    old_names = {(r["source"]["source_id"],
                  Path(r["source"]["image_relpath"]).stem.split(".rf.")[0].lower())
                 for r in parent}
    used_sha = {r["source_image_sha256"] for r in screened}
    result = []
    for row in rows:
        name = Path(row["path"]).stem.split(".rf.")[0].lower()
        if (row["split"] != "train" or row["invalid"]
                or row["sha256"] in old_sha | used_sha | excluded_sha
                or (source_id, name) in old_names
                or not hint_classes.intersection(row["classes"])):
            continue
        result.append({"source_id": source_id, "path": row["path"],
                       "sha256": row["sha256"], "lineage_hint": name,
                       "source_classes": ";".join(row["classes"]),
                       "status": "unreviewed_metadata_hint_not_independent_group"})
    return result


def csv_write(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise DataContractError("CSV audit không được rỗng")
    with path.open("w", encoding="utf8", newline="") as stream:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def public_csv_inventory(metadata: Path, prefix: Path) -> dict[str, int]:
    """Đếm image-info train và prefix bbox; bỏ toàn image group cuối prefix."""
    image_ids: set[str] = set()
    with metadata.open(encoding="utf8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["Subset"] != "train":
                raise DataContractError("Image-info audit chỉ cho train")
            if row["ImageID"] in image_ids:
                raise DataContractError("Image-info ID trùng")
            image_ids.add(row["ImageID"])
    boxed_ids: set[str] = set()
    last, lines = None, 0
    with prefix.open(encoding="utf8", newline="") as stream:
        for row in csv.DictReader(stream):
            last = row["ImageID"]
            boxed_ids.add(last)
            lines += 1
    if last is not None:
        boxed_ids.discard(last)
    return {"total_available_images": len(image_ids),
            "original_train_images": len(image_ids),
            "image_info_index_scanned_images": len(image_ids),
            "annotation_index_scanned_images": len(boxed_ids),
            "bbox_prefix_annotation_rows_read": lines,
            "bbox_prefix_bytes": prefix.stat().st_size}


def build(config_path: Path, workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    config = load_yaml(config_path)
    if config["status"] != "draft_metadata_coverage_audit":
        raise DataContractError("Chỉ audit Draft metadata")
    inputs: dict[str, Any] = {}
    for key, pin in config["inputs"].items():
        path = (workspace / pin["path"]).resolve()
        if not path.is_relative_to(workspace) or sha256_file(path) != pin["sha256"]:
            raise DataContractError(f"Input pin/path sai: {key}")
        inputs[key] = read_metadata(path)
    screenings: list[dict[str, Any]] = []
    pins = list(config["inputs"].values())
    for item in inputs["screening_inventory"]["screenings"]:
        path = (workspace / item["path"]).resolve()
        if not path.is_relative_to(workspace) or sha256_file(path) != item["sha256"]:
            raise DataContractError("Screening pin/path sai")
        pins.append({"path": item["path"], "sha256": item["sha256"]})
        rows = read_metadata(path)
        if len(rows) != item["payload_records"] or len(rows) != item["visual_panels_reviewed"]:
            raise DataContractError("Receipt screening không khớp số dòng")
        screenings.extend({**r, "screening_set": item["id"]} for r in rows)
    candidates = inputs["candidates"]
    if not {(r["screening_set"], r["screening_id"]) for r in candidates} <= {
            (r["screening_set"], r["sample_id"]) for r in screenings}:
        raise DataContractError("Candidate tham chiếu screening thiếu")
    records, unused = [], []
    for source in config["sources"]:
        sid = source["id"]
        screened = [r for r in screenings if r["source_id"] == sid]
        crop = [r for r in candidates if r["source_id"] == sid]
        record: dict[str, Any] = {"source_id": sid, "name": source["name"],
                                  **selection_funnel(screened, crop)}
        if source["kind"] == "roboflow":
            rows = [r for r in inputs["roboflow_inventory"]
                    if r["source"] == source["inventory_id"]]
            supply = inputs[source["supply"]]
            counts = supply["counts"]
            exclusion = {r["sha256"] for r in supply["quarantine"]
                         if r["source_id"] == sid}
            left = remaining_rows(rows, inputs["parent"], screened, exclusion,
                                  sid, set(source["hint_classes"]))
            unused.extend(left)
            record.update(total_available_images=len(rows),
                          original_train_images=sum(r["split"] == "train" for r in rows),
                          annotation_index_scanned_images=len(rows),
                          source_payload_received_images=len(rows),
                          strict_train_supply_rows=counts[f"{sid}:strict_train_images"],
                          parent_lineage_exclusions=counts.get(f"{sid}:parent_or_lineage", 0),
                          near_evaluation_quarantine=counts.get(f"{sid}:evaluation_quarantine", 0),
                          remaining_metadata_hint_rows=len(left),
                          remaining_metadata_hint_unique_sha=len({r["sha256"] for r in left}),
                          remaining_metadata_hint_lineages=len({r["lineage_hint"] for r in left}))
        elif source["kind"] == "scb":
            audit = inputs[source["audit"]]
            archive = next(a for a in inputs["scb_reaudit"]["archives"]
                           if a["id"] == source["archive_id"])
            counts = inputs[source["supply"]]["counts"]
            record.update(total_available_images=audit["image_count"],
                          original_train_images=archive["images_by_split"]["train"],
                          annotation_index_scanned_images=audit["image_count"],
                          source_payload_received_images=audit["image_count"],
                          strict_train_supply_rows=counts[f"{sid}:strict_train_images"],
                          parent_lineage_exclusions=None,
                          near_evaluation_quarantine=counts[f"{sid}:evaluation_quarantine"],
                          remaining_metadata_hint_rows=None,
                          remaining_metadata_hint_unique_sha=None,
                          remaining_metadata_hint_lineages=None)
        else:
            record.update(total_available_images=source.get("available_images"),
                          original_train_images=source.get("available_images"),
                          annotation_index_scanned_images=source.get("index_scanned_images"),
                          source_payload_received_images=len(screened),
                          strict_train_supply_rows=None, parent_lineage_exclusions=None,
                          near_evaluation_quarantine=0, remaining_metadata_hint_rows=None,
                          remaining_metadata_hint_unique_sha=None,
                          remaining_metadata_hint_lineages=None)
        crop_ids = {r["candidate_id"] for r in crop}
        exceptions = [r for r in inputs["owner_feedback"]["exceptions"]
                      if r["sample_id"] in crop_ids]
        record.update(owner_rejected_crops=0, owner_accepted_crops=0,
                      owner_feedback_exceptions=len(exceptions),
                      owner_target_positive_rejections=sum(
                          r["assessment"] == "Không chấp nhận P hiện tại" for r in exceptions),
                      owner_status="Không suy batch acceptance từ receipt đã xem toàn bộ",
                      measured_numbers=True, remaining_useful_independent_groups=None,
                      exhaustion_status=source["exhaustion_status"],
                      candidate_cap=source["candidate_cap"])
        records.append(record)
    if config.get("public_csv_audit"):
        public = config["public_csv_audit"]
        for key in ("image_metadata", "bbox_prefix"):
            pin = public[key]
            path = (workspace / pin["path"]).resolve()
            if not path.is_relative_to(workspace) or sha256_file(path) != pin["sha256"]:
                raise DataContractError("Public CSV pin/path sai")
            pins.append(pin)
        measured = public_csv_inventory(workspace / public["image_metadata"]["path"],
                                        workspace / public["bbox_prefix"]["path"])
        next(r for r in records if r["source_id"] == public["source_id"]).update(measured)
    observations = {r["screening_id"]: r for key in config["visual_observation_inputs"]
                    for r in inputs[key]["records"]}
    exam = [{"screening_id": r["sample_id"], "hint_kind": r["hint_kind"],
             "source_image_sha256": r["source_image_sha256"],
             "candidate_ids": [c["candidate_id"] for c in candidates
                               if (c["screening_set"], c["screening_id"])
                               == (r["screening_set"], r["sample_id"])],
             "prior_observation": observations.get(r["sample_id"]),
             "owner_rejected": False}
            for r in screenings if r["source_id"] == config["exam_source_id"]]
    report = {"status": "draft_metadata_coverage_audit", "date": config["date"],
              "records": records, "input_pins": pins,
              "unknown_semantics": "null là chưa đo; không đổi thành 0 hoặc exhausted",
              "owner_feedback_pin": config["inputs"]["owner_feedback"],
              "r8_execution": {"new_downloads": 0, "new_crops": 0,
                               "diversity_gain": None, "status": "plan_only"},
              "test_media_read": False, "training_run": False,
              "canonical_mutation": False}
    output = workspace / config["output"]
    names = ["source-coverage-measured.json", "source-coverage-measured.csv",
             "source-exam-screening.json", "source-unused-metadata.csv"]
    if not output.resolve().is_relative_to(workspace / "artifacts/reports") or any(
            (output / name).exists() for name in names):
        raise DataContractError("Artifact source audit phải mới trong artifacts/reports")
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / names[0], report)
    csv_write(output / names[1], records)
    write_json(output / names[2], {"records": exam, "note": "Receipt cũ, không owner rejection"})
    csv_write(output / names[3], unused)
    return {"sources": len(records), "screened_images": len(screenings),
            "draft_crops": len(candidates), "unused_metadata_rows": len(unused)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.workspace), ensure_ascii=True))


if __name__ == "__main__":
    main()
