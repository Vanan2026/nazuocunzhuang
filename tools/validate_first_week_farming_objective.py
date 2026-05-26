from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS: dict[str, list[str]] = {
    "game/autoload/QuestManager.gd": [
        '"watered_first_crop_day1"',
        '"old_well_restored",\n\t"watered_first_crop_day1"',
        '"watered_first_crop_day1": _get_flag(game_state, "watered_first_crop_day1")',
        '"harvested_first_crop_day1": _get_flag(game_state, "harvested_first_crop_day1")',
        '"给第一块作物浇水"',
        '"收获第一棵作物"',
    ],
    "game/scenes/world/PlayerYard.gd": [
        "func _connect_farm_plot_progress_signals(",
        "func _on_farm_plot_changed(",
        '"watered_first_crop_day1"',
        '"harvested_first_crop_day1"',
        'state_name != "watered"',
        'game_state.is_restored("old_well")',
        'inventory_manager.set_selected_item("")',
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        '"watered_first_crop_day1"',
        '"harvested_first_crop_day1"',
    ],
    "game/scenes/ui/FirstWeekQuestHUD.gd": [
        '"watered_first_crop_day1"',
        '"harvested_first_crop_day1"',
    ],
    "tools/validate_first_week_farming_objective.gd": [
        "first-week farming objective runtime validation passed",
        "_validate_farming_objective_after_well",
        "_validate_watering_advances_objective",
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
    print("OK: first-week farming objective static contract validated")


if __name__ == "__main__":
    main()
