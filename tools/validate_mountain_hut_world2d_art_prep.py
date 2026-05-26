from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "mountain_hut_world2d" / "v001"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
README = PACKAGE_DIR / "README.md"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock" / "layout_lock.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export" / "layer_contract.json"
REVIEW_GATE = PACKAGE_DIR / "05_review_and_qa" / "review_gate.md"

SEAM_DIR = ROOT / "production" / "assets" / "seams" / "village_to_mountain_hut" / "v001"
SEAM_BRIEF = SEAM_DIR / "seam_brief.md"

PROJECT_ART_MANIFEST = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"
OUTDOOR_WORLD_LAYOUT_LOCK = (
    ROOT
    / "production"
    / "assets"
    / "outdoor_world_world2d"
    / "v001"
    / "01_world_layout"
    / "outdoor_world_layout_lock.json"
)

CANVAS = [1800, 1200]
RUNTIME_SCALE = 0.18
REGION_ID = "Region_MountainHut"
REGION_SLUG = "mountain_hut"
NODE_ID = "MountainHut"
PACKAGE_POINTER = "production/assets/regions/mountain_hut_world2d/v001/workflow_manifest.json"
PACKAGE_DIR_POINTER = "production/assets/regions/mountain_hut_world2d/v001"
SEAM_BRIEF_POINTER = "production/assets/seams/village_to_mountain_hut/v001/seam_brief.md"
PARENT_WORLD_POINTER = "production/assets/outdoor_world_world2d/v001/workflow_manifest.json"

REQUIRED_PACKAGE_FILES = [
    WORKFLOW,
    README,
    LAYOUT_LOCK,
    LAYER_CONTRACT,
    REVIEW_GATE,
    SEAM_BRIEF,
]
REQUIRED_LAYER_IDS = {
    "base_ground",
    "terrain_details",
    "behind_player_structures",
    "ysort_props_structures",
    "foreground_occlusion",
}
REQUIRED_LAYOUT_ANCHORS = {
    "MountainHutExterior",
    "HutDoor",
    "HutApproachPath",
    "VillageConnectorPath",
}

failures: list[str] = []
reported_missing_paths: set[Path] = set()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_failure(message: str) -> None:
    failures.append(message)


def add_missing_file(path: Path) -> None:
    if path in reported_missing_paths:
        return
    reported_missing_paths.add(path)
    add_failure(f"missing required file: {rel(path)}")


def require(condition: bool, message: str) -> None:
    if not condition:
        add_failure(message)


def read_optional(path: Path) -> str:
    if not path.is_file():
        add_missing_file(path)
        return ""
    return path.read_text(encoding="utf-8")


def load_json_optional(path: Path) -> Any:
    text = read_optional(path)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        add_failure(f"invalid json in {rel(path)}: {exc}")
        return None


def as_dict(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        add_failure(f"{context} must be an object")
        return {}
    return value


def as_list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        add_failure(f"{context} must be a list")
        return []
    return value


def assert_canvas(value: Any, context: str) -> None:
    if isinstance(value, list):
        require(value == CANVAS, f"{context} canvas must be {CANVAS}, got {value}")
        return
    canvas = as_dict(value, f"{context}.canvas")
    if not canvas:
        return
    require(int(canvas.get("width", 0)) == CANVAS[0], f"{context} width must be {CANVAS[0]}")
    require(int(canvas.get("height", 0)) == CANVAS[1], f"{context} height must be {CANVAS[1]}")
    require(canvas.get("export_rule") == "full_canvas_shared_origin", f"{context} must use full_canvas_shared_origin")


def validate_required_files() -> None:
    for path in REQUIRED_PACKAGE_FILES:
        if not path.is_file():
            add_missing_file(path)


def validate_workflow() -> None:
    workflow = load_json_optional(WORKFLOW)
    if workflow is None:
        return
    data = as_dict(workflow, "workflow_manifest")
    require(data.get("package_id") == "mountain_hut_world2d_v001", "workflow package_id mismatch")
    require(data.get("region_id") == REGION_ID, f"workflow region_id must be {REGION_ID}")
    require(data.get("node_id") == NODE_ID, f"workflow node_id must be {NODE_ID}")
    require(data.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")
    require(data.get("launch_quality_approved") is False, "workflow must keep launch_quality_approved=false")
    require(data.get("human_visual_approval_required") is True, "workflow must require human visual approval")
    require(data.get("parent_world_art_package") == PARENT_WORLD_POINTER, "workflow must point at OutdoorWorld master package")
    require(data.get("active_seam_brief") == SEAM_BRIEF_POINTER, "workflow must point at village_to_mountain_hut seam brief")

    assert_canvas(data.get("canvas"), "workflow")
    source_policy = as_dict(data.get("source_policy"), "workflow.source_policy")
    for key in [
        "single_painted_source",
        "runtime_layers_derive_from_painted_source",
        "transparent_layers_full_canvas",
        "no_cropped_structural_layers",
        "one_scene_composition",
    ]:
        require(source_policy.get(key) is True, f"workflow.source_policy must set {key}=true")
    require(
        "registration-perfect" in str(source_policy.get("registration_target", "")),
        "workflow must use registration-perfect layer alignment wording",
    )


def validate_layout_lock() -> None:
    layout = load_json_optional(LAYOUT_LOCK)
    if layout is None:
        return
    data = as_dict(layout, "layout_lock")
    require(data.get("layout_id") == "mountain_hut_layout_lock_v001", "layout_id mismatch")
    require(data.get("region_id") == REGION_ID, f"layout region_id must be {REGION_ID}")
    require(data.get("node_id") == NODE_ID, f"layout node_id must be {NODE_ID}")
    require(data.get("parent_connection_id") == "village_to_mountain_hut", "layout must bind to village_to_mountain_hut")
    require(data.get("export_rule") == "full_canvas_shared_origin", "layout must require full_canvas_shared_origin")
    require("registration-perfect" in str(data.get("registration_rule", "")), "layout must use registration-perfect wording")

    coordinate_spaces = as_dict(data.get("coordinate_spaces"), "layout.coordinate_spaces")
    assert_canvas(coordinate_spaces.get("source_canvas"), "layout.source_canvas")
    runtime = as_dict(coordinate_spaces.get("godot_runtime"), "layout.godot_runtime")
    require(float(runtime.get("texture_scale", 0.0)) == RUNTIME_SCALE, "layout runtime scale must be 0.18")

    seams = as_list(data.get("seam_connectors"), "layout.seam_connectors")
    seam_edges = {str(as_dict(item, "layout seam").get("edge")) for item in seams}
    require("west" in seam_edges, "layout must define west seam connector back to Village")

    road_paths = as_list(data.get("road_paths"), "layout.road_paths")
    road_ids = {str(as_dict(item, "layout road").get("id")) for item in road_paths}
    require("village_connector_path" in road_ids, "layout must define village_connector_path")

    zones = as_list(data.get("object_zones"), "layout.object_zones")
    zone_ids = {str(as_dict(item, "object zone").get("id")) for item in zones}
    missing_anchors = REQUIRED_LAYOUT_ANCHORS - zone_ids
    require(not missing_anchors, f"layout object_zones missing anchors: {sorted(missing_anchors)}")


def validate_layer_contract() -> None:
    contract = load_json_optional(LAYER_CONTRACT)
    if contract is None:
        return
    data = as_dict(contract, "layer_contract")
    require(data.get("contract_id") == "mountain_hut_world2d_v001_layer_contract", "layer contract id mismatch")
    require(data.get("region_id") == REGION_ID, f"layer contract region_id must be {REGION_ID}")
    require(data.get("node_id") == NODE_ID, f"layer contract node_id must be {NODE_ID}")
    assert_canvas(data.get("canvas"), "layer_contract")

    source_image = as_dict(data.get("source_image"), "layer_contract.source_image")
    require(source_image.get("id") == "mountain_hut_painted_source", "layer contract must use mountain_hut_painted_source")
    require(source_image.get("required_before_layer_export") is True, "source image must be required before layer export")

    rules_text = "\n".join(str(rule) for rule in as_list(data.get("global_rules"), "layer_contract.global_rules"))
    for token in ["full 1800x1200 canvas", "registration-perfect", "painted_source", "runtime replacement"]:
        require(token in rules_text, f"layer contract global rules missing token: {token}")

    layers = as_list(data.get("layers"), "layer_contract.layers")
    layer_ids = {str(as_dict(item, "layer").get("id")) for item in layers}
    missing_layers = REQUIRED_LAYER_IDS - layer_ids
    require(not missing_layers, f"layer contract missing layers: {sorted(missing_layers)}")
    for raw_layer in layers:
        layer = as_dict(raw_layer, "layer")
        layer_id = str(layer.get("id", ""))
        if not layer_id:
            continue
        require(layer.get("canvas") == CANVAS, f"layer {layer_id} must declare canvas {CANVAS}")
        expected_prefix = "production/assets/regions/mountain_hut_world2d/v001/03_layer_export/layers/"
        require(
            str(layer.get("production_path", "")).startswith(expected_prefix),
            f"layer {layer_id} production path must stay inside MountainHut package",
        )
        alpha = str(layer.get("alpha", ""))
        if layer_id == "base_ground":
            require(alpha == "opaque", "base_ground must be opaque")
        else:
            require(alpha == "transparent_full_canvas", f"layer {layer_id} must be transparent_full_canvas")


def validate_seam_brief() -> None:
    text = read_optional(SEAM_BRIEF)
    if not text:
        return
    for token in [
        "village_to_mountain_hut",
        "Village",
        "MountainHut",
        "OutdoorWorld",
        "registration-perfect",
        "full canvas",
        "road",
        "ground",
        "detail density",
        "runtime replacement",
    ]:
        require(token in text, f"seam brief missing token: {token}")


def validate_review_gate() -> None:
    text = read_optional(REVIEW_GATE)
    if not text:
        return
    for token in [
        "MountainHut",
        "village_to_mountain_hut",
        "human visual review",
        "runtime replacement",
        "launch_quality_approved=false",
    ]:
        require(token in text, f"review gate missing token: {token}")


def validate_project_manifest_pointer() -> None:
    manifest = load_json_optional(PROJECT_ART_MANIFEST)
    if manifest is None:
        return
    data = as_dict(manifest, "project_art_manifest")
    regions = as_list(data.get("current_runtime_regions"), "project_art_manifest.current_runtime_regions")
    mountain_hut = None
    for raw_region in regions:
        region = as_dict(raw_region, "project_art_manifest region")
        if region.get("region_id") == REGION_ID:
            mountain_hut = region
            break
    require(mountain_hut is not None, f"project art manifest missing {REGION_ID}")
    if mountain_hut is None:
        return
    require(
        mountain_hut.get("required_package_dir") == PACKAGE_DIR_POINTER,
        f"{REGION_ID} required_package_dir must be {PACKAGE_DIR_POINTER}",
    )
    require(
        mountain_hut.get("active_package") == PACKAGE_POINTER,
        f"{REGION_ID} active_package must point at {PACKAGE_POINTER}",
    )
    require(
        mountain_hut.get("active_seam_brief") == SEAM_BRIEF_POINTER,
        f"{REGION_ID} active_seam_brief must point at {SEAM_BRIEF_POINTER}",
    )
    require(mountain_hut.get("runtime_replacement") is False, f"{REGION_ID} must keep runtime_replacement=false")
    require(mountain_hut.get("launch_quality_approved") is False, f"{REGION_ID} must keep launch_quality_approved=false")
    require(
        mountain_hut.get("human_visual_approval_required") is True,
        f"{REGION_ID} must require human_visual_approval_required=true",
    )


def validate_outdoor_world_connection() -> None:
    layout = load_json_optional(OUTDOOR_WORLD_LAYOUT_LOCK)
    if layout is None:
        return
    data = as_dict(layout, "outdoor_world_layout_lock")
    connections = as_list(data.get("connections"), "outdoor_world_layout_lock.connections")
    connection = None
    for raw_connection in connections:
        item = as_dict(raw_connection, "outdoor world connection")
        if item.get("id") == "village_to_mountain_hut":
            connection = item
            break
    require(connection is not None, "OutdoorWorld layout lock missing village_to_mountain_hut connection")
    if connection is None:
        return
    require(connection.get("from") == "village", "village_to_mountain_hut connection must start at village")
    require(connection.get("to") == REGION_SLUG, "village_to_mountain_hut connection must end at mountain_hut")
    require(len(as_list(connection.get("points"), "village_to_mountain_hut.points")) >= 2, "seam connection must have at least two points")


def main() -> None:
    validate_required_files()
    validate_workflow()
    validate_layout_lock()
    validate_layer_contract()
    validate_seam_brief()
    validate_review_gate()
    validate_project_manifest_pointer()
    validate_outdoor_world_connection()

    if failures:
        print("FAIL: MountainHut World2D art-prep package is not ready")
        for failure in failures:
            print(f"- {failure}")
        sys.exit(1)
    print("OK: MountainHut World2D art-prep package validated")


if __name__ == "__main__":
    main()
