from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
VILLAGE_SOURCE = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001" / "02_source_generation" / "village_painted_source.png"
MOUNTAIN_HUT_SOURCE = ROOT / "production" / "assets" / "regions" / "mountain_hut_world2d" / "v001" / "02_source_generation" / "mountain_hut_painted_source.png"
OUTPUT = ROOT / ".codex" / "reports" / "mountain_hut_village_seam_preview_2026-05-24.png"
REPORT = ROOT / ".codex" / "reports" / "mountain_hut_village_seam_review_2026-05-24.md"

CANVAS = (1800, 1200)
CROP_W = 520
CROP_H = 520


def load_source(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if image.size != CANVAS:
        raise SystemExit(f"{path.relative_to(ROOT).as_posix()} size mismatch: {image.size}")
    return image


def crop_village_east(image: Image.Image) -> Image.Image:
    # Source-space crop around the Village east seam connector.
    return image.crop((CANVAS[0] - CROP_W, 380, CANVAS[0], 380 + CROP_H))


def crop_hut_west(image: Image.Image) -> Image.Image:
    # Source-space crop around the MountainHut west seam connector.
    return image.crop((0, 420, CROP_W, 420 + CROP_H))


def edge_average(image: Image.Image, side: str) -> tuple[float, float, float]:
    if side == "right":
        crop = image.crop((image.width - 40, 0, image.width, image.height))
    else:
        crop = image.crop((0, 0, 40, image.height))
    stat = ImageStat.Stat(crop)
    return tuple(float(v) for v in stat.mean)


def color_delta(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum(abs(a[i] - b[i]) for i in range(3)) / 3.0


def main() -> None:
    village = crop_village_east(load_source(VILLAGE_SOURCE))
    hut = crop_hut_west(load_source(MOUNTAIN_HUT_SOURCE))
    output = Image.new("RGB", (CROP_W * 2 + 64, CROP_H + 120), (238, 226, 200))
    output.paste(village, (24, 76))
    output.paste(hut, (CROP_W + 40, 76))

    draw = ImageDraw.Draw(output)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        small = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    draw.text((24, 22), "Village east source crop", fill=(52, 43, 31), font=font)
    draw.text((CROP_W + 40, 22), "MountainHut west source crop", fill=(52, 43, 31), font=font)
    draw.line((CROP_W + 32, 76, CROP_W + 32, CROP_H + 76), fill=(80, 60, 42), width=4)
    draw.text((24, CROP_H + 92), "Offline seam preview only. Runtime replacement remains blocked.", fill=(74, 58, 40), font=small)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    output.save(OUTPUT)

    village_edge = edge_average(village, "right")
    hut_edge = edge_average(hut, "left")
    delta = color_delta(village_edge, hut_edge)
    REPORT.write_text(
        f"""# MountainHut / Village Seam Review - 2026-05-24

## Preview

- Image: `.codex/reports/mountain_hut_village_seam_preview_2026-05-24.png`

## Automated Read

- Village east edge RGB mean: `{tuple(round(v, 2) for v in village_edge)}`
- MountainHut west edge RGB mean: `{tuple(round(v, 2) for v in hut_edge)}`
- Average channel delta: `{delta:.2f}`

## Human Review Notes

- This is an offline source-crop preview, not a Godot runtime screenshot.
- The MountainHut west path is readable and enters from the same side as the OutdoorWorld seam.
- The candidate still needs human/art review for final storybook quality and exact Village style continuity.
- Runtime replacement remains blocked.
""",
        encoding="utf-8",
    )
    print(f"OK: wrote {OUTPUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
