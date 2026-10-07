"""Finite SCB anchor selection; source classes never become canonical targets."""

from __future__ import annotations

import hashlib
import json
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .yolo import YoloAnnotation


def source_file(root: Path, relative: str) -> Path:
    """Resolve a portable source member without permitting traversal/symlink escape."""
    parts = PurePosixPath(relative)
    if (
        not relative or "\\" in relative or ":" in relative or parts.is_absolute()
        or any(part in {".", ".."} for part in parts.parts)
    ):
        raise DataContractError(f"Unsafe source relative path: {relative!r}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise DataContractError(f"Missing/unsafe source member: {relative}")
    return path


@dataclass(frozen=True, slots=True)
class CandidateAnchor:
    source_id: str
    archive_sha256: str
    source_image_relpath: str
    source_image_sha256: str
    source_label_relpath: str
    source_label_sha256: str
    source_label_line_1based: int
    source_class_id: int
    width: int
    height: int
    stratum: str
    source_anchor_yolo: YoloAnnotation
    rank_sha256: str
    exact_aliases: tuple[str, ...] = ()

    @property
    def identity(self) -> tuple[str, str, str, int]:
        return (
            self.archive_sha256, self.source_image_relpath,
            self.source_label_relpath, self.source_label_line_1based,
        )

    def to_dict(self, sample_id: str) -> dict[str, Any]:
        row = asdict(self)
        annotation = self.source_anchor_yolo
        row["sample_id"] = sample_id
        row["source_anchor_xyxy"] = [
            (annotation.x_center - annotation.width / 2) * self.width,
            (annotation.y_center - annotation.height / 2) * self.height,
            (annotation.x_center + annotation.width / 2) * self.width,
            (annotation.y_center + annotation.height / 2) * self.height,
        ]
        row["selection_reason"] = "stable_hash_round_robin_unique_image_anchor"
        row["annotation_status"] = "source_anchor_not_person_or_target_approval"
        return row


def inventory_anchors(
    report: dict[str, Any], *, source_id: str, source_root: Path, archive_sha256: str,
    strata_by_class: dict[int, str], rank_namespace: str,
    aliases_by_sha: dict[str, tuple[str, ...]] | None = None,
    archive_path: Path | None = None, archive_prefix: str = "",
    image_prefix: str = "images/train/",
) -> list[CandidateAnchor]:
    """Reuse strict audit inventory and verify its anchors/bytes against pinned inputs.

    With archive_path, every selected-pool image/label is compared to ZIP bytes.
    Archive hashing is the caller's separate pin gate. Nothing is extracted or mutated.
    """
    if report.get("schema_version") != 2 or not isinstance(report.get("samples"), list):
        raise DataContractError("Expected schema-v2 source audit inventory")
    if not strata_by_class or not rank_namespace:
        raise DataContractError("Selection strata and rank namespace are required")
    if image_prefix not in {"images/train/", "train/images/"}:
        raise DataContractError("Candidate inventory must use an explicit upstream train layout")
    source_root = Path(source_root).resolve()
    aliases_by_sha = aliases_by_sha or {}
    result = []
    seen_images = set()
    archive = zipfile.ZipFile(archive_path) if archive_path is not None else None
    try:
        for sample in report["samples"]:
            image_relative, label_relative = sample["image"], sample["label"]
            if not image_relative.startswith(image_prefix):
                continue
            expected = [YoloAnnotation(**row) for row in sample["annotations"]]
            if not any(row.class_id in strata_by_class for row in expected):
                continue
            if image_relative in seen_images:
                raise DataContractError("Duplicate image row in strict audit inventory")
            seen_images.add(image_relative)
            image_path = source_file(source_root, image_relative)
            label_path = source_file(source_root, label_relative)
            image_sha, label_sha = sha256_file(image_path), sha256_file(label_path)
            if archive is not None:
                for relative, digest in ((image_relative, image_sha), (label_relative, label_sha)):
                    member = f"{archive_prefix.rstrip('/')}/{relative}".lstrip("/")
                    try:
                        original_sha = hashlib.sha256(archive.read(member)).hexdigest()
                    except KeyError as exc:
                        raise DataContractError(f"Missing ZIP member: {member}") from exc
                    if digest != original_sha:
                        raise DataContractError(
                            f"Extracted source differs from pinned ZIP: {relative}"
                        )
            lines = label_path.read_text(encoding="utf-8").splitlines()
            numbered = [
                (number, YoloAnnotation.parse(line))
                for number, line in enumerate(lines, 1)
                if line.strip()
            ]
            if [annotation for _, annotation in numbered] != expected:
                raise DataContractError(
                    f"Source label differs from audit anchors: {label_relative}"
                )
            width, height = sample["width"], sample["height"]
            if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
                raise DataContractError("Invalid audit image dimensions")
            for line_number, annotation in numbered:
                if annotation.class_id not in strata_by_class:
                    continue
                rank_input = "|".join((
                    rank_namespace, archive_sha256, image_sha, label_relative, str(line_number),
                ))
                result.append(CandidateAnchor(
                    source_id=source_id, archive_sha256=archive_sha256,
                    source_image_relpath=image_relative, source_image_sha256=image_sha,
                    source_label_relpath=label_relative, source_label_sha256=label_sha,
                    source_label_line_1based=line_number, source_class_id=annotation.class_id,
                    width=width, height=height, stratum=strata_by_class[annotation.class_id],
                    source_anchor_yolo=annotation,
                    rank_sha256=hashlib.sha256(rank_input.encode("utf-8")).hexdigest(),
                    exact_aliases=aliases_by_sha.get(image_sha, ()),
                ))
    finally:
        if archive is not None:
            archive.close()
    return sorted(result, key=lambda row: (row.rank_sha256, row.identity))


def select_round_robin(
    candidates: list[CandidateAnchor], *, stratum_order: tuple[str, ...], quota_per_stratum: int,
) -> list[dict[str, Any]]:
    """One anchor per exact-unique image, bounded quota and no implicit refill policy."""
    if (
        type(quota_per_stratum) is not int or quota_per_stratum <= 0
        or not stratum_order or len(set(stratum_order)) != len(stratum_order)
    ):
        raise DataContractError("Positive quota and unique ordered strata are required")
    identities = [row.identity for row in candidates]
    if len(set(identities)) != len(identities):
        raise DataContractError("Duplicate candidate identity")
    if any(row.stratum not in stratum_order for row in candidates):
        raise DataContractError("Candidate stratum is outside the reviewed selection contract")
    pools: dict[str, list[CandidateAnchor]] = {}
    for stratum in stratum_order:
        per_image: dict[str, CandidateAnchor] = {}
        for candidate in sorted(candidates, key=lambda row: (row.rank_sha256, row.identity)):
            if candidate.stratum == stratum:
                per_image.setdefault(candidate.source_image_sha256, candidate)
        pools[stratum] = list(per_image.values())
    selected: list[dict[str, Any]] = []
    used_hashes: set[str] = set()
    counts: Counter[str] = Counter()
    for _ in range(quota_per_stratum):
        for stratum in stratum_order:
            available = next(
                (row for row in pools[stratum] if row.source_image_sha256 not in used_hashes), None,
            )
            if available is None:
                raise DataContractError(
                    f"Selection shortage for {stratum}: selected {counts[stratum]}/"
                    f"{quota_per_stratum}; no quota transfer or new source is allowed"
                )
            used_hashes.add(available.source_image_sha256)
            counts[stratum] += 1
            selected.append(available.to_dict(f"SCB-{stratum}-{counts[stratum]:03d}"))
    return selected


def write_selection(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8", newline="\n",
    )
