from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEST_MANAGER_GD = ROOT / "game" / "autoload" / "QuestManager.gd"
CURRENT_CHIP_GD = ROOT / "game" / "scenes" / "ui" / "CurrentObjectiveChip.gd"
HUD_GD = ROOT / "game" / "scenes" / "ui" / "FirstWeekQuestHUD.gd"
RUNTIME_GD = ROOT / "tools" / "validate_village_first_week_guidance_bridge.gd"
TASK_PATHS = [
    ROOT / ".codex" / "tasks" / "open" / "2026-05-23-village-first-week-guidance-bridge.md",
    ROOT / ".codex" / "tasks" / "done" / "2026-05-23-village-first-week-guidance-bridge.md",
]

ENTRY_OBJECTIVE_ID = "read_village_notice_day1"
EXPLORATION_FLAG_IDS = [
    "asked_seed_stall_advice_spring_day1",
    "found_village_soft_clue_day1",
    "heard_old_well_echo_after_village_clue_day1",
    "heard_mika_old_well_echo_day1",
]

OBJECTIVE_ARRAYS = {
    QUEST_MANAGER_GD: "FIRST_WEEK_OBJECTIVES",
    CURRENT_CHIP_GD: "OBJECTIVE_ORDER",
    HUD_GD: "OBJECTIVE_ORDER",
}

REQUIRED_ENTRY_TOKENS = [
    ENTRY_OBJECTIVE_ID,
]

REQUIRED_RUNTIME_TOKENS = [
    "village first-week exploration bridge runtime validation passed",
    "_mark_pre_village_progress",
    "_expect_current_objective",
    "_complete_village_notice_bridge",
    ENTRY_OBJECTIVE_ID,
    "asked_seed_stall_advice_spring_day1",
    "13",
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


def extract_array_block(text: str, const_name: str) -> str:
    start_token = f"const {const_name}"
    start = text.find(start_token)
    require(start >= 0, f"missing const array: {const_name}")
    equals = text.find("=", start)
    require(equals >= 0, f"missing array assignment for {const_name}")
    open_bracket = text.find("[", equals)
    require(open_bracket >= 0, f"missing array open bracket for {const_name}")
    close_bracket = text.find("]", open_bracket)
    require(close_bracket >= 0, f"missing array close bracket for {const_name}")
    return text[open_bracket : close_bracket + 1]


def main() -> None:
    quest_text = read(QUEST_MANAGER_GD)
    chip_text = read(CURRENT_CHIP_GD)
    hud_text = read(HUD_GD)
    runtime_text = read(RUNTIME_GD)
    task_text = read_existing_task()

    for token in REQUIRED_ENTRY_TOKENS:
        require(token in quest_text, f"QuestManager.gd missing village entry token: {token}")
    for path, const_name in OBJECTIVE_ARRAYS.items():
        text = read(path)
        block = extract_array_block(text, const_name)
        require(ENTRY_OBJECTIVE_ID in block, f"{path.relative_to(ROOT)} missing entry objective in {const_name}")
        for flag_id in EXPLORATION_FLAG_IDS:
            require(
                flag_id not in block,
                f"{path.relative_to(ROOT)} should leave exploratory flag out of {const_name}: {flag_id}",
            )

    for token in REQUIRED_RUNTIME_TOKENS:
        require(token in runtime_text, f"runtime validator missing token: {token}")
    require(ENTRY_OBJECTIVE_ID in task_text, f"task record missing entry objective: {ENTRY_OBJECTIVE_ID}")
    for flag_id in EXPLORATION_FLAG_IDS:
        require(flag_id in task_text, f"task record should name exploratory non-objective flag: {flag_id}")
    require(
        "exploration" in task_text and "not formal objectives" in task_text and "Village notice bridge" in task_text,
        "task record should describe the light Village notice bridge and exploration boundary",
    )
    print("OK: village first-week exploration bridge static validation passed")


if __name__ == "__main__":
    main()
