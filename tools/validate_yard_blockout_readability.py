from __future__ import annotations

import json
import re
import sys
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/scenes/world/PlayerYard.tscn": [
        '[node name="YardStructure" type="Node2D" parent="."]',
        "polygon = PackedVector2Array(-360, -220, 640, -220, 640, 460, -360, 460)",
        '[node name="HomeApproachZone" type="Polygon2D" parent="YardStructure"]',
        '[node name="RoutePathNetwork" type="Node2D" parent="YardStructure"]',
        '[node name="MailboxNoticeRepairPath" type="Polygon2D" parent="YardStructure/RoutePathNetwork"]',
        '[node name="RepairForestPath" type="Polygon2D" parent="YardStructure/RoutePathNetwork"]',
        '[node name="FarmBranchPath" type="Polygon2D" parent="YardStructure/RoutePathNetwork"]',
        '[node name="ResourceBranchPath" type="Polygon2D" parent="YardStructure/RoutePathNetwork"]',
        '[node name="FirstStepGuidance" type="Node2D" parent="YardStructure"]',
        '[node name="SpawnMailboxPath" type="Polygon2D" parent="YardStructure/FirstStepGuidance"]',
        '[node name="MailboxFocusMarker" type="Polygon2D" parent="YardStructure/FirstStepGuidance"]',
        '[node name="SocialNoticeZone" type="Polygon2D" parent="YardStructure"]',
        '[node name="FarmGardenZone" type="Polygon2D" parent="YardStructure"]',
        '[node name="RepairYardZone" type="Polygon2D" parent="YardStructure"]',
        '[node name="ForestTrailZone" type="Polygon2D" parent="YardStructure"]',
        '[node name="ResourceStagingZone" type="Polygon2D" parent="YardStructure"]',
        '[node name="Hana" parent="NPCs"',
        "visible = false",
        "monitoring = false",
    ],
    "game/entities/npc/NPC.tscn": [
        '[node name="Sprite2D" type="Sprite2D" parent="."]',
        "scale = Vector2(0.45, 0.45)",
        '[node name="NameLabel" type="Label" parent="."]',
        "visible = false",
        "offset_top = -72.0",
    ],
    "game/scenes/ui/InventoryUI.tscn": [
        '[node name="InventoryUI" type="CanvasLayer"]',
        "visible = false",
    ],
    "game/scenes/ui/DialogueBox.tscn": [
        '[node name="DialogueBox" type="CanvasLayer"]',
        "offset_left = 24.0",
        "offset_top = 588.0",
        "offset_right = 620.0",
        "offset_bottom = 708.0",
    ],
    "game/scenes/world/PlayerYard.gd": [
        "func toggle_inventory_panel(",
        'Input.is_action_just_pressed("open_inventory")',
    ],
    "game/systems/npc/NpcScheduleDirector.gd": [
        'String(entry.get("time_block", "")) == block',
        "return {}",
    ],
    "tools/validate_yard_blockout_readability.gd": [
        "yard blockout readability runtime validation passed",
        "_validate_layout_relationships",
        "_validate_npc_schedule_readability",
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


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        fail(f"missing file: {relative_path}")
    return path.read_text(encoding="utf-8")


def validate_snippets() -> None:
    for relative_path, snippets in EXPECTED_SNIPPETS.items():
        text = read_text(relative_path)
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                fail(f"{relative_path} contains forbidden gameplay term: {pattern.pattern}")


def validate_schedule_spacing() -> None:
    path = ROOT / "game/data/npc_schedules.json"
    schedules = json.loads(path.read_text(encoding="utf-8"))
    by_block: dict[str, list[tuple[str, tuple[float, float]]]] = {}
    for schedule in schedules:
        schedule_id = str(schedule.get("schedule_id", ""))
        for entry in schedule.get("entries", []):
            if entry.get("scene_id") != "player_yard":
                continue
            block = str(entry.get("time_block", ""))
            position = entry.get("position", [])
            if not isinstance(position, list) or len(position) != 2:
                fail(f"{schedule_id}/{block} has invalid player_yard position")
            x, y = float(position[0]), float(position[1])
            if not (-80 <= x <= 360 and 40 <= y <= 250):
                fail(f"{schedule_id}/{block} position outside readable yard bounds: {position}")
            by_block.setdefault(block, []).append((schedule_id, (x, y)))

    for block, records in by_block.items():
        for (left_id, left_pos), (right_id, right_pos) in combinations(records, 2):
            distance = ((left_pos[0] - right_pos[0]) ** 2 + (left_pos[1] - right_pos[1]) ** 2) ** 0.5
            if distance < 64:
                fail(f"player_yard {block} schedule positions too close: {left_id} vs {right_id} ({distance:.1f}px)")


def main() -> None:
    validate_snippets()
    validate_schedule_spacing()
    print("OK: yard blockout readability static contract validated")


if __name__ == "__main__":
    main()
