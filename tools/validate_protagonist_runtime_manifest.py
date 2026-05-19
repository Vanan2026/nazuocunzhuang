from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "production" / "assets" / "protagonist" / "protagonist_runtime_manifest_v001.json"
FINAL_STRIP_DIR = ROOT / "production" / "assets" / "protagonist" / "final_source_strips"
FRAME_DIR = ROOT / "sprites" / "characters" / "protagonist" / "frames"
SPRITE_FRAMES = ROOT / "sprites" / "characters" / "protagonist" / "player_mvp_4dir_frames.tres"

EXPECTED = {
    "player_walk_down": 8, "player_walk_down_left": 8, "player_walk_left": 8, "player_walk_up_left": 8,
    "player_walk_up": 8, "player_walk_up_right": 8, "player_walk_right": 8, "player_walk_down_right": 8,
    "player_idle_down": 4, "player_idle_down_left": 4, "player_idle_left": 4, "player_idle_up_left": 4,
    "player_idle_up": 4, "player_idle_up_right": 4, "player_idle_right": 4, "player_idle_down_right": 4,
    "player_interact_down": 6, "player_interact_down_left": 6, "player_interact_left": 6, "player_interact_up_left": 6,
    "player_interact_up": 6, "player_interact_up_right": 6, "player_interact_right": 6, "player_interact_down_right": 6,
    "player_sit_down_side": 6, "player_sit_down_down": 6, "player_sit_down_up": 6,
    "player_sit_idle_side": 6, "player_sit_idle_down": 6, "player_sit_idle_up": 6,
    "player_stand_up_side": 6, "player_stand_up_down": 6, "player_stand_up_up": 6,
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def frame_paths(animation: str, count: int) -> list[Path]:
    paths = [FRAME_DIR / f"{animation}_{idx:02d}.png" for idx in range(count)]
    for path in paths:
        require(path.exists(), f"missing runtime frame: {path.name}")
    return paths


def main() -> None:
    require(MANIFEST.exists(), "missing protagonist runtime manifest")
    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "protagonist manifest")
    require(manifest.get("package_id") == "protagonist_runtime_v001", "manifest package_id mismatch")
    require(manifest.get("source_dir") == "production/assets/protagonist/final_source_strips", "manifest source_dir mismatch")
    require(manifest.get("runtime_sprite_frames") == "sprites/characters/protagonist/player_mvp_4dir_frames.tres", "manifest SpriteFrames path mismatch")
    animations = require_dict(manifest.get("animations"), "animations")
    require(set(animations.keys()) == set(EXPECTED.keys()), "manifest animation set mismatch")

    sprite_text = SPRITE_FRAMES.read_text(encoding="utf-8")
    for animation, count in EXPECTED.items():
        record = require_dict(animations.get(animation), animation)
        require(int(record.get("frame_count")) == count, f"{animation} frame count mismatch")
        source = FINAL_STRIP_DIR / f"{animation}_source_strip.png"
        require(source.exists(), f"missing source strip: {source.name}")
        require(record.get("source_strip_sha256") == sha256(source), f"{animation} source strip checksum mismatch")
        frame_records = record.get("frames")
        require(isinstance(frame_records, list), f"{animation} frames must be a list")
        require(len(frame_records) == count, f"{animation} manifest frame list mismatch")
        for idx, frame_record_raw in enumerate(frame_records):
            frame_record = require_dict(frame_record_raw, f"{animation} frame {idx}")
            frame = FRAME_DIR / f"{animation}_{idx:02d}.png"
            require(frame_record.get("path") == frame.relative_to(ROOT).as_posix(), f"{animation}_{idx:02d} path mismatch")
            require(frame_record.get("sha256") == sha256(frame), f"{animation}_{idx:02d} checksum mismatch")
            require(f'path="res://{frame.relative_to(ROOT).as_posix()}"' in sprite_text, f"SpriteFrames missing {frame.name}")
        require(f'name": &"{animation}"' in sprite_text, f"SpriteFrames missing animation {animation}")
    print("OK: protagonist runtime manifest matches final source strips and SpriteFrames")


if __name__ == "__main__":
    main()
