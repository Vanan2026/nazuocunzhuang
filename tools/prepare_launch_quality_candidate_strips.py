from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "production" / "assets" / "protagonist" / "launch_quality" / "raw_final"
CANDIDATE_DIR = ROOT / "production" / "assets" / "protagonist" / "launch_quality" / "candidate_source_strips"
PREVIEW = ROOT / ".codex" / "protagonist_launch_quality_full_preview.png"

SOURCE_SLOT_SIZE = (384, 576)
SOURCE_BASELINE_Y = 540
RUNTIME_FRAME_SIZE = (192, 288)
RUNTIME_BASELINE_Y = 270


@dataclass(frozen=True)
class StripSpec:
    animation: str
    frames: int
    target_height: int = 500
    height_scale: float = 1.0


SPECS = [
    StripSpec("player_walk_down", 8),
    StripSpec("player_walk_down_left", 8),
    StripSpec("player_walk_left", 8),
    StripSpec("player_walk_up_left", 8),
    StripSpec("player_walk_up", 8),
    StripSpec("player_walk_up_right", 8, 512),
    StripSpec("player_walk_right", 8),
    StripSpec("player_walk_down_right", 8),
    StripSpec("player_idle_down", 4, 488),
    StripSpec("player_idle_down_left", 4, 491),
    StripSpec("player_idle_left", 4),
    StripSpec("player_idle_up_left", 4),
    StripSpec("player_idle_up", 4),
    StripSpec("player_idle_up_right", 4, 500),
    StripSpec("player_idle_right", 4),
    StripSpec("player_idle_down_right", 4, 490),
    StripSpec("player_interact_down", 6),
    StripSpec("player_interact_down_left", 6),
    StripSpec("player_interact_left", 6),
    StripSpec("player_interact_up_left", 6, 549, 1.10),
    StripSpec("player_interact_up", 6, 508),
    StripSpec("player_interact_up_right", 6, 545, 1.09),
    StripSpec("player_interact_right", 6, 520, 1.04),
    StripSpec("player_interact_down_right", 6, 492),
    StripSpec("player_sit_down_side", 6),
    StripSpec("player_sit_down_down", 6),
    StripSpec("player_sit_down_up", 6),
    StripSpec("player_sit_idle_side", 6, 360),
    StripSpec("player_sit_idle_down", 6, 360),
    StripSpec("player_sit_idle_up", 6, 360),
    StripSpec("player_stand_up_side", 6),
    StripSpec("player_stand_up_down", 6),
    StripSpec("player_stand_up_up", 6),
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def chroma_to_alpha(image: Image.Image) -> Image.Image:
    rgb = np.array(image.convert("RGB")).astype(np.int16)
    h, w, _ = rgb.shape
    border = np.concatenate([rgb[0, :, :], rgb[h - 1, :, :], rgb[:, 0, :], rgb[:, w - 1, :]], axis=0)
    key = np.median(border, axis=0)
    dist = np.linalg.norm(rgb - key, axis=2)
    alpha = np.clip((dist - 26.0) / 72.0, 0.0, 1.0)
    alpha = (alpha * alpha * (3.0 - 2.0 * alpha) * 255.0).astype(np.uint8)

    # Despill green-screen edges without touching the teal skirt too aggressively.
    out = rgb.astype(np.int16)
    green_excess = out[:, :, 1] - np.maximum(out[:, :, 0], out[:, :, 2])
    spill = (alpha > 0) & (alpha < 245) & (green_excess > 10)
    out[:, :, 1] = np.where(spill, np.maximum(out[:, :, 0], out[:, :, 2]) + 4, out[:, :, 1])
    out = np.clip(out, 0, 255).astype(np.uint8)
    rgba = np.dstack([out, alpha])
    return Image.fromarray(rgba, "RGBA")


def clean_components(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[:, :, 3]
    mask = (alpha > 10).astype(np.uint8)
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(mask, 8)
    if count <= 1:
        return rgba
    largest = int(stats[1:, cv2.CC_STAT_AREA].max())
    keep = np.zeros(mask.shape, dtype=bool)
    min_area = max(260, int(largest * 0.025))
    for idx in range(1, count):
        if int(stats[idx, cv2.CC_STAT_AREA]) >= min_area:
            keep |= labels == idx
    arr[:, :, 3] = np.where(keep, alpha, 0).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def alpha_bounds(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = np.array(image.convert("RGBA"))[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        fail("empty frame alpha")
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def split_raw_strip(spec: StripSpec) -> list[Image.Image]:
    path = RAW_DIR / f"{spec.animation}_raw_chromakey.png"
    if not path.exists():
        fail(f"missing raw strip: {path}")
    image = chroma_to_alpha(Image.open(path))
    w, h = image.size
    frames: list[Image.Image] = []
    for idx in range(spec.frames):
        x1 = int(round(idx * w / spec.frames))
        x2 = int(round((idx + 1) * w / spec.frames))
        frames.append(clean_components(image.crop((x1, 0, x2, h))))
    return repair_weak_frames(frames)


def alpha_area(image: Image.Image) -> int:
    alpha = np.array(image.convert("RGBA"))[:, :, 3]
    return int((alpha > 10).sum())


def repair_weak_frames(frames: list[Image.Image]) -> list[Image.Image]:
    areas = [alpha_area(frame) for frame in frames]
    useful = [area for area in areas if area > 0]
    if not useful:
        return frames
    median_area = float(np.median(useful))
    repaired = list(frames)
    for idx, area in enumerate(areas):
        if area >= median_area * 0.35:
            continue
        replacement = None
        for offset in range(1, len(frames)):
            for candidate in (idx - offset, idx + offset):
                if 0 <= candidate < len(frames) and areas[candidate] >= median_area * 0.55:
                    replacement = repaired[candidate].copy()
                    break
            if replacement is not None:
                break
        if replacement is not None:
            repaired[idx] = replacement
    return repaired


def normalize_strip(spec: StripSpec, frames: list[Image.Image]) -> list[Image.Image]:
    crops: list[Image.Image] = []
    widths: list[int] = []
    heights: list[int] = []
    for frame in frames:
        x1, y1, x2, y2 = alpha_bounds(frame)
        crop = frame.crop((x1, y1, x2 + 1, y2 + 1))
        crops.append(crop)
        widths.append(crop.width)
        heights.append(crop.height)

    scale = min(248 / max(widths), spec.target_height / max(heights))
    output: list[Image.Image] = []
    for crop in crops:
        size = (max(1, int(crop.width * scale)), max(1, int(crop.height * scale * spec.height_scale)))
        subject = crop.resize(size, Image.Resampling.LANCZOS)
        slot = Image.new("RGBA", SOURCE_SLOT_SIZE, (0, 0, 0, 0))
        x = (SOURCE_SLOT_SIZE[0] - size[0]) // 2
        y = SOURCE_BASELINE_Y - size[1]
        y = max(8, min(y, SOURCE_SLOT_SIZE[1] - size[1]))
        slot.alpha_composite(subject, (x, y))
        output.append(slot)
    return output


def write_source_strip(spec: StripSpec, frames: list[Image.Image]) -> None:
    strip = Image.new("RGBA", (SOURCE_SLOT_SIZE[0] * spec.frames, SOURCE_SLOT_SIZE[1]), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        strip.alpha_composite(frame, (idx * SOURCE_SLOT_SIZE[0], 0))
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    strip.save(CANDIDATE_DIR / f"{spec.animation}_source_strip.png")


def runtime_frame(source_frame: Image.Image) -> Image.Image:
    frame = source_frame.resize(RUNTIME_FRAME_SIZE, Image.Resampling.LANCZOS)
    alpha = np.array(frame)[:, :, 3]
    ys, _xs = np.where(alpha > 10)
    if len(ys) == 0:
        return frame
    dy = RUNTIME_BASELINE_Y - int(ys.max())
    if dy == 0:
        return frame
    out = Image.new("RGBA", RUNTIME_FRAME_SIZE, (0, 0, 0, 0))
    out.alpha_composite(frame, (0, dy))
    return out


def write_preview(all_frames: dict[str, list[Image.Image]]) -> None:
    label_w = 215
    cols = 8
    cell_w, cell_h = RUNTIME_FRAME_SIZE
    canvas = Image.new("RGBA", (label_w + cols * cell_w, len(SPECS) * cell_h), (238, 232, 217, 255))
    draw = ImageDraw.Draw(canvas)
    for row_idx, spec in enumerate(SPECS):
        y = row_idx * cell_h
        draw.text((8, y + 12), spec.animation, fill=(34, 32, 28, 255))
        frames = all_frames[spec.animation]
        for col in range(cols):
            x = label_w + col * cell_w
            frame = runtime_frame(frames[col % len(frames)])
            canvas.alpha_composite(frame, (x, y))
            draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(174, 163, 141, 160))
            draw.line((x, y + RUNTIME_BASELINE_Y, x + cell_w, y + RUNTIME_BASELINE_Y), fill=(180, 70, 60, 120))
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(PREVIEW)


def main() -> None:
    all_frames: dict[str, list[Image.Image]] = {}
    for spec in SPECS:
        raw_frames = split_raw_strip(spec)
        frames = normalize_strip(spec, raw_frames)
        all_frames[spec.animation] = frames
        write_source_strip(spec, frames)
    write_preview(all_frames)
    print(f"OK: wrote candidate strips -> {CANDIDATE_DIR}")
    print(f"OK: wrote preview -> {PREVIEW}")


if __name__ == "__main__":
    main()
