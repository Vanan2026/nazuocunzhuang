from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/entities/interactable/ResourcePickup.gd": [
        "@export var pickup_id: String",
        "@export var claim_flag_id: String",
        "@export var game_state_path: NodePath",
        "func refresh_claim_state(",
        "func _get_claim_flag_id(",
        "resource_pickup_claimed_%s",
        ".get_flag(",
        ".set_flag(",
        "_set_claimed_visual_state",
    ],
    "game/scenes/world/PlayerYard.tscn": [
        'pickup_id = "player_yard_wood_pile_day1"',
        'pickup_id = "player_yard_stone_pile_day1"',
    ],
    "game/scenes/world/ForestEdge.tscn": [
        'pickup_id = "forest_edge_fallen_branch_bundle_day1"',
        'pickup_id = "forest_edge_flat_stone_cache_day1"',
    ],
    "game/scenes/ui/DialogueBox.tscn": [
        "offset_left = 24.0",
        "offset_top = 588.0",
        "offset_right = 620.0",
        "offset_bottom = 708.0",
        "custom_minimum_size = Vector2(72, 72)",
    ],
    "tools/validate_resource_pickup_persistence.gd": [
        "resource pickup persistence runtime validation passed",
        "_validate_yard_pickups",
        "_validate_forest_pickups",
        "_validate_save_resume_claims",
        "_validate_dialogue_box_layout",
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


def validate_snippets() -> None:
    for relative_path, snippets in EXPECTED_SNIPPETS.items():
        text = read_text(relative_path)
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                fail(f"{relative_path} contains forbidden gameplay term: {pattern.pattern}")


def main() -> None:
    validate_snippets()
    print("OK: resource pickup persistence static contract validated")


if __name__ == "__main__":
    main()
