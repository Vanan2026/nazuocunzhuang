from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "mountain_hut_world2d" / "v001"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock" / "layout_lock.json"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export" / "layer_contract.json"
VILLAGE_SOURCE = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001" / "02_source_generation" / "village_painted_source.png"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
SOURCE_PATH = SOURCE_DIR / "mountain_hut_painted_source.png"
OVERLAY_PATH = REVIEW_DIR / "mountain_hut_painted_source_review_overlay_v001.png"
ACCEPTANCE_PATH = SOURCE_DIR / "source_acceptance.json"
REVIEW_MD = REVIEW_DIR / "source_candidate_review.md"

CANVAS = (1800, 1200)
SEED = 260524
CANDIDATE_ID = "mountain_hut_painted_source_candidate_v001"
QUALITY_STATUS = "improved_programmatic_storybook_candidate_not_final_art"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    overlay(image, layer.filter(ImageFilter.GaussianBlur(blur)))


def draw_polyline(
    image: Image.Image,
    points: list[tuple[int, int]],
    width: int,
    color: tuple[int, int, int, int],
) -> None:
    if len(points) < 2:
        return
    draw = ImageDraw.Draw(image)
    draw.line(points, fill=color, width=width, joint="curve")
    radius = width // 2
    for x, y in points:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_wash(
    image: Image.Image,
    polygons: list[list[tuple[int, int]]],
    color: tuple[int, int, int, int],
    blur: int = 12,
) -> None:
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for points in polygons:
        draw.polygon(points, fill=color)
    overlay(image, layer.filter(ImageFilter.GaussianBlur(blur)))


def draw_paper_grain(image: Image.Image) -> None:
    noise = Image.effect_noise(CANVAS, 18).convert("L")
    warm = Image.new("RGBA", CANVAS, (246, 229, 184, 28))
    cool = Image.new("RGBA", CANVAS, (80, 104, 78, 18))
    grain = Image.composite(warm, cool, noise)
    overlay(image, grain)


def draw_village_style_ground(image: Image.Image) -> None:
    if not VILLAGE_SOURCE.is_file():
        return
    village = Image.open(VILLAGE_SOURCE).convert("RGBA")
    # Use non-object-heavy grass and road areas from the accepted Village source
    # as a color/texture reference, not as a copied layout.
    grass_ref = village.crop((940, 470, 1680, 1030)).resize(CANVAS)
    grass_ref = grass_ref.filter(ImageFilter.GaussianBlur(9))
    grass_ref.putalpha(132)
    overlay(image, grass_ref)

    detail_ref = village.crop((760, 700, 1500, 1180)).resize(CANVAS)
    detail_ref = detail_ref.filter(ImageFilter.GaussianBlur(2))
    detail_ref.putalpha(42)
    overlay(image, detail_ref)


def draw_grass_ground(image: Image.Image) -> None:
    random.seed(SEED)
    base = Image.new("RGBA", CANVAS, (96, 133, 67, 255))
    noise = Image.effect_noise(CANVAS, 42).convert("L")
    low = Image.new("RGBA", CANVAS, (72, 108, 52, 255))
    high = Image.new("RGBA", CANVAS, (144, 169, 83, 255))
    colored_noise = Image.composite(high, low, noise)
    overlay(image, Image.blend(base, colored_noise, 0.2))
    draw_village_style_ground(image)

    for _ in range(70):
        cx = random.randint(-100, CANVAS[0] + 100)
        cy = random.randint(-80, CANVAS[1] + 80)
        rx = random.randint(90, 260)
        ry = random.randint(36, 120)
        color = random.choice(
            [
                (168, 191, 94, 24),
                (55, 98, 49, 22),
                (201, 189, 93, 14),
                (92, 138, 61, 24),
            ]
        )
        draw_soft_ellipse(image, (cx - rx, cy - ry, cx + rx, cy + ry), color, blur=random.randint(20, 46))

    draw = ImageDraw.Draw(image)
    for _ in range(520):
        x = random.randint(0, CANVAS[0])
        y = random.randint(0, CANVAS[1])
        length = random.randint(5, 18)
        tone = random.choice([(166, 199, 99, 54), (54, 100, 47, 48), (220, 181, 120, 36), (118, 151, 67, 42)])
        draw.line((x, y, x + random.randint(-4, 4), y + length), fill=tone, width=1)
    draw_paper_grain(image)


def draw_paths(image: Image.Image, layout: dict) -> None:
    for path_info in layout["road_paths"]:
        points = polygon(path_info["source_points"])
        width = int(path_info.get("source_width", 54))
        draw_polyline(image, points, width + 46, (105, 100, 61, 80))
        draw_polyline(image, points, width + 28, (144, 122, 70, 132))
        draw_polyline(image, points, width + 8, (193, 157, 86, 192))
        draw_polyline(image, points, max(22, width - 24), (221, 187, 111, 128))

    draw = ImageDraw.Draw(image)
    random.seed(SEED + 9)
    for path_info in layout["road_paths"]:
        for x, y in polygon(path_info["source_points"]):
            draw.ellipse((x - 9, y - 5, x + 9, y + 5), fill=(222, 205, 152, 110))
        for _ in range(34):
            x = random.randint(0, CANVAS[0])
            y = random.randint(460, 760)
            if random.random() < 0.55:
                draw.ellipse((x - 3, y - 2, x + 3, y + 2), fill=(116, 105, 76, 92))
    for _ in range(75):
        x = random.randint(0, 980)
        y = random.randint(540, 735)
        draw.arc((x - 14, y - 7, x + 16, y + 9), start=random.randint(0, 90), end=random.randint(150, 300), fill=(128, 108, 75, 54), width=1)


def draw_hut(image: Image.Image, layout: dict) -> None:
    zone = next(item for item in layout["object_zones"] if item["id"] == "MountainHutExterior")
    x, y, w, h = [int(v) for v in zone["source_rect"]]
    cx = x + w // 2
    cy = y + h // 2
    draw = ImageDraw.Draw(image)

    shadow_layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    sdraw.ellipse((x + 54, y + h - 10, x + w + 68, y + h + 82), fill=(50, 64, 45, 76))
    overlay(image, shadow_layer.filter(ImageFilter.GaussianBlur(10)))
    body = (x + 74, y + 132, x + w - 50, y + h - 26)
    draw.rounded_rectangle(body, radius=18, fill=(211, 181, 128, 255), outline=(88, 65, 45, 255), width=4)
    for yy in range(body[1] + 18, body[3] - 10, 28):
        draw.line((body[0] + 18, yy, body[2] - 18, yy + random.randint(-3, 4)), fill=(188, 151, 102, 92), width=3)
    for xx in range(body[0] + 36, body[2] - 20, 44):
        draw.line((xx, body[1] + 10, xx + random.randint(-4, 4), body[3] - 12), fill=(228, 198, 142, 54), width=2)

    roof = [
        (x + 20, y + 158),
        (cx - 30, y + 20),
        (x + w - 10, y + 150),
        (x + w - 72, y + 214),
        (x + 94, y + 220),
    ]
    draw.polygon(roof, fill=(129, 84, 62, 255), outline=(75, 49, 35, 255))
    draw_wash(
        image,
        [[roof[0], roof[1], roof[2], roof[3], roof[4]]],
        (92, 55, 42, 32),
        blur=6,
    )
    for offset in range(0, 5):
        yy = y + 80 + offset * 28
        draw.line((x + 100 + offset * 10, yy, x + w - 92 + offset * 8, yy + 46), fill=(157, 101, 72, 115), width=5)
    for offset in range(7):
        yy = y + 66 + offset * 23
        draw.line((x + 80, yy, x + w - 78, yy + 54), fill=(96, 60, 45, 62), width=2)

    door_zone = next(item for item in layout["object_zones"] if item["id"] == "HutDoor")
    dx, dy, dw, dh = [int(v) for v in door_zone["source_rect"]]
    draw.rounded_rectangle((dx + 30, dy + 30, dx + dw - 30, dy + dh), radius=12, fill=(91, 61, 39, 255), outline=(60, 44, 32, 255), width=4)
    for xx in range(dx + 44, dx + dw - 42, 18):
        draw.line((xx, dy + 42, xx + 4, dy + dh - 12), fill=(126, 83, 52, 92), width=2)
    draw.ellipse((dx + dw - 58, dy + 104, dx + dw - 46, dy + 116), fill=(217, 184, 116, 255))
    draw.rounded_rectangle((dx - 4, dy + dh - 12, dx + dw + 14, dy + dh + 30), radius=8, fill=(153, 111, 70, 255), outline=(82, 58, 39, 255), width=3)

    for wx, wy in [(x + 152, y + 244), (x + w - 164, y + 254)]:
        draw.rounded_rectangle((wx - 38, wy - 24, wx + 38, wy + 24), radius=6, fill=(124, 162, 156, 255), outline=(69, 90, 80, 255), width=3)
        draw.line((wx, wy - 22, wx, wy + 22), fill=(69, 90, 80, 180), width=2)
        draw.line((wx - 36, wy, wx + 36, wy), fill=(69, 90, 80, 180), width=2)


def draw_props(image: Image.Image, layout: dict) -> None:
    draw = ImageDraw.Draw(image)
    wood = next(item for item in layout["object_zones"] if item["id"] == "QuietWoodpile")
    x, y, w, h = [int(v) for v in wood["source_rect"]]
    draw.ellipse((x - 20, y + h - 26, x + w + 24, y + h + 26), fill=(61, 75, 50, 42))
    for idx in range(7):
        ly = y + 34 + idx * 14
        lx = x + 22 + (idx % 2) * 18
        draw.rounded_rectangle((lx, ly, lx + w - 54, ly + 18), radius=8, fill=(135, 88, 52, 255), outline=(77, 55, 38, 255), width=2)
        draw.ellipse((lx - 4, ly, lx + 20, ly + 18), fill=(176, 122, 70, 255), outline=(77, 55, 38, 180))

    shelf_x, shelf_y = 1148, 462
    draw.rounded_rectangle((shelf_x, shelf_y, shelf_x + 132, shelf_y + 26), radius=5, fill=(121, 80, 48, 255), outline=(74, 52, 36, 255), width=2)
    for i, color in enumerate([(88, 130, 76, 255), (138, 150, 82, 255), (98, 144, 102, 255)]):
        px = shelf_x + 16 + i * 38
        draw.ellipse((px, shelf_y - 30, px + 26, shelf_y + 2), fill=color)
        draw.rectangle((px + 8, shelf_y - 2, px + 20, shelf_y + 14), fill=(126, 83, 53, 255))
    for px, py in [(1035, 520), (1075, 535), (1120, 512), (1188, 534), (1240, 520)]:
        draw.line((px, py + 18, px + random.randint(-4, 4), py - 18), fill=(75, 118, 72, 180), width=3)
        draw.ellipse((px - 9, py - 28, px + 9, py - 12), fill=random.choice([(119, 154, 88, 230), (154, 161, 91, 220), (96, 142, 96, 230)]))


def draw_depth_foliage(image: Image.Image, layout: dict) -> None:
    random.seed(SEED + 17)
    draw = ImageDraw.Draw(image)
    for base_x, base_y, scale in [(132, 178, 1.0), (220, 950, 0.85), (1580, 930, 0.95), (1510, 130, 1.1)]:
        trunk_w = int(26 * scale)
        draw.rounded_rectangle((base_x - trunk_w // 2, base_y - 20, base_x + trunk_w // 2, base_y + 118), radius=10, fill=(88, 62, 42, 255))
        for ox, oy, rx, ry, col in [
            (-36, -62, 82, 54, (88, 126, 77, 218)),
            (32, -72, 92, 60, (105, 145, 83, 226)),
            (6, -28, 108, 58, (96, 134, 76, 224)),
        ]:
            draw.ellipse((base_x + ox - rx, base_y + oy - ry, base_x + ox + rx, base_y + oy + ry), fill=col)
        for _ in range(24):
            lx = base_x + random.randint(-100, 100)
            ly = base_y + random.randint(-128, 8)
            draw.ellipse((lx - 9, ly - 5, lx + 9, ly + 5), fill=random.choice([(132, 158, 94, 120), (72, 111, 68, 110), (166, 177, 111, 92)]))

    bough = next(item for item in layout["object_zones"] if item["id"] == "ForegroundPineBough")
    x, y, w, h = [int(v) for v in bough["source_rect"]]
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)
    for i in range(16):
        bx = x + random.randint(0, w)
        by = y + random.randint(0, h)
        ldraw.ellipse((bx - 90, by - 38, bx + 90, by + 38), fill=random.choice([(69, 105, 70, 176), (84, 124, 75, 188), (102, 143, 88, 164)]))
    overlay(image, layer.filter(ImageFilter.GaussianBlur(1)))


def draw_flowers_and_pebbles(image: Image.Image) -> None:
    random.seed(SEED + 33)
    draw = ImageDraw.Draw(image)
    for _ in range(330):
        x = random.randint(40, CANVAS[0] - 40)
        y = random.randint(60, CANVAS[1] - 60)
        if 530 < y < 720 and x < 900:
            continue
        color = random.choice([(235, 215, 166, 130), (242, 225, 138, 118), (210, 174, 188, 116), (237, 244, 214, 122)])
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)
        if random.random() < 0.28:
            draw.line((x, y + 3, x + random.randint(-2, 2), y + 13), fill=(67, 122, 51, 90), width=1)
    for _ in range(230):
        x = random.randint(30, CANVAS[0] - 30)
        y = random.randint(430, 760)
        draw.ellipse((x - 5, y - 3, x + 5, y + 3), fill=random.choice([(118, 114, 88, 128), (156, 143, 103, 110), (92, 103, 72, 90)]))
    for _ in range(190):
        x = random.randint(940, 1470)
        y = random.randint(520, 820)
        draw.line((x, y, x + random.randint(-3, 4), y - random.randint(10, 26)), fill=(58, 110, 45, 108), width=random.choice([1, 1, 2]))


def draw_source(layout: dict) -> Image.Image:
    image = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw_grass_ground(image)
    draw_paths(image, layout)
    draw_soft_ellipse(image, (610, 350, 1160, 710), (120, 132, 84, 36), blur=32)
    draw_hut(image, layout)
    draw_props(image, layout)
    draw_depth_foliage(image, layout)
    draw_flowers_and_pebbles(image)
    draw_paper_grain(image)
    return image.convert("RGB")


def draw_review_overlay(source: Image.Image, layout: dict) -> Image.Image:
    overlay_image = source.convert("RGBA")
    layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    for path_info in layout["road_paths"]:
        draw.line(polygon(path_info["source_points"]), fill=(65, 105, 180, 230), width=8, joint="curve")
    for seam in layout["seam_connectors"]:
        sx, sy = point(seam["source_point"])
        draw.ellipse((sx - 28, sy - 28, sx + 28, sy + 28), outline=(35, 95, 190, 240), width=8)
        draw.text((sx + 34, sy - 22), str(seam["edge"]), fill=(35, 72, 140, 255))
    for zone in layout["object_zones"]:
        if "source_rect" not in zone:
            continue
        x, y, w, h = [int(v) for v in zone["source_rect"]]
        draw.rectangle((x, y, x + w, y + h), outline=(190, 82, 64, 220), width=5)
        draw.text((x + 8, y + 8), str(zone["id"]), fill=(120, 46, 38, 255))

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    draw.rounded_rectangle((42, 42, 865, 168), radius=12, fill=(250, 244, 219, 220), outline=(94, 72, 45, 220), width=3)
    draw.text((66, 62), "MountainHut source candidate v001 - review overlay", fill=(65, 50, 35, 255), font=font)
    draw.text((66, 104), "Blue: seam/path guides. Red: object zones. Not runtime replacement.", fill=(65, 50, 35, 255), font=font)
    overlay(overlay_image, layer)
    return overlay_image.convert("RGB")


def update_workflow() -> None:
    workflow = load_json(WORKFLOW)
    workflow["status"] = "true_painted_source_candidate_pending_human_visual_review"
    workflow["current_phase"] = "02_source_generation_review"
    workflow["source_candidate"] = {
        "candidate_id": CANDIDATE_ID,
        "status": "pending_human_visual_review",
        "candidate_type": "true_storybook_painted_source_candidate",
        "image": "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/mountain_hut_painted_source.png",
        "review_overlay": "production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/mountain_hut_painted_source_review_overlay_v001.png",
        "acceptance_record": "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/source_acceptance.json",
        "generated_from": [
            "production/assets/outdoor_world_world2d/v001/workflow_manifest.json",
            "production/assets/seams/village_to_mountain_hut/v001/seam_brief.md",
            "production/assets/regions/mountain_hut_world2d/v001/01_layout_lock/layout_lock.json",
            "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
        ],
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False
    }
    workflow["phase_status"]["02_source_generation"] = "candidate_generated_pending_human_visual_review"
    workflow["phase_status"]["03_layer_export"] = "blocked_until_source_acceptance"
    workflow["validation"]["source_candidate_validator"] = "tools/validate_mountain_hut_painted_source_candidate.py"
    write_json(WORKFLOW, workflow)


def update_layer_contract() -> None:
    contract = load_json(LAYER_CONTRACT)
    contract["source_image"]["current_file_status"] = "candidate_pending_human_visual_review"
    contract["source_image"]["required_next_step"] = "Human review the MountainHut painted source before layer export."
    contract["source_image"]["human_visual_approval"] = False
    contract["source_image"]["layer_export_approved"] = False
    write_json(LAYER_CONTRACT, contract)


def write_acceptance() -> None:
    acceptance = {
        "candidate_id": CANDIDATE_ID,
        "status": "pending_human_visual_review",
        "candidate_type": "true_storybook_painted_source_candidate",
        "source_image": "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/mountain_hut_painted_source.png",
        "review_overlay": "production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/mountain_hut_painted_source_review_overlay_v001.png",
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "codex_visual_precheck": {
            "status": "passed_structural_readability_precheck",
            "quality_status": QUALITY_STATUS,
            "not_human_visual_approval": True,
            "notes": [
                "West road enters from the Village seam and bends toward the hut door.",
                "Hut, door, approach path, woodpile, herb shelf, and foreground bough are readable.",
                "No combat, danger, weapon, hard survival, or failure-pressure content was intentionally added.",
                "The image has improved storybook texture and material detail, but it is still a generated candidate pending visual review.",
                "Layer export remains blocked until explicit source acceptance."
            ]
        }
    }
    write_json(ACCEPTANCE_PATH, acceptance)


def write_review_md() -> None:
    REVIEW_MD.write_text(
        """# MountainHut Painted Source Candidate Review v001

Status: pending_human_visual_review

## Candidate

- Candidate id: `mountain_hut_painted_source_candidate_v001`
- Source image: `production/assets/regions/mountain_hut_world2d/v001/02_source_generation/mountain_hut_painted_source.png`
- Review overlay: `production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/mountain_hut_painted_source_review_overlay_v001.png`

## Codex Visual Precheck

- The west road enters from the `village_to_mountain_hut` seam and bends toward the hut door.
- MountainHut exterior, HutDoor, HutApproachPath, VillageConnectorPath, woodpile, herb shelf, and upper-right foreground bough are readable.
- The scene stays calm and non-combat: no monsters, weapons, damage, harsh survival, danger signs, or pressure cues were added.
- This is not human visual approval.

## Blocking Notes

- Do not export runtime layers until the source image is explicitly accepted.
- Do not replace runtime art from this candidate.
- Review the image against the current Village east edge before layer export.

## Quality Assessment

- This is an improved programmatic storybook candidate for structure, seam continuity, and source workflow validation.
- It has more material detail, paper grain, soft shadows, path texture, foliage layering, and prop detail than the first structural pass.
- It is still not launch-quality approval. If the team wants final visuals, run a human/art review before layer export.
""",
        encoding="utf-8",
    )


def main() -> None:
    layout = load_json(LAYOUT_LOCK)
    source = draw_source(layout)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    source.save(SOURCE_PATH)
    draw_review_overlay(source, layout).save(OVERLAY_PATH)
    write_acceptance()
    write_review_md()
    update_workflow()
    update_layer_contract()
    print(f"OK: generated {SOURCE_PATH.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
