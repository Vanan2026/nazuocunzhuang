from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/autoload/QuestManager.gd": [
        '"harvested_first_crop_day1",\n\t"shared_first_turnip_day1",\n\t"planted_aoi_strawberry_day1"',
        '"shared_first_turnip_day1": _get_flag(game_state, "shared_first_turnip_day1")',
        '"shared_first_turnip_day1": "把第一根萝卜送给葵"',
        '"shared_first_turnip_day1": "院子里 · 在背包选择春萝卜，再和葵交谈"',
    ],
    "game/entities/npc/NPC.gd": [
        "signal gift_given(npc_id: String, item_id: String, delta: int, already_gifted: bool)",
        "gift_given.emit(npc_id, selected_item_id",
    ],
    "game/scenes/world/PlayerYard.gd": [
        "func _connect_npc_progress_signals() -> void:",
        "func _on_npc_gift_given(",
        '"shared_first_turnip_day1"',
        '"aoi"',
        '"crop_turnip"',
    ],
    "game/scenes/ui/CurrentObjectiveChip.gd": [
        '"shared_first_turnip_day1"',
        '"把第一根萝卜送给葵"',
        '"院子里 · 在背包选择春萝卜，再和葵交谈"',
    ],
    "game/scenes/ui/FirstWeekQuestHUD.gd": [
        '"shared_first_turnip_day1"',
        '"把第一根萝卜送给葵"',
    ],
    "game/scenes/ui/CurrentObjectiveChip.tscn": [
        'text = "0 / 13"',
    ],
    "game/scenes/ui/FirstWeekQuestHUD.tscn": [
        'text = "进度 0 / 13"',
        'text = "[ ] 把第一根萝卜送给葵"',
    ],
    "tools/validate_post_harvest_aoi_share.gd": [
        "post-harvest Aoi share runtime validation passed",
        "shared_first_turnip_day1",
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

    items_text = (ROOT / "game/data/items.json").read_text(encoding="utf-8")
    npcs_text = (ROOT / "game/data/npcs.json").read_text(encoding="utf-8")
    if '"item_id": "crop_turnip"' not in items_text or '"vegetable"' not in items_text:
        fail("crop_turnip should remain tagged as a vegetable gift candidate")
    if '"npc_id": "aoi"' not in npcs_text or '"vegetable"' not in npcs_text:
        fail("Aoi should like vegetable-tagged gifts for the first harvest handoff")

    print("OK: post-harvest Aoi share static contract validated")


if __name__ == "__main__":
    main()
