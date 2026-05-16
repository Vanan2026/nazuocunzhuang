from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "scenes" / "regions" / "region_home_area.tscn"
ART_ROOT = "res://production/assets/regions/home_area_art/v003"
MANIFEST = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v003" / "region_home_area_art_v003_manifest.json"

REQUIRED_SPRITES = {
    "ground_yard": ("GroundYardArtV003", "TileMapLayer_Ground/GroundModules", "Vector2(0, 0)", "ground_yard_art_v003"),
    "path_village_road": ("VillageRoadArtV003", "TileMapLayer_Path/PathModules", "Vector2(208, 488)", "path_village_road_art_v003"),
    "path_back_farm": ("BackFarmPathArtV003", "TileMapLayer_Path/PathModules", "Vector2(3477, 2338)", "path_back_farm_art_v003"),
    "veranda_floor": ("VerandaFloorArtV003", "TileMapLayer_Detail", "Vector2(2432, 1602)", "veranda_floor_art_v003"),
    "house_body": ("HouseBodyArtV003", "YSortWorld/Houses/CloudHouse", "Vector2(-928, -598)", "house_body_art_v003"),
    "tree_left_trunk": ("TreeLeftTrunkArtV003", "YSortWorld/Trees/BigShadeTree", "Vector2(-348, -518)", "tree_left_trunk_art_v003"),
    "tree_right_trunk": ("TreeRightTrunkArtV003", "YSortWorld/Trees/PersimmonTree", "Vector2(-348, -558)", "tree_right_trunk_art_v003"),
    "house_roof_occluder": ("HouseRoofOccluderArtV003", "ForegroundStatic/Occluders", "Vector2(1992, 727)", "house_roof_occluder_art_v003"),
    "tree_left_canopy_occluder": ("TreeLeftCanopyOccluderArtV003", "ForegroundStatic/Occluders", "Vector2(715, 432)", "tree_left_canopy_occluder_art_v003"),
    "tree_right_canopy_occluder": ("TreeRightCanopyOccluderArtV003", "ForegroundStatic/Occluders", "Vector2(4089, 816)", "tree_right_canopy_occluder_art_v003"),
    "foreground_grass": ("ForegroundGrassArtV003", "ForegroundStatic", "Vector2(0, 1915)", "foreground_grass_art_v003"),
    "shadow_dappled": ("ShadowDappledArtV003", "LightAndWeather", "Vector2(592, 739)", "shadow_dappled_art_v003"),
    "light_overlay": ("LightOverlayArtV003", "LightAndWeather", "Vector2(410, 708)", "light_overlay_art_v003"),
}

LEGACY_NODES = (
    ("GroundBase", "TileMapLayer_Ground"),
    ("GrassBaseNorth", "TileMapLayer_Ground/GroundModules"),
    ("GrassBaseHomeYard", "TileMapLayer_Ground/GroundModules"),
    ("GrassBaseSouth", "TileMapLayer_Ground/GroundModules"),
    ("GardenSoilWest", "TileMapLayer_Ground/GroundModules"),
    ("VillageRoadNorth", "TileMapLayer_Path"),
    ("HomeFrontYardPath", "TileMapLayer_Path"),
    ("SouthStonePath", "TileMapLayer_Path"),
    ("WestGardenPath", "TileMapLayer_Path"),
    ("VillageRoadNorthModule", "TileMapLayer_Path/PathModules"),
    ("HomeFrontYardPathModule", "TileMapLayer_Path/PathModules"),
    ("SouthStonePathModule", "TileMapLayer_Path/PathModules"),
    ("WestGardenPathModule", "TileMapLayer_Path/PathModules"),
    ("PebbleBand", "TileMapLayer_Detail"),
    ("FlowerPatchGuide", "TileMapLayer_Detail"),
    ("SoftTreeShadows", "GroundDecorations"),
    ("HouseShadow", "GroundDecorations"),
    ("HouseMain", "YSortWorld/Houses/CloudHouse"),
    ("HouseRoof", "YSortWorld/Houses/CloudHouse"),
    ("HouseEaves", "YSortWorld/Houses/CloudHouse"),
    ("DoorMarker", "YSortWorld/Houses/CloudHouse"),
    ("Canopy", "YSortWorld/Trees/PersimmonTree"),
    ("Trunk", "YSortWorld/Trees/PersimmonTree"),
    ("Canopy", "YSortWorld/Trees/BigShadeTree"),
    ("Trunk", "YSortWorld/Trees/BigShadeTree"),
    ("Canopy", "YSortWorld/Trees/SmallLeftTree"),
    ("Trunk", "YSortWorld/Trees/SmallLeftTree"),
    ("FrontGrassLeft", "ForegroundStatic"),
    ("FrontFlowersRight", "ForegroundStatic"),
    ("DappledLight", "LightAndWeather"),
    ("WindLeavesGuide", "LightAndWeather"),
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def node_block(scene_text: str, name: str, parent: str | None = None) -> str:
    if parent is None:
        header = rf'\[node name="{re.escape(name)}" [^\]]*\]'
    else:
        header = rf'\[node name="{re.escape(name)}" [^\]]*parent="{re.escape(parent)}"[^\]]*\]'
    match = re.search(header + r".*?(?=\n\[node |\n\[connection |\Z)", scene_text, re.S)
    if match is None:
        location = f"{parent}/{name}" if parent else name
        fail(f"missing node: {location}")
    return match.group(0)


def load_manifest_assets() -> dict[str, dict[str, Any]]:
    require(MANIFEST.exists(), f"missing manifest: {MANIFEST}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("layer_split_ready") is True, "v003 manifest must be split-ready before runtime integration")
    require(manifest.get("runtime_replacement") is False, "v003 manifest must not claim whole-plate replacement")
    assets = {record.get("asset_id"): record for record in manifest.get("assets", []) if isinstance(record, dict)}
    require("source_v002_base_full" in assets and assets["source_v002_base_full"].get("target_parent") == "art_review_only", "source_v002_base_full must stay review-only")
    return assets


def require_hidden(scene_text: str, name: str, parent: str) -> None:
    block = node_block(scene_text, name, parent)
    require("visible = false" in block, f"{parent}/{name} must be hidden after v003 runtime art integration")


def require_sprite(scene_text: str, asset_id: str, record: dict[str, Any]) -> None:
    node_name, parent, position, paint_id = REQUIRED_SPRITES[asset_id]
    file_name = record.get("file")
    require(isinstance(file_name, str), f"{asset_id} missing manifest file")
    texture_path = f"{ART_ROOT}/{file_name}"
    block = node_block(scene_text, node_name, parent)
    require(f'[node name="{node_name}" type="Sprite2D"' in block, f"{node_name} must be Sprite2D")
    require("centered = false" in block, f"{node_name} must use top-left source-space placement")
    require(f"position = {position}" in block, f"{node_name} must use manifest/runtime position {position}")
    require("texture = ExtResource" in block, f"{node_name} must bind an ExtResource texture")
    require('metadata/asset_package = "home_area_art_v003"' in block, f"{node_name} must record v003 art package")
    require(f'metadata/paint_id = "{paint_id}"' in block, f"{node_name} must record paint_id")
    require(texture_path in scene_text, f"{node_name} missing required texture asset path {texture_path}")
    require((ROOT / texture_path.removeprefix("res://")).exists(), f"missing texture file for {node_name}: {texture_path}")

    if asset_id in {"path_village_road", "path_back_farm", "veranda_floor"}:
        require("visible = false" not in block, f"{node_name} must be visible for v003 runtime review")


def main() -> None:
    require(SCENE.exists(), f"missing scene: {SCENE}")
    scene_text = SCENE.read_text(encoding="utf-8")
    manifest_assets = load_manifest_assets()
    root = node_block(scene_text, "Region_HomeArea")
    require('metadata/art_package = "home_area_art_v003"' in root, "Region_HomeArea must record active v003 art package")
    require('metadata/art_integration_group = "foundation_depth_v003"' in root, "Region_HomeArea must record v003 integration group")
    require("region_home_area_base_full_v002.png" not in scene_text, "runtime scene must not reference the opaque v002 full plate")
    require("region_home_area_base_full_v003.png" not in scene_text, "runtime scene must not reference the opaque v003 full plate")
    require("home_area_art/v002/region_home_area_" not in scene_text, "runtime scene must not reference v002 foundation/depth art")
    require("home_area_art/v001/region_home_area_" not in scene_text, "runtime scene must not reference v001 foundation/depth art")

    for asset_id in REQUIRED_SPRITES:
        require(asset_id in manifest_assets, f"manifest missing runtime asset: {asset_id}")
        require_sprite(scene_text, asset_id, manifest_assets[asset_id])

    for name, parent in LEGACY_NODES:
        require_hidden(scene_text, name, parent)

    print("OK: Region_HomeArea art v003 runtime foundation/depth integration validated")


if __name__ == "__main__":
    main()
