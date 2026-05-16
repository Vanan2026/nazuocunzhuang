from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v002"
MANIFEST = ART_DIR / "region_home_area_art_v002_manifest.json"
RAW_SOURCE = ART_DIR / "region_home_area_art_v002_generated_source.png"
BASE_FULL = ART_DIR / "region_home_area_base_full_v002.png"
REVIEW_PREVIEW = ART_DIR / "region_home_area_art_v002_preview.png"
RUNTIME_PREVIEW = ART_DIR / "region_home_area_art_v002_runtime_preview.png"
CONTACT = ART_DIR / "region_home_area_art_v002_layer_contact_sheet.png"
PROMPT_FILE = ART_DIR / "region_home_area_art_v002_prompt.md"

CANVAS = (6144, 4096)
PREVIEW_SIZE = (1536, 1024)

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


def validate_image(path: Path, size: tuple[int, int] | None, opaque: bool = False, require_alpha_holes: bool = False) -> None:
    require(path.exists(), f"missing image: {path}")
    with Image.open(path) as image:
        require(image.mode == "RGBA", f"{path.name} must be RGBA")
        if size is not None:
            require(image.size == size, f"{path.name} must be {size[0]}x{size[1]}")
        require(alpha_bbox(image) is not None, f"{path.name} must contain visible pixels")
        alpha_min, alpha_max = image.getchannel("A").getextrema()
        if opaque:
            require(alpha_min == 255 and alpha_max == 255, f"{path.name} must be opaque")
        if require_alpha_holes:
            require(alpha_min < 255 and alpha_max == 255, f"{path.name} must contain cutout alpha and opaque paint")


def validate_manifest() -> dict[str, Any]:
    require(MANIFEST.exists(), f"missing manifest: {MANIFEST}")
    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "manifest")
    require(manifest.get("region_id") == "Region_HomeArea", "manifest region_id must be Region_HomeArea")
    require(manifest.get("package_id") == "home_area_art_v002", "manifest package_id must be home_area_art_v002")
    require(
        manifest.get("status") == "runtime_layer_candidate_visual_review_required",
        "manifest must mark v002 as runtime layer candidate pending visual review",
    )
    require(manifest.get("runtime_replacement") is False, "v002 must not claim whole-plate runtime replacement")
    require(manifest.get("layer_split_ready") is True, "v002 must declare split layer candidates ready")
    require("single full plate" in manifest.get("split_method", ""), "manifest must document that full plate is not wired")
    canvas = require_dict(manifest.get("canvas_px"), "manifest canvas_px")
    require((canvas.get("width"), canvas.get("height")) == CANVAS, "manifest canvas must be 6144x4096")
    require(manifest.get("prompt_file") == PROMPT_FILE.name, "manifest prompt_file must reference the saved prompt")
    require(manifest.get("runtime_preview") == RUNTIME_PREVIEW.name, "manifest must reference runtime preview")
    require(manifest.get("contact_sheet") == CONTACT.name, "manifest must reference contact sheet")

    assets = manifest.get("assets")
    require(isinstance(assets, list), "manifest assets must be a list")
    by_id = {record.get("asset_id"): record for record in assets if isinstance(record, dict)}
    require({"generated_source", "base_full", "review_preview"}.issubset(by_id), "manifest must retain source/base/review records")
    require(RUNTIME_LAYER_IDS.issubset(by_id), f"manifest missing runtime layers: {sorted(RUNTIME_LAYER_IDS - set(by_id))}")
    require(by_id["base_full"].get("target_parent") == "art_review_only", "base_full must stay review-only")
    require(by_id["base_full"].get("file") == BASE_FULL.name, "base_full must reference the opaque mother plate")

    for asset_id in RUNTIME_LAYER_IDS:
        record = require_dict(by_id[asset_id], asset_id)
        file_name = record.get("file")
        require(isinstance(file_name, str) and file_name.endswith("_v002.png"), f"{asset_id} must use a v002 PNG")
        require(record.get("target_parent") != "art_review_only", f"{asset_id} must target a runtime parent")
        require(record.get("source") == "v002_mother_plate_extracted_with_v001_spatial_alpha_contract", f"{asset_id} source must document split method")
        size = require_dict(record.get("size_px"), f"{asset_id}.size_px")
        validate_image(ART_DIR / file_name, (int(size["width"]), int(size["height"])), opaque=asset_id == "ground_yard")
    return manifest


def main() -> None:
    validate_manifest()
    require(PROMPT_FILE.exists(), f"missing prompt file: {PROMPT_FILE}")
    validate_image(RAW_SOURCE, None, opaque=True)
    validate_image(BASE_FULL, CANVAS, opaque=True)
    validate_image(REVIEW_PREVIEW, PREVIEW_SIZE, opaque=True)
    validate_image(RUNTIME_PREVIEW, PREVIEW_SIZE)
    validate_image(CONTACT, (2048, 1536), opaque=True)
    print("OK: Region_HomeArea art v002 runtime layer package validated")


if __name__ == "__main__":
    main()
