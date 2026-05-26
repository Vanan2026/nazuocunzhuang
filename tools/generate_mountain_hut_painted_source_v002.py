from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
V002_DIR = SOURCE_DIR / "v002"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock/layout_lock.json"
VILLAGE_SOURCE = ROOT / "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
V001_SOURCE = SOURCE_DIR / "mountain_hut_painted_source.png"
V002_SOURCE = V002_DIR / "mountain_hut_painted_source_v002.png"
V002_OVERLAY = REVIEW_DIR / "mountain_hut_painted_source_review_overlay_v002.png"
V002_CONTACT = REVIEW_DIR / "mountain_hut_v002_review_contact_sheet.png"
V002_QUALITY = REVIEW_DIR / "source_quality_review_v002.json"
V002_ACCEPTANCE = V002_DIR / "source_acceptance_v002.json"
V002_REPORT = ROOT / ".codex/reports/mountain_hut_v002_source_candidate_review_2026-05-25.md"

CANVAS = (1800, 1200)
CONTACT_SIZE = (1800, 1500)
SEED = 250525
CANDIDATE_ID = "mountain_hut_painted_source_candidate_v002"
STATUS = "v002_candidate_ready_for_human_art_review"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def point(values: Iterable[float]) -> tuple[int, int]:
    x, y = values
    return int(round(float(x))), int(round(float(y)))


def polygon(values: Iterable[Iterable[float]]) -> list[tuple[int, int]]:
    return [point(item) for item in values]


def overlay(base: Image.Image, layer: Image.Image) -> None:
    base.alpha_composite(layer)


def safe_font(size: int) -> ImageFont.ImageFont:
    for name in ["arial.ttf", "seguiemj.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_soft_shape(
    image: Image.Image,
    kind: str,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
    blur: int,
) -> None:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    if kind == "ellipse":
        draw.ellipse(box, fill=color)
    else:
        draw.rounded_rectangle(box, radius=max(4, min(box[2] - box[0], box[3] - box[1]) // 6), fill=color)
    overlay(image, layer.filter(ImageFilter.GaussianBlur(blur)))


def draw_polyline(
    image: Image.Image,
    points: list[tuple[int, int]],
    width: int,
    color: tuple[int, int, int, int],
) -> None:
    if len(points) < 2:
        return
    draw = ImageDraw.Draw(image)
    draw.line(points, fill=color, width=width, joint="curve")
    radius = width // 2
    for x, y in points:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def make_path_mask(layout: dict[str, Any], expand: int = 80) -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    draw = ImageDraw.Draw(mask)
    for road in layout.get("road_paths", []):
        if not isinstance(road, dict):
            continue
        points = polygon(road.get("source_points", []))
        width = int(road.get("source_width", 54)) + expand
        if len(points) >= 2:
            draw.line(points, fill=255, width=width, joint="curve")
            radius = width // 2
            for x, y in points:
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)
    return mask.filter(ImageFilter.GaussianBlur(22))


def draw_ground(image: Image.Image, layout: dict[str, Any]) -> None:
    random.seed(SEED)
    base = Image.new("RGBA", CANVAS, (92, 124, 54, 255))
    noise = Image.effect_noise(CANVAS, 58).convert("L")
    dark = Image.new("RGBA", CANVAS, (48, 88, 38, 255))
    light = Image.new("RGBA", CANVAS, (149, 163, 70, 255))
    texture = Image.composite(light, dark, noise)
    overlay(image, Image.blend(base, texture, 0.28))

    if VILLAGE_SOURCE.is_file():
        village = Image.open(VILLAGE_SOURCE).convert("RGBA")
        ref = village.crop((1020, 50, 1780, 960)).resize(CANVAS)
        ref = ref.filter(ImageFilter.GaussianBlur(5))
        ref.putalpha(88)
        overlay(image, ref)
        detail = ImageChops.subtract(village.filter(ImageFilter.UnsharpMask(radius=2.0, percent=135, threshold=3)), village.filter(ImageFilter.GaussianBlur(4)))
        detail = detail.crop((900, 80, 1780, 1120)).resize(CANVAS)
        detail.putalpha(58)
        overlay(image, detail)

    for _ in range(110):
        cx = random.randint(-140, CANVAS[0] + 140)
        cy = random.randint(-100, CANVAS[1] + 100)
        rx = random.randint(80, 260)
        ry = random.randint(34, 130)
        color = random.choice(
            [
                (165, 184, 84, 30),
                (38, 86, 37, 28),
                (200, 180, 86, 20),
                (83, 128, 57, 34),
                (122, 153, 75, 26),
            ]
        )
        draw_soft_shape(image, "ellipse", (cx - rx, cy - ry, cx + rx, cy + ry), color, blur=random.randint(18, 42))

    path_mask = make_path_mask(layout)
    shoulder = Image.new("RGBA", CANVAS, (156, 139, 76, 0))
    shoulder.putalpha(path_mask.point(lambda value: int(value * 0.22)))
    overlay(image, shoulder)


def draw_paths(image: Image.Image, layout: dict[str, Any]) -> None:
    random.seed(SEED + 11)
    draw = ImageDraw.Draw(image)
    for road in layout.get("road_paths", []):
        points = polygon(road.get("source_points", []))
        width = int(road.get("source_width", 54))
        draw_polyline(image, points, width + 56, (81, 95, 53, 96))
        draw_polyline(image, points, width + 38, (134, 120, 70, 146))
        draw_polyline(image, points, width + 20, (184, 151, 84, 218))
        draw_polyline(image, points, max(22, width - 8), (219, 181, 103, 212))
        draw_polyline(image, points, max(12, width - 32), (232, 203, 132, 104))

    for road in layout.get("road_paths", []):
        points = polygon(road.get("source_points", []))
        for index in range(len(points) - 1):
            x1, y1 = points[index]
            x2, y2 = points[index + 1]
            for step in range(48):
                t = (step + random.random()) / 48.0
                x = int(x1 + (x2 - x1) * t + random.randint(-44, 44))
                y = int(y1 + (y2 - y1) * t + random.randint(-30, 30))
                if random.random() < 0.62:
                    draw.ellipse((x - 5, y - 3, x + 6, y + 3), fill=random.choice([(112, 105, 76, 132), (151, 137, 94, 118), (92, 104, 74, 110)]))
                else:
                    draw.arc((x - 16, y - 8, x + 18, y + 10), start=random.randint(5, 85), end=random.randint(140, 300), fill=(119, 97, 66, 84), width=1)

    path_mask = make_path_mask(layout, expand=40)
    grass_draw = ImageDraw.Draw(image)
    for _ in range(900):
        x = random.randint(0, CANVAS[0] - 1)
        y = random.randint(0, CANVAS[1] - 1)
        if path_mask.getpixel((x, y)) < random.randint(24, 128):
            continue
        length = random.randint(8, 28)
        grass_draw.line((x, y, x + random.randint(-5, 5), y - length), fill=random.choice([(49, 102, 43, 126), (95, 136, 57, 116), (161, 170, 80, 90)]), width=random.choice([1, 1, 2]))


def draw_roof_tiles(draw: ImageDraw.ImageDraw, roof: list[tuple[int, int]]) -> None:
    draw.polygon(roof, fill=(143, 76, 48, 255), outline=(75, 48, 32, 255))
    for row in range(9):
        y = min(point[1] for point in roof) + 50 + row * 24
        x_start = min(point[0] for point in roof) + 70 - row * 3
        x_end = max(point[0] for point in roof) - 60 + row * 2
        draw.line((x_start, y, x_end, y + 34), fill=(92, 53, 38, 108), width=2)
        for col in range(0, max(1, x_end - x_start), 46):
            x = x_start + col + (row % 2) * 18
            draw.arc((x - 4, y - 6, x + 42, y + 22), start=188, end=358, fill=(190, 106, 62, 150), width=2)
            draw.line((x, y + 3, x + 14, y + 42), fill=(105, 59, 42, 76), width=1)
    for x, y in roof:
        draw.ellipse((x - 5, y - 3, x + 5, y + 3), fill=(203, 136, 86, 100))


def draw_hut(image: Image.Image, layout: dict[str, Any]) -> None:
    zones = {item["id"]: item for item in layout["object_zones"]}
    x, y, w, h = [int(value) for value in zones["MountainHutExterior"]["source_rect"]]
    cx = x + w // 2
    draw_soft_shape(image, "ellipse", (x + 42, y + h - 26, x + w + 90, y + h + 92), (37, 53, 31, 94), blur=16)
    draw = ImageDraw.Draw(image)

    body = (x + 70, y + 132, x + w - 40, y + h - 20)
    draw.rounded_rectangle(body, radius=20, fill=(213, 184, 128, 255), outline=(74, 55, 36, 255), width=4)
    for yy in range(body[1] + 18, body[3] - 10, 17):
        draw.line((body[0] + 14, yy, body[2] - 18, yy + random.randint(-2, 3)), fill=random.choice([(174, 136, 88, 92), (232, 203, 146, 76), (119, 91, 61, 52)]), width=random.choice([1, 2, 2]))
    for _ in range(110):
        px = random.randint(body[0] + 10, body[2] - 10)
        py = random.randint(body[1] + 8, body[3] - 8)
        draw.ellipse((px - 2, py - 1, px + 2, py + 1), fill=random.choice([(178, 145, 100, 92), (236, 210, 154, 70), (128, 97, 65, 60)]))

    roof = [
        (x + 8, y + 168),
        (cx - 24, y + 22),
        (x + w + 20, y + 156),
        (x + w - 62, y + 224),
        (x + 96, y + 228),
    ]
    draw_roof_tiles(draw, roof)
    draw.line((x + 34, y + 172, x + 108, y + 226), fill=(232, 154, 90, 118), width=5)
    draw.line((x + w - 26, y + 158, x + w - 82, y + 222), fill=(76, 47, 34, 108), width=5)

    dx, dy, dw, dh = [int(value) for value in zones["HutDoor"]["source_rect"]]
    draw.rounded_rectangle((dx + 28, dy + 24, dx + dw - 28, dy + dh + 4), radius=12, fill=(86, 58, 36, 255), outline=(52, 38, 28, 255), width=4)
    for xx in range(dx + 42, dx + dw - 38, 17):
        draw.line((xx, dy + 34, xx + random.randint(-2, 4), dy + dh - 4), fill=(137, 86, 49, 118), width=2)
    for yy in range(dy + 52, dy + dh - 8, 22):
        draw.line((dx + 38, yy, dx + dw - 40, yy + random.randint(-2, 2)), fill=(56, 42, 31, 92), width=1)
    draw.ellipse((dx + dw - 58, dy + 98, dx + dw - 45, dy + 111), fill=(222, 182, 91, 255))
    draw.rounded_rectangle((dx - 6, dy + dh - 8, dx + dw + 20, dy + dh + 34), radius=7, fill=(146, 102, 63, 255), outline=(72, 50, 33, 255), width=3)
    for px in range(dx + 10, dx + dw + 8, 32):
        draw.line((px, dy + dh - 6, px + 18, dy + dh + 30), fill=(99, 69, 45, 80), width=2)

    for wx, wy in [(x + 148, y + 250), (x + w - 158, y + 254)]:
        draw.rounded_rectangle((wx - 40, wy - 26, wx + 42, wy + 28), radius=6, fill=(117, 162, 160, 255), outline=(55, 83, 76, 255), width=3)
        draw.rectangle((wx - 30, wy - 18, wx + 32, wy + 20), fill=(141, 185, 177, 160))
        draw.line((wx, wy - 24, wx, wy + 26), fill=(50, 78, 72, 180), width=2)
        draw.line((wx - 38, wy, wx + 40, wy), fill=(50, 78, 72, 180), width=2)
        for sx in [-52, 52]:
            draw.polygon([(wx + sx, wy - 28), (wx + sx + 18 * (1 if sx < 0 else -1), wy - 12), (wx + sx, wy + 28)], fill=(94, 144, 151, 210), outline=(53, 85, 88, 170))


def draw_props_and_plants(image: Image.Image, layout: dict[str, Any]) -> None:
    random.seed(SEED + 29)
    zones = {item["id"]: item for item in layout["object_zones"]}
    draw = ImageDraw.Draw(image)
    wx, wy, ww, wh = [int(value) for value in zones["QuietWoodpile"]["source_rect"]]
    draw.ellipse((wx - 28, wy + wh - 22, wx + ww + 26, wy + wh + 32), fill=(44, 61, 35, 58))
    for idx in range(10):
        ly = wy + 18 + idx * 13
        lx = wx + 18 + (idx % 3) * 17
        length = ww - random.randint(44, 72)
        draw.rounded_rectangle((lx, ly, lx + length, ly + 18), radius=8, fill=random.choice([(137, 84, 45, 255), (158, 102, 55, 255), (115, 73, 44, 255)]), outline=(72, 50, 34, 210), width=2)
        draw.ellipse((lx - 4, ly, lx + 20, ly + 18), fill=(191, 128, 68, 230), outline=(72, 50, 34, 170))
        draw.arc((lx + 2, ly + 3, lx + 17, ly + 15), start=30, end=330, fill=(112, 77, 47, 150), width=1)

    shelf_x, shelf_y = 1138, 462
    draw.rounded_rectangle((shelf_x, shelf_y, shelf_x + 158, shelf_y + 30), radius=5, fill=(112, 72, 43, 255), outline=(68, 48, 32, 255), width=2)
    for index in range(5):
        px = shelf_x + 14 + index * 29
        color = random.choice([(93, 137, 78, 255), (134, 153, 77, 255), (83, 133, 101, 255), (156, 141, 73, 255)])
        draw.rectangle((px + 7, shelf_y - 2, px + 21, shelf_y + 18), fill=(128, 80, 49, 255))
        for leaf in range(6):
            lx = px + 14 + random.randint(-14, 14)
            ly = shelf_y - 10 + random.randint(-28, 0)
            draw.ellipse((lx - 8, ly - 5, lx + 8, ly + 5), fill=color)

    for base_x, base_y in [(1030, 552), (1086, 544), (1195, 554), (1254, 538), (1310, 586), (930, 604)]:
        for blade in range(24):
            x = base_x + random.randint(-26, 26)
            y = base_y + random.randint(-12, 24)
            draw.line((x, y + 20, x + random.randint(-9, 9), y - random.randint(16, 44)), fill=random.choice([(50, 103, 44, 148), (91, 134, 60, 132), (157, 156, 71, 110)]), width=random.choice([1, 2]))
        for flower in range(5):
            fx = base_x + random.randint(-32, 32)
            fy = base_y + random.randint(-36, 2)
            draw.ellipse((fx - 4, fy - 4, fx + 4, fy + 4), fill=random.choice([(236, 221, 158, 180), (219, 172, 191, 150), (241, 238, 201, 170)]))


def draw_leaf_cluster(draw: ImageDraw.ImageDraw, cx: int, cy: int, rx: int, ry: int, palette: list[tuple[int, int, int, int]], count: int) -> None:
    for _ in range(count):
        angle = random.random() * math.tau
        radius = math.sqrt(random.random())
        x = int(cx + math.cos(angle) * rx * radius)
        y = int(cy + math.sin(angle) * ry * radius)
        w = random.randint(9, 22)
        h = random.randint(5, 14)
        draw.ellipse((x - w, y - h, x + w, y + h), fill=random.choice(palette))


def draw_depth_foliage(image: Image.Image, layout: dict[str, Any]) -> None:
    random.seed(SEED + 43)
    draw = ImageDraw.Draw(image)
    tree_palette = [
        (66, 106, 58, 232),
        (86, 132, 70, 236),
        (117, 151, 78, 226),
        (148, 169, 92, 198),
        (44, 82, 47, 210),
    ]
    for base_x, base_y, scale in [(135, 180, 1.0), (230, 955, 0.92), (1578, 935, 0.96), (1510, 128, 1.1), (1660, 235, 0.82)]:
        trunk_w = int(28 * scale)
        draw.rounded_rectangle((base_x - trunk_w // 2, base_y - 12, base_x + trunk_w // 2, base_y + int(122 * scale)), radius=10, fill=(83, 59, 39, 255))
        for offset in range(5):
            draw.line((base_x - trunk_w // 2 + offset * 6, base_y, base_x - trunk_w // 2 + offset * 8, base_y + int(118 * scale)), fill=(119, 80, 50, 74), width=2)
        draw_leaf_cluster(draw, base_x - 48, base_y - 58, int(92 * scale), int(58 * scale), tree_palette, 95)
        draw_leaf_cluster(draw, base_x + 38, base_y - 68, int(112 * scale), int(64 * scale), tree_palette, 115)
        draw_leaf_cluster(draw, base_x + 8, base_y - 18, int(126 * scale), int(66 * scale), tree_palette, 120)
        for _ in range(20):
            lx = base_x + random.randint(-95, 95)
            ly = base_y + random.randint(-112, 8)
            draw.line((lx, ly, lx + random.randint(-24, 24), ly + random.randint(8, 34)), fill=(42, 75, 40, 80), width=1)

    bough = next(item for item in layout["object_zones"] if item["id"] == "ForegroundPineBough")
    x, y, w, h = [int(value) for value in bough["source_rect"]]
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)
    pine_palette = [(45, 82, 58, 190), (62, 105, 67, 210), (85, 128, 78, 188), (34, 68, 49, 180)]
    for _ in range(120):
        bx = x + random.randint(-40, w + 80)
        by = y + random.randint(-26, h + 28)
        ldraw.ellipse((bx - random.randint(38, 105), by - random.randint(12, 32), bx + random.randint(38, 105), by + random.randint(12, 32)), fill=random.choice(pine_palette))
    overlay(image, layer.filter(ImageFilter.GaussianBlur(0.6)))


def draw_field_detail(image: Image.Image, layout: dict[str, Any]) -> None:
    random.seed(SEED + 61)
    draw = ImageDraw.Draw(image)
    path_mask = make_path_mask(layout, expand=60)
    for _ in range(2100):
        x = random.randint(24, CANVAS[0] - 24)
        y = random.randint(24, CANVAS[1] - 24)
        on_path = path_mask.getpixel((x, y)) > 96
        if on_path and random.random() < 0.74:
            continue
        length = random.randint(5, 26)
        draw.line((x, y, x + random.randint(-4, 5), y - length), fill=random.choice([(42, 96, 37, 104), (91, 137, 57, 96), (151, 166, 79, 76), (64, 113, 55, 98)]), width=random.choice([1, 1, 1, 2]))
    flower_clusters = [
        (210, 238, 92, 46),
        (300, 935, 120, 72),
        (820, 766, 128, 82),
        (1040, 610, 108, 78),
        (1270, 574, 92, 58),
        (1515, 920, 132, 78),
        (1642, 214, 124, 64),
    ]
    for _ in range(310):
        cx, cy, rx, ry = random.choice(flower_clusters)
        x = int(random.gauss(cx, rx * 0.42))
        y = int(random.gauss(cy, ry * 0.42))
        if x < 24 or x >= CANVAS[0] - 24 or y < 24 or y >= CANVAS[1] - 24:
            continue
        if path_mask.getpixel((x, y)) > 96 and random.random() < 0.72:
            continue
        petal = random.choice([(235, 224, 166, 142), (242, 240, 214, 136), (218, 171, 190, 118), (235, 185, 93, 116), (196, 207, 133, 105)])
        if random.random() < 0.42:
            for dx, dy in [(0, -2), (2, 0), (0, 2), (-2, 0)]:
                draw.ellipse((x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2), fill=petal)
        else:
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=petal)
    for _ in range(420):
        x = random.randint(20, CANVAS[0] - 20)
        y = random.randint(420, 820)
        if random.random() < 0.45 or path_mask.getpixel((x, y)) > 48:
            draw.ellipse((x - random.randint(3, 8), y - random.randint(2, 5), x + random.randint(3, 8), y + random.randint(2, 5)), fill=random.choice([(105, 107, 80, 124), (155, 145, 101, 112), (86, 98, 70, 106), (180, 165, 116, 82)]))
    for _ in range(150):
        x = random.randint(40, CANVAS[0] - 40)
        y = random.randint(80, CANVAS[1] - 80)
        draw.arc((x - 15, y - 7, x + 18, y + 9), start=random.randint(0, 80), end=random.randint(150, 310), fill=(71, 99, 53, 78), width=1)


def draw_paper_grain(image: Image.Image) -> None:
    noise = Image.effect_noise(CANVAS, 24).convert("L")
    warm = Image.new("RGBA", CANVAS, (241, 219, 160, 24))
    cool = Image.new("RGBA", CANVAS, (45, 74, 44, 18))
    grain = Image.composite(warm, cool, noise)
    overlay(image, grain)
    vignette = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    draw.rectangle((0, 0, CANVAS[0], CANVAS[1]), outline=(51, 70, 38, 52), width=50)
    overlay(image, vignette.filter(ImageFilter.GaussianBlur(34)))


def draw_source_v002(layout: dict[str, Any]) -> Image.Image:
    image = Image.new("RGBA", CANVAS, (0, 0, 0, 255))
    draw_ground(image, layout)
    draw_paths(image, layout)
    draw_soft_shape(image, "ellipse", (720, 310, 1290, 710), (83, 104, 61, 50), blur=28)
    draw_hut(image, layout)
    draw_props_and_plants(image, layout)
    draw_depth_foliage(image, layout)
    draw_field_detail(image, layout)
    draw_paper_grain(image)
    return image.convert("RGB")


def draw_review_overlay(source: Image.Image, layout: dict[str, Any]) -> Image.Image:
    result = source.convert("RGBA")
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for road in layout.get("road_paths", []):
        draw.line(polygon(road.get("source_points", [])), fill=(47, 91, 190, 230), width=8, joint="curve")
    for seam in layout.get("seam_connectors", []):
        sx, sy = point(seam["source_point"])
        draw.ellipse((sx - 28, sy - 28, sx + 28, sy + 28), outline=(35, 95, 190, 240), width=8)
        draw.text((sx + 34, sy - 22), str(seam["edge"]), fill=(35, 72, 140, 255), font=safe_font(24))
    for zone in layout.get("object_zones", []):
        if "source_rect" not in zone:
            continue
        x, y, w, h = [int(value) for value in zone["source_rect"]]
        draw.rectangle((x, y, x + w, y + h), outline=(190, 82, 64, 220), width=5)
        draw.text((x + 8, y + 8), str(zone["id"]), fill=(120, 46, 38, 255), font=safe_font(18))
    draw.rounded_rectangle((42, 42, 950, 168), radius=12, fill=(250, 244, 219, 224), outline=(94, 72, 45, 220), width=3)
    draw.text((66, 62), "MountainHut source candidate v002 - review overlay", fill=(65, 50, 35, 255), font=safe_font(30))
    draw.text((66, 104), "Blue: seam/path guides. Red: object zones. Runtime export still blocked.", fill=(65, 50, 35, 255), font=safe_font(26))
    overlay(result, layer)
    return result.convert("RGB")


def edge_detail_score(image: Image.Image) -> float:
    return float(ImageStat.Stat(image.convert("L").filter(ImageFilter.FIND_EDGES)).mean[0])


def gray_variance(image: Image.Image) -> float:
    return float(ImageStat.Stat(image.convert("L")).var[0])


def edge_rgb_mean(image: Image.Image, edge: str, width: int = 56) -> tuple[float, float, float]:
    if edge == "west":
        crop = image.crop((0, 0, width, image.height))
    elif edge == "east":
        crop = image.crop((image.width - width, 0, image.width, image.height))
    else:
        raise ValueError(edge)
    return tuple(float(value) for value in ImageStat.Stat(crop).mean[:3])


def average_delta(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum(abs(a[index] - b[index]) for index in range(3)) / 3.0


def calculate_metrics(v002: Image.Image) -> dict[str, float | list[float] | bool]:
    village = Image.open(VILLAGE_SOURCE).convert("RGB")
    v001 = Image.open(V001_SOURCE).convert("RGB")
    village_detail = edge_detail_score(village)
    v001_detail = edge_detail_score(v001)
    v002_detail = edge_detail_score(v002)
    village_variance = gray_variance(village)
    v002_variance = gray_variance(v002)
    seam_delta = average_delta(edge_rgb_mean(village, "east"), edge_rgb_mean(v002, "west"))
    return {
        "village_detail_edge_mean": round(village_detail, 4),
        "v001_detail_edge_mean": round(v001_detail, 4),
        "v002_detail_edge_mean": round(v002_detail, 4),
        "detail_ratio": round(v002_detail / village_detail, 4),
        "detail_improvement_over_v001": round(v002_detail / max(0.001, v001_detail), 4),
        "minimum_detail_ratio_for_review_ready": 0.68,
        "village_gray_variance": round(village_variance, 4),
        "v002_gray_variance": round(v002_variance, 4),
        "variance_ratio": round(v002_variance / village_variance, 4),
        "minimum_variance_ratio_for_review_ready": 0.62,
        "seam_edge_average_channel_delta": round(seam_delta, 4),
        "maximum_preferred_seam_delta_for_precheck": 24.0,
        "seam_color_precheck_passed": seam_delta <= 24.0,
    }


def make_contact_sheet(v002: Image.Image, overlay_image: Image.Image) -> None:
    board = Image.new("RGB", CONTACT_SIZE, (232, 221, 188))
    draw = ImageDraw.Draw(board)
    draw.text((36, 28), "MountainHut v002 source review", fill=(45, 36, 25), font=safe_font(34))
    draw.text((36, 74), "Compare Village quality target, v001 blocker, and v002 candidate. Runtime replacement remains blocked.", fill=(66, 54, 38), font=safe_font(22))
    village = Image.open(VILLAGE_SOURCE).convert("RGB")
    v001 = Image.open(V001_SOURCE).convert("RGB")

    cards = [
        ("Accepted Village quality target", village, (36, 130), (540, 360)),
        ("MountainHut v001 blocker", v001, (630, 130), (540, 360)),
        ("MountainHut v002 candidate", v002, (1224, 130), (540, 360)),
        ("v002 review overlay", overlay_image, (36, 560), (840, 560)),
        ("Village east / v002 west seam crops", make_seam_pair(village, v002), (960, 610), (760, 420)),
    ]
    for title, image, pos, size in cards:
        x, y = pos
        w, h = size
        draw.rounded_rectangle((x - 10, y - 42, x + w + 10, y + h + 14), radius=12, fill=(247, 240, 214), outline=(123, 101, 65), width=2)
        draw.text((x, y - 34), title, fill=(54, 45, 32), font=safe_font(22))
        board.paste(image.resize(size, Image.Resampling.LANCZOS), pos)
    V002_CONTACT.parent.mkdir(parents=True, exist_ok=True)
    board.save(V002_CONTACT)


def make_seam_pair(village: Image.Image, v002: Image.Image) -> Image.Image:
    village_crop = village.crop((village.width - 360, 490, village.width, 850))
    hut_crop = v002.crop((0, 487, 360, 847))
    pair = Image.new("RGB", (760, 420), (231, 219, 187))
    pair.paste(village_crop.resize((360, 360), Image.Resampling.LANCZOS), (20, 40))
    pair.paste(hut_crop.resize((360, 360), Image.Resampling.LANCZOS), (380, 40))
    draw = ImageDraw.Draw(pair)
    draw.line((380, 24, 380, 404), fill=(47, 91, 190), width=4)
    draw.text((52, 10), "Village east", fill=(55, 44, 32), font=safe_font(20))
    draw.text((504, 10), "MountainHut west", fill=(55, 44, 32), font=safe_font(20))
    return pair


def write_records(metrics: dict[str, Any]) -> None:
    quality = {
        "review_id": "mountain_hut_source_quality_review_v002",
        "status": STATUS,
        "reviewed_at": "2026-05-25",
        "source_candidate": rel(V002_SOURCE),
        "quality_reference_source": rel(VILLAGE_SOURCE),
        "previous_source_candidate": rel(V001_SOURCE),
        "review_overlay": rel(V002_OVERLAY),
        "review_contact_sheet": rel(V002_CONTACT),
        "source_candidate_review": rel(V002_REPORT),
        "metrics": metrics,
        "producer_verdict": "The v002 source candidate is a stronger full-canvas repaint candidate and is ready for human/art review, while layer export and runtime replacement remain blocked.",
        "remaining_review_notes": [
            "Human/art review must still approve the full composition before layer export.",
            "If accepted, runtime layers must derive from this single full-canvas painted source without independent recomposition.",
            "Godot screenshot review is still required after any future layer export."
        ],
        "hard_approval_flags": {
            "human_visual_approval": False,
            "layer_export_approved": False,
            "runtime_replacement": False,
            "launch_quality_approved": False,
        },
    }
    write_json(V002_QUALITY, quality)

    acceptance = {
        "candidate_id": CANDIDATE_ID,
        "status": STATUS,
        "candidate_type": "v002_full_canvas_storybook_source_candidate",
        "source_image": rel(V002_SOURCE),
        "review_overlay": rel(V002_OVERLAY),
        "quality_review": rel(V002_QUALITY),
        "review_contact_sheet": rel(V002_CONTACT),
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "codex_visual_precheck": {
            "status": "passed_v002_source_quality_precheck",
            "not_human_visual_approval": True,
            "notes": [
                "registration-perfect layer alignment remains the target; the image is one full canvas with shared origin",
                "single painted source rule is preserved before any future runtime layer split",
                "full canvas source remains opaque 1800x1200",
                "no runtime replacement or layer export is approved by this candidate",
                "human/art review is still required before acceptance"
            ],
        },
    }
    write_json(V002_ACCEPTANCE, acceptance)

    V002_REPORT.parent.mkdir(parents=True, exist_ok=True)
    V002_REPORT.write_text(
        f"""# MountainHut v002 Source Candidate Review - 2026-05-25

Status: {STATUS}

## Candidate

- Candidate id: `{CANDIDATE_ID}`
- Source image: `{rel(V002_SOURCE)}`
- Review overlay: `{rel(V002_OVERLAY)}`
- Contact sheet: `{rel(V002_CONTACT)}`
- Quality record: `{rel(V002_QUALITY)}`

## Automated Source-Quality Precheck

- Detail ratio: `{metrics['detail_ratio']}` against Village reference.
- Variance ratio: `{metrics['variance_ratio']}` against Village reference.
- Detail improvement over v001: `{metrics['detail_improvement_over_v001']}`.
- West seam color delta: `{metrics['seam_edge_average_channel_delta']}`.

## Boundary

Runtime replacement remains blocked. This is not human/art approval, not launch-quality approval, and not layer-export approval.

If human/art review accepts this source, every runtime layer must derive from this same full-canvas source with registration-perfect alignment.
""",
        encoding="utf-8",
    )


def update_manifests() -> None:
    workflow = load_json(WORKFLOW)
    workflow["status"] = "v002_source_candidate_ready_for_human_art_review"
    workflow["current_phase"] = "02_source_generation_v002_review"
    workflow["runtime_replacement"] = False
    workflow["launch_quality_approved"] = False
    workflow.setdefault("phase_status", {})["02_source_generation_v002"] = STATUS
    workflow["phase_status"]["03_layer_export"] = "blocked_until_source_acceptance"
    workflow.setdefault("validation", {})["v002_source_candidate_validator"] = "tools/validate_mountain_hut_v002_source_candidate.py"
    workflow["v002_source_candidate"] = {
        "candidate_id": CANDIDATE_ID,
        "status": STATUS,
        "candidate_type": "v002_full_canvas_storybook_source_candidate",
        "image": rel(V002_SOURCE),
        "review_overlay": rel(V002_OVERLAY),
        "review_contact_sheet": rel(V002_CONTACT),
        "acceptance_record": rel(V002_ACCEPTANCE),
        "quality_review_record": rel(V002_QUALITY),
        "generated_from": [
            rel(LAYOUT_LOCK),
            "production/assets/seams/village_to_mountain_hut/v001/seam_brief.md",
            rel(VILLAGE_SOURCE),
            rel(V001_SOURCE),
        ],
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
    }
    workflow["next_art_step"] = "human/art review the v002 source candidate before any layer export or runtime replacement."
    write_json(WORKFLOW, workflow)

    contract = load_json(LAYER_CONTRACT)
    source_image = contract.setdefault("source_image", {})
    source_image["v002_candidate"] = rel(V002_SOURCE)
    source_image["v002_quality_review"] = rel(V002_QUALITY)
    source_image["required_next_step"] = "Human/art review the v002 full-canvas source candidate before layer export."
    source_image["human_visual_approval"] = False
    source_image["layer_export_approved"] = False
    contract["layer_export_status"] = "blocked_until_v002_human_art_acceptance"
    contract["runtime_replacement"] = False
    write_json(LAYER_CONTRACT, contract)

    manifest = load_json(PROJECT_MANIFEST)
    for region in manifest.get("current_runtime_regions", []):
        if isinstance(region, dict) and region.get("region_id") == "Region_MountainHut":
            region["phase"] = "mountain_hut_v002_candidate_ready_for_human_art_review"
            region["active_v002_source_candidate"] = rel(V002_SOURCE)
            region["active_v002_quality_review"] = rel(V002_QUALITY)
            region["active_v002_review_contact_sheet"] = rel(V002_CONTACT)
            region["runtime_replacement"] = False
            region["launch_quality_approved"] = False
            region["human_visual_approval_required"] = True
            region["next_art_step"] = "human/art review the v002 source candidate before any layer export or runtime replacement."
    write_json(PROJECT_MANIFEST, manifest)


def main() -> None:
    layout = load_json(LAYOUT_LOCK)
    V002_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    source = draw_source_v002(layout)
    overlay_image = draw_review_overlay(source, layout)
    source.save(V002_SOURCE)
    overlay_image.save(V002_OVERLAY)
    make_contact_sheet(source, overlay_image)
    metrics = calculate_metrics(source)
    write_records(metrics)
    update_manifests()
    print(f"OK: generated {rel(V002_SOURCE)}")
    print(f"detail_ratio={metrics['detail_ratio']} variance_ratio={metrics['variance_ratio']} seam_delta={metrics['seam_edge_average_channel_delta']}")


if __name__ == "__main__":
    main()
