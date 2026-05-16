from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
AUTOLOAD_DIR = ROOT / "game" / "autoload"

EXPECTED = {
    "GameState.gd": ["var flags: Dictionary", "func set_flag(", "func get_flag(", "func is_restored("],
    "EventBus.gd": ["signal day_started", "signal inventory_changed", "signal restoration_completed"],
    "TimeManager.gd": ["signal time_changed", "func get_date_info(", "func advance_minutes("],
    "SeasonManager.gd": ["const SEASONS", "func get_current_season(", "func get_next_season("],
    "WeatherManager.gd": ["signal weather_changed", "func get_today_weather(", "func generate_tomorrow_weather("],
    "DataRegistry.gd": ["func get_item(", "func get_crop(", "func get_npc(", "func get_restoration("],
    "InventoryManager.gd": ["signal inventory_changed", "func add_item(", "func remove_item(", "func has_item(", "func get_count("],
    "RelationshipManager.gd": ["signal relationship_changed", "func get_relationship(", "func add_relationship("],
    "QuestManager.gd": ["signal quest_updated", "func get_quest_state(", "func set_quest_state("],
    "DialogueManager.gd": ["signal dialogue_started", "func get_dialogue(", "func start_dialogue("],
    "SaveManager.gd": ["const SAVE_VERSION", "const DEFAULT_SAVE_PATH", "func build_save_data(", "func apply_save_data("],
    "SceneRouter.gd": ["signal scene_change_requested", "func request_scene_change(", "func get_current_scene_id("],
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
    missing = [name for name in EXPECTED if not (AUTOLOAD_DIR / name).is_file()]
    if missing:
        fail("missing autoload scripts: " + ", ".join(missing))

    for name, snippets in EXPECTED.items():
        path = AUTOLOAD_DIR / name
        text = path.read_text(encoding="utf-8")
        if "extends Node" not in text:
            fail(f"{name} must extend Node")
        for snippet in snippets:
            if snippet not in text:
                fail(f"{name} missing required snippet: {snippet}")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                fail(f"{name} contains forbidden gameplay term: {pattern.pattern}")

    print(f"OK: validated {len(EXPECTED)} Task 002 autoload skeletons")


if __name__ == "__main__":
    main()
