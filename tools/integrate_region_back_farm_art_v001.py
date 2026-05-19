from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "scenes" / "regions" / "region_back_farm.tscn"
MANIFEST = ROOT / "production" / "assets" / "regions" / "back_farm_art" / "v001" / "region_back_farm_art_v001_manifest.json"

TEXTURE_IDS = {
    "ground": "8_back_farm_ground_art",
    "path": "9_back_farm_path_art",
    "field_rows": "10_back_farm_field_rows_art",
    "shed": "11_back_farm_shed_art",
    "pond": "12_back_farm_pond_art",
    "fence": "13_back_farm_fence_art",
    "foreground_grass": "14_back_farm_foreground_art",
    "shadow": "15_back_farm_shadow_art",
    "light": "16_back_farm_light_art",
}

NODE_NAMES = {
    "ground": "BackFarmGroundArtV001",
    "path": "BackFarmPathArtV001",
    "field_rows": "BackFarmFieldRowsArtV001",
    "shed": "BackFarmShedArtV001",
    "pond": "BackFarmPondArtV001",
    "fence": "BackFarmFenceArtV001",
    "foreground_grass": "BackFarmForegroundGrassArtV001",
    "shadow": "BackFarmShadowArtV001",
    "light": "BackFarmLightArtV001",
}

PARENTS = {
    "ground": "TileMapLayer_Ground/ArtLayers",
    "path": "TileMapLayer_Path/ArtLayers",
    "field_rows": "TileMapLayer_Detail/ArtLayers",
    "shed": "YSortWorld/FarmStructures/ToolShed",
    "pond": "YSortWorld/SmallPond",
    "fence": "YSortWorld/FarmStructures",
    "foreground_grass": "ForegroundStatic",
    "shadow": "LightAndWeather",
    "light": "LightAndWeather",
}

PARENT_OFFSETS = {
    "shed": (1600, 400),
    "pond": (1700, 1500),
}

GRAYBOX = [
    ("GroundBase", "TileMapLayer_Ground"),
    ("Field1", "TileMapLayer_Ground/FarmFields"),
    ("Field2", "TileMapLayer_Ground/FarmFields"),
    ("Field3", "TileMapLayer_Ground/FarmFields"),
    ("Field4", "TileMapLayer_Ground/FarmFields"),
    ("MainPath", "TileMapLayer_Path"),
    ("ShedBase", "YSortWorld/FarmStructures/ToolShed"),
    ("ShedRoof", "YSortWorld/FarmStructures/ToolShed"),
    ("PondBase", "YSortWorld/SmallPond"),
    ("ForegroundLeft", "ForegroundStatic"),
    ("ForegroundRight", "ForegroundStatic"),
]


def node_pattern(name: str, parent: str | None = None) -> re.Pattern[str]:
    if parent is None:
        header = rf'\[node name="{re.escape(name)}" [^\]]*\]'
    else:
        header = rf'\[node name="{re.escape(name)}" [^\]]*parent="{re.escape(parent)}"[^\]]*\]'
    return re.compile(header + r".*?(?=\n\[node |\n\[connection |\Z)", re.S)


def get_block(text: str, name: str, parent: str | None = None) -> str:
    match = node_pattern(name, parent).search(text)
    if match is None:
        raise SystemExit(f"missing block {parent}/{name}")
    return match.group(0)


def replace_block(text: str, name: str, parent: str | None, block: str) -> str:
    pattern = node_pattern(name, parent)
    if pattern.search(text) is None:
        raise SystemExit(f"missing block for replace {parent}/{name}")
    return pattern.sub(block, text, count=1)


def ensure_visible_false(block: str) -> str:
    if "visible = false" in block:
        return block
    lines = block.splitlines()
    return "\n".join([lines[0], "visible = false", *lines[1:]])


def replace_or_add_property(block: str, key: str, value_line: str) -> str:
    lines = block.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(key + " = "):
            lines[index] = value_line
            return "\n".join(lines)
    return "\n".join([*lines, value_line])


def vec2(x: int, y: int) -> str:
    return f"Vector2({x}, {y})"


def sprite_block(asset_id: str, record: dict) -> str:
    parent = PARENTS[asset_id]
    origin = record["origin_px"]
    x, y = int(origin["x"]), int(origin["y"])
    ox, oy = PARENT_OFFSETS.get(asset_id, (0, 0))
    local_x, local_y = x - ox, y - oy
    node_name = NODE_NAMES[asset_id]
    texture_id = TEXTURE_IDS[asset_id]
    z_index = int(record["z_index"])
    paint_id = asset_id
    return "\n".join([
        f'[node name="{node_name}" type="Sprite2D" parent="{parent}"]',
        f"position = {vec2(local_x, local_y)}",
        f"z_index = {z_index}",
        f'texture = ExtResource("{texture_id}")',
        "centered = false",
        'metadata/asset_package = "back_farm_art_v001"',
        f'metadata/paint_id = "{paint_id}"',
    ])


def main() -> None:
    text = SCENE.read_text(encoding="utf-8-sig")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = {rec["asset_id"]: rec for rec in manifest["required_layers"]}

    # Fix mojibake text and lock the current art package on the root.
    root = get_block(text, "Region_BackFarm")
    root = replace_or_add_property(root, "region_display_name", 'region_display_name = "后院菜园"')
    root = replace_or_add_property(root, "metadata/art_package", 'metadata/art_package = "back_farm_art_v001"')
    root = replace_or_add_property(root, "metadata/art_status", 'metadata/art_status = "self_checked_final_runtime_candidate"')
    text = replace_block(text, "Region_BackFarm", None, root)

    # Add texture resources once.
    if "back_farm_art/v001/region_back_farm_ground_v001.png" not in text:
        resource_lines = []
        for asset_id, texture_id in TEXTURE_IDS.items():
            file_name = records[asset_id]["file"]
            resource_lines.append(f'[ext_resource type="Texture2D" path="res://production/assets/regions/back_farm_art/v001/{file_name}" id="{texture_id}"]')
        text = text.replace('[ext_resource type="Script" path="res://scripts/activities/farm_system.gd" id="7_farm_system"]', '[ext_resource type="Script" path="res://scripts/activities/farm_system.gd" id="7_farm_system"]\n' + "\n".join(resource_lines))

    # Hide old graybox visuals.
    for name, parent in GRAYBOX:
        block = get_block(text, name, parent)
        text = replace_block(text, name, parent, ensure_visible_false(block))

    # Clean farm interactable text.
    for index in range(4):
        plot = f"FarmPlot{index}"
        block = get_block(text, plot, "YSortWorld/Interactables")
        block = replace_or_add_property(block, "display_name", 'display_name = "菜地"')
        block = replace_or_add_property(block, "interaction_hint", 'interaction_hint = "按 E 种植"')
        text = replace_block(text, plot, "YSortWorld/Interactables", block)
        hint = get_block(text, "HintLabel", f"YSortWorld/Interactables/{plot}")
        hint = replace_or_add_property(hint, "text", 'text = "按 E 种植"')
        text = replace_block(text, "HintLabel", f"YSortWorld/Interactables/{plot}", hint)

    exit_block = get_block(text, "ExitToHomeArea", "YSortWorld/Interactables")
    exit_block = replace_or_add_property(exit_block, "position", "position = Vector2(1000, 220)")
    exit_block = replace_or_add_property(exit_block, "interaction_hint", 'interaction_hint = "按 E 返回庭院"')
    text = replace_block(text, "ExitToHomeArea", "YSortWorld/Interactables", exit_block)
    exit_hint = get_block(text, "HintLabel", "YSortWorld/Interactables/ExitToHomeArea")
    exit_hint = replace_or_add_property(exit_hint, "text", 'text = "按 E 返回庭院"')
    text = replace_block(text, "HintLabel", "YSortWorld/Interactables/ExitToHomeArea", exit_hint)

    walkable = get_block(text, "WalkableZone", ".")
    walkable = replace_or_add_property(walkable, "polygon", "polygon = PackedVector2Array(120, 120, 1880, 120, 1880, 1740, 1500, 1900, 500, 1900, 120, 1740)")
    text = replace_block(text, "WalkableZone", ".", walkable)

    spawn = get_block(text, "PlayerSpawn", "YSortWorld")
    spawn = replace_or_add_property(spawn, "position", "position = Vector2(1000, 280)")
    text = replace_block(text, "PlayerSpawn", "YSortWorld", spawn)

    # Add art layer containers and sprites.
    if '[node name="ArtLayers" type="Node2D" parent="TileMapLayer_Ground"]' not in text:
        ground_layers = [
            '[node name="ArtLayers" type="Node2D" parent="TileMapLayer_Ground"]',
            'metadata/purpose = "formal_back_farm_ground_art"',
            sprite_block("ground", records["ground"]),
        ]
        text = text.replace('[node name="FarmFields" type="Node2D" parent="TileMapLayer_Ground"]', "\n".join(ground_layers) + '\n\n[node name="FarmFields" type="Node2D" parent="TileMapLayer_Ground"]')

    if '[node name="ArtLayers" type="Node2D" parent="TileMapLayer_Path"]' not in text:
        path_layers = [
            '[node name="ArtLayers" type="Node2D" parent="TileMapLayer_Path"]',
            'metadata/purpose = "formal_back_farm_path_art"',
            sprite_block("path", records["path"]),
        ]
        text = text.replace('[node name="TileMapLayer_Detail" type="TileMapLayer" parent="."]', "\n".join(path_layers) + '\n\n[node name="TileMapLayer_Detail" type="TileMapLayer" parent="."]')

    if '[node name="ArtLayers" type="Node2D" parent="TileMapLayer_Detail"]' not in text:
        detail_layers = [
            '[node name="ArtLayers" type="Node2D" parent="TileMapLayer_Detail"]',
            'metadata/purpose = "formal_back_farm_field_detail_art"',
            sprite_block("field_rows", records["field_rows"]),
        ]
        text = text.replace('[node name="WalkableZone" type="Node2D" parent="."]', "\n".join(detail_layers) + '\n\n[node name="WalkableZone" type="Node2D" parent="."]')

    if NODE_NAMES["shed"] not in text:
        text = text.replace('[node name="SmallPond" type="Node2D" parent="YSortWorld"]', sprite_block("shed", records["shed"]) + '\n\n' + sprite_block("fence", records["fence"]) + '\n\n[node name="SmallPond" type="Node2D" parent="YSortWorld"]')
    if NODE_NAMES["pond"] not in text:
        text = text.replace('[node name="Interactables" type="Node2D" parent="YSortWorld"]', sprite_block("pond", records["pond"]) + '\n\n[node name="Interactables" type="Node2D" parent="YSortWorld"]')
    if '[node name="LightAndWeather" type="Node2D" parent="."]' not in text:
        light_layers = [
            '[node name="LightAndWeather" type="Node2D" parent="."]',
            'z_index = -80',
            'metadata/purpose = "formal_back_farm_light_shadow_overlays"',
            sprite_block("shadow", records["shadow"]),
            sprite_block("light", records["light"]),
        ]
        text = text.replace('[node name="CameraRig" type="Camera2D" parent="."]', "\n".join(light_layers) + '\n\n[node name="CameraRig" type="Camera2D" parent="."]')
    if NODE_NAMES["foreground_grass"] not in text:
        text = text.replace('[node name="CameraRig" type="Camera2D" parent="."]', sprite_block("foreground_grass", records["foreground_grass"]) + '\n\n[node name="CameraRig" type="Camera2D" parent="."]')

    SCENE.write_text(text, encoding="utf-8", newline="\n")
    print("OK: integrated BackFarm v001 formal art into region_back_farm.tscn")


if __name__ == "__main__":
    main()
