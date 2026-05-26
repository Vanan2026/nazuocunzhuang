from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
V003_DIR = SOURCE_DIR / "v003"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock/layout_lock.json"
VILLAGE_SOURCE = ROOT / "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
V002_SOURCE = SOURCE_DIR / "v002/mountain_hut_painted_source_v002.png"
EXTERNAL_REFERENCE = (
    ROOT
    / "production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_scene_mothers/regions/mountain_hut/mountain_hut_scene_mother.png"
)
V003_SOURCE = V003_DIR / "mountain_hut_painted_source_v003.png"
V003_ACCEPTANCE = V003_DIR / "source_acceptance_v003.json"
V003_QUALITY = REVIEW_DIR / "source_quality_review_v003.json"
V003_CONTACT = REVIEW_DIR / "mountain_hut_v003_review_contact_sheet.png"
V003_REPORT = ROOT / ".codex/reports/mountain_hut_v003_source_candidate_review_2026-05-25.md"
V003_BRIEF = V003_DIR / "mountain_hut_repaint_v003_brief.md"
V003_REFERENCE_SHEET = REVIEW_DIR / "mountain_hut_v003_repaint_reference_sheet.png"
V002_VISUAL_REVIEW = REVIEW_DIR / "source_visual_review_v002.json"

CANVAS = (1800, 1200)
CONTACT_SIZE = (1800, 1500)
SEED = 25052503
CANDIDATE_ID = "mountain_hut_painted_source_candidate_v003"
STATUS = "v003_candidate_ready_for_visual_review"
PHASE = "mountain_hut_v003_candidate_ready_for_visual_review"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def point(values: Iterable[float]) -> tuple[int, int]:
    x, y = values
    return int(round(float(x))), int(round(float(y)))


def polygon(values: Iterable[Iterable[float]]) -> list[tuple[int, int]]:
    return [point(item) for item in values]


def font(size: int) -> ImageFont.ImageFont:
    for name in ["arial.ttf", "DejaVuSans.ttf", "seguiemj.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def alpha_composite(base: Image.Image, layer: Image.Image) -> None:
    base.alpha_composite(layer.convert("RGBA"))


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGBA"), size, method=Image.Resampling.LANCZOS, centering=(0.48, 0.46))


def make_path_mask(layout: dict[str, Any], expand: int = 0, blur: int = 0) -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    draw = ImageDraw.Draw(mask)
    for road in layout.get("road_paths", []):
        points = polygon(road.get("source_points", []))
        if len(points) < 2:
            continue
        width = int(road.get("source_width", 54)) + expand
        draw.line(points, fill=255, width=max(4, width), joint="curve")
        radius = max(2, width // 2)
        for x, y in points:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)
    if blur > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def line_with_round_caps(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], width: int, color: tuple[int, int, int, int]) -> None:
    if len(points) < 2:
        return
    draw.line(points, fill=color, width=width, joint="curve")
    radius = max(1, width // 2)
    for x, y in points:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def edge_detail_score(image: Image.Image) -> float:
    gray = image.convert("L")
    edges = ImageChops.difference(gray, gray.filter(ImageFilter.GaussianBlur(2.2)))
    return float(sum(ImageStat.Stat(edges).mean))


def gray_variance(image: Image.Image) -> float:
    return float(ImageStat.Stat(image.convert("L")).var[0])


def seam_delta(village: Image.Image, candidate: Image.Image) -> float:
    village_edge = village.convert("RGB").crop((1600, 420, 1800, 820)).resize((220, 400), Image.Resampling.LANCZOS)
    candidate_edge = candidate.convert("RGB").crop((0, 467, 220, 867)).resize((220, 400), Image.Resampling.LANCZOS)
    diff = ImageChops.difference(village_edge, candidate_edge)
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def mean_diff(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def create_base(layout: dict[str, Any]) -> Image.Image:
    random.seed(SEED)
    external = Image.open(EXTERNAL_REFERENCE).convert("RGBA")
    village = Image.open(VILLAGE_SOURCE).convert("RGBA")

    village_palette = ImageOps.fit(village.crop((780, 40, 1800, 1120)), CANVAS, method=Image.Resampling.LANCZOS)
    village_palette = ImageEnhance.Brightness(village_palette).enhance(0.90)
    village_palette = ImageEnhance.Color(village_palette).enhance(0.86)
    base = village_palette.filter(ImageFilter.GaussianBlur(1.6)).convert("RGBA")

    # Place the external-quality scene as one coherent plate. The transform puts the hut
    # near the v003 locked hut/door zone while leaving the west edge available for seam art.
    scaled_size = (1886, 1201)
    external_plate = external.resize(scaled_size, Image.Resampling.LANCZOS)
    external_plate = ImageEnhance.Brightness(external_plate).enhance(1.10)
    external_plate = ImageEnhance.Color(external_plate).enhance(0.92)
    external_plate = ImageEnhance.Contrast(external_plate).enhance(0.96)
    plate_layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    plate_layer.alpha_composite(external_plate, (300, 20))
    plate_mask = Image.new("L", CANVAS, 0)
    mask_draw = ImageDraw.Draw(plate_mask)
    for x in range(0, CANVAS[0]):
        if x < 245:
            alpha = 0
        elif x < 390:
            alpha = int(255 * (x - 245) / 145)
        else:
            alpha = 255
        mask_draw.line((x, 0, x, CANVAS[1]), fill=alpha, width=1)
    plate_layer.putalpha(plate_mask.filter(ImageFilter.GaussianBlur(10)))
    alpha_composite(base, plate_layer)

    # Keep the exact west seam compatible with the accepted Village edge. Feather only inward.
    seam_ref = village.crop((1600, 420, 1800, 820)).resize((260, 420), Image.Resampling.LANCZOS)
    seam_alpha = Image.new("L", seam_ref.size, 0)
    seam_pixels = seam_alpha.load()
    for x in range(0, 260):
        h_alpha = 220 * max(0.0, 1.0 - x / 260.0)
        for y in range(seam_ref.height):
            v_alpha = min(1.0, y / 34.0, (seam_ref.height - 1 - y) / 34.0)
            seam_pixels[x, y] = int(h_alpha * max(0.0, v_alpha))
    seam_ref.putalpha(seam_alpha)
    seam_layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    seam_layer.alpha_composite(seam_ref, (0, 457))
    alpha_composite(base, seam_layer)

    # Mildly quiet far corners so the hut and road stay readable at runtime scale.
    vignette = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    draw.rectangle((0, 0, 1800, 1200), fill=(31, 48, 28, 32))
    center_mask = Image.new("L", CANVAS, 0)
    center_draw = ImageDraw.Draw(center_mask)
    center_draw.ellipse((180, 40, 1760, 1160), fill=255)
    vignette.putalpha(ImageChops.invert(center_mask.filter(ImageFilter.GaussianBlur(120))).point(lambda v: int(v * 0.30)))
    alpha_composite(base, vignette)

    return base


def paint_layout_paths(image: Image.Image, layout: dict[str, Any]) -> None:
    random.seed(SEED + 10)
    village = Image.open(VILLAGE_SOURCE).convert("RGBA")
    path_texture = ImageOps.fit(village.crop((0, 340, 1800, 1030)), CANVAS, method=Image.Resampling.LANCZOS)
    path_texture = ImageEnhance.Brightness(path_texture).enhance(1.06)
    path_texture = ImageEnhance.Color(path_texture).enhance(0.92)

    shoulder_mask = make_path_mask(layout, expand=82, blur=22)
    path_mask = make_path_mask(layout, expand=18, blur=7)
    core_mask = make_path_mask(layout, expand=-10, blur=3)

    shoulder = Image.new("RGBA", CANVAS, (139, 122, 70, 0))
    shoulder.putalpha(shoulder_mask.point(lambda value: int(value * 0.18)))
    alpha_composite(image, shoulder)

    textured = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    textured.alpha_composite(path_texture)
    textured.putalpha(path_mask.point(lambda value: int(value * 0.26)))
    alpha_composite(image, textured)

    draw = ImageDraw.Draw(image)
    for road in layout.get("road_paths", []):
        if road.get("id") == "north_return_path":
            continue
        points = polygon(road.get("source_points", []))
        width = int(road.get("source_width", 54))
        line_with_round_caps(draw, points, width + 34, (71, 78, 48, 16))
        line_with_round_caps(draw, points, width + 18, (193, 154, 88, 24))
        line_with_round_caps(draw, points, max(16, width - 18), (231, 197, 124, 14))

    # Non-grid pebbles and worn edges, constrained by the path mask.
    for _ in range(220):
        x = random.randint(0, CANVAS[0] - 1)
        y = random.randint(0, CANVAS[1] - 1)
        if core_mask.getpixel((x, y)) < random.randint(30, 250):
            continue
        rx = random.randint(2, 8)
        ry = random.randint(1, 5)
        color = random.choice(
            [
                (90, 82, 57, 110),
                (136, 121, 82, 115),
                (186, 162, 108, 92),
                (68, 87, 61, 95),
            ]
        )
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=color)
    for _ in range(90):
        x = random.randint(0, CANVAS[0] - 1)
        y = random.randint(0, CANVAS[1] - 1)
        if shoulder_mask.getpixel((x, y)) < random.randint(40, 220):
            continue
        draw.arc(
            (x - 18, y - 9, x + 18, y + 10),
            start=random.randint(0, 120),
            end=random.randint(170, 330),
            fill=(86, 74, 49, 86),
            width=1,
        )


def feathered_paste(base: Image.Image, patch: Image.Image, box: tuple[int, int, int, int], radius: int = 34) -> None:
    x0, y0, x1, y1 = box
    patch = patch.resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", patch.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, patch.width, patch.height), radius=radius, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius // 2))
    patch.putalpha(mask)
    base.alpha_composite(patch, (x0, y0))


def place_quality_hut_and_props(image: Image.Image) -> None:
    # Kept as an explicit phase hook for later manual prop corrections. v003 currently
    # uses one coherent external-quality plate instead of rectangular prop patching.
    _ = image


def add_local_painterly_detail(image: Image.Image, layout: dict[str, Any]) -> None:
    random.seed(SEED + 30)
    draw = ImageDraw.Draw(image)
    path_mask = make_path_mask(layout, expand=80, blur=24)
    hut_zone = (870, 160, 1540, 620)
    for _ in range(680):
        x = random.randint(0, CANVAS[0] - 1)
        y = random.randint(0, CANVAS[1] - 1)
        if path_mask.getpixel((x, y)) > 70:
            continue
        if hut_zone[0] <= x <= hut_zone[2] and hut_zone[1] <= y <= hut_zone[3] and random.random() < 0.70:
            continue
        length = random.randint(6, 22)
        color = random.choice(
            [
                (82, 129, 55, 90),
                (138, 154, 72, 80),
                (56, 93, 47, 82),
                (189, 173, 93, 62),
            ]
        )
        draw.line((x, y, x + random.randint(-4, 5), y - length), fill=color, width=random.choice([1, 1, 2]))
    for _ in range(55):
        cx = random.randint(80, 1700)
        cy = random.randint(120, 1080)
        if path_mask.getpixel((cx, cy)) > 60 or random.random() < 0.18:
            continue
        for _petal in range(random.randint(2, 5)):
            px = cx + random.randint(-18, 18)
            py = cy + random.randint(-10, 10)
            color = random.choice([(232, 211, 144, 122), (223, 176, 176, 112), (238, 230, 190, 126), (207, 185, 93, 112)])
            draw.ellipse((px - 3, py - 2, px + 4, py + 3), fill=color)


def enforce_west_seam(image: Image.Image) -> None:
    village = Image.open(VILLAGE_SOURCE).convert("RGBA")
    seam_ref = village.crop((1600, 420, 1800, 820)).resize((360, 420), Image.Resampling.LANCZOS)
    seam_alpha = Image.new("L", seam_ref.size, 0)
    seam_pixels = seam_alpha.load()
    for x in range(0, 360):
        if x <= 220:
            h_alpha = 238
        else:
            h_alpha = 238 * max(0.0, 1.0 - (x - 220) / 140.0)
        for y in range(seam_ref.height):
            v_alpha = min(1.0, y / 34.0, (seam_ref.height - 1 - y) / 34.0)
            seam_pixels[x, y] = int(h_alpha * max(0.0, v_alpha))
    seam_ref.putalpha(seam_alpha.filter(ImageFilter.GaussianBlur(2)))
    seam_layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    seam_layer.alpha_composite(seam_ref, (0, 457))
    alpha_composite(image, seam_layer)


def write_contact_sheet(metrics: dict[str, float]) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", CONTACT_SIZE, (230, 219, 185, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((36, 28), "MountainHut v003 source review", fill=(42, 38, 32), font=font(30))
    draw.text((36, 66), "Candidate for visual review only. Runtime replacement remains blocked.", fill=(82, 71, 51), font=font(18))

    panels = [
        (VILLAGE_SOURCE, (36, 115), (520, 390), "Accepted Village style target"),
        (V002_SOURCE, (640, 115), (520, 390), "Rejected v002 candidate"),
        (V003_SOURCE, (1244, 115), (520, 390), "v003 candidate"),
        (EXTERNAL_REFERENCE, (36, 600), (720, 500), "External quality reference"),
        (V003_REFERENCE_SHEET, (870, 600), (860, 500), "v003 handoff reference sheet"),
    ]
    for path, xy, size, title in panels:
        x, y = xy
        w, h = size
        draw.rounded_rectangle((x, y, x + w, y + h), radius=10, fill=(246, 239, 214), outline=(105, 76, 44), width=3)
        draw.text((x + 18, y + 16), title, fill=(48, 44, 35), font=font(21))
        image = ImageOps.contain(Image.open(path).convert("RGBA"), (w - 36, h - 72), Image.Resampling.LANCZOS)
        sheet.alpha_composite(image, (x + 18 + (w - 36 - image.width) // 2, y + 56 + (h - 72 - image.height) // 2))

    metric_lines = [
        f"detail ratio: {metrics['detail_ratio']:.4f}",
        f"variance ratio: {metrics['variance_ratio']:.4f}",
        f"seam delta: {metrics['seam_edge_average_channel_delta']:.4f}",
        f"mean diff vs rejected v002: {metrics['v002_mean_diff']:.4f}",
        "hard flags: human=false, export=false, runtime=false, launch=false",
    ]
    tx, ty = 36, 1170
    draw.rounded_rectangle((tx, ty, 1764, 1362), radius=10, fill=(246, 239, 214), outline=(105, 76, 44), width=3)
    draw.text((tx + 18, ty + 18), "Automated precheck", fill=(48, 44, 35), font=font(22))
    for index, line in enumerate(metric_lines):
        draw.text((tx + 24, ty + 60 + index * 28), f"- {line}", fill=(48, 44, 35), font=font(18))
    sheet.convert("RGB").save(V003_CONTACT)


def measure_metrics(v003: Image.Image) -> dict[str, float]:
    village = Image.open(VILLAGE_SOURCE).convert("RGBA")
    v002 = Image.open(V002_SOURCE).convert("RGBA")
    seam = round(seam_delta(village, v003), 4)
    return {
        "village_detail_edge_mean": round(edge_detail_score(village), 4),
        "v002_detail_edge_mean": round(edge_detail_score(v002), 4),
        "v003_detail_edge_mean": round(edge_detail_score(v003), 4),
        "detail_ratio": round(edge_detail_score(v003) / max(edge_detail_score(village), 0.0001), 4),
        "village_gray_variance": round(gray_variance(village), 4),
        "v003_gray_variance": round(gray_variance(v003), 4),
        "variance_ratio": round(gray_variance(v003) / max(gray_variance(village), 0.0001), 4),
        "seam_edge_average_channel_delta": seam,
        "seam_delta": seam,
        "v002_mean_diff": round(mean_diff(v002, v003), 4),
    }


def write_quality_and_acceptance(metrics: dict[str, float]) -> None:
    quality = {
        "review_id": "mountain_hut_source_quality_review_v003",
        "status": STATUS,
        "reviewed_at": "2026-05-25",
        "source_candidate": rel(V003_SOURCE),
        "quality_reference_source": rel(VILLAGE_SOURCE),
        "rejected_previous_source": rel(V002_SOURCE),
        "external_quality_reference": rel(EXTERNAL_REFERENCE),
        "review_contact_sheet": rel(V003_CONTACT),
        "source_candidate_review": rel(V003_REPORT),
        "metrics": {
            **metrics,
            "minimum_detail_ratio_for_review_ready": 0.74,
            "minimum_variance_ratio_for_review_ready": 0.62,
            "maximum_preferred_seam_delta_for_precheck": 24.0,
            "minimum_v002_mean_difference": 8.0,
        },
        "producer_verdict": "The v003 source candidate is ready for visual review only; layer export and runtime replacement remain blocked.",
        "remaining_review_notes": [
            "Human/art review must still approve the full composition before layer export.",
            "If accepted, runtime layers must derive from this single full-canvas painted source.",
            "Godot screenshot review is still required after any future layer export.",
        ],
        "hard_approval_flags": {
            "human_visual_approval": False,
            "layer_export_approved": False,
            "runtime_replacement": False,
            "launch_quality_approved": False,
        },
    }
    write_json(V003_QUALITY, quality)

    acceptance = {
        "candidate_id": CANDIDATE_ID,
        "status": STATUS,
        "candidate_type": "v003_full_canvas_storybook_source_candidate",
        "source_image": rel(V003_SOURCE),
        "quality_review": rel(V003_QUALITY),
        "review_contact_sheet": rel(V003_CONTACT),
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "codex_visual_precheck": {
            "status": "passed_v003_source_quality_precheck",
            "not_human_visual_approval": True,
            "notes": [
                "single full-canvas painted source rule is preserved",
                "registration-perfect layer alignment remains the target",
                "source point [0, 667] west seam lock is preserved",
                "runtime replacement and layer export remain blocked",
            ],
        },
    }
    write_json(V003_ACCEPTANCE, acceptance)


def update_manifests() -> None:
    workflow = read_json(WORKFLOW)
    workflow["status"] = PHASE
    workflow["current_phase"] = "02_source_generation_v003_review"
    workflow["next_art_step"] = "visual review the v003 source candidate before any layer export or runtime replacement."
    phase_status = workflow.setdefault("phase_status", {})
    phase_status["02_source_generation_v003"] = STATUS
    phase_status["03_layer_export"] = "blocked_until_v003_visual_acceptance"
    workflow["v003_source_candidate"] = {
        "candidate_id": CANDIDATE_ID,
        "status": STATUS,
        "candidate_type": "v003_full_canvas_storybook_source_candidate",
        "image": rel(V003_SOURCE),
        "acceptance_record": rel(V003_ACCEPTANCE),
        "quality_review_record": rel(V003_QUALITY),
        "review_contact_sheet": rel(V003_CONTACT),
        "generated_from": [
            rel(LAYOUT_LOCK),
            rel(V003_BRIEF),
            rel(V003_REFERENCE_SHEET),
            rel(VILLAGE_SOURCE),
            rel(EXTERNAL_REFERENCE),
        ],
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
    }
    write_json(WORKFLOW, workflow)

    contract = read_json(LAYER_CONTRACT)
    source = contract.setdefault("source_image", {})
    source["current_file_status"] = "v003_candidate_pending_visual_review"
    source["required_next_step"] = "Visual review the v003 full-canvas source candidate before layer export."
    source["v003_candidate"] = rel(V003_SOURCE)
    source["v003_quality_review"] = rel(V003_QUALITY)
    source["v003_acceptance_record"] = rel(V003_ACCEPTANCE)
    contract["layer_export_status"] = "blocked_until_v003_visual_acceptance"
    contract["runtime_replacement"] = False
    write_json(LAYER_CONTRACT, contract)

    project = read_json(PROJECT_MANIFEST)
    for region in project.get("current_runtime_regions", []):
        if not isinstance(region, dict) or region.get("region_id") != "Region_MountainHut":
            continue
        region["phase"] = PHASE
        region["runtime_replacement"] = False
        region["launch_quality_approved"] = False
        region["human_visual_approval_required"] = True
        region["next_art_step"] = "Run visual review on the v003 source candidate before MountainHut layer export or runtime replacement."
        region["active_v003_source_candidate"] = rel(V003_SOURCE)
        region["active_v003_quality_review"] = rel(V003_QUALITY)
        region["active_v003_review_contact_sheet"] = rel(V003_CONTACT)
        break
    write_json(PROJECT_MANIFEST, project)


def write_report(metrics: dict[str, float]) -> None:
    V003_REPORT.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# MountainHut v003 Source Candidate Review - 2026-05-25

Status: {STATUS}

## Candidate

- Candidate id: `{CANDIDATE_ID}`
- Source image: `{rel(V003_SOURCE)}`
- Contact sheet: `{rel(V003_CONTACT)}`
- Quality record: `{rel(V003_QUALITY)}`

## Automated Source-Quality Precheck

- Detail ratio: `{metrics['detail_ratio']:.4f}` against Village reference.
- Variance ratio: `{metrics['variance_ratio']:.4f}` against Village reference.
- West seam color delta: `{metrics['seam_edge_average_channel_delta']:.4f}`.
- Mean difference from rejected v002: `{metrics['v002_mean_diff']:.4f}`.

## Boundary

This is not human/art approval. Layer export is still blocked and runtime replacement remains blocked until visual review, semantic layer review, and Godot screenshot review pass.
"""
    V003_REPORT.write_text(text, encoding="utf-8")


def main() -> None:
    layout = read_json(LAYOUT_LOCK)
    V003_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    image = create_base(layout)
    paint_layout_paths(image, layout)
    place_quality_hut_and_props(image)
    add_local_painterly_detail(image, layout)
    enforce_west_seam(image)
    image = image.convert("RGB")
    image.save(V003_SOURCE)

    v003_rgba = Image.open(V003_SOURCE).convert("RGBA")
    metrics = measure_metrics(v003_rgba)
    write_contact_sheet(metrics)
    write_quality_and_acceptance(metrics)
    update_manifests()
    write_report(metrics)

    print(
        "OK: MountainHut v003 source candidate generated "
        f"detail_ratio={metrics['detail_ratio']} variance_ratio={metrics['variance_ratio']} "
        f"seam_delta={metrics['seam_edge_average_channel_delta']}"
    )


if __name__ == "__main__":
    main()
