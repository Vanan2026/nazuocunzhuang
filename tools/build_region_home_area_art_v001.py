from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "production" / "assets" / "regions" / "home_area_design" / "region_home_area_layout_v001.json"
OUT_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v001"
MANIFEST = OUT_DIR / "region_home_area_art_v001_manifest.json"
PREVIEW = OUT_DIR / "region_home_area_art_v001_preview.png"
CONTACT = OUT_DIR / "region_home_area_art_v001_layer_contact_sheet.png"

CANVAS = (6144, 4096)
SEED = 20260514


@dataclass(frozen=True)
class LayerSpec:
    asset_id: str
    filename: str
    target_parent: str
    z_index: int
    anchor_px: tuple[int, int]
    role: str
    integration_note: str
    full_canvas: bool = False


LAYER_SPECS = [
    LayerSpec(
        "base_full",
        "region_home_area_base_full_v001.png",
        "art_review_only",
        0,
        (0, 0),
        "Full scene visual plate assembled from all v001 layers.",
        "Review only; do not wire this single plate as the playable scene.",
        True,
    ),
    LayerSpec(
        "ground_yard",
        "region_home_area_ground_yard_v001.png",
        "TileMapLayer_Ground",
        -100,
        (0, 0),
        "Central grass yard, west garden blending, and edge ground paint.",
        "Integrate before structures so walkable-zone readability can be checked first.",
    ),
    LayerSpec(
        "path_village_road",
        "region_home_area_path_village_road_v001.png",
        "TileMapLayer_Path",
        -90,
        (0, 0),
        "North village road with dirt, stone, and hedge-readable edges.",
        "Keep aligned with the future north Village exit and walkable corridor.",
    ),
    LayerSpec(
        "path_back_farm",
        "region_home_area_path_back_farm_v001.png",
        "TileMapLayer_Path",
        -89,
        (0, 0),
        "Southeast path that visually leads toward BackFarm.",
        "Keep the path clear around the existing BackFarm entrance target.",
    ),
    LayerSpec(
        "house_body",
        "region_home_area_house_body_v001.png",
        "YSortWorld/Houses",
        40,
        (3160, 1660),
        "Wooden home body, windows, door, and wall shadow.",
        "Y-sort by foot/base around the veranda edge.",
    ),
    LayerSpec(
        "house_roof_occluder",
        "region_home_area_house_roof_occluder_v001.png",
        "ForegroundStatic/Occluders",
        180,
        (3160, 1220),
        "Roof and eave occluder split from the house body.",
        "Can cover head and torso near the door but must not hide player feet.",
    ),
    LayerSpec(
        "veranda_floor",
        "region_home_area_veranda_floor_v001.png",
        "TileMapLayer_Detail",
        -30,
        (3160, 1720),
        "Low wooden veranda floor and step slab.",
        "Keep below the player; use house roof for upper-body occlusion.",
    ),
    LayerSpec(
        "tree_left_trunk",
        "region_home_area_tree_left_trunk_v001.png",
        "YSortWorld/Trees",
        55,
        (1420, 1220),
        "Left shade tree trunk, branches, and root shadow.",
        "Collision should stay near the lower trunk only.",
    ),
    LayerSpec(
        "tree_left_canopy_occluder",
        "region_home_area_tree_left_canopy_occluder_v001.png",
        "ForegroundStatic/Occluders",
        190,
        (1420, 760),
        "Left tree canopy with transparent leaf clusters.",
        "Occluder only; do not include trunk collision in this layer.",
    ),
    LayerSpec(
        "tree_right_trunk",
        "region_home_area_tree_right_trunk_v001.png",
        "YSortWorld/Trees",
        55,
        (4630, 1660),
        "Right fruit tree trunk and lower branches.",
        "Collision should stay near the lower trunk only.",
    ),
    LayerSpec(
        "tree_right_canopy_occluder",
        "region_home_area_tree_right_canopy_occluder_v001.png",
        "ForegroundStatic/Occluders",
        188,
        (4630, 1110),
        "Right fruit tree canopy with small warm fruit accents.",
        "Keep the BackFarm path mouth readable below it.",
    ),
    LayerSpec(
        "foreground_grass",
        "region_home_area_foreground_grass_v001.png",
        "ForegroundStatic",
        200,
        (0, 3300),
        "Foreground grass and low leaves along bottom and side edges.",
        "Edge framing only; should not cover the main path or interaction points.",
    ),
    LayerSpec(
        "shadow_dappled",
        "region_home_area_shadow_dappled_v001.png",
        "LightAndWeather",
        210,
        (0, 0),
        "Soft tree-cast dappled shadow overlay.",
        "Blend as multiply/modulate style overlay after art review.",
    ),
    LayerSpec(
        "light_overlay",
        "region_home_area_light_overlay_v001.png",
        "LightAndWeather",
        220,
        (0, 0),
        "Warm dappled sunlight overlay.",
        "Blend additively or at low alpha; keep gameplay silhouettes clear.",
    ),
]


def rgba(color: tuple[int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def noise_texture(size: tuple[int, int], dark: tuple[int, int, int], light: tuple[int, int, int], sigma: float = 46) -> Image.Image:
    noise = Image.effect_noise(size, sigma).convert("L")
    noise = ImageOps.autocontrast(noise, cutoff=2)
    return ImageOps.colorize(noise, dark, light).convert("RGBA")


def polygon_mask(points: list[tuple[int, int]], blur: float = 0.0, size: tuple[int, int] = CANVAS) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    if blur:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def ellipse_mask(bounds: tuple[int, int, int, int], blur: float = 0.0, size: tuple[int, int] = CANVAS) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse(bounds, fill=255)
    if blur:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def apply_mask(image: Image.Image, mask: Image.Image, alpha: int = 255) -> Image.Image:
    result = image.copy()
    if alpha != 255:
        mask = ImageChops.multiply(mask, Image.new("L", mask.size, alpha))
    result.putalpha(mask)
    return result


def alpha_composite_masked(target: Image.Image, source: Image.Image, mask: Image.Image, alpha: int = 255) -> None:
    target.alpha_composite(apply_mask(source, mask, alpha))


def draw_path_detail(layer: Image.Image, mask: Image.Image, seed: int, count: int) -> None:
    rng = random.Random(seed)
    draw = ImageDraw.Draw(layer, "RGBA")
    for _ in range(count):
        x = rng.randrange(CANVAS[0])
        y = rng.randrange(CANVAS[1])
        if mask.getpixel((x, y)) < 12:
            continue
        rx = rng.randrange(7, 34)
        ry = rng.randrange(3, 12)
        color = rng.choice(
            (
                (117, 101, 76, 42),
                (199, 181, 134, 36),
                (91, 82, 67, 36),
                (146, 123, 89, 30),
            )
        )
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=color)


def draw_grass_strokes(layer: Image.Image, mask: Image.Image, seed: int, count: int, tall: bool = False) -> None:
    rng = random.Random(seed)
    draw = ImageDraw.Draw(layer, "RGBA")
    max_len = 92 if tall else 34
    min_len = 16 if tall else 5
    for _ in range(count):
        x = rng.randrange(CANVAS[0])
        y = rng.randrange(CANVAS[1])
        if mask.getpixel((x, y)) < 20:
            continue
        length = rng.randrange(min_len, max_len)
        bend = rng.randrange(-22, 23) if tall else rng.randrange(-8, 9)
        color = rng.choice(
            (
                (55, 103, 57, 116),
                (88, 138, 75, 100),
                (141, 169, 89, 78),
                (80, 126, 64, 90),
            )
        )
        draw.line((x, y, x + bend, y - length), fill=color, width=rng.choice((1, 1, 2)))


def draw_soft_shadow(target: Image.Image, bounds: tuple[int, int, int, int], alpha: int = 60) -> None:
    shadow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow, "RGBA")
    draw.ellipse(bounds, fill=(48, 42, 31, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    target.alpha_composite(shadow)


def build_ground_yard() -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    mask = Image.new("L", CANVAS, 255)
    texture = noise_texture(CANVAS, (91, 134, 82), (159, 188, 116), sigma=54)
    alpha_composite_masked(layer, texture, mask)

    edge_vignette = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    edge_draw = ImageDraw.Draw(edge_vignette, "RGBA")
    edge_draw.rectangle((0, 0, CANVAS[0], 520), fill=(67, 104, 71, 28))
    edge_draw.rectangle((0, 3520, CANVAS[0], CANVAS[1]), fill=(72, 112, 70, 22))
    edge_draw.rectangle((0, 0, 380, CANVAS[1]), fill=(72, 112, 70, 18))
    edge_draw.rectangle((5740, 0, CANVAS[0], CANVAS[1]), fill=(72, 112, 70, 18))
    layer.alpha_composite(edge_vignette.filter(ImageFilter.GaussianBlur(95)))

    garden_mask = polygon_mask([(500, 1570), (1980, 1485), (2130, 2810), (430, 2910), (300, 2130)], blur=18)
    garden = noise_texture(CANVAS, (84, 128, 68), (148, 176, 87), sigma=62)
    alpha_composite_masked(layer, garden, garden_mask, 118)

    draw = ImageDraw.Draw(layer, "RGBA")
    rng = random.Random(SEED + 2)
    for x in range(720, 1960, 165):
        y0 = 1670 + rng.randrange(-50, 70)
        draw.rounded_rectangle((x, y0, x + 82, y0 + 900), radius=18, fill=(78, 106, 58, 54))
        draw.line((x + 15, y0 + 40, x + 62, y0 + 850), fill=(61, 86, 47, 56), width=3)

    draw_grass_strokes(layer, mask, SEED + 3, 8400)
    for _ in range(260):
        x = rng.randrange(540, 2120)
        y = rng.randrange(1560, 2860)
        if garden_mask.getpixel((x, y)) < 30:
            continue
        color = rng.choice(((228, 198, 129, 126), (209, 126, 104, 104), (235, 225, 170, 94)))
        r = rng.randrange(2, 6)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

    draw_soft_shadow(layer, (2080, 1680, 4260, 2860), 28)
    return layer


def build_village_road() -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    road_poly = [
        (240, 650),
        (5780, 520),
        (6030, 1130),
        (5380, 1460),
        (3220, 1370),
        (1860, 1510),
        (460, 1320),
    ]
    mask = polygon_mask(road_poly, blur=6)
    road = noise_texture(CANVAS, (129, 112, 82), (189, 170, 124), sigma=52)
    alpha_composite_masked(layer, road, mask)
    draw_path_detail(layer, mask, SEED + 10, 1700)
    draw = ImageDraw.Draw(layer, "RGBA")
    rng = random.Random(SEED + 11)
    for _ in range(360):
        x = rng.randrange(250, 5840)
        y = rng.choice((rng.randrange(560, 720), rng.randrange(1280, 1510)))
        if mask.getpixel((x, y)) < 10:
            continue
        draw.line((x, y, x + rng.randrange(-30, 31), y - rng.randrange(15, 55)), fill=(64, 104, 57, 92), width=2)
    return layer


def build_back_farm_path() -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    path_poly = [
        (3540, 2460),
        (4300, 2440),
        (4480, 2840),
        (4390, 3290),
        (4580, 3790),
        (4250, 3990),
        (3835, 3920),
        (3890, 3330),
        (3710, 2880),
    ]
    mask = polygon_mask(path_poly, blur=22)
    path = noise_texture(CANVAS, (133, 116, 83), (195, 176, 126), sigma=50)
    alpha_composite_masked(layer, path, mask, 230)
    draw_path_detail(layer, mask, SEED + 20, 720)
    draw = ImageDraw.Draw(layer, "RGBA")
    rng = random.Random(SEED + 21)
    for _ in range(460):
        x = rng.randrange(3500, 4760)
        y = rng.randrange(2360, 3980)
        if mask.getpixel((x, y)) > 20:
            continue
        draw.line((x, y, x + rng.randrange(-11, 12), y - rng.randrange(7, 28)), fill=(62, 107, 54, 88), width=1)
    return layer


def build_veranda_floor() -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    floor = [(2450, 1655), (3890, 1620), (4060, 1905), (2580, 1970)]
    draw.polygon(floor, fill=(139, 99, 59, 248))
    for i in range(13):
        y = 1668 + i * 22
        draw.line((2485, y, 3995, y - 38), fill=(89, 62, 37, 78), width=3)
    for x in range(2550, 3980, 145):
        draw.line((x, 1648, x + 128, 1934), fill=(188, 145, 88, 38), width=2)
    draw.polygon([(2610, 1940), (4000, 1878), (4110, 1972), (2710, 2040)], fill=(103, 75, 49, 210))
    return layer.filter(ImageFilter.UnsharpMask(radius=1.0, percent=60, threshold=2))


def build_house_body() -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    body = [(2250, 1110), (4040, 1080), (3920, 1690), (2360, 1750)]
    draw.polygon(body, fill=(171, 130, 82, 255))
    shadow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ImageDraw.Draw(shadow, "RGBA").polygon([(2290, 1510), (3965, 1450), (3920, 1690), (2360, 1750)], fill=(70, 47, 28, 78))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2)))

    rng = random.Random(SEED + 30)
    for y in range(1160, 1700, 42):
        draw.line((2320, y, 3960, y - rng.randrange(0, 32)), fill=(116, 78, 46, 54), width=3)
    for x in range(2400, 3920, 170):
        draw.line((x, 1120, x - 42, 1725), fill=(102, 68, 41, 54), width=4)

    draw.rectangle((3020, 1360, 3260, 1710), fill=(70, 47, 32, 245))
    draw.rectangle((3040, 1390, 3240, 1710), outline=(134, 88, 49, 180), width=7)
    draw.ellipse((3208, 1535, 3228, 1555), fill=(219, 176, 88, 235))

    for box in ((2490, 1265, 2785, 1450), (3490, 1238, 3795, 1430)):
        draw.rectangle(box, fill=(83, 105, 102, 155))
        draw.rectangle(box, outline=(91, 61, 37, 220), width=9)
        mid_x = (box[0] + box[2]) // 2
        mid_y = (box[1] + box[3]) // 2
        draw.line((mid_x, box[1], mid_x, box[3]), fill=(91, 61, 37, 180), width=5)
        draw.line((box[0], mid_y, box[2], mid_y), fill=(91, 61, 37, 180), width=5)

    for _ in range(240):
        x = rng.randrange(2260, 4040)
        y = rng.randrange(1120, 1720)
        draw.line((x, y, x + rng.randrange(10, 45), y + rng.randrange(-3, 4)), fill=(219, 170, 105, 28), width=1)

    return layer.filter(ImageFilter.UnsharpMask(radius=1.0, percent=70, threshold=2))


def build_house_roof() -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    roof = [(2010, 1075), (2390, 775), (3830, 745), (4280, 1025), (4050, 1215), (2190, 1245)]
    draw.polygon(roof, fill=(66, 73, 70, 255))
    ridge = [(2400, 775), (3830, 745), (4025, 865), (2220, 898)]
    draw.polygon(ridge, fill=(92, 99, 91, 230))
    rng = random.Random(SEED + 40)
    for x in range(2180, 4110, 68):
        draw.line((x, 900, x + rng.randrange(-80, 38), 1210), fill=(35, 42, 42, 95), width=5)
    for y in range(910, 1200, 44):
        draw.line((2140, y, 4110, y - 30), fill=(102, 111, 100, 42), width=3)
    draw.line((2180, 1240, 4050, 1210), fill=(45, 33, 23, 190), width=18)
    draw.line((2025, 1072, 4270, 1026), fill=(39, 46, 45, 120), width=8)
    return layer.filter(ImageFilter.UnsharpMask(radius=1.0, percent=80, threshold=2))


def build_tree_trunk(anchor: tuple[int, int], seed: int, scale: float = 1.0) -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    rng = random.Random(seed)
    ax, ay = anchor
    height = int(660 * scale)
    width = int(165 * scale)
    trunk = [
        (ax - width // 2, ay + height // 2),
        (ax - int(width * 0.24), ay - height // 2),
        (ax + int(width * 0.28), ay - height // 2),
        (ax + width // 2, ay + height // 2),
    ]
    draw.polygon(trunk, fill=(88, 56, 34, 255))
    draw_soft_shadow(layer, (ax - 190, ay + 205, ax + 210, ay + 340), 64)
    for _ in range(28):
        x = ax + rng.randrange(-int(width * 0.35), int(width * 0.35))
        draw.line((x, ay - height // 2 + 40, x + rng.randrange(-24, 28), ay + height // 2 - 26), fill=(48, 31, 22, 95), width=rng.randrange(2, 6))
    branch_color = (79, 49, 30, 238)
    draw.polygon([(ax - 36, ay - 120), (ax - 330, ay - 300), (ax - 306, ay - 350), (ax + 4, ay - 170)], fill=branch_color)
    draw.polygon([(ax + 34, ay - 160), (ax + 340, ay - 355), (ax + 312, ay - 405), (ax - 8, ay - 205)], fill=branch_color)
    draw.polygon([(ax - 8, ay - 250), (ax - 165, ay - 545), (ax - 122, ay - 570), (ax + 35, ay - 260)], fill=(82, 51, 30, 218))
    return layer.filter(ImageFilter.UnsharpMask(radius=1.0, percent=65, threshold=2))


def build_canopy(center: tuple[int, int], seed: int, fruit: bool = False, spread: tuple[int, int] = (760, 520)) -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    rng = random.Random(seed)
    cx, cy = center
    clusters = [
        (-0.42, -0.02, 0.34, 0.28),
        (-0.14, -0.22, 0.40, 0.32),
        (0.22, -0.14, 0.36, 0.29),
        (0.42, 0.12, 0.31, 0.24),
        (-0.04, 0.18, 0.52, 0.30),
    ]
    for ox, oy, rx, ry in clusters:
        x = cx + int(ox * spread[0])
        y = cy + int(oy * spread[1])
        color = rng.choice(((42, 90, 47, 238), (54, 112, 56, 234), (73, 130, 68, 228)))
        draw.ellipse((x - int(rx * spread[0]), y - int(ry * spread[1]), x + int(rx * spread[0]), y + int(ry * spread[1])), fill=color)

    for _ in range(1400):
        x = rng.randrange(max(0, cx - spread[0]), min(CANVAS[0], cx + spread[0]))
        y = rng.randrange(max(0, cy - spread[1]), min(CANVAS[1], cy + spread[1]))
        if layer.getpixel((x, y))[3] < 10:
            continue
        r = rng.randrange(4, 15)
        color = rng.choice(((29, 69, 36, 55), (103, 153, 79, 64), (154, 169, 83, 44), (52, 105, 51, 50)))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

    if fruit:
        for _ in range(65):
            x = rng.randrange(cx - spread[0] // 2, cx + spread[0] // 2)
            y = rng.randrange(cy - spread[1] // 3, cy + spread[1] // 2)
            if layer.getpixel((x, y))[3] < 80:
                continue
            r = rng.randrange(5, 11)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(205, 103, 58, 154))

    return layer.filter(ImageFilter.GaussianBlur(0.35)).filter(ImageFilter.UnsharpMask(radius=1.0, percent=80, threshold=3))


def build_foreground_grass() -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    bottom = polygon_mask([(0, 3290), (900, 3140), (1860, 3360), (3160, 3550), (4360, 3350), (6144, 3190), (6144, 4095), (0, 4095)], blur=5)
    left = polygon_mask([(0, 2200), (390, 2110), (700, 4095), (0, 4095)], blur=8)
    right = polygon_mask([(5790, 2020), (6144, 1960), (6144, 4095), (5460, 4095)], blur=8)
    mask = ImageChops.lighter(ImageChops.lighter(bottom, left), right)
    draw_grass_strokes(layer, mask, SEED + 80, 4600, tall=True)
    draw = ImageDraw.Draw(layer, "RGBA")
    rng = random.Random(SEED + 81)
    for _ in range(280):
        x = rng.randrange(0, CANVAS[0])
        y = rng.randrange(3080, CANVAS[1])
        if mask.getpixel((x, y)) < 20:
            continue
        color = rng.choice(((226, 214, 149, 120), (219, 139, 111, 92), (244, 229, 181, 82)))
        r = rng.randrange(2, 6)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
    return layer


def build_dappled_shadow() -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    rng = random.Random(SEED + 90)
    for _ in range(90):
        x = rng.randrange(850, 4800)
        y = rng.randrange(960, 3120)
        rx = rng.randrange(90, 360)
        ry = rng.randrange(22, 86)
        angle = rng.uniform(-0.8, 0.3)
        points = []
        for i in range(16):
            t = 2 * math.pi * i / 16
            px = math.cos(t) * rx
            py = math.sin(t) * ry
            points.append((x + px * math.cos(angle) - py * math.sin(angle), y + px * math.sin(angle) + py * math.cos(angle)))
        draw.polygon(points, fill=(42, 53, 37, rng.randrange(18, 48)))
    return layer.filter(ImageFilter.GaussianBlur(10))


def build_light_overlay() -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    rng = random.Random(SEED + 100)
    for _ in range(70):
        x = rng.randrange(740, 4880)
        y = rng.randrange(790, 2860)
        rx = rng.randrange(120, 420)
        ry = rng.randrange(24, 94)
        angle = rng.uniform(-0.85, 0.15)
        points = []
        for i in range(18):
            t = 2 * math.pi * i / 18
            px = math.cos(t) * rx
            py = math.sin(t) * ry
            points.append((x + px * math.cos(angle) - py * math.sin(angle), y + px * math.sin(angle) + py * math.cos(angle)))
        draw.polygon(points, fill=(255, 230, 146, rng.randrange(18, 48)))
    return layer.filter(ImageFilter.GaussianBlur(14))


def crop_layer(image: Image.Image, padding: int = 18) -> tuple[Image.Image, tuple[int, int]]:
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        return image, (0, 0)
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(image.width, bbox[2] + padding)
    bottom = min(image.height, bbox[3] + padding)
    return image.crop((left, top, right, bottom)), (left, top)


def paste_from_manifest(canvas: Image.Image, layer_path: Path, origin: tuple[int, int]) -> None:
    layer = Image.open(layer_path).convert("RGBA")
    canvas.alpha_composite(layer, origin)


def build_layers() -> dict[str, Image.Image]:
    return {
        "ground_yard": build_ground_yard(),
        "path_village_road": build_village_road(),
        "path_back_farm": build_back_farm_path(),
        "veranda_floor": build_veranda_floor(),
        "house_body": build_house_body(),
        "house_roof_occluder": build_house_roof(),
        "tree_left_trunk": build_tree_trunk((1420, 1290), SEED + 60, 1.0),
        "tree_left_canopy_occluder": build_canopy((1370, 760), SEED + 61, False, (840, 570)),
        "tree_right_trunk": build_tree_trunk((4630, 1690), SEED + 70, 0.88),
        "tree_right_canopy_occluder": build_canopy((4630, 1110), SEED + 71, True, (690, 500)),
        "foreground_grass": build_foreground_grass(),
        "shadow_dappled": build_dappled_shadow(),
        "light_overlay": build_light_overlay(),
    }


def make_base(layers: dict[str, Image.Image]) -> Image.Image:
    base = noise_texture(CANVAS, (90, 130, 81), (145, 176, 111), sigma=36)
    base.putalpha(Image.new("L", CANVAS, 255))
    order = [
        "ground_yard",
        "path_village_road",
        "path_back_farm",
        "veranda_floor",
        "house_body",
        "tree_left_trunk",
        "tree_right_trunk",
        "house_roof_occluder",
        "tree_left_canopy_occluder",
        "tree_right_canopy_occluder",
        "foreground_grass",
        "shadow_dappled",
        "light_overlay",
    ]
    for key in order:
        base.alpha_composite(layers[key])
    return base


def make_preview(base: Image.Image) -> None:
    preview = base.resize((1536, 1024), Image.Resampling.LANCZOS)
    preview.save(PREVIEW)


def make_contact_sheet(layer_records: list[dict[str, Any]]) -> None:
    tile_w, tile_h = 512, 384
    sheet = Image.new("RGBA", (tile_w * 4, tile_h * 4), (38, 44, 40, 255))
    draw = ImageDraw.Draw(sheet, "RGBA")
    for index, record in enumerate(layer_records):
        if record["asset_id"] == "base_full":
            continue
        path = OUT_DIR / record["file"]
        image = Image.open(path).convert("RGBA")
        cell_x = (index % 4) * tile_w
        cell_y = (index // 4) * tile_h
        scale = min((tile_w - 48) / image.width, (tile_h - 82) / image.height, 1.0)
        resized = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))), Image.Resampling.LANCZOS)
        sheet.alpha_composite(resized, (cell_x + (tile_w - resized.width) // 2, cell_y + 38 + (tile_h - 82 - resized.height) // 2))
        draw.text((cell_x + 18, cell_y + 14), record["asset_id"], fill=(230, 236, 220, 255))
        draw.text((cell_x + 18, cell_y + tile_h - 32), f"origin {record['origin_px']['x']},{record['origin_px']['y']}", fill=(178, 190, 171, 255))
    sheet.save(CONTACT)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    layers = build_layers()
    base = make_base(layers)
    layers["base_full"] = base

    records: list[dict[str, Any]] = []
    for spec in LAYER_SPECS:
        image = layers[spec.asset_id]
        if spec.full_canvas:
            output = image
            origin = (0, 0)
        else:
            output, origin = crop_layer(image)
        output.save(OUT_DIR / spec.filename)
        bbox = output.getchannel("A").getbbox() if output.mode == "RGBA" else None
        records.append(
            {
                "asset_id": spec.asset_id,
                "file": spec.filename,
                "origin_px": {"x": origin[0], "y": origin[1]},
                "size_px": {"width": output.width, "height": output.height},
                "alpha_bbox": list(bbox) if bbox else None,
                "anchor_px": {"x": spec.anchor_px[0], "y": spec.anchor_px[1]},
                "target_parent": spec.target_parent,
                "z_index": spec.z_index,
                "role": spec.role,
                "integration_note": spec.integration_note,
                "source": "single_composition_region_home_area_design_contract_v001",
            }
        )

    make_preview(base)
    make_contact_sheet(records)

    manifest = {
        "region_id": "Region_HomeArea",
        "package_id": "home_area_art_v001",
        "status": "visual_review_required_before_runtime_integration",
        "runtime_replacement": False,
        "canvas_px": layout["canvas_px"],
        "design_contract": LAYOUT.relative_to(ROOT).as_posix(),
        "composition_source": "region_home_area_design_blockout_3d_v001_spatial_reference",
        "assets": records,
        "preview": PREVIEW.name,
        "contact_sheet": CONTACT.name,
        "integration_gate": [
            "Do not wire runtime scene before visual acceptance.",
            "Integrate ground/path first, then house body and roof, then tree occluders and foreground overlays.",
            "After integration, validate player scale, walkable zones, z-index, occlusion, collisions, interactions, and transitions.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK: generated {len(records)} Region_HomeArea art v001 assets")
    print(f"OK: preview: {PREVIEW.relative_to(ROOT).as_posix()}")
    print(f"OK: manifest: {MANIFEST.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
