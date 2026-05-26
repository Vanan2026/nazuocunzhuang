from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/scenes/Main.gd": [
        "var farm_plot_states: Dictionary",
        "func _capture_farm_plot_states_from_scene(",
        "func _apply_farm_plot_states_to_scene(",
        "func _advance_farm_plot_states_for_new_day(",
        "func _on_scene_sleep_completed(",
        'data["farm_plots"] = farm_plot_states.duplicate(true)',
    ],
    "game/scenes/home/PlayerHouse.tscn": [
        "res://game/entities/interactable/BedInteractable.gd",
        '[node name="Bed" type="Area2D"',
        'interactable_id = "house_bed"',
        'interaction_hint = "按 E 休息到明天"',
    ],
    "game/scenes/world/PlayerYard.tscn": [
        '[node name="HouseDoor" type="Area2D"',
        'target_scene_id = "player_house"',
        'target_spawn_id = "inside_default"',
    ],
    "game/entities/interactable/BedInteractable.gd": [
        "while parent_node != null:",
        'parent_node.get_node_or_null(fallback_name)',
    ],
    "tools/validate_main_flow_crop_sleep_harvest.gd": [
        "house_bed.on_interact",
        'main.change_scene("player_yard", "from_house")',
        'crop_turnip',
        "farm_plot.harvest()",
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
    print("OK: main-flow crop sleep/harvest static contract validated")


if __name__ == "__main__":
    main()
