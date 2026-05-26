from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/scenes/Main.gd": [
        "func _build_crop_status_feedback(",
        "func _show_crop_status_feedback(",
        '"crop_status_sleep"',
        "菜地有新变化",
        "作物已经成熟，可以去院子里收获了。",
        "var advance_summary := _advance_farm_plot_states_for_new_day(auto_water)",
        "_show_crop_status_feedback(advance_summary)",
    ],
    "game/scenes/home/PlayerHouse.tscn": [
        'path="res://game/scenes/ui/DialogueBox.tscn"',
        '[node name="DialogueBox" parent="." instance=',
    ],
    "tools/validate_morning_crop_status_feedback.gd": [
        "morning crop status feedback runtime validation passed",
        "_expect_crop_feedback",
        "菜地",
        "成熟",
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
    print("OK: morning crop status feedback static contract validated")


if __name__ == "__main__":
    main()
