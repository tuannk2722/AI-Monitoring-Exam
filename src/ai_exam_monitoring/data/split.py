from __future__ import annotations

import hashlib
import math
from collections import defaultdict

from ai_exam_monitoring.common.errors import DataContractError

from .manifest import ManifestRow


def _stable_score(seed: int, group_id: str) -> float:
    digest = hashlib.sha256(f"{seed}:{group_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64)


def assign_grouped_splits(
    rows: list[ManifestRow], ratios: dict[str, float], seed: int
) -> list[ManifestRow]:
    expected = {"train", "val", "test"}
    if (set(ratios) != expected
            or any(not math.isfinite(value) for value in ratios.values())
            or abs(sum(ratios.values()) - 1.0) > 1e-9):
        raise DataContractError("Split ratios must define train/val/test and sum to 1.0")
    if any(value <= 0 for value in ratios.values()):
        raise DataContractError("Every split ratio must be positive")

    grouped: dict[str, list[ManifestRow]] = defaultdict(list)
    for row in rows:
        if not row.group_id:
            raise DataContractError(f"Missing group_id for {row.sample_id}")
        grouped[row.group_id].append(row)

    boundaries = (ratios["train"], ratios["train"] + ratios["val"])
    result: list[ManifestRow] = []
    for group_id, group_rows in grouped.items():
        score = _stable_score(seed, group_id)
        split = "train" if score < boundaries[0] else "val" if score < boundaries[1] else "test"
        for row in group_rows:
            payload = {field: getattr(row, field) for field in row.__dataclass_fields__}
            payload["split"] = split
            result.append(ManifestRow(**payload))
    return sorted(result, key=lambda row: row.sample_id)
