from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import cv2


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "production" / "assets" / "protagonist" / "launch_quality" / "raw_samples"
OUT_DIR = ROOT / "production" / "assets" / "protagonist" / "launch_quality" / "sample_source_strips"
PREVIEW = ROOT / ".codex" / "protagonist_launch_quality_sample_preview.png"

SOURCE_SLOT_SIZE = (384, 576)
RUNTIME_FRAME_SIZE = (192, 288)
SOURCE_BASELINE_Y = 540
RUNTIME_BASELINE_Y = 270


@dataclass(frozen=True)
class SampleSpec:
    animation: str
    frames: int


SAMPLES = [
    SampleSpec("player_idle_down", 4),
    SampleSpec("player_walk_down", 8),
    SampleSpec("player_walk_left", 8),
    SampleSpec("player_walk_right", 8),
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def alpha_bounds(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = np.array(image.convert("RGBA"))[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        fail("empty frame alpha")
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def clean_components(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[:, :, 3]
    mask = (alpha > 10).astype(np.uint8)
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(mask, 8)
    if count <= 1:
        return rgba

    areas = stats[1:, cv2.CC_STAT_AREA]
    largest = int(areas.max()) if len(areas) else 0
    keep = np.zeros(mask.shape, dtype=bool)
    min_area = max(260, int(largest * 0.03))
    for idx in range(1, count):
        area = int(stats[idx, cv2.CC_STAT_AREA])
        if area >= min_area:
            keep |= labels == idx

    arr[:, :, 3] = np.where(keep, alpha, 0).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def fit_to_source_slot(frame: Image.Image) -> Image.Image:
    frame = clean_components(frame)
    x1, y1, x2, y2 = alpha_bounds(frame)
    subject = frame.crop((x1, y1, x2 + 1, y2 + 1))
    subject_w, subject_h = subject.size

    max_w = 248
    max_h = 500
    scale = min(max_w / subject_w, max_h / subject_h)
    new_size = (max(1, int(subject_w * scale)), max(1, int(subject_h * scale)))
    subject = subject.resize(new_size, Image.Resampling.LANCZOS)

    out = Image.new("RGBA", SOURCE_SLOT_SIZE, (0, 0, 0, 0))
    x = (SOURCE_SLOT_SIZE[0] - new_size[0]) // 2
    y = SOURCE_BASELINE_Y - new_size[1]
    y = max(8, min(y, SOURCE_SLOT_SIZE[1] - new_size[1]))
    out.alpha_composite(subject, (x, y))
    return out


def split_equal_slots(image: Image.Image, count: int) -> list[Image.Image]:
    frames: list[Image.Image] = []
    w, h = image.size
    for idx in range(count):
        x1 = int(round(idx * w / count))
        x2 = int(round((idx + 1) * w / count))
        crop = image.crop((x1, 0, x2, h))
        frames.append(fit_to_source_slot(crop))
    return frames


def write_strip(spec: SampleSpec) -> list[Image.Image]:
    source = RAW_DIR / f"{spec.animation}_raw_alpha.png"
    if not source.exists():
        fail(f"missing alpha source: {source}")
    image = Image.open(source).convert("RGBA")
    frames = split_equal_slots(image, spec.frames)

    strip = Image.new("RGBA", (SOURCE_SLOT_SIZE[0] * spec.frames, SOURCE_SLOT_SIZE[1]), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        strip.alpha_composite(frame, (idx * SOURCE_SLOT_SIZE[0], 0))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    strip.save(OUT_DIR / f"{spec.animation}_source_strip.png")
    return frames


def runtime_preview_frame(source_frame: Image.Image) -> Image.Image:
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
    label_w = 190
    cols = 8
    rows = len(SAMPLES)
    cell_w, cell_h = RUNTIME_FRAME_SIZE
    canvas = Image.new("RGBA", (label_w + cols * cell_w, rows * cell_h), (238, 232, 217, 255))
    draw = ImageDraw.Draw(canvas)
    for row, spec in enumerate(SAMPLES):
        y = row * cell_h
        draw.text((10, y + 12), spec.animation, fill=(34, 32, 28, 255))
        frames = all_frames[spec.animation]
        for col in range(cols):
            frame = runtime_preview_frame(frames[col % len(frames)])
            x = label_w + col * cell_w
            canvas.alpha_composite(frame, (x, y))
            draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(174, 163, 141, 160))
            draw.line((x, y + RUNTIME_BASELINE_Y, x + cell_w, y + RUNTIME_BASELINE_Y), fill=(180, 70, 60, 120))
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(PREVIEW)


def main() -> None:
    all_frames: dict[str, list[Image.Image]] = {}
    for spec in SAMPLES:
        all_frames[spec.animation] = write_strip(spec)
    write_preview(all_frames)
    print(f"OK: wrote launch-quality sample strips -> {OUT_DIR}")
    print(f"OK: wrote preview -> {PREVIEW}")


if __name__ == "__main__":
    main()
