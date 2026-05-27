from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets/art/greenfield_p0/playable_scene_polish"
MANIFEST_PATH = ASSET_DIR / "playable_scene_polish_manifest_v001.json"
STYLE_REFERENCE = "production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg"

EXPECTED_ASSETS = {
    "player_house_warm_room_v001.png": {
        "min_size": 60_000,
        "scene": "game/scenes/home/PlayerHouse.tscn",
        "tokens": [
            'path="res://assets/art/greenfield_p0/playable_scene_polish/player_house_warm_room_v001.png"',
            '[node name="SceneArt" type="Node2D" parent="."]',
            '[node name="WarmRoomBackground" type="Sprite2D" parent="SceneArt"]',
            'texture = ExtResource("8_house_art")',
        ],
    },
    "player_yard_storybook_ground_v001.png": {
        "min_size": 100_000,
        "scene": "game/scenes/world/PlayerYard.tscn",
        "tokens": [
            'path="res://assets/art/greenfield_p0/playable_scene_polish/player_yard_storybook_ground_v001.png"',
            '[node name="SceneArt" type="Node2D" parent="."]',
            '[node name="StorybookGround" type="Sprite2D" parent="SceneArt"]',
            'texture = ExtResource("28_yard_art")',
            "modulate = Color(1, 1, 1, 0.06)",
        ],
    },
    "player_yard_bulletin_board_v001.png": {
        "min_size": 700,
        "scene": "game/scenes/world/PlayerYard.tscn",
        "tokens": [
            'path="res://assets/art/greenfield_p0/playable_scene_polish/player_yard_bulletin_board_v001.png"',
            '[node name="BulletinBoardArt" type="Sprite2D" parent="BulletinBoard"]',
            'texture = ExtResource("29_bulletin_art")',
            '[node name="WoodPileArt" type="Sprite2D" parent="WoodPile"]',
            '[node name="StonePileArt" type="Sprite2D" parent="StonePile"]',
        ],
    },
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


def validate_assets() -> None:
    if not MANIFEST_PATH.is_file():
        fail("missing playable scene polish manifest")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("status") != "runtime_review_ready":
        fail("manifest status must remain runtime_review_ready")
    if manifest.get("launch_quality_approved") is not False:
        fail("playable polish batch must not claim launch-quality approval")
    if manifest.get("human_visual_approval_required") is not True:
        fail("playable polish batch must require human visual approval")
    if manifest.get("style_reference") != STYLE_REFERENCE:
        fail("manifest must point to the current user-provided Greenfield P0 style mother")
    if not (ROOT / STYLE_REFERENCE).is_file():
        fail("missing current Greenfield P0 style mother reference")

    manifest_paths = {str(asset.get("path", "")) for asset in manifest.get("assets", [])}
    for filename, contract in EXPECTED_ASSETS.items():
        asset_path = ASSET_DIR / filename
        if not asset_path.is_file():
            fail(f"missing scene polish asset: {asset_path.relative_to(ROOT)}")
        if asset_path.stat().st_size < int(contract["min_size"]):
            fail(f"scene polish asset is unexpectedly small: {asset_path.relative_to(ROOT)}")
        with Image.open(asset_path) as image:
            width, height = image.size
            if width < 120 or height < 120:
                fail(f"scene polish asset dimensions are too small: {asset_path.relative_to(ROOT)} {image.size}")
            if image.mode != "RGBA":
                fail(f"scene polish asset must be RGBA: {asset_path.relative_to(ROOT)}")
        expected_manifest_path = asset_path.relative_to(ROOT).as_posix()
        if expected_manifest_path not in manifest_paths:
            fail(f"manifest does not register {expected_manifest_path}")


def validate_scene_tokens() -> None:
    for contract in EXPECTED_ASSETS.values():
        scene_path = str(contract["scene"])
        scene_text = read_text(scene_path)
        for token in contract["tokens"]:
            if str(token) not in scene_text:
                fail(f"{scene_path} missing scene polish token: {token}")
        for pattern in FORBIDDEN:
            if pattern.search(scene_text):
                fail(f"{scene_path} contains forbidden gameplay term: {pattern.pattern}")

    house_text = read_text("game/scenes/home/PlayerHouse.tscn")
    yard_text = read_text("game/scenes/world/PlayerYard.tscn")
    if '[node name="RoomBackdrop" type="Polygon2D" parent="."]\nz_index = -40' not in house_text:
        fail("PlayerHouse should keep RoomBackdrop as a low z-index fallback under the new art")
    if '[node name="WorldBackdrop" type="Polygon2D" parent="."]\nz_index = -40' not in yard_text:
        fail("PlayerYard should keep WorldBackdrop as a low z-index fallback under the new art")
    for token in [
        '[node name="RoughEnvironmentSilhouettes" type="Node2D" parent="."]\nvisible = false',
        '[node name="HomeStartGuidance" type="Node2D" parent="."]\nvisible = false',
        '[node name="IntentDeskMarker" type="Polygon2D" parent="IntentDesk"]\nvisible = false',
        '[node name="BulletinBoardMarker" type="Polygon2D" parent="BulletinBoard"]\nvisible = false',
        'scale = Vector2(0.68, 0.68)',
        'scale = Vector2(0.47, 0.47)',
    ]:
        combined = house_text if "0.68" in token or "IntentDesk" in token or "HomeStart" in token or "RoughEnvironment" in token else yard_text
        if token not in combined:
            fail(f"missing placeholder-hide token: {token}")


def main() -> None:
    validate_assets()
    validate_scene_tokens()
    print("OK: playable scene polish assets validate")


if __name__ == "__main__":
    main()
