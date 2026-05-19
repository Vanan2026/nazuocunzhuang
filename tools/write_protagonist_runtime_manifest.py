from __future__ import annotations

import hashlib
import json
from pathlib import Path

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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    animations = {}
    for animation, count in EXPECTED.items():
        source = FINAL_STRIP_DIR / f"{animation}_source_strip.png"
        frames = []
        for idx in range(count):
            frame = FRAME_DIR / f"{animation}_{idx:02d}.png"
            frames.append({
                "index": idx,
                "path": frame.relative_to(ROOT).as_posix(),
                "sha256": sha256(frame),
            })
        animations[animation] = {
            "frame_count": count,
            "source_strip": source.relative_to(ROOT).as_posix(),
            "source_strip_sha256": sha256(source),
            "frames": frames,
        }
    manifest = {
        "package_id": "protagonist_runtime_v001",
        "status": "self_checked_final_runtime_candidate",
        "source_dir": "production/assets/protagonist/final_source_strips",
        "runtime_frame_dir": "sprites/characters/protagonist/frames",
        "runtime_sprite_frames": "sprites/characters/protagonist/player_mvp_4dir_frames.tres",
        "generator": "tools/build_protagonist_from_production_strips.py",
        "contract": {
            "source_slot_px": {"width": 384, "height": 576},
            "runtime_frame_px": {"width": 192, "height": 288},
            "runtime_foot_baseline_y": 270,
            "runtime_sprite_foot_anchor": {"x": 96, "y": 280},
        },
        "animations": animations,
        "visual_review_gate": [
            "Automated checks prove source-to-runtime consistency, baseline, alpha, and animation coverage.",
            "Human visual review is still the final judge for acting polish, face readability, and cloth motion taste."
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(f"OK: wrote protagonist runtime manifest -> {MANIFEST.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
