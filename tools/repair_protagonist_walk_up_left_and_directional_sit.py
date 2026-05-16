from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
FRAME_DIR = ROOT / "sprites" / "characters" / "protagonist" / "frames"
FINAL_STRIP_DIR = ROOT / "production" / "assets" / "protagonist" / "final_source_strips"

FRAME_SIZE = (192, 288)
SOURCE_SLOT_SIZE = (384, 576)
FOOT_BASELINE_Y = 270

LINE = (65, 50, 36, 185)
SKIN = (230, 184, 145, 230)
SKIN_SHADE = (185, 132, 96, 170)
SANDAL = (87, 62, 39, 230)
SKIRT = (78, 122, 128, 210)
SKIRT_DARK = (43, 80, 87, 190)
HAIR = (55, 43, 36, 170)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_runtime(animation: str, frame: int) -> Image.Image:
    path = FRAME_DIR / f"{animation}_{frame:02d}.png"
    if not path.exists():
        fail(f"missing runtime frame: {path}")
    return Image.open(path).convert("RGBA")


def alpha_bounds(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = np.array(image.convert("RGBA"))[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        fail("empty alpha mask")
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def align_baseline(image: Image.Image) -> Image.Image:
    _x1, _y1, _x2, y2 = alpha_bounds(image)
    dy = FOOT_BASELINE_Y - y2
    out = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    out.alpha_composite(image, (0, dy))
    pixels = out.load()
    for y in range(FOOT_BASELINE_Y + 1, FRAME_SIZE[1]):
        for x in range(FRAME_SIZE[0]):
            pixels[x, y] = (0, 0, 0, 0)
    return out


def harden_alpha(frame: Image.Image, floor: int = 22) -> Image.Image:
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


def synthesize_up_left_frame_07() -> Image.Image:
    base = harden_alpha(load_runtime("player_walk_left", 7))
    image = base.copy()
    draw = ImageDraw.Draw(image, "RGBA")
    cx = 94
    sign = -1
    step = 4

    skirt_poly = [
        (cx - 24, 205),
        (cx + 23, 204),
        (cx + 29, 248),
        (cx + 10, 262),
        (cx - 27, 248),
    ]
    draw.line(skirt_poly + [skirt_poly[0]], fill=SKIRT_DARK, width=2)
    draw.arc((cx - 29, 91, cx + 18, 151), 165, 20, fill=HAIR, width=3)
    draw.line((cx - 18, 186, cx + 16, 188), fill=(214, 176, 145, 96), width=2)
    draw.line((cx + 13, 171, cx + 21, 205), fill=(245, 222, 198, 86), width=3)

    near_x = cx + sign * (9 + step * 0.45)
    far_x = cx - sign * (7 + step * 0.35)
    draw.line((far_x, 244, far_x - sign * 5, FOOT_BASELINE_Y - 4), fill=SKIN_SHADE, width=5)
    draw.line((near_x, 244, near_x + sign * 5, FOOT_BASELINE_Y - 2), fill=SKIN, width=6)
    ellipse(draw, near_x + sign * 8, FOOT_BASELINE_Y - 2, 12, 3.4, SANDAL, LINE)
    ellipse(draw, far_x - sign * 6, FOOT_BASELINE_Y - 5, 8, 2.8, SANDAL, LINE)

    image = align_baseline(image)
    return image.filter(ImageFilter.UnsharpMask(radius=0.7, percent=80, threshold=3))


def replace_source_slot(animation: str, slot: int, runtime_frame: Image.Image) -> None:
    path = FINAL_STRIP_DIR / f"{animation}_source_strip.png"
    if not path.exists():
        fail(f"missing source strip: {path}")
    strip = Image.open(path).convert("RGBA")
    expected_size = (SOURCE_SLOT_SIZE[0] * 8, SOURCE_SLOT_SIZE[1])
    if strip.size != expected_size:
        fail(f"{path.name} must be {expected_size}, got {strip.size}")
    source_frame = runtime_frame.resize(SOURCE_SLOT_SIZE, Image.Resampling.LANCZOS)
    clear = Image.new("RGBA", SOURCE_SLOT_SIZE, (0, 0, 0, 0))
    strip.alpha_composite(clear, (slot * SOURCE_SLOT_SIZE[0], 0))
    strip.paste(clear, (slot * SOURCE_SLOT_SIZE[0], 0))
    strip.alpha_composite(source_frame, (slot * SOURCE_SLOT_SIZE[0], 0))
    strip.save(path)


def scale_to_height(frame: Image.Image, target_height: float, anchor_x: int = 96) -> Image.Image:
    x1, y1, x2, y2 = alpha_bounds(frame)
    crop = frame.crop((x1, y1, x2 + 1, y2 + 1))
    width = crop.width
    height = max(1, int(round(target_height)))
    scaled = crop.resize((width, height), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    x = int(anchor_x - width / 2)
    y = FOOT_BASELINE_Y - height + 1
    out.alpha_composite(scaled, (x, y))
    return out


def visible_height(frame: Image.Image) -> int:
    _x1, y1, _x2, y2 = alpha_bounds(frame)
    return y2 - y1 + 1


def draw_seated_details(frame: Image.Image, direction: str, idx: int) -> Image.Image:
    image = harden_alpha(frame, floor=18)
    draw = ImageDraw.Draw(image, "RGBA")
    sway = [0, 1, 1, 0, -1, -1][idx % 6]
    cx = 96 + sway

    if direction == "down":
        ellipse(draw, cx - 13, FOOT_BASELINE_Y - 5, 14, 3.4, SANDAL, LINE)
        ellipse(draw, cx + 13, FOOT_BASELINE_Y - 5, 14, 3.4, SANDAL, LINE)
        draw.line((cx - 19, 247, cx - 13, FOOT_BASELINE_Y - 7), fill=SKIN, width=5)
        draw.line((cx + 19, 247, cx + 13, FOOT_BASELINE_Y - 7), fill=SKIN, width=5)
        draw.arc((cx - 35, 218, cx + 35, 270), 8, 172, fill=SKIRT_DARK, width=3)
        draw.line((cx - 25, 239, cx + 26, 239), fill=(119, 158, 158, 105), width=2)
    else:
        ellipse(draw, cx - 12, FOOT_BASELINE_Y - 6, 11, 3.0, SANDAL, LINE)
        ellipse(draw, cx + 12, FOOT_BASELINE_Y - 6, 11, 3.0, SANDAL, LINE)
        draw.line((cx - 16, 248, cx - 12, FOOT_BASELINE_Y - 8), fill=SKIN_SHADE, width=4)
        draw.line((cx + 16, 248, cx + 12, FOOT_BASELINE_Y - 8), fill=SKIN_SHADE, width=4)
        draw.arc((cx - 32, 216, cx + 32, 270), 15, 165, fill=SKIRT_DARK, width=3)
        draw.arc((cx - 24, 92, cx + 24, 145), 185, 355, fill=HAIR, width=4)

    return image.filter(ImageFilter.UnsharpMask(radius=0.7, percent=70, threshold=3))


def make_directional_sit_frames(direction: str, action: str) -> list[Image.Image]:
    base_anim = "player_idle_down" if direction == "down" else "player_idle_up"
    walk = [load_runtime(f"player_walk_{direction}", idx) for idx in range(8)]
    standing_height = float(np.median([visible_height(frame) for frame in walk]))
    seated_height = standing_height * 0.72
    idle_frames = [load_runtime(base_anim, idx % 4) for idx in range(6)]

    if action == "sit_down":
        ratios = [1.00, 0.94, 0.87, 0.80, 0.75, 0.72]
    elif action == "stand_up":
        ratios = [0.72, 0.75, 0.80, 0.87, 0.94, 1.00]
    elif action == "sit_idle":
        ratios = [0.72, 0.71, 0.72, 0.73, 0.72, 0.71]
    else:
        fail(f"unknown sit action: {action}")

    frames: list[Image.Image] = []
    for idx, ratio in enumerate(ratios):
        frame = scale_to_height(idle_frames[idx], standing_height * ratio)
        if ratio <= 0.80:
            frame = draw_seated_details(frame, direction, idx)
        frames.append(align_baseline(frame))
    return frames


def write_source_strip(animation: str, frames: list[Image.Image]) -> None:
    strip = Image.new("RGBA", (SOURCE_SLOT_SIZE[0] * len(frames), SOURCE_SLOT_SIZE[1]), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        source_frame = frame.resize(SOURCE_SLOT_SIZE, Image.Resampling.LANCZOS)
        strip.alpha_composite(source_frame, (idx * SOURCE_SLOT_SIZE[0], 0))
    FINAL_STRIP_DIR.mkdir(parents=True, exist_ok=True)
    strip.save(FINAL_STRIP_DIR / f"{animation}_source_strip.png")


def main() -> None:
    replace_source_slot("player_walk_up_left", 7, synthesize_up_left_frame_07())

    for direction in ("down", "up"):
        for action in ("sit_down", "sit_idle", "stand_up"):
            animation = f"player_{action}_{direction}"
            write_source_strip(animation, make_directional_sit_frames(direction, action))

    print("OK: repaired player_walk_up_left source slot 07")
    print("OK: wrote front/back sit source strips")


if __name__ == "__main__":
    main()
