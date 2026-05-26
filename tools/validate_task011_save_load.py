from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/autoload/SaveManager.gd": [
        'const DEFAULT_SAVE_PATH: String = "user://save_slot_01.json"',
        "func save_game(",
        "func load_game(",
        "func build_runtime_save_data(",
        "func apply_runtime_save_data(",
        "func build_save_data(",
        "func apply_save_data(",
        "FileAccess.open",
        "JSON.stringify",
        "JSON.parse_string",
    ],
    "game/autoload/TimeManager.gd": [
        "func get_save_data(",
        "func apply_save_data(",
    ],
    "game/autoload/WeatherManager.gd": [
        "func get_save_data(",
        "func apply_save_data(",
    ],
    "game/autoload/InventoryManager.gd": [
        "func get_save_data(",
        "func apply_save_data(",
    ],
    "game/autoload/RelationshipManager.gd": [
        "func get_save_data(",
        "func apply_save_data(",
    ],
    "game/autoload/GameState.gd": [
        "func get_save_data(",
        "func apply_save_data(",
    ],
    "game/systems/farming/FarmPlot.gd": [
        "func get_save_data(",
        "func apply_save_data(",
    ],
    "game/scenes/world/PlayerYard.gd": [
        "func save_game(",
        "func load_game(",
        "func _unhandled_input(",
        'Input.is_action_just_pressed("debug_save")',
        'Input.is_action_just_pressed("debug_load")',
    ],
    "project.godot": [
        "debug_save={",
        "debug_load={",
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
    for relative_path, snippets in EXPECTED_FILES.items():
        path = ROOT / relative_path
        if not path.is_file():
            fail(f"missing file: {relative_path}")
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")
        if relative_path.endswith(".gd"):
            for pattern in FORBIDDEN:
                if pattern.search(text):
                    fail(f"{relative_path} contains forbidden gameplay term: {pattern.pattern}")

    print("OK: Task 011 save/load file contract validated")


if __name__ == "__main__":
    main()
