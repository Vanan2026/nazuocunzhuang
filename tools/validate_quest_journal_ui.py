from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "project.godot": [
        "open_journal={",
        "physical_keycode\":74",
    ],
    "game/scenes/ui/QuestJournalUI.gd": [
        "class_name QuestJournalUI",
        "const OBJECTIVE_LABELS",
        "func bind_quest_manager(",
        "func toggle_journal(",
        "func show_journal(",
        "func hide_journal(",
        "func get_current_goal_text(",
        "func get_visible_objective_texts(",
        "村庄手账",
        "当前目标",
        "读邮箱",
        "听 Mika 的传闻",
    ],
    "game/scenes/ui/QuestJournalUI.tscn": [
        'path="res://game/scenes/ui/QuestJournalUI.gd"',
        '[node name="QuestJournalUI" type="CanvasLayer"]',
        '[node name="Panel" type="PanelContainer" parent="."]',
        '[node name="ObjectiveList" type="VBoxContainer" parent="Panel/Content"]',
        '[node name="CurrentGoalLabel" type="Label" parent="Panel/Content"]',
    ],
    "game/scenes/Main.tscn": [
        'path="res://game/scenes/ui/QuestJournalUI.tscn"',
        '[node name="QuestJournalUI" parent="." instance=',
    ],
    "game/scenes/Main.gd": [
        "quest_journal_ui",
        "QuestJournalUI",
        "bind_quest_manager",
    ],
}


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
    print("OK: quest journal UI static contract validated")


if __name__ == "__main__":
    main()
