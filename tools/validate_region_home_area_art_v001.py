from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v001"
MANIFEST = ART_DIR / "region_home_area_art_v001_manifest.json"
PREVIEW = ART_DIR / "region_home_area_art_v001_preview.png"
CONTACT = ART_DIR / "region_home_area_art_v001_layer_contact_sheet.png"

CANVAS = (6144, 4096)
PREVIEW_SIZE = (1536, 1024)

REQUIRED_FILES = {
    "region_home_area_base_full_v001.png",
    "region_home_area_ground_yard_v001.png",
    "region_home_area_path_village_road_v001.png",
    "region_home_area_path_back_farm_v001.png",
    "region_home_area_house_body_v001.png",
    "region_home_area_house_roof_occluder_v001.png",
    "region_home_area_veranda_floor_v001.png",
    "region_home_area_tree_left_trunk_v001.png",
    "region_home_area_tree_left_canopy_occluder_v001.png",
    "region_home_area_tree_right_trunk_v001.png",
    "region_home_area_tree_right_canopy_occluder_v001.png",
    "region_home_area_foreground_grass_v001.png",
    "region_home_area_shadow_dappled_v001.png",
    "region_home_area_light_overlay_v001.png",
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


def validate_manifest() -> dict[str, Any]:
    require(MANIFEST.exists(), f"missing manifest: {MANIFEST}")
    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "manifest")
    require(manifest.get("region_id") == "Region_HomeArea", "manifest region_id must be Region_HomeArea")
    require(manifest.get("package_id") == "home_area_art_v001", "manifest package_id must be home_area_art_v001")
    require(manifest.get("runtime_replacement") is False, "art package must not claim runtime replacement")
    require(manifest.get("status") == "visual_review_required_before_runtime_integration", "manifest must require visual review")
    canvas = require_dict(manifest.get("canvas_px"), "manifest canvas_px")
    require((canvas.get("width"), canvas.get("height")) == CANVAS, "manifest canvas must be 6144x4096")
    return manifest


def validate_png(record: dict[str, Any]) -> None:
    file_name = str(record.get("file"))
    path = ART_DIR / file_name
    require(path.exists(), f"missing asset file: {file_name}")
    with Image.open(path) as image:
        require(image.mode == "RGBA", f"{file_name} must be RGBA")
        width, height = image.size
        require(width > 0 and height > 0, f"{file_name} must have non-zero size")
        require(width <= CANVAS[0] and height <= CANVAS[1], f"{file_name} exceeds canvas size")
        bbox = alpha_bbox(image)
        require(bbox is not None, f"{file_name} must contain visible pixels")
        visible_w = bbox[2] - bbox[0]
        visible_h = bbox[3] - bbox[1]
        require(visible_w >= 16 and visible_h >= 16, f"{file_name} visible area is too small")
        if file_name == "region_home_area_base_full_v001.png":
            require(image.size == CANVAS, "base full plate must be full canvas 6144x4096")
            alpha_min, alpha_max = image.getchannel("A").getextrema()
            require(alpha_min == 255 and alpha_max == 255, "base full plate must be opaque for review")


def main() -> None:
    manifest = validate_manifest()
    assets = manifest.get("assets")
    require(isinstance(assets, list) and assets, "manifest assets must be a non-empty list")
    by_file = {str(record.get("file")): require_dict(record, "asset record") for record in assets if isinstance(record, dict)}
    missing = REQUIRED_FILES - set(by_file)
    extra = set(by_file) - REQUIRED_FILES
    require(not missing, f"missing required art files in manifest: {sorted(missing)}")
    require(not extra, f"unexpected art files in manifest: {sorted(extra)}")

    for record in by_file.values():
        origin = require_dict(record.get("origin_px"), f"{record.get('file')} origin_px")
        anchor = require_dict(record.get("anchor_px"), f"{record.get('file')} anchor_px")
        require(isinstance(record.get("target_parent"), str) and record["target_parent"], f"{record.get('file')} target_parent required")
        require(isinstance(record.get("z_index"), int), f"{record.get('file')} z_index must be int")
        require(0 <= int(origin["x"]) < CANVAS[0], f"{record.get('file')} origin x outside canvas")
        require(0 <= int(origin["y"]) < CANVAS[1], f"{record.get('file')} origin y outside canvas")
        require(0 <= int(anchor["x"]) <= CANVAS[0], f"{record.get('file')} anchor x outside canvas")
        require(0 <= int(anchor["y"]) <= CANVAS[1], f"{record.get('file')} anchor y outside canvas")
        validate_png(record)

    require(PREVIEW.exists(), f"missing preview: {PREVIEW}")
    with Image.open(PREVIEW) as preview:
        require(preview.mode == "RGBA", "preview must be RGBA")
        require(preview.size == PREVIEW_SIZE, "preview must be 1536x1024")
        require(alpha_bbox(preview) is not None, "preview must contain visible pixels")

    require(CONTACT.exists(), f"missing contact sheet: {CONTACT}")
    with Image.open(CONTACT) as contact:
        require(contact.mode == "RGBA", "contact sheet must be RGBA")
        require(contact.width >= 1024 and contact.height >= 768, "contact sheet is too small")
        require(alpha_bbox(contact) is not None, "contact sheet must contain visible pixels")

    print("OK: Region_HomeArea art v001 package validated")


if __name__ == "__main__":
    main()
