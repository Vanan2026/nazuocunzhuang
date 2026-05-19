from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "production" / "assets" / "regions" / "home_area_world2d" / "v001"
WORKFLOW_MANIFEST = PKG / "workflow_manifest.json"
FOUR_LAYER_MANIFEST = PKG / "03_layer_export" / "four_layer_package" / "four_layer_manifest.json"
SCENE = ROOT / "scenes" / "regions" / "region_home_area.tscn"
CANVAS = (1470, 1070)

REQUIRED_LAYERS = {
    "source": {
        "path": "production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/home_area_01_source.png",
        "alpha": "opaque",
        "scene_ref": "home_area_01_source.png",
    },
    "base_ground_paths": {
        "path": "production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/home_area_02_base_ground_paths.png",
        "alpha": "opaque",
        "scene_ref": "home_area_02_base_ground_paths.png",
    },
    "foreground_occlusion": {
        "path": "production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/home_area_03_foreground_occlusion_v4_no_bottom_leaf_wall.png",
        "alpha": "transparent",
        "scene_ref": "home_area_03_foreground_occlusion_v4_no_bottom_leaf_wall.png",
    },
    "midground_behind_player": {
        "path": "production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/home_area_04_midground_behind_player.png",
        "alpha": "transparent",
        "scene_ref": "home_area_04_midground_behind_player.png",
    },
}

REQUIRED_SCENE_FRAGMENTS = [
    'metadata/status = "home_area_world2d_four_layer_integrated"',
    'metadata/art_package = "home_area_world2d_v001"',
    'metadata/launch_quality_approved = false',
    'metadata/source = "production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/four_layer_manifest.json"',
    '[node name="SourceReferenceHidden" type="Sprite2D" parent="ArtLayers"',
    '[node name="BaseGroundPaths" type="Sprite2D" parent="ArtLayers"',
    '[node name="MidgroundBehindPlayer" type="Sprite2D" parent="ArtLayers"',
    '[node name="ForegroundOcclusion" type="Sprite2D" parent="."',
    'metadata/layer_role = "opaque_base_grass_and_paths"',
    'metadata/layer_role = "transparent_midground_renders_behind_player"',
    'metadata/layer_role = "transparent_foreground_occludes_player"',
]

FORBIDDEN_SCENE_TOKENS = [
    "production/assets/regions/home_area_art/",
    "production/assets/regions/home_area_launch/",
    "production/assets/regions/home_area_launch_quality/",
    "production/assets/regions/home_area_formal/",
    "region_home_area_base_full_",
    "region_home_area_formal_full_plate_",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path, label: str) -> dict[str, Any]:
    require(path.exists(), f"missing {label}: {path.relative_to(ROOT).as_posix()}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{label} must be a JSON object")
    return data


def image_has_partial_alpha(image: Image.Image) -> bool:
    if image.mode != "RGBA":
        return False
    alpha = image.getchannel("A")
    extrema = alpha.getextrema()
    return extrema[0] < 255 and extrema[1] == 255


def image_is_opaque(image: Image.Image) -> bool:
    if image.mode != "RGBA":
        return True
    return image.getchannel("A").getextrema() == (255, 255)


def validate_layer_file(layer_id: str, record: dict[str, Any]) -> None:
    relative_path = str(record["path"])
    path = ROOT / relative_path
    require(path.exists(), f"missing layer file for {layer_id}: {relative_path}")
    image = Image.open(path)
    require(image.size == CANVAS, f"{layer_id} must be {CANVAS[0]}x{CANVAS[1]}, got {image.size}")
    if record["alpha"] == "opaque":
        require(image_is_opaque(image), f"{layer_id} must be opaque")
    else:
        require(image_has_partial_alpha(image), f"{layer_id} must contain useful transparency")


def main() -> None:
    workflow = read_json(WORKFLOW_MANIFEST, "HomeArea World2D workflow manifest")
    manifest = read_json(FOUR_LAYER_MANIFEST, "HomeArea World2D four-layer manifest")
    require(SCENE.exists(), "missing Region_HomeArea scene")

    require(workflow.get("package_id") == "home_area_world2d_v001", "workflow package_id mismatch")
    require(workflow.get("current_phase") == "03_layer_export", "workflow current_phase should remain at layer export until capture passes")
    require(workflow.get("active_layer_package") == REQUIRED_LAYERS["source"]["path"].replace("home_area_01_source.png", "four_layer_manifest.json"), "workflow active layer package mismatch")
    require(workflow.get("godot_integration", {}).get("status") == "integrated_unverified", "workflow must not claim verified integration before capture")
    require(workflow.get("foreground_03_v4", {}).get("validation") == "pending_godot_capture", "foreground v4 must remain capture-pending")

    require(manifest.get("package_id") == "home_area_world2d_v001_four_layer_regenerated_package", "four-layer package_id mismatch")
    require(manifest.get("status") == "foreground_03_v4_no_bottom_leaf_wall_integrated_pending_godot_capture", "four-layer status mismatch")
    require(manifest.get("canvas") == {"width": CANVAS[0], "height": CANVAS[1]}, "four-layer canvas mismatch")
    require(manifest.get("coordinate_origin") == "top_left_canvas", "coordinate origin must be top_left_canvas")
    require(manifest.get("godot_integration", {}).get("status") == "integrated_unverified", "four-layer manifest must not claim verified integration before capture")

    layer_records = {layer.get("id"): layer for layer in manifest.get("layers", []) if isinstance(layer, dict)}
    require(set(REQUIRED_LAYERS) <= set(layer_records), f"missing layer records: {sorted(set(REQUIRED_LAYERS) - set(layer_records))}")
    for layer_id, expected in REQUIRED_LAYERS.items():
        record = layer_records[layer_id]
        require(record.get("path") == expected["path"], f"{layer_id} path mismatch")
        require(record.get("alpha") == expected["alpha"], f"{layer_id} alpha contract mismatch")
        validate_layer_file(layer_id, expected)

    scene_text = SCENE.read_text(encoding="utf-8")
    for fragment in REQUIRED_SCENE_FRAGMENTS:
        require(fragment in scene_text, f"scene missing fragment: {fragment}")
    for layer_id, expected in REQUIRED_LAYERS.items():
        require(expected["scene_ref"] in scene_text, f"scene missing {layer_id} texture reference")
    for token in FORBIDDEN_SCENE_TOKENS:
        require(token not in scene_text, f"scene still references forbidden legacy art path/token: {token}")

    print("OK: HomeArea World2D v001 package and scene integration validated")


if __name__ == "__main__":
    main()
