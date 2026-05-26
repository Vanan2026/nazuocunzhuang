from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTDOOR_GD = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"
SERVICE_GD = ROOT / "game" / "entities" / "interactable" / "SeedStallAdvice.gd"
RUNTIME_GD = ROOT / "tools" / "validate_village_seed_stall_daily_advice.gd"
TASK_OPEN = ROOT / ".codex" / "tasks" / "open" / "2026-05-23-village-seed-stall-daily-advice.md"
TASK_DONE = ROOT / ".codex" / "tasks" / "done" / "2026-05-23-village-seed-stall-daily-advice.md"

REQUIRED_SERVICE_TOKENS = [
    "class_name SeedStallAdvice",
    'extends "res://game/entities/interactable/Interactable.gd"',
    "PLAYER_VERB_TAG",
    "TODAY_REASON_TAG",
    "RETURN_REASON_TAG",
    "visited_village_seed_stall_day1",
    "asked_seed_stall_advice_%s_day%d",
    "func on_interact",
    "func get_today_advice_flag_id",
    "func _build_advice_dialogue",
    "func _get_game_state",
    "func _get_time_manager",
    "func _get_dialogue_box",
    "show_dialogue",
    "seed_stall_daily_advice",
]

REQUIRED_OUTDOOR_TOKENS = [
    'const SEED_STALL_ADVICE_SCRIPT: Script = preload("res://game/entities/interactable/SeedStallAdvice.gd")',
    "func _add_village_seed_stall_advice",
    "SeedStallProxy",
    "SEED_STALL_ADVICE_SCRIPT",
    "visited_village_seed_stall_day1",
]

REQUIRED_RUNTIME_TOKENS = [
    "asked_seed_stall_advice_spring_day1",
    "asked_seed_stall_advice_spring_day2",
    "visited_village_seed_stall_day1",
    "inventory should not change",
    "money should not change",
    "SeedStallProxy should show advice dialogue",
]

FORBIDDEN_SERVICE_TERMS = [
    "InventoryManager",
    "add_item",
    "remove_item",
    "set_player_money",
    "player_money",
    "sell_price",
    "price",
    "money",
    "reward",
    "combat",
    "monster",
    "damage",
    "weapon",
    "armor",
    "hp",
    "kill",
    "loot",
    "deadline",
    "countdown",
    "back_farm",
    "pond",
    "mountain_path",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    outdoor_text = read(OUTDOOR_GD)
    service_text = read(SERVICE_GD)
    runtime_text = read(RUNTIME_GD)

    for token in REQUIRED_SERVICE_TOKENS:
        require(token in service_text, f"SeedStallAdvice.gd missing token: {token}")

    for token in REQUIRED_OUTDOOR_TOKENS:
        require(token in outdoor_text, f"OutdoorWorld.gd missing seed-stall advice token: {token}")

    for token in REQUIRED_RUNTIME_TOKENS:
        require(token in runtime_text, f"runtime validator missing token: {token}")

    lowered_service = service_text.lower()
    for term in FORBIDDEN_SERVICE_TERMS:
        require(term not in lowered_service, f"seed-stall advice should not introduce forbidden scope: {term}")

    require(
        TASK_OPEN.exists() or TASK_DONE.exists(),
        "seed-stall daily advice task should be recorded in .codex/tasks/open or .codex/tasks/done",
    )

    print("OK: village seed-stall daily advice static validation passed")


if __name__ == "__main__":
    main()
