"""Đóng gói phương án membership để owner review; không tạo release accepted."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .pilot_inputs import verify_pin
from .pilot_owner_groups import verify_payload
from .pilot_schema import read_records, record_to_dict
from .pilot_source_candidates import _new_output


def propose_groups(rows: list[dict[str, Any]], relations: list[dict[str, Any]]) -> None:
    """Nối các quan hệ đã khai báo; không tìm nhóm bằng tên class/ảnh/metric."""
    by_id = {r["sample_id"]: r for r in rows}
    if len(by_id) != len(rows):
        raise DataContractError("ID trùng trong proposal")
    parents = {i: i for i in by_id}

    def find(i: str) -> str:
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    def join(ids: list[str]) -> None:
        if not ids or not set(ids).issubset(by_id):
            raise DataContractError("Quan hệ nhóm có ID thiếu hoặc lạ")
        for i in ids[1:]:
            parents[find(i)] = find(ids[0])

    old_groups: dict[str, list[str]] = defaultdict(list)
    exact: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        if r["parent_group"]:
            old_groups[r["parent_group"]].append(r["sample_id"])
        exact[r["source_image_sha256"]].append(r["sample_id"])
    for ids in list(old_groups.values()) + list(exact.values()):
        join(ids)
    for edge in relations:
        if not edge.get("observation_vi"):
            raise DataContractError("Quan hệ thiếu bằng chứng thị giác")
        join(edge["sample_ids"])
    components: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        components[find(r["sample_id"])].append(r)
    for members in components.values():
        inherited = {r["parent_group"] for r in members if r["parent_group"]}
        splits = {
            r["proposed_usage"] for r in members if r["proposed_usage"] in {"train", "val", "test"}
        }
        if len(inherited) > 1:
            raise DataContractError("Proposal nối nhiều group v5; cần quyết định riêng")
        if len(splits) > 1:
            raise DataContractError("Thành phần cảnh đi qua nhiều split")
        digest = hashlib.sha256("|".join(sorted(r["sample_id"] for r in members)).encode())
        gid = next(iter(inherited)) if inherited else "V6-G-" + digest.hexdigest()[:20]
        for r in members:
            r["proposed_group_id"] = gid


def assemble_rows(
    parent: list[dict[str, Any]], candidates: list[dict[str, Any]], decisions: dict[str, Any]
) -> list[dict[str, Any]]:
    choices = {r["sample_id"]: r for r in decisions["choices"]}
    if len(choices) != len(decisions["choices"]):
        raise DataContractError("Decision trùng ID")
    all_ids = {r["sample_id"] for r in parent + candidates}
    if not set(choices).issubset(all_ids):
        raise DataContractError("Decision ngoài selection")
    overrides = {r["sample_id"]: r for r in decisions["target_overrides"]}
    if len(overrides) != len(decisions["target_overrides"]) or not set(overrides).issubset(
        {r["sample_id"] for r in candidates}
        | {r["sample_id"] for r in parent if r["usage"] == "review_only"}
    ):
        raise DataContractError("Chỉ đề xuất nhãn candidate hoặc parent review_only")
    rows = []
    for p in parent:
        i = p["sample_id"]
        choice = choices.get(i)
        if choice and p["usage"] != "review_only":
            raise DataContractError("Không đổi membership parent đã freeze")
        crop = p["crop"]
        rows.append(
            {
                "sample_id": i,
                "origin": "v5",
                "parent_usage": p["usage"],
                "parent_group": (p["group"] or {}).get("leakage_group_id"),
                "proposed_usage": choice["proposed_usage"] if choice else p["usage"],
                "source_id": p["source"]["source_id"],
                "source_image_sha256": p["source"]["image_sha256"],
                "crop_path": decisions["parent_package"] + "/" + crop["crop_relpath"]
                if crop and p["usage"] != "excluded"
                else None,
                "crop_sha256": crop["crop_sha256"] if crop else None,
                "context_box": crop["context_box"] if crop else None,
                "phone_use": p["phone_use"]["state"],
                "looking_around": p["looking_around"]["state"],
                "work_context_review": p["work_context_review"]["state"],
                "observation": choice["reason"] if choice else "Bảo toàn trạng thái và nhãn v5.",
                "source_provenance": p["source"],
            }
        )
    for p in candidates:
        i = p["sample_id"]
        if i not in choices:
            raise DataContractError("Mỗi candidate phải có quyết định đề xuất")
        v, c = p["visual_proposal"], choices[i]
        r = {
            "sample_id": i,
            "origin": "new_candidate",
            "parent_usage": None,
            "parent_group": None,
            "proposed_usage": c["proposed_usage"],
            "source_id": p["source_id"],
            "source_image_sha256": p["source_image_sha256"],
            "crop_path": p["crop_path"],
            "crop_sha256": p["crop_sha256"],
            "context_box": dict(
                zip(("xmin", "ymin", "xmax", "ymax"), p["draft_xyxy"], strict=True)
            ),
            "phone_use": v["proposed_phone_use"],
            "looking_around": v["proposed_looking_around"],
            "work_context_review": v["proposed_work_context"],
            "observation": c["reason"],
            "source_provenance": {
                k: p[k]
                for k in (
                    "source_id",
                    "archive_sha256",
                    "source_image_relpath",
                    "source_image_sha256",
                    "source_label_relpath",
                    "source_label_sha256",
                    "source_label_line_1based",
                    "source_class_id",
                    "width",
                    "height",
                    "source_root",
                    "lineage_hint",
                )
            },
        }
        if i in overrides:
            o = overrides[i]
            for key in ("phone_use", "looking_around", "work_context_review"):
                if key in o:
                    r[key] = o[key]
            r["observation"] += " " + o["reason"]
        rows.append(r)
    for r in rows:
        if r["origin"] == "v5" and r["sample_id"] in overrides:
            o = overrides[r["sample_id"]]
            if o.get("crop_sha256") != r["crop_sha256"] or not o.get("reason"):
                raise DataContractError("Review parent phải pin crop và có lý do")
            for key in ("phone_use", "looking_around", "work_context_review"):
                if key in o:
                    if r[key] != "unknown" and o[key] != r[key]:
                        raise DataContractError("Không thay nhãn parent đã biết trong revision này")
                    r[key] = o[key]
            r["observation"] += " " + o["reason"]
        use = r["proposed_usage"]
        if use not in {"train", "val", "test", "review_only", "excluded"}:
            raise DataContractError("Usage proposal không hợp lệ")
        if use == "test" and r["parent_usage"] != "test":
            raise DataContractError("Không thêm test mới")
        states = [r["phone_use"], r["looking_around"]]
        if any(s not in {"positive", "negative", "unknown"} for s in states):
            raise DataContractError("Target state không hợp lệ")
        r["proposed_target_values"] = [
            {"positive": 1, "negative": 0, "unknown": None}[s] for s in states
        ]
        r["proposed_target_mask"] = [int(s != "unknown") for s in states]
        if use in {"train", "val", "test"} and (
            not r["crop_path"] or not any(r["proposed_target_mask"])
        ):
            raise DataContractError("Membership thiếu crop hoặc cả hai target unknown")
        if r["work_context_review"] not in {"confirmed_working", "confirmed_other", "unknown"}:
            raise DataContractError("Work context không hợp lệ")
        r["status"] = "draft_pending_owner_review"
        r["training_eligible"] = False
    propose_groups(rows, decisions["relations"])
    return sorted(rows, key=lambda r: r["sample_id"])


def build_review(decisions_path: Path, output: Path, workspace: Path) -> dict[str, Any]:
    workspace, output = workspace.resolve(), output.resolve()
    _new_output(output, workspace / "data/interim")
    decisions = json.loads(decisions_path.read_text(encoding="utf8"))
    if decisions["status"] != "draft_pending_owner_review":
        raise DataContractError("Chỉ tạo gói đề xuất")
    verify_pin(
        decisions_path.parent / "split-scope-approval.json",
        decisions["split_scope_approval_sha256"],
    )
    parent = workspace / decisions["parent_package"]
    verify_pin(parent / "checksums.sha256", decisions["parent_checksums_sha256"])
    verify_payload(parent)
    candidates_path = workspace / decisions["candidate_path"]
    verify_pin(candidates_path, decisions["candidate_sha256"])
    candidates = [
        json.loads(line) for line in candidates_path.read_text(encoding="utf8").splitlines()
    ]
    parents = [record_to_dict(r) for r in read_records(parent / "review-ledger.jsonl")]
    rows = assemble_rows(parents, candidates, decisions)
    for c in candidates:
        source = workspace / c["source_root"] / c["source_image_relpath"]
        verify_pin(source, c["source_image_sha256"])
        verify_pin(
            workspace / c["source_root"] / c["source_label_relpath"], c["source_label_sha256"]
        )
        verify_pin(workspace / c["crop_path"], c["crop_sha256"])
        with Image.open(source) as im, Image.open(workspace / c["crop_path"]) as crop_image:
            expected = im.convert("RGB").crop(c["draft_xyxy"])
            if (
                expected.size != crop_image.size
                or expected.tobytes() != crop_image.convert("RGB").tobytes()
            ):
                raise DataContractError("Crop khác pixels nguồn/toạ độ")
    output.mkdir(parents=True)
    (output / "crops").mkdir()
    for r in rows:
        if r["crop_path"]:
            source = workspace / r["crop_path"]
            verify_pin(source, r["crop_sha256"])
            target = output / "crops" / (r["sample_id"] + ".png")
            shutil.copyfile(source, target)
            r["review_crop_relpath"] = target.relative_to(output).as_posix()
    (output / "proposed-assignment.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
        encoding="utf8",
    )
    sections = []
    for r in rows:
        if r["parent_usage"] in {"train", "val", "test"}:
            continue
        crop = (
            '<img loading="lazy" src="' + r["review_crop_relpath"] + '">' if r["crop_path"] else ""
        )
        if r["origin"] == "new_candidate":
            p = r["source_provenance"]
            source = workspace / p["source_root"] / p["source_image_relpath"]
        else:
            source = (
                workspace / decisions["parent_source_cache"] / (r["source_image_sha256"] + ".jpg")
            )
        verify_pin(source, r["source_image_sha256"])
        url = quote(Path(os.path.relpath(source, output)).as_posix())
        text = html.escape(
            f"{r['sample_id']} | {r['proposed_usage']} | "
            f"phone={r['phone_use']} | looking={r['looking_around']} | "
            f"{r['proposed_group_id']}"
        )
        sections.append(
            f'<section><h2>{text}</h2><div><a href="{url}">'
            f'<img loading="lazy" src="{url}"></a>{crop}</div><p>'
            + html.escape(r["observation"])
            + "</p></section>"
        )
    (output / "review.html").write_text(
        '<!doctype html><html lang="vi"><meta charset="utf-8"><title>Nghiệm thu v6</title>'
        "<style>body{font:16px system-ui;margin:24px;background:#f1f5f9}section{background:white;"
        "padding:16px;margin:16px 0}h2{font-size:16px}"
        "img{max-width:45%;height:300px;object-fit:contain}"
        "</style><h1>Phương án v6 — chờ owner nghiệm thu</h1><p>Ảnh nguồn bên trái, crop bên phải. "
        "P/N/U là đề xuất quan sát; không phải prediction. Các mẫu train/val/test v5 được bảo toàn "
        "và không lặp lại ở trang này. Không có train hoặc test inference.</p>"
        + "".join(sections)
        + "</html>",
        encoding="utf8",
    )
    used = [r for r in rows if r["proposed_usage"] in {"train", "val", "test"}]
    coverage: dict[str, Any] = {}
    for split in ("train", "val", "test"):
        ss = [r for r in used if r["proposed_usage"] == split]
        coverage[split] = {
            "records": len(ss),
            "groups": len({r["proposed_group_id"] for r in ss}),
            "targets": {
                t: dict(Counter(r[t] for r in ss)) for t in ("phone_use", "looking_around")
            },
            "sources": dict(Counter(r["source_id"] for r in ss)),
            "cooccurrence": sum(r["phone_use"] == r["looking_around"] == "positive" for r in ss),
        }
    summary = {
        "status": "draft_pending_owner_review",
        "training_eligible": False,
        "ledger_records": len(rows),
        "candidate_records": len(candidates),
        "proposed_counts": dict(Counter(r["proposed_usage"] for r in rows)),
        "parent_promotions": sum(r["parent_usage"] == "review_only" and r in used for r in rows),
        "new_used": sum(r["origin"] == "new_candidate" for r in used),
        "coverage": coverage,
        "decisions_sha256": sha256_file(decisions_path),
        "assignment_sha256": sha256_file(output / "proposed-assignment.jsonl"),
        "parent_checksums_sha256": sha256_file(parent / "checksums.sha256"),
        "test_sample_ids": [r["sample_id"] for r in used if r["proposed_usage"] == "test"],
        "source_and_crop_hashes": "pass",
        "new_crop_pixels": "pass",
        "group_split_check": "pass",
        "limits": "Ranh giới nhóm thị giác thận trọng; không chứng minh độc lập subject/session. "
        "Validation mở rộng không so trực tiếp E002. Chưa đo cải thiện model.",
    }
    write_json(output / "summary.json", summary)
    files = sorted(p for p in output.rglob("*") if p.is_file())
    (output / "checksums.sha256").write_text(
        "".join(sha256_file(p) + "  " + p.relative_to(output).as_posix() + "\n" for p in files),
        encoding="utf8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_review(args.decisions, args.output, Path.cwd()), ensure_ascii=False))


if __name__ == "__main__":
    main()
