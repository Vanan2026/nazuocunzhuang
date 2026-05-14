from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
FRAME_DIR = ROOT / "sprites" / "characters" / "protagonist" / "frames"
PREVIEW = ROOT / ".codex" / "protagonist_final_side_walk_preview.png"

FRAME_SIZE = (192, 288)
FOOT_BASELINE_Y = 270

SKIRT = (86, 125, 130, 255)
SKIRT_DARK = (55, 86, 91, 245)
SKIRT_LIGHT = (116, 151, 152, 220)
LEG = (223, 185, 143, 255)
LEG_SHADOW = (176, 132, 96, 230)
SANDAL = (93, 69, 45, 255)
SANDAL_LIGHT = (138, 105, 70, 230)
INK = (54, 45, 34, 190)


SIDE_POSES = [
    # rear_dx, front_dx, rear_lift, front_lift, hem_sway
    (-10, 8, 0, 0, -5),
    (-6, 11, 5, 0, -2),
    (1, 9, 9, 1, 1),
    (10, 4, 2, 0, 5),
    (10, -8, 0, 0, 5),
    (6, -11, 5, 0, 2),
    (-1, -9, 9, 1, -1),
    (-10, -4, 2, 0, -5),
]


def ellipse(draw: ImageDraw.ImageDraw, cx: float, cy: float, rx: float, ry: float, fill, outline=None, width: int = 1) -> None:
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill, outline=outline, width=width)


def line(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill, width: int) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def erase_lower_body(frame: Image.Image) -> Image.Image:
    image = frame.convert("RGBA")
    mask = Image.new("L", FRAME_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(
        [
            (45, 213),
            (147, 213),
            (154, FOOT_BASELINE_Y + 4),
            (38, FOOT_BASELINE_Y + 4),
        ],
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(1.1))
    blank = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    image = Image.composite(blank, image, mask)
    return image


def draw_side_walk_lower(frame: Image.Image, direction: str, idx: int) -> Image.Image:
    image = erase_lower_body(frame)
    draw = ImageDraw.Draw(image, "RGBA")
    rear_dx, front_dx, rear_lift, front_lift, hem_sway = SIDE_POSES[idx]

    if direction == "right":
        sign = 1
        face_bias = 3
    elif direction == "left":
        sign = -1
        face_bias = -3
    else:
        raise ValueError(direction)

    hip_x = 96 + face_bias
    waist_y = 204
    hem_y = 247
    base_y = FOOT_BASELINE_Y
    hem_width = [0, 5, -4, 8, 0, 5, -4, 8][idx]

    skirt_poly = [
        (hip_x - 24, waist_y),
        (hip_x + 22, waist_y + 1),
        (hip_x + 32 + hem_sway + hem_width, hem_y),
        (hip_x + 18 + hem_sway + hem_width * 0.45, hem_y + 7),
        (hip_x - 8 + hem_sway * 0.4, hem_y + 5),
        (hip_x - 30 + hem_sway - hem_width * 0.45, hem_y),
    ]
    draw.polygon(skirt_poly, fill=SKIRT)
    draw.line(skirt_poly + [skirt_poly[0]], fill=SKIRT_DARK, width=2)
    draw.polygon(
        [
            (hip_x - 16, waist_y + 8),
            (hip_x - 1, waist_y + 6),
            (hip_x + 5 + hem_sway, hem_y + 2),
            (hip_x - 10 + hem_sway, hem_y + 3),
        ],
        fill=SKIRT_LIGHT,
    )
    for fold_x in (-15, -2, 12):
        line(
            draw,
            [(hip_x + fold_x, waist_y + 8), (hip_x + fold_x * 0.7 + hem_sway, hem_y + 2)],
            SKIRT_DARK,
            1,
        )

    rear_ankle = (hip_x + sign * rear_dx, base_y - rear_lift)
    front_ankle = (hip_x + sign * front_dx, base_y - front_lift)
    rear_knee = (hip_x + sign * (rear_dx * 0.45 - 4), 244 - rear_lift * 0.45)
    front_knee = (hip_x + sign * (front_dx * 0.45 + 4), 244 - front_lift * 0.45)

    # Far leg first, partly hidden by the skirt.
    line(draw, [rear_knee, rear_ankle], LEG_SHADOW, 6)
    line(draw, [front_knee, front_ankle], LEG, 7)
    line(draw, [front_knee, front_ankle], (245, 211, 170, 110), 2)

    rear_foot_len = 10 if rear_lift > 2 else 13
    front_foot_len = 15 if front_lift < 2 else 11
    rear_foot_x = rear_ankle[0] + sign * 3
    front_foot_x = front_ankle[0] + sign * 5

    rear_foot_cy = min(FOOT_BASELINE_Y - 3.2, rear_ankle[1] - 1)
    front_foot_cy = min(FOOT_BASELINE_Y - 3.6, front_ankle[1] - 1)
    ellipse(draw, rear_foot_x + sign * 2, rear_foot_cy, rear_foot_len, 3.2, SANDAL, INK)
    ellipse(draw, front_foot_x + sign * 2, front_foot_cy, front_foot_len, 3.6, SANDAL, INK)
    line(draw, [(front_foot_x - sign * 4, front_ankle[1] - 1), (front_foot_x + sign * 8, front_ankle[1] + 1)], SANDAL_LIGHT, 2)
    line(draw, [(rear_foot_x - sign * 3, rear_ankle[1] - 1), (rear_foot_x + sign * 6, rear_ankle[1] + 1)], SANDAL_LIGHT, 1)

    # Ground contact pixel guard: keeps validation and runtime anchor stable.
    draw.rounded_rectangle(
        (front_foot_x + sign * 1 - 5, FOOT_BASELINE_Y - 2, front_foot_x + sign * 8 + 5, FOOT_BASELINE_Y),
        radius=2,
        fill=(80, 58, 38, 220),
    )
    if rear_lift <= 1:
        draw.rounded_rectangle(
            (rear_foot_x + sign * 1 - 4, FOOT_BASELINE_Y - 2, rear_foot_x + sign * 6 + 4, FOOT_BASELINE_Y),
            radius=2,
            fill=(80, 58, 38, 180),
        )

    image = image.filter(ImageFilter.UnsharpMask(radius=0.6, percent=70, threshold=3))
    pixels = image.load()
    for y in range(FOOT_BASELINE_Y + 1, FRAME_SIZE[1]):
        for x in range(FRAME_SIZE[0]):
            pixels[x, y] = (0, 0, 0, 0)
    return image


def write_preview() -> None:
    cell_w, cell_h = FRAME_SIZE
    label_w = 140
    canvas = Image.new("RGBA", (label_w + cell_w * 8, cell_h * 2), (244, 239, 226, 255))
    draw = ImageDraw.Draw(canvas)
    for row, anim in enumerate(("player_walk_left", "player_walk_right")):
        y = row * cell_h
        draw.text((10, y + 12), anim, fill=(35, 31, 26, 255))
        for idx in range(8):
            path = FRAME_DIR / f"{anim}_{idx:02d}.png"
            image = Image.open(path).convert("RGBA")
            canvas.alpha_composite(image, (label_w + idx * cell_w, y))
            draw.rectangle(
                (label_w + idx * cell_w, y, label_w + (idx + 1) * cell_w - 1, y + cell_h - 1),
                outline=(185, 175, 150, 170),
            )
            draw.line(
                (label_w + idx * cell_w, y + FOOT_BASELINE_Y, label_w + (idx + 1) * cell_w, y + FOOT_BASELINE_Y),
                fill=(210, 90, 70, 150),
            )
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(PREVIEW)


def main() -> None:
    for direction in ("left", "right"):
        for idx in range(8):
            path = FRAME_DIR / f"player_walk_{direction}_{idx:02d}.png"
            frame = Image.open(path).convert("RGBA")
            updated = draw_side_walk_lower(frame, direction, idx)
            updated.save(path)
    write_preview()
    print(f"OK: wrote final side-walk pass -> {FRAME_DIR}")
    print(f"OK: wrote preview -> {PREVIEW}")


if __name__ == "__main__":
    main()
