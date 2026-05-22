from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES: dict[str, list[str]] = {
    "game/entities/npc/NPC.gd": [
        "extends \"res://game/entities/interactable/Interactable.gd\"",
        "@export var inventory_manager_path: NodePath",
        "func _try_gift_interaction(",
        "func _evaluate_gift(",
        "func _build_gift_dialogue(",
        "func _get_linked_node(path: NodePath, fallback_name: String) -> Node:",
        "birthday_gift_multiplier",
    ],
    "game/autoload/InventoryManager.gd": [
        "class_name InventoryManager",
        "var selected_item_id: String = \"\"",
        "func set_selected_item(item_id: String) -> bool:",
        "func remove_item(item_id: String, count: int = 1) -> bool:",
        "func get_selected_item_id() -> String",
    ],
    "game/autoload/RelationshipManager.gd": [
        "class_name RelationshipManager",
        "var gifted_today: Dictionary = {}",
        "func has_gifted_today(npc_id: String) -> bool:",
        "func mark_gifted_today(npc_id: String) -> void:",
        "func reset_daily_social_state() -> void:",
    ],
    "game/scenes/ui/InventoryUI.gd": [
        "class_name InventoryUI",
        "func select_item(item_id: String) -> bool:",
        "func _on_clear_selection() -> void:",
        "func _on_item_button_pressed(item_id: String) -> void:",
    ],
    "game/scenes/world/PlayerYard.tscn": [
        '[node name="InventoryManager" type="Node"',
        '[node name="RelationshipManager" type="Node"',
        '[node name="DialogueBox"',
        '[node name="Aoi" parent="NPCs"',
        '[node name="Gen" parent="NPCs"',
        '[node name="Mika" parent="NPCs"',
        ],
}

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


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def assert_file_contains(path: Path, snippets: list[str]) -> None:
    if not path.is_file():
        fail(f"missing file: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    for snippet in snippets:
        if snippet not in text:
            fail(f"{path.relative_to(ROOT)} missing required snippet: {snippet}")
    for pattern in FORBIDDEN:
        if pattern.search(text):
            fail(f"{path.relative_to(ROOT)} contains forbidden gameplay term: {pattern.pattern}")


def load_json_array(relative_path: str):
    path = ROOT / relative_path
    if not path.is_file():
        fail(f"missing JSON file: {relative_path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        fail(f"{relative_path} must contain a JSON array")
    return data


def main() -> None:
    for relative_path, snippets in EXPECTED_FILES.items():
        assert_file_contains(ROOT / relative_path, snippets)

    npcs = {record["npc_id"]: record for record in load_json_array("game/data/npcs.json")}
    items = {record["item_id"]: record for record in load_json_array("game/data/items.json")}

    for npc_id in ["aoi", "gen", "mika"]:
        if npc_id not in npcs:
            fail(f"game/data/npcs.json missing required NPC: {npc_id}")
        npc = npcs[npc_id]
        if not npc.get("likes"):
            fail(f"npc {npc_id} should define likes tags for gift evaluation")
        if not npc.get("dislikes"):
            fail(f"npc {npc_id} should define dislikes tags for gift evaluation")

    gift_item_ids = ["food_persimmon_riceball", "food_warm_tea"]
    for item_id in gift_item_ids:
        if item_id not in items:
            fail(f"game/data/items.json missing gift test item: {item_id}")

    aoi_birthday = npcs["aoi"].get("birthday", {})
    if aoi_birthday.get("season", "") != "spring" or int(aoi_birthday.get("day", 0)) != 12:
        fail("Task 009 gift flow currently assumes Aoi birthday at spring day 12")

    # Validate validator-specific expected tags can actually produce non-zero effect:
    aoi_likes = [str(tag).lower() for tag in npcs["aoi"].get("likes", [])]
    persimmon_tags = [str(tag).lower() for tag in items["food_persimmon_riceball"].get("tags", [])]
    if not set(aoi_likes) & set(persimmon_tags):
        fail("Aoi likes list should overlap food_persimmon_riceball tags to exercise positive gift response")

    print("OK: validated Task 009 gift + relationship response contract")


if __name__ == "__main__":
    main()
