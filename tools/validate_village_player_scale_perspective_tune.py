from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PLAYER_SCENE = ROOT / "game/entities/player/Player.tscn"
PLAYER_TEXTURE = ROOT / "assets/art/greenfield_p0/characters/player/chr_player_base_idle_down_128.png"
LAYER_MANIFEST = ROOT / "production/assets/regions/village_world2d/v001/03_layer_export/layer_export_manifest.json"
REPORT = ROOT / ".codex/reports/village_object_scale_perspective_review_2026-05-24.md"
TASK_RECORDS = [
    ROOT / ".codex/tasks/open/2026-05-24-village-player-scale-perspective-tune.md",
    ROOT / ".codex/tasks/done/2026-05-24-village-player-scale-perspective-tune.md",
]

TARGET_SCALE_X = (0.36, 0.39)
TARGET_SCALE_Y = (0.39, 0.41)
TARGET_VISIBLE_WIDTH = (19.0, 22.5)
TARGET_VISIBLE_HEIGHT = (37.0, 40.0)
TARGET_FOOT_BOTTOM_Y = (2.5, 4.5)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def extract_player_sprite_block(scene_text: str) -> str:
    marker = '[node name="PlayerSprite" type="AnimatedSprite2D" parent="."]'
    start = scene_text.find(marker)
    require(start >= 0, "Player.tscn missing PlayerSprite node")
    next_node = scene_text.find("\n[node ", start + len(marker))
    if next_node < 0:
        return scene_text[start:]
    return scene_text[start:next_node]


def extract_vector(block: str, key: str) -> tuple[float, float]:
    match = re.search(rf"^{re.escape(key)} = Vector2\(([-0-9.]+), ([-0-9.]+)\)$", block, re.MULTILINE)
    require(match is not None, f"PlayerSprite missing {key} Vector2")
    return float(match.group(1)), float(match.group(2))


def alpha_bbox(texture_path: Path) -> tuple[int, int, int, int]:
    require(texture_path.is_file(), f"missing player texture: {texture_path.relative_to(ROOT)}")
    image = Image.open(texture_path).convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    require(bbox is not None, "player texture alpha appears empty")
    return bbox


def validate_scene_contract() -> None:
    scene_text = read_text(PLAYER_SCENE)
    block = extract_player_sprite_block(scene_text)
    require("PlayerRuntimeFrames.tres" in scene_text, "Player.tscn should use the runtime-sized SpriteFrames resource")
    require('sprite_frames = ExtResource("3_player_frames")' in block, "PlayerSprite should use the declared SpriteFrames resource")

    position_x, position_y = extract_vector(block, "position")
    scale_x, scale_y = extract_vector(block, "scale")
    require(abs(position_x) <= 0.01, "PlayerSprite x anchor should stay centered")
    require(TARGET_SCALE_X[0] <= scale_x <= TARGET_SCALE_X[1], f"PlayerSprite scale.x should be in {TARGET_SCALE_X}, got {scale_x:.3f}")
    require(TARGET_SCALE_Y[0] <= scale_y <= TARGET_SCALE_Y[1], f"PlayerSprite scale.y should be in {TARGET_SCALE_Y}, got {scale_y:.3f}")
    require(scale_x < scale_y, "PlayerSprite should be slightly narrower than tall for Village 3/4 scale readability")

    x0, y0, x1, y1 = alpha_bbox(PLAYER_TEXTURE)
    visible_width = float(x1 - x0) * scale_x
    visible_height = float(y1 - y0) * scale_y
    texture_height = 128.0
    visible_bottom = position_y + (float(y1) - texture_height * 0.5) * scale_y

    require(TARGET_VISIBLE_WIDTH[0] <= visible_width <= TARGET_VISIBLE_WIDTH[1], f"player visible width should be {TARGET_VISIBLE_WIDTH} world units, got {visible_width:.2f}")
    require(TARGET_VISIBLE_HEIGHT[0] <= visible_height <= TARGET_VISIBLE_HEIGHT[1], f"player visible height should be {TARGET_VISIBLE_HEIGHT} world units, got {visible_height:.2f}")
    require(TARGET_FOOT_BOTTOM_Y[0] <= visible_bottom <= TARGET_FOOT_BOTTOM_Y[1], f"player visual foot anchor drifted: {visible_bottom:.2f}")

    require("size = Vector2(20, 28)" in scene_text, "player collision shape should stay unchanged in this visual-scale pass")
    require("radius = 32.0" in scene_text, "player interaction radius should stay unchanged in this visual-scale pass")


def validate_art_state_boundaries() -> None:
    manifest = json.loads(read_text(LAYER_MANIFEST))
    require(manifest.get("runtime_replacement") is False, "Village runtime_replacement must remain false")
    require(manifest.get("launch_quality_approved") is False, "Village launch_quality_approved must remain false")
    report_text = read_text(REPORT)
    require("Player scale and style do not match the Village source" in report_text, "scale review report should record the original blocker")
    task_path = next((path for path in TASK_RECORDS if path.is_file()), None)
    require(task_path is not None, "missing player scale/perspective task record")
    task_text = read_text(task_path)
    require("player visual scale" in task_text.lower() or "player visual-scale" in task_text.lower(), "task should describe the player visual scale tune")


def main() -> None:
    validate_scene_contract()
    validate_art_state_boundaries()
    print("OK: Village player scale and perspective tune validates")


if __name__ == "__main__":
    main()
