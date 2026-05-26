from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/scenes/ui/GreenfieldUITheme.gd": [
        "class_name GreenfieldUITheme",
        'res://assets/art/greenfield_p0/ui/ui_panel_frame_512x320.png',
        'res://assets/art/greenfield_p0/ui/ui_hud_panel_512x128.png',
        'res://assets/art/greenfield_p0/ui/ui_dialogue_frame_1024x256.png',
        'res://assets/art/greenfield_p0/ui/ui_button_256x96.png',
        "func apply_surface_panel(",
        "func apply_hud_panel(",
        "func apply_dialogue_panel(",
        "func apply_button(",
        "func apply_title_label(",
        "func apply_body_label(",
        "func apply_hint_label(",
    ],
    "game/scenes/ui/DialogueBox.gd": [
        "GreenfieldUITheme",
        "func _apply_visual_theme(",
        "apply_dialogue_panel",
        "apply_title_label",
        "apply_body_label",
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        "GreenfieldUITheme",
        "func _apply_visual_theme(",
        "apply_hud_panel",
        "apply_title_label",
        "apply_body_label",
        "apply_hint_label",
    ],
    "game/scenes/ui/DailyIntentPanel.gd": [
        "GreenfieldUITheme",
        "func _apply_visual_theme(",
        "apply_surface_panel",
        "apply_button(",
        "apply_title_label",
        "apply_body_label",
        "apply_hint_label",
    ],
    "game/scenes/ui/TimeWeatherHUD.gd": [
        "GreenfieldUITheme",
        "func _apply_visual_theme(",
        "apply_hud_panel",
        "apply_body_label",
        "apply_hint_label",
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


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        fail(f"missing file: {relative_path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    for relative_path, snippets in EXPECTED_SNIPPETS.items():
        text = read_text(relative_path)
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                fail(f"{relative_path} contains forbidden gameplay term: {pattern.pattern}")
    print("OK: UI quiet art pass static contract validated")


if __name__ == "__main__":
    main()
