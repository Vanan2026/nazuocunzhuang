from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_JSON = ROOT / "production" / "layout_blueprints" / "player_yard_layer_blueprint.json"
REVIEW_SCENE = ROOT / "scenes" / "dev" / "player_yard_layer_blueprint_review.tscn"

LAYER_COLORS = {
    "scene_mother": "Color(0.18, 0.18, 0.18, 0.16)",
    "base": "Color(0.46, 0.64, 0.38, 0.46)",
    "foreground_occlusion": "Color(0.84, 0.56, 0.27, 0.54)",
    "interaction_hotspots": "Color(0.22, 0.54, 0.72, 0.42)",
    "npc_standing_points": "Color(0.20, 0.24, 0.34, 0.92)",
}


def _safe_node_suffix(value: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", value)
    return "".join(part[:1].upper() + part[1:] for part in parts if part)


def _string(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def _rect_polygon(x: float, y: float, w: float, h: float) -> str:
    return f"PackedVector2Array({x:g}, {y:g}, {x + w:g}, {y:g}, {x + w:g}, {y + h:g}, {x:g}, {y + h:g})"


def _diamond_polygon(x: float, y: float, radius: float = 6.0) -> str:
    return f"PackedVector2Array({x:g}, {y - radius:g}, {x + radius:g}, {y:g}, {x:g}, {y + radius:g}, {x - radius:g}, {y:g})"


def _metadata_line(key: str, value: object) -> str:
    if isinstance(value, bool):
        return f"metadata/{key} = {'true' if value else 'false'}"
    return f'metadata/{key} = "{_string(value)}"'


def _append_polygon(
    lines: list[str],
    name: str,
    parent: str,
    color: str,
    polygon: str,
    metadata: dict[str, object] | None = None,
) -> None:
    lines.append(f'[node name="{name}" type="Polygon2D" parent="{parent}"]')
    lines.append(f"color = {color}")
    lines.append(f"polygon = {polygon}")
    if metadata:
        for key, value in metadata.items():
            lines.append(_metadata_line(key, value))
    lines.append("")


def _append_marker(lines: list[str], name: str, parent: str, x: float, y: float, metadata: dict[str, object]) -> None:
    lines.append(f'[node name="{name}" type="Marker2D" parent="{parent}"]')
    lines.append(f"position = Vector2({x:g}, {y:g})")
    for key, value in metadata.items():
        lines.append(_metadata_line(key, value))
    lines.append("")


def build_scene(data: dict[str, object]) -> str:
    canvas = data["canvas_rect"]
    if not isinstance(canvas, dict):
        raise TypeError("canvas_rect must be an object")

    canvas_x = float(canvas["x"])
    canvas_y = float(canvas["y"])
    canvas_w = float(canvas["w"])
    canvas_h = float(canvas["h"])
    canvas_right = canvas_x + canvas_w
    camera_x = canvas_x + canvas_w * 0.56
    camera_y = canvas_y + canvas_h * 0.50

    lines = ["[gd_scene format=3]", ""]
    lines.extend(
        [
            '[node name="PlayerYardLayerBlueprintReview" type="Node2D"]',
            _metadata_line("source_scene", data["source_scene"]),
            _metadata_line("blueprint_json_path", "res://production/layout_blueprints/player_yard_layer_blueprint.json"),
            _metadata_line("scene_id", data["scene_id"]),
            _metadata_line("coordinate_space", data["coordinate_space"]),
            _metadata_line("export_rule", data["export_rule"]),
            _metadata_line("canvas_rect", f"{canvas['x']},{canvas['y']},{canvas['w']},{canvas['h']}"),
            _metadata_line("review_scene_role", "layout_blueprint_inspection"),
            _metadata_line("launch_quality_approved", False),
            _metadata_line("human_visual_approval_required", True),
            "",
            '[node name="ReviewCamera" type="Camera2D" parent="."]',
            f"position = Vector2({camera_x:g}, {camera_y:g})",
            "zoom = Vector2(1.55, 1.55)",
            "enabled = true",
            "",
        ]
    )

    _append_polygon(
        lines,
        "CanvasContract",
        ".",
        "Color(0.10, 0.10, 0.10, 0.08)",
        _rect_polygon(canvas_x, canvas_y, canvas_w, canvas_h),
        {
            "export_rule": data["export_rule"],
            "source": "canvas_rect",
        },
    )

    lines.extend(['[node name="LayerLegend" type="Node2D" parent="."]', ""])
    legend_x = canvas_right + 20.0
    legend_y = canvas_y + 20.0
    for index, layer in enumerate(data["layers"]):
        if not isinstance(layer, dict):
            raise TypeError("layers must contain objects")
        layer_id = str(layer["id"])
        swatch_y = legend_y + index * 18.0
        _append_polygon(
            lines,
            "Layer_" + _safe_node_suffix(layer_id),
            "LayerLegend",
            LAYER_COLORS.get(layer_id, "Color(0.50, 0.50, 0.50, 0.42)"),
            _rect_polygon(legend_x, swatch_y, 14.0, 10.0),
            {
                "layer_id": layer_id,
                "role": layer.get("role", ""),
                "export": layer.get("export", ""),
            },
        )

    lines.extend(['[node name="ObjectZones" type="Node2D" parent="."]', ""])
    for zone in data["object_zones"]:
        if not isinstance(zone, dict):
            raise TypeError("object_zones must contain objects")
        zone_id = str(zone["id"])
        layer_id = str(zone["layer"])
        _append_polygon(
            lines,
            "Zone_" + _safe_node_suffix(zone_id),
            "ObjectZones",
            LAYER_COLORS.get(layer_id, "Color(0.50, 0.50, 0.50, 0.44)"),
            _rect_polygon(float(zone["x"]), float(zone["y"]), float(zone["w"]), float(zone["h"])),
            {
                "object_id": zone_id,
                "layer": layer_id,
                "source_node": zone.get("source_node", ""),
            },
        )

    lines.extend(['[node name="NPCStandingPoints" type="Node2D" parent="."]', ""])
    for index, point in enumerate(data["npc_standing_points"]):
        if not isinstance(point, dict):
            raise TypeError("npc_standing_points must contain objects")
        npc_id = str(point["npc_id"])
        time_block = str(point["time_block"])
        _append_polygon(
            lines,
            "Npc_" + _safe_node_suffix(f"{npc_id}_{time_block}_{index:02d}"),
            "NPCStandingPoints",
            LAYER_COLORS["npc_standing_points"],
            _diamond_polygon(float(point["x"]), float(point["y"])),
            {
                "npc_id": npc_id,
                "schedule_id": point.get("schedule_id", ""),
                "time_block": time_block,
                "activity_anchor": point.get("activity_anchor", ""),
            },
        )
        _append_marker(
            lines,
            "Anchor_" + _safe_node_suffix(f"{npc_id}_{time_block}_{index:02d}"),
            "NPCStandingPoints",
            float(point["x"]),
            float(point["y"]),
            {
                "npc_id": npc_id,
                "time_block": time_block,
                "anchor_type": "standing_point_center",
            },
        )

    lines.extend(
        [
            '[node name="ReviewNotes" type="Node" parent="."]',
            _metadata_line("source_rule", "generated_from_player_yard_layer_blueprint_json"),
            _metadata_line("layer_registration", "full_canvas_shared_origin"),
            _metadata_line("production_scope", "scene_mother_base_foreground_occlusion_blueprint_review"),
            _metadata_line("not_final_art", True),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    data = json.loads(BLUEPRINT_JSON.read_text(encoding="utf-8"))
    REVIEW_SCENE.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_SCENE.write_text(build_scene(data), encoding="utf-8")
    print("OK: generated PlayerYard layer blueprint review scene")
    print(str(REVIEW_SCENE.relative_to(ROOT)).replace("\\", "/"))


if __name__ == "__main__":
    main()
