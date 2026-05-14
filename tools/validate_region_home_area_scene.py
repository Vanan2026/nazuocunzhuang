from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "scenes" / "regions" / "region_home_area.tscn"
BACK_FARM_SCENE = ROOT / "scenes" / "regions" / "region_home_back_farm.tscn"
PROJECT = ROOT / "project.godot"
SCENE_TRANSITION_STATE = ROOT / "scripts" / "core" / "scene_transition_state.gd"
HOME_AREA_GRASS_YARD_ASSET = "res://sprites/environments/regions/home_area/ground/region_home_area_ground_grass_yard_v001.png"
HOME_AREA_FRONT_YARD_PATH_ASSET = "res://sprites/environments/regions/home_area/path/region_home_area_path_front_yard_v001.png"
HOME_AREA_FRONT_GRASS_LEFT_ASSET = "res://sprites/environments/regions/home_area/foreground/region_home_area_foreground_front_grass_left_v001.png"
ACTIVE_DEFAULT_FILES = (
    ROOT / "scripts" / "main.gd",
    ROOT / "scripts" / "world" / "backyard_entrance.gd",
    ROOT / "tools" / "load_scene.gd",
    ROOT / "tools" / "render_scene_snapshot.gd",
    ROOT / "tools" / "test_scene.gd",
)
ACTIVE_SCENE = "res://scenes/regions/region_home_area.tscn"
BACK_FARM_SCENE_PATH = "res://scenes/regions/region_home_back_farm.tscn"
HOME_AREA_FROM_BACK_FARM_SPAWN = "home_area_from_back_farm"
BACK_FARM_FROM_HOME_AREA_SPAWN = "back_farm_from_home_area"
LEGACY_SCENE_PREFIX = "res://scenes/world/"
LEGACY_TOOL_NAMES = (
    "build_cloud_village_homeyard_layers.py",
    "build_homeyard_assets.py",
    "derive_remaining_homeyard_layers.py",
    "formalize_homeyard_assets.py",
    "import_latest_generated_homeyard_asset.py",
    "preview_cloud_village_homeyard_layout.py",
    "slice_homeyard_from_mother.py",
    "validate_cloud_house_scene.py",
    "validate_cloud_house_visual.py",
    "validate_cloud_village_homeyard_scene.py",
    "validate_cloud_village_homeyard_visual.py",
    "validate_homeyard_assets.py",
)


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


def ext_resource_ids(scene_text: str, resource_path: str) -> set[str]:
    pattern = rf'\[ext_resource [^\]]*path="{re.escape(resource_path)}" [^\]]*id="([^"]+)"[^\]]*\]'
    return set(re.findall(pattern, scene_text))


def require_script_resource(scene_text: str, node_text: str, resource_path: str, label: str) -> None:
    ids = ext_resource_ids(scene_text, resource_path)
    require(ids, f"{label} missing script resource: {resource_path}")
    require(any(f'script = ExtResource("{resource_id}")' in node_text for resource_id in ids), label)


def require_scene_exit_spawn(
    exit_block: str,
    exit_name: str,
    target_scene_path: str,
    target_spawn_id: str,
    target_scene_text: str,
) -> None:
    require(f'target_scene = "{target_scene_path}"' in exit_block, f"{exit_name} must target {target_scene_path}")
    require(f'target_spawn_id = "{target_spawn_id}"' in exit_block, f"{exit_name} must set target_spawn_id={target_spawn_id}")
    require(
        f'metadata/target_spawn_id = "{target_spawn_id}"' in exit_block,
        f"{exit_name} must mirror target_spawn_id into metadata",
    )
    require(target_spawn_id in spawn_ids(target_scene_text), f"{target_scene_path} missing spawn_id={target_spawn_id}")


def require_sprite_module(scene_text: str, node_name: str, parent: str, asset_path: str) -> None:
    block = node_block(scene_text, node_name, parent)
    require(f'[node name="{node_name}" type="Sprite2D"' in block, f"{node_name} must be a Sprite2D PNG module")
    require("centered = false" in block, f"{node_name} must use top-left source-space placement")
    require("texture = ExtResource" in block, f"{node_name} must bind a PNG texture")
    require(asset_path in scene_text, f"{node_name} missing texture asset: {asset_path}")
    require((ROOT / asset_path.removeprefix("res://")).exists(), f"missing PNG asset: {asset_path}")


def main() -> None:
    require(SCENE.exists(), f"missing scene: {SCENE}")
    require(BACK_FARM_SCENE.exists(), f"missing scene: {BACK_FARM_SCENE}")
    scene_text = SCENE.read_text(encoding="utf-8")
    back_farm_text = BACK_FARM_SCENE.read_text(encoding="utf-8")
    project_text = PROJECT.read_text(encoding="utf-8")

    require(
        f'run/main_scene="{ACTIVE_SCENE}"' in project_text,
        "project main scene must point at Region_HomeArea",
    )
    require(SCENE_TRANSITION_STATE.exists(), "missing scene transition state autoload script")
    require(
        'SceneTransitionState="res://scripts/core/scene_transition_state.gd"' in project_text,
        "project must autoload SceneTransitionState",
    )

    for active_file in ACTIVE_DEFAULT_FILES:
        require(active_file.exists(), f"missing active default file: {active_file}")
        active_text = active_file.read_text(encoding="utf-8")
        require(
            LEGACY_SCENE_PREFIX not in active_text,
            f"{active_file.relative_to(ROOT)} must not default to legacy world scenes",
        )

    legacy_tool_root = ROOT / "tools" / "legacy_homeyard"
    for legacy_name in LEGACY_TOOL_NAMES:
        require(not (ROOT / "tools" / legacy_name).exists(), f"legacy tool still in active tools root: {legacy_name}")
        if legacy_tool_root.exists():
            require((legacy_tool_root / legacy_name).exists(), f"missing legacy tool: tools/legacy_homeyard/{legacy_name}")

    root = node_block(scene_text, "Region_HomeArea")
    require('metadata/world_model = "explorable_2d_oblique_region_v0_1"' in root, "root must declare explorable world model")
    require(
        "metadata/region_size = Vector2i(6144, 4096)" in root
        or "region_size = Vector2(6144, 4096)" in root,
        "root must declare 6144x4096 graybox region size",
    )

    for node_name in (
        "RegionBounds",
        "TileMapLayer_Ground",
        "TileMapLayer_Path",
        "TileMapLayer_Detail",
        "GroundDecorations",
        "WalkableZone",
        "YSortWorld",
        "ForegroundStatic",
        "LightAndWeather",
        "CameraRig",
        "CanvasLayer_UI",
    ):
        node_block(scene_text, node_name, ".")

    ground = node_block(scene_text, "TileMapLayer_Ground", ".")
    require("metadata/module_contract = \"modular_ground_patches_v0_1\"" in ground, "HomeArea ground must use modular ground contract")
    path = node_block(scene_text, "TileMapLayer_Path", ".")
    require("metadata/module_contract = \"modular_path_patches_v0_1\"" in path, "HomeArea path must use modular path contract")
    node_block(scene_text, "GroundModules", "TileMapLayer_Ground")
    node_block(scene_text, "PathModules", "TileMapLayer_Path")
    for node_name in ("GrassBaseNorth", "GrassBaseHomeYard", "GrassBaseSouth", "GardenSoilWest"):
        module = node_block(scene_text, node_name, "TileMapLayer_Ground/GroundModules")
        require('metadata/module_type = "ground_patch"' in module, f"{node_name} must be a replaceable ground patch")
    require_sprite_module(
        scene_text,
        "GrassBaseHomeYard",
        "TileMapLayer_Ground/GroundModules",
        HOME_AREA_GRASS_YARD_ASSET,
    )
    for node_name in ("VillageRoadNorthModule", "HomeFrontYardPathModule", "SouthStonePathModule", "WestGardenPathModule"):
        module = node_block(scene_text, node_name, "TileMapLayer_Path/PathModules")
        require('metadata/module_type = "path_patch"' in module, f"{node_name} must be a replaceable path patch")
    require_sprite_module(
        scene_text,
        "HomeFrontYardPathModule",
        "TileMapLayer_Path/PathModules",
        HOME_AREA_FRONT_YARD_PATH_ASSET,
    )

    walkable = node_block(scene_text, "WalkableZone", ".")
    require_script_resource(
        scene_text,
        walkable,
        "res://scripts/world/walkable_zone.gd",
        "WalkableZone must use shared walkable-zone script",
    )
    require("PackedVector2Array(" in walkable and "metadata/purpose = \"home_area_walkable_mask\"" in walkable, "WalkableZone must define a home-area polygon")

    ysort = node_block(scene_text, "YSortWorld", ".")
    require("y_sort_enabled = true" in ysort, "YSortWorld must enable y-sort")
    for child in ("Player", "Houses", "Trees", "Props", "Interactables", "NPCs", "Animals"):
        node_block(scene_text, child, "YSortWorld")

    player = node_block(scene_text, "Player", "YSortWorld")
    require_script_resource(scene_text, player, "res://scripts/player_controller.gd", "Player must use shared player controller")
    require('walkable_zone_path = NodePath("../../WalkableZone")' in player, "Player must bind to Region walkable zone")
    require("depth_scale_enabled = false" in player, "Player must keep scale stable in the graybox")
    require("sprite_frame_size = Vector2(192, 288)" in player and "sprite_foot_anchor = Vector2(96, 280)" in player, "Player must keep foot-anchor frame contract")
    node_block(scene_text, "PlayerSprite", "YSortWorld/Player")
    node_block(scene_text, "ShadowSprite", "YSortWorld/Player")

    camera = node_block(scene_text, "CameraRig", ".")
    require_script_resource(scene_text, camera, "res://scripts/world/camera_rig.gd", "CameraRig must use shared camera script")
    require('target_path = NodePath("../YSortWorld/Player")' in camera, "CameraRig must follow Player")
    require("limit_right = 6144" in camera and "limit_bottom = 4096" in camera, "CameraRig must use region bounds")

    for node_name in ("CloudHouse", "HouseMain", "HouseRoof", "HouseEaves"):
        node_block(scene_text, node_name, "YSortWorld/Houses" if node_name == "CloudHouse" else "YSortWorld/Houses/CloudHouse")
    for node_name in ("PersimmonTree", "BigShadeTree", "SmallLeftTree"):
        tree = node_block(scene_text, node_name, "YSortWorld/Trees")
        require('metadata/asset_type = "tree_split_graybox"' in tree, f"{node_name} must be a split tree graybox")
    for node_name in ("Mailbox", "Well", "Bench", "RoadSign", "CatBed"):
        prop = node_block(scene_text, node_name, "YSortWorld/Props")
        require('metadata/asset_type = "prop_graybox"' in prop, f"{node_name} must be a prop graybox")
    for node_name in ("MailboxInteract", "WellInteract", "BenchRestInteract", "RoadSignInteract", "HouseDoorEntrance", "BackyardFarmEntrance"):
        interactable = node_block(scene_text, node_name, "YSortWorld/Interactables")
        require("object_id =" in interactable or "target_scene =" in interactable, f"{node_name} must expose object id or transition target")
    bench_rest = node_block(scene_text, "BenchRestInteract", "YSortWorld/Interactables")
    require(
        ext_resource_ids(scene_text, "res://scripts/world/veranda_rest_area.gd")
        and any(
            f'script = ExtResource("{resource_id}")' in bench_rest
            for resource_id in ext_resource_ids(scene_text, "res://scripts/world/veranda_rest_area.gd")
        ),
        "BenchRestInteract must use the migrated veranda rest flow script",
    )
    require(
        "seat_anchor = Vector2(4110, 2428)" in bench_rest
        and "rest_facing = Vector2(1, 0)" in bench_rest
        and 'metadata/purpose = "veranda_rest_area"' in bench_rest,
        "BenchRestInteract must expose the current home-area seat anchor and rest facing",
    )
    require(
        "interaction_hint =" in bench_rest
        and "text =" in node_block(scene_text, "HintLabel", "YSortWorld/Interactables/BenchRestInteract"),
        "BenchRestInteract must show the rest interaction hint",
    )
    backyard = node_block(scene_text, "BackyardFarmEntrance", "YSortWorld/Interactables")
    require_scene_exit_spawn(
        backyard,
        "BackyardFarmEntrance",
        BACK_FARM_SCENE_PATH,
        BACK_FARM_FROM_HOME_AREA_SPAWN,
        back_farm_text,
    )

    foreground = node_block(scene_text, "ForegroundStatic", ".")
    require('metadata/layer_rule = "fixed_front_only_no_broad_rectangles"' in foreground, "ForegroundStatic must reject broad occlusion rectangles")
    node_block(scene_text, "FrontGrassLeft", "ForegroundStatic")
    node_block(scene_text, "FrontFlowersRight", "ForegroundStatic")
    require_sprite_module(scene_text, "FrontGrassLeft", "ForegroundStatic", HOME_AREA_FRONT_GRASS_LEFT_ASSET)

    require(
        (ROOT / "docs" / "scene_directory_status.md").exists(),
        "scene directory status doc must exist so old scene roles are explicit",
    )

    back_root = node_block(back_farm_text, "Region_HomeBackFarm")
    require('metadata/world_model = "explorable_2d_oblique_region_v0_1"' in back_root, "BackFarm root must declare explorable world model")
    require('metadata/region_id = "Region_HomeBackFarm"' in back_root, "BackFarm root must declare region id")
    for node_name in (
        "RegionBounds",
        "TileMapLayer_Ground",
        "TileMapLayer_Path",
        "TileMapLayer_Detail",
        "CropRows",
        "WalkableZone",
        "YSortWorld",
        "ForegroundStatic",
        "LightAndWeather",
        "CameraRig",
        "CanvasLayer_UI",
    ):
        node_block(back_farm_text, node_name, ".")
    node_block(back_farm_text, "GroundModules", "TileMapLayer_Ground")
    node_block(back_farm_text, "PathModules", "TileMapLayer_Path")
    back_walkable = node_block(back_farm_text, "WalkableZone", ".")
    require_script_resource(
        back_farm_text,
        back_walkable,
        "res://scripts/world/walkable_zone.gd",
        "BackFarm WalkableZone must use shared script",
    )
    back_ysort = node_block(back_farm_text, "YSortWorld", ".")
    require("y_sort_enabled = true" in back_ysort, "BackFarm YSortWorld must enable y-sort")
    for child in ("Player", "FarmStructures", "Props", "Interactables", "NPCs", "Animals"):
        node_block(back_farm_text, child, "YSortWorld")
    back_player = node_block(back_farm_text, "Player", "YSortWorld")
    require_script_resource(back_farm_text, back_player, "res://scripts/player_controller.gd", "BackFarm Player must use shared player controller")
    require('walkable_zone_path = NodePath("../../WalkableZone")' in back_player, "BackFarm Player must bind to walkable zone")
    back_camera = node_block(back_farm_text, "CameraRig", ".")
    require('target_path = NodePath("../YSortWorld/Player")' in back_camera, "BackFarm CameraRig must follow Player")
    for node_name in ("HomeAreaEntrance", "WateringCanInteract", "CompostBinInteract", "CropRowsInteract", "StorageCrateInteract"):
        interactable = node_block(back_farm_text, node_name, "YSortWorld/Interactables")
        require("object_id =" in interactable or "target_scene =" in interactable, f"{node_name} must expose object id or transition target")
    home_return = node_block(back_farm_text, "HomeAreaEntrance", "YSortWorld/Interactables")
    require_scene_exit_spawn(
        home_return,
        "HomeAreaEntrance",
        ACTIVE_SCENE,
        HOME_AREA_FROM_BACK_FARM_SPAWN,
        scene_text,
    )

    print("OK: Region_HomeArea scene contract validated")


if __name__ == "__main__":
    main()
