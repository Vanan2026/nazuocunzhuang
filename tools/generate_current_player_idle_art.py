from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sprites" / "characters" / "protagonist" / "frames" / "player_idle_down_00.png"
OUTPUT = ROOT / "assets" / "art" / "greenfield_p0" / "characters" / "player" / "chr_player_base_idle_down_128.png"
CANVAS = (128, 128)
BODY_SIZE = (37, 94)
BODY_TOP = 18


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    bbox = source.getchannel("A").getbbox()
    if bbox is None:
        raise RuntimeError(f"source alpha is empty: {SOURCE}")
    body = source.crop(bbox).resize(BODY_SIZE, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    shadow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.ellipse((39, 102, 89, 110), fill=(42, 35, 28, 76))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=1.0))
    canvas.alpha_composite(shadow)

    body_left = (CANVAS[0] - BODY_SIZE[0]) // 2
    canvas.alpha_composite(body, (body_left, BODY_TOP))
    pixels = canvas.load()
    for y in range(CANVAS[1]):
        for x in range(CANVAS[0]):
            red, green, blue, alpha = pixels[x, y]
            if alpha < 12:
                pixels[x, y] = (red, green, blue, 0)
    canvas.save(OUTPUT)
    print(f"OK: generated {OUTPUT.relative_to(ROOT).as_posix()} from {SOURCE.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
