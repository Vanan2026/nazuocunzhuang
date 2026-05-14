from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFilter

import build_protagonist_mvp_from_sheet as builder


ROOT = Path(__file__).resolve().parents[1]
FRAME_DIR = ROOT / "sprites" / "characters" / "protagonist" / "frames"
FINAL_STRIP_DIR = ROOT / "production" / "assets" / "protagonist" / "final_source_strips"
PREVIEW = ROOT / ".codex" / "protagonist_final_asset_batch_preview.png"

FRAME_SIZE = (192, 288)
SOURCE_SLOT_SIZE = (384, 576)
FOOT_BASELINE_Y = 270

DIRECTIONS = [
    "down",
    "down_left",
    "left",
    "up_left",
    "up",
    "up_right",
    "right",
    "down_right",
]

WALK_DIRECTIONS = DIRECTIONS
IDLE_DIRECTIONS = DIRECTIONS
INTERACT_DIRECTIONS = DIRECTIONS
SIT_ANIMS = ["player_sit_down_side", "player_sit_idle_side", "player_stand_up_side"]

LINE = (65, 50, 36, 185)
BLOUSE = (245, 222, 198, 230)
BLOUSE_SHADE = (214, 176, 145, 140)
SKIRT = (78, 122, 128, 230)
SKIRT_DARK = (43, 80, 87, 210)
SKIRT_LIGHT = (119, 158, 158, 110)
HAIR = (55, 43, 36, 230)
HAIR_LIGHT = (100, 78, 60, 130)
SKIN = (230, 184, 145, 230)
SANDAL = (87, 62, 39, 230)


@dataclass(frozen=True)
class AnimSpec:
    name: str
    frame_count: int


def strict_frame_paths(animation: str, frame_count: int) -> list[Path]:
    pattern = re.compile(rf"^{re.escape(animation)}_(\d{{2}})\.png$")
    indexed: list[tuple[int, Path]] = []
    for path in FRAME_DIR.glob(f"{animation}_*.png"):
        match = pattern.match(path.name)
        if match is not None:
            indexed.append((int(match.group(1)), path))
    indexed.sort(key=lambda item: item[0])
    if [idx for idx, _path in indexed] != list(range(frame_count)):
        raise SystemExit(f"FAIL: missing or non-contiguous frames for {animation}")
    return [path for _idx, path in indexed]


def load_row(animation: str, frame_count: int) -> list[Image.Image]:
    return [Image.open(path).convert("RGBA") for path in strict_frame_paths(animation, frame_count)]


def alpha_bottom_y(frame: Image.Image) -> int:
    alpha = frame.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return FRAME_SIZE[1] - 1
    return bbox[3] - 1


def align_baseline(frame: Image.Image) -> Image.Image:
    bottom = alpha_bottom_y(frame)
    dy = FOOT_BASELINE_Y - bottom
    if dy == 0:
        return frame
    out = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    out.alpha_composite(frame, (0, dy))
    return out


def harden_alpha(frame: Image.Image, floor: int = 18) -> Image.Image:
    image = frame.convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if 0 < a < floor:
                pixels[x, y] = (0, 0, 0, 0)
    return image


def ellipse(draw: ImageDraw.ImageDraw, cx: float, cy: float, rx: float, ry: float, fill, outline=None, width: int = 1) -> None:
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill, outline=outline, width=width)


def soften(frame: Image.Image) -> Image.Image:
    return frame.filter(ImageFilter.UnsharpMask(radius=0.7, percent=80, threshold=3))


def add_cardinal_walk_grounding(frame: Image.Image, direction: str, idx: int) -> Image.Image:
    image = harden_alpha(frame)
    draw = ImageDraw.Draw(image, "RGBA")
    step = [0, 3, 6, 2, 0, 3, 6, 2][idx]
    phase = -1 if idx < 4 else 1
    center_x = 96
    if direction == "down":
        near_x = center_x - phase * (8 + step * 0.5)
        far_x = center_x + phase * (7 + step * 0.35)
        knee_y = 246 - step * 0.35
        near_y = FOOT_BASELINE_Y - min(2, step // 3)
        far_y = FOOT_BASELINE_Y - max(0, step - 2)
        draw.line((far_x, 243, far_x + phase * 5, far_y - 3), fill=(188, 142, 103, 165), width=5)
        draw.line((near_x, knee_y, near_x - phase * 3, near_y - 2), fill=SKIN, width=6)
        ellipse(draw, near_x - phase * 7, FOOT_BASELINE_Y - 2, 12, 3.5, SANDAL, LINE)
        ellipse(draw, far_x + phase * 4, min(FOOT_BASELINE_Y - 3, far_y - 2), 9, 3.0, SANDAL, LINE)
    elif direction == "up":
        near_x = center_x + phase * (7 + step * 0.35)
        far_x = center_x - phase * (8 + step * 0.4)
        near_y = FOOT_BASELINE_Y - min(2, step // 3)
        far_y = FOOT_BASELINE_Y - max(0, step - 2)
        draw.line((far_x, 245, far_x - phase * 4, far_y - 3), fill=(181, 134, 99, 165), width=5)
        draw.line((near_x, 246 - step * 0.3, near_x + phase * 3, near_y - 2), fill=(218, 171, 132, 205), width=5)
        ellipse(draw, near_x + phase * 6, FOOT_BASELINE_Y - 2, 10, 3.2, SANDAL, LINE)
        ellipse(draw, far_x - phase * 4, min(FOOT_BASELINE_Y - 3, far_y - 2), 8, 2.8, SANDAL, LINE)
    else:
        return image

    for y in range(FOOT_BASELINE_Y + 1, image.height):
        for x in range(image.width):
            image.putpixel((x, y), (0, 0, 0, 0))
    return soften(image)


def paint_three_quarter(base: Image.Image, direction: str, idx: int) -> Image.Image:
    image = harden_alpha(base, floor=28)
    draw = ImageDraw.Draw(image, "RGBA")

    face_right = direction.endswith("right")
    upward = direction.startswith("up")
    sign = 1 if face_right else -1
    step = [0, 3, 7, 2, 0, 3, 7, 2][idx % 8]
    sway = [-2, -1, 1, 2, 2, 1, -1, -2][idx % 8]
    cx = 96 + sign * 2

    if upward:
        skirt_poly = [
            (cx - 25, 206),
            (cx + 23, 205),
            (cx + 31 + sign * sway, 248),
            (cx + 13, 262),
            (cx - 27 + sign * sway, 248),
        ]
        draw.line(skirt_poly + [skirt_poly[0]], fill=(43, 80, 87, 125), width=2)
        draw.arc((cx - 28, 93, cx + 18, 150), 195 if face_right else 165, 340 if face_right else 15, fill=(55, 43, 36, 105), width=3)
        draw.line((cx - 18, 186, cx + 17, 188), fill=(214, 176, 145, 92), width=2)
        draw.line((cx - sign * 13, 170, cx - sign * 10, 204), fill=(214, 176, 145, 92), width=2)
        draw.line((cx + sign * 12, 170, cx + sign * 20, 205), fill=(245, 222, 198, 82), width=3)
    else:
        panel = [
            (cx - 18, 151),
            (cx + 18, 151),
            (cx + 17 + sign * 4, 203),
            (cx - 15 + sign * 3, 203),
        ]
        draw.line((cx - 13, 156, cx + 15, 199), fill=(214, 176, 145, 88), width=2)
        skirt_poly = [
            (cx - 25, 205),
            (cx + 25, 205),
            (cx + 35 + sign * sway, 250),
            (cx + 9, 263),
            (cx - 31 + sign * sway, 250),
        ]
        draw.line(skirt_poly + [skirt_poly[0]], fill=(43, 80, 87, 125), width=2)
        ellipse(draw, cx + sign * 14, 125, 1.7, 1.7, (44, 34, 30, 145), None)
        draw.arc((cx - 20, 103, cx + 23, 149), 185 if face_right else 355, 295 if face_right else 105, fill=(55, 43, 36, 96), width=3)

    near_x = cx + sign * (10 + step * 0.45)
    far_x = cx - sign * (8 + step * 0.35)
    near_lift = min(2, step // 4)
    far_lift = max(0, step - 2)
    draw.line((far_x, 244, far_x - sign * 5, FOOT_BASELINE_Y - far_lift - 2), fill=(177, 130, 96, 150), width=5)
    draw.line((near_x, 244, near_x + sign * 5, FOOT_BASELINE_Y - near_lift - 2), fill=SKIN, width=6)
    ellipse(draw, near_x + sign * 8, FOOT_BASELINE_Y - 2, 12, 3.4, SANDAL, LINE)
    ellipse(draw, far_x - sign * 5, min(FOOT_BASELINE_Y - 3, FOOT_BASELINE_Y - far_lift - 2), 8, 2.8, SANDAL, LINE)

    for y in range(FOOT_BASELINE_Y + 1, image.height):
        for x in range(image.width):
            image.putpixel((x, y), (0, 0, 0, 0))
    return soften(image)


def finalize_walk_rows(rows: dict[str, list[Image.Image]]) -> None:
    rows["player_walk_down"] = [align_baseline(add_cardinal_walk_grounding(frame, "down", idx)) for idx, frame in enumerate(rows["player_walk_down"])]
    rows["player_walk_up"] = [align_baseline(add_cardinal_walk_grounding(frame, "up", idx)) for idx, frame in enumerate(rows["player_walk_up"])]
    rows["player_walk_down_left"] = [align_baseline(paint_three_quarter(frame, "down_left", idx)) for idx, frame in enumerate(rows["player_walk_left"])]
    rows["player_walk_up_left"] = [align_baseline(paint_three_quarter(frame, "up_left", idx)) for idx, frame in enumerate(rows["player_walk_left"])]
    rows["player_walk_up_right"] = [align_baseline(paint_three_quarter(frame, "up_right", idx)) for idx, frame in enumerate(rows["player_walk_right"])]
    rows["player_walk_down_right"] = [align_baseline(paint_three_quarter(frame, "down_right", idx)) for idx, frame in enumerate(rows["player_walk_right"])]


def finalize_diagonal_state_rows(rows: dict[str, list[Image.Image]], state: str, frame_count: int) -> None:
    left = rows[f"player_{state}_left"]
    right = rows[f"player_{state}_right"]
    rows[f"player_{state}_down_left"] = [align_baseline(paint_three_quarter(frame, "down_left", idx)) for idx, frame in enumerate(left[:frame_count])]
    rows[f"player_{state}_up_left"] = [align_baseline(paint_three_quarter(frame, "up_left", idx)) for idx, frame in enumerate(left[:frame_count])]
    rows[f"player_{state}_up_right"] = [align_baseline(paint_three_quarter(frame, "up_right", idx)) for idx, frame in enumerate(right[:frame_count])]
    rows[f"player_{state}_down_right"] = [align_baseline(paint_three_quarter(frame, "down_right", idx)) for idx, frame in enumerate(right[:frame_count])]


def match_state_heights_to_walk(rows: dict[str, list[Image.Image]]) -> None:
    for direction in DIRECTIONS:
        target_height = builder.median_visible_height(rows[f"player_walk_{direction}"])
        for state in ("idle", "interact"):
            animation = f"player_{state}_{direction}"
            rows[animation] = builder.align_row_baseline(
                builder.match_row_height(rows[animation], target_height)
            )


def build_rows_from_current_frames() -> dict[str, list[Image.Image]]:
    rows: dict[str, list[Image.Image]] = {}
    for direction in WALK_DIRECTIONS:
        rows[f"player_walk_{direction}"] = load_row(f"player_walk_{direction}", 8)
    for direction in IDLE_DIRECTIONS:
        rows[f"player_idle_{direction}"] = load_row(f"player_idle_{direction}", 4)
    for direction in INTERACT_DIRECTIONS:
        rows[f"player_interact_{direction}"] = load_row(f"player_interact_{direction}", 6)
    for anim in SIT_ANIMS:
        rows[anim] = load_row(anim, 6)

    finalize_walk_rows(rows)
    finalize_diagonal_state_rows(rows, "idle", 4)
    finalize_diagonal_state_rows(rows, "interact", 6)
    match_state_heights_to_walk(rows)
    side_walk_height = (
        builder.median_visible_height(rows["player_walk_left"])
        + builder.median_visible_height(rows["player_walk_right"])
    ) / 2.0
    sit_idle_target = side_walk_height * 0.74
    rows["player_sit_idle_side"] = builder.align_row_baseline(
        builder.match_row_height(rows["player_sit_idle_side"], sit_idle_target)
    )
    rows["player_sit_down_side"] = [align_baseline(harden_alpha(frame)) for frame in rows["player_sit_down_side"]]
    rows["player_sit_idle_side"] = [align_baseline(harden_alpha(frame)) for frame in rows["player_sit_idle_side"]]
    rows["player_stand_up_side"] = [align_baseline(harden_alpha(frame)) for frame in rows["player_stand_up_side"]]
    return rows


def write_source_strip(animation: str, frames: list[Image.Image]) -> Path:
    strip = Image.new("RGBA", (SOURCE_SLOT_SIZE[0] * len(frames), SOURCE_SLOT_SIZE[1]), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        source_frame = frame.resize(SOURCE_SLOT_SIZE, Image.Resampling.LANCZOS)
        strip.alpha_composite(source_frame, (idx * SOURCE_SLOT_SIZE[0], 0))
    FINAL_STRIP_DIR.mkdir(parents=True, exist_ok=True)
    out = FINAL_STRIP_DIR / f"{animation}_source_strip.png"
    strip.save(out)
    return out


def write_all_source_strips(rows: dict[str, list[Image.Image]]) -> None:
    for animation, frames in rows.items():
        write_source_strip(animation, frames)


def write_preview(rows: dict[str, list[Image.Image]]) -> None:
    preview_rows = [
        "player_walk_down",
        "player_walk_down_left",
        "player_walk_left",
        "player_walk_up_left",
        "player_walk_up",
        "player_walk_up_right",
        "player_walk_right",
        "player_walk_down_right",
        "player_idle_down_left",
        "player_interact_up_right",
        "player_sit_idle_side",
    ]
    label_w = 210
    cols = 8
    canvas = Image.new("RGBA", (label_w + FRAME_SIZE[0] * cols, FRAME_SIZE[1] * len(preview_rows)), (244, 239, 226, 255))
    draw = ImageDraw.Draw(canvas)
    for row_idx, animation in enumerate(preview_rows):
        y = row_idx * FRAME_SIZE[1]
        draw.text((8, y + 12), animation, fill=(38, 35, 30, 255))
        for idx, frame in enumerate(rows[animation]):
            canvas.alpha_composite(frame, (label_w + idx * FRAME_SIZE[0], y))
            draw.rectangle(
                (label_w + idx * FRAME_SIZE[0], y, label_w + (idx + 1) * FRAME_SIZE[0] - 1, y + FRAME_SIZE[1] - 1),
                outline=(190, 180, 160, 160),
            )
            draw.line(
                (label_w + idx * FRAME_SIZE[0], y + FOOT_BASELINE_Y, label_w + (idx + 1) * FRAME_SIZE[0], y + FOOT_BASELINE_Y),
                fill=(210, 90, 70, 120),
            )
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(PREVIEW)


def main() -> None:
    rows = build_rows_from_current_frames()
    write_all_source_strips(rows)
    write_preview(rows)
    builder.main()
    print(f"OK: wrote final source strips -> {FINAL_STRIP_DIR}")
    print(f"OK: wrote final batch preview -> {PREVIEW}")


if __name__ == "__main__":
    main()
