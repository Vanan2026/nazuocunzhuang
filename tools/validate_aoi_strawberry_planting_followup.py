from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/autoload/QuestManager.gd": [
        '"shared_first_turnip_day1",\n\t"planted_aoi_strawberry_day1",\n\t"garden_bench_restored"',
        '"planted_aoi_strawberry_day1": _get_flag(game_state, "planted_aoi_strawberry_day1")',
        '"planted_aoi_strawberry_day1"',
    ],
    "game/scenes/world/PlayerYard.gd": [
        "func _mark_aoi_strawberry_planted(",
        '"planted_aoi_strawberry_day1"',
        '"shared_first_turnip_day1"',
        '"seed_strawberry"',
        '"strawberry_spring"',
        "plot_index != 1",
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        '"shared_first_turnip_day1",\n\t"planted_aoi_strawberry_day1",\n\t"garden_bench_restored"',
        '"planted_aoi_strawberry_day1"',
    ],
    "game/scenes/ui/FirstWeekQuestHUD.gd": [
        '"planted_aoi_strawberry_day1"',
    ],
    "game/scenes/ui/CurrentObjectiveChip.tscn": [
        'text = "0 / 13"',
    ],
    "game/scenes/ui/FirstWeekQuestHUD.tscn": [
        "0 / 13",
    ],
    "tools/validate_aoi_strawberry_planting_followup.gd": [
        "aoi strawberry planting follow-up runtime validation passed",
        "planted_aoi_strawberry_day1",
        "FarmPlots/FarmPlot1",
        "seed_strawberry",
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

    print("OK: Aoi strawberry planting follow-up static contract validated")


if __name__ == "__main__":
    main()
