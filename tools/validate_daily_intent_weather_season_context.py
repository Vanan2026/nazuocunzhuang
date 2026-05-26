from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/systems/daily/DailyIntentContext.gd": [
        "class_name DailyIntentContext",
        "const WEATHER_INTENT_LINES",
        "const SEASON_INTENT_LINES",
        "func build_planner_feedback(",
        "func build_journal_summary(",
        "func build_chip_hint(",
        "func build_sleep_reflection(",
        "get_today_weather",
        "get_date_info",
        "夏天",
        "今天有雨",
    ],
    "game/scenes/ui/DailyIntentPanel.gd": [
        "weather_manager_path",
        "DailyIntentContext.build_planner_feedback",
        "func _get_weather_manager(",
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        "weather_manager_path",
        "func bind_weather_manager(",
        "DailyIntentContext.build_chip_hint",
        "func _on_weather_context_changed(",
    ],
    "game/scenes/Main.gd": [
        "current_objective_chip.bind_weather_manager(weather_manager)",
        "DailyIntentContext.build_sleep_reflection",
    ],
    "tools/validate_daily_intent_weather_season_context.gd": [
        "daily intent weather/season context runtime validation passed",
        "_validate_weather_and_season_context",
        "set_today_weather(\"rainy\")",
        "season_index",
    ],
}

FORBIDDEN_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bcombat\b",
        r"\bmonster\b",
        r"\bdamage\b",
        r"\bweapon\b",
        r"\bkill\b",
        r"\bloot\b",
        r"add_item\(",
        r"set_player_money",
        r"set_player_energy",
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
        if relative_path.startswith("game/"):
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(text):
                    fail(f"{relative_path} contains forbidden state/action token: {pattern.pattern}")
    print("OK: daily intent weather/season context static contract validated")


if __name__ == "__main__":
    main()
