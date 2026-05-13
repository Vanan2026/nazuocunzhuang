from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREVIEW_SCENE = ROOT / "scenes" / "dev" / "hunyuan_scene_001_preview.tscn"
TEST_SCENE = ROOT / "scenes" / "dev" / "hunyuan_scene_001_characterbody3d_test.tscn"
WALK_SCRIPT = ROOT / "scripts" / "tools" / "hunyuan_characterbody3d_walk_test.gd"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(cond: bool, message: str) -> None:
    if not cond:
        fail(message)


def main() -> None:
    for path in (PREVIEW_SCENE, TEST_SCENE, WALK_SCRIPT):
        require(path.exists(), f"missing required file: {path}")

    preview = PREVIEW_SCENE.read_text(encoding="utf-8")
    test = TEST_SCENE.read_text(encoding="utf-8")
    script = WALK_SCRIPT.read_text(encoding="utf-8")

    for required in (
        'node name="ImportedVisualRoot"',
        'node name="CollisionProxy"',
        'node name="NavigationRegion3D"',
        'node name="PlayerSpawn"',
        'node name="PreviewCamera"',
        'node name="SunLight"',
        'node name="WorldEnvironment"',
        'node name="BlockerLayer"',
    ):
        require(required in preview, f"preview missing node contract: {required}")

    require("collision_layer = 2" in preview, "preview must include floor collision layer 2")
    require("collision_layer = 4" in preview, "preview must include blocker collision layer 4")
    require("polygons = [PackedInt32Array(" in preview, "navigation mesh polygons were not generated")

    require('node name="TestWalker" type="CharacterBody3D"' in test, "test scene missing CharacterBody3D walker")
    require('node name="NavigationAgent3D" type="NavigationAgent3D" parent="TestWalker"' in test, "test scene missing NavigationAgent3D")
    require("floor_max_angle = 0.837758" in test, "test scene floor_max_angle should be set")
    require("script = ExtResource(\"2_walk_script\")" in test, "test walker script not attached")

    require("collision_mask = 6" in script, "walk test script must set mask for floor+blocker layers")
    require("floor_max_angle = deg_to_rad(floor_max_angle_deg)" in script, "walk test script must configure floor_max_angle")

    waypoint_count = len(re.findall(r'node name="Waypoint_[A-Z]" type="Marker3D"', test))
    require(waypoint_count >= 4, "test scene should provide at least 4 waypoints")

    print("OK: hunyuan CharacterBody3D walk test contract validated")


if __name__ == "__main__":
    main()
