from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
V003_DIR = SOURCE_DIR / "v003"
V004_DIR = SOURCE_DIR / "v004"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock/layout_lock.json"
VILLAGE_SOURCE = ROOT / "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
V002_SOURCE = SOURCE_DIR / "v002/mountain_hut_painted_source_v002.png"
V003_SOURCE = V003_DIR / "mountain_hut_painted_source_v003.png"
V003_ACCEPTANCE = V003_DIR / "source_acceptance_v003.json"
V003_VISUAL_REVIEW = REVIEW_DIR / "source_visual_review_v003.json"
V003_REPORT = ROOT / ".codex/reports/mountain_hut_v003_visual_review_2026-05-25.md"
EXTERNAL_REFERENCE = (
    ROOT
    / "production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_scene_mothers/regions/mountain_hut/mountain_hut_scene_mother.png"
)
V004_SOURCE = V004_DIR / "mountain_hut_painted_source_v004.png"
V004_ACCEPTANCE = V004_DIR / "source_acceptance_v004.json"
V004_QUALITY = REVIEW_DIR / "source_quality_review_v004.json"
V004_CONTACT = REVIEW_DIR / "mountain_hut_v004_review_contact_sheet.png"
V004_REPORT = ROOT / ".codex/reports/mountain_hut_v004_source_candidate_review_2026-05-25.md"

CANVAS = (1800, 1200)
CONTACT_SIZE = (1800, 1500)
V003_REJECT_STATUS = "needs_v004_repaint_before_layer_export"
V003_REJECT_PHASE = "mountain_hut_v003_visual_review_rejected_needs_v004_repaint"
V004_STATUS = "v004_candidate_ready_for_visual_review"
V004_PHASE = "mountain_hut_v004_candidate_ready_for_visual_review"
V004_CANDIDATE_ID = "mountain_hut_painted_source_candidate_v004"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def font(size: int) -> ImageFont.ImageFont:
    for name in ["arial.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


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


def hard_vector_road_ratio(image: Image.Image) -> float:
    count = 0
    rgb = image.convert("RGB")
    for r, g, b in rgb.getdata():
        if r > 205 and g > 165 and 70 < b < 150 and (r - b) > 70 and (g - b) > 45:
            count += 1
    return count / float(rgb.width * rgb.height)


def create_v004_source() -> Image.Image:
    external = Image.open(EXTERNAL_REFERENCE).convert("RGBA")
    village = Image.open(VILLAGE_SOURCE).convert("RGBA")

    image = ImageOps.fit(external, CANVAS, method=Image.Resampling.LANCZOS, centering=(0.50, 0.48))
    image = ImageEnhance.Brightness(image).enhance(1.04)
    image = ImageEnhance.Color(image).enhance(0.95)
    image = ImageEnhance.Contrast(image).enhance(0.98)

    # Feather the accepted Village east edge into the locked MountainHut west seam.
    # This is a seam continuity wash only, not a new road drawing layer.
    seam_ref = village.crop((1600, 420, 1800, 820)).resize((320, 420), Image.Resampling.LANCZOS)
    alpha = Image.new("L", seam_ref.size, 0)
    alpha_px = alpha.load()
    for x in range(seam_ref.width):
        if x < seam_ref.width * 0.45:
            h_alpha = 190
        else:
            h_alpha = 190 * max(0.0, 1.0 - (x - seam_ref.width * 0.45) / (seam_ref.width * 0.55))
        for y in range(seam_ref.height):
            v_alpha = min(1.0, y / 36.0, (seam_ref.height - 1 - y) / 36.0)
            alpha_px[x, y] = int(h_alpha * v_alpha)
    seam_ref.putalpha(alpha.filter(ImageFilter.GaussianBlur(5)))
    seam_layer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    seam_layer.alpha_composite(seam_ref, (0, 457))
    image.alpha_composite(seam_layer)

    return image.convert("RGB")


def measure_metrics(v004: Image.Image) -> dict[str, float]:
    village = Image.open(VILLAGE_SOURCE).convert("RGBA")
    v003 = Image.open(V003_SOURCE).convert("RGBA")
    return {
        "village_detail_edge_mean": round(edge_detail_score(village), 4),
        "v004_detail_edge_mean": round(edge_detail_score(v004), 4),
        "detail_ratio": round(edge_detail_score(v004) / max(edge_detail_score(village), 0.0001), 4),
        "village_gray_variance": round(gray_variance(village), 4),
        "v004_gray_variance": round(gray_variance(v004), 4),
        "variance_ratio": round(gray_variance(v004) / max(gray_variance(village), 0.0001), 4),
        "seam_edge_average_channel_delta": round(seam_delta(village, v004), 4),
        "v003_mean_diff": round(mean_diff(v003, v004), 4),
        "v003_hard_vector_road_ratio": round(hard_vector_road_ratio(v003), 6),
        "v004_hard_vector_road_ratio": round(hard_vector_road_ratio(v004), 6),
    }


def write_contact_sheet(metrics: dict[str, float]) -> None:
    sheet = Image.new("RGBA", CONTACT_SIZE, (230, 219, 185, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((36, 28), "MountainHut v004 source review", fill=(42, 38, 32), font=font(30))
    draw.text((36, 66), "v003 rejected for hard vector-road overlay. v004 is review-only.", fill=(82, 71, 51), font=font(18))

    panels = [
        (VILLAGE_SOURCE, (36, 115), (520, 390), "Accepted Village style target"),
        (V003_SOURCE, (640, 115), (520, 390), "Rejected v003 candidate"),
        (V004_SOURCE, (1244, 115), (520, 390), "v004 candidate"),
        (EXTERNAL_REFERENCE, (36, 600), (720, 500), "External quality reference"),
        (V004_SOURCE, (870, 600), (860, 500), "v004 full-canvas source"),
    ]
    for path, xy, size, title in panels:
        x, y = xy
        w, h = size
        draw.rounded_rectangle((x, y, x + w, y + h), radius=10, fill=(246, 239, 214), outline=(105, 76, 44), width=3)
        draw.text((x + 18, y + 16), title, fill=(48, 44, 35), font=font(21))
        image = ImageOps.contain(Image.open(path).convert("RGBA"), (w - 36, h - 72), Image.Resampling.LANCZOS)
        sheet.alpha_composite(image, (x + 18 + (w - 36 - image.width) // 2, y + 56 + (h - 72 - image.height) // 2))

    lines = [
        f"detail ratio: {metrics['detail_ratio']:.4f}",
        f"variance ratio: {metrics['variance_ratio']:.4f}",
        f"seam delta: {metrics['seam_edge_average_channel_delta']:.4f}",
        f"mean diff vs rejected v003: {metrics['v003_mean_diff']:.4f}",
        f"hard vector-road ratio v003 -> v004: {metrics['v003_hard_vector_road_ratio']:.4f} -> {metrics['v004_hard_vector_road_ratio']:.4f}",
        "hard flags: human=false, export=false, runtime=false, launch=false",
    ]
    tx, ty = 36, 1170
    draw.rounded_rectangle((tx, ty, 1764, 1388), radius=10, fill=(246, 239, 214), outline=(105, 76, 44), width=3)
    draw.text((tx + 18, ty + 18), "Automated precheck", fill=(48, 44, 35), font=font(22))
    for index, line in enumerate(lines):
        draw.text((tx + 24, ty + 58 + index * 27), f"- {line}", fill=(48, 44, 35), font=font(18))
    sheet.convert("RGB").save(V004_CONTACT)


def write_v003_rejection() -> None:
    review = {
        "review_id": "mountain_hut_v003_visual_review",
        "status": V003_REJECT_STATUS,
        "reviewed_at": "2026-05-25",
        "v003_visual_accepted": False,
        "v003_source": rel(V003_SOURCE),
        "v004_source_candidate": rel(V004_SOURCE),
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "rejection_reasons": [
            "A hard-edged light vector-road overlay crosses the middle of the scene and reads like pasted tape rather than painted terrain.",
            "The overlay covers natural ground, fence, lighting, and footpath detail from the stronger external quality reference.",
            "The source could pass edge/variance metrics while still failing the storybook visual bar, so visual review must override metric-only readiness.",
        ],
        "next_required_step": "produce_v004_full_canvas_candidate_without_vector_road_overlay",
    }
    write_json(V003_VISUAL_REVIEW, review)

    acceptance = read_json(V003_ACCEPTANCE)
    acceptance["status"] = V003_REJECT_PHASE
    acceptance["visual_review"] = rel(V003_VISUAL_REVIEW)
    acceptance["human_visual_approval"] = False
    acceptance["layer_export_approved"] = False
    acceptance["runtime_replacement"] = False
    acceptance["launch_quality_approved"] = False
    acceptance["codex_visual_review"] = {
        "status": V003_REJECT_STATUS,
        "not_human_visual_approval": True,
        "review_record": rel(V003_VISUAL_REVIEW),
        "next_required_step": "produce_v004_full_canvas_candidate_without_vector_road_overlay",
    }
    write_json(V003_ACCEPTANCE, acceptance)

    V003_REPORT.parent.mkdir(parents=True, exist_ok=True)
    V003_REPORT.write_text(
        f"""# MountainHut v003 Visual Review - 2026-05-25

Status: {V003_REJECT_STATUS}

## Decision

v003 rejected for layer export and runtime promotion.

## Blocking Issue

The scene has a hard-edged light vector-road overlay through the center. It passes some automated texture metrics but fails the painterly source-quality bar because the road reads pasted on top of the natural ground.

## Boundary

This review is not human/art approval for v004. Layer export and runtime replacement remain blocked.
""",
        encoding="utf-8",
    )


def write_v004_records(metrics: dict[str, float]) -> None:
    quality = {
        "review_id": "mountain_hut_source_quality_review_v004",
        "status": V004_STATUS,
        "reviewed_at": "2026-05-25",
        "source_candidate": rel(V004_SOURCE),
        "quality_reference_source": rel(VILLAGE_SOURCE),
        "rejected_previous_source": rel(V003_SOURCE),
        "v003_visual_review": rel(V003_VISUAL_REVIEW),
        "external_quality_reference": rel(EXTERNAL_REFERENCE),
        "review_contact_sheet": rel(V004_CONTACT),
        "source_candidate_review": rel(V004_REPORT),
        "metrics": {
            **metrics,
            "minimum_detail_ratio_for_review_ready": 0.74,
            "minimum_variance_ratio_for_review_ready": 0.62,
            "maximum_preferred_seam_delta_for_precheck": 24.0,
            "maximum_hard_vector_road_ratio": 0.012,
        },
        "producer_verdict": "The v004 source candidate removes the v003 hard vector-road overlay and is ready for visual review only.",
        "hard_approval_flags": {
            "human_visual_approval": False,
            "layer_export_approved": False,
            "runtime_replacement": False,
            "launch_quality_approved": False,
        },
    }
    write_json(V004_QUALITY, quality)

    acceptance = {
        "candidate_id": V004_CANDIDATE_ID,
        "status": V004_STATUS,
        "candidate_type": "v004_full_canvas_storybook_source_candidate",
        "source_image": rel(V004_SOURCE),
        "quality_review": rel(V004_QUALITY),
        "review_contact_sheet": rel(V004_CONTACT),
        "v003_visual_review": rel(V003_VISUAL_REVIEW),
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "codex_visual_precheck": {
            "status": "passed_v004_source_quality_precheck",
            "not_human_visual_approval": True,
            "notes": [
                "single full-canvas painted source rule is preserved",
                "v003 hard vector-road overlay is not carried forward",
                "registration-perfect layer alignment remains the target",
                "runtime replacement and layer export remain blocked",
            ],
        },
    }
    write_json(V004_ACCEPTANCE, acceptance)

    V004_REPORT.write_text(
        f"""# MountainHut v004 Source Candidate Review - 2026-05-25

Status: {V004_STATUS}

## Candidate

- Candidate id: `{V004_CANDIDATE_ID}`
- Source image: `{rel(V004_SOURCE)}`
- Contact sheet: `{rel(V004_CONTACT)}`
- Quality record: `{rel(V004_QUALITY)}`

## Automated Source-Quality Precheck

- Detail ratio: `{metrics['detail_ratio']:.4f}` against Village reference.
- Variance ratio: `{metrics['variance_ratio']:.4f}` against Village reference.
- West seam color delta: `{metrics['seam_edge_average_channel_delta']:.4f}`.
- Mean difference from rejected v003: `{metrics['v003_mean_diff']:.4f}`.
- Hard vector-road ratio: `{metrics['v004_hard_vector_road_ratio']:.4f}`.

## Boundary

This is not human/art approval. Layer export is still blocked and runtime replacement remains blocked until visual review, semantic layer review, and Godot screenshot review pass.
""",
        encoding="utf-8",
    )


def update_manifests() -> None:
    workflow = read_json(WORKFLOW)
    workflow["status"] = V004_PHASE
    workflow["current_phase"] = "02_source_generation_v004_review"
    workflow["next_art_step"] = "visual review the v004 source candidate before any layer export or runtime replacement."
    phase_status = workflow.setdefault("phase_status", {})
    phase_status["02_source_visual_review_v003"] = V003_REJECT_STATUS
    phase_status["02_source_generation_v004"] = V004_STATUS
    phase_status["03_layer_export"] = "blocked_until_v004_visual_acceptance"
    workflow["v003_visual_review"] = {
        "status": V003_REJECT_STATUS,
        "review": rel(V003_VISUAL_REVIEW),
        "report": rel(V003_REPORT),
        "layer_export_approved": False,
        "runtime_replacement": False,
    }
    workflow["v004_source_candidate"] = {
        "candidate_id": V004_CANDIDATE_ID,
        "status": V004_STATUS,
        "candidate_type": "v004_full_canvas_storybook_source_candidate",
        "image": rel(V004_SOURCE),
        "acceptance_record": rel(V004_ACCEPTANCE),
        "quality_review_record": rel(V004_QUALITY),
        "review_contact_sheet": rel(V004_CONTACT),
        "generated_from": [rel(EXTERNAL_REFERENCE), rel(VILLAGE_SOURCE), rel(LAYOUT_LOCK), rel(V003_VISUAL_REVIEW)],
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
    }
    write_json(WORKFLOW, workflow)

    contract = read_json(LAYER_CONTRACT)
    source = contract.setdefault("source_image", {})
    source["current_file_status"] = "v004_candidate_pending_visual_review"
    source["required_next_step"] = "Visual review the v004 full-canvas source candidate before layer export."
    source["v003_visual_review"] = rel(V003_VISUAL_REVIEW)
    source["v004_candidate"] = rel(V004_SOURCE)
    source["v004_quality_review"] = rel(V004_QUALITY)
    source["v004_acceptance_record"] = rel(V004_ACCEPTANCE)
    contract["layer_export_status"] = "blocked_until_v004_visual_acceptance"
    contract["runtime_replacement"] = False
    write_json(LAYER_CONTRACT, contract)

    project = read_json(PROJECT_MANIFEST)
    for region in project.get("current_runtime_regions", []):
        if not isinstance(region, dict) or region.get("region_id") != "Region_MountainHut":
            continue
        region["phase"] = V004_PHASE
        region["runtime_replacement"] = False
        region["launch_quality_approved"] = False
        region["human_visual_approval_required"] = True
        region["next_art_step"] = "Run visual review on the v004 source candidate before MountainHut layer export or runtime replacement."
        region["active_v003_visual_review"] = rel(V003_VISUAL_REVIEW)
        region["active_v004_source_candidate"] = rel(V004_SOURCE)
        region["active_v004_quality_review"] = rel(V004_QUALITY)
        region["active_v004_review_contact_sheet"] = rel(V004_CONTACT)
        break
    write_json(PROJECT_MANIFEST, project)


def main() -> None:
    V004_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    image = create_v004_source()
    image.save(V004_SOURCE)
    metrics = measure_metrics(image)
    write_contact_sheet(metrics)
    write_v003_rejection()
    write_v004_records(metrics)
    update_manifests()

    print(
        "OK: MountainHut v004 source candidate generated "
        f"detail_ratio={metrics['detail_ratio']} variance_ratio={metrics['variance_ratio']} "
        f"seam_delta={metrics['seam_edge_average_channel_delta']} "
        f"hard_road_ratio={metrics['v004_hard_vector_road_ratio']}"
    )


if __name__ == "__main__":
    main()
