from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/systems/daily/WeeklyRhythmContext.gd": [
        "class_name WeeklyRhythmContext",
        "const WEEKLY_RHYTHMS",
        "func get_rhythm_for_day(",
        "func build_planner_status(",
        "func build_journal_note(",
        "func build_chip_hint(",
        "total_day",
        "节奏",
        "提示",
    ],
    "game/scenes/ui/DailyIntentPanel.gd": [
        "const WeeklyRhythmContext",
        "func get_weekly_rhythm_status_text(",
        "WeeklyRhythmContext.build_planner_status",
    ],
    "game/scenes/Main.tscn": [
        '[node name="CurrentObjectiveChip" parent="." instance=',
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        "const WeeklyRhythmContext",
        "WeeklyRhythmContext.build_chip_hint",
        "晨间小桌",
    ],
    "tools/validate_daily_intent_weekly_rhythm.gd": [
        "daily intent weekly rhythm runtime validation passed",
        "_validate_weekly_rhythm_context",
        "_validate_no_pressure_state_changes",
    ],
    "tools/capture_daily_intent_weekly_rhythm.gd": [
        "captured daily intent weekly rhythm snapshot",
        "get_weekly_rhythm_status_text",
        "get_current_hint_text",
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
        r"\breward\b",
        r"\bpenalty\b",
        r"\bdeadline\b",
        r"\bscore\b",
        r"\bbonus\b",
        r"add_item\(",
        r"remove_item\(",
        r"set_player_money",
        r"set_player_energy",
        r"complete_objective",
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
                    fail(f"{relative_path} contains forbidden pressure/state token: {pattern.pattern}")
    print("OK: daily intent weekly rhythm static contract validated")


if __name__ == "__main__":
    main()
