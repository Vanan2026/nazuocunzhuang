from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/scenes/world/PlayerYard.tscn": [
        '[node name="ForestTrailGate" type="Area2D" parent="." groups=["interactable"]]',
        'target_scene_id = "forest_edge"',
        'target_spawn_id = "from_yard"',
        'arrival_flag_id = "visited_forest_edge"',
    ],
    "game/scenes/world/ForestEdge.tscn": [
        '[node name="ForestStructure" type="Node2D" parent="."]',
        '[node name="RoutePathNetwork" type="Node2D" parent="ForestStructure"]',
        '[node name="ArrivalReturnPath" type="Polygon2D" parent="ForestStructure/RoutePathNetwork"]',
        '[node name="ShrineResourcePath" type="Polygon2D" parent="ForestStructure/RoutePathNetwork"]',
        '[node name="MikaClearingPath" type="Polygon2D" parent="ForestStructure/RoutePathNetwork"]',
        '[node name="ArrivalTrailZone" type="Polygon2D" parent="ForestStructure"]',
        '[node name="QuietClearingZone" type="Polygon2D" parent="ForestStructure"]',
        '[node name="ResourceCacheZone" type="Polygon2D" parent="ForestStructure"]',
        '[node name="MikaMeetingZone" type="Polygon2D" parent="ForestStructure"]',
        '[node name="ShrineFocusMarker" type="Polygon2D" parent="ForestStructure"]',
        '[node name="ReturnFocusMarker" type="Polygon2D" parent="ForestStructure"]',
    ],
    "tools/validate_forest_edge_gameplay_layout.gd": [
        "forest edge gameplay layout runtime validation passed",
        "_validate_visit_completion_on_travel",
        "_validate_forest_layout_structure",
        "watered_first_crop_day1",
        "harvested_first_crop_day1",
        "shared_first_turnip_day1",
        "planted_aoi_strawberry_day1",
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


def main() -> None:
    for relative_path, snippets in EXPECTED_SNIPPETS.items():
        text = read_text(relative_path)
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                fail(f"{relative_path} contains forbidden gameplay term: {pattern.pattern}")
    print("OK: forest edge gameplay layout static contract validated")


if __name__ == "__main__":
    main()
