from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "production" / "assets" / "regions" / "home_area_launch" / "v001"
MANIFEST = PACKAGE_ROOT / "region_home_area_launch_art_manifest.json"
PREVIEW = PACKAGE_ROOT / "region_home_area_launch_preview.png"
REQUIRED_IDS = {
    "homeyard_bg_sky_01",
    "homeyard_mid_house_main_01",
    "homeyard_mid_house_roof_01",
    "homeyard_mid_garden_ground_01",
    "homeyard_mid_stone_path_01",
    "homeyard_mid_persimmon_tree_trunk_01",
    "homeyard_mid_persimmon_tree_canopy_01",
    "homeyard_fg_leaves_top_01",
    "homeyard_fx_dapplelight_01",
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


def main() -> None:
    require(MANIFEST.exists(), f"missing manifest: {MANIFEST}")
    require(PREVIEW.exists(), f"missing preview: {PREVIEW}")

    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "manifest")
    require(manifest.get("region_id") == "Region_HomeArea", "manifest region_id must be Region_HomeArea")
    require(manifest.get("status") == "rejected_composition_source_pool", "package must be marked as rejected source pool")
    require(manifest.get("runtime_replacement") is False, "packaging step must not change runtime references")
    require("procedural engineering candidates excluded" in str(manifest.get("source_policy")), "source policy must exclude engineering candidates")

    layers = manifest.get("layers")
    require(isinstance(layers, list) and len(layers) >= 30, "launch package must include at least 30 art assets")
    layer_ids = {layer.get("id") for layer in layers if isinstance(layer, dict)}
    missing_required = REQUIRED_IDS - layer_ids
    require(not missing_required, f"missing required launch assets: {sorted(missing_required)}")

    for raw_layer in layers:
        layer = require_dict(raw_layer, "layer")
        asset_id = str(layer.get("id"))
        require(layer.get("source_kind") == "formal_homeyard_generated_or_source_derived", f"{asset_id} source_kind is not formal")
        require("procedural_candidate" not in json.dumps(layer), f"{asset_id} must not reference procedural candidate output")
        path = PACKAGE_ROOT / str(layer.get("file"))
        require(path.exists(), f"{asset_id} missing copied file: {path}")

        with Image.open(path) as image:
            require(image.width >= 256 and image.height >= 256, f"{asset_id} is too small for launch package")
            if asset_id != "homeyard_bg_sky_01":
                require(image.mode == "RGBA", f"{asset_id} must be RGBA")
                alpha = image.getchannel("A")
                require(alpha.getbbox() is not None, f"{asset_id} must contain visible alpha pixels")
                require(alpha.getextrema()[0] < 255, f"{asset_id} must have transparent pixels")

    with Image.open(PREVIEW) as preview:
        require(preview.size == (1920, 1080), "launch preview must be 1920x1080")
        require(preview.mode == "RGBA", "launch preview must be RGBA")

    print("OK: Region_HomeArea rejected source-pool package validated")


if __name__ == "__main__":
    main()
