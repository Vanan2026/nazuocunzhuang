from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/scenes/world/PlayerYard.gd": [
        '@export var aoi_turnip_reward_item_id: String = "seed_strawberry"',
        "@export var aoi_turnip_reward_count: int = 1",
        "func _grant_aoi_turnip_thanks_reward() -> void:",
        "inventory_manager.add_item(aoi_turnip_reward_item_id, aoi_turnip_reward_count)",
        "func _show_aoi_turnip_thanks_feedback() -> void:",
        '"aoi_turnip_thanks_reward"',
        '"shared_first_turnip_day1"',
    ],
    "tools/validate_aoi_turnip_thanks_reward.gd": [
        "aoi turnip thanks reward runtime validation passed",
        "seed_strawberry",
        "shared_first_turnip_day1",
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


def main() -> None:
    for relative_path, snippets in EXPECTED_SNIPPETS.items():
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

    items = json.loads((ROOT / "game/data/items.json").read_text(encoding="utf-8"))
    item_by_id = {record.get("item_id"): record for record in items}
    seed = item_by_id.get("seed_strawberry", {})
    if seed.get("category") != "seed":
        fail("seed_strawberry should remain a seed item for Aoi's first-harvest thanks")
    if "spring" not in [str(tag).lower() for tag in seed.get("tags", [])]:
        fail("seed_strawberry should remain spring-tagged")

    print("OK: Aoi turnip thanks reward static contract validated")


if __name__ == "__main__":
    main()
