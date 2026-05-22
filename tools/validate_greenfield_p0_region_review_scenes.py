from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENE_DIR = ROOT / "scenes" / "dev" / "greenfield_p0_reviews"

REVIEW_REGIONS = [
    "home_area",
    "village",
    "back_farm",
    "forest_edge",
    "orchard",
    "pond",
    "mountain_path",
    "mountain_hut",
    "mountain",
    "cliff_view",
]
BATCH_A_REGIONS = REVIEW_REGIONS[:3]
WORLD_LAYOUT_SCENE = "greenfield_p0_world_layout_review"
REQUIRED_REGION_NODES = [
    "RuntimeLayerStack",
    "BaseGround",
    "TerrainDetails",
    "BehindPlayerStructures",
    "YSortPropsStructures",
    "ShadowOverlay",
    "ForegroundOcclusion",
    "LightWeatherOverlaySpring",
    "ReviewAnchors",
    "ReviewNotes",
]
BANNED_SOURCE_STRINGS = [
    "home_area_world2d/v001",
    "home_area_formal",
    "home_area_launch",
    "home_area_art/v",
    "region_home_area.before_",
    "manual_foreground_slices",
    "foreground_full_canvas",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_scene(path: Path) -> str:
    require(path.exists(), f"missing scene: {path}")
    return path.read_text(encoding="utf-8")


def validate_region_scene(region_id: str) -> None:
    path = SCENE_DIR / f"greenfield_p0_region_review_{region_id}.tscn"
    text = read_scene(path)
    require(f'metadata/region_id = "{region_id}"' in text, f"{region_id} missing region metadata")
    require('metadata/package_id = "greenfield_p0_base_asset_pack_v001"' in text, f"{region_id} missing package metadata")
    require("metadata/launch_quality_approved = false" in text, f"{region_id} must remain unapproved")
    require("metadata/human_visual_approval_required = true" in text, f"{region_id} must require human review")
    for node_name in REQUIRED_REGION_NODES:
        require(node_name in text, f"{region_id} missing node: {node_name}")
    for layer_name in [
        "base_ground",
        "terrain_details",
        "behind_player_structures",
        "ysort_props_structures",
        "shadow_overlay",
        "foreground_occlusion",
        "light_weather_overlay_spring",
    ]:
        require(f"assets/art/greenfield_p0/regions/{region_id}/layers/{region_id}_{layer_name}" in text, f"{region_id} missing layer path: {layer_name}")
    for banned in BANNED_SOURCE_STRINGS:
        require(banned not in text, f"{region_id} references banned old source: {banned}")


def validate_batch_scene(scene_name: str, region_ids: list[str]) -> None:
    path = SCENE_DIR / f"{scene_name}.tscn"
    text = read_scene(path)
    require('metadata/package_id = "greenfield_p0_base_asset_pack_v001"' in text, f"{scene_name} missing package metadata")
    require("metadata/launch_quality_approved = false" in text, f"{scene_name} must remain unapproved")
    for region_id in region_ids:
        require(f'[node name="{region_id}" type="Node2D" parent="RegionPreviews"]' in text, f"{scene_name} missing region preview: {region_id}")
        require(f"production/assets/base_asset_pack/v001/01_mother_images/regions/{region_id}/{region_id}_painted_source.png" in text, f"{scene_name} missing painted source: {region_id}")
    for banned in BANNED_SOURCE_STRINGS:
        require(banned not in text, f"batch scene references banned old source: {banned}")


def validate_world_layout_scene() -> None:
    path = SCENE_DIR / f"{WORLD_LAYOUT_SCENE}.tscn"
    text = read_scene(path)
    require('metadata/package_id = "greenfield_p0_base_asset_pack_v001"' in text, "world layout scene missing package metadata")
    require('metadata/status = "review_candidate"' in text, "world layout scene missing review candidate status")
    require("metadata/launch_quality_approved = false" in text, "world layout scene must remain unapproved")
    require("Connections" in text, "world layout scene missing Connections")
    require("RegionTiles" in text, "world layout scene missing RegionTiles")
    for region_id in REVIEW_REGIONS:
        require(f'[node name="{region_id}" type="Node2D" parent="RegionTiles"]' in text, f"world layout missing region tile: {region_id}")
        require(f'metadata/region_id = "{region_id}"' in text, f"world layout missing region metadata: {region_id}")
    for required in [
        "home_village_daily_lane",
        "home_farm_work_lane",
        "forest_orchard_link",
        "ridge_hut_link",
        "hut_pond_supply_path",
    ]:
        require(required in text, f"world layout missing route role: {required}")
    for banned in BANNED_SOURCE_STRINGS:
        require(banned not in text, f"world layout scene references banned old source: {banned}")


def main() -> None:
    for region_id in REVIEW_REGIONS:
        validate_region_scene(region_id)
    validate_batch_scene("greenfield_p0_region_review_batch_a", BATCH_A_REGIONS)
    validate_batch_scene("greenfield_p0_region_review_all", REVIEW_REGIONS)
    validate_world_layout_scene()
    print("OK: greenfield P0 region review scenes validate")


if __name__ == "__main__":
    main()
