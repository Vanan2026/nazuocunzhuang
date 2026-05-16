from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "project.godot"
WORLD_SCENE = ROOT / "scenes" / "world" / "world.tscn"
HOME_SCENE = ROOT / "scenes" / "regions" / "region_home_area.tscn"
BACK_FARM_SCENE = ROOT / "scenes" / "regions" / "region_back_farm.tscn"
WORLD_CONTROLLER = ROOT / "scripts" / "world" / "world_controller.gd"
PLAYER_CONTROLLER = ROOT / "scripts" / "player_controller.gd"
INTERACTION_HINT_UI = ROOT / "scripts" / "world" / "interaction_hint_ui.gd"

WORLD_SCENE_PATH = "res://scenes/world/world.tscn"
HOME_SCENE_PATH = "res://scenes/regions/region_home_area.tscn"
BACK_FARM_SCENE_PATH = "res://scenes/regions/region_back_farm.tscn"

ART_V003_ROOT = "res://production/assets/regions/home_area_art/v003"
RUNTIME_PROP_SCRIPT = "res://game/entities/visual/RuntimeTextureSprite.gd"
RUNTIME_PROP_TEXTURES = {
    "MailboxArt": (
        "YSortWorld/Props/Mailbox",
        "res://assets/art/props/region_home_area_prop_mailbox_v001.png",
        "mailbox_art_v001",
        ("Body", "Post"),
    ),
    "WellArt": (
        "YSortWorld/Props/Well",
        "res://assets/art/props/region_home_area_prop_well_broken_v001.png",
        "well_broken_art_v001",
        ("Curb", "Roof"),
    ),
    "BenchArt": (
        "YSortWorld/Props/Bench",
        "res://assets/art/props/region_home_area_prop_bench_v001.png",
        "bench_art_v001",
        ("Seat", "Legs"),
    ),
    "RoadSignArt": (
        "YSortWorld/Props/RoadSign",
        "res://assets/art/props/region_home_area_prop_road_sign_v001.png",
        "road_sign_art_v001",
        ("Board", "Post"),
    ),
}
RUNTIME_PROP_BLOCKERS = {
    "Mailbox": "RectangleShape2D_prop_small",
    "Well": "RectangleShape2D_well",
    "Bench": "RectangleShape2D_bench",
    "RoadSign": "RectangleShape2D_road_sign",
}
ART_V003_TEXTURES = {
    "ground_yard": f"{ART_V003_ROOT}/region_home_area_ground_yard_v003.png",
    "path_village_road": f"{ART_V003_ROOT}/region_home_area_path_village_road_v003.png",
    "path_back_farm": f"{ART_V003_ROOT}/region_home_area_path_back_farm_v003.png",
    "house_body": f"{ART_V003_ROOT}/region_home_area_house_body_v003.png",
    "house_roof_occluder": f"{ART_V003_ROOT}/region_home_area_house_roof_occluder_v003.png",
    "veranda_floor": f"{ART_V003_ROOT}/region_home_area_veranda_floor_v003.png",
    "tree_left_trunk": f"{ART_V003_ROOT}/region_home_area_tree_left_trunk_v003.png",
    "tree_left_canopy": f"{ART_V003_ROOT}/region_home_area_tree_left_canopy_occluder_v003.png",
    "tree_right_trunk": f"{ART_V003_ROOT}/region_home_area_tree_right_trunk_v003.png",
    "tree_right_canopy": f"{ART_V003_ROOT}/region_home_area_tree_right_canopy_occluder_v003.png",
    "foreground_grass": f"{ART_V003_ROOT}/region_home_area_foreground_grass_v003.png",
    "shadow_dappled": f"{ART_V003_ROOT}/region_home_area_shadow_dappled_v003.png",
    "light_overlay": f"{ART_V003_ROOT}/region_home_area_light_overlay_v003.png",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def node_block(scene_text: str, name: str, parent: str | None = None) -> str:
    if parent is None:
        header = rf'\[node name="{re.escape(name)}" [^\]]*\]'
    else:
        header = rf'\[node name="{re.escape(name)}" [^\]]*parent="{re.escape(parent)}"[^\]]*\]'
    match = re.search(header + r".*?(?=\n\[node |\n\[connection |\Z)", scene_text, re.S)
    if match is None:
        location = f"{parent}/{name}" if parent else name
        fail(f"missing node: {location}")
    return match.group(0)


def spawn_ids(scene_text: str) -> set[str]:
    return set(re.findall(r'metadata/spawn_id = "([^"]+)"', scene_text))


def require_node_path(scene_text: str, name: str, parent: str) -> str:
    block = node_block(scene_text, name, parent)
    require(block, f"missing {parent}/{name}")
    return block


def require_texture(scene_text: str, texture_path: str) -> None:
    require(texture_path in scene_text, f"missing texture resource path: {texture_path}")
    require((ROOT / texture_path.removeprefix("res://")).exists(), f"missing texture file: {texture_path}")


def require_sprite_art_module(scene_text: str, node_name: str, parent: str, texture_path: str, paint_id: str) -> None:
    block = node_block(scene_text, node_name, parent)
    require(f'[node name="{node_name}" type="Sprite2D"' in block, f"{node_name} must be Sprite2D")
    require("centered = false" in block, f"{node_name} must use top-left placement")
    require("texture = ExtResource" in block, f"{node_name} must bind a texture")
    require('metadata/asset_package = "home_area_art_v003"' in block, f"{node_name} must record asset package")
    require(f'metadata/paint_id = "{paint_id}"' in block, f"{node_name} must record paint id")
    require_texture(scene_text, texture_path)

    if node_name in {"VillageRoadArtV003", "BackFarmPathArtV003", "VerandaFloorArtV003"}:
        require("visible = false" not in block, f"{node_name} must be visible in the v003 runtime candidate")


def require_hidden(scene_text: str, name: str, parent: str) -> None:
    block = node_block(scene_text, name, parent)
    require("visible = false" in block, f"{parent}/{name} must be hidden after art v003 replacement")


def validate_project() -> None:
    require(PROJECT.exists(), "missing project.godot")
    require(WORLD_SCENE.exists(), "missing world scene")
    text = PROJECT.read_text(encoding="utf-8")
    require(f'run/main_scene="{WORLD_SCENE_PATH}"' in text, "project main scene must be world.tscn")


def validate_runtime_scripts() -> None:
    require(WORLD_CONTROLLER.exists(), "missing world_controller.gd")
    world_controller = WORLD_CONTROLLER.read_text(encoding="utf-8")
    require("camera_look_ahead_offset: Vector2 = Vector2(0, -280)" in world_controller, "World camera must keep an upward look-ahead offset for HomeArea composition")
    require("player.global_position + camera_look_ahead_offset" in world_controller, "World camera must follow the player with look-ahead offset")

    require(PLAYER_CONTROLLER.exists(), "missing player_controller.gd")
    player_controller = PLAYER_CONTROLLER.read_text(encoding="utf-8")
    require('"move_left", "ui_left", "move_right", "ui_right"' in player_controller, "Player movement must read project move_* actions with ui_* fallback")
    require('"move_up", "ui_up", "move_down", "ui_down"' in player_controller, "Player movement must read vertical project move_* actions with ui_* fallback")
    require("func _update_nearest_interaction_hint()" in player_controller, "Player must refresh nearest interaction hint continuously")

    require(INTERACTION_HINT_UI.exists(), "missing interaction_hint_ui.gd")
    hint_ui = INTERACTION_HINT_UI.read_text(encoding="utf-8")
    require("func _create_default_hint_label()" in hint_ui, "InteractionHintUI must create its own prompt label when autoloaded")
    require('label.name = "InteractionPrompt"' in hint_ui, "InteractionHintUI default prompt label must be named InteractionPrompt")


def validate_home_area() -> None:
    require(HOME_SCENE.exists(), f"missing scene: {HOME_SCENE}")
    scene_text = HOME_SCENE.read_text(encoding="utf-8")
    root = node_block(scene_text, "Region_HomeArea")
    require('region_id = "Region_HomeArea"' in root, "HomeArea region_id must be Region_HomeArea")
    require("region_size = Vector2(6144, 4096)" in root, "HomeArea region size must be 6144x4096")
    require('metadata/art_package = "home_area_art_v003"' in root, "HomeArea must record active art package")
    require('metadata/art_integration_group = "foundation_depth_v003"' in root, "HomeArea must record active art integration group")

    for node_name in (
        "RegionRuntime",
        "TileMapLayer_Ground",
        "TileMapLayer_Path",
        "TileMapLayer_Detail",
        "WalkableZone",
        "YSortWorld",
        "ForegroundStatic",
        "LightAndWeather",
        "CameraRig",
    ):
        node_block(scene_text, node_name, ".")

    require_node_path(scene_text, "GroundModules", "TileMapLayer_Ground")
    require_node_path(scene_text, "PathModules", "TileMapLayer_Path")
    require_node_path(scene_text, "Occluders", "ForegroundStatic")

    require_sprite_art_module(
        scene_text,
        "GroundYardArtV003",
        "TileMapLayer_Ground/GroundModules",
        ART_V003_TEXTURES["ground_yard"],
        "ground_yard_art_v003",
    )
    require_sprite_art_module(
        scene_text,
        "VillageRoadArtV003",
        "TileMapLayer_Path/PathModules",
        ART_V003_TEXTURES["path_village_road"],
        "path_village_road_art_v003",
    )
    require_sprite_art_module(
        scene_text,
        "BackFarmPathArtV003",
        "TileMapLayer_Path/PathModules",
        ART_V003_TEXTURES["path_back_farm"],
        "path_back_farm_art_v003",
    )
    for node_name, parent, texture_key, paint_id in (
        ("VerandaFloorArtV003", "TileMapLayer_Detail", "veranda_floor", "veranda_floor_art_v003"),
        ("HouseBodyArtV003", "YSortWorld/Houses/CloudHouse", "house_body", "house_body_art_v003"),
        ("TreeLeftTrunkArtV003", "YSortWorld/Trees/BigShadeTree", "tree_left_trunk", "tree_left_trunk_art_v003"),
        ("TreeRightTrunkArtV003", "YSortWorld/Trees/PersimmonTree", "tree_right_trunk", "tree_right_trunk_art_v003"),
        ("HouseRoofOccluderArtV003", "ForegroundStatic/Occluders", "house_roof_occluder", "house_roof_occluder_art_v003"),
        ("TreeLeftCanopyOccluderArtV003", "ForegroundStatic/Occluders", "tree_left_canopy", "tree_left_canopy_occluder_art_v003"),
        ("TreeRightCanopyOccluderArtV003", "ForegroundStatic/Occluders", "tree_right_canopy", "tree_right_canopy_occluder_art_v003"),
        ("ForegroundGrassArtV003", "ForegroundStatic", "foreground_grass", "foreground_grass_art_v003"),
        ("ShadowDappledArtV003", "LightAndWeather", "shadow_dappled", "shadow_dappled_art_v003"),
        ("LightOverlayArtV003", "LightAndWeather", "light_overlay", "light_overlay_art_v003"),
    ):
        require_sprite_art_module(scene_text, node_name, parent, ART_V003_TEXTURES[texture_key], paint_id)

    for name, parent in (
        ("GroundBase", "TileMapLayer_Ground"),
        ("GrassBaseNorth", "TileMapLayer_Ground/GroundModules"),
        ("GrassBaseHomeYard", "TileMapLayer_Ground/GroundModules"),
        ("GrassBaseSouth", "TileMapLayer_Ground/GroundModules"),
        ("GardenSoilWest", "TileMapLayer_Ground/GroundModules"),
        ("VillageRoadNorth", "TileMapLayer_Path"),
        ("HomeFrontYardPath", "TileMapLayer_Path"),
        ("SouthStonePath", "TileMapLayer_Path"),
        ("WestGardenPath", "TileMapLayer_Path"),
        ("VillageRoadNorthModule", "TileMapLayer_Path/PathModules"),
        ("HomeFrontYardPathModule", "TileMapLayer_Path/PathModules"),
        ("SouthStonePathModule", "TileMapLayer_Path/PathModules"),
        ("WestGardenPathModule", "TileMapLayer_Path/PathModules"),
        ("PebbleBand", "TileMapLayer_Detail"),
        ("FlowerPatchGuide", "TileMapLayer_Detail"),
        ("SoftTreeShadows", "GroundDecorations"),
        ("HouseShadow", "GroundDecorations"),
        ("HouseMain", "YSortWorld/Houses/CloudHouse"),
        ("HouseRoof", "YSortWorld/Houses/CloudHouse"),
        ("HouseEaves", "YSortWorld/Houses/CloudHouse"),
        ("DoorMarker", "YSortWorld/Houses/CloudHouse"),
        ("Canopy", "YSortWorld/Trees/PersimmonTree"),
        ("Trunk", "YSortWorld/Trees/PersimmonTree"),
        ("Canopy", "YSortWorld/Trees/BigShadeTree"),
        ("Trunk", "YSortWorld/Trees/BigShadeTree"),
        ("Canopy", "YSortWorld/Trees/SmallLeftTree"),
        ("Trunk", "YSortWorld/Trees/SmallLeftTree"),
        ("FrontGrassLeft", "ForegroundStatic"),
        ("FrontFlowersRight", "ForegroundStatic"),
        ("DappledLight", "LightAndWeather"),
        ("WindLeavesGuide", "LightAndWeather"),
    ):
        require_hidden(scene_text, name, parent)

    ysort = node_block(scene_text, "YSortWorld", ".")
    require("y_sort_enabled = true" in ysort, "HomeArea YSortWorld must enable y-sort")
    for child in ("Player", "Houses", "Trees", "Props", "Interactables", "NPCs", "Animals"):
        node_block(scene_text, child, "YSortWorld")

    require(RUNTIME_PROP_SCRIPT in scene_text, "Region_HomeArea must reference RuntimeTextureSprite for runtime prop art")
    for node_name, (parent, texture_path, paint_id, hidden_children) in RUNTIME_PROP_TEXTURES.items():
        block = node_block(scene_text, node_name, parent)
        require(f'[node name="{node_name}" type="Sprite2D"' in block, f"{node_name} must be Sprite2D")
        require("script = ExtResource" in block, f"{node_name} must use RuntimeTextureSprite")
        require(f'texture_path = "{texture_path}"' in block, f"{node_name} must load {texture_path}")
        require(f'metadata/paint_id = "{paint_id}"' in block, f"{node_name} must record paint id")
        require((ROOT / texture_path.removeprefix("res://")).exists(), f"missing runtime prop art: {texture_path}")
        for child_name in hidden_children:
            require_hidden(scene_text, child_name, parent)

    for prop_name, shape_id in RUNTIME_PROP_BLOCKERS.items():
        blocker = node_block(scene_text, "PropBlocker", f"YSortWorld/Props/{prop_name}")
        require("StaticBody2D" in blocker, f"{prop_name} must keep a StaticBody2D blocker")
        collision = node_block(scene_text, "CollisionShape2D", f"YSortWorld/Props/{prop_name}/PropBlocker")
        require(f'SubResource("{shape_id}")' in collision, f"{prop_name} blocker must use {shape_id}")

    cat_bed = node_block(scene_text, "CatBed", "YSortWorld/Props")
    require("visible = false" not in cat_bed, "CatBed must be visible once runtime art exists")
    require('metadata/asset_type = "runtime_prop_art"' in cat_bed, "CatBed must record runtime prop art status")
    cat_bed_art = node_block(scene_text, "CatBedArt", "YSortWorld/Props/CatBed")
    require("script = ExtResource" in cat_bed_art, "CatBedArt must use RuntimeTextureSprite")
    require('texture_path = "res://assets/art/props/region_home_area_prop_cat_bed_v001.png"' in cat_bed_art, "CatBedArt must load runtime CatBed PNG")
    require((ROOT / "assets/art/props/region_home_area_prop_cat_bed_v001.png").exists(), "missing runtime CatBed art")
    require_hidden(scene_text, "Cushion", "YSortWorld/Props/CatBed")

    player = node_block(scene_text, "Player", "YSortWorld")
    require('walkable_zone_path = NodePath("../../WalkableZone")' in player, "HomeArea Player must bind WalkableZone")
    require("sprite_frame_size = Vector2(192, 288)" in player, "HomeArea Player frame size must remain stable")
    require("sprite_foot_anchor = Vector2(96, 280)" in player, "HomeArea Player foot anchor must remain stable")

    backyard = node_block(scene_text, "BackyardFarmEntrance", "YSortWorld/Interactables")
    require('target_region_id = "Region_BackFarm"' in backyard, "HomeArea exit must target Region_BackFarm")
    require('target_spawn_id = "back_farm_default"' in backyard, "HomeArea exit must target back_farm_default")
    house_door = node_block(scene_text, "HouseDoorEntrance", "YSortWorld/Interactables")
    require("position = Vector2(3300, 1880)" in house_door, "HomeArea house-door interaction must be reachable from the default player spawn")
    require('interaction_hint = "按 E 查看屋檐"' in house_door, "HomeArea house-door interaction must expose the current launch hint")
    require("home_area_default" in spawn_ids(scene_text), "HomeArea missing default spawn")
    require("home_area_from_back_farm" in spawn_ids(scene_text), "HomeArea missing return spawn")


def validate_back_farm() -> None:
    require(BACK_FARM_SCENE.exists(), f"missing scene: {BACK_FARM_SCENE}")
    scene_text = BACK_FARM_SCENE.read_text(encoding="utf-8")
    root = node_block(scene_text, "Region_BackFarm")
    require('region_id = "Region_BackFarm"' in root, "BackFarm region_id must be Region_BackFarm")
    require("region_size = Vector2(2000, 2000)" in root, "BackFarm region size must be 2000x2000")
    for node_name in (
        "FarmSystem",
        "TileMapLayer_Ground",
        "TileMapLayer_Path",
        "TileMapLayer_Detail",
        "WalkableZone",
        "YSortWorld",
        "ForegroundStatic",
        "CameraRig",
    ):
        node_block(scene_text, node_name, ".")
    ysort = node_block(scene_text, "YSortWorld", ".")
    require("y_sort_enabled = true" in ysort, "BackFarm YSortWorld must enable y-sort")
    for plot in ("FarmPlot0", "FarmPlot1", "FarmPlot2", "FarmPlot3"):
        block = node_block(scene_text, plot, "YSortWorld/Interactables")
        require("plot_index =" in block, f"{plot} must expose plot_index")
    exit_block = node_block(scene_text, "ExitToHomeArea", "YSortWorld/Interactables")
    require('target_region_id = "Region_HomeArea"' in exit_block, "BackFarm exit must target Region_HomeArea")
    require('target_spawn_id = "home_area_from_back_farm"' in exit_block, "BackFarm exit must target HomeArea return spawn")
    require("back_farm_default" in spawn_ids(scene_text), "BackFarm missing default spawn")


def main() -> None:
    validate_project()
    validate_runtime_scripts()
    validate_home_area()
    validate_back_farm()
    print("OK: Region_HomeArea scene contract validated")


if __name__ == "__main__":
    main()
