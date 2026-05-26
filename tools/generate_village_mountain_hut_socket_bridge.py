from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "art" / "greenfield_p0" / "world" / "socket_bridges" / "village_mountain_hut_socket_bridge.png"
RNG = random.Random(260526)
CANVAS = (72, 112)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ground = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    pixels = ground.load()
    for y in range(CANVAS[1]):
        for x in range(CANVAS[0]):
            edge_fade = min(x / 8.0, (CANVAS[0] - 1 - x) / 8.0, y / 14.0, (CANVAS[1] - 1 - y) / 14.0, 1.0)
            if edge_fade <= 0.0:
                continue
            noise = RNG.randint(-10, 10)
            pixels[x, y] = (
                112 + noise,
                134 + noise // 2,
                78 + noise // 3,
                int(180 * edge_fade),
            )
    image.alpha_composite(ground)

    road = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(road)
    center_y = 56
    shoulder_points = []
    body_points = []
    for x in range(-8, CANVAS[0] + 9, 6):
        waviness = RNG.randint(-4, 4)
        shoulder_points.append((x, center_y + waviness))
        body_points.append((x, center_y + waviness // 2))
    draw.line(shoulder_points, fill=(122, 104, 67, 150), width=58, joint="curve")
    draw.line(body_points, fill=(188, 162, 100, 225), width=38, joint="curve")
    draw.line(body_points, fill=(226, 203, 142, 80), width=12, joint="curve")
    road = road.filter(ImageFilter.GaussianBlur(radius=1.15))
    image.alpha_composite(road)

    detail = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    detail_draw = ImageDraw.Draw(detail)
    for _ in range(140):
        x = RNG.randrange(CANVAS[0])
        y = RNG.randrange(CANVAS[1])
        radius = RNG.choice([1, 1, 2])
        color = RNG.choice(
            [
                (87, 112, 62, 80),
                (216, 197, 126, 75),
                (151, 126, 78, 70),
                (230, 190, 170, 45),
            ]
        )
        detail_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    image.alpha_composite(detail.filter(ImageFilter.GaussianBlur(radius=0.25)))
    image.save(OUTPUT)
    print(f"OK: generated {OUTPUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
