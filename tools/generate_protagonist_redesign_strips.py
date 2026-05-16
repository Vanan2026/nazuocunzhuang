from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
FINAL_STRIP_DIR = ROOT / "production" / "assets" / "protagonist" / "final_source_strips"
SEED_PREVIEW = ROOT / ".codex" / "protagonist_redesign_seed_preview.png"
SAMPLE_PREVIEW = ROOT / ".codex" / "protagonist_redesign_sample_preview.png"

FRAME_SIZE = (192, 288)
SOURCE_SLOT_SIZE = (384, 576)
FOOT_BASELINE_Y = 270
SCALE = 4

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
    animation: str
    frame_count: int
    action: str
    direction: str


SPECS: list[AnimSpec] = (
    [AnimSpec(f"player_walk_{direction}", 8, "walk", direction) for direction in DIRECTIONS]
    + [AnimSpec(f"player_idle_{direction}", 4, "idle", direction) for direction in DIRECTIONS]
    + [AnimSpec(f"player_interact_{direction}", 6, "interact", direction) for direction in DIRECTIONS]
    + [
        AnimSpec("player_sit_down_side", 6, "sit_down", "right"),
        AnimSpec("player_sit_down_down", 6, "sit_down", "down"),
        AnimSpec("player_sit_down_up", 6, "sit_down", "up"),
        AnimSpec("player_sit_idle_side", 6, "sit_idle", "right"),
        AnimSpec("player_sit_idle_down", 6, "sit_idle", "down"),
        AnimSpec("player_sit_idle_up", 6, "sit_idle", "up"),
        AnimSpec("player_stand_up_side", 6, "stand_up", "right"),
        AnimSpec("player_stand_up_down", 6, "stand_up", "down"),
        AnimSpec("player_stand_up_up", 6, "stand_up", "up"),
    ]
)

LINE = (55, 45, 34, 175)
HAIR = (42, 34, 29, 245)
HAIR_LIGHT = (103, 82, 65, 105)
SKIN = (225, 177, 137, 245)
SKIN_SHADOW = (179, 128, 92, 185)
BLOUSE = (242, 225, 198, 238)
BLOUSE_SHADOW = (202, 170, 135, 145)
BLOUSE_LIGHT = (255, 243, 218, 150)
SKIRT = (74, 116, 126, 242)
SKIRT_DARK = (40, 76, 86, 205)
SKIRT_LIGHT = (120, 154, 154, 105)
SANDAL = (84, 61, 39, 240)
SANDAL_LIGHT = (148, 110, 71, 165)
RIBBON = (139, 72, 62, 185)

SIDE_POSES = [
    (-12, 10, 0, 0, -7, 0),
    (-7, 14, 6, 0, -3, 1),
    (0, 12, 11, 1, 1, 2),
    (12, 5, 3, 0, 7, 1),
    (12, -10, 0, 0, 7, 0),
    (7, -14, 6, 0, 3, -1),
    (0, -12, 11, 1, -1, -2),
    (-12, -5, 3, 0, -7, -1),
]


def sc(value: float) -> int:
    return int(round(value * SCALE))


def xy(x: float, y: float) -> tuple[int, int]:
    return sc(x), sc(y)


def rgba(color: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return color


def ellipse(draw: ImageDraw.ImageDraw, cx: float, cy: float, rx: float, ry: float, fill, outline=None, width: int = 1) -> None:
    draw.ellipse((sc(cx - rx), sc(cy - ry), sc(cx + rx), sc(cy + ry)), fill=fill, outline=outline, width=sc(width))


def line(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill, width: float) -> None:
    draw.line([xy(x, y) for x, y in points], fill=fill, width=max(1, sc(width)), joint="curve")


def polygon(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill, outline=None) -> None:
    draw.polygon([xy(x, y) for x, y in points], fill=fill)
    if outline is not None:
        draw.line([xy(x, y) for x, y in points + [points[0]]], fill=outline, width=sc(1.2), joint="curve")


def angle_kind(direction: str) -> str:
    if direction == "down":
        return "front"
    if direction == "up":
        return "back"
    if direction in ("left", "right"):
        return "side"
    return "diagonal"


def facing_sign(direction: str) -> int:
    return -1 if direction.endswith("left") or direction == "left" else 1


def is_upward(direction: str) -> bool:
    return direction.startswith("up") or direction == "up"


def pose_offsets(action: str, direction: str, idx: int, count: int) -> dict[str, float]:
    t = idx / max(1, count)
    bob = 0.0
    sway = 0.0
    reach = 0.0
    crouch = 0.0
    sit = 0.0

    if action == "walk":
        bob = [0, -2, -1, 1, 0, -2, -1, 1][idx % 8]
        sway = [-2, -1, 2, 4, 2, 1, -2, -4][idx % 8]
    elif action == "idle":
        bob = [0, -1, 0, 1][idx % 4]
        sway = [-1, 0, 1, 0][idx % 4]
    elif action == "interact":
        reach = [0, 0.35, 0.8, 1.0, 0.65, 0.2][idx % 6]
        bob = [0, -1, -2, -2, -1, 0][idx % 6]
        sway = [0, 1, 2, 2, 1, 0][idx % 6] * facing_sign(direction)
    elif action == "sit_down":
        crouch = idx / 5.0
        sit = max(0.0, (idx - 2) / 3.0)
    elif action == "stand_up":
        crouch = 1.0 - idx / 5.0
        sit = max(0.0, (3 - idx) / 3.0)
    elif action == "sit_idle":
        crouch = 1.0
        sit = 1.0
        bob = [0, -1, 0, 1, 0, -1][idx % 6] * 0.5

    return {"bob": bob, "sway": sway, "reach": reach, "crouch": crouch, "sit": sit, "t": t}


def leg_pose(action: str, direction: str, idx: int) -> tuple[tuple[float, float, float], tuple[float, float, float], float]:
    if action != "walk":
        return (-7, 0, 0), (8, 0, 0), 0

    if angle_kind(direction) in ("side", "diagonal"):
        rear_dx, front_dx, rear_lift, front_lift, hem_sway, _body = SIDE_POSES[idx % 8]
        sign = facing_sign(direction)
        return (rear_dx * sign, rear_lift, 0), (front_dx * sign, front_lift, 0), hem_sway * sign

    phase = -1 if idx < 4 else 1
    step = [0, 6, 12, 5, 0, 6, 12, 5][idx % 8]
    near = (-phase * (7 + step * 0.68), min(3, step // 4), 0)
    far = (phase * (7 + step * 0.5), max(0, step - 3), 0)
    return far, near, phase * step * 0.9


def add_texture(image: Image.Image, seed: int) -> Image.Image:
    rng = random.Random(seed)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    for _ in range(90):
        x = rng.randint(sc(44), sc(148))
        y = rng.randint(sc(83), sc(268))
        r = rng.randint(sc(1), sc(5))
        alpha = rng.randint(8, 22)
        color = (255, 250, 230, alpha) if rng.random() < 0.55 else (42, 36, 30, alpha)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
    subject_alpha = image.getchannel("A")
    overlay_alpha = ImageChops.multiply(overlay.getchannel("A"), subject_alpha)
    overlay.putalpha(overlay_alpha)
    return Image.alpha_composite(image, overlay)


def draw_feet_and_legs(
    draw: ImageDraw.ImageDraw,
    cx: float,
    direction: str,
    action: str,
    idx: int,
    waist_y: float,
    hem_y: float,
    crouch: float,
) -> float:
    if action in ("sit_idle",):
        sign = facing_sign(direction)
        knee_y = FOOT_BASELINE_Y - 18
        line(draw, [(cx - sign * 5, knee_y - 9), (cx + sign * 18, knee_y + 2)], SKIN_SHADOW, 5.5)
        line(draw, [(cx + sign * 18, knee_y + 2), (cx + sign * 34, FOOT_BASELINE_Y - 3)], SKIN, 5.0)
        ellipse(draw, cx + sign * 43, FOOT_BASELINE_Y - 2.5, 10, 3.0, SANDAL, LINE)
        return 0.0

    if action in ("sit_down", "stand_up") and crouch > 0.58:
        sign = facing_sign(direction)
        bend = (crouch - 0.58) / 0.42
        line(draw, [(cx - sign * 2, hem_y - 9), (cx + sign * (12 + 14 * bend), FOOT_BASELINE_Y - 7)], SKIN_SHADOW, 5.5)
        line(draw, [(cx + sign * 8, hem_y - 8), (cx + sign * (27 + 15 * bend), FOOT_BASELINE_Y - 3)], SKIN, 5.5)
        ellipse(draw, cx + sign * (35 + 14 * bend), FOOT_BASELINE_Y - 2.5, 10, 3.0, SANDAL, LINE)
        return 0.0

    far, near, hem_sway = leg_pose(action, direction, idx)
    far_dx, far_lift, _ = far
    near_dx, near_lift, _ = near
    base_y = FOOT_BASELINE_Y
    hip_y = hem_y - 5

    line(draw, [(cx + far_dx * 0.5, hip_y), (cx + far_dx, base_y - far_lift - 2)], SKIN_SHADOW, 5.0)
    line(draw, [(cx + near_dx * 0.45, hip_y - 1), (cx + near_dx, base_y - near_lift - 2)], SKIN, 6.0)

    foot_sign = facing_sign(direction) if angle_kind(direction) in ("side", "diagonal") else 1
    far_len = 10 if far_lift > 2 else 13
    near_len = 11 if near_lift > 2 else 15
    ellipse(draw, cx + far_dx + foot_sign * 3, min(base_y - 3, base_y - far_lift - 2), far_len, 3.0, SANDAL, LINE)
    ellipse(draw, cx + near_dx + foot_sign * 4, min(base_y - 3, base_y - near_lift - 2), near_len, 3.4, SANDAL, LINE)
    line(draw, [(cx + near_dx - foot_sign * 5, base_y - near_lift - 3), (cx + near_dx + foot_sign * 9, base_y - near_lift - 2)], SANDAL_LIGHT, 1.2)
    if near_lift <= 1:
        draw.rounded_rectangle((sc(cx + near_dx - 8), sc(base_y - 2), sc(cx + near_dx + 10), sc(base_y)), radius=sc(2), fill=(72, 52, 34, 190))
    if far_lift <= 1:
        draw.rounded_rectangle((sc(cx + far_dx - 7), sc(base_y - 2), sc(cx + far_dx + 9), sc(base_y)), radius=sc(2), fill=(72, 52, 34, 155))
    return hem_sway


def draw_skirt(draw: ImageDraw.ImageDraw, cx: float, waist_y: float, hem_y: float, direction: str, hem_sway: float, crouch: float, sit: float) -> None:
    sign = facing_sign(direction)
    if sit >= 0.92:
        points = [
            (cx - 30, hem_y - 25),
            (cx + 14, hem_y - 27),
            (cx + sign * 46, FOOT_BASELINE_Y - 15),
            (cx + sign * 27, FOOT_BASELINE_Y - 2),
            (cx - sign * 25, FOOT_BASELINE_Y - 6),
            (cx - sign * 37, FOOT_BASELINE_Y - 17),
        ]
        polygon(draw, points, SKIRT, SKIRT_DARK)
        for offset in (-16, -3, 12):
            line(draw, [(cx + offset, hem_y - 22), (cx + offset * 0.4 + sign * 22, FOOT_BASELINE_Y - 8)], SKIRT_LIGHT, 1.0)
        return

    half_top = 23 - 5 * crouch
    half_bottom = 34 - 10 * crouch
    side_bias = sign * 4 if angle_kind(direction) in ("side", "diagonal") else 0
    gait_spread = abs(hem_sway) * 0.85 if angle_kind(direction) in ("side", "diagonal") else 0.0
    points = [
        (cx - half_top + side_bias * 0.2, waist_y),
        (cx + half_top + side_bias * 0.4, waist_y + 1),
        (cx + half_bottom + hem_sway + side_bias + gait_spread, hem_y),
        (cx + 14 + hem_sway * 0.5 + side_bias + gait_spread * 0.35, hem_y + 7),
        (cx - 13 + hem_sway * 0.25 + side_bias * 0.3, hem_y + 6),
        (cx - half_bottom + hem_sway - side_bias * 0.2 - gait_spread, hem_y),
    ]
    polygon(draw, points, SKIRT, SKIRT_DARK)
    polygon(
        draw,
        [
            (cx - 13 + side_bias * 0.2, waist_y + 8),
            (cx + 2 + side_bias * 0.3, waist_y + 6),
            (cx + 7 + hem_sway * 0.6 + side_bias, hem_y + 2),
            (cx - 10 + hem_sway * 0.3 + side_bias * 0.2, hem_y + 2),
        ],
        SKIRT_LIGHT,
    )
    for offset in (-15, -3, 10):
        line(draw, [(cx + offset + side_bias * 0.2, waist_y + 8), (cx + offset * 0.7 + hem_sway * 0.6 + side_bias * 0.4, hem_y + 3)], SKIRT_DARK, 0.8)


def draw_torso_and_arms(
    draw: ImageDraw.ImageDraw,
    cx: float,
    top_y: float,
    waist_y: float,
    direction: str,
    action: str,
    idx: int,
    reach: float,
    crouch: float,
) -> None:
    kind = angle_kind(direction)
    sign = facing_sign(direction)
    shoulder_y = top_y + 12
    torso_bottom = waist_y + 4
    side_bias = sign * 4 if kind in ("side", "diagonal") else 0
    width_top = 26 - 4 * crouch
    width_bottom = 21 - 5 * crouch
    if kind == "side":
        width_top = 15
        width_bottom = 13
    elif kind == "diagonal":
        width_top = 22
        width_bottom = 18

    polygon(
        draw,
        [
            (cx - width_top + side_bias, shoulder_y),
            (cx + width_top * (0.75 if kind == "side" else 1.0) + side_bias, shoulder_y + 1),
            (cx + width_bottom + side_bias * 0.6, torso_bottom),
            (cx - width_bottom + side_bias * 0.3, torso_bottom),
        ],
        BLOUSE,
        BLOUSE_SHADOW,
    )

    if kind != "back":
        line(draw, [(cx + side_bias * 0.4, shoulder_y + 4), (cx + side_bias * 0.3, torso_bottom - 3)], BLOUSE_SHADOW, 0.9)
        for by in (shoulder_y + 13, shoulder_y + 25, shoulder_y + 37):
            ellipse(draw, cx + side_bias * 0.4, by, 1.25, 1.25, (103, 83, 62, 130), None)
    else:
        line(draw, [(cx - 12, shoulder_y + 8), (cx + 13, shoulder_y + 8)], BLOUSE_LIGHT, 1.1)

    sleeve_l = (cx - width_top + side_bias, shoulder_y + 8)
    sleeve_r = (cx + width_top + side_bias, shoulder_y + 8)
    if kind == "side":
        sleeve_l = (cx - sign * 5, shoulder_y + 9)
        sleeve_r = (cx + sign * 11, shoulder_y + 8)
    if kind == "diagonal":
        sleeve_l = (cx - 19 + side_bias * 0.3, shoulder_y + 9)
        sleeve_r = (cx + 18 + side_bias * 0.5, shoulder_y + 8)

    if action == "interact":
        lead = sign if kind in ("side", "diagonal") else 1
        hand_x = cx + lead * (18 + 18 * reach)
        hand_y = shoulder_y + 46 - 8 * reach
        elbow_x = cx + lead * (18 + 9 * reach)
        elbow_y = shoulder_y + 31 - 6 * reach
        line(draw, [sleeve_r, (elbow_x, elbow_y), (hand_x, hand_y)], BLOUSE_SHADOW, 5.0)
        line(draw, [(elbow_x, elbow_y), (hand_x, hand_y)], SKIN, 3.4)
        ellipse(draw, hand_x, hand_y, 3.2, 3.2, SKIN, LINE)
        line(draw, [sleeve_l, (sleeve_l[0] - lead * 7, shoulder_y + 43)], BLOUSE_SHADOW, 4.2)
        ellipse(draw, sleeve_l[0] - lead * 8, shoulder_y + 45, 2.8, 2.8, SKIN, LINE)
        return

    arm_drop = 44 - 24 * crouch
    if action in ("sit_down", "stand_up", "sit_idle"):
        arm_drop = 32
    line(draw, [sleeve_l, (sleeve_l[0] - 8, shoulder_y + arm_drop)], BLOUSE_SHADOW, 4.0)
    line(draw, [sleeve_r, (sleeve_r[0] + 8, shoulder_y + arm_drop - 2)], BLOUSE_SHADOW, 4.0)
    ellipse(draw, sleeve_l[0] - 9, shoulder_y + arm_drop + 1, 2.8, 2.8, SKIN, LINE)
    ellipse(draw, sleeve_r[0] + 9, shoulder_y + arm_drop - 1, 2.8, 2.8, SKIN, LINE)
    if action == "sit_idle":
        line(draw, [(cx + sign * 5, waist_y + 7), (cx + sign * 27, FOOT_BASELINE_Y - 21)], BLOUSE_SHADOW, 4.0)
        ellipse(draw, cx + sign * 30, FOOT_BASELINE_Y - 20, 2.6, 2.6, SKIN, LINE)


def draw_head(draw: ImageDraw.ImageDraw, cx: float, neck_y: float, direction: str, action: str, idx: int) -> None:
    kind = angle_kind(direction)
    sign = facing_sign(direction)
    head_y = neck_y - 28
    if action in ("sit_down", "stand_up"):
        head_y += 5
    if action == "sit_idle":
        head_y += 9

    line(draw, [(cx - 4, neck_y - 4), (cx - 4, neck_y + 13)], SKIN_SHADOW, 5.5)
    line(draw, [(cx + 4, neck_y - 4), (cx + 4, neck_y + 13)], SKIN, 5.5)

    if kind == "back":
        ellipse(draw, cx, head_y - 3, 21, 26, HAIR, LINE, 1)
        ellipse(draw, cx + 2, head_y - 28, 12, 9, HAIR, LINE, 1)
        for ox in (-8, 0, 8):
            line(draw, [(cx + ox, head_y - 25), (cx + ox * 0.8, head_y + 17)], HAIR_LIGHT, 0.8)
        return

    if kind == "front":
        ellipse(draw, cx, head_y, 17, 21, SKIN, LINE, 1)
        ellipse(draw, cx, head_y - 14, 21, 18, HAIR, LINE, 1)
        ellipse(draw, cx + 10, head_y - 29, 10, 8, HAIR, LINE, 1)
        line(draw, [(cx - 16, head_y - 2), (cx - 21, head_y + 22)], HAIR, 3.0)
        line(draw, [(cx + 16, head_y - 2), (cx + 20, head_y + 21)], HAIR, 2.2)
        ellipse(draw, cx - 6, head_y + 2, 1.5, 1.5, (40, 34, 30, 170), None)
        ellipse(draw, cx + 7, head_y + 2, 1.5, 1.5, (40, 34, 30, 170), None)
        line(draw, [(cx - 5, head_y + 12), (cx + 5, head_y + 12)], (151, 92, 84, 125), 0.8)
        return

    face_cx = cx + sign * 5
    ellipse(draw, face_cx, head_y, 14, 20, SKIN, LINE, 1)
    ellipse(draw, cx - sign * 2, head_y - 12, 19, 17, HAIR, LINE, 1)
    ellipse(draw, cx - sign * 16, head_y + 5, 10, 25, HAIR, LINE, 1)
    ellipse(draw, cx - sign * 8, head_y - 30, 9, 8, HAIR, LINE, 1)
    line(draw, [(cx + sign * 13, head_y - 3), (cx + sign * 17, head_y + 17)], HAIR, 2.0)
    ellipse(draw, cx + sign * 14, head_y + 2, 1.4, 1.4, (40, 34, 30, 170), None)
    line(draw, [(cx + sign * 10, head_y + 12), (cx + sign * 16, head_y + 12)], (151, 92, 84, 125), 0.8)
    line(draw, [(cx - sign * 7, head_y - 21), (cx + sign * 7, head_y - 11)], HAIR_LIGHT, 0.8)


def render_frame(animation: str, action: str, direction: str, idx: int, count: int) -> Image.Image:
    large = Image.new("RGBA", (FRAME_SIZE[0] * SCALE, FRAME_SIZE[1] * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(large, "RGBA")
    pose = pose_offsets(action, direction, idx, count)
    crouch = pose["crouch"]
    sit = pose["sit"]
    sign = facing_sign(direction)
    body_shift = 0.0
    if action == "walk" and angle_kind(direction) in ("side", "diagonal"):
        body_shift = SIDE_POSES[idx % 8][5] * sign
    cx = 96 + pose["sway"] * 0.35 + body_shift

    if action in ("sit_idle",):
        waist_y = 232 + pose["bob"]
        top_y = 178 + pose["bob"]
        hem_y = 255
        neck_y = top_y - 6
    elif action in ("sit_down", "stand_up"):
        waist_y = 186 + crouch * 38 + pose["bob"]
        top_y = 133 + crouch * 27 + pose["bob"]
        hem_y = 246 + crouch * 12
        neck_y = top_y - 7
    else:
        waist_y = 190 + pose["bob"]
        top_y = 135 + pose["bob"]
        hem_y = 248 + abs(pose["sway"]) * 0.35
        neck_y = top_y - 8

    hem_sway = draw_feet_and_legs(draw, cx, direction, action, idx, waist_y, hem_y, crouch)
    draw_skirt(draw, cx, waist_y, hem_y, direction, hem_sway + pose["sway"] * 0.7, crouch, sit)
    draw_torso_and_arms(draw, cx, top_y, waist_y, direction, action, idx, pose["reach"], crouch)
    draw_head(draw, cx, neck_y, direction, action, idx)

    if direction in ("down_left", "down_right") and action == "interact":
        ellipse(draw, cx + sign * 35, waist_y + 18, 3, 3, RIBBON, None)

    large = add_texture(large, hash(animation) + idx)
    large = large.filter(ImageFilter.GaussianBlur(radius=0.08 * SCALE))
    frame = large.resize(FRAME_SIZE, Image.Resampling.LANCZOS)
    pixels = frame.load()
    for y in range(FOOT_BASELINE_Y + 1, FRAME_SIZE[1]):
        for x in range(FRAME_SIZE[0]):
            pixels[x, y] = (0, 0, 0, 0)

    # Keep a stable non-shadow contact pixel at the runtime baseline.
    contact = ImageDraw.Draw(frame, "RGBA")
    if action in ("sit_idle",) or (action in ("sit_down", "stand_up") and crouch > 0.58):
        contact.rounded_rectangle((101, FOOT_BASELINE_Y - 2, 145, FOOT_BASELINE_Y), radius=2, fill=(72, 52, 34, 190))
    else:
        contact.rounded_rectangle((83, FOOT_BASELINE_Y - 2, 109, FOOT_BASELINE_Y), radius=2, fill=(72, 52, 34, 165))
    return frame


def upscale_to_source(frame: Image.Image) -> Image.Image:
    return frame.resize(SOURCE_SLOT_SIZE, Image.Resampling.LANCZOS)


def write_strip(spec: AnimSpec) -> list[Image.Image]:
    frames = [render_frame(spec.animation, spec.action, spec.direction, idx, spec.frame_count) for idx in range(spec.frame_count)]
    strip = Image.new("RGBA", (SOURCE_SLOT_SIZE[0] * spec.frame_count, SOURCE_SLOT_SIZE[1]), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        strip.alpha_composite(upscale_to_source(frame), (idx * SOURCE_SLOT_SIZE[0], 0))
    FINAL_STRIP_DIR.mkdir(parents=True, exist_ok=True)
    strip.save(FINAL_STRIP_DIR / f"{spec.animation}_source_strip.png")
    return frames


def write_seed_preview(frames_by_anim: dict[str, list[Image.Image]]) -> None:
    SEED_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (768, 432), (238, 232, 216, 255))
    draw = ImageDraw.Draw(canvas)
    title = "Redesigned protagonist seed - hand-painted watercolor runtime target"
    draw.text((24, 20), title, fill=(48, 42, 34, 255))
    entries = [
        ("front", "player_idle_down", 0),
        ("left", "player_idle_left", 0),
        ("back", "player_idle_up", 0),
        ("walk beat", "player_walk_left", 2),
    ]
    for i, (label, anim, idx) in enumerate(entries):
        x = 64 + i * 170
        y = 72
        frame = frames_by_anim[anim][idx]
        canvas.alpha_composite(frame.resize((144, 216), Image.Resampling.LANCZOS), (x, y))
        draw.line((x, y + int(FOOT_BASELINE_Y * 0.75), x + 144, y + int(FOOT_BASELINE_Y * 0.75)), fill=(160, 88, 70, 120), width=1)
        draw.text((x + 28, y + 226), label, fill=(48, 42, 34, 255))
    canvas.save(SEED_PREVIEW)


def write_sample_preview(frames_by_anim: dict[str, list[Image.Image]]) -> None:
    rows = ["player_idle_down", "player_walk_down", "player_walk_left", "player_walk_right"]
    label_w = 170
    cols = 8
    canvas = Image.new("RGBA", (label_w + FRAME_SIZE[0] * cols, FRAME_SIZE[1] * len(rows)), (244, 239, 226, 255))
    draw = ImageDraw.Draw(canvas)
    for row_idx, anim in enumerate(rows):
        y = row_idx * FRAME_SIZE[1]
        draw.text((8, y + 12), anim, fill=(38, 35, 30, 255))
        frames = frames_by_anim[anim]
        for idx in range(cols):
            frame = frames[idx % len(frames)]
            x = label_w + idx * FRAME_SIZE[0]
            canvas.alpha_composite(frame, (x, y))
            draw.rectangle((x, y, x + FRAME_SIZE[0] - 1, y + FRAME_SIZE[1] - 1), outline=(190, 180, 160, 150))
            draw.line((x, y + FOOT_BASELINE_Y, x + FRAME_SIZE[0], y + FOOT_BASELINE_Y), fill=(210, 90, 70, 120))
    canvas.save(SAMPLE_PREVIEW)


def main() -> None:
    frames_by_anim: dict[str, list[Image.Image]] = {}
    for spec in SPECS:
        frames_by_anim[spec.animation] = write_strip(spec)
    write_seed_preview(frames_by_anim)
    write_sample_preview(frames_by_anim)
    print(f"OK: wrote redesigned protagonist source strips -> {FINAL_STRIP_DIR}")
    print(f"OK: wrote seed preview -> {SEED_PREVIEW}")
    print(f"OK: wrote sample preview -> {SAMPLE_PREVIEW}")


if __name__ == "__main__":
    main()
