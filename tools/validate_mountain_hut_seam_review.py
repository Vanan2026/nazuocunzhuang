from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / ".codex" / "reports" / "mountain_hut_village_seam_preview_2026-05-24.png"
REPORT = ROOT / ".codex" / "reports" / "mountain_hut_village_seam_review_2026-05-24.md"
BUILDER = ROOT / "tools" / "build_mountain_hut_seam_review.py"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    require(PREVIEW.is_file(), "missing MountainHut/Village seam preview")
    require(REPORT.is_file(), "missing MountainHut/Village seam review report")
    require(BUILDER.is_file(), "missing seam review builder")
    image = Image.open(PREVIEW).convert("RGB")
    require(image.size == (1104, 640), f"seam preview size mismatch: {image.size}")
    stat = ImageStat.Stat(image)
    require(sum(stat.var) > 500, "seam preview appears too flat")
    text = REPORT.read_text(encoding="utf-8")
    for token in [
        "MountainHut / Village Seam Review",
        "Average channel delta",
        "offline source-crop preview",
        "not a Godot runtime screenshot",
        "Runtime replacement remains blocked",
    ]:
        require(token in text, f"seam review report missing token: {token}")
    print("OK: MountainHut/Village seam review validates")


if __name__ == "__main__":
    main()
