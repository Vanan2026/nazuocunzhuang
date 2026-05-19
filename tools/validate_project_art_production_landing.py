from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
DOC = ROOT / "docs/13_ART_PRODUCTION_LANDING.md"
WORLD_CONTROLLER = ROOT / "scripts/world/world_controller.gd"
HOME_SCENE = ROOT / "scenes/regions/region_home_area.tscn"
BACK_FARM_SCENE = ROOT / "scenes/regions/region_back_farm.tscn"
ITEMS = ROOT / "game/data/items.json"
CROPS = ROOT / "game/data/crops.json"
NPCS = ROOT / "game/data/npcs.json"

EXPECTED_REGIONS = {
    "Region_HomeArea",
    "Region_Village",
    "Region_BackFarm",
    "Region_MountainPath",
    "Region_MountainHut",
    "Region_Mountain",
    "Region_CliffView",
    "Region_ForestEdge",
    "Region_Orchard",
    "Region_Pond",
}

FORBIDDEN_ACTIVE_SCENE_TOKENS = [
    "production/assets/regions/home_area_art/",
    "production/assets/regions/home_area_launch/",
    "production/assets/regions/home_area_launch_quality/",
    "production/assets/regions/home_area_formal/",
]

REQUIRED_VALIDATORS = [
    "tools/validate_project_art_production_landing.py",
    "tools/validate_home_area_world2d_v001.py",
    "tools/validate_region_back_farm_art_v002.py",
    "tools/validate_protagonist_runtime_manifest.py",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path, label: str) -> Any:
    require(path.exists(), f"missing {label}: {path.relative_to(ROOT).as_posix()}")
    return json.loads(path.read_text(encoding="utf-8"))


def as_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def res_path_exists(res_path: str) -> bool:
    require(res_path.startswith("res://"), f"expected res:// path, got {res_path}")
    return (ROOT / res_path.removeprefix("res://")).exists()


def manifest_entry_by_id(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = manifest.get("current_runtime_regions")
    require(isinstance(entries, list), "current_runtime_regions must be a list")
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        record = as_dict(entry, "region entry")
        region_id = str(record.get("region_id", ""))
        require(region_id, "region entry missing region_id")
        require(region_id not in by_id, f"duplicate region entry: {region_id}")
        by_id[region_id] = record
    return by_id


def validate_registered_regions(by_id: dict[str, dict[str, Any]]) -> None:
    text = WORLD_CONTROLLER.read_text(encoding="utf-8")
    registered = set(re.findall(r'"region_id"\s*:\s*"([^"]+)"', text))
    require(registered == EXPECTED_REGIONS, f"registered region set changed: {sorted(registered)}")
    require(set(by_id) == registered, f"manifest region rows do not match WorldController: {sorted(set(by_id) ^ registered)}")
    for region_id, record in by_id.items():
        scene = ROOT / str(record.get("scene", ""))
        require(scene.exists(), f"missing scene for {region_id}: {record.get('scene')}")
        require(record.get("launch_quality_approved") is False, f"{region_id} must not claim launch-quality approval")


def validate_active_region_packages(by_id: dict[str, dict[str, Any]]) -> None:
    home = by_id["Region_HomeArea"]
    require(home.get("phase") == "source_first_layer_package_integrated_pending_capture", "HomeArea phase mismatch")
    require(home.get("runtime_scene_reference_allowed") is True, "HomeArea scene reference flag mismatch")
    require(home.get("human_visual_approval_required") is True, "HomeArea must require human review")
    require((ROOT / str(home["active_package"])).exists(), "HomeArea active package missing")
    require((ROOT / str(home["active_layer_package"])).exists(), "HomeArea layer package missing")

    back = by_id["Region_BackFarm"]
    require(back.get("phase") == "active_structural_placeholder_not_launch_quality", "BackFarm phase mismatch")
    require(back.get("runtime_scene_reference_allowed") is True, "BackFarm scene reference flag mismatch")
    require(back.get("human_visual_approval_required") is True, "BackFarm must require human review")
    require((ROOT / str(back["active_package"])).exists(), "BackFarm active package missing")

    for region_id, record in by_id.items():
        if region_id in {"Region_HomeArea", "Region_BackFarm"}:
            continue
        require(record.get("phase") == "graybox_scene_needs_source_package", f"{region_id} must remain an explicit art backlog row")
        require(str(record.get("required_package_dir", "")).startswith("production/assets/regions/"), f"{region_id} missing required package dir")


def validate_active_scenes_do_not_use_rejected_paths() -> None:
    for scene in [HOME_SCENE, BACK_FARM_SCENE]:
        text = scene.read_text(encoding="utf-8-sig")
        for token in FORBIDDEN_ACTIVE_SCENE_TOKENS:
            require(token not in text, f"{scene.relative_to(ROOT).as_posix()} references rejected art path: {token}")


def validate_runtime_asset_groups(manifest: dict[str, Any]) -> None:
    groups = manifest.get("runtime_asset_groups")
    require(isinstance(groups, list), "runtime_asset_groups must be a list")
    by_id = {str(as_dict(group, "asset group").get("id")): as_dict(group, "asset group") for group in groups}
    for required in ["crop_stage_sprites", "weather_icons", "ui_base_pieces", "item_icons", "home_area_props"]:
        require(required in by_id, f"missing runtime asset group: {required}")

    crops = read_json(CROPS, "crop data")
    require(isinstance(crops, list) and crops, "crop data must be a non-empty list")
    for crop in crops:
        record = as_dict(crop, "crop record")
        for sprite_path in record.get("stage_sprites", []):
            require(res_path_exists(str(sprite_path)), f"missing crop stage sprite: {sprite_path}")

    items = read_json(ITEMS, "item data")
    missing_item_icons = []
    for item in items:
        record = as_dict(item, "item record")
        icon = str(record.get("icon", ""))
        if icon and not res_path_exists(icon):
            missing_item_icons.append(icon)
    require(missing_item_icons, "expected explicit item icon backlog, but all item icons currently resolve")
    require(by_id["item_icons"].get("status") == "known_gap_partial_crop_icons_only", "item icon gap must remain explicit")

    npcs = read_json(NPCS, "npc data")
    npc_ids = {str(as_dict(npc, "npc record").get("npc_id")) for npc in npcs}
    character_assets = as_dict(manifest.get("character_assets"), "character_assets")
    mvp_npcs = as_dict(character_assets.get("mvp_npcs"), "mvp_npcs")
    covered = set(mvp_npcs.get("covered_npc_ids", []))
    missing = set(mvp_npcs.get("missing_npc_ids", []))
    require({"aoi", "gen", "mika"} <= covered, "Aoi/Gen/Mika coverage must be explicit")
    require("hana" in missing and "hana" in npc_ids, "Hana art backlog must be explicit")
    for npc_id in covered:
        require((ROOT / f"assets/art/characters/npc/npc_{npc_id}_idle_down_128.png").exists(), f"missing NPC idle sprite: {npc_id}")
        require((ROOT / f"assets/art/portraits/npc_{npc_id}_portrait_neutral_512.png").exists(), f"missing NPC portrait: {npc_id}")


def validate_manifest_structure(manifest: dict[str, Any]) -> None:
    require(manifest.get("package_id") == "project_art_production_landing_2026_05_19", "package_id mismatch")
    require(manifest.get("status") == "active_production_landing_not_launch_approval", "status mismatch")
    require(manifest.get("runtime_entry") == "res://scenes/world/world.tscn", "runtime entry mismatch")
    require(DOC.exists(), "missing docs/13_ART_PRODUCTION_LANDING.md")
    for validator in REQUIRED_VALIDATORS:
        require((ROOT / validator).exists(), f"missing validation entrypoint: {validator}")
    character_assets = as_dict(manifest.get("character_assets"), "character_assets")
    protagonist = as_dict(character_assets.get("protagonist"), "protagonist")
    require((ROOT / str(protagonist.get("manifest"))).exists(), "protagonist runtime manifest missing")
    require((ROOT / str(protagonist.get("runtime_sprite_frames"))).exists(), "protagonist runtime SpriteFrames missing")
    known_gaps = {str(as_dict(gap, "known gap").get("id")) for gap in manifest.get("known_runtime_gaps", [])}
    for required_gap in ["item_icon_backlog", "hana_npc_art_backlog", "remaining_region_world2d_packages"]:
        require(required_gap in known_gaps, f"missing known runtime gap: {required_gap}")


def main() -> None:
    manifest = as_dict(read_json(MANIFEST, "project art production manifest"), "project art production manifest")
    validate_manifest_structure(manifest)
    by_id = manifest_entry_by_id(manifest)
    validate_registered_regions(by_id)
    validate_active_region_packages(by_id)
    validate_active_scenes_do_not_use_rejected_paths()
    validate_runtime_asset_groups(manifest)
    print("OK: project art production landing manifest validates registered regions, active art packages, and explicit runtime gaps")


if __name__ == "__main__":
    main()
