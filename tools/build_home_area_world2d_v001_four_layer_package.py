from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "production" / "assets" / "regions" / "home_area_world2d" / "v001"
SOURCE_DIR = PKG / "02_source_generation"
EXPORT_DIR = PKG / "03_layer_export"
FOUR_DIR = EXPORT_DIR / "four_layer_package"

SOURCE = SOURCE_DIR / "source_full.png"


def poly_mask(size: tuple[int, int], points: list[tuple[int, int]], blur: float = 0.0) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(points, fill=255)
    if blur > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def ellipse_mask(size: tuple[int, int], bbox: tuple[int, int, int, int], blur: float = 0.0) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(bbox, fill=255)
    if blur > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def rect_mask(size: tuple[int, int], bbox: tuple[int, int, int, int], blur: float = 0.0) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle(bbox, fill=255)
    if blur > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def union(size: tuple[int, int], masks: list[Image.Image]) -> Image.Image:
    result = Image.new("L", size, 0)
    for mask in masks:
        result = ImageChops.lighter(result, mask)
    return result


def subtract(mask: Image.Image, remove: Image.Image) -> Image.Image:
    return ImageChops.subtract(mask, remove)


def vegetation_alpha(source: Image.Image, broad: Image.Image) -> Image.Image:
    """Create a perforated alpha mask for leaves/grass inside broad art-director masks."""

    rgb = source.convert("RGB")
    pix = rgb.load()
    broad_px = broad.load()
    refined = Image.new("L", source.size, 0)
    out = refined.load()
    width, height = source.size

    for y in range(height):
        for x in range(width):
            alpha = broad_px[x, y]
            if alpha == 0:
                continue
            r, g, b = pix[x, y]
            # Keep vegetation-like pixels and let sky/ground/dirt gaps remain transparent.
            green_bias = g - max(r, b)
            warm_leaf = (r + g) - (2 * b)
            dark_leaf = g > 34 and r > 24 and b < 142
            if (green_bias > 5 and dark_leaf) or (warm_leaf > 52 and g > 50 and b < 150):
                out[x, y] = alpha

    refined = refined.filter(ImageFilter.MaxFilter(3))
    refined = refined.filter(ImageFilter.GaussianBlur(0.65))
    return refined


def extract(source: Image.Image, mask: Image.Image, out_path: Path) -> None:
    rgba = source.convert("RGBA")
    alpha = Image.composite(mask, Image.new("L", source.size, 0), mask)
    rgba.putalpha(alpha)
    rgba.save(out_path)


def is_ground_or_road(r: int, g: int, b: int) -> bool:
    # Dirt paths: warm ochre, lower green bias.
    dirt = r > 105 and g > 82 and b < 115 and r >= g - 14
    # Grass: muted green/yellow-green.
    grass = g > 58 and r > 45 and b < 130 and g >= b + 16
    # Very dark grassy shadow, but avoid trunks/roof by requiring green/yellow bias.
    shadow_grass = g > 38 and b < 92 and (g + r) > (2 * b + 42)
    return dirt or grass or shadow_grass


def synthesize_ground_base(source: Image.Image, removal_mask: Image.Image) -> Image.Image:
    """Paint a same-canvas base where non-ground structures are replaced by grass/road texture."""

    rgb = source.convert("RGB")
    width, height = source.size
    src = rgb.load()
    remove = removal_mask.load()
    rng = random.Random(190519)

    bands: dict[int, list[tuple[int, int, tuple[int, int, int]]]] = {}
    for y in range(height):
        band = y // 36
        row = bands.setdefault(band, [])
        for x in range(width):
            if remove[x, y] > 0:
                continue
            r, g, b = src[x, y]
            if is_ground_or_road(r, g, b):
                row.append((x, y, (r, g, b)))

    all_samples = [item for row in bands.values() for item in row]
    if not all_samples:
        raise RuntimeError("No ground samples found for base synthesis.")

    out = rgb.copy()
    out_px = out.load()

    for y in range(height):
        band = y // 36
        samples: list[tuple[int, int, tuple[int, int, int]]] = []
        for bidx in range(band - 2, band + 3):
            samples.extend(bands.get(bidx, []))
        if not samples:
            samples = all_samples

        for x in range(width):
            if remove[x, y] == 0:
                continue
            # Prefer nearby source texture from the same vertical band.
            candidates = samples
            sx, sy, color = min(
                (rng.choice(candidates) for _ in range(10)),
                key=lambda item: abs(item[0] - x) + 1.8 * abs(item[1] - y),
            )
            r, g, b = color
            jitter = rng.randint(-8, 8)
            out_px[x, y] = (
                max(0, min(255, r + jitter)),
                max(0, min(255, g + jitter)),
                max(0, min(255, b + jitter)),
            )

    # Smooth only the painted areas, then feather transitions back to original ground.
    smoothed = out.filter(ImageFilter.GaussianBlur(1.25))
    feather = removal_mask.filter(ImageFilter.GaussianBlur(2.2))
    out = Image.composite(smoothed, rgb, feather)

    # A mild global texture pass keeps the base from looking flat after large fills.
    texture = out.filter(ImageFilter.UnsharpMask(radius=1.0, percent=70, threshold=4))
    out = Image.blend(out, texture, 0.28)
    return out.convert("RGBA")


def save_contact_sheet(items: list[tuple[str, Path]], out_path: Path) -> None:
    thumb_w, thumb_h = 430, 313
    cols = 2
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 36)), (30, 34, 28))
    draw = ImageDraw.Draw(sheet)

    for i, (label, path) in enumerate(items):
        img = Image.open(path).convert("RGBA")
        checker = Image.new("RGBA", img.size, (54, 56, 50, 255))
        cd = ImageDraw.Draw(checker)
        step = 32
        for y0 in range(0, img.height, step):
            for x0 in range(0, img.width, step):
                if (x0 // step + y0 // step) % 2 == 0:
                    cd.rectangle([x0, y0, x0 + step - 1, y0 + step - 1], fill=(86, 91, 78, 255))
        comp = Image.alpha_composite(checker, img)
        comp.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (i % cols) * thumb_w
        y = (i // cols) * (thumb_h + 36)
        sheet.paste(comp.convert("RGB"), (x + (thumb_w - comp.width) // 2, y))
        draw.text((x + 10, y + thumb_h + 10), label, fill=(238, 232, 202))

    sheet.save(out_path)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

    FOUR_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    size = source.size
    width, height = size

    # Broad structure masks, authored in accepted source coordinates.
    left_canopy_broad = union(
        size,
        [
            poly_mask(size, [(0, 0), (590, 0), (585, 105), (515, 185), (445, 285), (380, 390), (290, 495), (150, 500), (0, 420)], 1.2),
            ellipse_mask(size, (0, 55, 275, 330), 1.0),
            ellipse_mask(size, (120, 0, 470, 230), 1.0),
        ],
    )
    right_canopy_broad = union(
        size,
        [
            poly_mask(size, [(850, 0), (1245, 0), (1325, 110), (1275, 290), (1165, 435), (1020, 455), (890, 385), (820, 210)], 1.2),
            ellipse_mask(size, (910, 40, 1215, 365), 1.0),
        ],
    )
    bottom_foreground_broad = union(
        size,
        [
            poly_mask(size, [(0, 595), (130, 575), (320, 650), (520, 775), (800, 920), (900, 1070), (0, 1070)], 1.0),
            poly_mask(size, [(1150, 535), (1470, 470), (1470, 1070), (1065, 1070), (955, 900), (1050, 690)], 1.0),
            ellipse_mask(size, (1160, 730, 1505, 1095), 1.0),
            ellipse_mask(size, (-50, 735, 330, 1105), 1.0),
        ],
    )
    roof_foreground = poly_mask(size, [(500, 85), (905, 75), (940, 255), (910, 325), (500, 318), (475, 245)], 0.8)

    foreground_vegetation = union(
        size,
        [
            vegetation_alpha(source, left_canopy_broad),
            vegetation_alpha(source, right_canopy_broad),
            vegetation_alpha(source, bottom_foreground_broad),
        ],
    )
    foreground_mask = union(size, [foreground_vegetation, roof_foreground])

    # Midground is behind the player: house body, trunks, props, fences, well, sign.
    house_body = poly_mask(size, [(490, 245), (910, 245), (910, 415), (520, 425), (485, 310)], 0.7)
    left_trunk = poly_mask(size, [(70, 250), (235, 230), (295, 350), (270, 560), (175, 595), (85, 535), (35, 410)], 0.8)
    right_trunk = poly_mask(size, [(995, 300), (1110, 300), (1140, 520), (1060, 565), (990, 515)], 0.8)
    bench = poly_mask(size, [(185, 450), (350, 425), (390, 520), (270, 585), (175, 555)], 0.8)
    well = ellipse_mask(size, (990, 550, 1120, 735), 0.8)
    mailbox = rect_mask(size, (470, 360, 545, 455), 0.8)
    road_sign = poly_mask(size, [(1130, 745), (1255, 765), (1245, 925), (1160, 920)], 0.8)
    front_props = union(
        size,
        [
            rect_mask(size, (395, 285, 520, 430), 0.8),
            rect_mask(size, (610, 300, 670, 395), 0.8),
            rect_mask(size, (760, 300, 825, 395), 0.8),
            rect_mask(size, (845, 300, 930, 410), 0.8),
        ],
    )
    fences = union(
        size,
        [
            poly_mask(size, [(170, 390), (405, 330), (415, 390), (185, 460)], 0.8),
            poly_mask(size, [(1170, 155), (1470, 120), (1470, 250), (1160, 270)], 0.8),
            poly_mask(size, [(1120, 315), (1325, 250), (1335, 340), (1135, 410)], 0.8),
        ],
    )

    midground_mask = subtract(
        union(size, [house_body, left_trunk, right_trunk, bench, well, mailbox, road_sign, front_props, fences]),
        foreground_mask,
    )

    # Base removes both foreground and midground, plus decorative border clusters, leaving grass/roads.
    decorative_clusters = union(
        size,
        [
            ellipse_mask(size, (0, 690, 330, 1065), 1.0),
            ellipse_mask(size, (1180, 650, 1510, 1075), 1.0),
            ellipse_mask(size, (1100, 345, 1310, 560), 1.0),
            ellipse_mask(size, (340, 225, 445, 360), 1.0),
        ],
    )
    removal_mask = union(size, [foreground_mask, midground_mask, decorative_clusters]).filter(ImageFilter.MaxFilter(9))

    source_out = FOUR_DIR / "home_area_01_source.png"
    base_out = FOUR_DIR / "home_area_02_base_ground_paths.png"
    foreground_out = FOUR_DIR / "home_area_03_foreground_occlusion.png"
    midground_out = FOUR_DIR / "home_area_04_midground_behind_player.png"

    source.save(source_out)
    synthesize_ground_base(source, removal_mask).save(base_out)
    extract(source, foreground_mask, foreground_out)
    extract(source, midground_mask, midground_out)

    manifest = {
        "package_id": "home_area_world2d_v001_four_layer_package",
        "status": "four_same_canvas_layers_exported",
        "canvas": {"width": width, "height": height},
        "coordinate_origin": "top_left_source_full",
        "rules": [
            "all four images have identical canvas size",
            "base contains grass and roads only as a paint/inpaint base pass",
            "foreground uses alpha and perforated vegetation masks so shrub gaps stay transparent",
            "midground is transparent and should render behind the player",
            "gameplay blockers/interactions are still authored later from approved visible structure",
        ],
        "layers": [
            {"id": "source", "path": str(source_out.relative_to(ROOT)).replace("\\", "/"), "alpha": "opaque"},
            {"id": "base_ground_paths", "path": str(base_out.relative_to(ROOT)).replace("\\", "/"), "alpha": "opaque"},
            {"id": "foreground_occlusion", "path": str(foreground_out.relative_to(ROOT)).replace("\\", "/"), "alpha": "transparent"},
            {"id": "midground_behind_player", "path": str(midground_out.relative_to(ROOT)).replace("\\", "/"), "alpha": "transparent"},
        ],
        "known_limits": [
            "base_ground_paths is deterministic inpaint from the accepted source, not a hand-painted PSD layer",
            "foreground and midground masks are first-pass authored masks and may need human edge cleanup",
        ],
    }
    write_json(FOUR_DIR / "four_layer_manifest.json", manifest)

    save_contact_sheet(
        [
            ("01 source", source_out),
            ("02 base: grass + roads", base_out),
            ("03 foreground occlusion alpha", foreground_out),
            ("04 midground behind player alpha", midground_out),
        ],
        FOUR_DIR / "four_layer_contact_sheet.png",
    )

    # Replace the old formal export manifest pointer with this four-layer contract.
    write_json(EXPORT_DIR / "layer_export_manifest.json", manifest)

    print(f"Built four-layer HomeArea package at {FOUR_DIR} ({width}x{height}).")


if __name__ == "__main__":
    main()
