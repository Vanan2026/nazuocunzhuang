from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPTURE_GD = ROOT / "tools" / "capture_village_normal_input_route.gd"
PLAYER_GD = ROOT / "game" / "entities" / "player" / "Player.gd"
INTERACTION_AREA_GD = ROOT / "game" / "entities" / "interactable" / "InteractionArea.gd"
OUTDOOR_WORLD_GD = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"
TASK_PATHS = [
    ROOT / ".codex" / "tasks" / "open" / "2026-05-23-village-normal-input-route-review.md",
    ROOT / ".codex" / "tasks" / "done" / "2026-05-23-village-normal-input-route-review.md",
]

REQUIRED_CAPTURE_TOKENS = [
    "DEFAULT_OUTPUT_DIR := \"res://.codex/village_normal_input_route\"",
    "Input.action_press",
    "Input.action_release",
    "Input.parse_input_event",
    "\"walk_to_village_prompt\"",
    "\"notice_input_dialogue\"",
    "\"seed_stall_input_dialogue\"",
    "\"old_maple_input_dialogue\"",
    "\"old_well_input_echo\"",
    "\"mika_input_followup\"",
    "01_walk_to_village_prompt.png",
    "02_notice_input_dialogue.png",
    "03_seed_stall_input_dialogue.png",
    "04_old_maple_input_dialogue.png",
    "05_old_well_input_echo.png",
    "06_mika_input_followup.png",
    "InteractionHintUI",
    "_drive_player_to_global",
    "_press_interact_action",
    "_expect_prompt_hidden",
    "VillagePath",
    "VillageNotice",
    "SeedStallProxy",
    "OldMapleClue",
    "old_maple_clue_dialogue",
    "VillageReturnPath",
    "heard_old_well_echo_after_village_clue_day1",
    "mika_old_well_echo_followup",
    "--check-only",
    "save_png",
    "HeadlessLifecycle.cleanup_and_quit",
]

REQUIRED_PLAYER_TOKENS = [
    "_refresh_interaction_hint_ui",
    "InteractionHintUI",
    "get_interaction_hint",
    "show_hint",
    "hide_hint",
    "hide_hint_now",
]

REQUIRED_INTERACTION_AREA_TOKENS = [
    "_is_candidate_in_active_region",
    "_get_candidate_region_id",
    "outdoor_region_id",
    "region_id",
    "get_active_region_id",
]

REQUIRED_OUTDOOR_WORLD_TOKENS = [
    "_assign_outdoor_region_meta",
    "outdoor_region_id",
    '"player_yard"',
    '"forest_edge"',
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def read_existing_task() -> str:
    for path in TASK_PATHS:
        if path.exists():
            return path.read_text(encoding="utf-8")
    candidates = ", ".join(str(path.relative_to(ROOT)) for path in TASK_PATHS)
    raise AssertionError(f"missing required task record; checked: {candidates}")


def main() -> None:
    capture_text = read(CAPTURE_GD)
    player_text = read(PLAYER_GD)
    interaction_area_text = read(INTERACTION_AREA_GD)
    outdoor_world_text = read(OUTDOOR_WORLD_GD)
    task_text = read_existing_task()

    for token in REQUIRED_CAPTURE_TOKENS:
        require(token in capture_text, f"capture script missing token: {token}")
    for token in REQUIRED_PLAYER_TOKENS:
        require(token in player_text, f"Player.gd missing prompt integration token: {token}")
    for token in REQUIRED_INTERACTION_AREA_TOKENS:
        require(token in interaction_area_text, f"InteractionArea.gd missing active-region gate token: {token}")
    for token in REQUIRED_OUTDOOR_WORLD_TOKENS:
        require(token in outdoor_world_text, f"OutdoorWorld.gd missing region metadata token: {token}")
    require(
        "normal-input" in task_text
        and "movement" in task_text
        and "InteractionHintUI" in task_text
        and "Village route" in task_text,
        "task record should describe the normal-input Village route review scope",
    )
    print("OK: village normal-input route review static validation passed")


if __name__ == "__main__":
    main()
