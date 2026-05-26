from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTDOOR_GD = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"
NPC_SCHEDULES = ROOT / "game" / "data" / "npc_schedules.json"
CAPTURE_SCRIPT = ROOT / "tools" / "capture_outdoor_world_visual_calibration.gd"

REQUIRED_OUTDOOR_TOKENS = [
    "func _add_village_authored_slice",
    "VillagePlazaZone",
    "VillageNotice",
    "SeedStallProxy",
    "OldMapleClue",
    "VillageReturnPath",
    "read_village_notice_day1",
    "visited_village_seed_stall_day1",
    "found_village_soft_clue_day1",
    "village_default",
    "res://game/entities/interactable/FlagInteractable.gd",
    "res://game/entities/interactable/SceneTravel.gd",
]

FORBIDDEN_TERMS = [
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
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> object:
    return json.loads(read(path))


def _schedule_has_village_aoi_proof(schedules: list[dict]) -> bool:
    for schedule in schedules:
        if schedule.get("schedule_id") != "shopkeeper_basic":
            continue
        for entry in schedule.get("entries", []):
            if entry.get("scene_id") != "village":
                continue
            if entry.get("time_block") not in {"morning", "late_morning", "afternoon"}:
                continue
            position = entry.get("position", [])
            if not (isinstance(position, list) and len(position) == 2):
                continue
            x, y = float(position[0]), float(position[1])
            if 48.0 <= x <= 280.0 and 48.0 <= y <= 200.0:
                return True
    return False


def main() -> None:
    outdoor_text = read(OUTDOOR_GD)
    capture_text = read(CAPTURE_SCRIPT)
    schedules = load_json(NPC_SCHEDULES)
    require(isinstance(schedules, list), "npc_schedules.json should contain a list")

    for token in REQUIRED_OUTDOOR_TOKENS:
        require(token in outdoor_text, f"OutdoorWorld.gd missing village slice token: {token}")

    require(
        _schedule_has_village_aoi_proof(schedules),
        "shopkeeper_basic should include one explicit village schedule entry in local village coordinates",
    )
    require(
        '"village"' in capture_text and "outdoor_region_village.png" in capture_text,
        "OutdoorWorld visual capture should keep a village screenshot target",
    )

    changed_contract_text = "\n".join([outdoor_text, json.dumps(schedules, ensure_ascii=False)])
    lowered = changed_contract_text.lower()
    for term in FORBIDDEN_TERMS:
        require(term not in lowered, f"village slice should not introduce pressure or combat term: {term}")

    print("OK: village authored slice static validation passed")


if __name__ == "__main__":
    main()
