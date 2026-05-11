from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "sprites" / "characters" / "protagonist" / "source"
OUT_DIR = ROOT / "sprites" / "characters" / "protagonist" / "frames"
SPRITE_FRAMES = ROOT / "sprites" / "characters" / "protagonist" / "player_mvp_4dir_frames.tres"
PREVIEW = ROOT / ".codex" / "protagonist_mvp_animation_preview.png"
SCENE_PREVIEW = ROOT / ".codex" / "protagonist_mvp_scene_preview.png"
SCALE_DEPTH_PREVIEW = ROOT / ".codex" / "protagonist_scale_depth_preview.png"
SCENE_BG = ROOT / "resources" / "design" / "CloudVillageHomeyard_no_character_master.png"

WALK_SHEET = SOURCE_DIR / "protagonist_generated_walk_4dir_sheet.png"
IDLE_SHEET = SOURCE_DIR / "protagonist_generated_idle_4dir_sheet.png"
INTERACT_SHEET = SOURCE_DIR / "protagonist_generated_interact_4dir_sheet.png"
SIT_SHEET = SOURCE_DIR / "protagonist_generated_sit_side_sheet.png"

FRAME_SIZE = (192, 288)
FOOT_ANCHOR = (96, 280)
VISUAL_BASE_SCALE = 1.0
DEPTH_Y_FAR = 456.0
DEPTH_Y_NEAR = 706.0
DEPTH_SCALE_FAR = 0.90
DEPTH_SCALE_NEAR = 1.15


@dataclass(frozen=True)
class RowSpec:
    animation: str
    loop: bool
    speed: float
    expected: int


WALK_ANIMS = ["player_walk_down", "player_walk_up", "player_walk_left", "player_walk_right"]
IDLE_ANIMS = ["player_idle_down", "player_idle_up", "player_idle_left", "player_idle_right"]
INTERACT_ANIMS = ["player_interact_down", "player_interact_up", "player_interact_left", "player_interact_right"]
SIT_ANIMS = ["player_sit_down_side", "player_sit_idle_side", "player_stand_up_side"]
DIRECTION_SUFFIXES = ["down", "up", "left", "right"]

ROWS = [
    RowSpec("player_walk_down", True, 7.0, 8),
    RowSpec("player_walk_up", True, 7.0, 8),
    RowSpec("player_walk_left", True, 6.5, 8),
    RowSpec("player_walk_right", True, 6.5, 8),
    RowSpec("player_idle_down", True, 5.0, 4),
    RowSpec("player_idle_up", True, 5.0, 4),
    RowSpec("player_idle_left", True, 5.0, 4),
    RowSpec("player_idle_right", True, 5.0, 4),
    RowSpec("player_interact_down", False, 10.0, 6),
    RowSpec("player_interact_up", False, 10.0, 6),
    RowSpec("player_interact_left", False, 10.0, 6),
    RowSpec("player_interact_right", False, 10.0, 6),
    RowSpec("player_sit_down_side", False, 8.0, 6),
    RowSpec("player_sit_idle_side", True, 5.0, 6),
    RowSpec("player_stand_up_side", False, 8.0, 6),
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


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


def extract_grid_boxes(sheet_path: Path, expected_rows: int, expected_cols: int) -> list[list[tuple[int, int, int, int]]]:
    image = Image.open(sheet_path).convert("RGB")
    rgb = np.array(image)
    mask = foreground_mask(rgb)
    count, _labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)

    boxes: list[tuple[int, int, int, int, float, float]] = []
    for idx in range(1, count):
        x, y, w, h, area = stats[idx]
        if area < 700:
            continue
        cx, cy = centroids[idx]
        boxes.append((x, y, x + w, y + h, float(cx), float(cy)))

    expected_total = expected_rows * expected_cols
    if len(boxes) != expected_total:
        fail(f"{sheet_path.name} expected {expected_total} components, found {len(boxes)}")

    boxes.sort(key=lambda item: item[5])
    rows: list[list[tuple[int, int, int, int, float, float]]] = []
    row_gap = max(24.0, image.height / (expected_rows * 3.0))
    for box in boxes:
        if not rows:
            rows.append([box])
            continue
        row_center = sum(item[5] for item in rows[-1]) / len(rows[-1])
        if abs(box[5] - row_center) <= row_gap:
            rows[-1].append(box)
        else:
            rows.append([box])

    if len(rows) != expected_rows:
        fail(f"{sheet_path.name} expected {expected_rows} rows, found {len(rows)}")

    ordered: list[list[tuple[int, int, int, int]]] = []
    for row_idx, row in enumerate(rows):
        row = sorted(row, key=lambda item: item[4])
        if len(row) != expected_cols:
            fail(f"{sheet_path.name} row {row_idx} expected {expected_cols} cols, found {len(row)}")
        ordered.append([(x1, y1, x2, y2) for (x1, y1, x2, y2, _cx, _cy) in row])
    return ordered


def chroma_to_alpha(crop: Image.Image) -> Image.Image:
    rgba = np.array(crop.convert("RGBA")).astype(np.uint8)
    r = rgba[:, :, 0].astype(np.float32)
    g = rgba[:, :, 1].astype(np.float32)
    b = rgba[:, :, 2].astype(np.float32)

    score = g - np.maximum(r, b)
    alpha = np.clip((62.0 - score) / 40.0, 0.0, 1.0)
    rgba[:, :, 3] = np.round(alpha * 255.0).astype(np.uint8)

    translucent = rgba[:, :, 3] < 245
    max_rb = np.maximum(r, b)
    rgba[:, :, 1] = np.where(translucent, np.minimum(g, max_rb + 8.0), g).astype(np.uint8)

    kernel = np.ones((2, 2), np.uint8)
    a = cv2.morphologyEx(rgba[:, :, 3], cv2.MORPH_OPEN, kernel)
    rgba[:, :, 3] = a
    return Image.fromarray(rgba, "RGBA")


def crop_foreground(image: Image.Image, box: tuple[int, int, int, int]) -> tuple[Image.Image, int]:
    pad = 10
    raw_x1, raw_y1, raw_x2, raw_y2 = box
    x1, y1, x2, y2 = raw_x1, raw_y1, raw_x2, raw_y2
    x1 = max(0, x1 - pad)
    y1 = max(0, y1 - pad)
    x2 = min(image.width, x2 + pad)
    y2 = min(image.height, y2 + pad)

    crop = chroma_to_alpha(image.crop((x1, y1, x2, y2)))
    alpha = np.array(crop)[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        fail("chroma extraction produced empty frame")
    bx1 = int(xs.min())
    by1 = int(ys.min())
    bx2 = int(xs.max()) + 1
    by2 = int(ys.max()) + 1
    trimmed = crop.crop((bx1, by1, bx2, by2))
    comp_bottom_in_crop = min(y2 - y1, max(1, raw_y2 - y1))
    foot_local = max(0, min(trimmed.height - 1, comp_bottom_in_crop - by1 - 1))
    return trimmed, foot_local


def normalize_frame(frame: Image.Image, foot_local: int, scale_override: float | None = None) -> Image.Image:
    dst_w, dst_h = FRAME_SIZE
    src_w, src_h = frame.size

    if scale_override is None:
        fit_ratio = min((dst_w - 6) / max(1, src_w), (dst_h - 6) / max(1, src_h))
        fit_ratio = max(0.1, min(1.0, fit_ratio))
    else:
        fit_ratio = scale_override
        max_fit = min((dst_w - 6) / max(1, src_w), (dst_h - 6) / max(1, src_h))
        fit_ratio = max(0.1, min(max_fit, fit_ratio))
    resized = frame.resize(
        (max(1, round(src_w * fit_ratio)), max(1, round(src_h * fit_ratio))),
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    rw, rh = resized.size
    x = (dst_w - rw) // 2
    scaled_foot = round(foot_local * fit_ratio)
    y = FOOT_ANCHOR[1] - scaled_foot
    y = max(0, min(dst_h - rh, y))
    canvas.alpha_composite(resized, (x, y))
    return canvas


def visible_bounds(frame: Image.Image) -> tuple[int, int, int, int]:
    alpha = np.array(frame.convert("RGBA"))[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        return (0, 0, 0, 0)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def visible_height(frame: Image.Image) -> int:
    _x1, y1, _x2, y2 = visible_bounds(frame)
    return max(0, y2 - y1)


def rescale_to_height(frame: Image.Image, target_height: float) -> Image.Image:
    current_height = visible_height(frame)
    if current_height <= 0:
        return frame
    scale = target_height / current_height
    if abs(scale - 1.0) < 0.015:
        return frame

    x1, y1, x2, y2 = visible_bounds(frame)
    trim = frame.crop((x1, y1, x2, y2))
    resized = trim.resize(
        (max(1, round(trim.width * scale)), max(1, round(trim.height * scale))),
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    x = (FRAME_SIZE[0] - resized.width) // 2
    y = FOOT_ANCHOR[1] - resized.height + 1
    y = max(0, min(FRAME_SIZE[1] - resized.height, y))
    canvas.alpha_composite(resized, (x, y))
    return canvas


def match_row_height(frames: list[Image.Image], target_height: float) -> list[Image.Image]:
    return [rescale_to_height(frame, target_height) for frame in frames]


def median_visible_height(frames: list[Image.Image]) -> float:
    heights = sorted(visible_height(frame) for frame in frames if visible_height(frame) > 0)
    if not heights:
        return 0.0
    mid = len(heights) // 2
    if len(heights) % 2 == 1:
        return float(heights[mid])
    return (heights[mid - 1] + heights[mid]) / 2.0


def raw_scale_for_target_height(frame: Image.Image, target_height: float) -> float:
    height = max(1, frame.height)
    return max(0.1, target_height / height)


def alpha_bottom_y(frame: Image.Image) -> int:
    alpha = np.array(frame.convert("RGBA"))[:, :, 3]
    ys = np.where(alpha > 10)[0]
    if len(ys) == 0:
        return FRAME_SIZE[1] - 1
    return int(ys.max())


def shift_frame_y(frame: Image.Image, dy: int) -> Image.Image:
    if dy == 0:
        return frame
    w, h = frame.size
    src = np.array(frame.convert("RGBA"))
    dst = np.zeros_like(src)
    if dy > 0:
        if dy >= h:
            return Image.fromarray(dst, "RGBA")
        dst[dy:, :, :] = src[: h - dy, :, :]
    else:
        up = -dy
        if up >= h:
            return Image.fromarray(dst, "RGBA")
        dst[: h - up, :, :] = src[up:, :, :]
    return Image.fromarray(dst, "RGBA")


def align_row_baseline(frames: list[Image.Image], target_bottom: int = 270) -> list[Image.Image]:
    aligned: list[Image.Image] = []
    for frame in frames:
        current_bottom = alpha_bottom_y(frame)
        dy = target_bottom - current_bottom
        aligned.append(shift_frame_y(frame, dy))
    return aligned


def collect_animation_frames() -> dict[str, list[Image.Image]]:
    if not WALK_SHEET.exists():
        fail(f"missing walk sheet: {WALK_SHEET}")
    if not IDLE_SHEET.exists():
        fail(f"missing idle sheet: {IDLE_SHEET}")
    if not INTERACT_SHEET.exists():
        fail(f"missing interact sheet: {INTERACT_SHEET}")

    walk_image = Image.open(WALK_SHEET).convert("RGBA")
    idle_image = Image.open(IDLE_SHEET).convert("RGBA")
    interact_image = Image.open(INTERACT_SHEET).convert("RGBA")
    walk_rows = extract_grid_boxes(WALK_SHEET, expected_rows=4, expected_cols=8)
    idle_rows = extract_grid_boxes(IDLE_SHEET, expected_rows=4, expected_cols=4)
    interact_rows = extract_grid_boxes(INTERACT_SHEET, expected_rows=4, expected_cols=6)
    sit_image = Image.open(SIT_SHEET).convert("RGBA") if SIT_SHEET.exists() else None
    sit_rows = extract_grid_boxes(SIT_SHEET, expected_rows=3, expected_cols=6) if SIT_SHEET.exists() else []

    frames: dict[str, list[Image.Image]] = {}
    direction_heights: dict[str, float] = {}

    for suffix, anim, boxes in zip(DIRECTION_SUFFIXES, WALK_ANIMS, walk_rows):
        row_frames: list[Image.Image] = []
        for box in boxes:
            crop, foot = crop_foreground(walk_image, box)
            row_frames.append(normalize_frame(crop, foot))
        aligned = align_row_baseline(row_frames)
        frames[anim] = aligned
        direction_heights[suffix] = median_visible_height(aligned)

    for suffix, anim, boxes in zip(DIRECTION_SUFFIXES, IDLE_ANIMS, idle_rows):
        row_frames = []
        for box in boxes:
            crop, foot = crop_foreground(idle_image, box)
            row_frames.append(normalize_frame(crop, foot))
        matched = match_row_height(row_frames, direction_heights[suffix])
        frames[anim] = align_row_baseline(matched)

    for suffix, anim, boxes in zip(DIRECTION_SUFFIXES, INTERACT_ANIMS, interact_rows):
        row_frames = []
        for box in boxes:
            crop, foot = crop_foreground(interact_image, box)
            row_frames.append(normalize_frame(crop, foot))
        matched = match_row_height(row_frames, direction_heights[suffix])
        frames[anim] = align_row_baseline(matched)

    if sit_image is not None:
        side_target = (direction_heights["left"] + direction_heights["right"]) / 2.0
        first_sit_crop, _first_sit_foot = crop_foreground(sit_image, sit_rows[0][0])
        last_stand_crop, _last_stand_foot = crop_foreground(sit_image, sit_rows[2][-1])
        sit_scale = (
            raw_scale_for_target_height(first_sit_crop, side_target)
            + raw_scale_for_target_height(last_stand_crop, side_target)
        ) / 2.0
        for anim, boxes in zip(SIT_ANIMS, sit_rows):
            row_frames = []
            for box in boxes:
                crop, foot = crop_foreground(sit_image, box)
                row_frames.append(normalize_frame(crop, foot, sit_scale))
            frames[anim] = align_row_baseline(row_frames)

    return frames


def write_frames(animation_frames: dict[str, list[Image.Image]]) -> dict[str, list[Path]]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in OUT_DIR.glob("*.png"):
        path.unlink()

    written: dict[str, list[Path]] = {}
    for spec in ROWS:
        row = animation_frames.get(spec.animation, [])
        if len(row) != spec.expected:
            fail(f"{spec.animation} expected {spec.expected} frames, got {len(row)}")
        paths: list[Path] = []
        for idx, frame in enumerate(row):
            out = OUT_DIR / f"{spec.animation}_{idx:02d}.png"
            frame.save(out)
            paths.append(out)
        written[spec.animation] = paths
    return written


def build_tres(frame_paths: dict[str, list[Path]]) -> None:
    resources: list[str] = []
    resource_ids: dict[str, str] = {}
    index = 1
    for spec in ROWS:
        for path in frame_paths[spec.animation]:
            key = f"frame_{index}"
            rel = path.relative_to(ROOT).as_posix()
            resources.append(f'[ext_resource type="Texture2D" path="res://{rel}" id="{key}"]')
            resource_ids[str(path)] = key
            index += 1

    animations: list[str] = []
    for spec in ROWS:
        parts = []
        for frame in frame_paths[spec.animation]:
            key = resource_ids[str(frame)]
            parts.append(
                '{\n"duration": 1.0,\n"texture": ExtResource("%s")\n}' % key
            )
        animation_block = (
            '{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %.1f\n}'
            % (", ".join(parts), "true" if spec.loop else "false", spec.animation, spec.speed)
        )
        animations.append(animation_block)

    text = '[gd_resource type="SpriteFrames" load_steps=%d format=3]\n\n%s\n\n[resource]\nanimations = [%s]\n' % (
        len(resources) + 1,
        "\n".join(resources),
        ", ".join(animations),
    )
    SPRITE_FRAMES.write_text(text, encoding="utf-8")


def write_preview(frame_paths: dict[str, list[Path]]) -> None:
    cell_w, cell_h = FRAME_SIZE
    label_w = 210
    rows = len(ROWS)
    cols = max(len(items) for items in frame_paths.values())
    canvas = Image.new("RGBA", (label_w + cols * cell_w, rows * cell_h), (244, 239, 226, 255))
    draw = ImageDraw.Draw(canvas)

    y = 0
    for spec in ROWS:
        draw.text((8, y + 12), spec.animation, fill=(38, 35, 30, 255))
        for idx, frame_path in enumerate(frame_paths[spec.animation]):
            img = Image.open(frame_path).convert("RGBA")
            canvas.alpha_composite(img, (label_w + idx * cell_w, y))
            draw.rectangle(
                (label_w + idx * cell_w, y, label_w + (idx + 1) * cell_w - 1, y + cell_h - 1),
                outline=(190, 180, 160, 160),
            )
        y += cell_h

    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(PREVIEW)


def write_scene_preview(frame_paths: dict[str, list[Path]]) -> None:
    if not SCENE_BG.exists():
        return
    bg = Image.open(SCENE_BG).convert("RGBA").resize((1280, 720), Image.Resampling.LANCZOS)
    player = Image.open(frame_paths["player_idle_down"][0]).convert("RGBA")

    def visual_scale(y: float) -> float:
        t = max(0.0, min(1.0, (y - DEPTH_Y_FAR) / max(1.0, DEPTH_Y_NEAR - DEPTH_Y_FAR)))
        return VISUAL_BASE_SCALE * (DEPTH_SCALE_FAR + (DEPTH_SCALE_NEAR - DEPTH_SCALE_FAR) * t)

    foot = (550, 530)
    scale = visual_scale(foot[1])
    size = (round(FRAME_SIZE[0] * scale), round(FRAME_SIZE[1] * scale))
    scaled = player.resize(size, Image.Resampling.LANCZOS)
    bg.alpha_composite(
        scaled,
        (
            round(foot[0] - FOOT_ANCHOR[0] * scale),
            round(foot[1] - FOOT_ANCHOR[1] * scale),
        ),
    )
    SCENE_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    bg.save(SCENE_PREVIEW)

    depth_bg = Image.open(SCENE_BG).convert("RGBA").resize((1280, 720), Image.Resampling.LANCZOS)
    samples = [((470, 464), "far"), ((610, 530), "spawn"), ((760, 676), "near")]
    draw = ImageDraw.Draw(depth_bg)
    for foot, label in samples:
        scale = visual_scale(foot[1])
        size = (round(FRAME_SIZE[0] * scale), round(FRAME_SIZE[1] * scale))
        scaled = player.resize(size, Image.Resampling.LANCZOS)
        depth_bg.alpha_composite(
            scaled,
            (
                round(foot[0] - FOOT_ANCHOR[0] * scale),
                round(foot[1] - FOOT_ANCHOR[1] * scale),
            ),
        )
        draw.text((foot[0] + 8, foot[1] - 18), f"{label} {scale:.2f}x", fill=(255, 245, 220, 255))
    depth_bg.save(SCALE_DEPTH_PREVIEW)


def main() -> None:
    animation_images = collect_animation_frames()
    frame_paths = write_frames(animation_images)
    build_tres(frame_paths)
    write_preview(frame_paths)
    write_scene_preview(frame_paths)
    print(f"OK: wrote frames -> {OUT_DIR}")
    print(f"OK: wrote SpriteFrames -> {SPRITE_FRAMES}")
    print(f"OK: wrote preview -> {PREVIEW}")
    print(f"OK: wrote scene preview -> {SCENE_PREVIEW}")
    print(f"OK: wrote scale/depth preview -> {SCALE_DEPTH_PREVIEW}")


if __name__ == "__main__":
    main()
