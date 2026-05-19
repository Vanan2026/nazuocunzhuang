from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
LAYOUT_PATH = ROOT / "production" / "assets" / "regions" / "home_area_design" / "region_home_area_layout_v001.json"
OUT_DIR = ROOT / "production" / "assets" / "regions" / "home_area_blockout" / "v001"
SCENE_PATH = ROOT / "scenes" / "dev" / "region_home_area_blockout_3d_v002.tscn"
MANIFEST_PATH = OUT_DIR / "region_home_area_blockout_manifest.json"
PROMPT_PACK_PATH = OUT_DIR / "region_home_area_blockout_prompt_pack.md"
REVIEW_PATH = OUT_DIR / "region_home_area_blockout_review.png"
CODEX_REVIEW_PATH = ROOT / ".codex" / "home_area_blockout_v001_review.png"

CANVAS = {"width": 6144, "height": 4096}
SCALE = 0.25
REVIEW_SIZE = (1536, 1024)

ZONE_COLORS = {
    "north_village_road": (159, 135, 89, 210),
    "house_veranda": (156, 102, 60, 220),
    "front_yard_walkable": (135, 174, 105, 190),
    "west_garden": (102, 148, 84, 180),
    "back_farm_path": (178, 150, 92, 210),
    "left_tree": (66, 104, 61, 190),
    "right_tree": (68, 116, 65, 190),
    "foreground_edges": (58, 115, 66, 150),
    "light_weather": (247, 214, 118, 120),
}

REQUIRED_EXPORT_LAYERS = [
    ("ground_yard", "region_home_area_ground_yard_v005.png", "TileMapLayer_Ground/GroundModules", "ground_base"),
    ("path_village_road", "region_home_area_path_village_road_v005.png", "TileMapLayer_Path/PathModules", "path"),
    ("path_back_farm", "region_home_area_path_back_farm_v005.png", "TileMapLayer_Path/PathModules", "path"),
    ("house_body", "region_home_area_house_body_v005.png", "YSortWorld/Houses", "ysort_structure"),
    ("house_roof_occluder", "region_home_area_house_roof_occluder_v005.png", "ForegroundStatic/Occluders", "occluder"),
    ("veranda_floor", "region_home_area_veranda_floor_v005.png", "TileMapLayer_Detail", "detail"),
    ("tree_left_trunk", "region_home_area_tree_left_trunk_v005.png", "YSortWorld/Trees", "ysort_structure"),
    ("tree_left_canopy_occluder", "region_home_area_tree_left_canopy_occluder_v005.png", "ForegroundStatic/Occluders", "occluder"),
    ("tree_right_trunk", "region_home_area_tree_right_trunk_v005.png", "YSortWorld/Trees", "ysort_structure"),
    ("tree_right_canopy_occluder", "region_home_area_tree_right_canopy_occluder_v005.png", "ForegroundStatic/Occluders", "occluder"),
    ("foreground_grass", "region_home_area_foreground_grass_v005.png", "ForegroundStatic", "edge_occluder"),
    ("shadow_dappled", "region_home_area_shadow_dappled_v005.png", "LightAndWeather", "transparent_overlay"),
    ("light_overlay", "region_home_area_light_overlay_v005.png", "LightAndWeather", "transparent_overlay"),
]


def load_layout() -> dict[str, Any]:
    return json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))


def rect_to_3d(rect: dict[str, int]) -> tuple[float, float, float, float]:
    x = float(rect["x"]) / 100.0
    z = float(rect["y"]) / 100.0
    w = float(rect["w"]) / 100.0
    d = float(rect["h"]) / 100.0
    return x + w * 0.5, z + d * 0.5, w, d


def marker_to_3d(point: dict[str, int]) -> tuple[float, float]:
    return float(point["x"]) / 100.0, float(point["y"]) / 100.0


def scene_text(layout: dict[str, Any]) -> str:
    zones = {zone["id"]: zone for zone in layout["zones"]}
    interactions = {item["id"]: item for item in layout["interaction_points"]}

    def zone_node(node_name: str, zone_id: str, mesh: str, material: str, y: float = 0.12, extra: str = "") -> str:
        zone = zones[zone_id]
        rect = zone.get("rect_px")
        if rect:
            x, z, w, d = rect_to_3d(rect)
            scale = f"scale = Vector3({w:.2f}, 1, {d:.2f})\n" if mesh == "mesh_zone" else ""
        else:
            anchor = zone["anchor_px"]
            x, z = marker_to_3d(anchor)
            scale = ""
        return f"""[node name=\"{node_name}\" type=\"MeshInstance3D\" parent=\"ZoneGuides\"]
position = Vector3({x:.2f}, {y:.2f}, {z:.2f})
{scale}mesh = SubResource(\"{mesh}\")
surface_material_override/0 = SubResource(\"{material}\")
metadata/zone_id = \"{zone_id}\"
metadata/blockout_role = \"{zone.get('purpose', '')}\"{extra}
"""

    def marker_node(node_name: str, interaction_id: str) -> str:
        point = interactions[interaction_id]["position_px"]
        x, z = marker_to_3d(point)
        role = interactions[interaction_id]["role"]
        return f"""[node name=\"{node_name}\" type=\"MeshInstance3D\" parent=\"InteractionMarkers\"]
position = Vector3({x:.2f}, 0.9, {z:.2f})
mesh = SubResource(\"mesh_marker\")
surface_material_override/0 = SubResource(\"mat_interaction\")
metadata/interaction_id = \"{interaction_id}\"
metadata/interaction_role = \"{role}\"
"""

    def prop_volume_node(node_name: str, interaction_id: str, mesh: str, y: float, contract: str) -> str:
        point = interactions[interaction_id]["position_px"]
        x, z = marker_to_3d(point)
        return f"""[node name=\"{node_name}\" type=\"MeshInstance3D\" parent=\"PropScaleGuides\"]
position = Vector3({x:.2f}, {y:.2f}, {z:.2f})
mesh = SubResource(\"{mesh}\")
surface_material_override/0 = SubResource(\"mat_interaction\")
metadata/interaction_id = \"{interaction_id}\"
metadata/scale_contract = \"{contract}\"
"""

    scene = f"""[gd_scene load_steps=27 format=3 uid=\"uid://region_home_area_blockout_3d_v002\"]

[sub_resource type=\"StandardMaterial3D\" id=\"mat_ground\"]
albedo_color = Color(0.43, 0.60, 0.36, 1)

[sub_resource type=\"StandardMaterial3D\" id=\"mat_path\"]
albedo_color = Color(0.62, 0.52, 0.36, 1)

[sub_resource type=\"StandardMaterial3D\" id=\"mat_house\"]
albedo_color = Color(0.62, 0.43, 0.25, 1)

[sub_resource type=\"StandardMaterial3D\" id=\"mat_roof\"]
albedo_color = Color(0.22, 0.25, 0.25, 1)

[sub_resource type=\"StandardMaterial3D\" id=\"mat_tree\"]
albedo_color = Color(0.34, 0.20, 0.10, 1)

[sub_resource type=\"StandardMaterial3D\" id=\"mat_canopy\"]
albedo_color = Color(0.20, 0.42, 0.22, 0.78)
transparency = 1

[sub_resource type=\"StandardMaterial3D\" id=\"mat_foreground\"]
albedo_color = Color(0.20, 0.46, 0.22, 0.45)
transparency = 1

[sub_resource type=\"StandardMaterial3D\" id=\"mat_light\"]
albedo_color = Color(1, 0.86, 0.45, 0.28)
transparency = 1

[sub_resource type=\"StandardMaterial3D\" id=\"mat_interaction\"]
albedo_color = Color(0.36, 0.58, 0.90, 0.75)
transparency = 1

[sub_resource type=\"BoxMesh\" id=\"mesh_region\"]
size = Vector3(61.44, 0.08, 40.96)

[sub_resource type=\"BoxMesh\" id=\"mesh_zone\"]
size = Vector3(1, 0.1, 1)

[sub_resource type=\"BoxMesh\" id=\"mesh_house\"]
size = Vector3(18.6, 6.4, 8.2)

[sub_resource type=\"BoxMesh\" id=\"mesh_roof\"]
size = Vector3(21.0, 1.2, 10.0)

[sub_resource type=\"BoxMesh\" id=\"mesh_veranda\"]
size = Vector3(16.0, 0.35, 2.8)

[sub_resource type=\"CylinderMesh\" id=\"mesh_tree_trunk\"]
top_radius = 0.35
bottom_radius = 0.55
height = 4.8

[sub_resource type=\"SphereMesh\" id=\"mesh_canopy\"]
radius = 3.6
height = 4.8

[sub_resource type=\"BoxMesh\" id=\"mesh_marker\"]
size = Vector3(0.7, 0.7, 0.7)

[sub_resource type=\"BoxMesh\" id=\"mesh_mailbox\"]
size = Vector3(1.25, 1.95, 0.52)

[sub_resource type=\"CylinderMesh\" id=\"mesh_well\"]
top_radius = 0.95
bottom_radius = 1.05
height = 1.85

[sub_resource type=\"BoxMesh\" id=\"mesh_bench\"]
size = Vector3(3.15, 0.72, 0.82)

[node name=\"RegionHomeAreaBlockout3DV002\" type=\"Node3D\"]
metadata/region_id = \"Region_HomeArea\"
metadata/package_id = \"home_area_blockout_v001\"
metadata/layout_contract = \"res://production/assets/regions/home_area_design/region_home_area_layout_v001.json\"
metadata/blockout_manifest = \"res://production/assets/regions/home_area_blockout/v001/region_home_area_blockout_manifest.json\"
metadata/runtime_boundary = \"offline_blockout_review_only\"
metadata/unit_mapping = \"100px_to_1m_xz_region_top_left\"
metadata/approval_status = \"needs_human_review\"

[node name=\"BlockoutReviewCamera\" type=\"Camera3D\" parent=\".\"]
transform = Transform3D(1, 0, 0, 0, 0.707107, 0.707107, 0, -0.707107, 0.707107, 30.72, 46, 55)
projection = 1
size = 58.0
current = true
metadata/purpose = \"fixed 3D blockout review camera before 2D art production\"
metadata/target_canvas_px = Vector2i(6144, 4096)

[node name=\"SunLight\" type=\"DirectionalLight3D\" parent=\".\"]
transform = Transform3D(0.819152, -0.40558, 0.40558, 0, 0.707107, 0.707107, -0.573576, -0.579228, 0.579228, 0, 0, 0)
light_energy = 1.45
metadata/purpose = \"summer afternoon light reference, not final runtime lighting\"

[node name=\"RegionPlane\" type=\"MeshInstance3D\" parent=\".\"]
position = Vector3(30.72, 0, 20.48)
mesh = SubResource(\"mesh_region\")
surface_material_override/0 = SubResource(\"mat_ground\")
metadata/zone_id = \"region_canvas\"

[node name=\"ZoneGuides\" type=\"Node3D\" parent=\".\"]
metadata/purpose = \"reviewable spatial zones from region_home_area_layout_v001.json\"

"""
    scene += zone_node("NorthVillageRoad", "north_village_road", "mesh_zone", "mat_path")
    scene += zone_node("CentralFrontYard", "front_yard_walkable", "mesh_zone", "mat_ground", extra="\nmetadata/must_remain_readable = true")
    scene += zone_node("WestGarden", "west_garden", "mesh_zone", "mat_ground")
    scene += zone_node("BackFarmPath", "back_farm_path", "mesh_zone", "mat_path", extra="\nmetadata/must_remain_readable = true")

    house = zones["house_veranda"]["anchor_px"]
    hx, hz = marker_to_3d(house)
    scene += f"""[node name=\"HouseBlock\" type=\"MeshInstance3D\" parent=\"ZoneGuides\"]
position = Vector3({hx:.2f}, 3.2, {hz - 2.4:.2f})
mesh = SubResource(\"mesh_house\")
surface_material_override/0 = SubResource(\"mat_house\")
metadata/zone_id = \"house_veranda\"
metadata/source_runtime_anchor_px = Vector2i({house['x']}, {house['y']})
metadata/export_layer_id = \"house_body\"

[node name=\"HouseRoofOccluderBlock\" type=\"MeshInstance3D\" parent=\"ZoneGuides\"]
position = Vector3({hx:.2f}, 6.9, {hz - 3.2:.2f})
mesh = SubResource(\"mesh_roof\")
surface_material_override/0 = SubResource(\"mat_roof\")
metadata/asset_role = \"house_roof_occluder\"
metadata/export_layer_id = \"house_roof_occluder\"
metadata/occlusion_rule = \"may cover head and torso near door, never feet\"

[node name=\"VerandaFloorBlock\" type=\"MeshInstance3D\" parent=\"ZoneGuides\"]
position = Vector3({hx:.2f}, 0.28, {hz + 1.1:.2f})
mesh = SubResource(\"mesh_veranda\")
surface_material_override/0 = SubResource(\"mat_path\")
metadata/export_layer_id = \"veranda_floor\"
metadata/zone_id = \"house_veranda\"

"""

    for side, zone_id, node_prefix, scale in [
        ("left", "left_tree", "LeftShadeTree", "Vector3(1.55, 1, 1.25)"),
        ("right", "right_tree", "RightPersimmonTree", "Vector3(1.35, 0.95, 1.2)"),
    ]:
        anchor = zones[zone_id]["anchor_px"]
        x, z = marker_to_3d(anchor)
        scene += f"""[node name=\"{node_prefix}Trunk\" type=\"MeshInstance3D\" parent=\"ZoneGuides\"]
position = Vector3({x:.2f}, 2.4, {z:.2f})
mesh = SubResource(\"mesh_tree_trunk\")
surface_material_override/0 = SubResource(\"mat_tree\")
metadata/zone_id = \"{zone_id}\"
metadata/source_runtime_anchor_px = Vector2i({anchor['x']}, {anchor['y']})
metadata/export_layer_id = \"tree_{side}_trunk\"

[node name=\"{node_prefix}Canopy\" type=\"MeshInstance3D\" parent=\"ZoneGuides\"]
position = Vector3({x:.2f}, 6.0, {z - 3.0:.2f})
scale = {scale}
mesh = SubResource(\"mesh_canopy\")
surface_material_override/0 = SubResource(\"mat_canopy\")
metadata/asset_role = \"tree_{side}_canopy_occluder\"
metadata/export_layer_id = \"tree_{side}_canopy_occluder\"
metadata/occlusion_rule = \"split canopy only; leaf holes required in 2D pass\"

"""

    scene += zone_node("ForegroundEdgeGuide", "foreground_edges", "mesh_zone", "mat_foreground", y=0.3, extra="\nmetadata/export_layer_id = \"foreground_grass\"\nmetadata/occlusion_rule = \"edge-only, no full-width player-covering plate\"")
    scene += zone_node("LightOverlayGuide", "light_weather", "mesh_zone", "mat_light", y=0.35, extra="\nmetadata/export_layer_id = \"light_overlay\"")

    scene += """[node name=\"InteractionMarkers\" type=\"Node3D\" parent=\".\"]
metadata/purpose = \"gameplay anchors from region_home_area_layout_v001.json\"

"""
    marker_order = [
        ("DefaultSpawn", "home_area_default_spawn"),
        ("HouseDoor", "homearea_house_door_001"),
        ("Mailbox", "homearea_mailbox_001"),
        ("Well", "homearea_well_001"),
        ("BenchRest", "homearea_bench_rest_001"),
        ("RoadSign", "homearea_roadsign_001"),
        ("BackFarmExit", "home_area_to_back_farm"),
    ]
    for node_name, interaction_id in marker_order:
        scene += marker_node(node_name, interaction_id) + "\n"

    scene += """[node name=\"PropScaleGuides\" type=\"Node3D\" parent=\".\"]
metadata/purpose = \"reviewable prop massing and scale before 2D v005 art production\"

"""
    scene += prop_volume_node("MailboxScaleGuide", "homearea_mailbox_001", "mesh_mailbox", 0.98, "mailbox top reaches protagonist waist/chest range") + "\n"
    scene += prop_volume_node("WellScaleGuide", "homearea_well_001", "mesh_well", 0.92, "well is a substantial yard landmark, not a tiny corner prop") + "\n"
    scene += prop_volume_node("BenchScaleGuide", "homearea_bench_rest_001", "mesh_bench", 0.36, "bench seats one or two characters and aligns to veranda/front-yard rest area") + "\n"
    return scene


def draw_review(layout: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CODEX_REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", REVIEW_SIZE, (243, 231, 209, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    for zone in layout["zones"]:
        zone_id = zone["id"]
        rect = zone.get("rect_px")
        if not rect:
            anchor = zone["anchor_px"]
            x = int(anchor["x"] * SCALE)
            y = int(anchor["y"] * SCALE)
            rect = {"x": anchor["x"] - 180, "y": anchor["y"] - 180, "w": 360, "h": 360}
        x0 = int(rect["x"] * SCALE)
        y0 = int(rect["y"] * SCALE)
        x1 = int((rect["x"] + rect["w"]) * SCALE)
        y1 = int((rect["y"] + rect["h"]) * SCALE)
        fill = ZONE_COLORS.get(zone_id, (140, 140, 140, 160))
        draw.rectangle((x0, y0, x1, y1), fill=fill, outline=(70, 58, 42, 230), width=2)
        draw.text((x0 + 6, y0 + 6), zone_id, fill=(48, 39, 30, 255))

    for point in layout["interaction_points"]:
        pos = point["position_px"]
        x = int(pos["x"] * SCALE)
        y = int(pos["y"] * SCALE)
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(61, 105, 166, 235), outline=(255, 255, 255, 255), width=2)
        draw.text((x + 10, y - 8), point["id"], fill=(42, 58, 88, 255))

    draw.rectangle((0, 0, REVIEW_SIZE[0] - 1, REVIEW_SIZE[1] - 1), outline=(90, 74, 54, 255), width=3)
    draw.text((18, 18), "Region_HomeArea blockout v001 review schematic - 6144x4096 source space", fill=(45, 38, 30, 255))
    image.convert("RGB").save(REVIEW_PATH)
    image.convert("RGB").save(CODEX_REVIEW_PATH)


def build_manifest(layout: dict[str, Any]) -> dict[str, Any]:
    return {
        "region_id": "Region_HomeArea",
        "package_id": "home_area_blockout_v001",
        "status": "blockout_review_candidate",
        "approval_status": "needs_human_review",
        "runtime_boundary": "offline_blockout_review_only",
        "runtime_import_mode_after_approval": "layered_2d_png",
        "source_layout": "production/assets/regions/home_area_design/region_home_area_layout_v001.json",
        "scene_path": "scenes/dev/region_home_area_blockout_3d_v002.tscn",
        "review_image": "production/assets/regions/home_area_blockout/v001/region_home_area_blockout_review.png",
        "codex_review_image": ".codex/home_area_blockout_v001_review.png",
        "canvas_px": CANVAS,
        "unit_mapping": {
            "pixels_per_meter": 100,
            "origin": "region_top_left",
            "axis_map": {
                "godot_2d_x": "godot_3d_x",
                "godot_2d_y": "godot_3d_z",
                "height": "godot_3d_y",
            },
        },
        "review_camera": {
            "node_path": "RegionHomeAreaBlockout3DV002/BlockoutReviewCamera",
            "projection": "orthogonal_oblique",
            "size": 58.0,
            "target_canvas_px": CANVAS,
        },
        "zones": layout["zones"],
        "interaction_points": layout["interaction_points"],
        "required_2d_layer_contract": [
            {
                "asset_id": asset_id,
                "file": file_name,
                "target_parent": parent,
                "role": role,
                "status": "not_generated_until_blockout_approval",
            }
            for asset_id, file_name, parent, role in REQUIRED_EXPORT_LAYERS
        ],
        "prop_scale_contract": [
            {"asset_id": "mailbox", "interaction_id": "homearea_mailbox_001", "guide_node": "PropScaleGuides/MailboxScaleGuide", "rule": "top reaches protagonist waist/chest range"},
            {"asset_id": "well", "interaction_id": "homearea_well_001", "guide_node": "PropScaleGuides/WellScaleGuide", "rule": "substantial yard landmark, placed inside the front-yard composition"},
            {"asset_id": "bench", "interaction_id": "homearea_bench_rest_001", "guide_node": "PropScaleGuides/BenchScaleGuide", "rule": "wide enough for seated rest, aligned to veranda/front-yard rest area"},
        ],
        "acceptance_gate": [
            "Human review must approve the 3D blockout before v005 2D layer production starts.",
            "No v002-v004 mother-plate fragments may be promoted into v005 final art.",
            "House, roads, BackFarm path, tree canopies, foreground edges, and interaction anchors must match this manifest.",
            "2D exports must be transparent layered PNGs with source-space origin/anchor records.",
        ],
        "next_step_after_approval": "Generate or commission v005 2D layered art from this blockout and the project art bible.",
    }


def write_prompt_pack() -> None:
    content = """# Region_HomeArea Blockout Prompt Pack v001

## Purpose
Use this after human approval of the 3D blockout. It is an art-production brief, not runtime content.

## Style Lock
Warm low-saturation Japanese countryside storybook feeling, fixed top-down 3/4 perspective, soft hand-painted texture, clear silhouettes, Godot-ready 2D layered PNGs. No combat, monsters, weapons, blood, dark fantasy, photorealism, neon, text, watermark, or imitation of any named existing game/anime.

## Blockout Source
- Scene: `res://scenes/dev/region_home_area_blockout_3d_v002.tscn`
- Layout: `production/assets/regions/home_area_design/region_home_area_layout_v001.json`
- Manifest: `production/assets/regions/home_area_blockout/v001/region_home_area_blockout_manifest.json`
- Review image: `production/assets/regions/home_area_blockout/v001/region_home_area_blockout_review.png`

## Required Output Policy
Generate one coherent HomeArea art package from the approved blockout. Do not collage v002-v004 repair layers. Full plate is review-only. Runtime uses separated transparent layers.

## Required v005 Layers
- `region_home_area_ground_yard_v005.png`
- `region_home_area_path_village_road_v005.png`
- `region_home_area_path_back_farm_v005.png`
- `region_home_area_house_body_v005.png`
- `region_home_area_house_roof_occluder_v005.png`
- `region_home_area_veranda_floor_v005.png`
- `region_home_area_tree_left_trunk_v005.png`
- `region_home_area_tree_left_canopy_occluder_v005.png`
- `region_home_area_tree_right_trunk_v005.png`
- `region_home_area_tree_right_canopy_occluder_v005.png`
- `region_home_area_foreground_grass_v005.png`
- `region_home_area_shadow_dappled_v005.png`
- `region_home_area_light_overlay_v005.png`

## Review Gates
- Player scale must read against the house, grass, trees, props, and paths.
- Foreground grass may frame only the edges and must not wash over the player or primary paths.
- Tree canopy occluders need real transparent holes between leaf clusters.
- BackFarm and Village exits remain visually readable.
- No baked player, NPC, animal, UI text, or watermark.
"""
    PROMPT_PACK_PATH.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    layout = load_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCENE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCENE_PATH.write_text(scene_text(layout), encoding="utf-8", newline="\n")
    draw_review(layout)
    MANIFEST_PATH.write_text(json.dumps(build_manifest(layout), ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    write_prompt_pack()
    print(f"OK: wrote HomeArea blockout scene: {SCENE_PATH.relative_to(ROOT).as_posix()}")
    print(f"OK: wrote HomeArea blockout manifest: {MANIFEST_PATH.relative_to(ROOT).as_posix()}")
    print(f"OK: wrote HomeArea blockout review image: {REVIEW_PATH.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()