from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/autoload/DialogueManager.gd": [
        "func get_daily_intent_dialogue(",
        "required_daily_intent",
        '_matches_text_condition(conditions, context, "daily_intent")',
    ],
    "game/entities/npc/NPC.gd": [
        "get_daily_intent_dialogue",
        "func _try_daily_intent_dialogue_interaction(",
        'String(conditions.get("daily_intent", ""))',
    ],
    "tools/validate_daily_intent_relationship_variation.gd": [
        "daily intent relationship variation runtime validation passed",
        "_validate_close_neighbor_dialogue",
        "_validate_generic_relationship_does_not_hide_daily_intent",
        "_validate_npc_interaction_uses_intent_specific_dialogue",
    ],
}

EXPECTED_DIALOGUE = {
    "dialogue_id": "hana_daily_intent_visit_neighbor_close_01",
    "npc_id": "hana",
    "type": "relationship",
    "daily_intent": "visit_neighbor",
    "min_hearts": 2,
    "required_text": "热茶",
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

    dialogue_path = ROOT / "game" / "data" / "dialogues.json"
    dialogues = json.loads(dialogue_path.read_text(encoding="utf-8"))
    by_id = {str(row.get("dialogue_id", "")): row for row in dialogues}
    row = by_id.get(EXPECTED_DIALOGUE["dialogue_id"])
    if row is None:
        fail(f"missing relationship-aware daily intent dialogue: {EXPECTED_DIALOGUE['dialogue_id']}")
    if row.get("npc_id") != EXPECTED_DIALOGUE["npc_id"]:
        fail("relationship-aware daily intent dialogue should belong to Hana")
    if row.get("type") != EXPECTED_DIALOGUE["type"]:
        fail("relationship-aware daily intent dialogue should use relationship type")
    conditions = row.get("conditions", {})
    if conditions.get("daily_intent") != EXPECTED_DIALOGUE["daily_intent"]:
        fail("relationship-aware dialogue should require visit_neighbor daily intent")
    if int(conditions.get("min_hearts", 0)) < int(EXPECTED_DIALOGUE["min_hearts"]):
        fail("relationship-aware dialogue should require at least 2 hearts")
    if row.get("sets_flags") != []:
        fail("relationship-aware daily intent dialogue should not set flags or rewards")
    line_text = " ".join(str(line.get("text", "")) for line in row.get("lines", []))
    if EXPECTED_DIALOGUE["required_text"] not in line_text:
        fail("relationship-aware Hana line should feel more personal")

    print("OK: daily intent relationship variation static contract validated")


if __name__ == "__main__":
    main()
