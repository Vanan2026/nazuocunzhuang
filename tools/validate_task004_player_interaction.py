from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/entities/player/Player.gd": [
        "extends CharacterBody2D",
        "class_name Player",
        "Input.get_vector(\"move_left\", \"move_right\", \"move_up\", \"move_down\")",
        "func try_interact(",
        "move_and_slide()",
    ],
    "game/entities/player/Player.tscn": [
        '[node name="Player" type="CharacterBody2D"',
        '[node name="CollisionShape2D"',
        '[node name="InteractionArea" type="Area2D"',
    ],
    "game/entities/interactable/Interactable.gd": [
        "extends Area2D",
        "class_name Interactable",
        "signal interacted",
        "func on_interact(",
        "func get_interaction_hint(",
        'add_to_group("interactable")',
    ],
    "game/entities/interactable/InteractionArea.gd": [
        "extends Area2D",
        "class_name InteractionArea",
        "func get_nearest_interactable(",
        "area_entered.connect",
        "area_exited.connect",
    ],
    "game/scenes/world/PlayerYard.tscn": [
        "res://game/entities/player/Player.tscn",
        "res://game/entities/interactable/Interactable.gd",
        '[node name="Mailbox"',
        '[node name="Bed"',
        '[node name="Signboard"',
    ],
}

REQUIRED_ACTIONS = [
    "move_up",
    "move_down",
    "move_left",
    "move_right",
    "interact",
    "use_tool",
    "open_inventory",
    "open_journal",
    "cancel",
]

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

    project_text = (ROOT / "project.godot").read_text(encoding="utf-8")
    for action in REQUIRED_ACTIONS:
        if f"{action}={{" not in project_text:
            fail(f"project.godot missing input action: {action}")

    print("OK: validated Task 004 player and interaction file contract")


if __name__ == "__main__":
    main()
