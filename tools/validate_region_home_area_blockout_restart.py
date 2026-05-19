from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "production" / "assets" / "regions" / "home_area_blockout" / "v001" / "region_home_area_blockout_manifest.json"
SCENE = ROOT / "scenes" / "dev" / "region_home_area_blockout_3d_v002.tscn"
PROMPT_PACK = ROOT / "production" / "assets" / "regions" / "home_area_blockout" / "v001" / "region_home_area_blockout_prompt_pack.md"
REVIEW_IMAGE = ROOT / "production" / "assets" / "regions" / "home_area_blockout" / "v001" / "region_home_area_blockout_review.png"
CODEX_REVIEW_IMAGE = ROOT / ".codex" / "home_area_blockout_v001_review.png"
LAYOUT = ROOT / "production" / "assets" / "regions" / "home_area_design" / "region_home_area_layout_v001.json"

REQUIRED_ZONES = {
    "north_village_road",
    "house_veranda",
    "front_yard_walkable",
    "west_garden",
    "back_farm_path",
    "left_tree",
    "right_tree",
    "foreground_edges",
    "light_weather",
}

REQUIRED_INTERACTIONS = {
    "home_area_default_spawn",
    "homearea_house_door_001",
    "homearea_mailbox_001",
    "homearea_well_001",
    "homearea_bench_rest_001",
    "homearea_roadsign_001",
    "home_area_to_back_farm",
}

REQUIRED_LAYER_IDS = {
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

SCENE_NODE_REQUIREMENTS = [
    "RegionHomeAreaBlockout3DV002",
    "BlockoutReviewCamera",
    "SunLight",
    "RegionPlane",
    "ZoneGuides",
    "NorthVillageRoad",
    "CentralFrontYard",
    "WestGarden",
    "BackFarmPath",
    "HouseBlock",
    "HouseRoofOccluderBlock",
    "VerandaFloorBlock",
    "LeftShadeTreeTrunk",
    "LeftShadeTreeCanopy",
    "RightPersimmonTreeTrunk",
    "RightPersimmonTreeCanopy",
    "ForegroundReviewBoundaryGuide",
    "ForegroundLeftOccluderGuide",
    "ForegroundRightOccluderGuide",
    "ForegroundBottomTuftGuide",
    "ForegroundClearPlayerCorridorGuide",
    "LightOverlayGuide",
    "MainDoorPathGuide",
    "YardLoopPathGuide",
    "HouseDoorScaleGuide",
    "InteractionMarkers",
    "PropScaleGuides",
    "MailboxScaleGuide",
    "WellScaleGuide",
    "BenchScaleGuide",
    "BenchBackScaleGuide",
    "WellRoofScaleGuide",
    "WellLeftPostScaleGuide",
    "WellRightPostScaleGuide",
    "PlayerScaleGuides",
    "DefaultSpawnPlayerScaleGuide",
    "DoorPlayerScaleGuide",
    "DefaultSpawn",
    "HouseDoor",
    "Mailbox",
    "Well",
    "BenchRest",
    "RoadSign",
    "BackFarmExit",
]


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
    for path in (MANIFEST, SCENE, PROMPT_PACK, REVIEW_IMAGE, CODEX_REVIEW_IMAGE, LAYOUT):
        require(path.exists(), f"missing required blockout file: {path.relative_to(ROOT).as_posix()}")

    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "manifest")
    require(manifest.get("region_id") == "Region_HomeArea", "manifest region_id must be Region_HomeArea")
    require(manifest.get("package_id") == "home_area_blockout_v001", "manifest package_id must be home_area_blockout_v001")
    require(manifest.get("status") == "blockout_review_candidate", "blockout status must be review candidate")
    require(manifest.get("approval_status") in {"needs_human_review", "approved_for_v005_generation"}, "blockout approval_status must be review-pending or approved for v005 generation")
    require(manifest.get("runtime_boundary") == "offline_blockout_review_only", "blockout must be offline review only")
    require(manifest.get("runtime_import_mode_after_approval") == "layered_2d_png", "approved blockout must feed layered 2D PNG production")
    require(manifest.get("canvas_px") == {"width": 6144, "height": 4096}, "canvas must match Region_HomeArea")

    unit_mapping = require_dict(manifest.get("unit_mapping"), "unit_mapping")
    require(unit_mapping.get("pixels_per_meter") == 100, "pixels_per_meter must be 100")
    require(unit_mapping.get("origin") == "region_top_left", "unit origin must be region_top_left")

    camera = require_dict(manifest.get("review_camera"), "review_camera")
    require(camera.get("node_path") == "RegionHomeAreaBlockout3DV002/BlockoutReviewCamera", "review camera node path changed unexpectedly")
    require(camera.get("projection") == "orthogonal_oblique", "review camera must be orthogonal oblique")

    zone_ids = {zone.get("id") for zone in manifest.get("zones", []) if isinstance(zone, dict)}
    require(REQUIRED_ZONES <= zone_ids, f"missing zones from blockout manifest: {sorted(REQUIRED_ZONES - zone_ids)}")
    interaction_ids = {point.get("id") for point in manifest.get("interaction_points", []) if isinstance(point, dict)}
    require(REQUIRED_INTERACTIONS <= interaction_ids, f"missing interaction points: {sorted(REQUIRED_INTERACTIONS - interaction_ids)}")

    layer_ids = {layer.get("asset_id") for layer in manifest.get("required_2d_layer_contract", []) if isinstance(layer, dict)}
    require(REQUIRED_LAYER_IDS <= layer_ids, f"missing required v005 layer contracts: {sorted(REQUIRED_LAYER_IDS - layer_ids)}")
    for layer in manifest.get("required_2d_layer_contract", []):
        layer = require_dict(layer, "layer contract")
        require(str(layer.get("file", "")).endswith("_v005.png"), f"{layer.get('asset_id')} must reserve a v005 PNG filename")
        require(layer.get("status") == "not_generated_until_blockout_approval", f"{layer.get('asset_id')} must not be marked generated before approval")

    scene_text = SCENE.read_text(encoding="utf-8")
    for node_name in SCENE_NODE_REQUIREMENTS:
        require(f'[node name="{node_name}"' in scene_text, f"missing blockout scene node: {node_name}")
    for fragment in [
        'metadata/runtime_boundary = "offline_blockout_review_only"',
        'metadata/approval_status = "needs_human_review"',
        'metadata/layout_contract = "res://production/assets/regions/home_area_design/region_home_area_layout_v001.json"',
        'metadata/blockout_manifest = "res://production/assets/regions/home_area_blockout/v001/region_home_area_blockout_manifest.json"',
        'metadata/export_layer_id = "house_body"',
        'metadata/export_layer_id = "house_roof_occluder"',
        'metadata/export_layer_id = "foreground_grass_boundary"',
    ]:
        require(fragment in scene_text, f"blockout scene missing metadata fragment: {fragment}")
    for interaction_id in REQUIRED_INTERACTIONS:
        require(f'metadata/interaction_id = "{interaction_id}"' in scene_text, f"scene missing interaction marker: {interaction_id}")
    for fragment in [
        'metadata/scale_contract = "mailbox top reaches protagonist waist/chest range, not ankle-height icon scale"',
        'metadata/scale_contract = "well is a substantial yard landmark with readable base, roof, and posts"',
        'metadata/scale_contract = "bench seats one or two characters and aligns to veranda/front-yard rest area"',
    ]:
        require(fragment in scene_text, f"blockout scene missing prop scale fragment: {fragment}")


    require(manifest.get("blockout_revision") == "v002_scale_composition_pass", "manifest must record the current scale/composition pass")
    player_contract = require_dict(manifest.get("player_scale_contract"), "player_scale_contract")
    require(player_contract.get("visible_body_height_m") == 2.15, "player scale guide height must match the blockout contract")
    require("PlayerScaleGuides/DefaultSpawnPlayerScaleGuide" in player_contract.get("guide_nodes", []), "missing default spawn player scale guide contract")
    path_contracts = manifest.get("path_review_contract", [])
    require(isinstance(path_contracts, list) and len(path_contracts) >= 2, "path review contracts must include door and yard loop guides")
    foreground_contracts = manifest.get("foreground_occlusion_contract", [])
    require(isinstance(foreground_contracts, list) and len(foreground_contracts) >= 4, "foreground occlusion contracts must be split into edge modules plus clear corridor")

    prop_contracts = manifest.get("prop_scale_contract", [])
    require(isinstance(prop_contracts, list), "manifest prop_scale_contract must be a list")
    prop_ids = {record.get("asset_id") for record in prop_contracts if isinstance(record, dict)}
    require({"mailbox", "well", "bench"} <= prop_ids, "blockout must include mailbox/well/bench prop scale contracts")
    for record in prop_contracts:
        record = require_dict(record, "prop scale contract")
        require(str(record.get("guide_node", "")).startswith("PropScaleGuides/"), "prop scale contract must point to a PropScaleGuides node")
        require("rule" in record and str(record.get("rule")), "prop scale contract must include a readable rule")

    prompt = PROMPT_PACK.read_text(encoding="utf-8")
    require("Do not collage v002-v004 repair layers" in prompt, "prompt pack must forbid v002-v004 collage promotion")
    require("Full plate is review-only" in prompt, "prompt pack must keep full plate review-only")

    for image_path in (REVIEW_IMAGE, CODEX_REVIEW_IMAGE):
        image = Image.open(image_path)
        require(image.size == (1536, 1024), f"review image must be 1536x1024: {image_path.relative_to(ROOT).as_posix()}")

    print("OK: HomeArea 3D blockout restart contract validated")


if __name__ == "__main__":
    main()