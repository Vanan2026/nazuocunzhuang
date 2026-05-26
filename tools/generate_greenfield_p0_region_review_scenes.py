from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "production" / "assets" / "base_asset_pack" / "v001"
MANIFEST = PACKAGE / "workflow_manifest.json"
SCENE_DIR = ROOT / "scenes" / "dev" / "greenfield_p0_reviews"

REVIEW_REGIONS = [
    "home_area",
    "village",
    "back_farm",
    "forest_edge",
    "orchard",
    "pond",
    "mountain_path",
    "mountain_hut",
    "mountain",
    "cliff_view",
]
BATCH_A_REGIONS = REVIEW_REGIONS[:3]
WORLD_LAYOUT_SCENE = "greenfield_p0_world_layout_review"
REVIEW_LAYERS = [
    ("base_ground", "BaseGround"),
    ("terrain_details", "TerrainDetails"),
    ("behind_player_structures", "BehindPlayerStructures"),
    ("ysort_props_structures", "YSortPropsStructures"),
    ("shadow_overlay", "ShadowOverlay"),
    ("foreground_occlusion", "ForegroundOcclusion"),
]
LIGHT_LAYER_NAME = "LightWeatherOverlaySpring"


def res_path(path: str | Path) -> str:
    if isinstance(path, str):
        path = ROOT / path
    return "res://" + str(path.relative_to(ROOT)).replace("\\", "/")


def find_region(manifest: dict, region_id: str) -> dict:
    for region in manifest["regions"]:
        if region["region_id"] == region_id:
            return region
    raise KeyError(region_id)


def runtime_res(record: dict) -> str:
    return str(record["runtime_path"])


def write_region_scene(region: dict) -> Path:
    region_id = region["region_id"]
    width, height = region["canvas_size"]
    resource_paths: list[tuple[str, str]] = []

    for layer_key, _node_name in REVIEW_LAYERS:
        resource_paths.append((f"tex_{layer_key}", runtime_res(region["layers"][layer_key])))
    spring_overlay = next(item for item in region["layers"]["light_weather_overlays"] if item["season"] == "spring")
    resource_paths.append(("tex_light_spring", runtime_res(spring_overlay)))

    scene_path = SCENE_DIR / f"greenfield_p0_region_review_{region_id}.tscn"
    lines = [f"[gd_scene load_steps={len(resource_paths) + 1} format=3]", ""]
    for resource_id, path in resource_paths:
        lines.append(f'[ext_resource type="Texture2D" path="{path}" id="{resource_id}"]')
    camera_zoom = min(0.7, max(0.32, 900.0 / max(width, height)))
    lines.extend(
        [
            "",
            f'[node name="GreenfieldP0RegionReview_{region_id}" type="Node2D"]',
            'metadata/package_id = "greenfield_p0_base_asset_pack_v001"',
            f'metadata/region_id = "{region_id}"',
            'metadata/status = "usable"',
            'metadata/launch_quality_approved = false',
            'metadata/human_visual_approval_required = true',
            "",
            '[node name="ReviewCamera" type="Camera2D" parent="."]',
            f"position = Vector2({width / 2:.1f}, {height / 2:.1f})",
            f"zoom = Vector2({camera_zoom:.3f}, {camera_zoom:.3f})",
            "enabled = true",
            "",
            '[node name="RuntimeLayerStack" type="Node2D" parent="."]',
            "",
        ]
    )
    for layer_key, node_name in REVIEW_LAYERS:
        lines.extend(
            [
                f'[node name="{node_name}" type="Sprite2D" parent="RuntimeLayerStack"]',
                f"position = Vector2({width / 2:.1f}, {height / 2:.1f})",
                f'texture = ExtResource("tex_{layer_key}")',
                "",
            ]
        )
    lines.extend(
        [
            f'[node name="{LIGHT_LAYER_NAME}" type="Sprite2D" parent="RuntimeLayerStack"]',
            f"position = Vector2({width / 2:.1f}, {height / 2:.1f})",
            'modulate = Color(1, 1, 1, 0.65)',
            'texture = ExtResource("tex_light_spring")',
            "",
            '[node name="ReviewAnchors" type="Node2D" parent="."]',
            "",
        ]
    )
    for anchor in region["anchors"]:
        safe_name = "Anchor_" + str(anchor["id"]).title().replace("_", "")
        x, y = anchor["position"]
        lines.extend(
            [
                f'[node name="{safe_name}" type="Marker2D" parent="ReviewAnchors"]',
                f"position = Vector2({x}, {y})",
                "",
            ]
        )
    lines.extend(
        [
            '[node name="ReviewNotes" type="Node" parent="."]',
            'metadata/review_gate = "visual_review_required"',
            'metadata/source_rule = "do_not_patch_independent_scene_sprites"',
            "",
        ]
    )
    scene_path.write_text("\n".join(lines), encoding="utf-8")
    return scene_path


def write_batch_scene(regions: list[dict], scene_name: str, cols: int, scale: float) -> Path:
    scene_path = SCENE_DIR / f"{scene_name}.tscn"
    resources: list[tuple[str, str]] = []
    for region in regions:
        resources.append((f"tex_{region['region_id']}", res_path(region["painted_source"])))
    lines = [f"[gd_scene load_steps={len(resources) + 1} format=3]", ""]
    for resource_id, path in resources:
        lines.append(f'[ext_resource type="Texture2D" path="{path}" id="{resource_id}"]')
    lines.extend(
        [
            "",
            f'[node name="{scene_name.title().replace("_", "")}" type="Node2D"]',
            'metadata/package_id = "greenfield_p0_base_asset_pack_v001"',
            'metadata/status = "usable"',
            'metadata/launch_quality_approved = false',
            'metadata/human_visual_approval_required = true',
            "",
            '[node name="ReviewCamera" type="Camera2D" parent="."]',
            f"position = Vector2({cols * 310}, {max(1, (len(regions) + cols - 1) // cols) * 230})",
            "zoom = Vector2(0.45, 0.45)",
            "enabled = true",
            "",
            '[node name="RegionPreviews" type="Node2D" parent="."]',
            "",
        ]
    )
    for index, region in enumerate(regions):
        x = 300 + (index % cols) * 520
        y = 320 + (index // cols) * 360
        rid = region["region_id"]
        lines.extend(
            [
                f'[node name="{rid}" type="Node2D" parent="RegionPreviews"]',
                f"position = Vector2({x}, {y})",
                f'metadata/region_id = "{rid}"',
                "",
                f'[node name="PaintedSource" type="Sprite2D" parent="RegionPreviews/{rid}"]',
                f"scale = Vector2({scale:.3f}, {scale:.3f})",
                f'texture = ExtResource("tex_{rid}")',
                "",
            ]
        )
    scene_path.write_text("\n".join(lines), encoding="utf-8")
    return scene_path


def write_world_layout_scene(manifest: dict, regions: list[dict]) -> Path:
    world_layout = manifest["world_layout"]
    scene_path = SCENE_DIR / f"{WORLD_LAYOUT_SCENE}.tscn"
    resources: list[tuple[str, str]] = []
    for region in regions:
        resources.append((f"tex_{region['region_id']}", res_path(region["painted_source"])))
    lines = [f"[gd_scene load_steps={len(resources) + 1} format=3]", ""]
    for resource_id, path in resources:
        lines.append(f'[ext_resource type="Texture2D" path="{path}" id="{resource_id}"]')
    tile_by_region = {tile["region_id"]: tile for tile in world_layout["tiles"]}
    cell_w = 520
    cell_h = 360
    margin_x = 300
    margin_y = 260

    def center(region_id: str) -> tuple[int, int]:
        grid = tile_by_region[region_id]["grid"]
        return (margin_x + grid[0] * cell_w, margin_y + grid[1] * cell_h)

    lines.extend(
        [
            "",
            '[node name="GreenfieldP0WorldLayoutReview" type="Node2D"]',
            'metadata/package_id = "greenfield_p0_base_asset_pack_v001"',
            'metadata/status = "review_candidate"',
            'metadata/launch_quality_approved = false',
            'metadata/human_visual_approval_required = true',
            'metadata/source_rule = "edit_generator_not_scene_sprites"',
            "",
            '[node name="ReviewCamera" type="Camera2D" parent="."]',
            "position = Vector2(1080, 780)",
            "zoom = Vector2(0.42, 0.42)",
            "enabled = true",
            "",
            '[node name="Connections" type="Node2D" parent="."]',
            "",
        ]
    )
    for adjacency in world_layout["adjacencies"]:
        start = center(adjacency["from"])
        end = center(adjacency["to"])
        node_name = "Connection_" + adjacency["id"].title().replace("_", "")
        lines.extend(
            [
                f'[node name="{node_name}" type="Line2D" parent="Connections"]',
                f"points = PackedVector2Array({start[0]}, {start[1]}, {end[0]}, {end[1]})",
                "width = 8.0",
                "default_color = Color(0.55, 0.37, 0.20, 0.82)",
                f'metadata/connection_id = "{adjacency["id"]}"',
                f'metadata/route_role = "{adjacency["route_role"]}"',
                f'metadata/traversal = "{adjacency["traversal"]}"',
                "",
            ]
        )
    lines.extend(['[node name="RegionTiles" type="Node2D" parent="."]', ""])
    sockets_by_region: dict[str, list[dict]] = {}
    for socket in world_layout["sockets"]:
        sockets_by_region.setdefault(socket["region_id"], []).append(socket)
    socket_offsets = {"north": (0, -132), "south": (0, 132), "west": (-186, 0), "east": (186, 0)}
    for region in regions:
        rid = region["region_id"]
        x, y = center(rid)
        role = tile_by_region[rid]["world_role"]
        lines.extend(
            [
                f'[node name="{rid}" type="Node2D" parent="RegionTiles"]',
                f"position = Vector2({x}, {y})",
                f'metadata/region_id = "{rid}"',
                f'metadata/world_role = "{role}"',
                "",
                f'[node name="PaintedSource" type="Sprite2D" parent="RegionTiles/{rid}"]',
                "scale = Vector2(0.13, 0.13)",
                f'texture = ExtResource("tex_{rid}")',
                "",
                f'[node name="Sockets" type="Node2D" parent="RegionTiles/{rid}"]',
                "",
            ]
        )
        for socket in sockets_by_region.get(rid, []):
            offset = socket_offsets[socket["edge"]]
            socket_name = "Socket_" + socket["edge"].title() + "_" + socket["connects_to_region"].title().replace("_", "")
            lines.extend(
                [
                    f'[node name="{socket_name}" type="Marker2D" parent="RegionTiles/{rid}/Sockets"]',
                    f"position = Vector2({offset[0]}, {offset[1]})",
                    f'metadata/edge = "{socket["edge"]}"',
                    f'metadata/connection_id = "{socket["connection_id"]}"',
                    f'metadata/connects_to_region = "{socket["connects_to_region"]}"',
                    f'metadata/route_role = "{socket["route_role"]}"',
                    "",
                ]
            )
    scene_path.write_text("\n".join(lines), encoding="utf-8")
    return scene_path


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    regions = [find_region(manifest, region_id) for region_id in REVIEW_REGIONS]
    batch_a_regions = [find_region(manifest, region_id) for region_id in BATCH_A_REGIONS]
    created = [write_region_scene(region) for region in regions]
    created.append(write_batch_scene(batch_a_regions, "greenfield_p0_region_review_batch_a", cols=3, scale=0.26))
    created.append(write_batch_scene(regions, "greenfield_p0_region_review_all", cols=5, scale=0.14))
    created.append(write_world_layout_scene(manifest, regions))
    rel = [str(path.relative_to(ROOT)).replace("\\", "/") for path in created]
    print("OK: generated greenfield P0 region review scenes")
    for path in rel:
        print(path)


if __name__ == "__main__":
    main()
