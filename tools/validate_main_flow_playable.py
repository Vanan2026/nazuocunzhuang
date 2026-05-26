from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_MAIN_SCENE = 'run/main_scene="res://game/scenes/Main.tscn"'

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
    "project.godot": [
        EXPECTED_MAIN_SCENE,
    ],
    "game/autoload/DataRegistry.gd": [
        '"npc_schedules": {"path": "res://game/data/npc_schedules.json", "id_key": "schedule_id"}',
        "var npc_schedules: Dictionary",
        "func get_npc_schedule(",
        "func _validate_npc_schedules(",
    ],
    "game/entities/interactable/RumorBoard.gd": [
        "class_name RumorBoard",
        "extends \"res://game/entities/interactable/Interactable.gd\"",
        "build_rumor_dialogue",
        "mark_dialogue_rumors_seen",
    ],
    "game/entities/interactable/SceneTravel.gd": [
        "class_name SceneTravel",
        "extends \"res://game/entities/interactable/Interactable.gd\"",
        "target_scene",
        "change_scene_to_file",
    ],
    "game/systems/npc/NpcScheduleDirector.gd": [
        "class_name NpcScheduleDirector",
        "func apply_schedule(",
        "func get_current_assignment(",
        "get_npc_schedule",
    ],
    "game/scenes/Main.tscn": [
        "res://game/scenes/home/PlayerHouse.tscn",
        '[node name="PlayerHouse"',
    ],
    "game/scenes/home/PlayerHouse.tscn": [
        "res://game/entities/interactable/SceneTravel.gd",
        'target_scene = "res://game/scenes/world/PlayerYard.tscn"',
    ],
    "game/scenes/world/PlayerYard.tscn": [
        "res://game/entities/interactable/RumorBoard.gd",
        "res://game/entities/interactable/SceneTravel.gd",
        "res://game/systems/npc/NpcScheduleDirector.gd",
        '[node name="BulletinBoard" type="Area2D" parent="."',
        '[node name="ScheduleDirector" type="Node" parent="."',
        '[node name="GardenBenchRepair" type="Area2D" parent="."',
        '[node name="VillageSignRepair" type="Area2D" parent="."',
        '[node name="ForestTrailGate" type="Area2D" parent="."',
        'target_scene = "res://game/scenes/world/ForestEdge.tscn"',
    ],
    "game/scenes/world/ForestEdge.tscn": [
        '[node name="ForestEdge" type="Node2D"',
        '[node name="BackToYard" type="Area2D" parent="."',
        '[node name="FallenBranchBundle" type="Area2D" parent="."',
        '[node name="QuietShrine" type="Area2D" parent="."',
        'target_scene = "res://game/scenes/world/PlayerYard.tscn"',
        'flag_id = "visited_forest_edge"',
        'item_id = "wood"',
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


def validate_npc_schedules() -> None:
    schedules = load_json_array("game/data/npc_schedules.json")
    if len(schedules) < 3:
        fail("npc_schedules.json should contain at least 3 schedules")
    required_blocks = {"morning", "late_morning", "afternoon", "evening"}
    schedule_ids = {record.get("schedule_id") for record in schedules}
    npcs = load_json_array("game/data/npcs.json")
    for npc in npcs:
        schedule_id = npc.get("schedule_id")
        if schedule_id not in schedule_ids:
            fail(f"npc {npc.get('npc_id')} references missing schedule {schedule_id}")
    for schedule in schedules:
        for field in ["schedule_id", "entries"]:
            if field not in schedule:
                fail(f"schedule missing required field {field}: {schedule}")
        entries = schedule["entries"]
        if not isinstance(entries, list) or not entries:
            fail(f"schedule {schedule['schedule_id']} entries must be a non-empty array")
        blocks = set()
        for entry in entries:
            if not isinstance(entry, dict):
                fail(f"schedule {schedule['schedule_id']} entry must be an object")
            for field in ["time_block", "scene_id", "position", "activity"]:
                if field not in entry:
                    fail(f"schedule {schedule['schedule_id']} entry missing {field}")
            blocks.add(str(entry["time_block"]))
            position = entry["position"]
            if not isinstance(position, list) or len(position) != 2:
                fail(f"schedule {schedule['schedule_id']} position must be [x, y]")
        if not required_blocks.issubset(blocks):
            fail(f"schedule {schedule['schedule_id']} should cover {sorted(required_blocks)}")


def validate_restoration_targets() -> None:
    targets = load_json_array("game/data/restoration_targets.json")
    target_ids = {str(record.get("restoration_id")) for record in targets}
    for required_id in ["old_well", "garden_bench", "village_sign"]:
        if required_id not in target_ids:
            fail(f"restoration_targets.json missing {required_id}")
    if len(targets) < 3:
        fail("restoration_targets.json should contain at least 3 main-flow repair goals")


def validate_rumor_sources() -> None:
    rumors = load_json_array("game/data/rumors.json")
    sources = {str(record.get("source")) for record in rumors}
    for source in ["mailbox", "bulletin", "npc"]:
        if source not in sources:
            fail(f"rumors.json missing source {source}")


def main() -> None:
    validate_snippets()
    validate_npc_schedules()
    validate_restoration_targets()
    validate_rumor_sources()
    print("OK: main flow playable file/data contract validated")


if __name__ == "__main__":
    main()
