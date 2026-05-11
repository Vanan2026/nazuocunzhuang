from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "sprites" / "characters" / "protagonist" / "source"
FRAME_DIR = ROOT / "sprites" / "characters" / "protagonist" / "frames"
SPRITE_FRAMES = ROOT / "sprites" / "characters" / "protagonist" / "player_mvp_4dir_frames.tres"

FRAME_SIZE = (192, 288)
FOOT_BASELINE_Y = 270

SOURCES = {
    "protagonist_generated_walk_4dir_sheet.png": 32,
    "protagonist_generated_idle_4dir_sheet.png": 16,
    "protagonist_generated_interact_4dir_sheet.png": 24,
    "protagonist_generated_sit_side_sheet.png": 18,
}

ANIMATIONS = {
    "player_walk_down": (8, 8.4),
    "player_walk_up": (8, 8.4),
    "player_walk_left": (8, 9.0),
    "player_walk_right": (8, 9.0),
    "player_idle_down": (4, 5.0),
    "player_idle_up": (4, 5.0),
    "player_idle_left": (4, 5.0),
    "player_idle_right": (4, 5.0),
    "player_interact_down": (6, 10.0),
    "player_interact_up": (6, 10.0),
    "player_interact_left": (6, 10.0),
    "player_interact_right": (6, 10.0),
    "player_sit_down_side": (6, 8.0),
    "player_sit_idle_side": (6, 5.0),
    "player_stand_up_side": (6, 8.0),
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def foreground_mask(rgb: np.ndarray) -> np.ndarray:
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    green_score = g - np.maximum(r, b)
    mask = (
        (green_score < 40)
        | (r > 120)
        | (b > 120)
        | ((r + g + b) > 700)
    )
    return mask.astype(np.uint8) * 255


def count_components(path: Path) -> int:
    rgb = np.array(Image.open(path).convert("RGB"))
    mask = foreground_mask(rgb)
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(mask, 8)
    total = 0
    for idx in range(1, count):
        area = stats[idx][cv2.CC_STAT_AREA]
        if area >= 700:
            total += 1
    return total


def alpha_bounds(path: Path) -> tuple[int, int, int, int]:
    rgba = np.array(Image.open(path).convert("RGBA"))
    require((rgba.shape[1], rgba.shape[0]) == FRAME_SIZE, f"{path.name} must be {FRAME_SIZE}")
    alpha = rgba[:, :, 3]
    foreground = alpha > 10
    require(int(foreground.sum()) >= 4500, f"{path.name} has too little visible character alpha")
    require(int(((alpha > 0) & (alpha < 255)).sum()) >= 80, f"{path.name} lost soft alpha edge detail")
    ys, xs = np.where(foreground)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def alpha_bottom_y(path: Path) -> int:
    _x1, _y1, _x2, y2 = alpha_bounds(path)
    return y2


def visible_height(path: Path) -> int:
    _x1, y1, _x2, y2 = alpha_bounds(path)
    return y2 - y1 + 1


def median(values: list[int]) -> float:
    ordered = sorted(values)
    require(len(ordered) > 0, "median requires at least one value")
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def main() -> None:
    for name, expected_count in SOURCES.items():
        path = SOURCE_DIR / name
        require(path.exists(), f"missing source sheet: {path}")
        actual_count = count_components(path)
        require(actual_count == expected_count, f"{name} expected {expected_count} components, got {actual_count}")

    require(SPRITE_FRAMES.exists(), f"missing SpriteFrames: {SPRITE_FRAMES}")
    sprite_text = SPRITE_FRAMES.read_text(encoding="utf-8")

    expected_total = sum(frame_count for frame_count, _speed in ANIMATIONS.values())
    actual_total = len(list(FRAME_DIR.glob("*.png")))
    require(actual_total == expected_total, f"expected {expected_total} frame pngs, got {actual_total}")

    heights_by_animation: dict[str, list[int]] = {}
    for animation, (frame_count, speed) in ANIMATIONS.items():
        require(f'name": &"{animation}"' in sprite_text, f"missing animation: {animation}")
        require(f'"speed": {speed:.1f}' in sprite_text, f"{animation} must use speed {speed:.1f}")
        paths = sorted(FRAME_DIR.glob(f"{animation}_*.png"))
        require(len(paths) == frame_count, f"{animation} expected {frame_count} frames, got {len(paths)}")
        heights_by_animation[animation] = []
        for path in paths:
            bottom = alpha_bottom_y(path)
            require(bottom == FOOT_BASELINE_Y, f"{path.name} baseline must be {FOOT_BASELINE_Y}, got {bottom}")
            heights_by_animation[animation].append(visible_height(path))

    for suffix in ("down", "up", "left", "right"):
        walk = median(heights_by_animation[f"player_walk_{suffix}"])
        for state in ("idle", "interact"):
            actual = median(heights_by_animation[f"player_{state}_{suffix}"])
            require(
                abs(actual - walk) <= 3.0,
                f"player_{state}_{suffix} height {actual:.1f} must match walk height {walk:.1f}",
            )

    side_walk = (
        median(heights_by_animation["player_walk_left"])
        + median(heights_by_animation["player_walk_right"])
    ) / 2.0
    require(
        abs(heights_by_animation["player_sit_down_side"][0] - side_walk) <= 5.0,
        "player_sit_down_side first frame must match side-walk standing height",
    )
    require(
        abs(heights_by_animation["player_stand_up_side"][-1] - side_walk) <= 5.0,
        "player_stand_up_side last frame must match side-walk standing height",
    )
    sit_idle = median(heights_by_animation["player_sit_idle_side"])
    require(
        side_walk * 0.55 <= sit_idle <= side_walk * 0.85,
        f"player_sit_idle_side seated height {sit_idle:.1f} must stay naturally shorter than standing height {side_walk:.1f}",
    )

    print("OK: protagonist animation assets validated")


if __name__ == "__main__":
    main()
