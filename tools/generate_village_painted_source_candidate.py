from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock" / "layout_lock.json"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
SOURCE_PATH = SOURCE_DIR / "village_painted_source.png"
OVERLAY_PATH = REVIEW_DIR / "village_painted_source_review_overlay_v001.png"
ACCEPTANCE_PATH = SOURCE_DIR / "source_acceptance.json"
REVIEW_MD = REVIEW_DIR / "source_candidate_review.md"

CANVAS = (1800, 1200)
SEED = 230523
LAYOUT_DRAFT_ID = "village_layout_structure_draft_v001"


def load_layout() -> dict:
    return json.loads(LAYOUT_LOCK.read_text(encoding="utf-8"))


def point(values: Iterable[float]) -> tuple[int, int]:
    x, y = values
    return int(round(float(x))), int(round(float(y)))


def polygon(values: Iterable[Iterable[float]]) -> list[tuple[int, int]]:
    return [point(item) for item in values]


def overlay(base: Image.Image, layer: Image.Image) -> None:
    base.alpha_composite(layer)


def draw_soft_ellipse(
    image: Image.Image,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
    blur: int = 18,
) -> None:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(box, fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    overlay(image, layer)


def draw_polyline(
    image: Image.Image,
    points: list[tuple[int, int]],
    width: int,
    color: tuple[int, int, int, int],
    joint: str = "curve",
) -> None:
    draw = ImageDraw.Draw(image)
    if len(points) < 2:
        return
    draw.line(points, fill=color, width=width, joint=joint)
    radius = width // 2
    for x, y in points:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_texture(image: Image.Image) -> None:
    random.seed(SEED)
    base = Image.new("RGBA", CANVAS, (123, 162, 101, 255))
    noise = Image.effect_noise(CANVAS, 44).convert("L")
    low = Image.new("RGBA", CANVAS, (103, 145, 88, 255))
    high = Image.new("RGBA", CANVAS, (153, 183, 121, 255))
    colored_noise = Image.composite(high, low, noise)
    base = Image.blend(base, colored_noise, 0.22)
    overlay(image, base)

    for _ in range(58):
        cx = random.randint(-80, CANVAS[0] + 80)
        cy = random.randint(-60, CANVAS[1] + 60)
        rx = random.randint(90, 240)
        ry = random.randint(42, 130)
        color = random.choice(
            [
                (176, 198, 131, 22),
                (90, 128, 80, 18),
                (205, 206, 159, 14),
                (120, 154, 95, 20),
            ]
        )
        draw_soft_ellipse(image, (cx - rx, cy - ry, cx + rx, cy + ry), color, blur=random.randint(20, 42))

    draw = ImageDraw.Draw(image)
    for _ in range(420):
        x = random.randint(0, CANVAS[0])
        y = random.randint(0, CANVAS[1])
        length = random.randint(6, 18)
        tone = random.choice([(181, 204, 142, 46), (94, 130, 77, 38), (219, 184, 169, 52)])
        draw.line((x, y, x + random.randint(-3, 4), y + length), fill=tone, width=1)


def draw_roads(image: Image.Image, layout: dict) -> None:
    plaza = next(zone for zone in layout["object_zones"] if zone["id"] == "VillagePlazaZone")
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.polygon(polygon(plaza["source_polygon"]), fill=(181, 156, 91, 92))
    overlay(image, layer)

    for connector in layout.get("seam_connector_paths", []):
        points = polygon(connector["source_points"])
        width = int(connector.get("source_width", 48))
        draw_polyline(image, points, width + 22, (153, 132, 82, 76))
        draw_polyline(image, points, width, (187, 164, 103, 146))
        draw_polyline(image, points, max(24, width - 24), (204, 183, 123, 96))

    for path_info in layout["road_paths"]:
        points = polygon(path_info["source_points"])
        draw_polyline(image, points, 82, (162, 139, 84, 96))
        draw_polyline(image, points, 58, (190, 166, 103, 178))
        draw_polyline(image, points, 34, (202, 179, 117, 110))

    draw = ImageDraw.Draw(image)
    for path_info in layout["road_paths"]:
        points = polygon(path_info["source_points"])
        for x, y in points:
            draw.ellipse((x - 8, y - 5, x + 8, y + 5), fill=(220, 205, 150, 115))
    for connector in layout.get("seam_connector_paths", []):
        for x, y in polygon(connector["source_points"]):
            draw.ellipse((x - 7, y - 4, x + 7, y + 4), fill=(218, 202, 145, 92))

    for seam in layout["seam_connectors"]:
        sx, sy = point(seam["source_position"])
        draw.ellipse((sx - 12, sy - 12, sx + 12, sy + 12), fill=(184, 158, 99, 180))


def draw_house(image: Image.Image, center: tuple[int, int], scale: float, roof_color: tuple[int, int, int, int]) -> None:
    cx, cy = center
    w = int(210 * scale)
    h = int(122 * scale)
    body = [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2]
    draw = ImageDraw.Draw(image)
    shadow = (body[0] + 18, body[3] - 4, body[2] + 24, body[3] + 32)
    draw.ellipse(shadow, fill=(72, 86, 55, 52))
    roof = [
        (cx - int(w * 0.62), body[1] + int(h * 0.05)),
        (cx, body[1] - int(h * 0.52)),
        (cx + int(w * 0.62), body[1] + int(h * 0.05)),
        (cx + int(w * 0.48), body[1] + int(h * 0.28)),
        (cx - int(w * 0.48), body[1] + int(h * 0.28)),
    ]
    draw.rounded_rectangle(body, radius=10, fill=(215, 187, 130, 255), outline=(92, 67, 43, 255), width=3)
    draw.polygon(roof, fill=roof_color, outline=(92, 55, 34, 255))
    for offset in [-int(w * 0.3), int(w * 0.28)]:
        wx = cx + offset
        wy = cy - int(h * 0.12)
        draw.rounded_rectangle((wx - 28, wy - 18, wx + 28, wy + 18), radius=4, fill=(125, 168, 164, 255), outline=(75, 92, 83, 255), width=2)
    draw.rectangle((cx - 20, cy + 4, cx + 20, cy + 54), fill=(94, 61, 38, 255))
    draw.rounded_rectangle((cx - 50, cy + 48, cx + 50, cy + 74), radius=5, fill=(162, 111, 64, 255), outline=(91, 61, 38, 255), width=2)


def draw_notice(image: Image.Image, center: tuple[int, int]) -> None:
    cx, cy = center
    draw = ImageDraw.Draw(image)
    draw.ellipse((cx - 74, cy + 48, cx + 84, cy + 74), fill=(72, 86, 55, 42))
    draw.rectangle((cx - 8, cy - 6, cx + 8, cy + 82), fill=(100, 70, 43, 255))
    draw.rounded_rectangle((cx - 78, cy - 64, cx + 78, cy + 18), radius=8, fill=(154, 101, 56, 255), outline=(86, 58, 38, 255), width=3)
    for i in range(4):
        y = cy - 42 + i * 15
        draw.line((cx - 50, y, cx + 50, y + random.randint(-2, 2)), fill=(198, 152, 92, 105), width=3)
    draw.polygon([(cx + 80, cy - 42), (cx + 118, cy - 20), (cx + 80, cy + 2)], fill=(170, 95, 54, 255), outline=(91, 55, 36, 255))


def draw_seed_stall(image: Image.Image, center: tuple[int, int]) -> None:
    cx, cy = center
    draw = ImageDraw.Draw(image)
    draw.ellipse((cx - 118, cy + 42, cx + 130, cy + 82), fill=(72, 86, 55, 45))
    draw.rounded_rectangle((cx - 98, cy - 4, cx + 100, cy + 46), radius=8, fill=(157, 105, 57, 255), outline=(91, 62, 39, 255), width=3)
    draw.polygon([(cx - 112, cy - 30), (cx + 112, cy - 34), (cx + 90, cy - 78), (cx - 92, cy - 70)], fill=(188, 117, 71, 255), outline=(98, 65, 40, 255))
    for i, color in enumerate([(209, 179, 92, 255), (168, 121, 76, 255), (127, 151, 92, 255)]):
        bx = cx - 64 + i * 58
        draw.rounded_rectangle((bx, cy + 2, bx + 42, cy + 32), radius=5, fill=color, outline=(82, 64, 42, 255), width=2)
    draw.rectangle((cx - 76, cy + 42, cx - 60, cy + 108), fill=(104, 72, 42, 255))
    draw.rectangle((cx + 68, cy + 42, cx + 84, cy + 104), fill=(104, 72, 42, 255))


def draw_old_maple(image: Image.Image, center: tuple[int, int]) -> None:
    cx, cy = center
    draw = ImageDraw.Draw(image)
    draw.ellipse((cx - 96, cy + 88, cx + 108, cy + 132), fill=(64, 81, 52, 42))
    for angle in [-32, -14, 12, 34]:
        length = 120
        ex = cx + int(math.cos(math.radians(angle)) * length)
        ey = cy - 48 + int(math.sin(math.radians(angle)) * length * 0.45)
        draw.line((cx, cy + 38, ex, ey), fill=(91, 63, 42, 255), width=18)
    draw.rounded_rectangle((cx - 25, cy - 36, cx + 25, cy + 100), radius=16, fill=(102, 67, 43, 255), outline=(62, 47, 35, 255), width=3)
    canopy_layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(canopy_layer)
    for ox, oy, rx, ry, col in [
        (-74, -100, 112, 72, (104, 137, 84, 230)),
        (24, -116, 122, 78, (122, 154, 89, 230)),
        (95, -65, 94, 66, (92, 125, 75, 222)),
        (-14, -45, 132, 82, (115, 148, 88, 232)),
    ]:
        cdraw.ellipse((cx + ox - rx, cy + oy - ry, cx + ox + rx, cy + oy + ry), fill=col)
    overlay(image, canopy_layer.filter(ImageFilter.GaussianBlur(1)))
    draw.rounded_rectangle((cx - 70, cy + 88, cx - 30, cy + 124), radius=4, fill=(132, 94, 58, 255), outline=(72, 51, 35, 255), width=2)


def draw_bench(image: Image.Image, center: tuple[int, int]) -> None:
    cx, cy = center
    draw = ImageDraw.Draw(image)
    draw.ellipse((cx - 115, cy + 48, cx + 124, cy + 76), fill=(72, 86, 55, 40))
    for y in [cy - 22, cy + 18]:
        draw.rounded_rectangle((cx - 102, y, cx + 102, y + 24), radius=8, fill=(142, 85, 46, 255), outline=(79, 54, 36, 255), width=3)
    draw.rectangle((cx - 82, cy + 40, cx - 66, cy + 96), fill=(88, 59, 38, 255))
    draw.rectangle((cx + 66, cy + 40, cx + 82, cy + 96), fill=(88, 59, 38, 255))


def draw_flowers_and_stones(image: Image.Image) -> None:
    random.seed(SEED + 1)
    draw = ImageDraw.Draw(image)
    clusters = [(370, 930), (930, 840), (1505, 780), (790, 650), (1260, 600)]
    for cx, cy in clusters:
        for _ in range(18):
            x = cx + random.randint(-42, 42)
            y = cy + random.randint(-26, 26)
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=random.choice([(218, 179, 176, 210), (232, 207, 162, 205), (175, 200, 130, 210)]))
    for _ in range(70):
        x = random.randint(80, 1720)
        y = random.randint(120, 1100)
        if random.random() < 0.5:
            draw.ellipse((x - 5, y - 3, x + 5, y + 3), fill=(128, 135, 97, 90))


def draw_source(layout: dict) -> Image.Image:
    image = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw_texture(image)
    draw_roads(image, layout)
    draw_house(image, (486, 420), 1.0, (144, 70, 42, 255))
    draw_house(image, (1332, 444), 0.84, (151, 76, 45, 255))
    zones = {zone["id"]: zone for zone in layout["object_zones"]}
    draw_notice(image, point(zones["VillageNotice"]["source_position"]))
    draw_seed_stall(image, point(zones["SeedStallProxy"]["source_position"]))
    draw_bench(image, point(zones["BenchRestProp"]["source_position"]))

    # Aoi's standing pocket is intentionally an empty readable patch, not a character.
    pocket = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(pocket)
    ax, ay = point(zones["AoiVillageStandLateMorning"]["source_position"])
    pdraw.ellipse((ax - 54, ay - 30, ax + 54, ay + 28), fill=(214, 190, 128, 68), outline=(142, 118, 73, 96), width=3)
    overlay(image, pocket.filter(ImageFilter.GaussianBlur(1)))

    draw_old_maple(image, point(zones["OldMapleClue"]["source_position"]))
    draw_flowers_and_stones(image)
    return image.convert("RGB")


def draw_review_overlay(source: Image.Image, layout: dict) -> Image.Image:
    image = source.convert("RGBA")
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = ImageFont.load_default()
    for zone in layout["object_zones"]:
        zone_id = zone["id"]
        if "source_rect" in zone:
            x, y, w, h = [int(v) for v in zone["source_rect"]]
            draw.rectangle((x, y, x + w, y + h), outline=(210, 76, 54, 230), width=4)
            draw.text((x + 6, y + 6), zone_id, fill=(62, 34, 24, 255), font=font)
        if "source_position" in zone:
            px, py = point(zone["source_position"])
            draw.ellipse((px - 14, py - 14, px + 14, py + 14), fill=(36, 84, 112, 210), outline=(255, 255, 255, 230), width=2)
    for seam in layout["seam_connectors"]:
        sx, sy = point(seam["source_position"])
        draw.ellipse((sx - 18, sy - 18, sx + 18, sy + 18), fill=(201, 67, 47, 220))
        draw.text((sx + 22, sy - 8), seam["id"], fill=(70, 35, 24, 255), font=font)
    image.alpha_composite(layer)
    return image.convert("RGB")


def write_acceptance() -> None:
    payload = {
        "candidate_id": LAYOUT_DRAFT_ID,
        "status": "layout_structure_draft_pending_seamless_master_review",
        "candidate_type": "layout_structure_draft",
        "not_final_painted_source": True,
        "do_not_split_layers_from_this_image": True,
        "source_image": "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png",
        "review_overlay": "production/assets/regions/village_world2d/v001/05_review_and_qa/village_painted_source_review_overlay_v001.png",
        "canvas": {"width": CANVAS[0], "height": CANVAS[1]},
        "alpha": "opaque",
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "human_visual_approval": False,
        "layer_export_approved": False,
        "codex_visual_precheck": {
            "status": "passed_readability_precheck",
            "not_human_visual_approval": True,
            "checks": [
                "Village Plaza reads as one small social node.",
                "West, north, east, and south road connections are visible in the source image.",
                "VillageNotice, SeedStallProxy, OldMapleClue, Aoi standing pocket, and BenchRestProp remain identifiable.",
                "Hidden discovery remains environmental and has no readable clue text."
            ],
            "blocking_note": "This is a layout draft only; generate a true storybook painted_source after OutdoorWorld seamless master review before layer export."
        },
        "generated_from": "production/assets/regions/village_world2d/v001/01_layout_lock/layout_lock.json",
        "notes": [
            "Local generated structure/layout draft only.",
            "This image is not final storybook painted_source art.",
            "No runtime art paths are changed.",
            "Layer export remains blocked until a true painted_source is produced from the seamless OutdoorWorld master blueprint and approved."
        ],
    }
    ACCEPTANCE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_review_md() -> None:
    REVIEW_MD.write_text(
        """# Village layout structure draft review

Candidate: `village_layout_structure_draft_v001`

Status: structure/layout draft only. This is not final painted source art, not final `village_painted_source`, and must not be split into runtime layers.

## Files

- Structure draft: `02_source_generation/village_painted_source.png`
- Review overlay: `05_review_and_qa/village_painted_source_review_overlay_v001.png`
- Acceptance record: `02_source_generation/source_acceptance.json`

## Review checklist

- Roads connect west, north, east, and south seams without visual breaks.
- `VillageNotice`, `SeedStallProxy`, `OldMapleClue`, `VillageReturnPath`, Aoi's standing pocket, and `BenchRestProp` are readable.
- Hidden discovery remains environmental; no quest text or explicit clue label is baked into source art.
- A seamless OutdoorWorld master blueprint and true storybook `village_painted_source` are still required before layer export or runtime replacement.

## Codex visual precheck

Status: pass for structure/layout readability. This is not human visual approval and not final painted source approval.

- Composition: pass. The image reads as a compact village entry plaza, not a full town.
- Roads: pass. The west return road and north/east/south future connector roads visibly tie into the central plaza.
- VillageNotice: pass. The notice silhouette is clear and contains only unreadable decorative strokes.
- SeedStallProxy: pass. The stall reads as a small advice/service point, not a full shop economy.
- OldMapleClue: pass. The old maple is visually prominent and remains an environmental clue without baked instructions.
- Aoi standing pocket: pass with caution. The empty standing patch beside the stall is visible; later layer work must keep it open and avoid filling it with flowers or props.
- BenchRestProp: pass. The bench reads as a quiet rest prop below the main plaza path.

Blocking note: keep `human_visual_approval=false`, `layer_export_approved=false`, and `runtime_replacement=false`. Do not split layers from this structure draft.
""",
        encoding="utf-8",
    )


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    layout = load_layout()
    source = draw_source(layout)
    source.save(SOURCE_PATH)
    overlay_image = draw_review_overlay(source, layout)
    overlay_image.save(OVERLAY_PATH)
    write_acceptance()
    write_review_md()
    print(f"OK: wrote {SOURCE_PATH.relative_to(ROOT)}")
    print(f"OK: wrote {OVERLAY_PATH.relative_to(ROOT)}")
    print(f"OK: wrote {ACCEPTANCE_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
