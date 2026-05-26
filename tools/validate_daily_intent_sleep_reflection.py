from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/scenes/Main.gd": [
        "const DAILY_INTENT_SLEEP_REFLECTIONS",
        "func _build_daily_intent_sleep_reflection(",
        "func _get_previous_day_key(",
        "_copy_scene_state_to_shared(\"TimeManager\", time_manager)",
        "_copy_scene_state_to_shared(\"WeatherManager\", weather_manager)",
        "daily_intent_sleep_reflection",
        "daily_reflection",
        "睡前想起",
        "get_daily_intent(_get_previous_day_key())",
    ],
    "tools/validate_daily_intent_sleep_reflection.gd": [
        "daily intent sleep reflection runtime validation passed",
        "_validate_no_reflection_before_first_week_complete",
        "_validate_post_week_reflection_after_sleep",
        "_validate_crop_feedback_keeps_first_line",
    ],
    "tools/capture_daily_intent_sleep_reflection.gd": [
        "captured daily intent sleep reflection snapshot",
        "check_village_notice",
        "daily_intent_sleep_reflection",
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
    print("OK: daily intent sleep reflection static contract validated")


if __name__ == "__main__":
    main()
