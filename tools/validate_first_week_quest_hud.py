from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/scenes/ui/FirstWeekQuestHUD.gd": [
        "class_name FirstWeekQuestHUD",
        "const OBJECTIVE_LABELS",
        "func bind_quest_manager(",
        "func refresh(",
        "func get_visible_objective_texts(",
        "读邮箱",
        "看公告板",
        "修旧井",
        "修长椅",
        "扶正路牌",
        "去森林边缘",
        "听 Mika 的传闻",
    ],
    "game/scenes/ui/FirstWeekQuestHUD.tscn": [
        'path="res://game/scenes/ui/FirstWeekQuestHUD.gd"',
        '[node name="FirstWeekQuestHUD" type="CanvasLayer"]',
        '[node name="ObjectiveList" type="VBoxContainer" parent="Panel/Content"]',
    ],
    "game/scenes/Main.tscn": [
        'path="res://game/scenes/ui/FirstWeekQuestHUD.tscn"',
        '[node name="FirstWeekQuestHUD" parent="." instance=',
    ],
    "game/scenes/Main.gd": [
        "first_week_quest_hud",
        "bind_quest_manager",
        "FirstWeekQuestHUD",
    ],
    "game/autoload/QuestManager.gd": [
        "const FIRST_WEEK_QUEST_ID",
        "const FIRST_WEEK_OBJECTIVES",
        "func update_first_week_progress(",
        "func get_first_week_progress(",
        "signal quest_updated",
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
        for pattern in FORBIDDEN:
            if pattern.search(text):
                fail(f"{relative_path} contains forbidden gameplay term: {pattern.pattern}")

    print("OK: first-week quest HUD static contract validated")


if __name__ == "__main__":
    main()
