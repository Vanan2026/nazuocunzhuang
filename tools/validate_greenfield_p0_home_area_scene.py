from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STYLE_REFERENCE = "production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg"

REQUIRED_COMPONENTS = {
    "home_house_body_01": ((640, 512), True),
    "home_house_roof_01": ((640, 512), True),
    "home_well_01": ((256, 256), True),
    "home_mailbox_01": ((128, 128), True),
    "home_fence_horizontal_01": ((256, 128), True),
    "home_fence_vertical_01": ((128, 256), True),
    "home_fence_corner_01": ((192, 192), True),
    "home_garden_plot_grown_01": ((512, 384), True),
    "home_tree_large_01": ((512, 512), True),
    "home_bush_flower_01": ((192, 160), True),
    "home_table_wood_01": ((256, 192), True),
    "home_bridge_wood_01": ((384, 256), True),
}

REQUIRED_INTERACTIONS = {"home_door", "old_well", "mailbox", "farm_plot_cluster"}

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


def _fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def _read(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        _fail(f"missing file: {relative_path}")
    return path.read_text(encoding="utf-8")


def _validate_component_manifest() -> None:
    manifest_path = ROOT / "assets/scenes/home_area/home_area_scene_manifest_v001.json"
    if not manifest_path.is_file():
        _fail("missing HomeArea scene manifest")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if manifest.get("style_reference") != STYLE_REFERENCE:
        _fail("HomeArea manifest must reference the current style mother")
    if manifest.get("launch_quality_approved") is not False:
        _fail("HomeArea package must not claim launch approval")
    if manifest.get("human_visual_approval_required") is not True:
        _fail("HomeArea package must require human visual approval")
    if manifest.get("workflow") != "component_based_godot_assembly":
        _fail("HomeArea manifest must use component_based_godot_assembly workflow")

    components = manifest.get("components", {})
    for component_id, (expected_size, expected_transparent) in REQUIRED_COMPONENTS.items():
        record = components.get(component_id)
        if record is None:
            _fail(f"manifest missing component: {component_id}")
        if tuple(record.get("expected_size", [])) != expected_size:
            _fail(f"{component_id} expected_size mismatch")
        if bool(record.get("transparent")) != expected_transparent:
            _fail(f"{component_id} transparency flag mismatch")

        runtime_path = record.get("runtime_path")
        if not runtime_path:
            _fail(f"{component_id} missing runtime_path")

        path = ROOT / runtime_path
        # Component files may be pending generation. If they already exist, validate hard image requirements.
        if path.is_file():
            with Image.open(path) as image:
                if image.size != expected_size:
                    _fail(f"{runtime_path} must be {expected_size}, got {image.size}")
                if expected_transparent and image.mode != "RGBA":
                    _fail(f"{runtime_path} must be RGBA")


def _validate_interaction_points() -> None:
    path = ROOT / "assets/scenes/home_area/scene_home_area_interaction_points.json"
    if not path.is_file():
        _fail("missing HomeArea interaction points JSON")

    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("style_reference") != STYLE_REFERENCE:
        _fail("interaction points must reference style mother")

    ids = {point.get("id") for point in data.get("points", [])}
    if not REQUIRED_INTERACTIONS.issubset(ids):
        _fail(f"interaction points missing ids: {sorted(REQUIRED_INTERACTIONS - ids)}")

    for point in data.get("points", []):
        position = point.get("position", [])
        if len(position) != 2:
            _fail(f"interaction point {point.get('id')} missing position")
        if not point.get("hint") or not point.get("text"):
            _fail(f"interaction point {point.get('id')} needs hint and text")


def _validate_scene_files() -> None:
    scene_text = _read("game/scenes/world/HomeArea.tscn")
    script_text = _read("game/scenes/world/HomeArea.gd")

    for token in [
        "YSortObjects",
        "CollisionLayer",
        "InteractionPoints",
        "NavigationRegion2D",
        "PlayerSpawnPoint",
        "home_door",
        "old_well",
        "mailbox",
        "farm_plot_cluster",
        "res://game/entities/player/Player.tscn",
    ]:
        if token not in scene_text:
            _fail(f"HomeArea scene missing token: {token}")

    for token in [
        "class_name HomeArea",
        "interaction_points_path",
        "get_registered_interaction_ids",
        "load_interaction_points_data",
    ]:
        if token not in script_text:
            _fail(f"HomeArea script missing token: {token}")

    combined = scene_text + "\n" + script_text
    for pattern in FORBIDDEN:
        if pattern.search(combined):
            _fail(f"HomeArea files contain forbidden gameplay term: {pattern.pattern}")


def main() -> None:
    _validate_component_manifest()
    _validate_interaction_points()
    _validate_scene_files()
    print("OK: Greenfield P0 HomeArea component package validates")


if __name__ == "__main__":
    main()
