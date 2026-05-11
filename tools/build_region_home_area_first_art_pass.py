from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "sprites" / "environments" / "regions" / "home_area"

ASSETS = [
    {
        "name": "region_home_area_ground_grass_yard_v001",
        "kind": "ground",
        "dir": "ground",
        "origin": (1440, 1320),
        "size": (3580, 1800),
        "polygon": [(1440, 1320), (4630, 1320), (5020, 2650), (4140, 3120), (2140, 3020), (1480, 2380)],
        "base": (126, 170, 109),
        "variation": (34, 52, 28),
    },
    {
        "name": "region_home_area_path_front_yard_v001",
        "kind": "path",
        "dir": "path",
        "origin": (2060, 1600),
        "size": (2200, 980),
        "polygon": [(2240, 1600), (3920, 1620), (4260, 2100), (3680, 2580), (2650, 2580), (2060, 2200)],
        "base": (156, 139, 105),
        "variation": (46, 39, 27),
    },
    {
        "name": "region_home_area_foreground_front_grass_left_v001",
        "kind": "foreground_grass",
        "dir": "foreground",
        "origin": (420, 2460),
        "size": (1500, 620),
        "polygon": [(0, 260), (1100, 120), (1500, 620), (0, 620)],
        "base": (56, 112, 53),
        "variation": (26, 42, 22),
    },
]


def clamp_channel(value: int) -> int:
    return max(0, min(255, value))


def build_mask(size: tuple[int, int], origin: tuple[int, int], polygon: list[tuple[int, int]]) -> Image.Image:
    mask = Image.new("L", size, 0)
    local_polygon = [(x - origin[0], y - origin[1]) for x, y in polygon]
    ImageDraw.Draw(mask).polygon(local_polygon, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(0.4))


def build_texture(asset: dict) -> Image.Image:
    width, height = asset["size"]
    if asset["kind"] == "foreground_grass":
        rgba = Image.new("RGBA", asset["size"], (0, 0, 0, 0))
        draw = ImageDraw.Draw(rgba, "RGBA")
        rng = random.Random(asset["name"])
        for _ in range(760):
            x = rng.randrange(width)
            base_y = rng.randrange(220, height)
            length = rng.randrange(22, 120)
            bend = rng.randrange(-26, 28)
            color = rng.choice(((43, 91, 43, 150), (74, 132, 62, 135), (101, 148, 75, 120)))
            draw.line((x, base_y, x + bend, max(0, base_y - length)), fill=color, width=rng.choice((1, 1, 2)))
        for _ in range(95):
            x = rng.randrange(width)
            y = rng.randrange(270, height)
            r = rng.randrange(2, 5)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(228, 210, 146, 120))
        mask = Image.new("L", asset["size"], 0)
        ImageDraw.Draw(mask).polygon(asset["polygon"], fill=255)
        rgba.putalpha(ImageChops.multiply(rgba.getchannel("A"), mask.filter(ImageFilter.GaussianBlur(0.4))))
        return rgba

    mask = build_mask(asset["size"], asset["origin"], asset["polygon"])
    noise = Image.effect_noise(asset["size"], 58).convert("L")
    fine_noise = Image.effect_noise(asset["size"], 18).convert("L")
    noise = ImageChops.add(noise, fine_noise, scale=2.0)

    base = asset["base"]
    variation = asset["variation"]
    rgb = Image.new("RGB", asset["size"], base)
    pixels = rgb.load()
    noise_pixels = noise.load()
    for y in range(height):
        for x in range(width):
            n = noise_pixels[x, y] - 128
            pixels[x, y] = (
                clamp_channel(base[0] + int(n * variation[0] / 128)),
                clamp_channel(base[1] + int(n * variation[1] / 128)),
                clamp_channel(base[2] + int(n * variation[2] / 128)),
            )

    draw = ImageDraw.Draw(rgb, "RGBA")
    rng = random.Random(asset["name"])
    if asset["kind"] == "ground":
        for _ in range(640):
            x = rng.randrange(width)
            y = rng.randrange(height)
            length = rng.randrange(8, 28)
            color = rng.choice(((73, 122, 68, 70), (161, 186, 118, 55), (92, 145, 82, 60)))
            draw.line((x, y, x + rng.randrange(-6, 8), y - length), fill=color, width=1)
        for _ in range(100):
            x = rng.randrange(width)
            y = rng.randrange(height)
            r = rng.randrange(2, 5)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(239, 216, 151, 55))
    else:
        for _ in range(360):
            x = rng.randrange(width)
            y = rng.randrange(height)
            rx = rng.randrange(8, 26)
            ry = rng.randrange(3, 10)
            color = rng.choice(((121, 104, 82, 65), (191, 172, 132, 48), (91, 82, 70, 45)))
            draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=color)
        for _ in range(50):
            x = rng.randrange(width)
            y = rng.randrange(height)
            draw.line((x, y, x + rng.randrange(18, 70), y + rng.randrange(-10, 12)), fill=(92, 79, 62, 38), width=1)

    rgba = rgb.convert("RGBA")
    rgba.putalpha(mask)
    return rgba


def main() -> None:
    manifest = []
    for asset in ASSETS:
        target_dir = ASSET_ROOT / asset["dir"]
        target_dir.mkdir(parents=True, exist_ok=True)
        output = target_dir / f'{asset["name"]}.png'
        build_texture(asset).save(output)
        manifest.append(
            {
                "file": output.relative_to(ROOT).as_posix(),
                "origin_x": asset["origin"][0],
                "origin_y": asset["origin"][1],
                "width": asset["size"][0],
                "height": asset["size"][1],
                "anchor": "top_left_source_space",
            }
        )

    manifest_path = ASSET_ROOT / "region_home_area_first_art_pass_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"OK: generated {len(manifest)} HomeArea art-pass PNG modules")


if __name__ == "__main__":
    main()
