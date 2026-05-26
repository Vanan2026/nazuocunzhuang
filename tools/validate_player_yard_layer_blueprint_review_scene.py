from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_JSON = ROOT / "production" / "layout_blueprints" / "player_yard_layer_blueprint.json"
GENERATOR = ROOT / "tools" / "generate_player_yard_layer_blueprint_review_scene.py"
REVIEW_SCENE = ROOT / "scenes" / "dev" / "player_yard_layer_blueprint_review.tscn"
RUNTIME_VALIDATOR = ROOT / "tools" / "validate_player_yard_layer_blueprint_review_scene.gd"

REQUIRED_NODES = [
    '[node name="PlayerYardLayerBlueprintReview" type="Node2D"]',
    '[node name="ReviewCamera" type="Camera2D" parent="."]',
    '[node name="CanvasContract" type="Polygon2D" parent="."]',
    '[node name="LayerLegend" type="Node2D" parent="."]',
    '[node name="ObjectZones" type="Node2D" parent="."]',
    '[node name="NPCStandingPoints" type="Node2D" parent="."]',
    '[node name="ReviewNotes" type="Node" parent="."]',
]

REQUIRED_METADATA = [
    'metadata/source_scene = "res://game/scenes/world/PlayerYard.tscn"',
    'metadata/blueprint_json_path = "res://production/layout_blueprints/player_yard_layer_blueprint.json"',
    'metadata/export_rule = "full_canvas_shared_origin"',
    'metadata/launch_quality_approved = false',
    'metadata/human_visual_approval_required = true',
    'metadata/review_scene_role = "layout_blueprint_inspection"',
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def _safe_node_suffix(value: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", value)
    return "".join(part[:1].upper() + part[1:] for part in parts if part)


def _read_text(path: Path) -> str:
    if not path.is_file():
        fail(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def _load_blueprint() -> dict[str, object]:
    if not BLUEPRINT_JSON.is_file():
        fail(f"missing blueprint json: {BLUEPRINT_JSON.relative_to(ROOT)}")
    return json.loads(BLUEPRINT_JSON.read_text(encoding="utf-8"))


def _validate_contract_files() -> None:
    _read_text(GENERATOR)
    _read_text(RUNTIME_VALIDATOR)
    _read_text(REVIEW_SCENE)


def _validate_scene_text(data: dict[str, object]) -> None:
    text = _read_text(REVIEW_SCENE)
    for snippet in REQUIRED_NODES + REQUIRED_METADATA:
        if snippet not in text:
            fail(f"review scene missing snippet: {snippet}")

    canvas = data.get("canvas_rect")
    if not isinstance(canvas, dict):
        fail("blueprint missing canvas_rect")
    expected_canvas = f'metadata/canvas_rect = "{canvas["x"]},{canvas["y"]},{canvas["w"]},{canvas["h"]}"'
    if expected_canvas not in text:
        fail("review scene canvas metadata does not match blueprint")

    layers = data.get("layers")
    if not isinstance(layers, list):
        fail("blueprint missing layers")
    for layer in layers:
        if not isinstance(layer, dict):
            fail("blueprint layer entries must be objects")
        layer_id = str(layer.get("id", ""))
        if f'metadata/layer_id = "{layer_id}"' not in text:
            fail(f"review scene missing layer legend metadata: {layer_id}")

    zones = data.get("object_zones")
    if not isinstance(zones, list):
        fail("blueprint missing object_zones")
    for zone in zones:
        if not isinstance(zone, dict):
            fail("object_zones entries must be objects")
        zone_id = str(zone.get("id", ""))
        node_name = "Zone_" + _safe_node_suffix(zone_id)
        if f'[node name="{node_name}" type="Polygon2D" parent="ObjectZones"]' not in text:
            fail(f"review scene missing object zone polygon: {zone_id}")
        if f'metadata/object_id = "{zone_id}"' not in text:
            fail(f"review scene missing object zone metadata: {zone_id}")
        if f'metadata/layer = "{zone.get("layer", "")}"' not in text:
            fail(f"review scene missing object zone layer metadata: {zone_id}")

    standpoints = data.get("npc_standing_points")
    if not isinstance(standpoints, list):
        fail("blueprint missing npc_standing_points")
    for index, point in enumerate(standpoints):
        if not isinstance(point, dict):
            fail("npc_standing_points entries must be objects")
        npc_id = str(point.get("npc_id", ""))
        time_block = str(point.get("time_block", ""))
        node_name = "Npc_" + _safe_node_suffix(f"{npc_id}_{time_block}_{index:02d}")
        if f'[node name="{node_name}" type="Polygon2D" parent="NPCStandingPoints"]' not in text:
            fail(f"review scene missing npc standpoint polygon: {npc_id}/{time_block}")
        if f'metadata/npc_id = "{npc_id}"' not in text:
            fail(f"review scene missing npc metadata: {npc_id}")
        if f'metadata/time_block = "{time_block}"' not in text:
            fail(f"review scene missing npc time metadata: {npc_id}/{time_block}")

    for token in ["full_canvas_shared_origin", "scene_mother", "base", "foreground_occlusion", "npc_standing_points"]:
        if token not in text:
            fail(f"review scene missing production token: {token}")


def main() -> None:
    data = _load_blueprint()
    _validate_contract_files()
    _validate_scene_text(data)
    print("OK: PlayerYard layer blueprint review scene static contract validated")


if __name__ == "__main__":
    main()
