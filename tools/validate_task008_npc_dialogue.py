from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES: dict[str, list[str]] = {
    "game/entities/npc/NPC.gd": [
        "class_name NPC",
        "extends \"res://game/entities/interactable/Interactable.gd\"",
        "npc_id",
        "dialogue_manager_path",
        "relationship_manager_path",
        "func configure_from_data(",
        "func on_interact(",
    ],
    "game/entities/npc/NPC.tscn": [
        '[node name="NPC" type="Area2D"',
        "res://game/entities/npc/NPC.gd",
        '[node name="Sprite2D"',
        '[node name="CollisionShape2D"',
    ],
    "game/scenes/ui/DialogueBox.gd": [
        "class_name DialogueBox",
        "extends CanvasLayer",
        "func show_dialogue(",
        "func advance(",
        "func close(",
    ],
    "game/scenes/ui/DialogueBox.tscn": [
        '[node name="DialogueBox" type="CanvasLayer"]',
        "res://game/scenes/ui/DialogueBox.gd",
        '[node name="Portrait"',
        '[node name="SpeakerLabel"',
        '[node name="LineLabel"',
    ],
    "game/autoload/DialogueManager.gd": [
        "const TYPE_PRIORITY",
        "func bind_registry(",
        "func get_dialogue(",
        "func start_dialogue(",
        "func finish_dialogue(",
        "sets_flags",
        "flag_not_set",
    ],
    "game/scenes/world/PlayerYard.tscn": [
        "res://game/entities/npc/NPC.tscn",
        "res://game/scenes/ui/DialogueBox.tscn",
        '[node name="DialogueManager"',
        '[node name="RelationshipManager"',
        '[node name="DialogueBox"',
        '[node name="NPCs"',
        '[node name="Aoi"',
        '[node name="Gen"',
        '[node name="Mika"',
    ],
}

EXPECTED_ASSETS = [
    "assets/art/characters/npc/npc_aoi_idle_down_128.png",
    "assets/art/characters/npc/npc_gen_idle_down_128.png",
    "assets/art/characters/npc/npc_mika_idle_down_128.png",
    "assets/art/portraits/npc_aoi_portrait_neutral_512.png",
    "assets/art/portraits/npc_gen_portrait_neutral_512.png",
    "assets/art/portraits/npc_mika_portrait_neutral_512.png",
    "assets/art/icons/weather_sunny_64.png",
    "assets/art/icons/weather_cloudy_64.png",
    "assets/art/icons/weather_rainy_64.png",
    "assets/art/ui/ui_panel_paper_256x128.png",
    "assets/art/ui/ui_button_wood_128x48.png",
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


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def load_json_array(relative_path: str) -> list[dict[str, Any]]:
    path = ROOT / relative_path
    if not path.is_file():
        fail(f"missing JSON file: {relative_path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        fail(f"{relative_path} must contain a JSON array")
    return data


def main() -> None:
    for relative_path, snippets in EXPECTED_FILES.items():
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

    npcs = {record["npc_id"]: record for record in load_json_array("game/data/npcs.json")}
    for npc_id in ["aoi", "gen", "mika"]:
        if npc_id not in npcs:
            fail(f"game/data/npcs.json missing required NPC: {npc_id}")
        portrait = str(npcs[npc_id].get("portrait", ""))
        if not portrait.startswith("res://assets/art/portraits/"):
            fail(f"NPC {npc_id} portrait should point at runtime portraits: {portrait}")

    dialogues = load_json_array("game/data/dialogues.json")
    dialogue_types_by_npc: dict[str, set[str]] = {"aoi": set(), "gen": set(), "mika": set()}
    for dialogue in dialogues:
        npc_id = str(dialogue.get("npc_id", ""))
        if npc_id in dialogue_types_by_npc:
            dialogue_types_by_npc[npc_id].add(str(dialogue.get("type", "")))
    for npc_id, types in dialogue_types_by_npc.items():
        if not ({"daily", "fallback"} <= types):
            fail(f"NPC {npc_id} needs at least daily and fallback dialogue, got {sorted(types)}")

    crops = load_json_array("game/data/crops.json")
    for crop in crops:
        for sprite_path in crop.get("stage_sprites", []):
            relative = str(sprite_path).replace("res://", "")
            if not (ROOT / relative).is_file():
                fail(f"missing crop stage sprite for {crop['crop_id']}: {sprite_path}")

    for relative_path in EXPECTED_ASSETS:
        if not (ROOT / relative_path).is_file():
            fail(f"missing Batch E/runtime asset: {relative_path}")

    print("OK: validated Task 008 NPC/Dialogue and Batch E file contract")


if __name__ == "__main__":
    main()
