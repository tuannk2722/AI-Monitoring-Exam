"""Kiểm integrity dùng chung; tách khỏi các launcher review đã lưu lịch sử."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .pilot_schema import PilotRecord, record_to_dict


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


def verify_payload(folder: Path) -> None:
    expected = {}
    for line in (folder / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        if relative in expected or sha256_file(source_file(folder, relative)) != digest:
            raise DataContractError("Pinned package/review payload differs")
        expected[relative] = digest
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob("*")
              if p.is_file() and p.relative_to(folder).as_posix() != "checksums.sha256"}
    if set(expected) != actual:
        raise DataContractError("Pinned package/review file inventory differs")


def safe_path(root: Path, relative: str, *, media: bool = False) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or ".." in Path(relative).parts:
        raise DataContractError("Path thoát workspace")
    if media and (not (path.is_relative_to(root / "data/raw")
                       or path.is_relative_to(root / "data/interim")
                       or path.is_relative_to(root / "outputs"))
                  or any(p.lower() in {"val", "valid", "validation", "test", "holdout",
                                       "val2017", "test2017", "data/processed"}
                         for p in path.relative_to(root).parts)):
        raise DataContractError("Không đọc processed/evaluation media")
    return path


def pin(root: Path, value: dict[str, str], *, media: bool = False) -> Path:
    path = safe_path(root, value["path"], media=media)
    if sha256_file(path) != value["sha256"]:
        raise DataContractError(f"SHA thay đổi: {value['path']}")
    return path


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines()
            if line.strip()]


def test_freeze_attestation(
    records: list[PilotRecord], *, config_sha256: str, approval_sha256: str,
    owner_decision_ref: str, approval: dict[str, Any], commit: str, protocol: str,
) -> dict[str, Any]:
    """Pin serializer-exact hashes without a cycle through release.json/checksums."""
    used = sorted((r for r in records if r.split), key=lambda r: r.sample_id)

    def digest(rows: list[dict[str, Any]]) -> str:
        payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True,
                                     allow_nan=False) + "\n" for row in rows)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return {
        "status": "frozen", "frozen_at": approval["recorded_at"],
        "reviewer": approval["reviewer"], "owner_decision_ref": owner_decision_ref,
        "owner_decision_sha256": approval_sha256, "config_sha256": config_sha256,
        "git_commit": commit, "split_version": used[0].split_version,
        "manifest_sha256": digest([record_to_dict(r) for r in used]),
        "split_assignment_sha256": digest([
            {"sample_id": r.sample_id, "split": r.split,
             "leakage_group_id": r.group.leakage_group_id if r.group else None,
             "split_version": r.split_version, "test_freeze_ref": r.test_freeze_ref}
            for r in used
        ]),
        "test_manifest_sha256": digest([record_to_dict(r) for r in used if r.split == "test"]),
        "test_sample_ids": [r.sample_id for r in used if r.split == "test"],
        "protocol": protocol,
    }
