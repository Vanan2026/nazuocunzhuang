from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STYLE_REFERENCE = "production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg"
CANVAS_SIZE = (1920, 1080)

ASSETS = {
    "mother": "assets/scenes/home_area/scene_home_area_mother.png",
    "base": "assets/scenes/home_area/scene_home_area_base.png",
    "foreground_occlusion": "assets/scenes/home_area/scene_home_area_foreground_occlusion.png",
    "collision_mask": "assets/scenes/home_area/scene_home_area_collision_mask.png",
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


def _validate_image_assets() -> None:
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
    if tuple(manifest.get("canvas_size", [])) != CANVAS_SIZE:
        _fail("HomeArea manifest canvas size mismatch")

    for key, relative_path in ASSETS.items():
        if manifest.get("assets", {}).get(key) != relative_path:
            _fail(f"manifest missing or mismatched asset for {key}")
        path = ROOT / relative_path
        if not path.is_file():
            _fail(f"missing HomeArea asset: {relative_path}")
        with Image.open(path) as image:
            if image.size != CANVAS_SIZE:
                _fail(f"{relative_path} must be full-canvas {CANVAS_SIZE}, got {image.size}")
            if image.mode != "RGBA":
                _fail(f"{relative_path} must be RGBA")

    with Image.open(ROOT / ASSETS["foreground_occlusion"]) as foreground:
        alpha = foreground.getchannel("A")
        opaque_pixels = sum(1 for value in alpha.getdata() if value > 8)
        if opaque_pixels < 10000:
            _fail("foreground occlusion has too few alpha pixels")
        if opaque_pixels > CANVAS_SIZE[0] * CANVAS_SIZE[1] * 0.35:
            _fail("foreground occlusion is too broad for an occlusion layer")

    with Image.open(ROOT / ASSETS["collision_mask"]) as mask:
        alpha = mask.getchannel("A")
        blocked_pixels = sum(1 for value in alpha.getdata() if value > 128)
        if blocked_pixels < 30000:
            _fail("collision mask has too few blocked pixels")
        if blocked_pixels > CANVAS_SIZE[0] * CANVAS_SIZE[1] * 0.45:
            _fail("collision mask is too broad")


def _validate_interaction_points() -> None:
    path = ROOT / "assets/scenes/home_area/scene_home_area_interaction_points.json"
    if not path.is_file():
        _fail("missing HomeArea interaction points JSON")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("style_reference") != STYLE_REFERENCE:
        _fail("interaction points must reference style mother")
    if tuple(data.get("canvas_size", [])) != CANVAS_SIZE:
        _fail("interaction points must use the full HomeArea canvas")
    if data.get("coordinate_space") != "shared_full_canvas_origin_top_left":
        _fail("interaction points must declare shared canvas coordinate space")
    ids = {point.get("id") for point in data.get("points", [])}
    if not REQUIRED_INTERACTIONS.issubset(ids):
        _fail(f"interaction points missing ids: {sorted(REQUIRED_INTERACTIONS - ids)}")
    for point in data.get("points", []):
        position = point.get("position", [])
        if len(position) != 2:
            _fail(f"interaction point {point.get('id')} missing position")
        x, y = float(position[0]), float(position[1])
        if not (0.0 <= x <= CANVAS_SIZE[0] and 0.0 <= y <= CANVAS_SIZE[1]):
            _fail(f"interaction point {point.get('id')} outside canvas")
        if not point.get("hint") or not point.get("text"):
            _fail(f"interaction point {point.get('id')} needs hint and text")


def _validate_scene_files() -> None:
    scene_text = _read("game/scenes/world/HomeArea.tscn")
    for token in [
        "BaseSprite",
        "BaseLayer",
        "YSortObjects",
        "ForegroundOcclusion",
        "CollisionLayer",
        "InteractionPoints",
        "NavigationRegion2D",
        "PlayerSpawnPoint",
        "scene_home_area_base.png",
        "scene_home_area_foreground_occlusion.png",
        "scene_home_area_mother.png",
        "home_door",
        "old_well",
        "mailbox",
        "farm_plot_cluster",
        "res://game/entities/player/Player.tscn",
    ]:
        if token not in scene_text:
            _fail(f"HomeArea scene missing token: {token}")

    script_text = _read("game/scenes/world/HomeArea.gd")
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
    _validate_image_assets()
    _validate_interaction_points()
    _validate_scene_files()
    print("OK: Greenfield P0 HomeArea scene package validates")


if __name__ == "__main__":
    main()
