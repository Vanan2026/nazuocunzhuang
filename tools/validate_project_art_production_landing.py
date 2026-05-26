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
    "tools/validate_outdoor_world_seamless_art_master.py",
    "tools/validate_mountain_hut_world2d_art_prep.py",
    "tools/validate_mountain_hut_painted_source_candidate.py",
    "tools/validate_mountain_hut_source_quality_gate.py",
    "tools/validate_mountain_hut_v002_source_candidate.py",
    "tools/validate_home_area_world2d_v001.py",
    "tools/validate_region_back_farm_art_v002.py",
    "tools/validate_protagonist_runtime_manifest.py",
    "tools/validate_complete_p0_asset_package.py",
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

    village = by_id["Region_Village"]
    village_layer_manifest_phases = {
        "village_layers_exported_pending_review",
        "village_layers_rejected_semantic_rework_required",
        "village_semantic_layers_exported_pending_review",
        "v002_inherited_crop_candidate_ready_for_visual_review",
        "v002_codex_visual_accepted_for_semantic_layer_export",
        "v002_semantic_layers_exported_pending_review",
    }
    require(
        village.get("phase") in {"village_plaza_art_prep_package_ready", *village_layer_manifest_phases},
        "Village phase mismatch",
    )
    require(village.get("runtime_replacement") is False, "Village must keep runtime_replacement=false")
    require(village.get("human_visual_approval_required") is True, "Village must require human review")
    require((ROOT / str(village["active_package"])).exists(), "Village active package missing")
    require((ROOT / str(village["required_package_dir"])).exists(), "Village required package dir missing")
    if village.get("phase") in village_layer_manifest_phases:
        require((ROOT / str(village.get("active_layer_manifest", ""))).exists(), "Village active layer manifest missing")
    if village.get("phase") == "v002_inherited_crop_candidate_ready_for_visual_review":
        require((ROOT / str(village.get("active_inherited_repaint_handoff", ""))).exists(), "Village inherited repaint handoff missing")
        require((ROOT / str(village.get("active_v002_source_candidate", ""))).exists(), "Village v002 source candidate missing")
        require((ROOT / str(village.get("active_v002_quality_review", ""))).exists(), "Village v002 quality review missing")
        require((ROOT / str(village.get("active_v002_review_contact_sheet", ""))).exists(), "Village v002 contact sheet missing")
        require("inherited repaint" in str(village.get("next_art_step", "")), "Village next step must mention inherited repaint")
    if village.get("phase") in {
        "v002_codex_visual_accepted_for_semantic_layer_export",
        "v002_semantic_layers_exported_pending_review",
    }:
        require((ROOT / str(village.get("active_inherited_repaint_handoff", ""))).exists(), "Village inherited repaint handoff missing")
        require((ROOT / str(village.get("active_v002_source_candidate", ""))).exists(), "Village v002 source candidate missing")
        require((ROOT / str(village.get("active_v002_quality_review", ""))).exists(), "Village v002 quality review missing")
        require((ROOT / str(village.get("active_v002_review_contact_sheet", ""))).exists(), "Village v002 contact sheet missing")
        require((ROOT / str(village.get("active_v002_visual_review", ""))).exists(), "Village v002 visual review missing")
    if village.get("phase") == "v002_semantic_layers_exported_pending_review":
        require((ROOT / str(village.get("active_v002_layer_manifest", ""))).exists(), "Village v002 layer manifest missing")
        require("semantic layers" in str(village.get("next_art_step", "")), "Village next step must point to semantic layer review")

    mountain_hut = by_id["Region_MountainHut"]
    mountain_hut_source_phases = {
        "mountain_hut_source_candidate_pending_review",
        "mountain_hut_source_candidate_needs_repaint",
        "mountain_hut_v002_candidate_ready_for_human_art_review",
        "mountain_hut_v002_visual_review_rejected_needs_v003_repaint",
        "mountain_hut_v003_candidate_ready_for_visual_review",
        "mountain_hut_v004_candidate_ready_for_visual_review",
        "v004_semantic_layers_exported_pending_review",
    }
    require(
        mountain_hut.get("phase") in {"mountain_hut_art_prep_package_ready", *mountain_hut_source_phases},
        "MountainHut phase mismatch",
    )
    require(mountain_hut.get("runtime_replacement") is False, "MountainHut must keep runtime_replacement=false")
    require(mountain_hut.get("human_visual_approval_required") is True, "MountainHut must require human review")
    require(
        mountain_hut.get("active_package") == "production/assets/regions/mountain_hut_world2d/v001/workflow_manifest.json",
        "MountainHut active package mismatch",
    )
    require(
        mountain_hut.get("active_seam_brief") == "production/assets/seams/village_to_mountain_hut/v001/seam_brief.md",
        "MountainHut active seam brief mismatch",
    )
    require((ROOT / str(mountain_hut["active_package"])).exists(), "MountainHut active package missing")
    require((ROOT / str(mountain_hut["required_package_dir"])).exists(), "MountainHut required package dir missing")
    require((ROOT / str(mountain_hut["active_seam_brief"])).exists(), "MountainHut active seam brief missing")
    if mountain_hut.get("phase") in mountain_hut_source_phases:
        require((ROOT / str(mountain_hut.get("active_source_candidate", ""))).exists(), "MountainHut active source candidate missing")
        require((ROOT / str(mountain_hut.get("active_source_review", ""))).exists(), "MountainHut active source review missing")
    if mountain_hut.get("phase") == "mountain_hut_source_candidate_needs_repaint":
        require((ROOT / str(mountain_hut.get("active_source_quality_review", ""))).exists(), "MountainHut source quality review missing")
        require((ROOT / str(mountain_hut.get("active_repaint_reference_board", ""))).exists(), "MountainHut repaint reference board missing")
        require((ROOT / str(mountain_hut.get("active_repaint_brief", ""))).exists(), "MountainHut repaint brief missing")
        require("v002 repaint" in str(mountain_hut.get("next_art_step", "")), "MountainHut next step must point to v002 repaint")
    if mountain_hut.get("phase") == "mountain_hut_v002_candidate_ready_for_human_art_review":
        require((ROOT / str(mountain_hut.get("active_v002_source_candidate", ""))).exists(), "MountainHut v002 source candidate missing")
        require((ROOT / str(mountain_hut.get("active_v002_quality_review", ""))).exists(), "MountainHut v002 quality review missing")
        require((ROOT / str(mountain_hut.get("active_v002_review_contact_sheet", ""))).exists(), "MountainHut v002 contact sheet missing")
        require("human/art review" in str(mountain_hut.get("next_art_step", "")), "MountainHut next step must point to v002 human/art review")
    if mountain_hut.get("phase") == "mountain_hut_v002_visual_review_rejected_needs_v003_repaint":
        require((ROOT / str(mountain_hut.get("active_v002_source_candidate", ""))).exists(), "MountainHut v002 source candidate missing")
        require((ROOT / str(mountain_hut.get("active_v002_quality_review", ""))).exists(), "MountainHut v002 quality review missing")
        require((ROOT / str(mountain_hut.get("active_v002_visual_review", ""))).exists(), "MountainHut v002 visual review missing")
        require((ROOT / str(mountain_hut.get("active_v003_repaint_brief", ""))).exists(), "MountainHut v003 repaint brief missing")
        require((ROOT / str(mountain_hut.get("active_v003_reference_sheet", ""))).exists(), "MountainHut v003 reference sheet missing")
        require("v003" in str(mountain_hut.get("next_art_step", "")), "MountainHut next step must point to v003 repaint")
    if mountain_hut.get("phase") == "mountain_hut_v003_candidate_ready_for_visual_review":
        require((ROOT / str(mountain_hut.get("active_v002_source_candidate", ""))).exists(), "MountainHut v002 source candidate missing")
        require((ROOT / str(mountain_hut.get("active_v002_quality_review", ""))).exists(), "MountainHut v002 quality review missing")
        require((ROOT / str(mountain_hut.get("active_v003_source_candidate", ""))).exists(), "MountainHut v003 source candidate missing")
        require((ROOT / str(mountain_hut.get("active_v003_quality_review", ""))).exists(), "MountainHut v003 quality review missing")
        require((ROOT / str(mountain_hut.get("active_v003_review_contact_sheet", ""))).exists(), "MountainHut v003 contact sheet missing")
        require("visual review" in str(mountain_hut.get("next_art_step", "")), "MountainHut next step must point to v003 visual review")
    if mountain_hut.get("phase") == "mountain_hut_v004_candidate_ready_for_visual_review":
        require((ROOT / str(mountain_hut.get("active_v003_visual_review", ""))).exists(), "MountainHut v003 visual review missing")
        require((ROOT / str(mountain_hut.get("active_v004_source_candidate", ""))).exists(), "MountainHut v004 source candidate missing")
        require((ROOT / str(mountain_hut.get("active_v004_quality_review", ""))).exists(), "MountainHut v004 quality review missing")
        require((ROOT / str(mountain_hut.get("active_v004_review_contact_sheet", ""))).exists(), "MountainHut v004 contact sheet missing")
        require("visual review" in str(mountain_hut.get("next_art_step", "")), "MountainHut next step must point to v004 visual review")
    if mountain_hut.get("phase") == "v004_semantic_layers_exported_pending_review":
        require((ROOT / str(mountain_hut.get("active_v004_source_candidate", ""))).exists(), "MountainHut v004 source candidate missing")
        require((ROOT / str(mountain_hut.get("active_v004_visual_review", ""))).exists(), "MountainHut v004 visual review missing")
        require((ROOT / str(mountain_hut.get("active_layer_manifest", ""))).exists(), "MountainHut active layer manifest missing")
        require("semantic layers" in str(mountain_hut.get("next_art_step", "")), "MountainHut next step must point to semantic layer review")

    for region_id, record in by_id.items():
        if region_id in {"Region_HomeArea", "Region_BackFarm", "Region_Village", "Region_MountainHut"}:
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
    item_status = by_id["item_icons"].get("status")
    if missing_item_icons:
        require(item_status == "known_gap_partial_crop_icons_only", "item icon gap must remain explicit while icons are missing")
    else:
        require(item_status == "runtime_files_present_for_current_item_data", "item icon group must record resolved runtime files when all icons exist")
        require((ROOT / "production/assets/items/p0_item_icons/v001/p0_item_icons_manifest.json").exists(), "resolved item icon package manifest missing")

    npcs = read_json(NPCS, "npc data")
    npc_ids = {str(as_dict(npc, "npc record").get("npc_id")) for npc in npcs}
    character_assets = as_dict(manifest.get("character_assets"), "character_assets")
    mvp_npcs = as_dict(character_assets.get("mvp_npcs"), "mvp_npcs")
    required_ids = set(mvp_npcs.get("required_npc_ids", []))
    npc_status = mvp_npcs.get("status")
    require(npc_status in {"complete_runtime_package_backlog", "complete_runtime_package_usable"}, "P0 NPCs must use complete runtime package backlog or usable status")
    if npc_status == "complete_runtime_package_usable":
        require((ROOT / "production/assets/characters/p0_npc_complete_runtime/v001/p0_npc_complete_runtime_manifest.json").exists(), "resolved P0 NPC package manifest missing")
        require(set(mvp_npcs.get("covered_npc_ids", [])) == {"aoi", "gen", "mika", "hana"}, "complete P0 NPC covered ids mismatch")
        require(not mvp_npcs.get("missing_npc_ids", []), "complete P0 NPC package should not list missing NPC ids")
    require({"aoi", "gen", "mika", "hana"} <= required_ids, "complete P0 NPC backlog must cover Aoi/Gen/Mika/Hana")
    require(required_ids <= npc_ids, f"manifest references unknown NPC ids: {sorted(required_ids - npc_ids)}")
    package = as_dict(mvp_npcs.get("required_runtime_package"), "required_runtime_package")
    require(set(package.get("sprites", [])) == {"idle_down", "idle_up", "idle_left", "idle_right", "walk_down", "walk_up", "walk_left", "walk_right"}, "P0 NPC sprite package must include 4-direction idle and walk")
    require(set(package.get("portraits", [])) == {"neutral", "happy", "thinking"}, "P0 NPC portrait package must include neutral/happy/thinking")


def validate_manifest_structure(manifest: dict[str, Any]) -> None:
    require(manifest.get("package_id") == "project_art_production_landing_2026_05_19", "package_id mismatch")
    require(manifest.get("status") == "active_production_landing_not_launch_approval", "status mismatch")
    require(manifest.get("runtime_entry") == "res://scenes/world/world.tscn", "runtime entry mismatch")
    require(DOC.exists(), "missing docs/13_ART_PRODUCTION_LANDING.md")
    for validator in REQUIRED_VALIDATORS:
        require((ROOT / validator).exists(), f"missing validation entrypoint: {validator}")
    seamless = as_dict(manifest.get("seamless_outdoor_world"), "seamless_outdoor_world")
    require(seamless.get("active_runtime_scene") == "res://game/scenes/world/OutdoorWorld.tscn", "seamless OutdoorWorld scene mismatch")
    require(seamless.get("active_package") == "production/assets/outdoor_world_world2d/v001/workflow_manifest.json", "seamless OutdoorWorld active package mismatch")
    require((ROOT / str(seamless.get("active_package"))).exists(), "seamless OutdoorWorld package missing")
    require(seamless.get("runtime_replacement") is False, "seamless OutdoorWorld must not replace runtime art")
    require(seamless.get("human_visual_approval_required") is True, "seamless OutdoorWorld must require human review")
    character_assets = as_dict(manifest.get("character_assets"), "character_assets")
    protagonist = as_dict(character_assets.get("protagonist"), "protagonist")
    require((ROOT / str(protagonist.get("manifest"))).exists(), "protagonist runtime manifest missing")
    require((ROOT / str(protagonist.get("runtime_sprite_frames"))).exists(), "protagonist runtime SpriteFrames missing")
    known_gaps = {str(as_dict(gap, "known gap").get("id")) for gap in manifest.get("known_runtime_gaps", [])}
    for required_gap in ["item_icon_backlog", "p0_npc_complete_art_backlog", "remaining_region_world2d_packages"]:
        require(required_gap in known_gaps, f"missing known runtime gap: {required_gap}")


def main() -> None:
    manifest = as_dict(read_json(MANIFEST, "project art production manifest"), "project art production manifest")
    validate_manifest_structure(manifest)
    by_id = manifest_entry_by_id(manifest)
    validate_registered_regions(by_id)
    validate_active_region_packages(by_id)
    validate_active_scenes_do_not_use_rejected_paths()
    validate_runtime_asset_groups(manifest)
    print("OK: project art production landing manifest validates registered regions, active art packages, and runtime art package state")


if __name__ == "__main__":
    main()
