from __future__ import annotations

from pathlib import Path
import re

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FRAME_DIR = ROOT / "sprites" / "characters" / "protagonist" / "frames"
FINAL_STRIP_DIR = ROOT / "production" / "assets" / "protagonist" / "final_source_strips"

FRAME_SIZE = (192, 288)
FOOT_BASELINE_Y = 270

FINAL_STRIPS = {
    "player_walk_down": 8,
    "player_walk_down_left": 8,
    "player_walk_left": 8,
    "player_walk_up_left": 8,
    "player_walk_up": 8,
    "player_walk_up_right": 8,
    "player_walk_right": 8,
    "player_walk_down_right": 8,
    "player_idle_down": 4,
    "player_idle_down_left": 4,
    "player_idle_left": 4,
    "player_idle_up_left": 4,
    "player_idle_up": 4,
    "player_idle_up_right": 4,
    "player_idle_right": 4,
    "player_idle_down_right": 4,
    "player_interact_down": 6,
    "player_interact_down_left": 6,
    "player_interact_left": 6,
    "player_interact_up_left": 6,
    "player_interact_up": 6,
    "player_interact_up_right": 6,
    "player_interact_right": 6,
    "player_interact_down_right": 6,
    "player_sit_down_side": 6,
    "player_sit_down_down": 6,
    "player_sit_down_up": 6,
    "player_sit_idle_side": 6,
    "player_sit_idle_down": 6,
    "player_sit_idle_up": 6,
    "player_stand_up_side": 6,
    "player_stand_up_down": 6,
    "player_stand_up_up": 6,
}

DIAGONAL_WALK_ANIMATIONS = (
    "player_walk_down_left",
    "player_walk_up_left",
    "player_walk_up_right",
    "player_walk_down_right",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def animation_frame_paths(animation: str) -> list[Path]:
    pattern = re.compile(rf"^{re.escape(animation)}_(\d{{2}})\.png$")
    matches: list[tuple[int, Path]] = []
    for path in FRAME_DIR.glob("*.png"):
        match = pattern.match(path.name)
        if match:
            matches.append((int(match.group(1)), path))
    matches.sort(key=lambda item: item[0])
    return [path for _idx, path in matches]


def alpha(path: Path) -> np.ndarray:
    image = Image.open(path).convert("RGBA")
    require(image.size == FRAME_SIZE, f"{path.name} must be {FRAME_SIZE}")
    return np.array(image)[:, :, 3]


def bounds(mask: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.where(mask)
    require(len(xs) > 0, "empty alpha mask")
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def lower_band_metrics(animation: str) -> dict[str, float]:
    paths = animation_frame_paths(animation)
    require(len(paths) == 8, f"{animation} expected 8 frames")

    masks: list[np.ndarray] = []
    centers: list[float] = []
    widths: list[int] = []
    areas: list[int] = []
    bottoms: list[int] = []

    for path in paths:
        a = alpha(path)
        visible = a > 10
        _x1, _y1, _x2, y2 = bounds(visible)
        bottoms.append(y2)
        lower = a[245 : FOOT_BASELINE_Y + 2, :] > 10
        ys, xs = np.where(lower)
        require(len(xs) >= 120, f"{path.name} has too little lower-body alpha for gait validation")
        masks.append(lower)
        centers.append(float(xs.mean()))
        widths.append(int(xs.max() - xs.min() + 1))
        areas.append(int(lower.sum()))

    diffs = [float(np.logical_xor(masks[idx], masks[idx - 1]).sum()) for idx in range(1, len(masks))]
    return {
        "center_range": max(centers) - min(centers),
        "width_range": float(max(widths) - min(widths)),
        "area_range": float(max(areas) - min(areas)),
        "mean_adjacent_diff": float(sum(diffs) / len(diffs)),
        "max_adjacent_diff": float(max(diffs)),
        "baseline_min": float(min(bottoms)),
        "baseline_max": float(max(bottoms)),
    }


def validate_no_exact_duplicates(animation: str) -> None:
    paths = animation_frame_paths(animation)
    seen: dict[bytes, Path] = {}
    for path in paths:
        digest = Image.open(path).convert("RGBA").tobytes()
        if digest in seen:
            fail(f"{animation} duplicate frames: {seen[digest].name} and {path.name}")
        seen[digest] = path


def validate_diagonal_walk(animation: str) -> None:
    validate_no_exact_duplicates(animation)
    metrics = lower_band_metrics(animation)
    require(metrics["mean_adjacent_diff"] >= 130.0, f"{animation} adjacent foot shapes are too similar: {metrics}")
    require(metrics["max_adjacent_diff"] >= 220.0, f"{animation} lacks a strong passing/contact pose: {metrics}")


def validate_side_walk(animation: str) -> None:
    metrics = lower_band_metrics(animation)
    require(
        metrics["baseline_min"] == FOOT_BASELINE_Y and metrics["baseline_max"] == FOOT_BASELINE_Y,
        f"{animation} foot baseline drifted: {metrics}",
    )
    require(metrics["center_range"] >= 1.5, f"{animation} lower-body center barely changes: {metrics}")
    require(metrics["width_range"] >= 6.0, f"{animation} lower-body width barely changes: {metrics}")
    require(metrics["area_range"] >= 90.0, f"{animation} lower-body silhouette area barely changes: {metrics}")
    require(metrics["mean_adjacent_diff"] >= 130.0, f"{animation} adjacent foot shapes are too similar: {metrics}")
    require(metrics["max_adjacent_diff"] >= 220.0, f"{animation} lacks a strong passing/contact pose: {metrics}")


def validate_final_source_strips() -> None:
    require(FINAL_STRIP_DIR.exists(), f"missing final source strip dir: {FINAL_STRIP_DIR}")
    for animation, frame_count in FINAL_STRIPS.items():
        path = FINAL_STRIP_DIR / f"{animation}_source_strip.png"
        require(path.exists(), f"missing final source strip: {path.name}")
        image = Image.open(path).convert("RGBA")
        expected_size = (384 * frame_count, 576)
        require(image.size == expected_size, f"{path.name} must be {expected_size}, got {image.size}")
        for idx in range(frame_count):
            crop = image.crop((idx * 384, 0, (idx + 1) * 384, 576))
            alpha_channel = np.array(crop)[:, :, 3]
            visible = alpha_channel > 10
            require(int(visible.sum()) >= 18000, f"{path.name} slot {idx:02d} has too little visible alpha")
            require(
                int(((alpha_channel > 0) & (alpha_channel < 255)).sum()) >= 240,
                f"{path.name} slot {idx:02d} lost soft alpha edge detail",
            )


def validate_diagonal_rows_are_not_mixed() -> None:
    for state, frame_count in (("walk", 8), ("idle", 4), ("interact", 6)):
        for suffix in ("down_left", "up_left", "up_right", "down_right"):
            animation = f"player_{state}_{suffix}"
            paths = animation_frame_paths(animation)
            require(len(paths) == frame_count, f"{animation} expected {frame_count} frames")
            for path in paths:
                a = alpha(path)
                visible = a > 10
                ghost_band = (a > 50) & (a < 130)
                ghost_ratio = float(ghost_band.sum()) / max(1.0, float(visible.sum()))
                require(ghost_ratio <= 0.18, f"{path.name} still reads like a mixed/ghost frame: ghost_ratio={ghost_ratio:.3f}")


def main() -> None:
    validate_final_source_strips()
    validate_diagonal_rows_are_not_mixed()
    validate_side_walk("player_walk_left")
    validate_side_walk("player_walk_right")
    for animation in DIAGONAL_WALK_ANIMATIONS:
        validate_diagonal_walk(animation)
    print("OK: protagonist final asset quality validated")


if __name__ == "__main__":
    main()
