from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets/scenes/home_area"
STYLE_REFERENCE = "production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg"
CANVAS_SIZE = (1920, 1080)


def _paper_noise(size: tuple[int, int], base: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", size, base + (255,))
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = size
    for y in range(0, height, 6):
        for x in range(0, width, 6):
            value = ((x * 11 + y * 17) % 29) - 14
            color = tuple(max(0, min(255, channel + value)) for channel in base)
            draw.rectangle((x, y, x + 5, y + 5), fill=color + (20,))
    return image.filter(ImageFilter.GaussianBlur(0.55))


def _draw_path(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], width: int) -> None:
    shadow = [(x + 3, y + 5) for x, y in points]
    draw.line(shadow, fill=(111, 83, 48, 70), width=width + 16, joint="curve")
    draw.line(points, fill=(186, 152, 93, 230), width=width, joint="curve")
    draw.line(points, fill=(223, 196, 136, 90), width=max(4, width // 7), joint="curve")


def _draw_tree(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0, spring: bool = False) -> None:
    trunk_w = int(22 * scale)
    trunk_h = int(64 * scale)
    draw.rounded_rectangle(
        (x - trunk_w // 2, y - trunk_h, x + trunk_w // 2, y + 12),
        radius=8,
        fill=(103, 67, 36, 255),
        outline=(68, 45, 29, 190),
        width=max(2, int(3 * scale)),
    )
    leaf = (112, 136, 63, 245) if not spring else (211, 154, 144, 235)
    dark = (71, 101, 49, 210) if not spring else (154, 103, 103, 210)
    for dx, dy, radius in [
        (-44, -96, 44),
        (0, -120, 54),
        (48, -92, 46),
        (-10, -78, 52),
    ]:
        rr = int(radius * scale)
        cx = int(x + dx * scale)
        cy = int(y + dy * scale)
        draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=leaf, outline=dark, width=max(2, int(4 * scale)))
    draw.arc((x - int(74 * scale), y - int(168 * scale), x + int(76 * scale), y - int(40 * scale)), 20, 180, fill=(244, 224, 157, 60), width=max(2, int(4 * scale)))


def _draw_house(draw: ImageDraw.ImageDraw) -> None:
    # 3/4 cottage footprint anchored to the upper-left yard.
    draw.polygon([(525, 258), (820, 216), (1010, 338), (704, 412)], fill=(71, 89, 91, 255), outline=(46, 57, 54, 255))
    draw.polygon([(462, 327), (704, 412), (704, 640), (462, 552)], fill=(207, 177, 124, 255), outline=(91, 58, 35, 255))
    draw.polygon([(704, 412), (1010, 338), (1010, 555), (704, 640)], fill=(190, 148, 94, 255), outline=(91, 58, 35, 255))
    draw.polygon([(462, 327), (525, 258), (820, 216), (704, 412)], fill=(48, 72, 76, 255), outline=(42, 48, 43, 255))
    for i in range(7):
        x = 545 + i * 44
        draw.line((x, 260, x + 190, 346), fill=(34, 49, 52, 125), width=4)
    draw.rectangle((560, 438, 638, 592), fill=(110, 67, 38, 255), outline=(70, 43, 28, 255), width=6)
    draw.ellipse((616, 512, 628, 524), fill=(226, 171, 72, 255))
    for x, y in [(735, 432), (875, 394)]:
        draw.rounded_rectangle((x, y, x + 76, y + 64), radius=8, fill=(105, 139, 142, 255), outline=(87, 57, 34, 255), width=6)
        draw.line((x + 38, y + 4, x + 38, y + 60), fill=(87, 57, 34, 180), width=3)
        draw.line((x + 4, y + 32, x + 72, y + 32), fill=(87, 57, 34, 180), width=3)
    draw.rectangle((822, 186, 874, 278), fill=(118, 70, 38, 255), outline=(74, 46, 31, 255), width=5)
    draw.rectangle((814, 172, 882, 202), fill=(92, 54, 34, 255))


def _draw_farm(draw: ImageDraw.ImageDraw) -> None:
    for row in range(3):
        for col in range(4):
            x0 = 420 + col * 112
            y0 = 700 + row * 70
            draw.rounded_rectangle((x0, y0, x0 + 92, y0 + 52), radius=10, fill=(110, 75, 44, 230), outline=(78, 52, 34, 210), width=4)
            draw.line((x0 + 16, y0 + 14, x0 + 76, y0 + 38), fill=(149, 103, 60, 160), width=3)
            draw.line((x0 + 18, y0 + 38, x0 + 74, y0 + 14), fill=(149, 103, 60, 120), width=3)


def _draw_well(draw: ImageDraw.ImageDraw) -> None:
    draw.ellipse((1120, 570, 1260, 650), fill=(122, 104, 81, 255), outline=(65, 52, 43, 255), width=8)
    draw.ellipse((1142, 590, 1238, 632), fill=(65, 95, 104, 255))
    draw.line((1132, 575, 1132, 455), fill=(99, 62, 34, 255), width=12)
    draw.line((1248, 575, 1248, 455), fill=(99, 62, 34, 255), width=12)
    draw.line((1118, 464, 1262, 464), fill=(99, 62, 34, 255), width=12)
    draw.polygon([(1110, 456), (1190, 396), (1270, 456)], fill=(114, 67, 38, 255), outline=(70, 45, 31, 255))


def _draw_mailbox(draw: ImageDraw.ImageDraw) -> None:
    draw.line((328, 548, 328, 632), fill=(91, 58, 34, 255), width=10)
    draw.rounded_rectangle((282, 496, 378, 558), radius=18, fill=(161, 76, 54, 255), outline=(89, 53, 35, 255), width=6)
    draw.rectangle((354, 514, 386, 538), fill=(215, 178, 91, 255), outline=(89, 53, 35, 255), width=3)


def _draw_fence(draw: ImageDraw.ImageDraw) -> None:
    for x in range(350, 760, 58):
        draw.rounded_rectangle((x, 652, x + 16, 738), radius=7, fill=(125, 77, 41, 255), outline=(78, 49, 31, 220), width=3)
    draw.line((342, 684, 770, 708), fill=(132, 82, 43, 255), width=14)
    draw.line((348, 724, 766, 748), fill=(116, 70, 38, 255), width=10)
    for x in range(1040, 1440, 62):
        draw.rounded_rectangle((x, 688, x + 16, 768), radius=7, fill=(125, 77, 41, 255), outline=(78, 49, 31, 220), width=3)
    draw.line((1032, 716, 1454, 726), fill=(132, 82, 43, 255), width=12)


def _draw_flowers(draw: ImageDraw.ImageDraw) -> None:
    for i in range(190):
        x = 140 + ((i * 73) % 1600)
        y = 410 + ((i * 47) % 520)
        if 380 < x < 830 and 640 < y < 960:
            continue
        color = [(220, 169, 69), (207, 118, 92), (229, 207, 120), (136, 153, 75)][i % 4]
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color + (185,))
        draw.line((x, y + 3, x, y + 12), fill=(83, 124, 61, 130), width=2)


def _build_images() -> tuple[Image.Image, Image.Image, Image.Image, Image.Image]:
    base = _paper_noise(CANVAS_SIZE, (143, 164, 98))
    draw = ImageDraw.Draw(base, "RGBA")
    for band_y, color in [(0, (113, 133, 76, 75)), (880, (101, 124, 78, 80))]:
        draw.rectangle((0, band_y, CANVAS_SIZE[0], band_y + 210), fill=color)
    draw.ellipse((1340, 448, 1740, 782), fill=(80, 133, 143, 210), outline=(61, 101, 114, 180), width=8)
    _draw_path(draw, [(0, 625), (310, 608), (560, 620), (840, 602), (1120, 640), (1460, 704), (1920, 740)], 86)
    _draw_path(draw, [(630, 594), (610, 676), (598, 762), (600, 930), (624, 1080)], 58)
    _draw_path(draw, [(1050, 626), (1130, 608), (1194, 594)], 42)
    _draw_farm(draw)
    _draw_house(draw)
    _draw_well(draw)
    _draw_mailbox(draw)
    _draw_fence(draw)
    _draw_flowers(draw)

    foreground = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    fg = ImageDraw.Draw(foreground, "RGBA")
    for tree in [(190, 478, 1.25, False), (1560, 470, 1.35, True), (1710, 690, 1.1, False), (260, 880, 1.05, False), (1490, 910, 1.2, False)]:
        _draw_tree(fg, tree[0], tree[1], tree[2], tree[3])
    fg.polygon([(462, 327), (525, 258), (820, 216), (704, 412)], fill=(48, 72, 76, 250), outline=(42, 48, 43, 230))
    for x in range(360, 760, 58):
        fg.rounded_rectangle((x, 652, x + 16, 710), radius=7, fill=(125, 77, 41, 230))
    for x in range(1050, 1440, 62):
        fg.rounded_rectangle((x, 688, x + 16, 740), radius=7, fill=(125, 77, 41, 230))
    foreground = foreground.filter(ImageFilter.GaussianBlur(0.15))

    mother = Image.alpha_composite(base, foreground)
    mother_draw = ImageDraw.Draw(mother, "RGBA")
    mother_draw.rounded_rectangle((34, 34, 482, 118), radius=22, fill=(232, 210, 160, 230), outline=(91, 55, 34, 255), width=6)
    mother_draw.text((62, 60), "GREENFIELD P0 HOME AREA", fill=(62, 43, 27, 255))

    mask = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(mask, "RGBA")
    for box in [
        (438, 244, 1034, 646),
        (1100, 410, 1286, 658),
        (132, 298, 318, 514),
        (1488, 280, 1646, 506),
        (1648, 534, 1776, 728),
        (202, 724, 322, 924),
        (1440, 760, 1588, 980),
        (338, 646, 780, 760),
        (1030, 682, 1466, 780),
    ]:
        mask_draw.rounded_rectangle(box, radius=18, fill=(255, 255, 255, 255))
    return mother, base, foreground, mask


def _write_interaction_points() -> None:
    points = {
        "package": "greenfield_p0_home_area_v001",
        "canvas_size": list(CANVAS_SIZE),
        "style_reference": STYLE_REFERENCE,
        "coordinate_space": "shared_full_canvas_origin_top_left",
        "points": [
            {
                "id": "home_door",
                "type": "door",
                "name": "Home Door",
                "position": [595, 603],
                "shape": {"type": "rectangle", "size": [88, 56]},
                "hint": "Press E to check the cottage door",
                "text": "The cottage smells faintly of sun-warmed wood and clean paper.",
            },
            {
                "id": "old_well",
                "type": "well",
                "name": "Old Well",
                "position": [1192, 628],
                "shape": {"type": "rectangle", "size": [112, 72]},
                "hint": "Press E to listen at the old well",
                "text": "Cool air rises from the stones. The water sounds close today.",
            },
            {
                "id": "mailbox",
                "type": "mailbox",
                "name": "Mailbox",
                "position": [328, 562],
                "shape": {"type": "rectangle", "size": [96, 64]},
                "hint": "Press E to check the mailbox",
                "text": "A folded village note waits inside the red mailbox.",
            },
            {
                "id": "farm_plot_cluster",
                "type": "farm",
                "name": "Spring Plot",
                "position": [592, 804],
                "shape": {"type": "rectangle", "size": [500, 256]},
                "hint": "Press E to inspect the spring plots",
                "text": "The soil is soft enough for the first repaired garden rows.",
            },
        ],
        "npc_points": [
            {"id": "aya_morning", "npc_id": "aya", "position": [980, 680], "facing": "down_left"}
        ],
        "player_spawn": {"id": "default", "position": [715, 690]},
    }
    (ASSET_ROOT / "scene_home_area_interaction_points.json").write_text(
        json.dumps(points, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_manifest() -> None:
    manifest = {
        "package": "greenfield_p0_home_area_v001",
        "status": "review_ready_placeholder",
        "launch_quality_approved": False,
        "human_visual_approval_required": True,
        "style_reference": STYLE_REFERENCE,
        "canvas_size": list(CANVAS_SIZE),
        "shared_origin": [0, 0],
        "registration_contract": "mother/base/foreground_occlusion/collision_mask share full canvas and origin",
        "assets": {
            "mother": "assets/scenes/home_area/scene_home_area_mother.png",
            "base": "assets/scenes/home_area/scene_home_area_base.png",
            "foreground_occlusion": "assets/scenes/home_area/scene_home_area_foreground_occlusion.png",
            "collision_mask": "assets/scenes/home_area/scene_home_area_collision_mask.png",
            "interaction_points": "assets/scenes/home_area/scene_home_area_interaction_points.json",
        },
    }
    (ASSET_ROOT / "home_area_scene_manifest_v001.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    mother, base, foreground, mask = _build_images()
    mother.save(ASSET_ROOT / "scene_home_area_mother.png")
    base.save(ASSET_ROOT / "scene_home_area_base.png")
    foreground.save(ASSET_ROOT / "scene_home_area_foreground_occlusion.png")
    mask.save(ASSET_ROOT / "scene_home_area_collision_mask.png")
    _write_interaction_points()
    _write_manifest()
    print("OK: generated Greenfield P0 HomeArea scene package")


if __name__ == "__main__":
    main()
