from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/autoload/DialogueManager.gd": [
        '_matches_text_condition(conditions, context, "scene_id")',
        "func get_daily_intent_dialogue(",
    ],
    "game/entities/npc/NPC.gd": [
        '"scene_id": ""',
        'context["scene_id"] = _get_scene_context_id()',
        "func _get_scene_context_id(",
        "get_active_region_id",
    ],
    "tools/validate_daily_intent_location_variation.gd": [
        "daily intent location variation runtime validation passed",
        "_validate_dialogue_manager_scene_id_conditions",
        "_validate_npc_context_reads_active_region",
        "_validate_main_village_uses_location_specific_reply",
    ],
}

EXPECTED_DIALOGUE = {
    "dialogue_id": "mika_daily_intent_village_notice_village_01",
    "npc_id": "mika",
    "type": "daily",
    "daily_intent": "check_village_notice",
    "scene_id": "village",
    "required_text": "旧枫树",
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

    dialogues = json.loads((ROOT / "game/data/dialogues.json").read_text(encoding="utf-8"))
    by_id = {str(row.get("dialogue_id", "")): row for row in dialogues}
    row = by_id.get(EXPECTED_DIALOGUE["dialogue_id"])
    if row is None:
        fail(f"missing location-aware daily intent dialogue: {EXPECTED_DIALOGUE['dialogue_id']}")
    if row.get("npc_id") != EXPECTED_DIALOGUE["npc_id"]:
        fail("location-aware daily intent dialogue should belong to Mika")
    if row.get("type") != EXPECTED_DIALOGUE["type"]:
        fail("location-aware daily intent dialogue should remain daily type")
    if int(row.get("priority", 0)) < 40:
        fail("location-aware daily intent dialogue should outrank the generic daily-intent line")
    conditions = row.get("conditions", {})
    if conditions.get("daily_intent") != EXPECTED_DIALOGUE["daily_intent"]:
        fail("location-aware dialogue should require check_village_notice daily intent")
    if conditions.get("scene_id") != EXPECTED_DIALOGUE["scene_id"]:
        fail("location-aware dialogue should require scene_id=village")
    if row.get("sets_flags") != []:
        fail("location-aware daily intent dialogue should not set flags or rewards")
    line_text = " ".join(str(line.get("text", "")) for line in row.get("lines", []))
    if EXPECTED_DIALOGUE["required_text"] not in line_text:
        fail("location-aware Mika line should mention Village-local detail")

    print("OK: daily intent location variation static contract validated")


if __name__ == "__main__":
    main()
