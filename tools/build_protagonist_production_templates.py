from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "production" / "assets" / "protagonist"
TEMPLATE_DIR = OUT_DIR / "templates"
MANIFEST = OUT_DIR / "protagonist_final_asset_manifest.json"

SOURCE_SLOT_SIZE = (384, 576)
SOURCE_FOOT_ANCHOR = (192, 540)
RUNTIME_FRAME_SIZE = (192, 288)
RUNTIME_FOOT_ANCHOR = (96, 270)

DIRECTIONS = [
    "down",
    "down_left",
    "left",
    "up_left",
    "up",
    "up_right",
    "right",
    "down_right",
]


@dataclass(frozen=True)
class AnimSpec:
    prefix: str
    directions: list[str]
    frame_count: int
    loop: bool
    notes: str


ANIMS = [
    AnimSpec(
        "player_walk",
        DIRECTIONS,
        8,
        True,
        "clear grounded walking cycle; side directions require visible alternating sandal/leg motion",
    ),
    AnimSpec("player_idle", DIRECTIONS, 4, True, "subtle breathing and cloth movement only"),
    AnimSpec("player_interact", DIRECTIONS, 6, False, "small reach/check/pick-up gesture; keep feet planted"),
    AnimSpec("player_sit_down", ["side", "down", "up"], 6, False, "directional sit-down transition; starts from standing height"),
    AnimSpec("player_sit_idle", ["side", "down", "up"], 6, True, "directional seated idle; calm breathing"),
    AnimSpec("player_stand_up", ["side", "down", "up"], 6, False, "directional stand-up transition; ends at standing height"),
]


def draw_template(path: Path, animation: str, frame_count: int) -> None:
    slot_w, slot_h = SOURCE_SLOT_SIZE
    canvas = Image.new("RGBA", (slot_w * frame_count, slot_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()

    for idx in range(frame_count):
        x = idx * slot_w
        draw.rectangle((x, 0, x + slot_w - 1, slot_h - 1), outline=(72, 126, 180, 180), width=2)
        draw.line((x + SOURCE_FOOT_ANCHOR[0], 0, x + SOURCE_FOOT_ANCHOR[0], slot_h), fill=(80, 160, 220, 120), width=1)
        draw.line((x, SOURCE_FOOT_ANCHOR[1], x + slot_w, SOURCE_FOOT_ANCHOR[1]), fill=(220, 72, 72, 180), width=2)
        draw.ellipse(
            (
                x + SOURCE_FOOT_ANCHOR[0] - 5,
                SOURCE_FOOT_ANCHOR[1] - 5,
                x + SOURCE_FOOT_ANCHOR[0] + 5,
                SOURCE_FOOT_ANCHOR[1] + 5,
            ),
            fill=(220, 72, 72, 220),
        )
        draw.text((x + 12, 12), f"{animation}_{idx:02d}", fill=(35, 35, 35, 210), font=font)

    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def main() -> None:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "source_slot_size": SOURCE_SLOT_SIZE,
        "source_foot_anchor": SOURCE_FOOT_ANCHOR,
        "runtime_frame_size": RUNTIME_FRAME_SIZE,
        "runtime_foot_anchor": RUNTIME_FOOT_ANCHOR,
        "animations": [],
    }

    animations: list[dict[str, object]] = []
    for spec in ANIMS:
        for direction in spec.directions:
            animation = f"{spec.prefix}_{direction}"
            template_path = TEMPLATE_DIR / f"{animation}_template.png"
            draw_template(template_path, animation, spec.frame_count)
            frame_files = [f"{animation}_{idx:02d}.png" for idx in range(spec.frame_count)]
            source_strip = f"{animation}_source_strip.png"
            animations.append(
                {
                    "animation": animation,
                    "direction": direction,
                    "frame_count": spec.frame_count,
                    "loop": spec.loop,
                    "notes": spec.notes,
                    "source_strip": source_strip,
                    "template": str(template_path.relative_to(ROOT)).replace("\\", "/"),
                    "runtime_frames": frame_files,
                }
            )

    manifest["animations"] = animations
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: wrote templates -> {TEMPLATE_DIR}")
    print(f"OK: wrote manifest -> {MANIFEST}")


if __name__ == "__main__":
    main()
