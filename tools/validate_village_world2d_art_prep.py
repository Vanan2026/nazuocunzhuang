from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock" / "layout_lock.json"
BLUEPRINT_MD = PACKAGE_DIR / "01_layout_lock" / "registration_blueprint.md"
BLUEPRINT_SVG = PACKAGE_DIR / "01_layout_lock" / "registration_blueprint.svg"
SOURCE_BRIEF = PACKAGE_DIR / "02_source_generation" / "source_brief.md"
SOURCE_PROMPT_PACK = PACKAGE_DIR / "02_source_generation" / "source_prompt_pack.md"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export" / "layer_contract.json"
GODOT_BOUNDARY = PACKAGE_DIR / "04_godot_integration" / "README.md"
REVIEW_GATE = PACKAGE_DIR / "05_review_and_qa" / "review_gate.md"
PROJECT_ART_MANIFEST = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"
REFERENCE_REQUEST = ROOT / "production" / "assets" / "external_gpt_handoff" / "greenfield_p0" / "v001" / "batch_02_scene_02_village_request.md"
OUTDOOR_WORLD_GD = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"
NPC_SCHEDULES = ROOT / "game" / "data" / "npc_schedules.json"

CANVAS = [1800, 1200]
RUNTIME_SCALE = 0.18
REQUIRED_FILES = [
    WORKFLOW,
    LAYOUT_LOCK,
    BLUEPRINT_MD,
    BLUEPRINT_SVG,
    SOURCE_BRIEF,
    SOURCE_PROMPT_PACK,
    LAYER_CONTRACT,
    GODOT_BOUNDARY,
    REVIEW_GATE,
]
REQUIRED_ANCHORS = {
    "VillageNotice",
    "SeedStallProxy",
    "OldMapleClue",
    "VillageReturnPath",
    "AoiVillageStandLateMorning",
    "BenchRestProp",
}
REQUIRED_LAYER_IDS = {
    "base_ground",
    "terrain_details",
    "behind_player_structures",
    "ysort_props_structures",
    "foreground_occlusion",
}
DEFERRED_LAYER_IDS = {
    "shadow_overlay",
    "light_weather_overlay_spring",
    "light_weather_overlay_summer",
    "light_weather_overlay_autumn",
    "light_weather_overlay_winter",
}
REQUIRED_RUNTIME_TOKENS = [
    "func _add_village_authored_slice",
    "VillagePlazaZone",
    "VillageNotice",
    "SeedStallProxy",
    "OldMapleClue",
    "VillageReturnPath",
    "read_village_notice_day1",
    "visited_village_seed_stall_day1",
    "found_village_soft_clue_day1",
    "returned_from_village_day1",
    "GENERATED_REGION_TEXTURE_SCALE: Vector2 = Vector2(0.18, 0.18)",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    try:
        return json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid json in {path.relative_to(ROOT)}: {exc}")


def as_list(value: Any, context: str) -> list[Any]:
    require(isinstance(value, list), f"{context} must be a list")
    return value


def as_dict(value: Any, context: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{context} must be an object")
    return value


def _assert_canvas(canvas: Any, context: str) -> None:
    if isinstance(canvas, list):
        require(canvas == CANVAS, f"{context} canvas must be {CANVAS}, got {canvas}")
        return
    canvas_dict = as_dict(canvas, context)
    require(int(canvas_dict.get("width", 0)) == CANVAS[0], f"{context} width must be {CANVAS[0]}")
    require(int(canvas_dict.get("height", 0)) == CANVAS[1], f"{context} height must be {CANVAS[1]}")


def _validate_required_files() -> None:
    for path in REQUIRED_FILES:
        require(path.is_file(), f"missing package file: {path.relative_to(ROOT)}")


def _validate_workflow(workflow: dict[str, Any]) -> None:
    require(workflow.get("package_id") == "village_world2d_v001", "workflow package_id mismatch")
    require(workflow.get("region_id") == "Region_Village", "workflow region_id must be Region_Village")
    require(workflow.get("node_id") == "VillagePlaza", "workflow node_id must be VillagePlaza")
    require(workflow.get("launch_quality_approved") is False, "workflow must not approve launch quality")
    require(workflow.get("human_visual_approval_required") is True, "workflow must require human visual approval")
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")

    canvas = as_dict(workflow.get("canvas"), "workflow.canvas")
    _assert_canvas(canvas, "workflow")
    require(float(canvas.get("godot_runtime_scale", 0.0)) == RUNTIME_SCALE, "workflow must lock Godot runtime scale 0.18")
    require(canvas.get("export_rule") == "full_canvas_shared_origin", "workflow must require full_canvas_shared_origin")

    source_policy = as_dict(workflow.get("source_policy"), "workflow.source_policy")
    for key in [
        "single_painted_source",
        "runtime_layers_derive_from_painted_source",
        "transparent_layers_full_canvas",
        "no_cropped_structural_layers",
        "one_scene_composition",
    ]:
        require(source_policy.get(key) is True, f"workflow source_policy must set {key}=true")
    require("registration-perfect" in str(source_policy.get("registration_target", "")), "workflow must use registration-perfect wording")

    art_node = as_dict(workflow.get("art_node"), "workflow.art_node")
    core_elements = {str(item) for item in as_list(art_node.get("core_elements"), "workflow.art_node.core_elements")}
    missing = REQUIRED_ANCHORS - core_elements
    require(not missing, f"workflow core_elements missing anchors: {sorted(missing)}")

    phase_status = as_dict(workflow.get("phase_status"), "workflow.phase_status")
    require(
        phase_status.get("04_godot_integration")
        in {
            "blocked_until_human_visual_review",
            "blocked_until_layer_review_and_godot_screenshot",
            "blocked_until_semantic_layer_review_and_godot_screenshot",
        },
        "Godot integration must be blocked",
    )


def _validate_layout(layout: dict[str, Any]) -> None:
    require(layout.get("layout_id") == "village_plaza_layout_lock_v001", "layout_id mismatch")
    require(layout.get("region_id") == "Region_Village", "layout region_id must be Region_Village")
    require(layout.get("node_id") == "VillagePlaza", "layout node_id must be VillagePlaza")
    require(layout.get("export_rule") == "full_canvas_shared_origin", "layout must require full_canvas_shared_origin")
    require("registration-perfect" in str(layout.get("registration_rule", "")), "layout must use registration-perfect wording")

    spaces = as_dict(layout.get("coordinate_spaces"), "layout.coordinate_spaces")
    _assert_canvas(spaces.get("source_canvas"), "layout.source_canvas")
    runtime = as_dict(spaces.get("godot_runtime"), "layout.godot_runtime")
    require(float(runtime.get("texture_scale", 0.0)) == RUNTIME_SCALE, "layout runtime scale must be 0.18")

    seams = as_list(layout.get("seam_connectors"), "layout.seam_connectors")
    require({str(seam.get("edge", "")) for seam in seams} == {"west", "north", "east", "south"}, "layout must define four seam connectors")

    road_paths = as_list(layout.get("road_paths"), "layout.road_paths")
    require(len(road_paths) >= 3, "layout must define plaza route paths")
    connector_paths = as_list(layout.get("seam_connector_paths"), "layout.seam_connector_paths")
    connector_ids = {str(path.get("id", "")) for path in connector_paths if isinstance(path, dict)}
    require(
        {"west_east_connector_spine", "north_south_connector_spine"}.issubset(connector_ids),
        "layout must define west/east and north/south connector spines",
    )
    for raw_connector in connector_paths:
        connector = as_dict(raw_connector, "layout.seam_connector_path")
        points = as_list(connector.get("source_points"), f"{connector.get('id')}.source_points")
        require(len(points) >= 4, f"{connector.get('id')} must have at least four source points")
        require(float(connector.get("source_width", 0)) >= 40, f"{connector.get('id')} must declare a readable source width")

    object_zones = as_list(layout.get("object_zones"), "layout.object_zones")
    by_id = {str(zone.get("id", "")): as_dict(zone, "object_zone") for zone in object_zones}
    missing = REQUIRED_ANCHORS - set(by_id)
    require(not missing, f"layout object_zones missing anchors: {sorted(missing)}")
    for anchor_id, zone in by_id.items():
        require(str(zone.get("layer", "")).strip() != "", f"{anchor_id} missing layer")
        if "source_rect" in zone:
            rect = as_list(zone["source_rect"], f"{anchor_id}.source_rect")
            require(len(rect) == 4, f"{anchor_id}.source_rect must have four values")
            require(float(rect[2]) > 0 and float(rect[3]) > 0, f"{anchor_id}.source_rect must have positive size")
        if "runtime_position" in zone and "source_position" in zone:
            runtime_position = as_list(zone["runtime_position"], f"{anchor_id}.runtime_position")
            source_position = as_list(zone["source_position"], f"{anchor_id}.source_position")
            require(len(runtime_position) == 2 and len(source_position) == 2, f"{anchor_id} positions must be 2D")
            expected = [float(runtime_position[0]) / RUNTIME_SCALE, float(runtime_position[1]) / RUNTIME_SCALE]
            delta = abs(float(source_position[0]) - expected[0]) + abs(float(source_position[1]) - expected[1])
            require(delta <= 3.0, f"{anchor_id} source_position should match runtime scale 0.18")

    hidden_policy = as_dict(layout.get("hidden_discovery_policy"), "layout.hidden_discovery_policy")
    forbidden = {str(item) for item in as_list(hidden_policy.get("forbidden"), "hidden_discovery_policy.forbidden")}
    require("baked quest text" in forbidden, "hidden discovery policy must forbid baked quest text")
    require("explicit old well instruction" in forbidden, "hidden discovery policy must forbid explicit old well instruction")


def _validate_layer_contract(contract: dict[str, Any]) -> None:
    require(contract.get("contract_id") == "village_world2d_v001_layer_contract", "layer contract id mismatch")
    _assert_canvas(contract.get("canvas"), "layer contract")
    source_image = as_dict(contract.get("source_image"), "layer_contract.source_image")
    require(source_image.get("id") == "village_painted_source", "layer contract must use village_painted_source")
    require(source_image.get("required_before_layer_export") is True, "source image must be required before layer export")
    require(
        source_image.get("current_file_status") in {"layout_structure_draft_only", "accepted_true_painted_source"},
        "current Village source status mismatch",
    )
    if source_image.get("current_file_status") == "layout_structure_draft_only":
        require(source_image.get("do_not_split_current_file") is True, "current Village layout draft must not be split")
    else:
        require(source_image.get("do_not_split_current_file") is False, "accepted Village source should allow layer export")

    rules_text = "\n".join(str(rule) for rule in as_list(contract.get("global_rules"), "layer_contract.global_rules"))
    for token in ["layout draft", "true storybook", "full 1800x1200 canvas", "registration-perfect", "review", "global Godot/system-level"]:
        require(token in rules_text, f"layer contract rules missing token: {token}")

    layers = as_list(contract.get("layers"), "layer_contract.layers")
    layer_ids = {str(layer.get("id", "")) for layer in layers if isinstance(layer, dict)}
    missing = REQUIRED_LAYER_IDS - layer_ids
    require(not missing, f"layer contract missing layers: {sorted(missing)}")
    for raw_layer in layers:
        layer = as_dict(raw_layer, "layer")
        layer_id = str(layer.get("id", ""))
        require(layer.get("canvas") == CANVAS, f"layer {layer_id} must declare canvas {CANVAS}")
        alpha = str(layer.get("alpha", ""))
        if layer_id == "base_ground":
            require(alpha == "opaque", "base_ground must be opaque")
        else:
            require(alpha == "transparent_full_canvas", f"layer {layer_id} must be transparent_full_canvas")
        require(str(layer.get("runtime_path", "")).startswith("res://assets/art/greenfield_p0/regions/village/layers/"), f"layer {layer_id} runtime path mismatch")
        require(str(layer.get("production_path", "")).startswith("production/assets/regions/village_world2d/v001/03_layer_export/layers/"), f"layer {layer_id} production path mismatch")
    deferred_layers = as_list(contract.get("deferred_layers"), "layer_contract.deferred_layers")
    deferred_ids = {str(as_dict(layer, "deferred layer").get("id")) for layer in deferred_layers}
    missing_deferred = DEFERRED_LAYER_IDS - deferred_ids
    require(not missing_deferred, f"layer contract missing deferred layers: {sorted(missing_deferred)}")


def _validate_text_artifacts() -> None:
    combined = "\n".join(read(path) for path in [BLUEPRINT_MD, BLUEPRINT_SVG, SOURCE_BRIEF, SOURCE_PROMPT_PACK, GODOT_BOUNDARY, REVIEW_GATE])
    for token in [
        "VillageNotice",
        "SeedStallProxy",
        "OldMapleClue",
        "VillageReturnPath",
        "Aoi",
        "1800x1200",
        "full canvas",
        "painted_source",
        "runtime replacement",
        "human visual review",
    ]:
        require(token in combined, f"text artifacts missing token: {token}")
    require("Do not put readable task text" in combined or "readable task text" in combined, "text artifacts must forbid readable task text")
    require("No Village World2D v001 runtime replacement is allowed" in read(GODOT_BOUNDARY), "Godot boundary must block runtime replacement")


def _validate_project_manifest() -> None:
    manifest = as_dict(load_json(PROJECT_ART_MANIFEST), "project art manifest")
    regions = as_list(manifest.get("current_runtime_regions"), "project_art_manifest.current_runtime_regions")
    village = None
    for region in regions:
        if isinstance(region, dict) and region.get("region_id") == "Region_Village":
            village = region
            break
    require(village is not None, "project art manifest missing Region_Village")
    assert village is not None
    require(
        village.get("phase")
        in {
            "village_plaza_art_prep_package_ready",
            "village_layers_exported_pending_review",
            "village_semantic_layers_exported_pending_review",
            "v002_inherited_crop_candidate_ready_for_visual_review",
            "v002_codex_visual_accepted_for_semantic_layer_export",
            "v002_semantic_layers_exported_pending_review",
        },
        "Region_Village phase should point at the active Village art package",
    )
    require(village.get("required_package_dir") == "production/assets/regions/village_world2d/v001", "Region_Village required package dir mismatch")
    require(village.get("active_package") == "production/assets/regions/village_world2d/v001/workflow_manifest.json", "Region_Village active package mismatch")
    require(village.get("launch_quality_approved") is False, "Region_Village must not be launch-approved")
    require(village.get("runtime_replacement") is False, "Region_Village must keep runtime_replacement=false")
    if village.get("phase") == "v002_inherited_crop_candidate_ready_for_visual_review":
        for key in ["active_inherited_repaint_handoff", "active_v002_source_candidate", "active_v002_quality_review"]:
            require((ROOT / str(village.get(key, ""))).exists(), f"Region_Village missing {key}")
    if village.get("phase") in {
        "v002_codex_visual_accepted_for_semantic_layer_export",
        "v002_semantic_layers_exported_pending_review",
    }:
        for key in [
            "active_inherited_repaint_handoff",
            "active_v002_source_candidate",
            "active_v002_quality_review",
            "active_v002_visual_review",
        ]:
            require((ROOT / str(village.get(key, ""))).exists(), f"Region_Village missing {key}")
    if village.get("phase") == "v002_semantic_layers_exported_pending_review":
        require((ROOT / str(village.get("active_v002_layer_manifest", ""))).exists(), "Region_Village missing active_v002_layer_manifest")


def _validate_runtime_alignment() -> None:
    outdoor_text = read(OUTDOOR_WORLD_GD)
    for token in REQUIRED_RUNTIME_TOKENS:
        require(token in outdoor_text, f"OutdoorWorld.gd missing runtime token: {token}")

    schedules = as_list(load_json(NPC_SCHEDULES), "npc_schedules")
    found_aoi = False
    for schedule in schedules:
        if not isinstance(schedule, dict) or schedule.get("schedule_id") != "shopkeeper_basic":
            continue
        for entry in schedule.get("entries", []):
            if not isinstance(entry, dict):
                continue
            if entry.get("scene_id") == "village" and entry.get("time_block") == "late_morning" and entry.get("position") == [196, 112]:
                found_aoi = True
    require(found_aoi, "shopkeeper_basic must keep Aoi late_morning village stand point [196, 112]")


def _validate_reference_request() -> None:
    request_text = read(REFERENCE_REQUEST)
    for token in [
        "Scene 02: village / Village",
        "registration-perfect",
        "painted_source",
        "1800x1200",
        "Do not crop",
    ]:
        require(token in request_text, f"reference Village request missing token: {token}")


def main() -> None:
    _validate_required_files()
    _validate_workflow(as_dict(load_json(WORKFLOW), "workflow"))
    _validate_layout(as_dict(load_json(LAYOUT_LOCK), "layout_lock"))
    _validate_layer_contract(as_dict(load_json(LAYER_CONTRACT), "layer_contract"))
    _validate_text_artifacts()
    _validate_project_manifest()
    _validate_runtime_alignment()
    _validate_reference_request()
    print("OK: Village World2D art prep package validated")


if __name__ == "__main__":
    main()
