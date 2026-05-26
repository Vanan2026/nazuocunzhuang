from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/scenes/home/PlayerHouse.tscn": [
        '[node name="RoughEnvironmentSilhouettes" type="Node2D" parent="."]',
        '[node name="WarmFloorWash" type="Polygon2D" parent="RoughEnvironmentSilhouettes"]',
        '[node name="PorchDoorMatShape" type="Polygon2D" parent="RoughEnvironmentSilhouettes"]',
        '[node name="WindowLightPatch" type="Polygon2D" parent="RoughEnvironmentSilhouettes"]',
    ],
    "game/scenes/world/PlayerYard.tscn": [
        '[node name="RoughEnvironmentSilhouettes" type="Node2D" parent="YardStructure"]',
        '[node name="HomePorchApronShape" type="Polygon2D" parent="YardStructure/RoughEnvironmentSilhouettes"]',
        '[node name="MailboxFootpathShape" type="Polygon2D" parent="YardStructure/RoughEnvironmentSilhouettes"]',
        '[node name="GardenSoilPatchShape" type="Polygon2D" parent="YardStructure/RoughEnvironmentSilhouettes"]',
        '[node name="RepairCornerGrassShape" type="Polygon2D" parent="YardStructure/RoughEnvironmentSilhouettes"]',
        '[node name="ForestEdgeBrushShape" type="Polygon2D" parent="YardStructure/RoughEnvironmentSilhouettes"]',
    ],
    "game/scenes/world/ForestEdge.tscn": [
        '[node name="RoughEnvironmentSilhouettes" type="Node2D" parent="ForestStructure"]',
        '[node name="TreeLineBackShape" type="Polygon2D" parent="ForestStructure/RoughEnvironmentSilhouettes"]',
        '[node name="LeafFloorPatchShape" type="Polygon2D" parent="ForestStructure/RoughEnvironmentSilhouettes"]',
        '[node name="ShrineRootMassShape" type="Polygon2D" parent="ForestStructure/RoughEnvironmentSilhouettes"]',
        '[node name="ReturnTrailBrushShape" type="Polygon2D" parent="ForestStructure/RoughEnvironmentSilhouettes"]',
    ],
    "tools/validate_rough_environment_silhouettes.gd": [
        "rough environment silhouette runtime validation passed",
        "_validate_scene_silhouettes",
        "_validate_polygon_points",
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
    print("OK: rough environment silhouette static contract validated")


if __name__ == "__main__":
    main()
