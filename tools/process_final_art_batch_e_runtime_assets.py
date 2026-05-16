from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
FINAL_ART = ROOT / "production" / "assets" / "final_art"
BATCH_E_DIR = FINAL_ART / "batch_e_runtime_ui_weather_crops"
RUNTIME_NPC_DIR = ROOT / "assets" / "art" / "characters" / "npc"
RUNTIME_PORTRAIT_DIR = ROOT / "assets" / "art" / "portraits"
RUNTIME_ICON_DIR = ROOT / "assets" / "art" / "icons"
RUNTIME_CROP_DIR = ROOT / "assets" / "art" / "crops"
RUNTIME_UI_DIR = ROOT / "assets" / "art" / "ui"
RUNTIME_ITEM_DIR = ROOT / "assets" / "art" / "items"


NPC_RUNTIME_FILES = [
    "npc_aoi_idle_down_128.png",
    "npc_gen_idle_down_128.png",
    "npc_mika_idle_down_128.png",
]

PORTRAIT_RUNTIME_FILES = [
    "npc_aoi_portrait_neutral_512.png",
    "npc_gen_portrait_neutral_512.png",
    "npc_mika_portrait_neutral_512.png",
]

WEATHER_COLORS = {
    "sunny": {"sky": (247, 202, 111), "mark": (255, 238, 154)},
    "cloudy": {"sky": (166, 190, 190), "mark": (232, 231, 211)},
    "rainy": {"sky": (112, 145, 160), "mark": (132, 188, 203)},
}

CROP_COLORS = {
    "turnip": (236, 232, 218),
    "strawberry": (199, 74, 72),
    "potato": (174, 132, 82),
    "cucumber": (82, 150, 89),
    "tomato": (207, 81, 64),
    "watermelon": (71, 139, 84),
    "pumpkin": (213, 142, 65),
    "daikon": (235, 237, 224),
}


def ensure_dirs() -> None:
    for directory in [
        BATCH_E_DIR,
        RUNTIME_NPC_DIR,
        RUNTIME_PORTRAIT_DIR,
        RUNTIME_ICON_DIR,
        RUNTIME_CROP_DIR,
        RUNTIME_UI_DIR,
        RUNTIME_ITEM_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def copy_npc_runtime_assets(manifest: list[dict[str, object]]) -> None:
    source_dir = FINAL_ART / "characters" / "npc"
    for filename in NPC_RUNTIME_FILES:
        src = source_dir / filename
        dst = RUNTIME_NPC_DIR / filename
        shutil.copy2(src, dst)
        manifest.append({"file": str(dst.relative_to(ROOT)).replace("\\", "/"), "source": str(src.relative_to(ROOT)).replace("\\", "/"), "role": "npc_idle"})
    for filename in PORTRAIT_RUNTIME_FILES:
        src = source_dir / filename
        dst = RUNTIME_PORTRAIT_DIR / filename
        shutil.copy2(src, dst)
        manifest.append({"file": str(dst.relative_to(ROOT)).replace("\\", "/"), "source": str(src.relative_to(ROOT)).replace("\\", "/"), "role": "npc_portrait"})


def draw_weather_icons(manifest: list[dict[str, object]]) -> None:
    for weather_id, colors in WEATHER_COLORS.items():
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        sky = colors["sky"]
        mark = colors["mark"]
        draw.rounded_rectangle((8, 8, 56, 56), radius=14, fill=(*sky, 235), outline=(92, 101, 85, 210), width=2)
        if weather_id == "sunny":
            draw.ellipse((22, 20, 42, 40), fill=(*mark, 255), outline=(141, 112, 53, 220), width=2)
            for x0, y0, x1, y1 in [(32, 12, 32, 17), (32, 43, 32, 49), (15, 30, 20, 30), (44, 30, 50, 30)]:
                draw.line((x0, y0, x1, y1), fill=(141, 112, 53, 220), width=3)
        elif weather_id == "cloudy":
            draw.ellipse((18, 26, 38, 42), fill=(*mark, 255))
            draw.ellipse((28, 20, 48, 42), fill=(*mark, 255))
            draw.rounded_rectangle((17, 31, 50, 45), radius=7, fill=(*mark, 255), outline=(106, 124, 118, 220), width=2)
        else:
            draw.ellipse((17, 17, 38, 35), fill=(221, 225, 213, 255))
            draw.ellipse((29, 14, 49, 36), fill=(221, 225, 213, 255))
            draw.rounded_rectangle((16, 25, 51, 39), radius=7, fill=(221, 225, 213, 255), outline=(90, 118, 126, 220), width=2)
            for x, y in [(23, 43), (34, 47), (45, 43)]:
                draw.line((x, y, x - 3, y + 8), fill=(*mark, 255), width=3)
        save_pair(image, f"weather_{weather_id}_64.png", RUNTIME_ICON_DIR, manifest, "weather_icon")


def draw_crop_stages(manifest: list[dict[str, object]]) -> None:
    for crop_name, crop_color in CROP_COLORS.items():
        for stage in range(4):
            image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.ellipse((12, 43, 52, 58), fill=(103, 79, 54, 210))
            stem_height = 8 + stage * 8
            draw.line((32, 46, 32, 46 - stem_height), fill=(82, 130, 73, 255), width=4)
            leaf_span = 7 + stage * 4
            draw.ellipse((32 - leaf_span, 37 - stage * 6, 32, 48 - stage * 6), fill=(91, 151, 85, 255))
            draw.ellipse((32, 37 - stage * 6, 32 + leaf_span, 48 - stage * 6), fill=(105, 160, 91, 255))
            if stage >= 2:
                radius = 5 + stage * 2
                draw.ellipse((32 - radius, 28 - stage * 3, 32 + radius, 28 - stage * 3 + radius * 2), fill=(*crop_color, 255), outline=(91, 89, 65, 190), width=1)
            save_pair(image, f"crop_{crop_name}_stage_{stage:02d}_64.png", RUNTIME_CROP_DIR, manifest, "crop_stage")

        item_icon = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(item_icon)
        draw.rounded_rectangle((12, 14, 52, 52), radius=12, fill=(*crop_color, 255), outline=(91, 89, 65, 190), width=2)
        draw.arc((22, 5, 46, 30), start=205, end=330, fill=(83, 136, 75, 255), width=4)
        save_pair(item_icon, f"crop_{crop_name}_64.png", RUNTIME_ITEM_DIR, manifest, "crop_item_icon")


def draw_ui_pieces(manifest: list[dict[str, object]]) -> None:
    panel = Image.new("RGBA", (256, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((4, 4, 252, 124), radius=8, fill=(238, 226, 202, 245), outline=(124, 98, 70, 230), width=3)
    draw.rounded_rectangle((12, 12, 244, 116), radius=6, outline=(202, 178, 141, 190), width=2)
    save_pair(panel, "ui_panel_paper_256x128.png", RUNTIME_UI_DIR, manifest, "ui_panel")

    button = Image.new("RGBA", (128, 48), (0, 0, 0, 0))
    draw = ImageDraw.Draw(button)
    draw.rounded_rectangle((4, 6, 124, 42), radius=7, fill=(151, 99, 59, 245), outline=(80, 55, 36, 230), width=3)
    draw.line((15, 18, 113, 17), fill=(194, 139, 87, 180), width=2)
    draw.line((18, 31, 110, 30), fill=(104, 68, 43, 150), width=2)
    save_pair(button, "ui_button_wood_128x48.png", RUNTIME_UI_DIR, manifest, "ui_button")


def save_pair(image: Image.Image, filename: str, runtime_dir: Path, manifest: list[dict[str, object]], role: str) -> None:
    runtime_path = runtime_dir / filename
    production_path = BATCH_E_DIR / filename
    image.save(runtime_path)
    image.save(production_path)
    manifest.append(
        {
            "file": str(runtime_path.relative_to(ROOT)).replace("\\", "/"),
            "production_file": str(production_path.relative_to(ROOT)).replace("\\", "/"),
            "role": role,
            "size_px": {"width": image.width, "height": image.height},
        }
    )


def main() -> None:
    ensure_dirs()
    manifest: list[dict[str, object]] = []
    copy_npc_runtime_assets(manifest)
    draw_weather_icons(manifest)
    draw_crop_stages(manifest)
    draw_ui_pieces(manifest)
    manifest_path = FINAL_ART / "final_art_phase2_batch_e_runtime_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "package_id": "final_art_phase2_batch_e_runtime",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "runtime_replacement": True,
                "assets": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"OK: wrote {len(manifest)} runtime assets and {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
