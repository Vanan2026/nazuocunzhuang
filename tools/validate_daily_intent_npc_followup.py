from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DIALOGUES = {
    "aoi_daily_intent_tend_crops_01": ("aoi", "tend_crops", "菜地"),
    "mika_daily_intent_village_notice_01": ("mika", "check_village_notice", "村口"),
    "hana_daily_intent_visit_neighbor_01": ("hana", "visit_neighbor", "问候"),
    "gen_daily_intent_repair_material_01": ("gen", "gather_repair_material", "修复材料"),
}

EXPECTED_SNIPPETS = {
    "game/entities/npc/NPC.gd": [
        '"daily_intent": ""',
        "func _try_daily_intent_dialogue_interaction(",
        'context["daily_intent"] = _get_selected_daily_intent_id()',
        "func _get_selected_daily_intent_id(",
        "func _get_current_day_key(",
        'game_state.get_daily_intent(_get_current_day_key())',
    ],
    "game/autoload/DialogueManager.gd": [
        '_matches_text_condition(conditions, context, "daily_intent")',
    ],
    "tools/validate_daily_intent_npc_followup.gd": [
        "daily intent NPC follow-up runtime validation passed",
        "_validate_dialogue_manager_daily_intent_conditions",
        "_validate_npc_context_uses_selected_daily_intent",
        "_validate_intent_does_not_carry_to_next_day",
        "_validate_main_scene_rumor_does_not_hide_intent",
    ],
    "tools/capture_daily_intent_npc_followup.gd": [
        "captured daily intent NPC follow-up snapshot",
        "check_village_notice",
        "mika_daily_intent_village_notice_village_01",
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

    dialogue_path = ROOT / "game/data/dialogues.json"
    dialogues = json.loads(dialogue_path.read_text(encoding="utf-8"))
    by_id = {str(row.get("dialogue_id", "")): row for row in dialogues}
    for dialogue_id, (npc_id, intent_id, required_text) in EXPECTED_DIALOGUES.items():
        row = by_id.get(dialogue_id)
        if row is None:
            fail(f"missing daily intent dialogue: {dialogue_id}")
        if row.get("npc_id") != npc_id:
            fail(f"{dialogue_id} should belong to {npc_id}")
        if row.get("type") != "daily":
            fail(f"{dialogue_id} should be daily dialogue")
        if int(row.get("priority", 0)) < 30:
            fail(f"{dialogue_id} should outrank normal daily dialogue")
        conditions = row.get("conditions", {})
        if conditions.get("daily_intent") != intent_id:
            fail(f"{dialogue_id} should require daily_intent {intent_id}")
        if row.get("sets_flags") != []:
            fail(f"{dialogue_id} should not set flags or rewards")
        line_text = " ".join(str(line.get("text", "")) for line in row.get("lines", []))
        if required_text not in line_text:
            fail(f"{dialogue_id} should include authored follow-up text: {required_text}")

    print("OK: daily intent NPC follow-up static contract validated")


if __name__ == "__main__":
    main()
