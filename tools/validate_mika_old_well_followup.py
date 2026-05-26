from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NPC_GD = ROOT / "game" / "entities" / "npc" / "NPC.gd"
DIALOGUES_JSON = ROOT / "game" / "data" / "dialogues.json"
TASK_PATHS = [
    ROOT / ".codex" / "tasks" / "open" / "2026-05-23-mika-old-well-followup.md",
    ROOT / ".codex" / "tasks" / "done" / "2026-05-23-mika-old-well-followup.md",
]

FOLLOWUP_DIALOGUE_ID = "mika_old_well_echo_followup"
SOURCE_FLAG = "heard_old_well_echo_after_village_clue_day1"
SEEN_FLAG = "heard_mika_old_well_echo_day1"

REQUIRED_NPC_TOKENS = [
    "game_state_path",
    "_try_priority_dialogue_interaction",
    "_show_npc_dialogue",
    "_apply_dialogue_flags",
    "_get_game_state_flags",
    "_get_game_state()",
    '"sets_flags"',
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def read_existing_task() -> str:
    for path in TASK_PATHS:
        if path.exists():
            return path.read_text(encoding="utf-8")
    candidates = ", ".join(str(path.relative_to(ROOT)) for path in TASK_PATHS)
    raise AssertionError(f"missing required task record; checked: {candidates}")


def load_json_array(path: Path) -> list[dict[str, Any]]:
    records = json.loads(read_text(path))
    require(isinstance(records, list), f"{path.relative_to(ROOT)} must contain a JSON array")
    return records


def main() -> None:
    npc_text = read_text(NPC_GD)
    task_text = read_existing_task()
    dialogues = load_json_array(DIALOGUES_JSON)

    for token in REQUIRED_NPC_TOKENS:
        require(token in npc_text, f"NPC.gd missing dialogue flag token: {token}")

    matches = [record for record in dialogues if record.get("dialogue_id") == FOLLOWUP_DIALOGUE_ID]
    require(len(matches) == 1, f"dialogues.json should define exactly one {FOLLOWUP_DIALOGUE_ID}")
    dialogue = matches[0]
    require(dialogue.get("npc_id") == "mika", "Mika old-well follow-up should belong to mika")
    require(dialogue.get("type") == "event", "Mika old-well follow-up should be an event dialogue")
    require(int(dialogue.get("priority", 0)) >= 60, "Mika old-well follow-up should outrank ordinary dialogue")
    conditions = dialogue.get("conditions", {})
    require(isinstance(conditions, dict), "Mika old-well conditions should be a dictionary")
    require(conditions.get("flag_set") == SOURCE_FLAG, f"Mika follow-up should require {SOURCE_FLAG}")
    require(conditions.get("flag_not_set") == SEEN_FLAG, f"Mika follow-up should stop after {SEEN_FLAG}")
    require(SEEN_FLAG in dialogue.get("sets_flags", []), f"Mika follow-up should set {SEEN_FLAG}")
    require(dialogue.get("lines"), "Mika follow-up should include at least one line")

    require(
        "Mika" in task_text and SOURCE_FLAG in task_text and SEEN_FLAG in task_text,
        "task record should describe Mika source and seen flags",
    )
    print("OK: Mika old-well follow-up static validation passed")


if __name__ == "__main__":
    main()
