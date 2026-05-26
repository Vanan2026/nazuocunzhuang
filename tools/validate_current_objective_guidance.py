from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/autoload/QuestManager.gd": [
        "const FIRST_WEEK_OBJECTIVE_LABELS",
        "const FIRST_WEEK_OBJECTIVE_HINTS",
        "func get_current_first_week_objective_id(",
        "func get_current_first_week_objective_label(",
        "func get_current_first_week_objective_hint(",
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        "class_name CurrentObjectiveChip",
        "const FALLBACK_HINTS",
        "func bind_quest_manager(",
        "func refresh(",
        "func get_current_goal_text(",
        "func get_current_hint_text(",
        "func get_progress_text(",
        "hint_label",
        "quest_updated",
        "当前目标",
        "读邮箱",
        "看公告板",
    ],
    "game/scenes/ui/CurrentObjectiveChip.tscn": [
        'path="res://game/scenes/ui/CurrentObjectiveChip.gd"',
        '[node name="CurrentObjectiveChip" type="CanvasLayer"]',
        "visible = true",
        '[node name="Panel" type="PanelContainer" parent="."]',
        "offset_left = 900.0",
        "offset_top = 16.0",
        "offset_right = 1264.0",
        "offset_bottom = 124.0",
        '[node name="ObjectiveLabel" type="Label" parent="Panel/Content"]',
        '[node name="HintLabel" type="Label" parent="Panel/Content"]',
    ],
    "game/scenes/Main.tscn": [
        'path="res://game/scenes/ui/CurrentObjectiveChip.tscn"',
        '[node name="CurrentObjectiveChip" parent="." instance=',
    ],
    "game/scenes/Main.gd": [
        "CURRENT_OBJECTIVE_CHIP_SCENE_NAME",
        "current_objective_chip",
        "bind_quest_manager",
        "_on_scene_game_state_flag_changed",
    ],
    "game/scenes/home/PlayerHouse.tscn": [
        '[node name="HomeStartGuidance" type="Node2D" parent="."]',
        '[node name="DoorGuidePath" type="Polygon2D" parent="HomeStartGuidance"]',
        '[node name="DoorFocusMarker" type="Polygon2D" parent="HomeStartGuidance"]',
        'interactable_id = "door_to_yard"',
        'display_name = "院门"',
    ],
    "game/scenes/world/PlayerYard.tscn": [
        '[node name="FirstStepGuidance" type="Node2D" parent="YardStructure"]',
        '[node name="SpawnMailboxPath" type="Polygon2D" parent="YardStructure/FirstStepGuidance"]',
        '[node name="MailboxFocusMarker" type="Polygon2D" parent="YardStructure/FirstStepGuidance"]',
    ],
    "tools/validate_current_objective_guidance.gd": [
        "current objective guidance runtime validation passed",
        "_validate_objective_chip",
        "_validate_house_guidance",
        "_validate_yard_guidance",
        "_validate_mailbox_advances_chip",
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
    print("OK: current objective guidance static contract validated")


if __name__ == "__main__":
    main()
