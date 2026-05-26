from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_JSON = ROOT / "production" / "layout_blueprints" / "player_yard_layer_blueprint.json"
BLUEPRINT_SVG = ROOT / "production" / "layout_blueprints" / "player_yard_layer_blueprint.svg"
BLUEPRINT_MD = ROOT / "production" / "layout_blueprints" / "player_yard_layer_blueprint.md"
SCHEDULES = ROOT / "game" / "data" / "npc_schedules.json"

REQUIRED_OBJECT_ZONES = {
    "home_mailbox",
    "notice_board",
    "farm_garden",
    "repair_well",
    "repair_bench",
    "village_sign",
    "forest_gate",
    "resource_staging",
}

REQUIRED_LAYERS = {
    "scene_mother",
    "base",
    "foreground_occlusion",
    "interaction_hotspots",
    "npc_standing_points",
}

EXPECTED_PLAYER_YARD_POINTS = {
    ("shopkeeper_basic", "late_morning"): (116, 86),
    ("shopkeeper_basic", "afternoon"): (208, 196),
    ("carpenter_basic", "late_morning"): (174, 224),
    ("post_runner_basic", "late_morning"): (188, 84),
    ("elder_basic", "morning"): (170, 224),
    ("elder_basic", "late_morning"): (150, 146),
    ("elder_basic", "afternoon"): (150, 146),
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def _rect_contains(rect: dict[str, object], point: tuple[float, float], padding: float = 0.0) -> bool:
    left = float(rect["x"]) - padding
    top = float(rect["y"]) - padding
    right = left + float(rect["w"]) + padding * 2.0
    bottom = top + float(rect["h"]) + padding * 2.0
    return left <= point[0] <= right and top <= point[1] <= bottom


def _load_blueprint() -> dict[str, object]:
    if not BLUEPRINT_JSON.is_file():
        fail(f"missing blueprint json: {BLUEPRINT_JSON.relative_to(ROOT)}")
    if not BLUEPRINT_SVG.is_file():
        fail(f"missing blueprint svg: {BLUEPRINT_SVG.relative_to(ROOT)}")
    if not BLUEPRINT_MD.is_file():
        fail(f"missing blueprint markdown: {BLUEPRINT_MD.relative_to(ROOT)}")
    return json.loads(BLUEPRINT_JSON.read_text(encoding="utf-8"))


def _validate_blueprint_contract(data: dict[str, object]) -> None:
    if data.get("scene_id") != "player_yard":
        fail("blueprint scene_id must be player_yard")
    if data.get("coordinate_space") != "godot_scene_units":
        fail("blueprint coordinate_space must be godot_scene_units")
    if data.get("source_scene") != "res://game/scenes/world/PlayerYard.tscn":
        fail("blueprint source_scene must point at PlayerYard.tscn")
    if data.get("export_rule") != "full_canvas_shared_origin":
        fail("blueprint export_rule must require full_canvas_shared_origin")

    canvas = data.get("canvas_rect")
    if not isinstance(canvas, dict):
        fail("blueprint missing canvas_rect")
    for key in ["x", "y", "w", "h"]:
        if key not in canvas:
            fail(f"canvas_rect missing {key}")
    if float(canvas["w"]) < 420.0 or float(canvas["h"]) < 280.0:
        fail("canvas_rect is too small for current PlayerYard layout")

    layers = data.get("layers")
    if not isinstance(layers, list):
        fail("blueprint missing layers")
    layer_ids = {str(layer.get("id", "")) for layer in layers if isinstance(layer, dict)}
    missing_layers = REQUIRED_LAYERS - layer_ids
    if missing_layers:
        fail(f"blueprint missing layer ids: {sorted(missing_layers)}")

    zones = data.get("object_zones")
    if not isinstance(zones, list):
        fail("blueprint missing object_zones")
    zone_by_id = {str(zone.get("id", "")): zone for zone in zones if isinstance(zone, dict)}
    missing_zones = REQUIRED_OBJECT_ZONES - set(zone_by_id)
    if missing_zones:
        fail(f"blueprint missing object zones: {sorted(missing_zones)}")
    for zone_id, zone in zone_by_id.items():
        for key in ["x", "y", "w", "h", "layer"]:
            if key not in zone:
                fail(f"object zone {zone_id} missing {key}")
        if float(zone["w"]) <= 0.0 or float(zone["h"]) <= 0.0:
            fail(f"object zone {zone_id} must have positive size")

    for required_id in ["farm_garden", "repair_bench", "repair_well", "notice_board"]:
        if str(zone_by_id[required_id].get("layer", "")).strip() == "":
            fail(f"object zone {required_id} missing layer assignment")

    standpoints = data.get("npc_standing_points")
    if not isinstance(standpoints, list):
        fail("blueprint missing npc_standing_points")
    if len(standpoints) < 7:
        fail("blueprint should include all active PlayerYard NPC standing points")
    for point in standpoints:
        if not isinstance(point, dict):
            fail("npc standing point entries must be objects")
        for key in ["npc_id", "time_block", "x", "y", "activity_anchor"]:
            if key not in point:
                fail(f"npc standing point missing {key}: {point}")
        position = (float(point["x"]), float(point["y"]))
        for zone_id in ["farm_garden", "repair_bench", "repair_well", "village_sign", "notice_board"]:
            zone = zone_by_id[zone_id]
            if _rect_contains(zone, position, padding=0.0):
                fail(f"npc standing point intersects object zone {zone_id}: {point}")


def _validate_schedule_positions() -> None:
    schedules = json.loads(SCHEDULES.read_text(encoding="utf-8"))
    seen: dict[tuple[str, str], tuple[int, int]] = {}
    for schedule in schedules:
        schedule_id = str(schedule.get("schedule_id", ""))
        for entry in schedule.get("entries", []):
            if not isinstance(entry, dict) or entry.get("scene_id") != "player_yard":
                continue
            position = entry.get("position", [])
            if not isinstance(position, list) or len(position) != 2:
                fail(f"invalid player_yard schedule position: {schedule_id}/{entry}")
            seen[(schedule_id, str(entry.get("time_block", "")))] = (int(position[0]), int(position[1]))

    for key, expected in EXPECTED_PLAYER_YARD_POINTS.items():
        actual = seen.get(key)
        if actual != expected:
            fail(f"unexpected player_yard NPC point for {key}: expected {expected}, got {actual}")


def _validate_text_artifacts() -> None:
    svg_text = BLUEPRINT_SVG.read_text(encoding="utf-8")
    md_text = BLUEPRINT_MD.read_text(encoding="utf-8")
    for token in [
        "farm_garden",
        "repair_bench",
        "npc_standing_points",
        "full_canvas_shared_origin",
        "foreground_occlusion",
    ]:
        if token not in svg_text and token not in md_text:
            fail(f"blueprint text artifacts missing token: {token}")


def main() -> None:
    data = _load_blueprint()
    _validate_blueprint_contract(data)
    _validate_schedule_positions()
    _validate_text_artifacts()
    print("OK: PlayerYard layer blueprint readiness validated")


if __name__ == "__main__":
    main()
