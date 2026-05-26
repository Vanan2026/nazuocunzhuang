from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPTURE_GD = ROOT / "tools" / "capture_village_old_well_mika_route.gd"
OUTDOOR_WORLD_GD = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"
FLAG_DIALOGUE_GD = ROOT / "game" / "entities" / "interactable" / "FlagDialogueInteractable.gd"
TASK_PATHS = [
    ROOT / ".codex" / "tasks" / "open" / "2026-05-23-village-old-well-mika-route-review.md",
    ROOT / ".codex" / "tasks" / "done" / "2026-05-23-village-old-well-mika-route-review.md",
]

REQUIRED_CAPTURE_TOKENS = [
    "DEFAULT_OUTPUT_DIR := \"res://.codex/village_old_well_mika_route\"",
    "\"seed_stall_advice\"",
    "\"village_clue\"",
    "\"old_well_echo\"",
    "\"mika_followup\"",
    "01_seed_stall_advice.png",
    "02_village_clue.png",
    "03_old_well_echo.png",
    "04_mika_followup.png",
    "VillageReturnPath",
    "SeedStallProxy",
    "OldMapleClue",
    "asked_seed_stall_advice_spring_day1",
    "seed_stall_daily_advice",
    "old_maple_clue_dialogue",
    "OldMapleClue should show clue dialogue",
    "heard_old_well_echo_after_village_clue_day1",
    "mika_old_well_echo_followup",
    "--check-only",
    "save_png",
    "REVIEW_HIDDEN_UI_NODE_NAMES",
    "CurrentObjectiveChip",
    "HeadlessLifecycle.cleanup_and_quit",
]

REQUIRED_OUTDOOR_TOKENS = [
    "FLAG_DIALOGUE_INTERACTABLE_SCRIPT",
    "FlagDialogueInteractable.gd",
    "_add_village_old_maple_clue",
    "old_maple_clue_dialogue",
    "found_village_soft_clue_day1",
]

REQUIRED_FLAG_DIALOGUE_TOKENS = [
    "class_name FlagDialogueInteractable",
    'extends "res://game/entities/interactable/FlagInteractable.gd"',
    "dialogue_id",
    "speaker_name",
    "show_dialogue",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_existing_task() -> str:
    for path in TASK_PATHS:
        if path.exists():
            return path.read_text(encoding="utf-8")
    candidates = ", ".join(str(path.relative_to(ROOT)) for path in TASK_PATHS)
    raise AssertionError(f"missing required task record; checked: {candidates}")


def main() -> None:
    require(CAPTURE_GD.exists(), f"missing review capture script: {CAPTURE_GD.relative_to(ROOT)}")
    require(OUTDOOR_WORLD_GD.exists(), f"missing outdoor world script: {OUTDOOR_WORLD_GD.relative_to(ROOT)}")
    require(FLAG_DIALOGUE_GD.exists(), f"missing flag dialogue interactable script: {FLAG_DIALOGUE_GD.relative_to(ROOT)}")
    capture_text = CAPTURE_GD.read_text(encoding="utf-8")
    outdoor_text = OUTDOOR_WORLD_GD.read_text(encoding="utf-8")
    flag_dialogue_text = FLAG_DIALOGUE_GD.read_text(encoding="utf-8")
    task_text = read_existing_task()

    for token in REQUIRED_CAPTURE_TOKENS:
        require(token in capture_text, f"capture script missing token: {token}")
    for token in REQUIRED_OUTDOOR_TOKENS:
        require(token in outdoor_text, f"OutdoorWorld missing token: {token}")
    for token in REQUIRED_FLAG_DIALOGUE_TOKENS:
        require(token in flag_dialogue_text, f"FlagDialogueInteractable missing token: {token}")
    require(
        "seed-stall advice" in task_text and "Village soft clue" in task_text and "Mika follow-up" in task_text,
        "task record should describe the seed-stall advice to village clue to Mika follow-up route",
    )
    print("OK: village old-well Mika route review static validation passed")


if __name__ == "__main__":
    main()
