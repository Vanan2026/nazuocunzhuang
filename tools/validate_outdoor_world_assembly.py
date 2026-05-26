from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_GD = ROOT / "game" / "scenes" / "Main.gd"
OUTDOOR_TSCN = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.tscn"
OUTDOOR_GD = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"

OUTDOOR_REGION_IDS = [
    "player_yard",
    "forest_edge",
    "village",
    "back_farm",
    "orchard",
    "pond",
    "mountain_path",
    "mountain_hut",
    "mountain",
    "cliff_view",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    main_text = read(MAIN_GD)
    outdoor_scene_text = read(OUTDOOR_TSCN)
    outdoor_script_text = read(OUTDOOR_GD)

    outdoor_path = "res://game/scenes/world/OutdoorWorld.tscn"
    require(outdoor_path in main_text, "Main.gd should route outdoor scene ids through OutdoorWorld")
    for region_id in OUTDOOR_REGION_IDS:
        require(f'"{region_id}"' in main_text, f"Main.gd should keep {region_id} as a public outdoor scene id")
        require(f'"{region_id}"' in outdoor_script_text, f"OutdoorWorld.gd should define {region_id} as an active outdoor region")
    require("set_active_region" in main_text, "Main.gd should switch outdoor regions without reloading OutdoorWorld")

    require('path="res://game/scenes/world/OutdoorWorld.gd"' in outdoor_scene_text, "OutdoorWorld.tscn should use OutdoorWorld.gd")
    require("node name=\"OutdoorWorld\"" in outdoor_scene_text, "OutdoorWorld scene root should be named OutdoorWorld before runtime aliasing")

    required_script_tokens = [
        "class_name OutdoorWorld",
        "signal active_region_changed",
        "PLAYER_YARD_SCENE",
        "FOREST_EDGE_SCENE",
        "FOREST_EDGE_OFFSET",
        "REGION_OFFSETS",
        "REGION_SIZES",
        "GENERATED_REGION_TEXTURE_LAYERS",
        "func set_active_region",
        "func get_active_region_id",
        "func get_outdoor_region_ids",
        "func get_region_offset",
        "func get_region_bounds",
        "func refresh_runtime_ui",
        "func _compose_player_yard",
        "func _compose_forest_edge",
        "func _compose_generated_region_sections",
        "func _update_active_region_from_player",
    ]
    for token in required_script_tokens:
        require(token in outdoor_script_text, f"OutdoorWorld.gd missing token: {token}")

    print("OK: outdoor world assembly static validation passed")


if __name__ == "__main__":
    main()
