"""Dựng crop/pair Draft đã tuyển; không tạo canonical manifest hoặc split."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file, write_json

from .pilot_inputs import verify_pin
from .pilot_schema import PixelBox
from .pilot_targeted_expansion import validate_budget


@dataclass(frozen=True)
class ReviewProposal:
    """Đề xuất chưa được owner duyệt, tách khỏi TargetReview canonical."""

    candidate_id: str
    screening_set: str
    screening_id: str
    bucket: str
    role: str
    states: tuple[str, str]
    xyxy: tuple[int, int, int, int]
    visual_family_hint: str
    observation: str
    phenotypes: tuple[str, ...]
    pair_id: str | None = None
    known_evaluation_family: bool = False
    aliases: tuple[str, ...] = ()
    person_unit_hint: str = "unresolved"
    domain: str = "pending_visual_review"

    def __post_init__(self) -> None:
        if re.fullmatch(r"V7-[A-D]-[0-9]{3}", self.candidate_id) is None:
            raise DataContractError("Candidate ID không an toàn")
        if self.bucket not in {"A", "B", "C", "D"} or self.role not in {"positive", "negative",
                                                                           "context"}:
            raise DataContractError("Bucket/role Draft không hợp lệ")
        if not self.candidate_id.startswith(f"V7-{self.bucket}-"):
            raise DataContractError("Candidate ID phải đúng primary bucket")
        if len(self.states) != 2 or any(s not in {"P", "N", "U"} for s in self.states):
            raise DataContractError("States phải đúng thứ tự phone/looking và P/N/U")
        if tuple(self.states) == ("U", "U"):
            raise DataContractError("Không tuyển crop toàn unknown vào targeted shortlist")
        PixelBox(*self.xyxy)
        if self.known_evaluation_family:
            raise DataContractError("Họ hàng evaluation phải nằm trong quarantine, không shortlist")
        if not all((self.candidate_id, self.visual_family_hint, self.observation, self.phenotypes)):
            raise DataContractError("Thiếu ID/family/observation/phenotypes")
        if self.bucket != "D":
            index = int(self.bucket == "C")
            expected = {"positive": "P", "negative": "N"}.get(self.role)
            if expected is None or self.states[index] != expected or not self.pair_id:
                raise DataContractError("A/B/C phải có pair và polarity đúng target")

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> ReviewProposal:
        return cls(**{**row, "states": tuple(row["states"]), "xyxy": tuple(row["xyxy"]),
                      "phenotypes": tuple(row["phenotypes"]),
                      "aliases": tuple(row.get("aliases", []))})


def check_pairs(proposals: list[ReviewProposal], pairs: list[dict[str, Any]]) -> None:
    by_id = {r.candidate_id: r for r in proposals}
    if len(by_id) != len(proposals):
        raise DataContractError("Candidate IDs trùng")
    pair_ids: set[str] = set()
    for pair in pairs:
        pid = pair["pair_id"]
        if pair["bucket"] not in {"A", "B", "C"} or any(
            pair[key] not in by_id for key in ("positive_id", "negative_id")
        ):
            raise DataContractError("Pair cần bucket A/B/C và hai candidate hiện hữu")
        if pid in pair_ids or pair["match_strength"] not in {"same_image", "same_scene",
                                                            "source_context"}:
            raise DataContractError("Pair trùng hoặc match strength không công bố")
        pair_ids.add(pid)
        p, n = by_id[pair["positive_id"]], by_id[pair["negative_id"]]
        index = int(pair["bucket"] == "C")
        if (p.states[index] != "P" or n.states[index] != "N" or p.candidate_id == n.candidate_id
                or not pair["matching_basis"]):
            raise DataContractError("Pair phải hai crop distinct/đúng target và evidence match")
        if p.bucket != pair["bucket"]:
            raise DataContractError("Positive pair phải thuộc primary bucket")
        if n.bucket != pair["bucket"] and pair.get("shared_negative_primary_bucket") != n.bucket:
            raise DataContractError("Negative dùng lại cần primary bucket; không đếm hai lần")
        if pair["match_strength"] == "same_image" and (
            p.screening_set, p.screening_id
        ) != (n.screening_set, n.screening_id):
            raise DataContractError("Không được gọi different-image là same_image")
        if pair["match_strength"] in {"same_image", "same_scene"} and (
            p.visual_family_hint != n.visual_family_hint
        ):
            raise DataContractError("Pair cùng cảnh phải cùng family hint")
    for row in proposals:
        if row.pair_id and not any(p["pair_id"] == row.pair_id and row.candidate_id in
            {p["positive_id"], p["negative_id"]} for p in pairs):
            raise DataContractError("Proposal tham chiếu pair không có evidence cho đúng crop")


def _source(row: dict[str, Any], workspace: Path) -> Path:
    if row.get("source_original_split") not in {None, "train", "train2017"}:
        raise DataContractError("Chỉ dùng original train source, không evaluation")
    if row.get("source_original_split") == "train2017":
        relative = row["source_image_path"]
    else:
        original_text = row["source_image_relpath"]
        original = PurePosixPath(original_text)
        if ("train" not in original.parts or original.is_absolute()
                or any(part in {"..", "test", "valid", "val", "test2017", "val2017"}
                       for part in original.parts)
                or "\\" in original_text or ":" in original_text):
            raise DataContractError("Chỉ dùng original train source, không evaluation")
        relative = row["source_local_image_path"]
    local = PurePosixPath(relative)
    if (local.is_absolute() or "\\" in relative or ":" in relative or any(
        part in {"..", "test", "valid", "val", "test2017", "val2017"} for part in local.parts
    )):
        raise DataContractError("Source local path phải relative và ngoài evaluation")
    path = (workspace / str(relative)).resolve()
    roots = (workspace / "data/raw", workspace / "data/interim")
    if not any(path.is_relative_to(root) for root in roots):
        raise DataContractError("Không mở processed/evaluation media làm source")
    if {"test", "valid", "val", "test2017", "val2017"}.intersection(
        path.relative_to(workspace).parts
    ):
        raise DataContractError("Source resolved path thuộc evaluation")
    verify_pin(path, row["source_image_sha256"])
    return path


def build(config_path: Path, workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    config = load_yaml(config_path)
    if (config["status"] != "draft_targeted_review_package"
            or config["training_eligible"] is not False):
        raise DataContractError("Chỉ dựng package Draft không training")
    for name in ("scope_approval", "selection", "parent_checksums"):
        pin = config[name]
        verify_pin(workspace / pin["path"], pin["sha256"])
    scope = json.loads((workspace / config["scope_approval"]["path"]).read_text(encoding="utf8"))
    if scope["decision"] != "approve_v7_targeted_preparation_only":
        raise DataContractError("Thiếu scope owner cho targeted preparation")
    output = (workspace / config["output"]).resolve()
    if not output.is_relative_to(workspace / "data/interim") or output.exists():
        raise DataContractError("Output phải là version interim mới")
    selection = json.loads((workspace / config["selection"]["path"]).read_text(encoding="utf8"))
    proposals = [ReviewProposal.from_dict(r) for r in selection["proposals"]]
    check_pairs(proposals, selection["pairs"])
    counts = Counter(r.bucket for r in proposals)
    for bucket, budget in config["budgets"].items():
        if bucket not in {"A", "B", "C", "D"}:
            raise DataContractError("Review budget cần bucket A/B/C/D")
        validate_budget(budget, f"review budget {bucket}")
        if counts[bucket] > budget:
            raise DataContractError("Vượt review budget, không âm thầm thay quota")
    if not set(counts) <= set(config["budgets"]):
        raise DataContractError("Thiếu review budget cho primary bucket")
    if config.get("require_person_units") and any(
        not r.person_unit_hint.strip() or r.person_unit_hint == "unresolved" for r in proposals
    ):
        raise DataContractError("Gói final Draft cần unit hint để chống đếm cùng người hai lần")
    sets: dict[str, dict[str, dict[str, Any]]] = {}
    for pin in config["screenings"]:
        if pin["id"] in sets:
            raise DataContractError("Screening set IDs trùng giữa versions")
        path = workspace / pin["path"]
        verify_pin(path, pin["sha256"])
        rows = [json.loads(line) for line in path.read_text(encoding="utf8").splitlines()]
        sets[pin["id"]] = {r["sample_id"]: r for r in rows}
        if len(sets[pin["id"]]) != len(rows):
            raise DataContractError("Screening IDs trùng trong cùng version")
    # Preflight mọi path trước mutation; không mở test images.
    for proposal in proposals:
        row = sets[proposal.screening_set][proposal.screening_id]
        _source(row, workspace)
        if proposal.xyxy[2] > row["width"] or proposal.xyxy[3] > row["height"]:
            raise DataContractError("Crop vượt kích thước source")
    output.mkdir(parents=True)
    for folder in ("crops", "review"):
        (output / folder).mkdir()
    rows, crop_hashes, unit_keys = [], set(), set()
    families: dict[str, set[str]] = defaultdict(set)
    font = ImageFont.load_default(size=16)
    for proposal in proposals:
        source = sets[proposal.screening_set][proposal.screening_id]
        with Image.open(_source(source, workspace)) as decoded:
            image = decoded.convert("RGB")
        if image.size != (source["width"], source["height"]):
            raise DataContractError("Kích thước source khác metadata đã pin")
        box = PixelBox(*proposal.xyxy)
        crop = image.crop(box.xyxy)
        crop_path = output / "crops" / f"{proposal.candidate_id}.png"
        crop.save(crop_path)
        crop_sha = sha256_file(crop_path)
        if crop_sha in crop_hashes:
            raise DataContractError("Crop pixels trùng; không dùng duplicate để bù quota")
        crop_hashes.add(crop_sha)
        pixel_sha = hashlib.sha256(image.tobytes()).hexdigest()
        unit_key = (pixel_sha, proposal.person_unit_hint)
        if config.get("require_person_units") and unit_key in unit_keys:
            raise DataContractError("Cùng ảnh/person unit bị đếm nhiều lần; cần alias primary")
        unit_keys.add(unit_key)
        families[pixel_sha].add(proposal.visual_family_hint)
        if len(families[pixel_sha]) > 1:
            raise DataContractError("Ảnh pixel trùng không được tách family hint")
        row = {**source, **asdict(proposal), "screening_sample_id": source["sample_id"],
               "sample_id": proposal.candidate_id, "status": "draft_pending_owner_review",
               "proposed_states": list(proposal.states), "canonical_targets": [None, None],
               "canonical_mask": [0, 0], "leakage_group_id": None, "split": None,
               "training_eligible": False, "usage": "review_only",
               "crop_path": crop_path.relative_to(workspace).as_posix(), "crop_sha256": crop_sha,
               "source_pixel_sha256": pixel_sha, "draft_xyxy": list(box.xyxy),
               "source_rights_status": source.get("source_rights_status",
                    "public_pending_attribution_and_owner_review"
                    if source.get("source_original_split") == "train2017"
                    else "existing_source_scope_only"),
               "qa": {"crop_geometry": "PASS", "source_hash": "PASS", "owner_review": "PENDING",
                      "person_unit": "draft_visual_proposal", "group_independence": "UNPROVEN",
                      "original_crop_size": list(crop.size)}}
        rows.append(row)
        drawn = image.copy()
        ImageDraw.Draw(drawn).rectangle(box.xyxy, outline="red", width=3)
        panel = Image.new("RGB", (900, 590), "white")
        ImageDraw.Draw(panel).text((5, 5), f"{proposal.candidate_id} {proposal.bucket} "
                                  f"{proposal.role} {'/'.join(proposal.states)} DRAFT", font=font,
                                  fill="black")
        ImageDraw.Draw(panel).text((5, 28), f"{proposal.screening_set}:{proposal.screening_id} "
                                  f"{proposal.visual_family_hint}", font=font, fill="black")
        panel.paste(ImageOps.contain(drawn, (550, 520)), (0, 65))
        panel.paste(ImageOps.contain(crop, (340, 520)), (558, 65))
        panel.save(output / "review" / f"{proposal.candidate_id}.jpg")
    for start in range(0, len(rows), 6):
        sheet = Image.new("RGB", (2700, 1180), "white")
        for index, row in enumerate(rows[start:start + 6]):
            with Image.open(output / "review" / f"{row['sample_id']}.jpg") as panel:
                sheet.paste(panel, ((index % 3) * 900, (index // 3) * 590))
        sheet.save(output / "review" / f"sheet-{start // 6 + 1:03d}.jpg")
    (output / "candidates.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False,
        sort_keys=True) + "\n" for r in rows), encoding="utf8")
    write_json(output / "pairs.json", selection["pairs"])
    coverage = {}
    for bucket, budget in config["budgets"].items():
        selected = [r for r in rows if r["bucket"] == bucket]
        coverage[bucket] = {"budget": budget, "proposed_crops": len(selected),
                            "by_role": dict(Counter(r["role"] for r in selected)),
                            "shortage": max(0, budget - len(selected)),
                            "auxiliary_public_crops": sum(r["domain"] == "auxiliary_out_of_exam"
                                                          for r in selected),
                            "family_hints_not_independent_groups": len({r["visual_family_hint"]
                                                                        for r in selected}),
                            "accepted_crops": 0, "training_eligible_crops": 0}
    cards = []
    for row in rows:
        sid = row["sample_id"]
        matches = []
        for pair in selection["pairs"]:
            if sid in {pair["positive_id"], pair["negative_id"]}:
                other = pair["negative_id"] if sid == pair["positive_id"] else pair["positive_id"]
                matches.append(f'<li><a href="#{other}">{other}</a> — '
                               f'{html.escape(pair["match_strength"])}: '
                               f'{html.escape(pair["matching_basis"])}</li>')
        source_link = row.get("flickr_url") or row.get("source_url")
        source_html = f'<a href="{html.escape(source_link, quote=True)}">Nguồn public</a>' \
            if source_link else html.escape(row["source_image_relpath"])
        cards.append(f'<article id="{sid}"><h2>{sid} — {row["bucket"]} '
                     f'{html.escape("/".join(row["proposed_states"]))} (Draft)</h2>'
                     f'<img loading="lazy" src="{sid}.jpg">'
                     f'<p>{html.escape(row["observation"])}</p>'
                     f'<p>Unit: {html.escape(row["person_unit_hint"])}; '
                     f'domain: {html.escape(row["domain"])}; '
                     f'family chưa chốt: {html.escape(row["visual_family_hint"])}</p>'
                     f'<p>Phenotype: {html.escape(", ".join(row["phenotypes"]))}; '
                     f'quyền: {html.escape(row["source_rights_status"])}</p>'
                     f'<p>{source_html}</p><ul>{"".join(matches)}</ul></article>')
    (output / "review/index.html").write_text('<!doctype html><meta charset="utf-8">'
        '<title>v7 targeted review Draft</title><style>body{font-family:system-ui;max-width:1000px;'
        'margin:auto}img{width:100%}article{border-bottom:1px solid #bbb}</style>'
        '<h1>Crop/nhãn/pair Draft — chưa release hoặc training</h1>' + "".join(cards),
        encoding="utf8")
    summary = {"status": "draft_pending_owner_review", "records": len(rows), "coverage": coverage,
               "pairs": len(selection["pairs"]), "pair_strengths": dict(Counter(
                   p["match_strength"] for p in selection["pairs"])), "test_media_read": False,
               "owner_review_required": ["crop/person", "states/phenotypes", "pairs", "groups",
                                         "public_rights_and_domain"], "training_eligible": False,
               "config_sha256": sha256_file(config_path),
               "candidate_sha256": sha256_file(output / "candidates.jsonl")}
    write_json(output / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.workspace), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
