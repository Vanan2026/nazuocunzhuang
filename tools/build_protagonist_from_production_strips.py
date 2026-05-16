from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
FINAL_STRIP_DIR = ROOT / "production" / "assets" / "protagonist" / "final_source_strips"
OUT_DIR = ROOT / "sprites" / "characters" / "protagonist" / "frames"
SPRITE_FRAMES = ROOT / "sprites" / "characters" / "protagonist" / "player_mvp_4dir_frames.tres"
MOTION_PREVIEW = ROOT / ".codex" / "protagonist_redesign_motion_preview.png"
RUNTIME_SCENE_PREVIEW = ROOT / ".codex" / "protagonist_redesign_runtime_scene_preview.png"
LEGACY_PREVIEW = ROOT / ".codex" / "protagonist_mvp_animation_preview.png"
SCENE_BG = ROOT / "resources" / "design" / "CloudVillageHomeyard_no_character_master.png"

SOURCE_SLOT_SIZE = (384, 576)
FRAME_SIZE = (192, 288)
FOOT_BASELINE_Y = 270


@dataclass(frozen=True)
class RowSpec:
    animation: str
    loop: bool
    speed: float
    expected: int


ROWS = [
    RowSpec("player_walk_down", True, 6.0, 8),
    RowSpec("player_walk_down_left", True, 6.0, 8),
    RowSpec("player_walk_left", True, 6.0, 8),
    RowSpec("player_walk_up_left", True, 6.0, 8),
    RowSpec("player_walk_up", True, 6.0, 8),
    RowSpec("player_walk_up_right", True, 6.0, 8),
    RowSpec("player_walk_right", True, 6.0, 8),
    RowSpec("player_walk_down_right", True, 6.0, 8),
    RowSpec("player_idle_down", True, 4.2, 4),
    RowSpec("player_idle_down_left", True, 4.2, 4),
    RowSpec("player_idle_left", True, 4.2, 4),
    RowSpec("player_idle_up_left", True, 4.2, 4),
    RowSpec("player_idle_up", True, 4.2, 4),
    RowSpec("player_idle_up_right", True, 4.2, 4),
    RowSpec("player_idle_right", True, 4.2, 4),
    RowSpec("player_idle_down_right", True, 4.2, 4),
    RowSpec("player_interact_down", False, 8.0, 6),
    RowSpec("player_interact_down_left", False, 8.0, 6),
    RowSpec("player_interact_left", False, 8.0, 6),
    RowSpec("player_interact_up_left", False, 8.0, 6),
    RowSpec("player_interact_up", False, 8.0, 6),
    RowSpec("player_interact_up_right", False, 8.0, 6),
    RowSpec("player_interact_right", False, 8.0, 6),
    RowSpec("player_interact_down_right", False, 8.0, 6),
    RowSpec("player_sit_down_side", False, 7.0, 6),
    RowSpec("player_sit_down_down", False, 7.0, 6),
    RowSpec("player_sit_down_up", False, 7.0, 6),
    RowSpec("player_sit_idle_side", True, 4.2, 6),
    RowSpec("player_sit_idle_down", True, 4.2, 6),
    RowSpec("player_sit_idle_up", True, 4.2, 6),
    RowSpec("player_stand_up_side", False, 7.0, 6),
    RowSpec("player_stand_up_down", False, 7.0, 6),
    RowSpec("player_stand_up_up", False, 7.0, 6),
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def alpha_bounds(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = np.array(image.convert("RGBA"))[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        fail("empty source slot")
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def align_baseline(image: Image.Image) -> Image.Image:
    x1, y1, x2, y2 = alpha_bounds(image)
    dy = FOOT_BASELINE_Y - y2
    if dy == 0:
        out = image.copy()
    else:
        out = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
        out.alpha_composite(image, (0, dy))
    pixels = out.load()
    for y in range(FOOT_BASELINE_Y + 1, FRAME_SIZE[1]):
        for x in range(FRAME_SIZE[0]):
            pixels[x, y] = (0, 0, 0, 0)
    return out


def import_strip(spec: RowSpec) -> list[Image.Image]:
    path = FINAL_STRIP_DIR / f"{spec.animation}_source_strip.png"
    if not path.exists():
        fail(f"missing source strip: {path}")
    strip = Image.open(path).convert("RGBA")
    expected_size = (SOURCE_SLOT_SIZE[0] * spec.expected, SOURCE_SLOT_SIZE[1])
    if strip.size != expected_size:
        fail(f"{path.name} must be {expected_size}, got {strip.size}")

    frames: list[Image.Image] = []
    for idx in range(spec.expected):
        crop = strip.crop((idx * SOURCE_SLOT_SIZE[0], 0, (idx + 1) * SOURCE_SLOT_SIZE[0], SOURCE_SLOT_SIZE[1]))
        frame = crop.resize(FRAME_SIZE, Image.Resampling.LANCZOS)
        frames.append(align_baseline(frame))
    return frames


def write_frames(animation_frames: dict[str, list[Image.Image]]) -> dict[str, list[Path]]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.png"):
        old.unlink()

    written: dict[str, list[Path]] = {}
    for spec in ROWS:
        frames = animation_frames.get(spec.animation)
        if frames is None or len(frames) != spec.expected:
            fail(f"{spec.animation} expected {spec.expected} frames")
        paths: list[Path] = []
        for idx, frame in enumerate(frames):
            out = OUT_DIR / f"{spec.animation}_{idx:02d}.png"
            frame.save(out)
            paths.append(out)
        written[spec.animation] = paths
    return written


def build_tres(frame_paths: dict[str, list[Path]]) -> None:
    resources: list[str] = []
    resource_ids: dict[str, str] = {}
    index = 1
    for spec in ROWS:
        for path in frame_paths[spec.animation]:
            key = f"frame_{index}"
            rel = path.relative_to(ROOT).as_posix()
            resources.append(f'[ext_resource type="Texture2D" path="res://{rel}" id="{key}"]')
            resource_ids[str(path)] = key
            index += 1

    animations: list[str] = []
    for spec in ROWS:
        frames = []
        for path in frame_paths[spec.animation]:
            key = resource_ids[str(path)]
            frames.append('{\n"duration": 1.0,\n"texture": ExtResource("%s")\n}' % key)
        animations.append(
            '{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %.1f\n}'
            % (", ".join(frames), "true" if spec.loop else "false", spec.animation, spec.speed)
        )

    text = '[gd_resource type="SpriteFrames" load_steps=%d format=3]\n\n%s\n\n[resource]\nanimations = [%s]\n' % (
        len(resources) + 1,
        "\n".join(resources),
        ", ".join(animations),
    )
    SPRITE_FRAMES.write_text(text, encoding="utf-8")


def write_motion_preview(frame_paths: dict[str, list[Path]]) -> None:
    label_w = 210
    cols = 8
    cell_w, cell_h = FRAME_SIZE
    canvas = Image.new("RGBA", (label_w + cols * cell_w, len(ROWS) * cell_h), (244, 239, 226, 255))
    draw = ImageDraw.Draw(canvas)
    for row_idx, spec in enumerate(ROWS):
        y = row_idx * cell_h
        draw.text((8, y + 12), spec.animation, fill=(38, 35, 30, 255))
        paths = frame_paths[spec.animation]
        for idx in range(cols):
            path = paths[idx % len(paths)]
            x = label_w + idx * cell_w
            canvas.alpha_composite(Image.open(path).convert("RGBA"), (x, y))
            draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(190, 180, 160, 150))
            draw.line((x, y + FOOT_BASELINE_Y, x + cell_w, y + FOOT_BASELINE_Y), fill=(210, 90, 70, 115))
    MOTION_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(MOTION_PREVIEW)
    canvas.save(LEGACY_PREVIEW)


def write_runtime_scene_preview(frame_paths: dict[str, list[Path]]) -> None:
    if SCENE_BG.exists():
        bg = Image.open(SCENE_BG).convert("RGBA").resize((1280, 720), Image.Resampling.LANCZOS)
    else:
        bg = Image.new("RGBA", (1280, 720), (202, 213, 184, 255))
    player = Image.open(frame_paths["player_idle_down"][0]).convert("RGBA")
    scale = 0.92
    scaled = player.resize((int(player.width * scale), int(player.height * scale)), Image.Resampling.LANCZOS)
    foot = (548, 540)
    pos = (int(foot[0] - 96 * scale), int(foot[1] - FOOT_BASELINE_Y * scale))
    bg.alpha_composite(scaled, pos)
    draw = ImageDraw.Draw(bg, "RGBA")
    draw.line((foot[0] - 70, foot[1], foot[0] + 70, foot[1]), fill=(185, 78, 62, 130), width=1)
    RUNTIME_SCENE_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    bg.save(RUNTIME_SCENE_PREVIEW)


def verify_names() -> None:
    for spec in ROWS:
        pattern = re.compile(rf"^{re.escape(spec.animation)}_source_strip\.png$")
        matches = [path.name for path in FINAL_STRIP_DIR.glob(f"{spec.animation}_source_strip.png") if pattern.match(path.name)]
        if matches != [f"{spec.animation}_source_strip.png"]:
            fail(f"source strip naming mismatch for {spec.animation}")


def main() -> None:
    verify_names()
    animation_frames = {spec.animation: import_strip(spec) for spec in ROWS}
    frame_paths = write_frames(animation_frames)
    build_tres(frame_paths)
    write_motion_preview(frame_paths)
    write_runtime_scene_preview(frame_paths)
    print(f"OK: imported production strips -> {OUT_DIR}")
    print(f"OK: wrote SpriteFrames -> {SPRITE_FRAMES}")
    print(f"OK: wrote motion preview -> {MOTION_PREVIEW}")
    print(f"OK: wrote runtime scene preview -> {RUNTIME_SCENE_PREVIEW}")


if __name__ == "__main__":
    main()
