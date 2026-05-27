from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets/ui"
STYLE_REFERENCE = "production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg"


def _ensure_dirs() -> None:
    for folder in [
        "panels",
        "buttons",
        "slots",
        "tabs",
        "widgets",
        "icons",
    ]:
        (ASSET_ROOT / folder).mkdir(parents=True, exist_ok=True)


def _paper_texture(size: tuple[int, int], base: tuple[int, int, int], alpha: int = 255) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size, base + (alpha,))
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            value = ((x * 13 + y * 17) % 31) - 15
            color = tuple(max(0, min(255, channel + value)) for channel in base)
            draw.rectangle((x, y, x + 3, y + 3), fill=color + (18,))
    return image.filter(ImageFilter.GaussianBlur(0.45))


def _draw_panel(
    path: Path,
    size: tuple[int, int],
    fill: tuple[int, int, int],
    border: tuple[int, int, int],
    inner: tuple[int, int, int],
    vine: bool = True,
) -> dict[str, object]:
    width, height = size
    image = _paper_texture(size, fill)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((8, 8, width - 8, height - 8), radius=24, outline=border + (255,), width=8)
    draw.rounded_rectangle((22, 22, width - 22, height - 22), radius=16, outline=inner + (140,), width=3)
    if vine:
        for corner_x, corner_y, flip_x, flip_y in [
            (24, 24, 1, 1),
            (width - 24, 24, -1, 1),
            (24, height - 24, 1, -1),
            (width - 24, height - 24, -1, -1),
        ]:
            draw.line(
                [(corner_x, corner_y), (corner_x + 42 * flip_x, corner_y + 8 * flip_y)],
                fill=(82, 113, 52, 180),
                width=4,
            )
            for i in range(3):
                lx = corner_x + (14 + i * 12) * flip_x
                ly = corner_y + (4 + (i % 2) * 9) * flip_y
                draw.ellipse((lx - 7, ly - 4, lx + 7, ly + 4), fill=(106, 138, 70, 190))
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": list(size)}


def _draw_button(path: Path, tint: tuple[int, int, int], pressed: bool = False) -> dict[str, object]:
    size = (256, 96)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    offset = 4 if pressed else 0
    draw.rounded_rectangle((10, 12 + offset, 246, 82 + offset), radius=18, fill=(94, 56, 32, 245))
    draw.rounded_rectangle((18, 18 + offset, 238, 76 + offset), radius=14, fill=tint + (255,))
    draw.rounded_rectangle((28, 26 + offset, 228, 68 + offset), radius=10, outline=(246, 218, 150, 100), width=2)
    for x in range(34, 230, 22):
        draw.line((x, 26 + offset, x + 16, 68 + offset), fill=(106, 70, 41, 42), width=1)
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": list(size)}


def _draw_slot(path: Path, selected: bool = False) -> dict[str, object]:
    size = (96, 96)
    image = _paper_texture(size, (226, 194, 134), 255)
    draw = ImageDraw.Draw(image, "RGBA")
    border = (98, 57, 34) if not selected else (156, 91, 40)
    draw.rounded_rectangle((6, 6, 90, 90), radius=12, outline=border + (255,), width=6)
    if selected:
        draw.rounded_rectangle((15, 15, 81, 81), radius=8, outline=(237, 188, 80, 230), width=4)
    else:
        draw.rounded_rectangle((16, 16, 80, 80), radius=8, outline=(132, 91, 55, 95), width=2)
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": list(size)}


def _draw_tab(path: Path, active: bool = False) -> dict[str, object]:
    size = (160, 72)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    fill = (230, 195, 130) if active else (199, 151, 91)
    draw.rounded_rectangle((6, 8, 154, 70), radius=14, fill=(91, 55, 34, 245))
    draw.rounded_rectangle((14, 14, 146, 70), radius=12, fill=fill + (255,))
    draw.line((22, 62, 138, 62), fill=(81, 54, 35, 130), width=2)
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": list(size)}


def _draw_checkbox(path: Path, checked: bool) -> dict[str, object]:
    size = (64, 64)
    image = _paper_texture(size, (224, 190, 128), 255)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((8, 8, 56, 56), radius=10, outline=(91, 55, 34, 255), width=5)
    if checked:
        draw.line((18, 34, 28, 44, 48, 20), fill=(73, 110, 55, 255), width=7)
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": list(size)}


def _draw_scrollbar(path: Path) -> dict[str, object]:
    size = (64, 256)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((24, 12, 40, 244), radius=8, fill=(99, 65, 41, 120))
    draw.rounded_rectangle((14, 72, 50, 146), radius=14, fill=(203, 151, 86, 255), outline=(84, 51, 31, 255), width=4)
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": list(size)}


def _draw_icon(path: Path, kind: str) -> dict[str, object]:
    size = (64, 64)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    if kind == "coin":
        draw.ellipse((10, 10, 54, 54), fill=(220, 159, 48, 255), outline=(101, 68, 30, 255), width=4)
        draw.arc((20, 18, 46, 48), 70, 290, fill=(250, 218, 112, 190), width=4)
    elif kind == "heart":
        draw.pieslice((8, 12, 36, 42), 180, 360, fill=(184, 74, 58, 255))
        draw.pieslice((28, 12, 56, 42), 180, 360, fill=(184, 74, 58, 255))
        draw.polygon([(8, 28), (56, 28), (32, 56)], fill=(184, 74, 58, 255))
        draw.line((18, 22, 32, 44, 48, 22), fill=(117, 47, 37, 170), width=3)
    elif kind == "sun":
        for i in range(12):
            angle = i * math.pi / 6
            draw.line(
                (32, 32, 32 + math.cos(angle) * 27, 32 + math.sin(angle) * 27),
                fill=(207, 147, 42, 200),
                width=3,
            )
        draw.ellipse((18, 18, 46, 46), fill=(236, 184, 71, 255), outline=(124, 82, 32, 255), width=3)
    elif kind == "rain":
        draw.ellipse((12, 18, 48, 42), fill=(139, 166, 170, 240), outline=(70, 98, 106, 210), width=3)
        for x in [18, 30, 42]:
            draw.line((x, 44, x - 5, 56), fill=(83, 137, 165, 230), width=3)
    elif kind == "bag":
        draw.rounded_rectangle((14, 22, 50, 56), radius=8, fill=(145, 89, 48, 255), outline=(75, 46, 31, 255), width=3)
        draw.arc((20, 8, 44, 34), 180, 360, fill=(75, 46, 31, 255), width=4)
    elif kind == "map":
        draw.polygon([(10, 16), (26, 10), (40, 16), (54, 10), (54, 48), (38, 54), (24, 48), (10, 54)], fill=(230, 201, 142, 255), outline=(91, 58, 36, 255))
        draw.line((26, 10, 24, 48), fill=(91, 58, 36, 130), width=2)
        draw.line((40, 16, 38, 54), fill=(91, 58, 36, 130), width=2)
        draw.line((18, 34, 32, 26, 46, 34), fill=(94, 132, 78, 210), width=3)
    elif kind == "settings":
        draw.ellipse((18, 18, 46, 46), fill=(160, 114, 65, 255), outline=(79, 50, 31, 255), width=4)
        draw.ellipse((26, 26, 38, 38), fill=(235, 203, 139, 255))
        for i in range(8):
            angle = i * math.pi / 4
            x = 32 + math.cos(angle) * 23
            y = 32 + math.sin(angle) * 23
            draw.rounded_rectangle((x - 4, y - 4, x + 4, y + 4), radius=2, fill=(79, 50, 31, 255))
    image.save(path)
    return {"path": path.relative_to(ROOT).as_posix(), "size": list(size)}


def main() -> None:
    _ensure_dirs()
    assets: list[dict[str, object]] = []
    assets.append(_draw_panel(ASSET_ROOT / "panels/ui_panel_paper_01.png", (512, 512), (231, 210, 164), (91, 55, 34), (151, 96, 54)))
    assets.append(_draw_panel(ASSET_ROOT / "panels/ui_panel_wood_01.png", (512, 512), (170, 113, 62), (77, 47, 30), (232, 195, 123), vine=False))
    assets.append(_draw_button(ASSET_ROOT / "buttons/ui_button_normal.png", (199, 146, 82)))
    assets.append(_draw_button(ASSET_ROOT / "buttons/ui_button_hover.png", (218, 168, 96)))
    assets.append(_draw_button(ASSET_ROOT / "buttons/ui_button_pressed.png", (168, 114, 67), pressed=True))
    assets.append(_draw_slot(ASSET_ROOT / "slots/ui_slot_item.png"))
    assets.append(_draw_slot(ASSET_ROOT / "slots/ui_slot_selected.png", selected=True))
    assets.append(_draw_tab(ASSET_ROOT / "tabs/ui_tab_normal.png"))
    assets.append(_draw_tab(ASSET_ROOT / "tabs/ui_tab_active.png", active=True))
    assets.append(_draw_scrollbar(ASSET_ROOT / "widgets/ui_scrollbar.png"))
    assets.append(_draw_checkbox(ASSET_ROOT / "widgets/ui_checkbox_on.png", checked=True))
    assets.append(_draw_checkbox(ASSET_ROOT / "widgets/ui_checkbox_off.png", checked=False))
    for name, kind in [
        ("ui_icon_coin", "coin"),
        ("ui_icon_heart", "heart"),
        ("ui_icon_weather_sun", "sun"),
        ("ui_icon_weather_rain", "rain"),
        ("ui_icon_bag", "bag"),
        ("ui_icon_map", "map"),
        ("ui_icon_settings", "settings"),
    ]:
        assets.append(_draw_icon(ASSET_ROOT / f"icons/{name}.png", kind))
    manifest = {
        "package": "greenfield_p0_ui_kit_v001",
        "status": "placeholder_allowed",
        "launch_quality_approved": False,
        "human_visual_approval_required": True,
        "style_reference": STYLE_REFERENCE,
        "assets": assets,
    }
    (ASSET_ROOT / "greenfield_p0_ui_kit_manifest_v001.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("OK: generated Greenfield P0 UI kit assets")


if __name__ == "__main__":
    main()
