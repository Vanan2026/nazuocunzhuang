from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "production/assets/regions/home_area_formal/v001"
MANIFEST = PKG / "region_home_area_formal_v001_manifest.json"
SOURCE = PKG / "source/region_home_area_formal_full_source_v001.png"
MASK_DIR = PKG / "source/masks"
LAYER_DIR = PKG / "layers"
PREVIEW = PKG / "region_home_area_formal_v001_runtime_preview.png"
CONTACT = PKG / "region_home_area_formal_v001_layer_contact_sheet.png"
CANVAS = (6144, 4096)

ASSETS: list[dict[str, Any]] = [
    {"asset_id": "ground_yard", "file": "region_home_area_formal_ground_yard_v001.png", "origin_px": {"x": 0, "y": 0}, "size_px": {"width": 6144, "height": 4096}, "z_index": -100, "target_parent": "TileMapLayer_Ground/GroundModules", "transparent_background": False, "runtime_role": "opaque_underpaint_ground"},
    {"asset_id": "path_village_road", "file": "region_home_area_formal_path_village_road_v001.png", "origin_px": {"x": 430, "y": 0}, "size_px": {"width": 5320, "height": 1760}, "z_index": -90, "target_parent": "TileMapLayer_Path/PathModules", "transparent_background": True},
    {"asset_id": "path_back_farm", "file": "region_home_area_formal_path_back_farm_v001.png", "origin_px": {"x": 2720, "y": 1880}, "size_px": {"width": 1940, "height": 1880}, "z_index": -89, "target_parent": "TileMapLayer_Path/PathModules", "transparent_background": True},
    {"asset_id": "veranda_floor", "file": "region_home_area_formal_veranda_floor_v001.png", "origin_px": {"x": 1890, "y": 1350}, "size_px": {"width": 2080, "height": 410}, "z_index": -30, "target_parent": "TileMapLayer_Detail", "transparent_background": True},
    {"asset_id": "house_body", "file": "region_home_area_formal_house_body_v001.png", "origin_px": {"x": 1810, "y": 900}, "size_px": {"width": 2330, "height": 1030}, "z_index": 40, "target_parent": "YSortWorld/Houses/CloudHouse", "transparent_background": True},
    {"asset_id": "house_roof_occluder", "file": "region_home_area_formal_house_roof_occluder_v001.png", "origin_px": {"x": 1680, "y": 235}, "size_px": {"width": 2760, "height": 960}, "z_index": 180, "target_parent": "ForegroundStatic/Occluders", "transparent_background": True, "occlusion_rule": "roof_only_visual_occluder"},
    {"asset_id": "tree_left_trunk", "file": "region_home_area_formal_tree_left_trunk_v001.png", "origin_px": {"x": 260, "y": 520}, "size_px": {"width": 860, "height": 1340}, "z_index": 55, "target_parent": "YSortWorld/Trees/BigShadeTree", "transparent_background": True},
    {"asset_id": "tree_left_canopy_occluder", "file": "region_home_area_formal_tree_left_canopy_occluder_v001.png", "origin_px": {"x": 0, "y": 0}, "size_px": {"width": 2360, "height": 1920}, "z_index": 190, "target_parent": "ForegroundStatic/Occluders", "transparent_background": True, "occlusion_rule": "canopy_only_visual_occluder"},
    {"asset_id": "tree_right_trunk", "file": "region_home_area_formal_tree_right_trunk_v001.png", "origin_px": {"x": 4050, "y": 680}, "size_px": {"width": 850, "height": 1540}, "z_index": 55, "target_parent": "YSortWorld/Trees/PersimmonTree", "transparent_background": True},
    {"asset_id": "tree_right_canopy_occluder", "file": "region_home_area_formal_tree_right_canopy_occluder_v001.png", "origin_px": {"x": 3710, "y": 0}, "size_px": {"width": 2240, "height": 1940}, "z_index": 188, "target_parent": "ForegroundStatic/Occluders", "transparent_background": True, "occlusion_rule": "canopy_only_visual_occluder"},
    {"asset_id": "foreground_grass", "file": "region_home_area_formal_foreground_grass_v001.png", "origin_px": {"x": 0, "y": 3000}, "size_px": {"width": 6144, "height": 1096}, "z_index": 198, "target_parent": "ForegroundStatic", "transparent_background": True, "occlusion_rule": "front_edge_only"},
    {"asset_id": "shadow_dappled", "file": "region_home_area_formal_shadow_dappled_v001.png", "origin_px": {"x": 0, "y": 0}, "size_px": {"width": 6144, "height": 4096}, "z_index": 0, "target_parent": "LightAndWeather", "transparent_background": True, "runtime_role": "ambient_shadow_overlay"},
    {"asset_id": "light_overlay", "file": "region_home_area_formal_light_overlay_v001.png", "origin_px": {"x": 0, "y": 0}, "size_px": {"width": 6144, "height": 4096}, "z_index": 1, "target_parent": "LightAndWeather", "transparent_background": True, "runtime_role": "ambient_light_overlay"},
    {"asset_id": "prop_mailbox", "file": "region_home_area_formal_prop_mailbox_v001.png", "origin_px": {"x": 1760, "y": 1180}, "size_px": {"width": 560, "height": 660}, "z_index": 60, "target_parent": "YSortWorld/Props/Mailbox", "transparent_background": True, "prop_node_position": {"x": 1980, "y": 1760}, "art_position": {"x": -220, "y": -580}},
    {"asset_id": "prop_well", "file": "region_home_area_formal_prop_well_v001.png", "origin_px": {"x": 4190, "y": 2030}, "size_px": {"width": 780, "height": 850}, "z_index": 62, "target_parent": "YSortWorld/Props/Well", "transparent_background": True, "prop_node_position": {"x": 4580, "y": 2840}, "art_position": {"x": -390, "y": -810}},
    {"asset_id": "prop_bench", "file": "region_home_area_formal_prop_bench_v001.png", "origin_px": {"x": 520, "y": 1340}, "size_px": {"width": 850, "height": 760}, "z_index": 61, "target_parent": "YSortWorld/Props/Bench", "transparent_background": True, "prop_node_position": {"x": 940, "y": 2020}, "art_position": {"x": -420, "y": -680}},
    {"asset_id": "prop_road_sign", "file": "region_home_area_formal_prop_road_sign_v001.png", "origin_px": {"x": 4850, "y": 2860}, "size_px": {"width": 520, "height": 520}, "z_index": 58, "target_parent": "YSortWorld/Props/RoadSign", "transparent_background": True, "prop_node_position": {"x": 5085, "y": 3270}, "art_position": {"x": -235, "y": -410}},
    {"asset_id": "prop_cat_bed", "file": "region_home_area_formal_prop_cat_bed_v001.png", "origin_px": {"x": 0, "y": 0}, "size_px": {"width": 256, "height": 192}, "z_index": 57, "target_parent": "YSortWorld/Props/CatBed", "transparent_background": True, "optional_hidden_placeholder": True},
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs() -> None:
    MASK_DIR.mkdir(parents=True, exist_ok=True)
    LAYER_DIR.mkdir(parents=True, exist_ok=True)


def polygon_mask(points: list[tuple[int, int]], blur: float = 0.0) -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(blur)) if blur > 0 else mask


def ellipse_mask(bounds: tuple[int, int, int, int], blur: float = 0.0) -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    ImageDraw.Draw(mask).ellipse(bounds, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(blur)) if blur > 0 else mask


def add_mask(base: Image.Image, extra: Image.Image) -> Image.Image:
    return ImageChops.lighter(base, extra)


def mask_for(asset_id: str) -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    if asset_id == "path_village_road":
        mask = add_mask(mask, polygon_mask([(5000, 0), (6100, 0), (6100, 1450), (5360, 1540), (5180, 920)], 24))
        mask = add_mask(mask, polygon_mask([(360, 1610), (1460, 1450), (2440, 1550), (3620, 1900), (3480, 2350), (1900, 2230), (620, 2020)], 30))
    elif asset_id == "path_back_farm":
        mask = polygon_mask([(2760, 2050), (3440, 2030), (4280, 2420), (4580, 3720), (3860, 3840), (3160, 2820)], 34)
    elif asset_id == "veranda_floor":
        mask = polygon_mask([(1870, 1440), (3970, 1440), (3920, 1690), (1980, 1740)], 10)
    elif asset_id == "house_body":
        mask = polygon_mask([(1860, 925), (3950, 925), (4045, 1660), (3860, 1870), (2010, 1760), (1845, 1180)], 8)
    elif asset_id == "house_roof_occluder":
        mask = polygon_mask([(1820, 300), (4100, 290), (4300, 900), (4180, 1110), (1780, 1110), (1680, 920)], 8)
    elif asset_id == "tree_left_trunk":
        mask = polygon_mask([(450, 460), (920, 450), (1030, 1160), (900, 1760), (540, 1780), (380, 1050)], 14)
    elif asset_id == "tree_left_canopy_occluder":
        mask = add_mask(mask, ellipse_mask((-520, -360, 2250, 1510), 22))
        mask = add_mask(mask, ellipse_mask((90, 140, 2050, 1910), 24))
    elif asset_id == "tree_right_trunk":
        mask = polygon_mask([(4290, 780), (4740, 780), (4860, 1540), (4670, 2190), (4300, 2200), (4140, 1490)], 14)
    elif asset_id == "tree_right_canopy_occluder":
        mask = add_mask(mask, ellipse_mask((3650, -300, 5900, 1500), 22))
        mask = add_mask(mask, ellipse_mask((3900, 190, 5600, 1910), 24))
    elif asset_id == "foreground_grass":
        mask = polygon_mask([(0, 3250), (690, 3030), (1600, 3210), (2900, 3180), (4110, 3090), (5280, 3040), (6144, 3190), (6144, 4096), (0, 4096)], 40)
    elif asset_id == "shadow_dappled":
        mask = add_mask(mask, polygon_mask([(240, 450), (2070, 650), (2020, 1750), (0, 1850), (0, 760)], 90))
        mask = add_mask(mask, polygon_mask([(3760, 350), (5740, 620), (5600, 2100), (3930, 1920)], 110))
        mask = add_mask(mask, polygon_mask([(0, 3200), (6144, 3000), (6144, 4096), (0, 4096)], 160))
    elif asset_id == "light_overlay":
        mask = add_mask(mask, polygon_mask([(1760, 650), (3950, 820), (4110, 1750), (1750, 1710)], 120))
        mask = add_mask(mask, polygon_mask([(2440, 1910), (4560, 2100), (4380, 3150), (1850, 2880)], 180))
    elif asset_id == "prop_mailbox":
        mask = polygon_mask([(1840, 1230), (2100, 1230), (2180, 1770), (1900, 1770)], 8)
    elif asset_id == "prop_well":
        mask = add_mask(mask, polygon_mask([(4320, 2140), (4640, 2140), (4810, 2440), (4750, 2790), (4240, 2790), (4180, 2420)], 10))
        mask = add_mask(mask, polygon_mask([(4280, 2080), (4690, 2080), (4890, 2260), (4780, 2370), (4160, 2370), (4070, 2260)], 8))
    elif asset_id == "prop_bench":
        mask = polygon_mask([(560, 1440), (1210, 1310), (1330, 1730), (1010, 2040), (620, 1970), (510, 1640)], 8)
    elif asset_id == "prop_road_sign":
        mask = polygon_mask([(4910, 2940), (5220, 2890), (5360, 3080), (5220, 3290), (4950, 3280)], 8)
    elif asset_id == "prop_cat_bed":
        return mask
    else:
        fail(f"no mask for asset_id: {asset_id}")
    return mask


def crop_box(asset: dict[str, Any]) -> tuple[int, int, int, int]:
    origin = asset["origin_px"]
    size = asset["size_px"]
    x = int(origin["x"])
    y = int(origin["y"])
    w = int(size["width"])
    h = int(size["height"])
    require(x >= 0 and y >= 0 and x + w <= CANVAS[0] and y + h <= CANVAS[1], f"{asset['asset_id']} crop outside canvas")
    return x, y, x + w, y + h


def visible_alpha(image: Image.Image) -> bool:
    return image.getchannel("A").getbbox() is not None


def build_layer(source: Image.Image, asset: dict[str, Any], underpaint_source: Image.Image) -> tuple[Image.Image, Image.Image]:
    asset_id = asset["asset_id"]
    if asset_id == "ground_yard":
        combined = Image.new("L", CANVAS, 0)
        for other in ASSETS:
            if other["asset_id"] in {"ground_yard", "shadow_dappled", "light_overlay", "prop_cat_bed"}:
                continue
            combined = add_mask(combined, mask_for(other["asset_id"]))
        # Keep the underpaint visually close to the approved source. A heavy blur
        # creates obvious smears in open areas, so only blend a soft repair pass
        # into extracted-object regions while preserving the original color field.
        blur_mask = combined.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(10))
        layer = source.copy()
        soft_repair = Image.blend(source, underpaint_source.filter(ImageFilter.GaussianBlur(18)), 0.18)
        layer.paste(soft_repair, (0, 0), blur_mask)
        layer.putalpha(255)
        return layer, Image.new("L", CANVAS, 255)
    if asset_id in {"shadow_dappled", "light_overlay"}:
        mask = mask_for(asset_id)
        color = (54, 48, 38, 70) if asset_id == "shadow_dappled" else (255, 234, 160, 54)
        layer = Image.new("RGBA", CANVAS, color)
        layer.putalpha(mask.point(lambda p: min(92, int(p * (0.34 if asset_id == "shadow_dappled" else 0.26)))))
        return layer.crop(crop_box(asset)), mask.crop(crop_box(asset))
    if asset_id == "prop_cat_bed":
        size = asset["size_px"]
        return Image.new("RGBA", (int(size["width"]), int(size["height"])), (0, 0, 0, 0)), Image.new("L", (int(size["width"]), int(size["height"])), 0)
    mask = mask_for(asset_id)
    full = source.copy()
    full.putalpha(mask)
    return full.crop(crop_box(asset)), mask.crop(crop_box(asset))


def build_preview(records: list[dict[str, Any]]) -> None:
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    for record in sorted(records, key=lambda r: int(r.get("z_index", 0))):
        img = Image.open(PKG / record["file"]).convert("RGBA")
        origin = record["origin_px"]
        canvas.alpha_composite(img, (int(origin["x"]), int(origin["y"])))
    canvas.save(PREVIEW)


def build_contact_sheet(records: list[dict[str, Any]]) -> None:
    thumb_w, thumb_h = 512, 384
    cols = 3
    rows = (len(records) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * thumb_w, rows * thumb_h), (240, 234, 220, 255))
    draw = ImageDraw.Draw(sheet)
    for i, record in enumerate(records):
        img = Image.open(PKG / record["file"]).convert("RGBA")
        img.thumbnail((thumb_w - 28, thumb_h - 78), Image.Resampling.LANCZOS)
        x = (i % cols) * thumb_w
        y = (i // cols) * thumb_h
        draw.rectangle((x, y, x + thumb_w - 1, y + thumb_h - 1), outline=(118, 98, 72, 255), width=2)
        px = x + (thumb_w - img.width) // 2
        py = y + 18 + (thumb_h - 78 - img.height) // 2
        draw.rectangle((px, py, px + img.width, py + img.height), fill=(224, 218, 204, 255))
        sheet.alpha_composite(img, (px, py))
        draw.text((x + 16, y + thumb_h - 48), record["asset_id"], fill=(38, 32, 24, 255))
        draw.text((x + 16, y + thumb_h - 26), f"{record['size_px']['width']}x{record['size_px']['height']} z{record['z_index']}", fill=(80, 68, 52, 255))
    sheet.convert("RGB").save(CONTACT)


def update_manifest(records: list[dict[str, Any]]) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_sha = sha256(SOURCE)
    manifest["status"] = "formal_split_godot_review_candidate"
    manifest["runtime_replacement"] = False
    manifest["runtime_scene_reference_allowed"] = True
    manifest["active_runtime_review_candidate"] = True
    manifest["human_visual_approval_required"] = True
    manifest["launch_quality_approved"] = False
    manifest["selected_route"] = "approved_formal_full_plate_split_into_editable_runtime_layers"
    manifest["runtime_layers"] = records
    manifest["split_outputs"] = {
        "splitter": "tools/split_home_area_formal_v001_layers.py",
        "runtime_preview": "region_home_area_formal_v001_runtime_preview.png",
        "layer_contact_sheet": "region_home_area_formal_v001_layer_contact_sheet.png",
    }
    manifest["quality_gate"] = {
        "approval_status": "needs_user_godot_visual_review",
        "may_set_runtime_replacement_before_approval": False,
        "layer_split_complete": True,
        "allowed_use": "formal split Godot review candidate for collision and interaction tuning",
        "blocked_claims": ["runtime replacement", "launch approved"],
    }
    manifest["known_limits"] = [
        "Formal/v001 is now split into editable Godot layers from one approved full source.",
        "Ground underpaint uses masked blur fill beneath extracted objects; final human visual review is still required.",
        "The cat bed has no formal visible art in the approved source and remains hidden as an optional placeholder.",
    ]
    for source_asset in manifest.get("source_assets", []):
        if source_asset.get("id") == "formal_full_plate":
            source_asset["sha256"] = source_sha
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    ensure_dirs()
    require(SOURCE.exists(), "missing formal full source")
    source = Image.open(SOURCE).convert("RGBA")
    require(source.size == CANVAS, f"source size mismatch: {source.size}")
    underpaint_source = source.copy()
    source_sha = sha256(SOURCE)
    records: list[dict[str, Any]] = []
    for asset in ASSETS:
        img, mask = build_layer(source, asset, underpaint_source)
        out = LAYER_DIR / asset["file"]
        mask_file = MASK_DIR / f"{asset['asset_id']}_mask.png"
        img.save(out)
        mask.save(mask_file)
        if not asset.get("optional_hidden_placeholder"):
            require(visible_alpha(img), f"{asset['asset_id']} has no visible pixels")
        record = {
            "asset_id": asset["asset_id"],
            "file": f"layers/{asset['file']}",
            "sha256": sha256(out),
            "size_px": asset["size_px"],
            "origin_px": asset["origin_px"],
            "target_parent": asset["target_parent"],
            "z_index": asset["z_index"],
            "transparent_background": bool(asset["transparent_background"]),
            "derived_from_single_source": True,
            "source_asset_id": "formal_full_plate",
            "source_sha256": source_sha,
            "source_rect_px": {"x": asset["origin_px"]["x"], "y": asset["origin_px"]["y"], "width": asset["size_px"]["width"], "height": asset["size_px"]["height"]},
            "mask_file": f"source/masks/{asset['asset_id']}_mask.png",
            "runtime_role": asset.get("runtime_role", asset["asset_id"]),
        }
        if "occlusion_rule" in asset:
            record["occlusion_rule"] = asset["occlusion_rule"]
        if "prop_node_position" in asset:
            record["prop_node_position"] = asset["prop_node_position"]
            record["art_position"] = asset["art_position"]
        if asset.get("optional_hidden_placeholder"):
            record["optional_hidden_placeholder"] = True
        records.append(record)
    build_preview(records)
    build_contact_sheet(records)
    update_manifest(records)
    print(f"OK: wrote {len(records)} formal/v001 split layers")
    print(f"OK: wrote {PREVIEW.relative_to(ROOT).as_posix()}")
    print(f"OK: wrote {CONTACT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()