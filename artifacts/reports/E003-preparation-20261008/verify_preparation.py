"""Kiểm hồ sơ E003 local; không khởi tạo model hoặc chạy huấn luyện/inference."""
import json
import math
import platform
import subprocess
from collections import Counter
from importlib.metadata import version
from pathlib import Path

from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import digest_json
from ai_exam_monitoring.training.config import load_config, verify_approval
from ai_exam_monitoring.training.data import verify_dataset

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def rows(path):
    return [json.loads(line) for line in (ROOT / path).read_text(encoding="utf-8").splitlines()]


def support(records):
    return {
        "records": len(records),
        "groups": len({r["group"]["leakage_group_id"] for r in records}),
        "sources": dict(Counter(r["source"]["source_id"] for r in records)),
        "targets": {t: dict(Counter(r[t]["state"] for r in records))
                    for t in ("phone_use", "looking_around")},
        "fully_known": sum(all(r["target_mask"]) for r in records),
        "co_positive": sum(r["target_values"] == [1, 1] for r in records),
    }


def main():
    configs = [load_config(ROOT / f"configs/experiments/{name}.yaml")
               for name in ("E003", "E003-smoke")]
    config = configs[0]
    if not __debug__:
        raise RuntimeError("Không chạy audit với Python -O")
    smoke_diff = {k for k, v in configs[1].to_dict().items() if config.to_dict()[k] != v}
    assert smoke_diff == {"experiment_id", "hypothesis", "max_epochs", "run_kind"}
    assert configs[1].max_epochs == 3 and configs[1].run_kind == "smoke"
    pointer = read("artifacts/reports/pilot-b-v6-release-20261007/release-pointer.json")
    for key in ("checksums", "config", "owner_approval", "evaluation_preservation"):
        pin = pointer[key]
        assert sha256_file(ROOT / pin["path"]) == pin["sha256"], key
    assert config.payload_sha256 == pointer["checksums"]["sha256"]
    verified = verify_dataset(ROOT / config.dataset, config)
    assert len(verified) == 378
    current = rows(f"{config.dataset}/manifest.jsonl")
    parent_config = load_config(ROOT / "configs/experiments/E002.yaml")
    verify_dataset(ROOT / parent_config.dataset, parent_config)
    parent = rows(f"{parent_config.dataset}/manifest.jsonl")
    indexed = {r["sample_id"]: r for r in current}
    fields = ("target_values", "target_mask", "usage", "split", "normal_review")
    for old in parent:
        new = indexed[old["sample_id"]]
        assert all(old[k] == new[k] for k in fields)
        assert old["crop"] == new["crop"]
        assert old["source"] == new["source"]
        assert old["group"] == new["group"]
    for field in ("image_sha256", "crop_sha256", "leakage_group_id"):
        section = {"image_sha256": "source", "crop_sha256": "crop",
                   "leakage_group_id": "group"}[field]
        ownership = {}
        for row in current:
            key = row[section][field]
            assert ownership.setdefault(key, row["usage"]) == row["usage"], field
    train = [r for r in current if r["usage"] == "train"]
    val = [r for r in current if r["usage"] == "val"]
    historical_ids = sorted(r["sample_id"] for r in parent if r["usage"] == "val")
    historical = [r for r in val if r["sample_id"] in historical_ids]
    added = [r for r in val if r["sample_id"] not in historical_ids]
    assert (len(train), len(val), len(historical), len(added)) == (317, 50, 13, 37)
    prediction_path = "outputs/E002-val-evaluation/predictions.json"
    old_pins = read("artifacts/reports/E002/validation-artifact-checksums.json")
    assert sha256_file(ROOT / prediction_path) == old_pins["predictions.json"]
    predictions = read(prediction_path)
    assert sorted(p["sample_id"] for p in predictions) == historical_ids
    for prediction in predictions:
        row = indexed[prediction["sample_id"]]
        assert prediction["targets"] == row["target_values"]
        assert prediction["mask"] == row["target_mask"]
        assert prediction["split"] == "val"
    prevalence = {}
    constant_bce = {}
    for target in ("phone_use", "looking_around"):
        counts = Counter(r[target]["state"] for r in train)
        p = counts["positive"] / (counts["positive"] + counts["negative"])
        assert 0 < p < 1
        prevalence[target] = p
        known = [r[target]["state"] == "positive" for r in val
                 if r[target]["state"] != "unknown"]
        constant_bce[target] = sum(-math.log(p if y else 1 - p) for y in known) / len(known)
    diffs = {k: {"E002": parent_config.to_dict()[k], "E003": v}
             for k, v in config.to_dict().items() if v != parent_config.to_dict()[k]}
    assert set(diffs) == {"experiment_id", "hypothesis", "approval_ref", "dataset",
                          "dataset_version", "split_version", "payload_sha256"}
    assert sha256_file(ROOT / config.weights) == config.weights_sha256
    denied = []
    approval = read(config.approval_ref)
    assert approval["status"] == "pending" and approval["configs"] == {}
    assert approval["training_authorized"] is False
    assert approval["final_test_authorized"] is False
    assert sha256_file(ROOT / approval["protocol"]["path"]) == approval["protocol"]["sha256"]
    for candidate in configs:
        assert approval["proposed_configs"][candidate.experiment_id] == digest_json(
            candidate.to_dict())
        try:
            verify_approval(candidate, ROOT)
        except ConfigurationError:
            denied.append(candidate.experiment_id)
        else:
            raise AssertionError("Proposal chưa được phép chạy")
    lock = (ROOT / "requirements/classifier-cpu-lock.txt").read_text().splitlines()
    packages = {line.split("==")[0]: version(line.split("==")[0])
                for line in lock if "==" in line and not line.startswith("#")}
    assert all(packages[line.split("==")[0]] == line.split("==")[1]
               for line in lock if "==" in line and not line.startswith("#"))
    report = {
        "status": "PASS", "prepared_on": "2026-10-08", "training_executed": False,
        "inference_executed": False, "test_access": "Chỉ checksum/metadata/preservation",
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                text=True).strip(),
        "git_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT,
                                                text=True).splitlines(),
        "resolved_config_digests": {c.experiment_id: digest_json(c.to_dict()) for c in configs},
        "pending_approval_rejected": denied,
        "payload_sha256": config.payload_sha256, "weights_sha256": config.weights_sha256,
        "preserved_parent_records": len(parent), "historical_val_ids": historical_ids,
        "historical_predictions": {"path": prediction_path,
                                   "sha256": old_pins["predictions.json"]},
        "support": {"train": support(train), "val": support(val),
                    "historical_val": support(historical), "added_val": support(added)},
        "train_prevalence": prevalence,
        "constant_val_bce": {**constant_bce, "macro": sum(constant_bce.values()) / 2},
        "constant_note": "Đối chứng thống kê từ nhãn; không phải metric model đã train.",
        "recipe_diff": diffs, "python": platform.python_version(), "packages": packages,
        "output_paths_absent": {name: not (ROOT / "outputs" / name).exists()
                                for name in ("E003", "E003-smoke", "E003-val-evaluation")},
    }
    (OUT / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)
                                           + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
