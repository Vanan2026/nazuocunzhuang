from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "production" / "assets" / "regions" / "home_area_world2d" / "v001"
SOURCE_DIR = PKG / "02_source_generation"
LAYER_DIR = PKG / "03_layer_export"

SOURCE = SOURCE_DIR / "source_original_accepted.png"
SOURCE_FULL = SOURCE_DIR / "source_full.png"


def polygon_mask(size: tuple[int, int], points: list[tuple[int, int]], blur: float = 1.2) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(points, fill=255)
    if blur > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def combine_masks(size: tuple[int, int], masks: list[Image.Image]) -> Image.Image:
    result = Image.new("L", size, 0)
    for mask in masks:
        result = Image.composite(Image.new("L", size, 255), result, mask)
    return result


def extract_layer(source: Image.Image, mask: Image.Image, out_path: Path) -> None:
    rgba = source.convert("RGBA")
    _, _, _, alpha = rgba.split()
    combined_alpha = Image.composite(alpha, Image.new("L", source.size, 0), mask)
    rgba.putalpha(combined_alpha)
    rgba.save(out_path)


def vegetation_refine(source: Image.Image, broad_mask: Image.Image) -> Image.Image:
    """Keep leafy/grass pixels inside broad authoring polygons.

    This avoids rectangular foreground plates while preserving hand-painted edges.
    The thresholds are intentionally permissive for this accepted warm-green scene.
    """

    rgb = source.convert("RGB")
    pix = rgb.load()
    broad = broad_mask.load()
    refined = Image.new("L", source.size, 0)
    out = refined.load()
    width, height = source.size

    for y in range(height):
        for x in range(width):
            if broad[x, y] == 0:
                continue
            r, g, b = pix[x, y]
            green_bias = g - max(r, b)
            yellow_green = (g + r) - (2 * b)
            dark_leaf = g > 38 and r > 25 and b < 130
            if (green_bias > 6 and dark_leaf) or (yellow_green > 55 and g > 55 and b < 145):
                out[x, y] = broad[x, y]

    refined = refined.filter(ImageFilter.MaxFilter(5))
    refined = refined.filter(ImageFilter.GaussianBlur(0.8))
    return refined


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing accepted source: {SOURCE}")

    LAYER_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    width, height = source.size

    source.save(SOURCE_FULL)
    source.save(LAYER_DIR / "base_full_reference.png")

    # Authoring polygons are in accepted source coordinates: 1470x1070.
    # They intentionally hug visual structures instead of creating broad rectangles.
    left_tree_canopy_poly = [
        (0, 0), (585, 0), (570, 95), (520, 160), (465, 220), (430, 315),
        (360, 390), (290, 475), (215, 500), (120, 455), (0, 415),
    ]
    left_tree_trunk_poly = [
        (78, 260), (230, 235), (285, 340), (270, 560), (190, 585),
        (100, 545), (45, 430),
    ]
    right_tree_canopy_poly = [
        (875, 0), (1245, 0), (1315, 90), (1285, 230), (1220, 340),
        (1140, 430), (1015, 445), (905, 365), (850, 240), (835, 110),
    ]
    right_tree_trunk_poly = [
        (1000, 320), (1110, 305), (1135, 515), (1060, 555), (995, 515),
    ]
    house_roof_poly = [
        (500, 85), (900, 75), (935, 255), (905, 325), (505, 318),
        (475, 250),
    ]
    left_bottom_grass_poly = [
        (0, 610), (110, 575), (285, 640), (415, 760), (760, 880),
        (900, 1070), (0, 1070),
    ]
    right_bottom_grass_poly = [
        (1160, 560), (1470, 470), (1470, 1070), (1090, 1070),
        (965, 885), (1080, 680),
    ]

    left_canopy_mask = vegetation_refine(source, polygon_mask(source.size, left_tree_canopy_poly, 1.5))
    right_canopy_mask = vegetation_refine(source, polygon_mask(source.size, right_tree_canopy_poly, 1.5))
    near_grass_mask = vegetation_refine(
        source,
        combine_masks(
            source.size,
            [
                polygon_mask(source.size, left_bottom_grass_poly, 1.5),
                polygon_mask(source.size, right_bottom_grass_poly, 1.5),
            ],
        ),
    )

    left_trunk_mask = polygon_mask(source.size, left_tree_trunk_poly, 1.0)
    right_trunk_mask = polygon_mask(source.size, right_tree_trunk_poly, 1.0)
    roof_mask = polygon_mask(source.size, house_roof_poly, 1.0)

    ysort_structure_mask = combine_masks(source.size, [left_trunk_mask, right_trunk_mask])

    extract_layer(source, left_canopy_mask, LAYER_DIR / "foreground_tree_left.png")
    extract_layer(source, right_canopy_mask, LAYER_DIR / "foreground_tree_right.png")
    extract_layer(source, roof_mask, LAYER_DIR / "foreground_house_roof_eaves.png")
    extract_layer(source, near_grass_mask, LAYER_DIR / "foreground_near_grass.png")
    extract_layer(source, ysort_structure_mask, LAYER_DIR / "ysort_tree_trunks.png")

    write_json(
        LAYER_DIR / "props_pivot_manifest.json",
        {
            "canvas": {"width": width, "height": height},
            "coordinate_origin": "top_left_source_full",
            "status": "initial_authoring_targets_from_accepted_source",
            "props": [
                {"id": "mailbox", "pivot": [510, 430], "bbox": [475, 370, 535, 455], "interaction": "mailbox_later"},
                {"id": "well", "pivot": [1045, 690], "bbox": [1000, 560, 1115, 730], "interaction": "repair_or_inspect_later"},
                {"id": "bench", "pivot": [275, 555], "bbox": [190, 445, 370, 575], "interaction": "sit_or_inspect_later"},
                {"id": "road_sign", "pivot": [1190, 880], "bbox": [1130, 760, 1250, 910], "interaction": "travel_hint_later"},
                {"id": "front_door", "pivot": [720, 370], "bbox": [685, 275, 755, 390], "interaction": "enter_home_later"},
            ],
        },
    )

    write_json(
        LAYER_DIR / "layer_export_manifest.json",
        {
            "package_id": "home_area_world2d_v001_layer_export",
            "status": "initial_layers_from_user_accepted_source",
            "source_full": str(SOURCE_FULL.relative_to(ROOT)).replace("\\", "/"),
            "canvas": {"width": width, "height": height},
            "coordinate_origin": "top_left_source_full",
            "base": {
                "id": "base_full_reference",
                "path": str((LAYER_DIR / "base_full_reference.png").relative_to(ROOT)).replace("\\", "/"),
                "note": "Accepted source copied as base reference. A true base_clean paint pass is still required if foreground pixels must be removed from the base.",
            },
            "layers": [
                "foreground_tree_left.png",
                "foreground_tree_right.png",
                "foreground_house_roof_eaves.png",
                "foreground_near_grass.png",
                "ysort_tree_trunks.png",
                "props_pivot_manifest.json",
            ],
        },
    )

    print(f"Built HomeArea World2D v001 initial layers from {SOURCE.name} ({width}x{height}).")


if __name__ == "__main__":
    main()
