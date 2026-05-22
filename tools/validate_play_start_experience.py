from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/entities/player/Player.tscn": [
        '[node name="PlayerSprite" type="Sprite2D" parent="."]',
        "chr_player_base_idle_down_128.png",
    ],
    "game/scenes/home/PlayerHouse.tscn": [
        '[node name="WorldCamera" type="Camera2D" parent="."]',
        "enabled = true",
        "zoom = Vector2(",
        '[node name="RoomBackdrop" type="Polygon2D" parent="."]',
    ],
    "game/scenes/world/PlayerYard.tscn": [
        'name="WorldCamera" type="Camera2D"',
        "enabled = true",
        "zoom = Vector2(",
        '[node name="WorldBackdrop" type="Polygon2D" parent="."]',
    ],
    "game/scenes/world/ForestEdge.tscn": [
        'name="WorldCamera" type="Camera2D"',
        "enabled = true",
        "zoom = Vector2(",
        '[node name="WorldBackdrop" type="Polygon2D" parent="."]',
    ],
    "game/scenes/ui/FirstWeekQuestHUD.tscn": [
        '[node name="FirstWeekQuestHUD" type="CanvasLayer"]',
        "visible = false",
    ],
    "game/scenes/ui/QuestJournalUI.tscn": [
        '[node name="QuestJournalUI" type="CanvasLayer"]',
        "visible = false",
    ],
    "tools/validate_play_start_experience.gd": [
        "Play start experience validation passed",
        "_validate_scene_view",
        "_validate_player_visible",
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

    print("OK: play start experience static contract validated")


if __name__ == "__main__":
    main()
