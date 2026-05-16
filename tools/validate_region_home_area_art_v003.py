from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v003"
MANIFEST = ART_DIR / "region_home_area_art_v003_manifest.json"
BASE_FULL = ART_DIR / "region_home_area_base_full_v003.png"
RUNTIME_PREVIEW = ART_DIR / "region_home_area_art_v003_runtime_preview.png"
CONTACT = ART_DIR / "region_home_area_art_v003_layer_contact_sheet.png"
PROMPT_FILE = ART_DIR / "region_home_area_art_v003_prompt.md"
CAT_BED = ROOT / "assets" / "art" / "props" / "region_home_area_prop_cat_bed_v001.png"

CANVAS = (6144, 4096)
PREVIEW_SIZE = (1536, 1024)
CONTACT_SIZE = (2048, 1536)
SOFT_ALPHA_ONLY_LAYER_IDS = {"shadow_dappled", "light_overlay", "foreground_grass"}
OVERLAY_LAYER_IDS = {"shadow_dappled", "light_overlay"}
RUNTIME_LAYER_IDS = {
    "ground_yard",
    "path_village_road",
    "path_back_farm",
    "house_body",
    "house_roof_occluder",
    "veranda_floor",
    "tree_left_trunk",
    "tree_left_canopy_occluder",
    "tree_right_trunk",
    "tree_right_canopy_occluder",
    "foreground_grass",
    "shadow_dappled",
    "light_overlay",
}
SOFT_EDGE_REQUIRED = {
    "path_village_road": 2500,
    "path_back_farm": 1800,
    "veranda_floor": 900,
    "house_roof_occluder": 1200,
    "tree_left_canopy_occluder": 1200,
    "tree_right_canopy_occluder": 900,
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    if image.mode != "RGBA":
        return None
    return image.getchannel("A").getbbox()


def validate_image(path: Path, size: tuple[int, int] | None, opaque: bool = False, require_alpha_holes: bool = False) -> Image.Image:
    require(path.exists(), f"missing image: {path}")
    image = Image.open(path).convert("RGBA")
    if size is not None:
        require(image.size == size, f"{path.name} must be {size[0]}x{size[1]}, got {image.size[0]}x{image.size[1]}")
    require(alpha_bbox(image) is not None, f"{path.name} must contain visible pixels")
    alpha_min, alpha_max = image.getchannel("A").getextrema()
    if opaque:
        require(alpha_min == 255 and alpha_max == 255, f"{path.name} must be opaque")
    if require_alpha_holes:
        require(alpha_min < alpha_max and alpha_max >= 180, f"{path.name} must contain transparent/soft alpha and readable solid paint")
    return image


def count_soft_alpha(image: Image.Image) -> int:
    histogram = image.getchannel("A").histogram()
    return sum(histogram[8:248])


def validate_manifest() -> dict[str, Any]:
    require(MANIFEST.exists(), f"missing manifest: {MANIFEST}")
    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "manifest")
    require(manifest.get("region_id") == "Region_HomeArea", "manifest region_id must be Region_HomeArea")
    require(manifest.get("package_id") == "home_area_art_v003", "manifest package_id must be home_area_art_v003")
    require(manifest.get("status") == "final_split_runtime_candidate", "manifest must mark v003 as final_split_runtime_candidate")
    require(manifest.get("runtime_replacement") is False, "v003 must not claim whole-plate runtime replacement")
    require(manifest.get("layer_split_ready") is True, "v003 must declare split layer candidates ready")
    require("Softened v001 spatial masks" in manifest.get("split_method", ""), "manifest must document the softened split method")
    canvas = require_dict(manifest.get("canvas_px"), "manifest canvas_px")
    require((canvas.get("width"), canvas.get("height")) == CANVAS, "manifest canvas must be 6144x4096")
    require(manifest.get("prompt_file") == PROMPT_FILE.name, "manifest prompt_file must reference the saved prompt")
    require(manifest.get("runtime_preview") == RUNTIME_PREVIEW.name, "manifest must reference runtime preview")
    require(manifest.get("contact_sheet") == CONTACT.name, "manifest must reference contact sheet")

    assets = manifest.get("assets")
    require(isinstance(assets, list), "manifest assets must be a list")
    by_id = {record.get("asset_id"): record for record in assets if isinstance(record, dict)}
    require("source_v002_base_full" in by_id, "manifest must retain source_v002_base_full review record")
    require(RUNTIME_LAYER_IDS.issubset(by_id), f"manifest missing runtime layers: {sorted(RUNTIME_LAYER_IDS - set(by_id))}")
    require(by_id["source_v002_base_full"].get("target_parent") == "art_review_only", "v003 full plate copy must stay review-only")
    require("prop_cat_bed" in by_id, "manifest must include CatBed runtime prop")
    return manifest


def main() -> None:
    manifest = validate_manifest()
    by_id = {record.get("asset_id"): record for record in manifest["assets"] if isinstance(record, dict)}
    require(PROMPT_FILE.exists(), f"missing prompt file: {PROMPT_FILE}")
    validate_image(BASE_FULL, CANVAS, opaque=True)
    validate_image(RUNTIME_PREVIEW, PREVIEW_SIZE)
    validate_image(CONTACT, CONTACT_SIZE, opaque=True)

    for asset_id in RUNTIME_LAYER_IDS:
        record = require_dict(by_id[asset_id], asset_id)
        file_name = record.get("file")
        require(isinstance(file_name, str) and file_name.endswith("_v003.png"), f"{asset_id} must use a v003 PNG")
        require(record.get("target_parent") != "art_review_only", f"{asset_id} must target a runtime parent")
        require(record.get("source") == "v003_soft_split_from_v002_mother_plate_with_refined_v001_spatial_masks", f"{asset_id} source must document v003 split method")
        size = require_dict(record.get("size_px"), f"{asset_id}.size_px")
        image = validate_image(ART_DIR / file_name, (int(size["width"]), int(size["height"])), opaque=asset_id == "ground_yard", require_alpha_holes=asset_id != "ground_yard" and asset_id not in SOFT_ALPHA_ONLY_LAYER_IDS)
        if asset_id in OVERLAY_LAYER_IDS:
            alpha_min, alpha_max = image.getchannel("A").getextrema()
            require(alpha_min < alpha_max and alpha_max <= 120, f"{asset_id} must stay a transparent low-alpha overlay")
        if asset_id in SOFT_EDGE_REQUIRED:
            soft_count = count_soft_alpha(image)
            require(soft_count >= SOFT_EDGE_REQUIRED[asset_id], f"{asset_id} must have softened alpha edges, got {soft_count} semi-transparent pixels")

    cat_bed = validate_image(CAT_BED, (256, 192), require_alpha_holes=True)
    cat_bbox = alpha_bbox(cat_bed)
    require(cat_bbox is not None and cat_bbox[3] >= 150, "CatBed visible paint must land near the documented base anchor")
    print("OK: Region_HomeArea art v003 final-split package validated")


if __name__ == "__main__":
    main()
