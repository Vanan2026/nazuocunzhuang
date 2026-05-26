from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PLAYER_SCENE = ROOT / "game" / "entities" / "player" / "Player.tscn"
PLAYER_TEXTURE = ROOT / "assets" / "art" / "greenfield_p0" / "characters" / "player" / "chr_player_base_idle_down_128.png"
PLAYER_FRAMES = ROOT / "game" / "entities" / "player" / "PlayerRuntimeFrames.tres"
VILLAGE_CAPTURE = ROOT / "tools" / "capture_village_v002_semantic_layer_godot_review.gd"
MOUNTAIN_CAPTURE = ROOT / "tools" / "capture_mountain_hut_semantic_layer_godot_review.gd"
VILLAGE_SCREENSHOT = ROOT / ".codex" / "village_v002_semantic_layer_godot_review" / "06_village_v002_player_scale_focus.png"
MOUNTAIN_SCREENSHOT = ROOT / ".codex" / "mountain_hut_semantic_layer_godot_review" / "05_mountain_hut_player_scale_focus.png"
VILLAGE_REPORT = ROOT / ".codex" / "reports" / "village_v002_semantic_layer_godot_review_2026-05-26.md"
MOUNTAIN_REPORT = ROOT / ".codex" / "reports" / "mountain_hut_semantic_layer_godot_review_2026-05-26.md"

TARGET_BBOX_WIDTH = (48, 62)
TARGET_BBOX_HEIGHT = (90, 104)
MIN_OPAQUE_COLOR_COUNT = 80


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def sprite_block(scene_text: str) -> str:
    marker = '[node name="PlayerSprite" type="AnimatedSprite2D" parent="."]'
    start = scene_text.find(marker)
    require(start >= 0, "Player.tscn missing PlayerSprite")
    next_node = scene_text.find("\n[node ", start + len(marker))
    if next_node < 0:
        return scene_text[start:]
    return scene_text[start:next_node]


def extract_vector(block: str, key: str) -> tuple[float, float]:
    match = re.search(rf"^{re.escape(key)} = Vector2\(([-0-9.]+), ([-0-9.]+)\)$", block, re.MULTILINE)
    require(match is not None, f"PlayerSprite missing {key}")
    return float(match.group(1)), float(match.group(2))


def validate_texture() -> None:
    require(PLAYER_TEXTURE.exists(), f"missing player texture: {PLAYER_TEXTURE.relative_to(ROOT)}")
    image = Image.open(PLAYER_TEXTURE).convert("RGBA")
    require(image.size == (128, 128), f"player texture must stay 128x128, got {image.size}")
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    require(bbox is not None, "player texture alpha is empty")
    x0, y0, x1, y1 = bbox
    width = x1 - x0
    height = y1 - y0
    require(TARGET_BBOX_WIDTH[0] <= width <= TARGET_BBOX_WIDTH[1], f"player alpha width should be {TARGET_BBOX_WIDTH}, got {width}")
    require(TARGET_BBOX_HEIGHT[0] <= height <= TARGET_BBOX_HEIGHT[1], f"player alpha height should be {TARGET_BBOX_HEIGHT}, got {height}")
    image_data = image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()
    opaque_colors = {
        (r, g, b)
        for r, g, b, a in image_data
        if a >= 180
    }
    require(
        len(opaque_colors) >= MIN_OPAQUE_COLOR_COUNT,
        f"player texture still reads too flat for current art review: {len(opaque_colors)} opaque colors",
    )


def validate_scene() -> None:
    scene_text = read(PLAYER_SCENE)
    block = sprite_block(scene_text)
    require(PLAYER_FRAMES.exists(), f"missing player SpriteFrames resource: {PLAYER_FRAMES.relative_to(ROOT)}")
    require("PlayerRuntimeFrames.tres" in scene_text, "Player scene must use the runtime-sized SpriteFrames resource")
    require('sprite_frames = ExtResource("3_player_frames")' in block, "PlayerSprite must use the declared SpriteFrames resource")
    position = extract_vector(block, "position")
    scale = extract_vector(block, "scale")
    require(abs(position[0]) <= 0.01, "PlayerSprite x anchor should stay centered")
    require(-17.0 <= position[1] <= -15.0, f"PlayerSprite y anchor drifted: {position[1]:.2f}")
    require(0.36 <= scale[0] <= 0.40, f"PlayerSprite scale.x drifted: {scale[0]:.3f}")
    require(0.38 <= scale[1] <= 0.42, f"PlayerSprite scale.y drifted: {scale[1]:.3f}")
    require("size = Vector2(20, 28)" in scene_text, "visual pass must not change player collision shape")
    require("radius = 32.0" in scene_text, "visual pass must not change interaction radius")


def validate_capture_contracts() -> None:
    village_text = read(VILLAGE_CAPTURE)
    mountain_text = read(MOUNTAIN_CAPTURE)
    for token in [
        '"06_village_v002_player_scale_focus.png"',
        "_capture_player_scale_focus",
        "player_scale_focus",
    ]:
        require(token in village_text, f"Village v002 capture missing player scale token: {token}")
    for token in [
        '"05_mountain_hut_player_scale_focus.png"',
        "_capture_player_scale_focus",
        "player_scale_focus",
    ]:
        require(token in mountain_text, f"MountainHut capture missing player scale token: {token}")


def validate_evidence() -> None:
    village_report = read(VILLAGE_REPORT)
    mountain_report = read(MOUNTAIN_REPORT)
    for screenshot in [VILLAGE_SCREENSHOT, MOUNTAIN_SCREENSHOT]:
        require(screenshot.exists(), f"missing player scale screenshot: {screenshot.relative_to(ROOT)}")
        require(screenshot.stat().st_size > 20_000, f"player scale screenshot unexpectedly small: {screenshot.relative_to(ROOT)}")
    require("player-scale focus" in village_report, "Village report must mention the player-scale focus evidence")
    require("player-scale focus" in mountain_report, "MountainHut report must mention the player-scale focus evidence")
    require("runtime_replacement=false" in village_report, "Village report must keep runtime replacement blocked")
    require("runtime_replacement=false" in mountain_report, "MountainHut report must keep runtime replacement blocked")


def main() -> None:
    validate_texture()
    validate_scene()
    validate_capture_contracts()
    validate_evidence()
    print("OK: current player art review gate validates")


if __name__ == "__main__":
    main()
