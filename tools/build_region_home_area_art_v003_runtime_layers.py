from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
V001_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v001"
V002_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v002"
V003_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v003"
V001_MANIFEST = V001_DIR / "region_home_area_art_v001_manifest.json"
V002_MANIFEST = V002_DIR / "region_home_area_art_v002_manifest.json"
V003_MANIFEST = V003_DIR / "region_home_area_art_v003_manifest.json"
BASE_V002 = V002_DIR / "region_home_area_base_full_v002.png"
BASE_V003 = V003_DIR / "region_home_area_base_full_v003.png"
PREVIEW = V003_DIR / "region_home_area_art_v003_runtime_preview.png"
CONTACT = V003_DIR / "region_home_area_art_v003_layer_contact_sheet.png"
PROMPT = V003_DIR / "region_home_area_art_v003_prompt.md"
CAT_BED_PRODUCTION = ROOT / "production" / "assets" / "final_art" / "home_area" / "props" / "region_home_area_prop_cat_bed_v001.png"
CAT_BED_RUNTIME = ROOT / "assets" / "art" / "props" / "region_home_area_prop_cat_bed_v001.png"

CANVAS = (6144, 4096)
PREVIEW_SIZE = (1536, 1024)

LAYER_ORDER = [
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

OVERLAY_LAYERS = {"shadow_dappled", "light_overlay"}
SOFT_MASK_SETTINGS = {
    "path_village_road": (14, 7.0),
    "path_back_farm": (14, 7.0),
    "veranda_floor": (10, 5.0),
    "house_roof_occluder": (10, 3.0),
    "tree_left_canopy_occluder": (10, 3.0),
    "tree_right_canopy_occluder": (10, 3.0),
    "house_body": (6, 2.0),
    "tree_left_trunk": (5, 1.5),
    "tree_right_trunk": (5, 1.5),
}


@dataclass(frozen=True)
class LayerRecord:
    asset_id: str
    source_file: str
    output_file: str
    origin: tuple[int, int]
    size: tuple[int, int]
    target_parent: str
    z_index: int
    anchor: tuple[int, int]
    role: str
    integration_note: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_rgba(path: Path) -> Image.Image:
    require(path.exists(), f"missing image: {path}")
    with Image.open(path) as image:
        return image.convert("RGBA")


def load_v001_records() -> list[LayerRecord]:
    manifest = json.loads(V001_MANIFEST.read_text(encoding="utf-8"))
    records: list[LayerRecord] = []
    for item in manifest["assets"]:
        asset_id = item["asset_id"]
        if asset_id == "base_full":
            continue
        source_file = item["file"]
        records.append(
            LayerRecord(
                asset_id=asset_id,
                source_file=source_file,
                output_file=source_file.replace("_v001.png", "_v003.png"),
                origin=(int(item["origin_px"]["x"]), int(item["origin_px"]["y"])),
                size=(int(item["size_px"]["width"]), int(item["size_px"]["height"])),
                target_parent=item["target_parent"],
                z_index=int(item["z_index"]),
                anchor=(int(item["anchor_px"]["x"]), int(item["anchor_px"]["y"])),
                role=item["role"],
                integration_note=item["integration_note"],
            )
        )
    return records


def full_canvas_alpha_from_v001(record: LayerRecord, grow: int, blur: float) -> Image.Image:
    source = load_rgba(V001_DIR / record.source_file)
    alpha_core = source.getchannel("A")
    alpha_grown = alpha_core.copy()
    for _ in range(max(0, grow)):
        alpha_grown = alpha_grown.filter(ImageFilter.MaxFilter(3))
    full_core = Image.new("L", CANVAS, 0)
    full_core.paste(alpha_core, record.origin)
    full_edge = Image.new("L", CANVAS, 0)
    full_edge.paste(alpha_grown, record.origin)
    if blur > 0:
        full_edge = full_edge.filter(ImageFilter.GaussianBlur(blur))
    return ImageChops.lighter(full_core, full_edge)


def make_overlay_mask(record: LayerRecord) -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    draw = ImageDraw.Draw(mask)
    if record.asset_id == "shadow_dappled":
        for bounds in (
            (700, 780, 2320, 1720),
            (2220, 1300, 4300, 2200),
            (3880, 1220, 5460, 2520),
            (520, 2380, 5200, 3400),
        ):
            draw.ellipse(bounds, fill=76)
        return mask.filter(ImageFilter.GaussianBlur(30))
    if record.asset_id == "light_overlay":
        for bounds in (
            (560, 560, 2620, 1480),
            (2200, 1120, 4500, 2380),
            (3380, 1960, 5600, 3320),
        ):
            draw.ellipse(bounds, fill=52)
        return mask.filter(ImageFilter.GaussianBlur(36))
    raise ValueError(record.asset_id)


def make_foreground_mask() -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(
        [
            (0, 3240),
            (780, 3060),
            (1600, 3240),
            (2820, 3470),
            (4180, 3290),
            (6144, 3070),
            (6144, 4096),
            (0, 4096),
        ],
        fill=222,
    )
    draw.polygon([(0, 2190), (420, 2100), (680, 4096), (0, 4096)], fill=176)
    draw.polygon([(5790, 2040), (6144, 1960), (6144, 4096), (5480, 4096)], fill=176)
    return mask.filter(ImageFilter.GaussianBlur(20))


def extract_layer(base: Image.Image, record: LayerRecord, mask: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    layer.alpha_composite(base)
    layer.putalpha(mask)
    x, y = record.origin
    w, h = record.size
    return layer.crop((x, y, x + w, y + h))


def fade_edges(image: Image.Image, bottom: int = 0, left: int = 0, right: int = 0) -> Image.Image:
    output = image.copy()
    alpha = output.getchannel("A")
    pixels = alpha.load()
    width, height = output.size
    for y in range(height):
        bottom_factor = 1.0
        if bottom > 0 and y >= height - bottom:
            bottom_factor = max(0.0, (height - 1 - y) / float(bottom))
        for x in range(width):
            factor = bottom_factor
            if left > 0 and x < left:
                factor = min(factor, x / float(left))
            if right > 0 and x >= width - right:
                factor = min(factor, (width - 1 - x) / float(right))
            if factor < 1.0:
                pixels[x, y] = int(pixels[x, y] * factor)
    output.putalpha(alpha)
    return output


def alpha_bbox(image: Image.Image) -> list[int] | None:
    bbox = image.getchannel("A").getbbox()
    return list(bbox) if bbox else None


def make_runtime_preview(records: list[LayerRecord]) -> None:
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    by_id = {record.asset_id: record for record in records}
    for asset_id in LAYER_ORDER:
        record = by_id[asset_id]
        image = load_rgba(V003_DIR / record.output_file)
        canvas.alpha_composite(image, record.origin)
    canvas.resize(PREVIEW_SIZE, Image.Resampling.LANCZOS).save(PREVIEW)


def make_contact_sheet(records: list[LayerRecord]) -> None:
    tile_w, tile_h = 512, 384
    sheet = Image.new("RGBA", (tile_w * 4, tile_h * 4), (34, 42, 38, 255))
    draw = ImageDraw.Draw(sheet, "RGBA")
    for index, record in enumerate(records):
        image = load_rgba(V003_DIR / record.output_file)
        cell_x = (index % 4) * tile_w
        cell_y = (index // 4) * tile_h
        scale = min((tile_w - 48) / image.width, (tile_h - 82) / image.height, 1.0)
        resized = image.resize(
            (max(1, int(image.width * scale)), max(1, int(image.height * scale))),
            Image.Resampling.LANCZOS,
        )
        sheet.alpha_composite(
            resized,
            (cell_x + (tile_w - resized.width) // 2, cell_y + 38 + (tile_h - 82 - resized.height) // 2),
        )
        draw.text((cell_x + 18, cell_y + 14), record.asset_id, fill=(230, 236, 220, 255))
        draw.text((cell_x + 18, cell_y + tile_h - 32), f"origin {record.origin[0]},{record.origin[1]}", fill=(178, 190, 171, 255))
    sheet.save(CONTACT)


def draw_cat_bed(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 256, 192
    scale = 3
    image = Image.new("RGBA", (width * scale, height * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")

    def oval(bounds: tuple[int, int, int, int], fill: tuple[int, int, int, int], outline: tuple[int, int, int, int] | None = None, w: int = 1) -> None:
        b = tuple(int(v * scale) for v in bounds)
        draw.ellipse(b, fill=fill, outline=outline, width=max(1, int(w * scale)))

    def poly(points: list[tuple[int, int]], fill: tuple[int, int, int, int], outline: tuple[int, int, int, int] | None = None) -> None:
        pts = [(int(x * scale), int(y * scale)) for x, y in points]
        draw.polygon(pts, fill=fill)
        if outline:
            draw.line(pts + [pts[0]], fill=outline, width=2 * scale, joint="curve")

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow, "RGBA")
    shadow_draw.ellipse((44 * scale, 126 * scale, 218 * scale, 170 * scale), fill=(52, 38, 24, 56))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5 * scale))
    image.alpha_composite(shadow)

    poly([(46, 84), (66, 58), (190, 58), (212, 84), (226, 128), (204, 158), (54, 158), (30, 128)], (133, 89, 62, 255), (83, 55, 40, 230))
    oval((33, 66, 224, 162), (155, 104, 72, 255), (87, 58, 42, 240), 2)
    oval((54, 72, 202, 149), (211, 160, 132, 255), (131, 82, 61, 210), 2)
    oval((72, 86, 184, 138), (225, 181, 158, 255), None, 1)
    draw.arc((62 * scale, 76 * scale, 196 * scale, 150 * scale), 190, 350, fill=(110, 72, 53, 160), width=2 * scale)
    draw.arc((70 * scale, 82 * scale, 186 * scale, 142 * scale), 195, 345, fill=(244, 203, 180, 120), width=2 * scale)

    for i in range(18):
        x = 54 + (i * 9) % 140
        y = 66 + int(7 * math.sin(i * 1.7))
        draw.line((x * scale, y * scale, (x + 18) * scale, (y + 7) * scale), fill=(104, 67, 48, 54), width=scale)
    for i in range(26):
        x = 64 + (i * 17) % 126
        y = 89 + (i * 11) % 44
        oval((x, y, x + 2, y + 2), (244, 207, 184, 70), None, 1)

    image = image.filter(ImageFilter.GaussianBlur(0.35 * scale))
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    image.save(path)


def write_prompt() -> None:
    PROMPT.write_text(
        "# Region HomeArea Art v003\n\n"
        "Purpose: final-split runtime candidate derived from the approved v002 HomeArea mother plate. "
        "The v002 full plate stays review-only; runtime references use replaceable v003 PNG layers with softened alpha masks.\n\n"
        "Style: warm low-saturation countryside storybook, fixed 3/4 top-down, modular 2D, no combat motifs.\n",
        encoding="utf-8",
    )


def write_manifest(records: list[LayerRecord]) -> None:
    v002 = json.loads(V002_MANIFEST.read_text(encoding="utf-8"))
    assets: list[dict[str, Any]] = [
        {
            "asset_id": "source_v002_base_full",
            "file": BASE_V003.name,
            "origin_px": {"x": 0, "y": 0},
            "size_px": {"width": CANVAS[0], "height": CANVAS[1]},
            "anchor_px": {"x": 0, "y": 0},
            "target_parent": "art_review_only",
            "z_index": 0,
            "role": "Review-only copy of the v002 mother plate used to derive v003 layers.",
            "integration_note": "Do not wire this full plate into runtime.",
            "source": "copied_from_home_area_art_v002_base_full",
        }
    ]
    for record in records:
        image = load_rgba(V003_DIR / record.output_file)
        assets.append(
            {
                "asset_id": record.asset_id,
                "file": record.output_file,
                "origin_px": {"x": record.origin[0], "y": record.origin[1]},
                "size_px": {"width": record.size[0], "height": record.size[1]},
                "alpha_bbox": alpha_bbox(image),
                "anchor_px": {"x": record.anchor[0], "y": record.anchor[1]},
                "target_parent": record.target_parent,
                "z_index": record.z_index,
                "role": record.role,
                "integration_note": record.integration_note,
                "source": "v003_soft_split_from_v002_mother_plate_with_refined_v001_spatial_masks",
            }
        )
    cat_bed = load_rgba(CAT_BED_RUNTIME)
    assets.append(
        {
            "asset_id": "prop_cat_bed",
            "file": "assets/art/props/region_home_area_prop_cat_bed_v001.png",
            "size_px": {"width": cat_bed.width, "height": cat_bed.height},
            "alpha_bbox": alpha_bbox(cat_bed),
            "anchor_px": {"x": 128, "y": 162},
            "target_parent": "YSortWorld/Props/CatBed",
            "z_index": 0,
            "role": "Small cozy cat bed prop, runtime PNG replacement for the graybox cushion.",
            "integration_note": "Decorative runtime prop; no interaction area until pet behavior exists.",
            "source": "generated_vector_paint_runtime_prop",
        }
    )
    manifest = {
        "region_id": "Region_HomeArea",
        "package_id": "home_area_art_v003",
        "status": "final_split_runtime_candidate",
        "runtime_replacement": False,
        "layer_split_ready": True,
        "canvas_px": {"width": CANVAS[0], "height": CANVAS[1]},
        "design_contract": v002.get("design_contract", "production/assets/regions/home_area_design/region_home_area_layout_v001.json"),
        "source_package": "home_area_art_v002",
        "prompt_file": PROMPT.name,
        "split_method": "Softened v001 spatial masks over the v002 mother plate; path, veranda, roof, and tree occluder masks are feathered for runtime review.",
        "runtime_preview": PREVIEW.name,
        "contact_sheet": CONTACT.name,
        "assets": assets,
        "integration_gate": [
            "Runtime may reference v003 split layer files, not v002 or v003 full-scene review plates.",
            "Path and veranda layers must be visible and have softened alpha edges.",
            "Roof and canopy occluders must not hide the player feet in walkthrough screenshots.",
            "CatBed must use runtime PNG art or stay hidden; graybox cushion must not be visible.",
        ],
    }
    V003_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    require(BASE_V002.exists(), f"missing v002 base plate: {BASE_V002}")
    V003_DIR.mkdir(parents=True, exist_ok=True)
    CAT_BED_PRODUCTION.parent.mkdir(parents=True, exist_ok=True)
    CAT_BED_RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(BASE_V002, BASE_V003)
    base = load_rgba(BASE_V002)
    require(base.size == CANVAS, f"v002 base plate must be {CANVAS}, got {base.size}")
    records = load_v001_records()
    by_id = {record.asset_id: record for record in records}
    require(set(LAYER_ORDER) == set(by_id), "v001 and v003 layer contracts drifted")

    for record in records:
        if record.asset_id == "ground_yard":
            output = base.copy()
        elif record.asset_id in OVERLAY_LAYERS:
            output = extract_layer(base, record, make_overlay_mask(record))
        elif record.asset_id == "foreground_grass":
            output = extract_layer(base, record, make_foreground_mask())
        else:
            grow, blur = SOFT_MASK_SETTINGS.get(record.asset_id, (4, 1.0))
            mask = full_canvas_alpha_from_v001(record, grow=grow, blur=blur)
            output = extract_layer(base, record, mask)
            if record.asset_id == "house_body":
                output = fade_edges(output, bottom=150, left=34, right=34)
        output.save(V003_DIR / record.output_file)

    draw_cat_bed(CAT_BED_PRODUCTION)
    shutil.copyfile(CAT_BED_PRODUCTION, CAT_BED_RUNTIME)
    make_runtime_preview(records)
    make_contact_sheet(records)
    write_prompt()
    write_manifest(records)
    print(f"OK: generated {len(records)} Region_HomeArea art v003 runtime layer candidates")
    print(f"OK: generated CatBed runtime prop: {CAT_BED_RUNTIME.relative_to(ROOT).as_posix()}")
    print(f"OK: preview: {PREVIEW.relative_to(ROOT).as_posix()}")
    print(f"OK: manifest: {V003_MANIFEST.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
