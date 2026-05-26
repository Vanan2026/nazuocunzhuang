from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/autoload/QuestManager.gd": [
        '"watered_first_crop_day1",\n\t"harvested_first_crop_day1",\n\t"shared_first_turnip_day1"',
        '"harvested_first_crop_day1": _get_flag(game_state, "harvested_first_crop_day1")',
        '"shared_first_turnip_day1": _get_flag(game_state, "shared_first_turnip_day1")',
        '"收获第一棵作物"',
        '"回屋睡觉后继续浇水，成熟后按 E 收获"',
    ],
    "game/scenes/world/PlayerYard.gd": [
        "func _on_farm_plot_harvested(",
        '"harvested_first_crop_day1"',
        'game_state.set_flag("harvested_first_crop_day1", true)',
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        '"harvested_first_crop_day1"',
        '"收获第一棵作物"',
    ],
    "game/scenes/ui/FirstWeekQuestHUD.gd": [
        '"harvested_first_crop_day1"',
        '"收获第一棵作物"',
    ],
    "game/scenes/ui/CurrentObjectiveChip.tscn": [
        'text = "0 / 13"',
    ],
    "game/scenes/ui/FirstWeekQuestHUD.tscn": [
        'text = "进度 0 / 13"',
    ],
    "tools/validate_first_week_harvest_guidance.gd": [
        "harvested_first_crop_day1",
        "first-week harvest guidance runtime validation passed",
        'main.get_node_or_null("QuestJournalUI") == null',
        'not InputMap.has_action("open_journal")',
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
    print("OK: first-week harvest guidance static contract validated")


if __name__ == "__main__":
    main()
