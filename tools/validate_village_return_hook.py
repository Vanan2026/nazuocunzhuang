from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAYER_YARD_GD = ROOT / "game" / "scenes" / "world" / "PlayerYard.gd"
OUTDOOR_GD = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"
TASK_PATHS = [
    ROOT / ".codex" / "tasks" / "open" / "2026-05-23-village-return-hook.md",
    ROOT / ".codex" / "tasks" / "done" / "2026-05-23-village-return-hook.md",
]

REQUIRED_PLAYER_YARD_TOKENS = [
    "old_well: Node",
    "get_node_or_null(\"OldWell\")",
    "_on_old_well_interacted",
    "_try_village_clue_old_well_echo",
    "_show_village_clue_old_well_echo",
    "heard_old_well_echo_after_village_clue_day1",
    "found_village_soft_clue_day1",
    "returned_from_village_day1",
]

REQUIRED_OUTDOOR_TOKENS = [
    "VillageReturnPath",
    "returned_from_village_day1",
    "OldMapleClue",
    "found_village_soft_clue_day1",
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
    player_yard_text = read(PLAYER_YARD_GD)
    outdoor_text = read(OUTDOOR_GD)
    task_text = read_existing_task()

    for token in REQUIRED_PLAYER_YARD_TOKENS:
        require(token in player_yard_text, f"PlayerYard.gd missing return-hook token: {token}")
    for token in REQUIRED_OUTDOOR_TOKENS:
        require(token in outdoor_text, f"OutdoorWorld.gd missing return-route token: {token}")

    require(
        "Village return hook" in task_text and "OldWell" in task_text,
        "open task should describe the Village return hook and OldWell target",
    )
    print("OK: village return hook static validation passed")


if __name__ == "__main__":
    main()
