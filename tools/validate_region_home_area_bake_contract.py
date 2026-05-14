from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "production" / "assets" / "regions" / "home_area_bake" / "region_home_area_bake_contract.json"
SCENE = ROOT / "scenes" / "dev" / "region_home_area_bake_blockout_3d.tscn"

REQUIRED_LAYER_IDS = {
    "ground_grass_yard",
    "path_front_yard",
    "structure_cloud_house_back",
    "structure_cloud_house_roof_occluder",
    "tree_left_trunk",
    "tree_left_canopy_occluder",
    "tree_right_trunk",
    "tree_right_canopy_occluder",
    "foreground_front_grass_left",
    "fx_dappled_light",
}

ALLOWED_TARGET_PARENTS = {
    "TileMapLayer_Ground/GroundModules",
    "TileMapLayer_Path/PathModules",
    "YSortWorld/Houses",
    "YSortWorld/Trees",
    "ForegroundStatic",
    "LightAndWeather",
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
    require(CONTRACT.exists(), f"missing bake contract: {CONTRACT}")
    require(SCENE.exists(), f"missing Godot 3D bake blockout scene: {SCENE}")

    contract = require_dict(json.loads(CONTRACT.read_text(encoding="utf-8")), "contract")
    scene_text = SCENE.read_text(encoding="utf-8")

    require(contract.get("region_id") == "Region_HomeArea", "contract region_id must be Region_HomeArea")
    require(contract.get("runtime_boundary") == "offline_3d_source_only", "contract must stay offline-only")
    require(contract.get("runtime_import_mode") == "layered_2d_png", "runtime import mode must be layered 2D PNG")
    require(contract.get("canvas_px") == {"width": 6144, "height": 4096}, "canvas_px must match Region_HomeArea")

    unit_mapping = require_dict(contract.get("unit_mapping"), "unit_mapping")
    require(unit_mapping.get("pixels_per_meter") == 100, "pixels_per_meter must be 100")
    require(unit_mapping.get("origin") == "region_top_left", "unit mapping origin must be region_top_left")

    layers = contract.get("export_layers")
    require(isinstance(layers, list) and layers, "export_layers must be a non-empty list")
    layer_ids = {layer.get("id") for layer in layers if isinstance(layer, dict)}
    missing_layers = REQUIRED_LAYER_IDS - layer_ids
    require(not missing_layers, f"missing required export layers: {sorted(missing_layers)}")

    for layer in layers:
        layer = require_dict(layer, "export layer")
        layer_id = str(layer.get("id"))
        export_name = str(layer.get("export_name"))
        require(export_name.startswith("region_home_area_"), f"{layer_id} export name must use region prefix")
        require(export_name.endswith("_v001.png"), f"{layer_id} export name must use v001 PNG naming")
        require(layer.get("target_parent") in ALLOWED_TARGET_PARENTS, f"{layer_id} has invalid target_parent")
        origin = require_dict(layer.get("origin_px"), f"{layer_id}.origin_px")
        require(isinstance(origin.get("x"), int) and isinstance(origin.get("y"), int), f"{layer_id} origin must be integer pixels")
        require(str(layer.get("anchor")), f"{layer_id} must define anchor")
        source_nodes = layer.get("source_nodes_3d")
        require(isinstance(source_nodes, list) and source_nodes, f"{layer_id} must define source_nodes_3d")
        for node_name in source_nodes:
            require(f'[node name="{node_name}" type="MeshInstance3D"' in scene_text, f"{layer_id} source node missing from scene: {node_name}")
        require(f'metadata/export_layer_id = "{layer_id}"' in scene_text, f"{layer_id} missing scene metadata/export_layer_id")

    required_scene_fragments = [
        '[node name="RegionHomeAreaBakeBlockout3D" type="Node3D"]',
        '[node name="BakeCamera" type="Camera3D"',
        '[node name="SunLight" type="DirectionalLight3D"',
        '[node name="ExportLayerGuides" type="Node3D"',
        'metadata/region_id = "Region_HomeArea"',
        'metadata/runtime_boundary = "offline_3d_source_only"',
        'metadata/bake_contract = "res://production/assets/regions/home_area_bake/region_home_area_bake_contract.json"',
    ]
    missing_fragments = [fragment for fragment in required_scene_fragments if fragment not in scene_text]
    require(not missing_fragments, f"scene missing required fragments: {missing_fragments}")

    print("OK: Region_HomeArea 3D bake contract validated")


if __name__ == "__main__":
    main()
