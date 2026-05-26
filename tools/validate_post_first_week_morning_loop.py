from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        "const DAILY_INTENT_LABELS",
        "const DAILY_INTENT_HINTS",
        "const DAILY_LOOP_NO_INTENT_TEXT",
        "func bind_game_state(",
        "func bind_time_manager(",
        "func _should_show_daily_loop(",
        "func _get_selected_daily_intent_id(",
        "今日方向",
        "整理今日方向",
        "晨间小桌",
        "日常",
    ],
    "game/scenes/ui/CurrentObjectiveChip.tscn": [
        "game_state_path = NodePath(\"../GameState\")",
        "time_manager_path = NodePath(\"../TimeManager\")",
    ],
    "game/scenes/Main.gd": [
        "current_objective_chip.bind_game_state(game_state)",
        "current_objective_chip.bind_time_manager(time_manager)",
    ],
    "tools/validate_post_first_week_morning_loop.gd": [
        "post-first-week morning loop runtime validation passed",
        "_validate_first_week_still_owns_chip_before_completion",
        "_validate_completed_week_prompts_daily_direction",
        "_validate_selected_intent_drives_chip",
        "_validate_next_day_resets_daily_direction_prompt",
    ],
    "tools/capture_post_first_week_morning_loop.gd": [
        "captured post-first-week morning loop snapshot",
        "check_village_notice",
        "今日方向",
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
    print("OK: post-first-week morning loop static contract validated")


if __name__ == "__main__":
    main()
