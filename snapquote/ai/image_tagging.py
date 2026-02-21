from __future__ import annotations

from pathlib import Path

KEYWORDS = ["oven", "carpet", "window", "heavy_dirt"]


def analyze_image(image_path: str) -> list[str]:
    if not image_path:
        return []
    path = Path(image_path)
    if not path.exists():
        return []
    lowered = path.name.lower()
    return [kw for kw in KEYWORDS if kw in lowered]
