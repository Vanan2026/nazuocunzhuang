from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "production/assets/regions/home_area_formal/v001"
CONTRACT = PKG / "home_area_formal_v001_pixel_layer_contract.json"
REPORT = ROOT / ".codex/reports/home_area_formal_v001_pixel_layer_contract.md"
ANNOTATED = PKG / "review/home_area_formal_v001_pixel_layer_contract_overlay.png"
SCENE = ROOT / "scenes/regions/region_home_area.tscn"
CANVAS = {"width": 6144, "height": 4096}
REQUIRED_OBJECTS = {
    "house_body",
    "house_roof",
    "veranda_floor",
    "front_steps",
    "house_door",
    "left_shade_tree",
    "right_persimmon_tree",
    "mailbox",
    "well",
    "bench_left_fence",
    "road_sign",
    "left_fence",
    "right_fence",
    "back_farm_rail",
    "local_foreground_plants",
    "back_farm_exit",
    "player_yard_exit",
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


def require_rect(rect: Any, label: str) -> dict[str, Any]:
    data = require_dict(rect, label)
    for key in ("x", "y", "width", "height"):
        require(isinstance(data.get(key), int), f"{label}.{key} must be int")
    require(data["width"] > 0 and data["height"] > 0, f"{label} must have positive size")
    require(0 <= data["x"] < CANVAS["width"], f"{label}.x outside canvas")
    require(0 <= data["y"] < CANVAS["height"], f"{label}.y outside canvas")
    require(data["x"] + data["width"] <= CANVAS["width"], f"{label} exceeds canvas width")
    require(data["y"] + data["height"] <= CANVAS["height"], f"{label} exceeds canvas height")
    return data


def require_point(point: Any, label: str) -> dict[str, Any]:
    data = require_dict(point, label)
    for key in ("x", "y"):
        require(isinstance(data.get(key), int), f"{label}.{key} must be int")
    require(0 <= data["x"] <= CANVAS["width"], f"{label}.x outside canvas")
    require(0 <= data["y"] <= CANVAS["height"], f"{label}.y outside canvas")
    return data


def main() -> None:
    require(CONTRACT.exists(), f"missing pixel contract: {CONTRACT.relative_to(ROOT).as_posix()}")
    require(REPORT.exists(), f"missing pixel contract report: {REPORT.relative_to(ROOT).as_posix()}")
    require(ANNOTATED.exists(), f"missing annotated contract overlay: {ANNOTATED.relative_to(ROOT).as_posix()}")
    require(SCENE.exists(), "missing HomeArea scene")

    contract = require_dict(json.loads(CONTRACT.read_text(encoding="utf-8")), "contract")
    require(contract.get("region_id") == "Region_HomeArea", "contract region mismatch")
    require(contract.get("package_id") == "home_area_formal_v001", "contract package mismatch")
    require(contract.get("canvas_px") == CANVAS, "contract canvas mismatch")
    require(contract.get("coordinate_space") == "source_pixels_equal_region_local_pixels", "contract must use source-pixel coordinates")
    require(contract.get("approval_boundary") == "design_contract_not_launch_approval", "contract must not imply launch approval")

    objects = contract.get("objects")
    require(isinstance(objects, list), "objects must be a list")
    by_id = {str(obj.get("object_id")): require_dict(obj, "object") for obj in objects if isinstance(obj, dict)}
    require(set(by_id) == REQUIRED_OBJECTS, f"object id mismatch: {sorted(set(by_id))}")

    scene_text = SCENE.read_text(encoding="utf-8-sig")
    for object_id, obj in by_id.items():
        require_rect(obj.get("source_rect_px"), f"{object_id}.source_rect_px")
        render_layers = obj.get("render_layers")
        require(isinstance(render_layers, list) and render_layers, f"{object_id} must define render_layers")
        for layer in render_layers:
            layer_data = require_dict(layer, f"{object_id}.render_layer")
            node_path = str(layer_data.get("scene_node", ""))
            if node_path != "none":
                require(node_path in scene_text, f"{object_id} render node not found in scene text: {node_path}")
            role = str(layer_data.get("role", ""))
            require(role in {"ground", "detail", "ysort_visual", "foreground_occluder", "ambient_overlay", "hidden_placeholder"}, f"{object_id} invalid render role: {role}")
        blockers = obj.get("blockers")
        require(isinstance(blockers, list), f"{object_id}.blockers must be a list")
        for blocker in blockers:
            blocker_data = require_dict(blocker, f"{object_id}.blocker")
            require_rect(blocker_data.get("rect_px"), f"{object_id}.blocker.rect_px")
            node_path = str(blocker_data.get("scene_node", ""))
            require(node_path == "none" or node_path in scene_text, f"{object_id} blocker node not found: {node_path}")
        interactions = obj.get("interactions")
        require(isinstance(interactions, list), f"{object_id}.interactions must be a list")
        for interaction in interactions:
            interaction_data = require_dict(interaction, f"{object_id}.interaction")
            require_rect(interaction_data.get("hotspot_rect_px"), f"{object_id}.interaction.hotspot_rect_px")
            require_point(interaction_data.get("stand_point_px"), f"{object_id}.interaction.stand_point_px")
            node_path = str(interaction_data.get("scene_node", ""))
            require(node_path == "none" or node_path in scene_text, f"{object_id} interaction node not found: {node_path}")
        tests = obj.get("qa_points")
        require(isinstance(tests, list) and tests, f"{object_id} must define qa_points")
        for point in tests:
            require_point(point, f"{object_id}.qa_point")

    print("OK: HomeArea formal/v001 pixel-level layer and interaction contract validates")


if __name__ == "__main__":
    main()