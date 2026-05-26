from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
README = PACKAGE_DIR / "README.md"
LAYOUT_LOCK = PACKAGE_DIR / "01_world_layout" / "outdoor_world_layout_lock.json"
BLUEPRINT_SVG = PACKAGE_DIR / "01_world_layout" / "outdoor_world_seamless_blueprint.svg"
BLUEPRINT_PNG = PACKAGE_DIR / "01_world_layout" / "outdoor_world_seamless_blueprint.png"
BLUEPRINT_MD = PACKAGE_DIR / "01_world_layout" / "outdoor_world_seamless_blueprint.md"
SOURCE_STRATEGY = PACKAGE_DIR / "02_source_strategy" / "source_generation_strategy.md"
CHUNK_CONTRACT = PACKAGE_DIR / "03_region_contracts" / "region_chunk_contract.json"
REVIEW_GATE = PACKAGE_DIR / "04_review_and_qa" / "review_gate.md"
GENERATOR = ROOT / "tools" / "generate_outdoor_world_seamless_art_master.py"
OUTDOOR_WORLD_GD = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"
PROJECT_MANIFEST = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"

EXPECTED_REGION_IDS = {
    "player_yard",
    "forest_edge",
    "village",
    "back_farm",
    "orchard",
    "pond",
    "mountain_path",
    "mountain_hut",
    "mountain",
    "cliff_view",
}

EXPECTED_MVP_LAYERS = [
    "base_ground",
    "terrain_details",
    "behind_player_structures",
    "ysort_props_structures",
    "foreground_occlusion",
]

DEFERRED_OVERLAY_LAYERS = {
    "shadow_overlay",
    "light_weather_overlay_spring",
    "light_weather_overlay_summer",
    "light_weather_overlay_autumn",
    "light_weather_overlay_winter",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT).as_posix()}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid json in {path.relative_to(ROOT).as_posix()}: {exc}")
    require(isinstance(value, dict), f"{path.relative_to(ROOT).as_posix()} must contain a JSON object")
    return value


def as_list(value: Any, label: str) -> list[Any]:
    require(isinstance(value, list), f"{label} must be a list")
    return value


def as_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def validate_workflow() -> None:
    workflow = load_json(WORKFLOW)
    require(workflow.get("package_id") == "outdoor_world_world2d_v001", "workflow package_id mismatch")
    require(workflow.get("status") == "master_blueprint_ready_not_runtime_replacement", "workflow status mismatch")
    require(workflow.get("active_runtime_scene") == "res://game/scenes/world/OutdoorWorld.tscn", "workflow active scene mismatch")
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")
    require(workflow.get("launch_quality_approved") is False, "workflow must keep launch_quality_approved=false")
    require(workflow.get("human_visual_approval_required") is True, "workflow must require human visual approval")
    decision = as_dict(workflow.get("art_pipeline_decision"), "workflow.art_pipeline_decision")
    require(decision.get("previous_village_candidate_status") == "layout_structure_draft_only", "workflow must downgrade previous Village candidate")
    require(decision.get("do_not_split_previous_village_candidate") is True, "workflow must block splitting the previous Village candidate")
    policy = as_dict(workflow.get("coordinate_policy"), "workflow.coordinate_policy")
    require(policy.get("generated_region_source_canvas") == [1800, 1200], "workflow source canvas mismatch")
    require(policy.get("generated_region_runtime_size") == [320, 240], "workflow runtime size mismatch")
    require(float(policy.get("runtime_texture_scale", 0.0)) == 0.18, "workflow runtime texture scale mismatch")
    require("registration-perfect" in str(policy.get("registration_target")), "workflow must use registration-perfect wording")
    artifacts = as_dict(workflow.get("artifacts"), "workflow.artifacts")
    require(artifacts.get("blueprint_png") == "production/assets/outdoor_world_world2d/v001/01_world_layout/outdoor_world_seamless_blueprint.png", "workflow blueprint_png path mismatch")


def validate_layout_lock() -> None:
    layout = load_json(LAYOUT_LOCK)
    require(layout.get("layout_id") == "outdoor_world_seamless_layout_lock_v001", "layout id mismatch")
    require(layout.get("active_runtime_scene") == "res://game/scenes/world/OutdoorWorld.tscn", "layout scene mismatch")
    require(layout.get("generated_region_source_canvas") == [1800, 1200], "layout source canvas mismatch")
    require(layout.get("generated_region_runtime_size") == [320, 240], "layout runtime size mismatch")
    regions = as_list(layout.get("regions"), "layout.regions")
    by_id = {str(as_dict(region, "layout region").get("region_id")): as_dict(region, "layout region") for region in regions}
    require(set(by_id) == EXPECTED_REGION_IDS, f"layout region ids mismatch: {sorted(EXPECTED_REGION_IDS ^ set(by_id))}")
    require(by_id["village"].get("source_status") == "layout_draft_only_not_final_painted_source", "Village must be marked as layout draft only")
    bounds = as_dict(layout.get("world_bounds"), "layout.world_bounds")
    require(bounds.get("width") == 1760 and bounds.get("height") == 880, "world bounds should match current OutdoorWorld layout")

    connections = as_list(layout.get("connections"), "layout.connections")
    require(len(connections) >= 10, "layout should define the current seam connection graph")
    connection_ids = {str(as_dict(item, "connection").get("id")) for item in connections}
    for expected in ["yard_to_village", "village_to_mountain_path", "village_to_pond", "mountain_to_cliff_view"]:
        require(expected in connection_ids, f"missing seam connection: {expected}")

    rules_text = "\n".join(str(rule) for rule in as_list(layout.get("global_art_rules"), "layout.global_art_rules"))
    for token in ["seamless world", "pixel-perfect", "full region canvas", "Godot/system-level"]:
        require(token in rules_text, f"layout global rules missing token: {token}")


def validate_chunk_contract() -> None:
    contract = load_json(CHUNK_CONTRACT)
    require(contract.get("contract_id") == "outdoor_world_region_chunk_contract_v001", "chunk contract id mismatch")
    source_rule = as_dict(contract.get("per_region_source_rule"), "contract.per_region_source_rule")
    for key in ["opaque_source_required", "single_painted_source_per_region", "layers_derive_from_source", "transparent_layers_full_canvas", "no_cropped_layers"]:
        require(source_rule.get(key) is True, f"contract source rule must set {key}=true")
    layers = as_list(contract.get("mvp_layers"), "contract.mvp_layers")
    require([str(as_dict(layer, "mvp layer").get("id")) for layer in layers] == EXPECTED_MVP_LAYERS, "MVP layer order mismatch")
    deferred = set(str(item) for item in as_list(contract.get("deferred_layers"), "contract.deferred_layers"))
    require(DEFERRED_OVERLAY_LAYERS <= deferred, "weather/shadow overlays must be deferred for seamless MVP")


def validate_text_artifacts() -> None:
    combined = "\n".join(read(path) for path in [README, BLUEPRINT_MD, BLUEPRINT_SVG, SOURCE_STRATEGY, REVIEW_GATE])
    for token in [
        "OutdoorWorld",
        "seamless",
        "not final art",
        "not runtime replacement",
        "layout draft",
        "not final `village_painted_source`",
        "weather, season, and time-of-day",
    ]:
        require(token in combined, f"text artifacts missing token: {token}")


def validate_blueprint_png() -> None:
    require(BLUEPRINT_PNG.is_file(), "missing PNG blueprint preview")
    image = Image.open(BLUEPRINT_PNG).convert("RGB")
    require(image.size == (2200, 1300), f"PNG blueprint preview size mismatch: {image.size}")
    stat = ImageStat.Stat(image)
    require(sum(stat.var) > 500, "PNG blueprint preview appears too flat")


def validate_generator_contract() -> None:
    text = read(GENERATOR)
    for token in ["REGIONS", "CONNECTIONS", "write_workflow", "write_layout_lock", "write_chunk_contract"]:
        require(token in text, f"generator missing token: {token}")


def _extract_string_array(text: str, const_name: str) -> set[str]:
    match = re.search(rf"const {const_name}:[^\n=]*=\s*\[(.*?)\]", text, re.S)
    require(match is not None, f"OutdoorWorld missing const {const_name}")
    assert match is not None
    return set(re.findall(r'"([^"]+)"', match.group(1)))


def validate_runtime_alignment() -> None:
    text = read(OUTDOOR_WORLD_GD)
    require(_extract_string_array(text, "OUTDOOR_REGION_IDS") == EXPECTED_REGION_IDS, "OutdoorWorld region ids mismatch")
    require(_extract_string_array(text, "GENERATED_REGION_IDS") == EXPECTED_REGION_IDS - {"player_yard", "forest_edge"}, "OutdoorWorld generated region ids mismatch")
    for token in [
        '"village": Vector2(720.0, -12.0)',
        '"mountain_path": Vector2(720.0, -316.0)',
        '"cliff_view": Vector2(1400.0, -316.0)',
        "GENERATED_REGION_TEXTURE_SCALE: Vector2 = Vector2(0.18, 0.18)",
        "GENERATED_REGION_SIZE: Vector2 = Vector2(320.0, 240.0)",
    ]:
        require(token in text, f"OutdoorWorld runtime token missing: {token}")
    for layer_id in EXPECTED_MVP_LAYERS:
        require(f'"suffix": "{layer_id}"' in text, f"OutdoorWorld generated layer missing suffix: {layer_id}")
    for layer_id in DEFERRED_OVERLAY_LAYERS:
        require(f'"suffix": "{layer_id}"' not in text, f"OutdoorWorld should not runtime-load deferred overlay layer: {layer_id}")


def validate_project_manifest_link() -> None:
    manifest = load_json(PROJECT_MANIFEST)
    master = as_dict(manifest.get("seamless_outdoor_world"), "project_art_manifest.seamless_outdoor_world")
    require(master.get("active_package") == "production/assets/outdoor_world_world2d/v001/workflow_manifest.json", "project manifest missing active seamless package")
    require(master.get("runtime_replacement") is False, "project manifest seamless package must block runtime replacement")
    require(master.get("human_visual_approval_required") is True, "project manifest seamless package must require human approval")


def main() -> None:
    validate_workflow()
    validate_layout_lock()
    validate_chunk_contract()
    validate_text_artifacts()
    validate_blueprint_png()
    validate_generator_contract()
    validate_runtime_alignment()
    validate_project_manifest_link()
    print("OK: OutdoorWorld seamless art master validates")


if __name__ == "__main__":
    main()
