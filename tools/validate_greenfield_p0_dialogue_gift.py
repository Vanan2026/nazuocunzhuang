from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SCENE_TOKENS = [
    "DialogueScreen",
    "visible = false",
    "res://game/scenes/ui/DialogueBox.gd",
    "res://ui/theme/greenfield_theme.tres",
    "Portrait",
    "SpeakerLabel",
    "LineLabel",
    "OptionRow",
    "GiftSelection",
    "GiftGrid",
    "RelationshipFeedback",
    "FeedbackTitleLabel",
    "FeedbackLineLabel",
    "FeedbackDeltaLabel",
]

REQUIRED_DIALOGUE_SCRIPT_TOKENS = [
    "func bind_managers(",
    "func show_gift_selection(",
    "func hide_gift_selection()",
    "func _show_gift_feedback(",
    "GiftSelection/Content/GiftGrid",
    "RelationshipFeedback/Content/FeedbackLineLabel",
    "GreenfieldUITheme.apply_item_slot",
    "GreenfieldUITheme.apply_surface_panel(gift_selection_panel)",
]

REQUIRED_NPC_TOKENS = [
    "func _get_gift_rule(",
    "get_gift_response",
    "relationship_delta",
    "feedback_text",
]

REQUIRED_REGISTRY_TOKENS = [
    '"gifts": {"path": "res://game/data/gifts.json", "id_key": "gift_id"}',
    "var gifts: Dictionary = {}",
    "func get_gift_response(",
    "func _validate_gifts()",
]

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


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _fail(message: str) -> None:
    raise AssertionError(message)


def _assert_contains(path: str, tokens: list[str]) -> None:
    text = _read(path)
    for token in tokens:
        if token not in text:
            _fail(f"{path} missing token: {token}")
    for pattern in FORBIDDEN:
        if pattern.search(text):
            _fail(f"{path} contains forbidden gameplay term: {pattern.pattern}")


def _load_json_array(relative_path: str) -> list[dict]:
    path = ROOT / relative_path
    if not path.exists():
        _fail(f"missing JSON file: {relative_path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        _fail(f"{relative_path} must contain a JSON array")
    return data


def _validate_gifts_data() -> None:
    npcs = {record["npc_id"] for record in _load_json_array("game/data/npcs.json")}
    items = {record["item_id"] for record in _load_json_array("game/data/items.json")}
    gifts = _load_json_array("game/data/gifts.json")
    if len(gifts) < 8:
        _fail("gifts.json should define at least 8 P0 gift response rows")

    seen: set[str] = set()
    reactions = set()
    for gift in gifts:
        for field in ["gift_id", "npc_id", "item_id", "reaction", "relationship_delta", "feedback_text"]:
            if field not in gift:
                _fail(f"gift record missing field: {field}")
        gift_id = str(gift["gift_id"])
        if gift_id in seen:
            _fail(f"duplicate gift_id: {gift_id}")
        seen.add(gift_id)
        if str(gift["npc_id"]) not in npcs:
            _fail(f"{gift_id} references missing npc: {gift['npc_id']}")
        if str(gift["item_id"]) not in items:
            _fail(f"{gift_id} references missing item: {gift['item_id']}")
        reaction = str(gift["reaction"])
        if reaction not in {"loved", "liked", "neutral", "disliked"}:
            _fail(f"{gift_id} has invalid reaction: {reaction}")
        reactions.add(reaction)
        int(gift["relationship_delta"])
        if not str(gift["feedback_text"]).strip():
            _fail(f"{gift_id} feedback_text should not be empty")

    if not {"loved", "liked", "neutral"} <= reactions:
        _fail("gifts.json should cover loved, liked, and neutral feedback states")


def main() -> None:
    _assert_contains("game/scenes/ui/DialogueScreen.tscn", REQUIRED_SCENE_TOKENS)
    _assert_contains("game/scenes/ui/DialogueBox.gd", REQUIRED_DIALOGUE_SCRIPT_TOKENS)
    _assert_contains("game/entities/npc/NPC.gd", REQUIRED_NPC_TOKENS)
    _assert_contains("game/autoload/DataRegistry.gd", REQUIRED_REGISTRY_TOKENS)
    _validate_gifts_data()
    print("OK: Greenfield P0 Dialogue + Gift static validation passed")


if __name__ == "__main__":
    main()
