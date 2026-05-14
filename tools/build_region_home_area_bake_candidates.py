from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "production" / "assets" / "regions" / "home_area_bake" / "region_home_area_bake_contract.json"
OUT_DIR = ROOT / "production" / "assets" / "regions" / "home_area_bake" / "candidates" / "v001"
MANIFEST = OUT_DIR / "region_home_area_bake_candidate_manifest.json"
PREVIEW = OUT_DIR / "region_home_area_bake_candidate_preview.png"

LAYER_SIZES = {
    "ground_grass_yard": (3580, 1800),
    "path_front_yard": (2200, 980),
    "structure_cloud_house_back": (1700, 920),
    "structure_cloud_house_roof_occluder": (1700, 260),
    "tree_left_trunk": (300, 560),
    "tree_left_canopy_occluder": (980, 760),
    "tree_right_trunk": (300, 640),
    "tree_right_canopy_occluder": (1080, 820),
    "foreground_front_grass_left": (1500, 620),
    "fx_dappled_light": (1780, 870),
}


def clamp(value: int) -> int:
    return max(0, min(255, value))


def textured_patch(size: tuple[int, int], base: tuple[int, int, int], variation: tuple[int, int, int], alpha: Image.Image) -> Image.Image:
    width, height = size
    noise = Image.effect_noise(size, 48).convert("L")
    fine = Image.effect_noise(size, 16).convert("L")
    noise = ImageChops.add(noise, fine, scale=2.0)
    rgb = Image.new("RGB", size, base)
    pixels = rgb.load()
    noise_pixels = noise.load()
    for y in range(height):
        for x in range(width):
            n = noise_pixels[x, y] - 128
            pixels[x, y] = (
                clamp(base[0] + int(n * variation[0] / 128)),
                clamp(base[1] + int(n * variation[1] / 128)),
                clamp(base[2] + int(n * variation[2] / 128)),
            )
    rgba = rgb.convert("RGBA")
    rgba.putalpha(alpha)
    return rgba


def polygon_alpha(size: tuple[int, int], polygon: list[tuple[int, int]], blur: float = 0.8) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(polygon, fill=255)
    if blur:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def build_ground(size: tuple[int, int], seed: str) -> Image.Image:
    rng = random.Random(seed)
    alpha = polygon_alpha(size, [(40, 70), (size[0] - 150, 0), (size[0], size[1] - 260), (size[0] - 860, size[1]), (180, size[1] - 120), (0, 730)])
    image = textured_patch(size, (119, 164, 103), (35, 48, 26), alpha)
    draw = ImageDraw.Draw(image, "RGBA")
    for _ in range(1450):
        x = rng.randrange(size[0])
        y = rng.randrange(size[1])
        length = rng.randrange(7, 30)
        bend = rng.randrange(-8, 9)
        color = rng.choice(((70, 122, 68, 72), (151, 184, 112, 58), (84, 142, 78, 64), (197, 188, 113, 28)))
        draw.line((x, y, x + bend, y - length), fill=color, width=1)
    for _ in range(190):
        x = rng.randrange(size[0])
        y = rng.randrange(size[1])
        radius = rng.randrange(2, 5)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(238, 219, 154, 58))
    return image


def build_path(size: tuple[int, int], seed: str) -> Image.Image:
    rng = random.Random(seed)
    alpha = polygon_alpha(size, [(180, 40), (1780, 60), (size[0], 470), (1600, size[1] - 30), (520, size[1] - 20), (0, 560)])
    image = textured_patch(size, (154, 138, 105), (48, 40, 28), alpha)
    draw = ImageDraw.Draw(image, "RGBA")
    for _ in range(520):
        x = rng.randrange(size[0])
        y = rng.randrange(size[1])
        rx = rng.randrange(10, 34)
        ry = rng.randrange(4, 13)
        color = rng.choice(((110, 94, 73, 58), (193, 176, 137, 46), (90, 82, 70, 42)))
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=color)
    for _ in range(72):
        x = rng.randrange(size[0])
        y = rng.randrange(size[1])
        draw.line((x, y, x + rng.randrange(25, 90), y + rng.randrange(-14, 15)), fill=(83, 71, 56, 38), width=1)
    return image


def build_house_body(size: tuple[int, int], seed: str) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    body = [(130, 260), (1570, 240), (1510, 830), (180, 860)]
    draw.polygon(body, fill=(178, 142, 94, 255))
    for i in range(20):
        y = 290 + i * 24
        draw.line((180, y, 1510, y + rng.randrange(-5, 6)), fill=(132, 96, 61, 38), width=2)
    for x in range(250, 1480, 120):
        draw.line((x, 260, x - 30, 845), fill=(112, 78, 48, 42), width=3)
    draw.rectangle((745, 520, 955, 845), fill=(68, 48, 34, 235))
    draw.rectangle((300, 430, 560, 630), fill=(72, 90, 90, 150))
    draw.rectangle((1130, 420, 1390, 620), fill=(72, 90, 90, 145))
    for x in (295, 565, 1125, 1395):
        draw.line((x, 415, x, 645), fill=(84, 58, 36, 180), width=8)
    for y in (415, 645):
        draw.line((290, y, 565, y), fill=(84, 58, 36, 180), width=8)
        draw.line((1120, y, 1400, y), fill=(84, 58, 36, 180), width=8)
    shade = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(shade, "RGBA").polygon([(170, 670), (1540, 625), (1510, 850), (190, 870)], fill=(53, 38, 25, 52))
    image.alpha_composite(shade)
    return image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70, threshold=3))


def build_roof(size: tuple[int, int], seed: str) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    roof = [(45, 130), (390, 35), (1300, 34), (1655, 132), (1510, 230), (190, 236)]
    draw.polygon(roof, fill=(62, 70, 68, 255))
    for x in range(120, 1580, 54):
        color = rng.choice(((39, 47, 47, 80), (91, 98, 91, 52)))
        draw.line((x, 90, x + rng.randrange(-28, 28), 225), fill=color, width=3)
    draw.line((80, 132, 1625, 132), fill=(34, 39, 38, 110), width=8)
    draw.line((190, 236, 1510, 230), fill=(40, 31, 23, 170), width=13)
    return image


def build_trunk(size: tuple[int, int], seed: str) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    cx = size[0] // 2
    trunk = [(cx - 58, size[1] - 20), (cx - 34, 120), (cx + 34, 120), (cx + 62, size[1] - 20)]
    draw.polygon(trunk, fill=(87, 54, 31, 255))
    for _ in range(18):
        x = cx + rng.randrange(-42, 42)
        draw.line((x, 145, x + rng.randrange(-18, 22), size[1] - 34), fill=(51, 32, 22, 86), width=rng.randrange(2, 5))
    draw.polygon([(cx - 40, 240), (cx - 160, 150), (cx - 140, 112), (cx - 25, 220)], fill=(78, 48, 28, 230))
    draw.polygon([(cx + 38, 280), (cx + 168, 180), (cx + 150, 138), (cx + 25, 250)], fill=(76, 46, 27, 225))
    draw.ellipse((cx - 76, size[1] - 58, cx + 78, size[1] - 4), fill=(48, 38, 25, 82))
    return image


def build_canopy(size: tuple[int, int], seed: str) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    clusters = [
        (size[0] * 0.28, size[1] * 0.42, size[0] * 0.28, size[1] * 0.22),
        (size[0] * 0.50, size[1] * 0.32, size[0] * 0.33, size[1] * 0.25),
        (size[0] * 0.70, size[1] * 0.46, size[0] * 0.30, size[1] * 0.24),
        (size[0] * 0.50, size[1] * 0.58, size[0] * 0.42, size[1] * 0.26),
    ]
    for cx, cy, rx, ry in clusters:
        color = rng.choice(((45, 91, 49, 232), (56, 111, 55, 228), (73, 127, 65, 222)))
        draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=color)
    for _ in range(780):
        x = rng.randrange(size[0])
        y = rng.randrange(size[1])
        if image.getpixel((x, y))[3] == 0:
            continue
        r = rng.randrange(3, 9)
        color = rng.choice(((27, 66, 35, 52), (105, 151, 77, 62), (167, 156, 72, 32)))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
    image = image.filter(ImageFilter.GaussianBlur(0.35))
    return image


def build_grass_foreground(size: tuple[int, int], seed: str) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    alpha = polygon_alpha(size, [(0, 300), (1080, 125), (1500, 620), (0, 620)], blur=0.6)
    for _ in range(1180):
        x = rng.randrange(size[0])
        base_y = rng.randrange(210, size[1])
        length = rng.randrange(28, 145)
        bend = rng.randrange(-30, 31)
        color = rng.choice(((39, 91, 42, 160), (76, 132, 61, 145), (119, 158, 76, 118)))
        draw.line((x, base_y, x + bend, max(0, base_y - length)), fill=color, width=rng.choice((1, 1, 2)))
    for _ in range(120):
        x = rng.randrange(size[0])
        y = rng.randrange(300, size[1])
        r = rng.randrange(2, 5)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(233, 212, 143, 128))
    image.putalpha(ImageChops.multiply(image.getchannel("A"), alpha))
    return image


def build_light(size: tuple[int, int], seed: str) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    for _ in range(36):
        x = rng.randrange(-80, size[0] - 80)
        y = rng.randrange(-50, size[1] - 70)
        rx = rng.randrange(90, 260)
        ry = rng.randrange(22, 78)
        angle = rng.random() * math.pi
        points = []
        for i in range(18):
            t = 2 * math.pi * i / 18
            px = math.cos(t) * rx
            py = math.sin(t) * ry
            points.append((x + px * math.cos(angle) - py * math.sin(angle), y + px * math.sin(angle) + py * math.cos(angle)))
        draw.polygon(points, fill=(255, 229, 135, rng.randrange(18, 44)))
    return image.filter(ImageFilter.GaussianBlur(8))


BUILDERS = {
    "ground_grass_yard": build_ground,
    "path_front_yard": build_path,
    "structure_cloud_house_back": build_house_body,
    "structure_cloud_house_roof_occluder": build_roof,
    "tree_left_trunk": build_trunk,
    "tree_left_canopy_occluder": build_canopy,
    "tree_right_trunk": build_trunk,
    "tree_right_canopy_occluder": build_canopy,
    "foreground_front_grass_left": build_grass_foreground,
    "fx_dappled_light": build_light,
}


def paste_layer(canvas: Image.Image, layer: Image.Image, origin: dict[str, int], scale: float) -> None:
    resized = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.Resampling.LANCZOS)
    canvas.alpha_composite(resized, (int(origin["x"] * scale), int(origin["y"] * scale)))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    manifest_layers: list[dict[str, Any]] = []
    generated: dict[str, Image.Image] = {}

    for layer in contract["export_layers"]:
        layer_id = layer["id"]
        builder = BUILDERS[layer_id]
        size = LAYER_SIZES[layer_id]
        image = builder(size, layer_id)
        output = OUT_DIR / layer["export_name"]
        image.save(output)
        generated[layer_id] = image
        manifest_layers.append(
            {
                "id": layer_id,
                "file": layer["export_name"],
                "origin_px": layer["origin_px"],
                "size_px": {"width": image.width, "height": image.height},
                "target_parent": layer["target_parent"],
                "anchor": layer["anchor"],
                "source": "procedural_candidate_from_home_area_bake_contract_v001",
            }
        )

    preview = Image.new("RGBA", (1536, 1024), (98, 134, 86, 255))
    scale = 0.25
    for layer in contract["export_layers"]:
        paste_layer(preview, generated[layer["id"]], layer["origin_px"], scale)
    preview.save(PREVIEW)

    manifest = {
        "region_id": contract["region_id"],
        "candidate_id": "home_area_bake_v001",
        "contract": CONTRACT.relative_to(ROOT).as_posix(),
        "layers": manifest_layers,
        "preview": PREVIEW.name,
        "runtime_replacement": False,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"OK: generated {len(manifest_layers)} Region_HomeArea bake candidate layers")


if __name__ == "__main__":
    main()
