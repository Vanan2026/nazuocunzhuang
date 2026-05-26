from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/autoload/GameState.gd": [
        "var daily_intents: Dictionary",
        "func set_daily_intent(",
        "func get_daily_intent(",
        "func get_daily_intents(",
        '"daily_intents": daily_intents.duplicate(true)',
        'if data.has("daily_intents"):',
    ],
    "game/entities/interactable/DailyIntentPlanner.gd": [
        "class_name DailyIntentPlanner",
        'extends "res://game/entities/interactable/Interactable.gd"',
        "daily_intent_panel_path",
        "show_planner",
    ],
    "game/scenes/ui/DailyIntentPanel.gd": [
        "class_name DailyIntentPanel",
        "const INTENT_OPTIONS",
        '"tend_crops"',
        '"check_village_notice"',
        '"visit_neighbor"',
        '"gather_repair_material"',
        "func select_intent(",
        "func get_available_intent_ids(",
        "func get_intent_feedback_text(",
        "_show_intent_feedback",
        "daily_intent_%s_feedback",
        "set_daily_intent",
    ],
    "game/scenes/ui/DailyIntentPanel.tscn": [
        '[node name="DailyIntentPanel" type="CanvasLayer"]',
        "visible = false",
        '[node name="ChoiceButtons" type="VBoxContainer" parent="Panel/Content"]',
        '[node name="CloseButton" type="Button" parent="Panel/Content"]',
    ],
    "game/scenes/home/PlayerHouse.tscn": [
        "res://game/entities/interactable/DailyIntentPlanner.gd",
        "res://game/scenes/ui/DailyIntentPanel.tscn",
        '[node name="IntentDesk" type="Area2D" parent="." groups=["interactable"]]',
        'interactable_id = "daily_intent_planner"',
        'interaction_hint = "按 E 整理今天想做的事"',
        '[node name="DailyIntentPanel" parent="." instance=',
    ],
    "tools/validate_daily_intent_planner.gd": [
        "daily intent planner runtime validation passed",
        "_validate_house_planner",
        "_validate_daily_intent_persistence",
    ],
    "tools/capture_daily_intent_planner.gd": [
        "captured daily intent planner snapshot",
        "IntentDesk",
        "DailyIntentPanel",
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

    print("OK: daily intent planner static contract validated")


if __name__ == "__main__":
    main()
