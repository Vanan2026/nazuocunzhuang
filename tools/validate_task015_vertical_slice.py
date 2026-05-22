from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/scenes/Main.tscn": [
        "res://game/scenes/home/PlayerHouse.tscn",
        '[node name="PlayerHouse"',
    ],
    "game/scenes/home/PlayerHouse.tscn": [
        '[node name="PlayerHouse" type="Node2D"',
        "res://game/entities/player/Player.tscn",
        '[node name="DoorToYard" type="Area2D"',
        'target_scene = "res://game/scenes/world/PlayerYard.tscn"',
    ],
    "game/entities/interactable/ResourcePickup.gd": [
        "class_name ResourcePickup",
        "extends \"res://game/entities/interactable/Interactable.gd\"",
        "func on_interact(",
        "add_item",
    ],
    "game/entities/interactable/FlagInteractable.gd": [
        "class_name FlagInteractable",
        "extends \"res://game/entities/interactable/Interactable.gd\"",
        "func on_interact(",
        "set_flag",
    ],
    "game/scenes/world/PlayerYard.tscn": [
        "res://game/entities/interactable/ResourcePickup.gd",
        "res://game/entities/interactable/FlagInteractable.gd",
        '[node name="VillagePath" type="Area2D" parent="."',
        '[node name="WoodPile" type="Area2D" parent="."',
        '[node name="StonePile" type="Area2D" parent="."',
        'flag_id = "visited_village_path"',
        'item_id = "wood"',
        'item_id = "stone"',
    ],
    "tools/validate_task015_vertical_slice.gd": [
        "Task 015 vertical slice runtime validation passed",
        "rumor_old_well_bell",
        "heard_bell_rumor_01",
        "visited_village_path",
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

    print("OK: Task 015 vertical slice file contract validated")


if __name__ == "__main__":
    main()
