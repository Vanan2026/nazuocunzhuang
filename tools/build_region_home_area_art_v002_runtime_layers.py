from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
V001_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v001"
V002_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v002"
V001_MANIFEST = V001_DIR / "region_home_area_art_v001_manifest.json"
V002_MANIFEST = V002_DIR / "region_home_area_art_v002_manifest.json"
BASE_FULL = V002_DIR / "region_home_area_base_full_v002.png"
PREVIEW = V002_DIR / "region_home_area_art_v002_runtime_preview.png"
CONTACT = V002_DIR / "region_home_area_art_v002_layer_contact_sheet.png"

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

PUNCH_FROM_GROUND: set[str] = set()

OVERLAY_LAYERS = {"shadow_dappled", "light_overlay"}


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
                output_file=source_file.replace("_v001.png", "_v002.png"),
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


def full_canvas_alpha_from_v001(record: LayerRecord, grow: int) -> Image.Image:
    source = load_rgba(V001_DIR / record.source_file)
    alpha = source.getchannel("A")
    if grow > 0:
        for _ in range(grow):
            alpha = alpha.filter(ImageFilter.MaxFilter(3))
    full = Image.new("L", CANVAS, 0)
    full.paste(alpha, record.origin)
    return full


def soften_mask(mask: Image.Image, blur: float = 1.0) -> Image.Image:
    if blur <= 0:
        return mask
    return mask.filter(ImageFilter.GaussianBlur(blur))


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
            draw.ellipse(bounds, fill=82)
        return mask.filter(ImageFilter.GaussianBlur(24))
    if record.asset_id == "light_overlay":
        for bounds in (
            (560, 560, 2620, 1480),
            (2200, 1120, 4500, 2380),
            (3380, 1960, 5600, 3320),
        ):
            draw.ellipse(bounds, fill=58)
        return mask.filter(ImageFilter.GaussianBlur(30))
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
        fill=230,
    )
    draw.polygon([(0, 2190), (420, 2100), (680, 4096), (0, 4096)], fill=185)
    draw.polygon([(5790, 2040), (6144, 1960), (6144, 4096), (5480, 4096)], fill=185)
    return mask.filter(ImageFilter.GaussianBlur(16))


def extract_layer(base: Image.Image, record: LayerRecord, mask: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    layer.alpha_composite(base)
    layer.putalpha(mask)
    x, y = record.origin
    w, h = record.size
    return layer.crop((x, y, x + w, y + h))


def fade_edges(image: Image.Image, bottom: int = 0, left: int = 0, right: int = 0) -> Image.Image:
    if bottom <= 0 and left <= 0 and right <= 0:
        return image
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


def build_ground(base: Image.Image, records: list[LayerRecord]) -> Image.Image:
    if not PUNCH_FROM_GROUND:
        return base.copy()
    punch = Image.new("L", CANVAS, 0)
    for record in records:
        if record.asset_id not in PUNCH_FROM_GROUND:
            continue
        punch = ImageChops.lighter(punch, full_canvas_alpha_from_v001(record, grow=9))
    punch = punch.filter(ImageFilter.GaussianBlur(2.0))
    alpha = ImageChops.subtract(Image.new("L", CANVAS, 255), punch)
    ground = base.copy()
    ground.putalpha(alpha)
    return ground


def make_runtime_preview(records: list[LayerRecord]) -> None:
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    by_id = {record.asset_id: record for record in records}
    for asset_id in LAYER_ORDER:
        record = by_id[asset_id]
        image = load_rgba(V002_DIR / record.output_file)
        canvas.alpha_composite(image, record.origin)
    canvas.resize(PREVIEW_SIZE, Image.Resampling.LANCZOS).save(PREVIEW)


def make_contact_sheet(records: list[LayerRecord]) -> None:
    tile_w, tile_h = 512, 384
    sheet = Image.new("RGBA", (tile_w * 4, tile_h * 4), (34, 42, 38, 255))
    draw = ImageDraw.Draw(sheet, "RGBA")
    for index, record in enumerate(records):
        image = load_rgba(V002_DIR / record.output_file)
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


def alpha_bbox(image: Image.Image) -> list[int] | None:
    bbox = image.getchannel("A").getbbox()
    return list(bbox) if bbox else None


def write_manifest(records: list[LayerRecord]) -> None:
    previous = json.loads(V002_MANIFEST.read_text(encoding="utf-8"))
    assets: list[dict[str, Any]] = []
    runtime_ids = {record.asset_id for record in records}
    for item in previous["assets"]:
        if item.get("asset_id") not in runtime_ids:
            assets.append(item)
    for record in records:
        image = load_rgba(V002_DIR / record.output_file)
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
                "source": "v002_mother_plate_extracted_with_v001_spatial_alpha_contract",
            }
        )
    manifest = {
        **previous,
        "status": "runtime_layer_candidate_visual_review_required",
        "runtime_replacement": False,
        "layer_split_ready": True,
        "split_method": "Used the validated v001 source-space alpha contract as replaceable masks over the v002 mother plate; no single full plate is wired into runtime.",
        "assets": assets,
        "runtime_preview": PREVIEW.name,
        "contact_sheet": CONTACT.name,
        "integration_gate": [
            "Runtime may reference split v002 layer files, not the opaque full-scene mother plate.",
            "Ground is kept as a full opaque underlay until manual masks are refined; runtime layers remain replaceable on top to avoid visible seams from v001 mask drift.",
            "Visual review is still required before labeling these layers final-quality hand-split art.",
        ],
    }
    V002_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    require(BASE_FULL.exists(), f"missing v002 base plate: {BASE_FULL}")
    base = load_rgba(BASE_FULL)
    require(base.size == CANVAS, f"v002 base plate must be {CANVAS}, got {base.size}")
    records = load_v001_records()
    by_id = {record.asset_id: record for record in records}
    require(set(LAYER_ORDER) == set(by_id), "v001 and v002 layer contracts drifted")

    for record in records:
        if record.asset_id == "ground_yard":
            output = build_ground(base, records)
        elif record.asset_id in OVERLAY_LAYERS:
            output = extract_layer(base, record, make_overlay_mask(record))
        elif record.asset_id == "foreground_grass":
            output = extract_layer(base, record, make_foreground_mask())
        else:
            grow = 8 if "canopy" in record.asset_id or "roof" in record.asset_id else 4
            mask = soften_mask(full_canvas_alpha_from_v001(record, grow=grow), blur=1.0)
            output = extract_layer(base, record, mask)
            if record.asset_id == "house_body":
                output = fade_edges(output, bottom=128, left=28, right=28)
        output.save(V002_DIR / record.output_file)

    make_runtime_preview(records)
    make_contact_sheet(records)
    write_manifest(records)
    print(f"OK: generated {len(records)} Region_HomeArea art v002 runtime layer candidates")
    print(f"OK: preview: {PREVIEW.relative_to(ROOT).as_posix()}")
    print(f"OK: manifest: {V002_MANIFEST.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
