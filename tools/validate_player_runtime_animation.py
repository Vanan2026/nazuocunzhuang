from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/entities/player/Player.tscn": [
        '[node name="PlayerSprite" type="AnimatedSprite2D" parent="."]',
        "PlayerRuntimeFrames.tres",
    ],
    "game/entities/player/Player.gd": [
        "func resolve_direction_suffix(",
        "func resolve_animation_name(",
        "func sync_visual_animation(",
        "func play_interaction_animation(",
    ],
    "tools/validate_player_runtime_animation.gd": [
        "resolve_animation_name",
        "sync_visual_animation",
        "play_interaction_animation",
        "player_walk_right",
        "player_interact_up_left",
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

    print("OK: player runtime animation static contract validated")


if __name__ == "__main__":
    main()
