from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/entities/interactable/ResourcePickup.gd": [
        "func _show_gain_feedback(",
        "func _get_dialogue_box(",
        "获得：%s x%d，已经放进背包。",
        "dialogue_box.show_dialogue",
    ],
    "game/scenes/world/PlayerYard.gd": [
        "crop_harvested.connect(_on_farm_plot_harvested)",
        "func _on_farm_plot_harvested(",
        "func _show_item_gain_feedback(",
        "收获：%s x%d，已经放进背包。",
    ],
    "tools/validate_item_gain_feedback.gd": [
        "wood_pile.on_interact",
        "farm_plot.harvest()",
        "获得",
        "收获",
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
    print("OK: item gain feedback static contract validated")


if __name__ == "__main__":
    main()
