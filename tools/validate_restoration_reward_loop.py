from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS: dict[str, list[str]] = {
    "game/systems/restoration/RestorationTarget.gd": [
        "func _grant_completion_rewards(",
        "reward_items",
        "inventory_manager.add_item",
        "func _format_item_stack(",
    ],
    "game/autoload/DataRegistry.gd": [
        'target.get("reward_items", [])',
        "references missing reward item",
        "reward item count",
    ],
}

EXPECTED_REWARDS: dict[str, dict[str, int]] = {
    "old_well": {
        "seed_turnip": 3,
        "old_bell_fragment": 1,
    },
    "garden_bench": {
        "wildflower_spring": 1,
    },
    "village_sign": {
        "seed_strawberry": 2,
    },
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
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, list):
        fail(f"{relative_path} must contain a JSON array")
    records: list[dict[str, Any]] = []
    for index, record in enumerate(parsed):
        if not isinstance(record, dict):
            fail(f"{relative_path}[{index}] must be an object")
        records.append(record)
    return records


def validate_snippets() -> None:
    for relative_path, snippets in EXPECTED_SNIPPETS.items():
        text = read_text(relative_path)
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")


def validate_reward_data() -> None:
    items = {str(record.get("item_id")) for record in load_json_array("game/data/items.json")}
    targets = {
        str(record.get("restoration_id")): record
        for record in load_json_array("game/data/restoration_targets.json")
    }
    for restoration_id, expected_items in EXPECTED_REWARDS.items():
        if restoration_id not in targets:
            fail(f"restoration_targets.json missing {restoration_id}")
        reward_items = targets[restoration_id].get("reward_items")
        if not isinstance(reward_items, list) or not reward_items:
            fail(f"{restoration_id} should define non-empty reward_items")
        actual: dict[str, int] = {}
        for reward_item in reward_items:
            if not isinstance(reward_item, dict):
                fail(f"{restoration_id} reward item must be an object")
            item_id = str(reward_item.get("item_id", ""))
            count = int(reward_item.get("count", 0))
            if item_id not in items:
                fail(f"{restoration_id} reward references missing item {item_id}")
            if count <= 0:
                fail(f"{restoration_id} reward item count should be positive")
            actual[item_id] = actual.get(item_id, 0) + count
        for item_id, count in expected_items.items():
            if actual.get(item_id) != count:
                fail(f"{restoration_id} should grant {item_id} x{count}")


def main() -> None:
    validate_snippets()
    validate_reward_data()
    print("OK: restoration reward loop static contract validated")


if __name__ == "__main__":
    main()
