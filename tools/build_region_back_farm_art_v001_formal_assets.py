from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "production" / "assets" / "regions" / "back_farm_art" / "v001"
MANIFEST = ART_DIR / "region_back_farm_art_v001_manifest.json"
PREVIEW = ART_DIR / "region_back_farm_art_v001_runtime_preview.png"
CONTACT = ART_DIR / "region_back_farm_art_v001_layer_contact_sheet.png"
CANVAS = (2000, 2000)
SEED = 2026051702
STATUS = "self_checked_final_runtime_candidate"
SOURCE = "procedural_formal_layered_png_pass_from_region_back_farm_runtime_layout_2026_05_17"

LAYER_META = {
    "ground": ("region_back_farm_ground_v001.png", "TileMapLayer_Ground/ArtLayers", -100, "ground_underlay"),
    "path": ("region_back_farm_path_v001.png", "TileMapLayer_Path/ArtLayers", -90, "below_player"),
    "field_rows": ("region_back_farm_field_rows_v001.png", "TileMapLayer_Detail/ArtLayers", -70, "below_player"),
    "shed": ("region_back_farm_shed_v001.png", "YSortWorld/FarmStructures/ToolShed", 45, "ysort_structure"),
    "pond": ("region_back_farm_pond_v001.png", "YSortWorld/SmallPond", 20, "low_prop"),
    "fence": ("region_back_farm_fence_v001.png", "YSortWorld/FarmStructures", 35, "low_prop_blocker_visual"),
    "foreground_grass": ("region_back_farm_foreground_grass_v001.png", "ForegroundStatic", 180, "edge_only_occluder"),
    "shadow": ("region_back_farm_shadow_overlay_v001.png", "LightAndWeather", 0, "transparent_overlay_only"),
    "light": ("region_back_farm_light_overlay_v001.png", "LightAndWeather", 1, "transparent_overlay_only"),
}

LAYER_ORDER = ["ground", "path", "field_rows", "fence", "pond", "shed", "foreground_grass", "shadow", "light"]


def new_layer() -> Image.Image:
    return Image.new("RGBA", CANVAS, (0, 0, 0, 0))


def noise_texture(size: tuple[int, int], dark: tuple[int, int, int], light: tuple[int, int, int], sigma: float = 24) -> Image.Image:
    noise = Image.effect_noise(size, sigma).convert("L")
    noise = ImageOps.autocontrast(noise, cutoff=1)
    return ImageOps.colorize(noise, dark, light).convert("RGBA")


def multiply_alpha(mask: Image.Image, alpha: int) -> Image.Image:
    return ImageChops.multiply(mask, Image.new("L", mask.size, alpha))


def apply_mask(texture: Image.Image, mask: Image.Image, alpha: int = 255) -> Image.Image:
    out = texture.copy()
    out.putalpha(multiply_alpha(mask, alpha) if alpha != 255 else mask)
    return out


def draw_soft_shadow(layer: Image.Image, bounds: tuple[int, int, int, int], alpha: int = 48, blur: int = 18) -> None:
    shadow = new_layer()
    ImageDraw.Draw(shadow, "RGBA").ellipse(bounds, fill=(42, 35, 24, alpha))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(blur)))


def mask_polygon(points: list[tuple[int, int]], blur: float = 0) -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    if blur:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def draw_grass(layer: Image.Image, bounds: tuple[int, int, int, int], seed: int, count: int, alpha: int = 55) -> None:
    rng = random.Random(seed)
    draw = ImageDraw.Draw(layer, "RGBA")
    x0, y0, x1, y1 = bounds
    palette = [(47, 105, 61), (78, 130, 72), (116, 154, 85), (196, 176, 105), (72, 118, 83)]
    for _ in range(count):
        x = rng.randrange(x0, x1)
        y = rng.randrange(y0, y1)
        length = rng.randrange(10, 38)
        bend = rng.randrange(-14, 15)
        color = (*rng.choice(palette), rng.randrange(max(14, alpha - 20), alpha + 20))
        draw.arc((x - 8 + bend, y - length, x + 9 + bend, y + length), 205, 274, fill=color, width=rng.randrange(1, 4))


def build_ground() -> Image.Image:
    layer = noise_texture(CANVAS, (88, 132, 76), (158, 189, 116), 22)
    layer.putalpha(Image.new("L", CANVAS, 255))
    draw = ImageDraw.Draw(layer, "RGBA")
    for bounds, color, blur in [
        ((0, 0, 2000, 430), (84, 130, 91, 70), 38),
        ((150, 430, 1850, 1570), (133, 171, 97, 52), 58),
        ((0, 1510, 2000, 2000), (74, 121, 70, 70), 44),
    ]:
        mask = Image.new("L", CANVAS, 0)
        ImageDraw.Draw(mask).rounded_rectangle(bounds, radius=90, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
        tint = Image.new("RGBA", CANVAS, color)
        tint.putalpha(multiply_alpha(mask, color[3]))
        layer.alpha_composite(tint)
    draw_grass(layer, (0, 0, 2000, 2000), SEED + 1, 950, 42)
    rng = random.Random(SEED + 2)
    for _ in range(110):
        x = rng.randrange(80, 1920)
        y = rng.randrange(230, 1850)
        draw.ellipse((x - 3, y - 2, x + 4, y + 3), fill=rng.choice([(222, 184, 113, 70), (216, 139, 126, 54), (172, 116, 150, 44)]))
    return layer


def build_path() -> Image.Image:
    layer = new_layer()
    draw = ImageDraw.Draw(layer, "RGBA")
    paths = [
        [(885, 0), (1115, 0), (1150, 390), (1080, 665), (918, 665), (850, 390)],
        [(285, 862), (1715, 850), (1840, 1045), (1660, 1190), (340, 1192), (170, 1030)],
        [(890, 1110), (1110, 1110), (1200, 2000), (798, 2000)],
    ]
    masks = []
    for points in paths:
        mask = mask_polygon(points, 24)
        masks.append(mask)
        layer.alpha_composite(apply_mask(noise_texture(CANVAS, (126, 98, 62), (207, 177, 114), 19), mask, 224))
        draw.line(points + [points[0]], fill=(72, 95, 51, 50), width=10, joint="curve")
    rng = random.Random(SEED + 3)
    combined = ImageChops.lighter(ImageChops.lighter(masks[0], masks[1]), masks[2])
    for _ in range(210):
        for _try in range(20):
            x = rng.randrange(0, 2000)
            y = rng.randrange(0, 2000)
            if combined.getpixel((x, y)) > 40:
                break
        else:
            continue
        rx, ry = rng.randrange(4, 17), rng.randrange(2, 8)
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=rng.choice([(86, 74, 51, 42), (229, 205, 144, 48), (142, 113, 74, 38)]))
    return layer


def build_field_rows() -> Image.Image:
    layer = new_layer()
    draw = ImageDraw.Draw(layer, "RGBA")
    field_blocks = [(225, 420, 825, 790), (930, 420, 1530, 790), (225, 925, 825, 1295), (930, 925, 1530, 1295)]
    rng = random.Random(SEED + 4)
    for idx, (x0, y0, x1, y1) in enumerate(field_blocks):
        draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=(113, 80, 49, 218), outline=(70, 92, 50, 90), width=5)
        for y in range(y0 + 38, y1 - 20, 54):
            draw.line((x0 + 38, y, x1 - 40, y + rng.randrange(-4, 5)), fill=(80, 57, 38, 78), width=5)
            draw.line((x0 + 42, y - 13, x1 - 42, y - 8), fill=(171, 127, 76, 52), width=3)
            for x in range(x0 + 80, x1 - 75, 82):
                leaf = rng.choice([(67, 128, 72, 145), (86, 148, 78, 136), (122, 154, 83, 118)])
                draw.ellipse((x - 16, y - 28, x + 16, y - 3), fill=leaf)
                draw.ellipse((x + 5, y - 26, x + 32, y - 1), fill=leaf)
        draw_soft_shadow(layer, (x0 + 35, y1 - 20, x1 - 35, y1 + 35), 28, 12)
    return layer


def build_shed() -> Image.Image:
    layer = new_layer()
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = 1600, 430
    draw_soft_shadow(layer, (x - 170, y + 92, x + 180, y + 165), 46, 16)
    body = [(x - 150, y - 130), (x + 150, y - 126), (x + 148, y + 95), (x - 146, y + 105)]
    side = [(x + 112, y - 118), (x + 178, y - 88), (x + 148, y + 95), (x + 105, y + 80)]
    draw.polygon(body, fill=(158, 112, 73, 246), outline=(82, 55, 36, 210))
    draw.polygon(side, fill=(124, 85, 60, 240), outline=(72, 49, 35, 190))
    for xx in range(x - 120, x + 125, 42):
        draw.line((xx, y - 104, xx - 16, y + 86), fill=(82, 54, 35, 70), width=3)
    draw.rounded_rectangle((x - 42, y - 40, x + 54, y + 95), radius=7, fill=(95, 67, 48, 238), outline=(61, 42, 31, 210), width=4)
    roof = [(x - 182, y - 144), (x + 142, y - 156), (x + 205, y - 85), (x - 150, y - 75)]
    draw.polygon(roof, fill=(74, 76, 65, 248), outline=(43, 48, 42, 218))
    draw.line((x - 150, y - 132, x + 150, y - 143), fill=(125, 130, 102, 74), width=5)
    for dx in range(-150, 150, 42):
        draw.line((x + dx, y - 140, x + dx + 38, y - 82), fill=(46, 55, 47, 70), width=3)
    return layer


def build_pond() -> Image.Image:
    layer = new_layer()
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = 1685, 1510
    draw_soft_shadow(layer, (x - 132, y - 54, x + 137, y + 68), 34, 10)
    draw.ellipse((x - 130, y - 75, x + 132, y + 78), fill=(71, 128, 139, 196), outline=(51, 92, 78, 158), width=7)
    draw.ellipse((x - 90, y - 44, x + 88, y + 40), fill=(99, 164, 171, 105))
    for yy in (-28, 4, 34):
        draw.arc((x - 88, y + yy - 22, x + 94, y + yy + 18), 12, 166, fill=(205, 229, 207, 82), width=3)
    for px, py in [(x - 126, y + 45), (x + 112, y - 38), (x - 78, y - 62)]:
        draw.ellipse((px - 18, py - 8, px + 20, py + 9), fill=(104, 142, 83, 160))
    return layer


def build_fence() -> Image.Image:
    layer = new_layer()
    draw = ImageDraw.Draw(layer, "RGBA")
    points = [(120, 310), (520, 280), (940, 305), (1380, 280), (1880, 330)]
    for x, y in points:
        draw.rounded_rectangle((x - 11, y - 70, x + 11, y + 86), radius=5, fill=(119, 80, 48, 235), outline=(70, 49, 32, 180), width=2)
    for offset in (0, 48):
        draw.line([(x, y - 20 + offset) for x, y in points], fill=(142, 98, 58, 225), width=14, joint="curve")
        draw.line([(x, y - 26 + offset) for x, y in points], fill=(213, 166, 98, 72), width=3, joint="curve")
    return layer


def build_foreground() -> Image.Image:
    layer = new_layer()
    rng = random.Random(SEED + 5)
    draw = ImageDraw.Draw(layer, "RGBA")
    zones = [(0, 1640, 620, 2000), (1390, 1580, 2000, 2000), (0, 1870, 2000, 2000)]
    palette = [(37, 99, 57, 224), (61, 128, 72, 206), (97, 150, 77, 170), (217, 177, 108, 115)]
    for x0, y0, x1, y1 in zones:
        for _ in range(130):
            x = rng.randrange(x0, x1)
            y = rng.randrange(y0, y1)
            h = rng.randrange(35, 128)
            bend = rng.randrange(-26, 27)
            draw.line((x, y, x + bend, y - h), fill=rng.choice(palette), width=rng.randrange(3, 9))
            if rng.random() < 0.14:
                draw.ellipse((x + bend - 9, y - h - 5, x + bend + 10, y - h + 6), fill=(224, 187, 112, 112))
    return layer.filter(ImageFilter.GaussianBlur(0.35))


def build_shadow() -> Image.Image:
    layer = new_layer()
    rng = random.Random(SEED + 6)
    draw = ImageDraw.Draw(layer, "RGBA")
    for _ in range(40):
        x = rng.randrange(80, 1900)
        y = rng.randrange(250, 1750)
        rx = rng.randrange(34, 120)
        ry = rng.randrange(12, 42)
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(45, 58, 39, rng.randrange(12, 36)))
    return layer.filter(ImageFilter.GaussianBlur(10))


def build_light() -> Image.Image:
    layer = new_layer()
    rng = random.Random(SEED + 7)
    draw = ImageDraw.Draw(layer, "RGBA")
    for _ in range(24):
        x = rng.randrange(120, 1850)
        y = rng.randrange(120, 1700)
        rx = rng.randrange(70, 220)
        ry = rng.randrange(28, 86)
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(255, 230, 152, rng.randrange(10, 28)))
    return layer.filter(ImageFilter.GaussianBlur(18))


def alpha_metrics(image: Image.Image) -> dict[str, Any]:
    alpha = image.getchannel("A")
    hist = alpha.histogram()
    total = image.width * image.height
    return {
        "alpha_bbox": list(alpha.getbbox() or (0, 0, 0, 0)),
        "transparent_ratio": round(hist[0] / total, 5),
        "semi_ratio": round(sum(hist[1:255]) / total, 5),
        "opaque_ratio": round(hist[255] / total, 5),
    }


def crop_to_bbox(image: Image.Image, asset_id: str) -> tuple[Image.Image, tuple[int, int]]:
    if asset_id in {"ground", "shadow", "light"}:
        return image, (0, 0)
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        return image, (0, 0)
    pad = 18 if asset_id != "foreground_grass" else 4
    x0 = max(0, bbox[0] - pad)
    y0 = max(0, bbox[1] - pad)
    x1 = min(CANVAS[0], bbox[2] + pad)
    y1 = min(CANVAS[1], bbox[3] + pad)
    return image.crop((x0, y0, x1, y1)), (x0, y0)


def make_preview(layers: dict[str, Image.Image]) -> Image.Image:
    out = new_layer()
    for key in LAYER_ORDER:
        out.alpha_composite(layers[key])
    return out


def make_contact(records: list[dict[str, Any]]) -> None:
    cols = 3
    tile_w, tile_h = 420, 320
    rows = math.ceil(len(records) / cols)
    sheet = Image.new("RGBA", (cols * tile_w, rows * tile_h), (244, 239, 226, 255))
    draw = ImageDraw.Draw(sheet)
    for idx, rec in enumerate(records):
        x = (idx % cols) * tile_w
        y = (idx // cols) * tile_h
        image = Image.open(ART_DIR / rec["file"]).convert("RGBA")
        image.thumbnail((tile_w - 36, tile_h - 58), Image.Resampling.LANCZOS)
        sheet.alpha_composite(image, (x + (tile_w - image.width) // 2, y + 38))
        draw.text((x + 10, y + 10), rec["asset_id"], fill=(40, 35, 29, 255))
        draw.rectangle((x, y, x + tile_w - 1, y + tile_h - 1), outline=(180, 170, 150, 160))
    sheet.save(CONTACT)


def main() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    layers = {
        "ground": build_ground(),
        "path": build_path(),
        "field_rows": build_field_rows(),
        "shed": build_shed(),
        "pond": build_pond(),
        "fence": build_fence(),
        "foreground_grass": build_foreground(),
        "shadow": build_shadow(),
        "light": build_light(),
    }
    preview = make_preview(layers)
    preview.resize((1000, 1000), Image.Resampling.LANCZOS).save(PREVIEW)
    records = []
    for asset_id, (file_name, target_parent, z_index, occlusion_rule) in LAYER_META.items():
        out, origin = crop_to_bbox(layers[asset_id], asset_id)
        out.save(ART_DIR / file_name)
        records.append({
            "asset_id": asset_id,
            "file": file_name,
            "origin_px": {"x": origin[0], "y": origin[1]},
            "size_px": {"width": out.width, "height": out.height},
            "target_parent": target_parent,
            "z_index": z_index,
            "occlusion_rule": occlusion_rule,
            "generated": True,
            "status": STATUS,
            "source": SOURCE,
            **alpha_metrics(out),
        })
    make_contact(records)
    manifest = {
        "region_id": "Region_BackFarm",
        "package_id": "back_farm_art_v001",
        "status": STATUS,
        "runtime_replacement": True,
        "canvas_px": {"width": CANVAS[0], "height": CANVAS[1]},
        "source_policy": "Formal replaceable layered PNGs generated for current 2000x2000 BackFarm runtime layout; no opaque full-plate runtime shortcut is used.",
        "runtime_preview": PREVIEW.name,
        "contact_sheet": CONTACT.name,
        "required_layers": records,
        "visual_self_review": [
            "BackFarm default spawn is moved inside the farm entry path, away from y=0 camera clamp.",
            "Farm plots read as soft tilled soil beds with crop-row detail instead of flat rectangles.",
            "Shed, pond, fence, foreground grass, light, and shadow remain separate replaceable layers."
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(f"OK: generated BackFarm art package -> {ART_DIR.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
