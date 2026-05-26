from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "art" / "greenfield_p0" / "world" / "socket_bridges" / "village_mountain_hut_socket_bridge.png"
RNG = random.Random(260526)
CANVAS = (72, 240)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ground = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    pixels = ground.load()
    seam_center_x = 36.0
    for y in range(CANVAS[1]):
        for x in range(CANVAS[0]):
            edge_fade = min(x / 18.0, (CANVAS[0] - 1 - x) / 18.0, y / 18.0, (CANVAS[1] - 1 - y) / 18.0, 1.0)
            seam_fade = max(0.0, 1.0 - abs(x - seam_center_x) / 36.0)
            if edge_fade <= 0.0:
                continue
            blend = x / float(CANVAS[0] - 1)
            noise = RNG.randint(-10, 10)
            pixels[x, y] = (
                int((126 * (1.0 - blend)) + (67 * blend)) + noise,
                int((151 * (1.0 - blend)) + (91 * blend)) + noise // 2,
                int((88 * (1.0 - blend)) + (54 * blend)) + noise // 3,
                int(82 * edge_fade * seam_fade * seam_fade),
            )
    image.alpha_composite(ground)

    road = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(road)
    center_y = 122
    shoulder_points = []
    body_points = []
    for x in range(-12, CANVAS[0] + 13, 7):
        slope = int((x / max(CANVAS[0], 1) - 0.5) * 10)
        waviness = RNG.randint(-5, 5) + slope
        shoulder_points.append((x, center_y + waviness))
        body_points.append((x, center_y + waviness // 2))
    draw.line(shoulder_points, fill=(78, 84, 49, 95), width=44, joint="curve")
    draw.line(body_points, fill=(158, 131, 81, 180), width=28, joint="curve")
    draw.line(body_points, fill=(222, 197, 129, 70), width=12, joint="curve")
    road = road.filter(ImageFilter.GaussianBlur(radius=1.15))
    image.alpha_composite(road)

    detail = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    detail_draw = ImageDraw.Draw(detail)
    for _ in range(260):
        x = RNG.randrange(CANVAS[0])
        y = RNG.randrange(CANVAS[1])
        radius = RNG.choice([1, 1, 2])
        color = RNG.choice(
            [
                (47, 75, 45, 95),
                (92, 115, 55, 85),
                (216, 197, 126, 70),
                (151, 126, 78, 75),
                (230, 190, 170, 50),
            ]
        )
        distance_fade = max(0.0, 1.0 - abs(x - seam_center_x) / 42.0)
        softened_color = (color[0], color[1], color[2], int(color[3] * distance_fade))
        detail_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=softened_color)
    for _ in range(18):
        x = RNG.choice([RNG.randrange(8, 28), RNG.randrange(44, CANVAS[0] - 8)])
        y = RNG.randrange(6, CANVAS[1] - 6)
        radius = RNG.randrange(5, 13)
        color = RNG.choice([(45, 73, 43, 55), (70, 96, 46, 48), (104, 116, 48, 42)])
        detail_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    image.alpha_composite(detail.filter(ImageFilter.GaussianBlur(radius=0.25)))
    image.save(OUTPUT)
    print(f"OK: generated {OUTPUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
