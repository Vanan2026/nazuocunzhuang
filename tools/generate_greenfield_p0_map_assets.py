from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "ui" / "maps"
MAP_PATH = OUTPUT_DIR / "ui_map_village_paper_01.png"
MANIFEST_PATH = OUTPUT_DIR / "greenfield_p0_map_assets_manifest_v001.json"
STYLE_REFERENCE = "production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg"


def _draw_soft_path(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], width: int, fill: tuple[int, int, int, int]) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")
    draw.line(points, fill=(201, 166, 103, 210), width=max(2, width // 3), joint="curve")


def _draw_tree(draw: ImageDraw.ImageDraw, x: int, y: int, scale: int = 1) -> None:
    trunk = (111, 79, 45, 255)
    leaf = (103, 128, 62, 235)
    shadow = (73, 89, 52, 170)
    draw.rectangle((x - 2 * scale, y, x + 2 * scale, y + 12 * scale), fill=trunk)
    draw.ellipse((x - 16 * scale, y - 24 * scale, x + 16 * scale, y + 8 * scale), fill=shadow)
    draw.ellipse((x - 14 * scale, y - 28 * scale, x + 12 * scale, y + 5 * scale), fill=leaf)
    draw.ellipse((x - 8 * scale, y - 34 * scale, x + 18 * scale, y - 2 * scale), fill=(128, 146, 72, 230))


def _draw_house(draw: ImageDraw.ImageDraw, x: int, y: int, color: tuple[int, int, int, int]) -> None:
    outline = (91, 62, 39, 255)
    roof = (86, 111, 116, 255)
    draw.polygon([(x - 34, y - 2), (x, y - 34), (x + 36, y - 2)], fill=roof, outline=outline)
    draw.rectangle((x - 26, y - 2, x + 28, y + 34), fill=color, outline=outline, width=2)
    draw.rectangle((x - 4, y + 10, x + 10, y + 34), fill=(113, 78, 45, 255), outline=outline)
    draw.rectangle((x - 21, y + 7, x - 9, y + 20), fill=(235, 209, 147, 255), outline=outline)


def generate() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 1024, 640
    image = Image.new("RGBA", (width, height), (232, 205, 148, 255))
    grain = Image.effect_noise((width, height), 18).convert("L")
    image.putalpha(Image.new("L", (width, height), 255))
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay.putalpha(grain.point(lambda v: max(0, min(34, int(v / 6)))))
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((18, 16, width - 18, height - 16), radius=28, fill=(235, 211, 157, 245), outline=(102, 70, 42, 255), width=6)
    draw.rounded_rectangle((42, 40, width - 42, height - 40), radius=20, fill=(222, 194, 131, 180), outline=(158, 116, 62, 220), width=2)

    water = [(120, 500), (220, 464), (330, 490), (470, 452), (620, 480), (780, 430), (930, 456)]
    draw.line(water, fill=(85, 132, 143, 210), width=42, joint="curve")
    draw.line(water, fill=(122, 162, 163, 210), width=20, joint="curve")

    _draw_soft_path(draw, [(155, 505), (275, 412), (410, 350), (535, 284), (710, 205), (870, 154)], 34, (174, 136, 82, 230))
    _draw_soft_path(draw, [(315, 130), (406, 248), (535, 284), (616, 382), (724, 488)], 28, (174, 136, 82, 225))
    _draw_soft_path(draw, [(214, 338), (410, 350), (596, 322), (830, 340)], 24, (174, 136, 82, 220))

    for x, y, scale in [
        (98, 132, 2), (144, 176, 2), (196, 136, 1), (820, 90, 2), (900, 110, 2),
        (860, 250, 1), (125, 420, 2), (888, 470, 2), (760, 520, 1), (650, 96, 1),
    ]:
        _draw_tree(draw, x, y, scale)

    _draw_house(draw, 310, 128, (190, 145, 88, 255))
    _draw_house(draw, 540, 278, (193, 156, 104, 255))
    _draw_house(draw, 728, 190, (183, 135, 86, 255))
    _draw_house(draw, 810, 338, (172, 128, 86, 255))
    _draw_house(draw, 708, 488, (188, 139, 82, 255))

    farm_fill = (122, 126, 66, 225)
    for rect in [(208, 315, 282, 380), (292, 305, 370, 372), (376, 298, 452, 362)]:
        draw.rounded_rectangle(rect, radius=8, fill=farm_fill, outline=(91, 73, 38, 210), width=2)
        for x in range(rect[0] + 10, rect[2] - 6, 18):
            draw.line((x, rect[1] + 6, x - 16, rect[3] - 6), fill=(84, 94, 54, 180), width=2)

    draw.ellipse((586, 332, 656, 402), fill=(106, 145, 137, 210), outline=(70, 92, 86, 255), width=3)
    draw.ellipse((604, 348, 638, 382), fill=(75, 119, 126, 230))

    for i, (x, y) in enumerate([(310, 128), (540, 278), (728, 190), (810, 338), (708, 488), (622, 366), (245, 344), (875, 154), (155, 505), (878, 470)], 1):
        draw.ellipse((x - 19, y - 50, x + 19, y - 12), fill=(245, 229, 176, 255), outline=(101, 68, 39, 255), width=3)
        draw.text((x - 5, y - 44), str(i), fill=(81, 50, 31, 255))

    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rounded_rectangle((0, 0, width, height), radius=32, outline=(95, 62, 37, 70), width=18)
    image = Image.alpha_composite(image, vignette).filter(ImageFilter.SMOOTH_MORE)
    image.save(MAP_PATH)

    manifest = {
        "style_reference": STYLE_REFERENCE,
        "assets": [
            {
                "path": "assets/ui/maps/ui_map_village_paper_01.png",
                "size": [width, height],
                "status": "review_ready_placeholder",
                "purpose": "P0 paper village map background for MapScreen",
            }
        ],
        "launch_quality_approved": False,
        "human_visual_approval_required": True,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {MAP_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    generate()
