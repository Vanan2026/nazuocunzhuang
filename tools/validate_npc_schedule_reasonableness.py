from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
FARM_GARDEN_EXCLUSION_RECT = (20.0, 150.0, 158.0, 242.0)

EXPECTED_SNIPPETS = {
    "tools/capture_npc_schedule_review.gd": [
        "npc schedule review",
        "--check-only",
        "yard_morning",
        "yard_late_morning",
        "yard_afternoon",
        "forest_afternoon",
        "apply_schedule",
        "Hana",
        "Aoi",
        "Gen",
        "Mika",
        "distance_to",
        "FARM_GARDEN_EXCLUSION_RECT",
        "FarmGardenZone",
        "_set_review_time_block",
        "_expect_review_time_block",
        "get_time_text",
    ],
    "game/data/npc_schedules.json": [
        '"time_block": "morning", "scene_id": "player_yard"',
        '"time_block": "late_morning", "scene_id": "player_yard"',
        '"time_block": "afternoon", "scene_id": "forest_edge"',
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


def _inside_rect(position: list[object], rect: tuple[float, float, float, float]) -> bool:
    if len(position) != 2:
        return False
    left, top, right, bottom = rect
    x = float(position[0])
    y = float(position[1])
    return left <= x <= right and top <= y <= bottom


def _expect_player_yard_npcs_outside_farm_zone() -> None:
    schedules_path = ROOT / "game/data/npc_schedules.json"
    schedules = json.loads(schedules_path.read_text(encoding="utf-8"))
    for schedule in schedules:
        schedule_id = str(schedule.get("schedule_id", ""))
        for entry in schedule.get("entries", []):
            if not isinstance(entry, dict):
                continue
            if entry.get("scene_id") != "player_yard":
                continue
            position = entry.get("position", [])
            if _inside_rect(position, FARM_GARDEN_EXCLUSION_RECT):
                fail(
                    "player_yard NPC schedule stands inside FarmGardenZone: "
                    f"{schedule_id}/{entry.get('time_block')} at {position}"
                )


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

    _expect_player_yard_npcs_outside_farm_zone()

    print("OK: NPC schedule reasonableness static contract validated")


if __name__ == "__main__":
    main()
