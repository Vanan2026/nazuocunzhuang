from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "game" / "data"
DATA_REGISTRY = ROOT / "game" / "autoload" / "DataRegistry.gd"

FORBIDDEN_FIELD_NAMES = {
    "combat",
    "monster",
    "damage",
    "weapon",
    "hp",
    "kill",
    "loot",
}
FORBIDDEN_KEY_PATTERN = re.compile(r"(combat|monster|damage|weapon|hp|kill|loot)", re.IGNORECASE)
VALID_SEASONS = {"spring", "summer", "autumn", "winter"}
VALID_ITEM_CATEGORIES = {"seed", "crop", "forage", "fish", "food", "material", "tool", "key", "furniture"}

DATA_SPECS: dict[str, dict[str, Any]] = {
    "items.json": {
        "id_key": "item_id",
        "minimum": 20,
        "required": ["item_id", "name", "category", "description", "stackable", "max_stack", "sell_price", "tags", "icon"],
    },
    "crops.json": {
        "id_key": "crop_id",
        "minimum": 8,
        "required": [
            "crop_id",
            "seed_item_id",
            "harvest_item_id",
            "name",
            "allowed_seasons",
            "grow_days",
            "regrow_days",
            "water_required",
            "stages",
            "stage_sprites",
        ],
    },
    "npcs.json": {
        "id_key": "npc_id",
        "minimum": 3,
        "required": [
            "npc_id",
            "name",
            "role",
            "birthday",
            "home_scene",
            "default_scene",
            "portrait",
            "likes",
            "dislikes",
            "schedule_id",
            "heart_events",
        ],
    },
    "dialogues.json": {
        "id_key": "dialogue_id",
        "minimum": 4,
        "required": ["dialogue_id", "npc_id", "type", "priority", "conditions", "lines", "sets_flags"],
    },
    "recipes.json": {
        "id_key": "recipe_id",
        "minimum": 5,
        "required": ["recipe_id", "name", "ingredients", "result", "energy_restore", "tags", "unlock_condition"],
    },
    "npc_schedules.json": {
        "id_key": "schedule_id",
        "minimum": 3,
        "required": ["schedule_id", "entries"],
    },
    "restoration_targets.json": {
        "id_key": "restoration_id",
        "minimum": 1,
        "required": [
            "restoration_id",
            "name",
            "description",
            "required_items",
            "required_money",
            "required_flags",
            "unlocks",
            "visual_states",
        ],
    },
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def load_json_array(name: str) -> list[dict[str, Any]]:
    path = DATA_DIR / name
    if not path.is_file():
        fail(f"missing data file: {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{name} is not valid JSON: {exc}")
    if not isinstance(data, list):
        fail(f"{name} must contain a JSON array")
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            fail(f"{name}[{index}] must be an object")
    return data


def assert_no_forbidden_keys(value: Any, location: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text.lower() in FORBIDDEN_FIELD_NAMES or FORBIDDEN_KEY_PATTERN.search(key_text):
                fail(f"{location} contains forbidden field: {key_text}")
            assert_no_forbidden_keys(child, f"{location}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_forbidden_keys(child, f"{location}[{index}]")


def validate_common(name: str, records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    spec = DATA_SPECS[name]
    if len(records) < spec["minimum"]:
        fail(f"{name} must contain at least {spec['minimum']} records")

    id_key = spec["id_key"]
    seen: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        for field in spec["required"]:
            if field not in record:
                fail(f"{name}[{index}] missing required field: {field}")
        record_id = record[id_key]
        if not isinstance(record_id, str) or not record_id.strip():
            fail(f"{name}[{index}] has empty {id_key}")
        if record_id in seen:
            fail(f"{name} has duplicate {id_key}: {record_id}")
        seen[record_id] = record
        if "name" in record and (not isinstance(record.get("name"), str) or not record["name"].strip()):
            fail(f"{name}[{index}] has empty display name")
        assert_no_forbidden_keys(record, f"{name}[{index}]")
    return seen


def validate_items(items: dict[str, dict[str, Any]]) -> None:
    for item_id, item in items.items():
        if item["category"] not in VALID_ITEM_CATEGORIES:
            fail(f"item {item_id} has invalid category: {item['category']}")
        if not isinstance(item["tags"], list):
            fail(f"item {item_id} tags must be an array")
        if not str(item["icon"]).startswith("res://assets/art/items/"):
            fail(f"item {item_id} has invalid icon path: {item['icon']}")


def validate_crops(crops: dict[str, dict[str, Any]], items: dict[str, dict[str, Any]]) -> None:
    for crop_id, crop in crops.items():
        for field in ["seed_item_id", "harvest_item_id"]:
            if crop[field] not in items:
                fail(f"crop {crop_id} references missing item {crop[field]}")
        if not set(crop["allowed_seasons"]).issubset(VALID_SEASONS):
            fail(f"crop {crop_id} has invalid season list: {crop['allowed_seasons']}")
        if int(crop["grow_days"]) <= 0:
            fail(f"crop {crop_id} grow_days must be positive")
        if int(crop["stages"]) != len(crop["stage_sprites"]):
            fail(f"crop {crop_id} stages must match stage_sprites length")


def validate_npcs(npcs: dict[str, dict[str, Any]]) -> None:
    for npc_id, npc in npcs.items():
        birthday = npc["birthday"]
        if not isinstance(birthday, dict):
            fail(f"npc {npc_id} birthday must be an object")
        if birthday.get("season") not in VALID_SEASONS:
            fail(f"npc {npc_id} has invalid birthday season")
        day = int(birthday.get("day", 0))
        if day < 1 or day > 28:
            fail(f"npc {npc_id} birthday day must be 1-28")


def validate_npc_schedules(
    schedules: dict[str, dict[str, Any]],
    npcs: dict[str, dict[str, Any]],
) -> None:
    for npc_id, npc in npcs.items():
        schedule_id = npc["schedule_id"]
        if schedule_id not in schedules:
            fail(f"npc {npc_id} references missing schedule {schedule_id}")
    for schedule_id, schedule in schedules.items():
        entries = schedule["entries"]
        if not isinstance(entries, list) or not entries:
            fail(f"schedule {schedule_id} entries must be a non-empty array")
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                fail(f"schedule {schedule_id} entries[{index}] must be an object")
            for field in ["time_block", "scene_id", "position", "activity"]:
                if field not in entry:
                    fail(f"schedule {schedule_id} entries[{index}] missing {field}")
            position = entry["position"]
            if not isinstance(position, list) or len(position) != 2:
                fail(f"schedule {schedule_id} entries[{index}] position must be [x, y]")


def validate_dialogues(dialogues: dict[str, dict[str, Any]], npcs: dict[str, dict[str, Any]]) -> None:
    for dialogue_id, dialogue in dialogues.items():
        if dialogue["npc_id"] not in npcs:
            fail(f"dialogue {dialogue_id} references missing npc {dialogue['npc_id']}")
        if not dialogue["lines"]:
            fail(f"dialogue {dialogue_id} must contain lines")


def validate_recipes(recipes: dict[str, dict[str, Any]], items: dict[str, dict[str, Any]]) -> None:
    for recipe_id, recipe in recipes.items():
        for ingredient in recipe["ingredients"]:
            if ingredient["item_id"] not in items:
                fail(f"recipe {recipe_id} references missing ingredient {ingredient['item_id']}")
        result_item_id = recipe["result"]["item_id"]
        if result_item_id not in items:
            fail(f"recipe {recipe_id} references missing result item {result_item_id}")


def validate_restoration_targets(targets: dict[str, dict[str, Any]], items: dict[str, dict[str, Any]]) -> None:
    for restoration_id, target in targets.items():
        for required_item in target["required_items"]:
            if required_item["item_id"] not in items:
                fail(f"restoration {restoration_id} references missing item {required_item['item_id']}")
        visual_states = target["visual_states"]
        for state_name in ["broken", "repaired"]:
            if state_name not in visual_states:
                fail(f"restoration {restoration_id} missing visual state: {state_name}")


def validate_registry_script() -> None:
    if not DATA_REGISTRY.is_file():
        fail("missing DataRegistry.gd")
    text = DATA_REGISTRY.read_text(encoding="utf-8")
    for snippet in [
        "const DATA_FILES",
        "func _ready(",
        "func load_all_data(",
        "func validate_all_data(",
        "func get_npc_schedule(",
        "print(",
        "data_loaded.emit()",
        "data_validation_failed.emit(",
    ]:
        if snippet not in text:
            fail(f"DataRegistry.gd missing required snippet: {snippet}")


def main() -> None:
    loaded = {name: load_json_array(name) for name in DATA_SPECS}
    indexed = {name: validate_common(name, records) for name, records in loaded.items()}
    validate_items(indexed["items.json"])
    validate_crops(indexed["crops.json"], indexed["items.json"])
    validate_npcs(indexed["npcs.json"])
    validate_npc_schedules(indexed["npc_schedules.json"], indexed["npcs.json"])
    validate_dialogues(indexed["dialogues.json"], indexed["npcs.json"])
    validate_recipes(indexed["recipes.json"], indexed["items.json"])
    validate_restoration_targets(indexed["restoration_targets.json"], indexed["items.json"])
    validate_registry_script()
    print("OK: validated Task 003 data files and DataRegistry contract")


if __name__ == "__main__":
    main()
