from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bcombat\b",
        r"\bmonster\b",
        r"\bdamage\b",
        r"\bweapon\b",
        r"\bhp\b",
        r"\bkill\b",
        r"\bloot\b",
    ]
]

EXPECTED_SNIPPETS: dict[str, list[str]] = {
    "game/scenes/Main.gd": [
        "class_name MainFlow",
        "const SCENE_REGISTRY",
        "func change_scene(",
        "func sync_current_scene_state(",
        "func apply_shared_state_to_current_scene(",
        "func build_main_flow_save_data(",
        "QuestManager",
    ],
    "game/scenes/Main.tscn": [
        "res://game/scenes/Main.gd",
        '[node name="SceneRouter" type="Node" parent="."',
        '[node name="QuestManager" type="Node" parent="."',
        '[node name="CurrentScene" type="Node" parent="."',
    ],
    "game/autoload/SceneRouter.gd": [
        "func request_scene_change(",
        "func set_current_scene(",
        "func get_current_spawn_id(",
        "func get_save_data(",
        "func apply_save_data(",
    ],
    "game/autoload/SaveManager.gd": [
        '"scene":',
        '"quests":',
        "QuestManager",
        "SceneRouter",
    ],
    "game/autoload/QuestManager.gd": [
        "FIRST_WEEK_QUEST_ID",
        "func update_first_week_progress(",
        "func get_first_week_progress(",
        "func is_first_week_complete(",
        "func get_save_data(",
        "func apply_save_data(",
    ],
    "game/entities/interactable/SceneTravel.gd": [
        "target_scene_id",
        "target_spawn_id",
        "request_scene_change",
        "SceneRouter",
    ],
    "game/entities/npc/NPC.gd": [
        "rumor_manager_path",
        "func _try_rumor_interaction(",
        "build_rumor_dialogue",
        "mark_dialogue_rumors_seen",
    ],
    "game/systems/npc/NpcScheduleDirector.gd": [
        "scene_id",
        "npc_node.visible = false",
        "func get_current_assignment(",
    ],
    "game/systems/scene/SpawnPoint.gd": [
        "class_name SpawnPoint",
        "@export var spawn_id",
    ],
    "game/scenes/home/PlayerHouse.tscn": [
        "res://game/systems/scene/SpawnPoint.gd",
        'spawn_id = "inside_default"',
        'target_scene_id = "player_yard"',
        'target_spawn_id = "from_house"',
    ],
    "game/scenes/world/PlayerYard.tscn": [
        "res://game/systems/scene/SpawnPoint.gd",
        'spawn_id = "from_house"',
        'spawn_id = "from_forest_edge"',
        'target_scene_id = "forest_edge"',
        'target_spawn_id = "from_yard"',
    ],
    "game/scenes/world/ForestEdge.tscn": [
        "res://game/systems/scene/SpawnPoint.gd",
        "res://game/systems/npc/NpcScheduleDirector.gd",
        'spawn_id = "from_yard"',
        'target_scene_id = "player_yard"',
        'target_spawn_id = "from_forest_edge"',
        '[node name="NPCs" type="Node2D" parent="."',
        '[node name="ScheduleDirector" type="Node" parent="."',
        '[node name="Mika" parent="NPCs"',
    ],
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        fail(f"missing file: {relative_path}")
    return path.read_text(encoding="utf-8")


def load_json_array(relative_path: str) -> list[dict[str, Any]]:
    path = ROOT / relative_path
    if not path.is_file():
        fail(f"missing data file: {relative_path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        fail(f"{relative_path} must contain a JSON array")
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            fail(f"{relative_path}[{index}] must be an object")
    return data


def assert_no_forbidden(relative_path: str, text: str) -> None:
    for pattern in FORBIDDEN:
        if pattern.search(text):
            fail(f"{relative_path} contains forbidden gameplay term: {pattern.pattern}")


def validate_snippets() -> None:
    for relative_path, snippets in EXPECTED_SNIPPETS.items():
        text = read_text(relative_path)
        assert_no_forbidden(relative_path, text)
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")


def validate_schedule_data() -> None:
    schedules = load_json_array("game/data/npc_schedules.json")
    scene_ids: set[str] = set()
    for schedule in schedules:
        for entry in schedule.get("entries", []):
            if not isinstance(entry, dict):
                continue
            scene_ids.add(str(entry.get("scene_id", "")))
    for required_scene in ["player_yard", "forest_edge", "village_shop", "carpenter_yard", "post_route"]:
        if required_scene not in scene_ids:
            fail(f"npc_schedules.json missing real area schedule scene_id={required_scene}")


def validate_rumor_data() -> None:
    rumors = load_json_array("game/data/rumors.json")
    ids = {str(record.get("rumor_id", "")): record for record in rumors}
    if "rumor_npc_forest_edge" not in ids:
        fail("rumors.json missing rumor_npc_forest_edge")
    npc_rumor = ids["rumor_npc_forest_edge"]
    if npc_rumor.get("source") != "npc":
        fail("rumor_npc_forest_edge must use source=npc")
    if "heard_npc_forest_edge" not in npc_rumor.get("sets_flags", []):
        fail("rumor_npc_forest_edge must set heard_npc_forest_edge")
    if npc_rumor.get("conditions", {}).get("flag_set") != "visited_forest_edge":
        fail("rumor_npc_forest_edge must require visited_forest_edge")


def main() -> None:
    validate_snippets()
    validate_schedule_data()
    validate_rumor_data()
    print("OK: persistent main flow file/data contract validated")


if __name__ == "__main__":
    main()
