from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MUST_NOT_CONTAIN = {
    "project.godot": [
        "open_journal={",
        "physical_keycode\":74",
    ],
    "game/scenes/Main.tscn": [
        'path="res://game/scenes/ui/QuestJournalUI.tscn"',
        '[node name="QuestJournalUI" parent="." instance=',
    ],
    "game/scenes/Main.gd": [
        "QUEST_JOURNAL_UI_SCENE_NAME",
        "quest_journal_ui",
        "$QuestJournalUI",
        "QuestJournalUI",
        "手账",
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        "打开手账",
        "手账",
    ],
    "game/scenes/ui/DailyIntentPanel.gd": [
        "QuestJournalUI",
        "hide_journal",
        "手账",
    ],
    "game/scenes/home/PlayerHouse.tscn": [
        "手账",
    ],
    "game/autoload/QuestManager.gd": [
        "打开手账",
        "手账",
    ],
}

MUST_CONTAIN = {
    "game/scenes/Main.tscn": [
        'path="res://game/scenes/ui/CurrentObjectiveChip.tscn"',
        '[node name="CurrentObjectiveChip" parent="." instance=',
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        "DAILY_LOOP_NO_INTENT_HINT",
        "晨间小桌",
        "WeeklyRhythmContext.build_chip_hint",
    ],
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    for relative_path, snippets in MUST_NOT_CONTAIN.items():
        path = ROOT / relative_path
        if not path.is_file():
            fail(f"missing file: {relative_path}")
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet in text:
                fail(f"{relative_path} still contains retired journal token: {snippet}")

    for relative_path, snippets in MUST_CONTAIN.items():
        path = ROOT / relative_path
        if not path.is_file():
            fail(f"missing file: {relative_path}")
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required replacement token: {snippet}")

    print("OK: player-facing journal retirement static contract validated")


if __name__ == "__main__":
    main()
