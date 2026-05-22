from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUMORS_JSON = ROOT / "game/data/rumors.json"

EXPECTED_FILES = {
    "game/data/rumors.json": [
        "rumor_old_well_bell",
        "heard_bell_rumor_01",
        "rumor_old_well_bell",
    ],
    "game/autoload/DataRegistry.gd": [
        '"rumors": {"path": "res://game/data/rumors.json", "id_key": "rumor_id"}',
        "var rumors: Dictionary",
        "func get_rumor(",
        "func _validate_rumors(",
    ],
    "game/autoload/RumorManager.gd": [
        "class_name RumorManager",
        "func bind_registry(",
        "func bind_game_state(",
        "func bind_time_manager(",
        "func bind_weather_manager(",
        "func get_daily_rumors(",
        "func build_rumor_dialogue(",
        "func mark_rumors_seen(",
        "flag_set",
        "flag_not_set",
    ],
    "game/scenes/world/PlayerYard.gd": [
        "@onready var rumor_manager",
        "@onready var mailbox",
        "func show_mailbox_rumors(",
        "rumor_manager.bind_registry(data_registry)",
        "mailbox.interacted.connect(_on_mailbox_interacted)",
    ],
    "game/scenes/world/PlayerYard.tscn": [
        "res://game/autoload/RumorManager.gd",
        '[node name="RumorManager" type="Node" parent="."',
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


def load_rumors() -> list[dict[str, Any]]:
    if not RUMORS_JSON.is_file():
        fail("missing game/data/rumors.json")
    data = json.loads(RUMORS_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        fail("rumors.json must contain a JSON array")
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            fail(f"rumors.json[{index}] must be an object")
    return data


def main() -> None:
    for relative_path, snippets in EXPECTED_FILES.items():
        path = ROOT / relative_path
        if not path.is_file():
            fail(f"missing file: {relative_path}")
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                fail(f"{relative_path} contains forbidden gameplay term: {pattern.pattern}")

    rumors = load_rumors()
    if len(rumors) < 5:
        fail("rumors.json should contain at least 5 MVP rumors")
    seen_ids: set[str] = set()
    bell_rumor = None
    for rumor in rumors:
        for field in ["rumor_id", "source", "priority", "conditions", "text", "sets_flags"]:
            if field not in rumor:
                fail(f"rumor missing required field {field}: {rumor}")
        rumor_id = str(rumor["rumor_id"])
        if not rumor_id:
            fail("rumor_id must not be empty")
        if rumor_id in seen_ids:
            fail(f"duplicate rumor_id: {rumor_id}")
        seen_ids.add(rumor_id)
        if str(rumor["source"]) not in {"mailbox", "bulletin", "npc"}:
            fail(f"invalid rumor source for {rumor_id}: {rumor['source']}")
        if not str(rumor["text"]).strip():
            fail(f"rumor {rumor_id} text must not be empty")
        if not isinstance(rumor["conditions"], dict):
            fail(f"rumor {rumor_id} conditions must be an object")
        if not isinstance(rumor["sets_flags"], list):
            fail(f"rumor {rumor_id} sets_flags must be an array")
        if rumor_id == "rumor_old_well_bell":
            bell_rumor = rumor

    if bell_rumor is None:
        fail("rumors.json missing rumor_old_well_bell")
    conditions = bell_rumor["conditions"]
    if conditions.get("flag_set") != "rumor_old_well_bell":
        fail("bell rumor must require flag_set=rumor_old_well_bell")
    if "heard_bell_rumor_01" not in bell_rumor["sets_flags"]:
        fail("bell rumor must set heard_bell_rumor_01 after being shown")

    print("OK: Task 012 rumor file/data contract validated")


if __name__ == "__main__":
    main()
