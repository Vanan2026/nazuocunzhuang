from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets/art/greenfield_p0/playable_scene_polish"
STYLE_REFERENCE = "production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg"


def _lerp(left: int, right: int, amount: float) -> int:
    return int(left + (right - left) * amount)


def _vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    pixels = image.load()
    for y in range(height):
        amount = y / max(1, height - 1)
        color = tuple(_lerp(top[i], bottom[i], amount) for i in range(3)) + (255,)
        for x in range(width):
            pixels[x, y] = color
    return image


def _paper_noise(size: tuple[int, int], alpha: int = 18) -> Image.Image:
    width, height = size
    noise = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(noise)
    for y in range(0, height, 3):
        for x in range(0, width, 3):
            value = 220 + ((x * 17 + y * 11) % 25)
            draw.rectangle((x, y, x + 2, y + 2), fill=(value, value, value, alpha))
    return noise.filter(ImageFilter.GaussianBlur(0.7))


def _soft_polygon(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: tuple[int, int, int, int]) -> None:
    draw.polygon([(round(x), round(y)) for x, y in points], fill=fill)


def _draw_brush_path(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    width: int,
    fill: tuple[int, int, int, int],
    highlight: tuple[int, int, int, int],
) -> None:
    draw.line(points, width=width, fill=fill, joint="curve")
    draw.line(points, width=max(2, width // 4), fill=highlight, joint="curve")


def _generate_house() -> dict[str, object]:
    width, height = 704, 440
    image = _vertical_gradient((width, height), (153, 123, 86), (218, 178, 119))
    image.alpha_composite(_paper_noise((width, height), 16))
    draw = ImageDraw.Draw(image, "RGBA")

    floor = [(96, 92), (628, 78), (660, 328), (114, 370), (48, 198)]
    _soft_polygon(draw, floor, (196, 148, 91, 210))
    for offset in range(0, 520, 38):
        x0 = 80 + offset
        draw.line([(x0, 101), (x0 - 74, 358)], fill=(131, 88, 54, 70), width=2)
    for offset in range(0, 300, 34):
        draw.line([(79, 121 + offset), (642, 90 + offset)], fill=(116, 78, 48, 54), width=2)

    draw.rounded_rectangle((34, 42, 180, 192), radius=14, fill=(93, 62, 44, 238))
    draw.rounded_rectangle((52, 64, 164, 174), radius=12, fill=(185, 131, 85, 245))
    draw.rounded_rectangle((64, 76, 152, 108), radius=8, fill=(235, 197, 137, 150))
    draw.rounded_rectangle((432, 32, 582, 178), radius=12, fill=(93, 63, 44, 232))
    draw.rounded_rectangle((454, 54, 560, 146), radius=9, fill=(244, 201, 119, 115))
    draw.line([(506, 54), (506, 146)], fill=(91, 58, 38, 160), width=3)
    draw.line([(454, 100), (560, 100)], fill=(91, 58, 38, 130), width=3)
    draw.polygon([(428, 56), (214, 112), (356, 330), (656, 230), (560, 106)], fill=(255, 213, 132, 40))

    draw.rounded_rectangle((124, 222, 248, 306), radius=16, fill=(104, 67, 48, 235))
    draw.rounded_rectangle((140, 210, 264, 286), radius=16, fill=(191, 130, 94, 235))
    draw.rounded_rectangle((356, 236, 512, 300), radius=10, fill=(104, 62, 38, 230))
    draw.rounded_rectangle((374, 218, 494, 264), radius=8, fill=(172, 111, 69, 235))
    draw.rounded_rectangle((388, 202, 482, 222), radius=8, fill=(232, 199, 134, 235))
    draw.ellipse((72, 272, 238, 356), fill=(138, 75, 68, 135))
    draw.ellipse((86, 286, 224, 344), fill=(186, 112, 91, 170))

    for sx, sy in [(294, 142), (318, 154), (338, 136), (590, 206), (616, 226)]:
        draw.line((sx, sy + 22, sx, sy + 48), fill=(73, 53, 35, 180), width=3)
        draw.ellipse((sx - 18, sy - 10, sx + 18, sy + 18), fill=(86, 124, 62, 145))
        draw.ellipse((sx - 11, sy - 5, sx + 11, sy + 12), fill=(126, 151, 72, 160))
    for sx, sy in [(286, 202), (306, 214), (556, 258), (578, 250), (604, 264)]:
        draw.ellipse((sx - 3, sy - 3, sx + 3, sy + 3), fill=(221, 162, 77, 150))

    for i in range(22):
        angle = i * 0.9
        x = 120 + math.cos(angle) * (42 + (i % 4) * 8)
        y = 52 + math.sin(angle) * (18 + (i % 3) * 5)
        draw.ellipse((x - 3, y - 2, x + 3, y + 2), fill=(231, 194, 135, 80))

    image = image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=70, threshold=4))
    path = OUTPUT_DIR / "player_house_warm_room_v001.png"
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": [width, height], "role": "play_start_house_background"}


def _generate_yard() -> dict[str, object]:
    width, height = 1000, 680
    image = _vertical_gradient((width, height), (121, 151, 93), (184, 172, 114))
    image.alpha_composite(_paper_noise((width, height), 20))
    draw = ImageDraw.Draw(image, "RGBA")

    _soft_polygon(draw, [(320, 176), (454, 156), (516, 246), (418, 330), (306, 298), (260, 224)], (172, 134, 86, 118))
    _soft_polygon(draw, [(308, 366), (492, 374), (508, 522), (286, 528), (262, 454)], (94, 61, 39, 150))
    _soft_polygon(draw, [(514, 302), (714, 300), (754, 496), (512, 528), (474, 408)], (100, 136, 78, 120))
    _soft_polygon(draw, [(692, 210), (858, 240), (852, 322), (686, 326)], (74, 118, 75, 125))
    _soft_polygon(draw, [(180, 392), (300, 390), (332, 520), (176, 530), (126, 460)], (132, 110, 75, 130))

    _draw_brush_path(draw, [(426, 284), (500, 270), (600, 300), (702, 354), (806, 348)], 42, (143, 114, 73, 190), (207, 174, 111, 90))
    _draw_brush_path(draw, [(492, 314), (500, 390), (466, 510)], 38, (126, 95, 63, 170), (209, 172, 114, 80))
    _draw_brush_path(draw, [(332, 400), (250, 436), (170, 466)], 34, (120, 92, 62, 150), (205, 169, 114, 80))

    for x in range(300, 490, 38):
        draw.line([(x, 394), (x + 22, 516)], fill=(86, 55, 38, 125), width=5)
    for y in range(398, 520, 34):
        draw.line([(296, y), (496, y + 8)], fill=(181, 128, 76, 70), width=3)

    for cx, cy, r in [(758, 190, 38), (818, 214, 44), (850, 278, 34), (728, 276, 36), (688, 230, 30)]:
        draw.ellipse((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), fill=(55, 105, 67, 145))
        draw.ellipse((cx - r * 0.65, cy - r * 0.48, cx + r * 0.65, cy + r * 0.48), fill=(91, 139, 82, 135))

    roof = [(342, 126), (462, 100), (552, 174), (436, 214)]
    house = [(360, 170), (492, 148), (526, 246), (386, 282)]
    draw.polygon(roof, fill=(72, 92, 86, 210))
    draw.line(roof + [roof[0]], fill=(61, 45, 33, 180), width=4)
    draw.polygon(house, fill=(184, 129, 77, 205))
    draw.line(house + [house[0]], fill=(82, 55, 36, 170), width=3)
    draw.rectangle((424, 192, 468, 252), fill=(91, 55, 35, 220))
    draw.rectangle((382, 184, 416, 214), fill=(230, 194, 118, 130))

    for cx, cy, color in [
        (408, 268, (199, 82, 61, 170)),
        (492, 256, (176, 118, 68, 160)),
        (624, 366, (108, 103, 92, 150)),
        (116, 444, (104, 72, 48, 150)),
    ]:
        draw.ellipse((cx - 18, cy - 10, cx + 18, cy + 10), fill=color)

    for i in range(180):
        x = 80 + ((i * 73) % 850)
        y = 150 + ((i * 41) % 430)
        color = [(230, 196, 116, 95), (190, 116, 94, 85), (95, 138, 75, 95)][i % 3]
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=color)

    image = image.filter(ImageFilter.UnsharpMask(radius=1.4, percent=65, threshold=4))
    path = OUTPUT_DIR / "player_yard_storybook_ground_v001.png"
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": [width, height], "role": "play_start_yard_background"}


def _generate_bulletin_board() -> dict[str, object]:
    width, height = 160, 160
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")

    draw.ellipse((42, 120, 120, 140), fill=(55, 36, 25, 48))
    draw.rounded_rectangle((38, 34, 122, 102), radius=8, fill=(112, 68, 38, 255))
    draw.rounded_rectangle((46, 42, 114, 94), radius=5, fill=(172, 119, 68, 255))
    draw.rectangle((72, 94, 88, 132), fill=(91, 56, 34, 255))
    draw.rectangle((66, 126, 94, 136), fill=(79, 49, 31, 255))
    for index, rect in enumerate([(54, 50, 80, 70), (86, 50, 106, 76), (58, 76, 102, 88)]):
        color = [(238, 210, 151, 238), (229, 188, 131, 238), (246, 225, 166, 238)][index]
        draw.rounded_rectangle(rect, radius=2, fill=color)
        x0, y0, x1, _y1 = rect
        draw.line((x0 + 5, y0 + 7, x1 - 5, y0 + 7), fill=(107, 74, 45, 130), width=1)
    draw.ellipse((50, 48, 56, 54), fill=(93, 55, 36, 210))
    draw.ellipse((92, 48, 98, 54), fill=(93, 55, 36, 210))
    draw.arc((30, 22, 130, 116), 195, 340, fill=(244, 206, 128, 70), width=3)

    path = OUTPUT_DIR / "player_yard_bulletin_board_v001.png"
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": [width, height], "role": "play_start_yard_bulletin_prop"}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "package": "playable_scene_polish_v001",
        "status": "runtime_review_ready",
        "launch_quality_approved": False,
        "human_visual_approval_required": True,
        "style_reference": STYLE_REFERENCE,
        "style": "match the Greenfield P0 style mother: warm low-saturation storybook 3/4 top-down, dense garden detail, paper and wood UI language",
        "assets": [_generate_house(), _generate_yard(), _generate_bulletin_board()],
    }
    (OUTPUT_DIR / "playable_scene_polish_manifest_v001.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("OK: generated playable scene polish assets")


if __name__ == "__main__":
    main()
