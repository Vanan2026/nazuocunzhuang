from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "production" / "assets" / "regions" / "home_area_bake" / "region_home_area_bake_contract.json"
SCENE = ROOT / "scenes" / "dev" / "region_home_area_bake_blockout_3d.tscn"
VALIDATOR = ROOT / "tools" / "validate_region_home_area_bake_contract.py"

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

REQUIRED_SCENE_MARKERS = {
    '[node name="RegionHomeAreaBakeBlockout3D" type="Node3D"]',
    '[node name="BakeCamera" type="Camera3D"',
    '[node name="SunLight" type="DirectionalLight3D"',
    '[node name="ExportLayerGuides" type="Node3D"',
    'metadata/region_id = "Region_HomeArea"',
    'metadata/runtime_boundary = "offline_3d_source_only"',
    'metadata/bake_contract = "res://production/assets/regions/home_area_bake/region_home_area_bake_contract.json"',
}


def test_home_area_bake_contract_exists_and_defines_required_layers() -> None:
    assert CONTRACT.exists(), f"missing bake contract: {CONTRACT}"

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["region_id"] == "Region_HomeArea"
    assert contract["runtime_boundary"] == "offline_3d_source_only"
    assert contract["runtime_import_mode"] == "layered_2d_png"
    assert contract["canvas_px"] == {"width": 6144, "height": 4096}
    assert contract["unit_mapping"]["pixels_per_meter"] == 100

    layer_ids = {layer["id"] for layer in contract["export_layers"]}
    missing = REQUIRED_LAYER_IDS - layer_ids
    assert not missing, f"missing required export layers: {sorted(missing)}"

    for layer in contract["export_layers"]:
        assert layer["export_name"].startswith("region_home_area_")
        assert layer["export_name"].endswith("_v001.png")
        assert layer["target_parent"] in {
            "TileMapLayer_Ground/GroundModules",
            "TileMapLayer_Path/PathModules",
            "YSortWorld/Houses",
            "YSortWorld/Trees",
            "ForegroundStatic",
            "LightAndWeather",
        }
        assert "origin_px" in layer and {"x", "y"} <= set(layer["origin_px"])
        assert "anchor" in layer
        assert "source_nodes_3d" in layer and layer["source_nodes_3d"]


def test_home_area_bake_blockout_scene_exists_and_links_contract() -> None:
    assert SCENE.exists(), f"missing Godot 3D bake blockout scene: {SCENE}"

    scene_text = SCENE.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_SCENE_MARKERS if marker not in scene_text]
    assert not missing, f"missing scene markers: {missing}"

    required_nodes = [
        "GroundPlane",
        "HomeFrontYardPath",
        "CloudHouseBody",
        "CloudHouseRoofOccluder",
        "LeftShadeTreeTrunk",
        "LeftShadeTreeCanopy",
        "RightPersimmonTreeTrunk",
        "RightPersimmonTreeCanopy",
        "ForegroundGrassLeftGuide",
        "DappledLightGuide",
    ]
    for node_name in required_nodes:
        assert f'[node name="{node_name}" type="MeshInstance3D"' in scene_text, f"missing MeshInstance3D: {node_name}"


def test_home_area_bake_validator_script_exists() -> None:
    assert VALIDATOR.exists(), f"missing validator: {VALIDATOR}"
    text = VALIDATOR.read_text(encoding="utf-8")
    required_fragments = [
        "region_home_area_bake_contract.json",
        "region_home_area_bake_blockout_3d.tscn",
        "REQUIRED_LAYER_IDS",
        "OK: Region_HomeArea 3D bake contract validated",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert not missing, f"validator missing fragments: {missing}"


if __name__ == "__main__":
    tests = [
        test_home_area_bake_contract_exists_and_defines_required_layers,
        test_home_area_bake_blockout_scene_exists_and_links_contract,
        test_home_area_bake_validator_script_exists,
    ]
    failures: list[str] = []
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            failures.append(f"{test.__name__}: {exc}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)

    print("OK: Region_HomeArea 3D bake contract tests passed")
