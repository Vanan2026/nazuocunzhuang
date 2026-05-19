from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "scenes/regions/region_home_area.tscn"
FORMAL_LAYER_ROOT = "res://production/assets/regions/home_area_formal/v001/layers"

EXT_RESOURCE_BLOCK = f'''[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_ground_yard_v001.png" id="15_ground_yard_art_v007"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_path_village_road_v001.png" id="16_formal_path_village"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_path_back_farm_v001.png" id="17_formal_path_back_farm"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_veranda_floor_v001.png" id="18_formal_veranda_floor"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_house_body_v001.png" id="19_formal_house_body"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_tree_left_trunk_v001.png" id="20_formal_tree_left_trunk"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_tree_right_trunk_v001.png" id="21_formal_tree_right_trunk"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_house_roof_occluder_v001.png" id="22_formal_house_roof"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_tree_left_canopy_occluder_v001.png" id="23_formal_tree_left_canopy"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_tree_right_canopy_occluder_v001.png" id="24_formal_tree_right_canopy"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_foreground_grass_v001.png" id="25_formal_foreground_grass"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_shadow_dappled_v001.png" id="26_formal_shadow_dappled"]
[ext_resource type="Texture2D" path="{FORMAL_LAYER_ROOT}/region_home_area_formal_light_overlay_v001.png" id="27_formal_light_overlay"]
[ext_resource type="Script" uid="uid://5031fus607k5" path="res://game/entities/visual/RuntimeTextureSprite.gd" id="28_runtime_sprite"]'''


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def replace_ext_resources(text: str) -> str:
    pattern = r'\[ext_resource type="Texture2D"[^\n]*id="15_ground_yard_art_v007"\]\n\[ext_resource type="Script"[^\n]*id="28_runtime_sprite"\]\n\[ext_resource type="Texture2D"[^\n]*id="29_foreground_grass_art_v007"\]'
    text, count = re.subn(pattern, EXT_RESOURCE_BLOCK, text)
    if count == 1:
        return text
    if 'id="16_formal_path_village"' in text and 'id="27_formal_light_overlay"' in text:
        return text
    fail(f"expected to replace one formal review ext_resource block, replaced {count}")


def node_pattern(name: str, parent: str | None = None) -> str:
    if parent is None:
        return rf'(\[node name="{re.escape(name)}" [^\]]*\].*?)(?=\n\[node |\n\[connection |\Z)'
    return rf'(\[node name="{re.escape(name)}" [^\]]*parent="{re.escape(parent)}"[^\]]*\].*?)(?=\n\[node |\n\[connection |\Z)'


def set_prop(block: str, key: str, value: str) -> str:
    line = f"{key} = {value}"
    pattern = rf'^{re.escape(key)} = .*$'
    new_block, count = re.subn(pattern, line, block, count=1, flags=re.M)
    if count == 0:
        parts = new_block.split("\n", 1)
        if len(parts) == 1:
            return new_block + "\n" + line
        return parts[0] + "\n" + line + "\n" + parts[1]
    return new_block


def set_props(text: str, name: str, parent: str | None, props: dict[str, str]) -> str:
    pattern = node_pattern(name, parent)
    match = re.search(pattern, text, re.S)
    if match is None:
        fail(f"missing node block: {parent + '/' if parent else ''}{name}")
    block = match.group(1)
    new_block = block
    for key, value in props.items():
        new_block = set_prop(new_block, key, value)
    return text[: match.start(1)] + new_block + text[match.end(1) :]


def remove_prop(text: str, name: str, parent: str | None, key: str) -> str:
    pattern = node_pattern(name, parent)
    match = re.search(pattern, text, re.S)
    if match is None:
        fail(f"missing node block: {parent + '/' if parent else ''}{name}")
    block = match.group(1)
    block = re.sub(rf'^\s*{re.escape(key)} = .*\n?', '', block, flags=re.M)
    return text[: match.start(1)] + block + text[match.end(1) :]


def main() -> None:
    text = SCENE.read_text(encoding="utf-8-sig")
    text = replace_ext_resources(text)
    replacements = {
        'metadata/status = "active_home_area_formal_v001_full_plate_review_candidate"': 'metadata/status = "active_home_area_formal_v001_split_review_candidate"',
        'metadata/art_integration_group = "formal_full_plate_review_v001"': 'metadata/art_integration_group = "formal_split_review_v001"',
        'metadata/formal_asset_pass = "home_area_formal_v001_full_plate_review_2026_05_18"': 'metadata/formal_asset_pass = "home_area_formal_v001_split_review_2026_05_18"',
        'metadata/paint_id = "formal_full_plate_v001"': 'metadata/paint_id = "formal_ground_underpaint_v001"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace('size = Vector2(860, 340)', 'size = Vector2(2100, 360)', 1)
    text = text.replace('size = Vector2(126, 82)', 'size = Vector2(120, 90)', 1)
    text = text.replace('size = Vector2(300, 96)', 'size = Vector2(280, 110)', 1)
    text = text.replace('size = Vector2(360, 92)', 'size = Vector2(540, 110)', 1)
    text = text.replace('size = Vector2(72, 56)', 'size = Vector2(110, 75)', 1)
    text = text.replace('size = Vector2(150, 110)', 'size = Vector2(180, 130)', 1)

    text = set_props(text, "GroundYardArtV007", "TileMapLayer_Ground/GroundModules", {
        "texture": 'ExtResource("15_ground_yard_art_v007")',
        "metadata/paint_id": '"formal_ground_underpaint_v001"',
    })
    text = set_props(text, "VillageRoadArtV007", "TileMapLayer_Path/PathModules", {
        "position": "Vector2(430, 0)",
        "texture": 'ExtResource("16_formal_path_village")',
        "metadata/paint_id": '"formal_path_village_road_v001"',
    })
    text = set_props(text, "BackFarmPathArtV007", "TileMapLayer_Path/PathModules", {
        "position": "Vector2(2720, 1880)",
        "texture": 'ExtResource("17_formal_path_back_farm")',
        "metadata/paint_id": '"formal_path_back_farm_v001"',
    })
    text = set_props(text, "VerandaFloorArtV007", "TileMapLayer_Detail", {
        "position": "Vector2(1890, 1350)",
        "texture": 'ExtResource("18_formal_veranda_floor")',
        "metadata/paint_id": '"formal_veranda_floor_v001"',
    })
    text = set_props(text, "WalkableZone", ".", {
        "polygon": "PackedVector2Array(430, 1600, 1220, 1440, 1930, 1680, 2920, 1760, 3880, 1780, 4560, 2220, 4580, 3720, 3840, 3900, 3020, 3180, 1800, 2650, 760, 2220)",
    })
    text = set_props(text, "CloudHouse", "YSortWorld/Houses", {"position": "Vector2(3160, 1660)"})
    text = set_props(text, "HouseBodyArtV007", "YSortWorld/Houses/CloudHouse", {
        "position": "Vector2(-1350, -760)",
        "texture": 'ExtResource("19_formal_house_body")',
        "metadata/paint_id": '"formal_house_body_v001"',
    })
    text = set_props(text, "HouseBlocker", "YSortWorld/Houses/CloudHouse", {"position": "Vector2(-150, 0)"})

    text = set_props(text, "PersimmonTree", "YSortWorld/Trees", {"position": "Vector2(4460, 2220)"})
    text = set_props(text, "TreeRightTrunkArtV007", "YSortWorld/Trees/PersimmonTree", {
        "position": "Vector2(-410, -1540)",
        "texture": 'ExtResource("21_formal_tree_right_trunk")',
        "metadata/paint_id": '"formal_tree_right_trunk_v001"',
    })
    text = set_props(text, "PersimmonRootBlocker", "YSortWorld/Trees/PersimmonTree", {"position": "Vector2(0, -40)"})
    text = set_props(text, "TreeBlocker", "YSortWorld/Trees/PersimmonTree", {"position": "Vector2(0, -320)"})

    text = set_props(text, "BigShadeTree", "YSortWorld/Trees", {"position": "Vector2(720, 1855)"})
    text = set_props(text, "TreeLeftTrunkArtV007", "YSortWorld/Trees/BigShadeTree", {
        "position": "Vector2(-460, -1335)",
        "texture": 'ExtResource("20_formal_tree_left_trunk")',
        "metadata/paint_id": '"formal_tree_left_trunk_v001"',
    })
    text = set_props(text, "BigShadeRootBlocker", "YSortWorld/Trees/BigShadeTree", {"position": "Vector2(0, -70)"})
    text = set_props(text, "TreeBlocker", "YSortWorld/Trees/BigShadeTree", {"position": "Vector2(0, -420)"})

    text = set_props(text, "Mailbox", "YSortWorld/Props", {"position": "Vector2(1980, 1760)"})
    text = set_props(text, "MailboxArt", "YSortWorld/Props/Mailbox", {
        "position": "Vector2(-220, -580)",
        "scale": "Vector2(1, 1)",
        "texture_path": f'"{FORMAL_LAYER_ROOT}/region_home_area_formal_prop_mailbox_v001.png"',
        "metadata/paint_id": '"formal_prop_mailbox_v001"',
    })
    text = set_props(text, "Well", "YSortWorld/Props", {"position": "Vector2(4580, 2840)"})
    text = set_props(text, "WellArt", "YSortWorld/Props/Well", {
        "position": "Vector2(-390, -810)",
        "scale": "Vector2(1, 1)",
        "texture_path": f'"{FORMAL_LAYER_ROOT}/region_home_area_formal_prop_well_v001.png"',
        "metadata/paint_id": '"formal_prop_well_v001"',
    })
    text = set_props(text, "Bench", "YSortWorld/Props", {"position": "Vector2(940, 2020)"})
    text = set_props(text, "BenchArt", "YSortWorld/Props/Bench", {
        "position": "Vector2(-420, -680)",
        "scale": "Vector2(1, 1)",
        "texture_path": f'"{FORMAL_LAYER_ROOT}/region_home_area_formal_prop_bench_v001.png"',
        "metadata/paint_id": '"formal_prop_bench_left_fence_v001"',
    })
    text = set_props(text, "RoadSign", "YSortWorld/Props", {"position": "Vector2(5085, 3270)"})
    text = set_props(text, "RoadSignArt", "YSortWorld/Props/RoadSign", {
        "position": "Vector2(-235, -410)",
        "scale": "Vector2(1, 1)",
        "texture_path": f'"{FORMAL_LAYER_ROOT}/region_home_area_formal_prop_road_sign_v001.png"',
        "metadata/paint_id": '"formal_prop_road_sign_v001"',
    })
    text = set_props(text, "CatBed", "YSortWorld/Props", {"visible": "false"})
    text = set_props(text, "CatBedArt", "YSortWorld/Props/CatBed", {
        "texture_path": f'"{FORMAL_LAYER_ROOT}/region_home_area_formal_prop_cat_bed_v001.png"',
        "metadata/paint_id": '"formal_prop_cat_bed_hidden_placeholder_v001"',
    })

    text = set_props(text, "MailboxInteract", "YSortWorld/Interactables", {"position": "Vector2(1980, 1760)"})
    text = set_props(text, "WellInteract", "YSortWorld/Interactables", {"position": "Vector2(4580, 2840)"})
    text = set_props(text, "BenchRestInteract", "YSortWorld/Interactables", {
        "position": "Vector2(940, 2020)",
        "seat_anchor": "Vector2(4940, 8020)",
        "interaction_hint": '"\u6309 E \u5750\u4e0b\u4f11\u606f"',
    })
    text = set_props(text, "RoadSignInteract", "YSortWorld/Interactables", {"position": "Vector2(5085, 3270)"})
    text = set_props(text, "HouseDoorEntrance", "YSortWorld/Interactables", {"position": "Vector2(3000, 1910)"})
    text = set_props(text, "BackyardFarmEntrance", "YSortWorld/Interactables", {"position": "Vector2(4200, 3370)"})
    text = set_props(text, "PlayerSpawn", "YSortWorld", {"position": "Vector2(3300, 2380)"})

    text = set_props(text, "HouseRoofOccluderArtV007", "ForegroundStatic/Occluders", {
        "position": "Vector2(1680, 235)",
        "texture": 'ExtResource("22_formal_house_roof")',
        "metadata/paint_id": '"formal_house_roof_occluder_v001"',
    })
    text = set_props(text, "TreeLeftCanopyOccluderArtV007", "ForegroundStatic/Occluders", {
        "position": "Vector2(0, 0)",
        "texture": 'ExtResource("23_formal_tree_left_canopy")',
        "metadata/paint_id": '"formal_tree_left_canopy_occluder_v001"',
    })
    text = set_props(text, "TreeRightCanopyOccluderArtV007", "ForegroundStatic/Occluders", {
        "position": "Vector2(3710, 0)",
        "texture": 'ExtResource("24_formal_tree_right_canopy")',
        "metadata/paint_id": '"formal_tree_right_canopy_occluder_v001"',
    })
    text = set_props(text, "ForegroundGrassArtV007", "ForegroundStatic", {
        "position": "Vector2(0, 3000)",
        "texture": 'ExtResource("25_formal_foreground_grass")',
        "metadata/paint_id": '"formal_foreground_grass_v001"',
    })
    text = set_props(text, "ShadowDappledArtV007", "LightAndWeather", {
        "texture": 'ExtResource("26_formal_shadow_dappled")',
        "z_index": "0",
        "metadata/paint_id": '"formal_shadow_dappled_v001"',
    })
    text = set_props(text, "LightOverlayArtV007", "LightAndWeather", {
        "texture": 'ExtResource("27_formal_light_overlay")',
        "z_index": "1",
        "metadata/paint_id": '"formal_light_overlay_v001"',
    })

    SCENE.write_text(text, encoding="utf-8", newline="\n")
    print("OK: integrated HomeArea formal/v001 split layers into region scene")


if __name__ == "__main__":
    main()