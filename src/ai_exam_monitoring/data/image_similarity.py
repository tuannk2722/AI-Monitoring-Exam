"""Image fingerprint distances for review triage, never automatic session IDs."""

from typing import Any

from PIL import Image


def difference_hash(image: Image.Image) -> int:
    """64 horizontal comparisons on a 9x8 grayscale resize, raw pixel orientation."""
    pixels = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS).tobytes()
    result = 0
    for y in range(8):
        for x in range(8):
            result = (result << 1) | int(pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return result


def nearest_by_split(query: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """One nearest other image per source split; ties use full path, not basename."""
    best: dict[str, Any] = {}
    for candidate in candidates:
        if candidate["path"] == query["path"]:
            continue
        distance = (query["dhash"] ^ candidate["dhash"]).bit_count()
        key = (distance, candidate["path"])
        split = candidate["split"]
        if split not in best or key < (best[split]["distance"], best[split]["path"]):
            best[split] = {"path": candidate["path"], "distance": distance}
    return best
