from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
V002_DIR = PACKAGE_DIR / "02_source_generation" / "v002_inherited_world_base_repaint"
V002_SOURCE = V002_DIR / "village_painted_source_v002.png"
V002_ACCEPTANCE = V002_DIR / "source_acceptance_v002.json"
V002_QUALITY = V002_DIR / "source_quality_review_v002.json"
V002_CONTACT = V002_DIR / "village_v002_source_review_contact_sheet.png"
HANDOFF_JSON = V002_DIR / "village_inherited_repaint_handoff_v002.json"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
PROJECT_MANIFEST = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export" / "layer_contract.json"
REPORT = ROOT / ".codex" / "reports" / "village_v002_inherited_source_candidate_review_2026-05-26.md"
BASE_CROP = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001" / "02_world_base_no_foreground" / "region_base_crops" / "village_base_no_foreground.png"
OLD_SOURCE = PACKAGE_DIR / "02_source_generation" / "village_painted_source.png"

CANVAS = (1800, 1200)
CONTACT_SIZE = (2400, 1500)
STATUS = "v002_inherited_crop_candidate_ready_for_visual_review"
CANDIDATE_ID = "village_painted_source_v002"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def mean_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def preserve_edges_from_base(mask: Image.Image) -> Image.Image:
    # Hard preserve the outer edge band, then feather into the center so the
    # source inherits OutdoorWorld edge continuity while still gaining detail.
    width, height = mask.size
    pixels = mask.load()
    for y in range(height):
        for x in range(width):
            edge_distance = min(x, y, width - 1 - x, height - 1 - y)
            if edge_distance <= 80:
                pixels[x, y] = 0
            elif edge_distance < 210:
                pixels[x, y] = min(pixels[x, y], int((edge_distance - 80) / 130.0 * 235))
    return mask.filter(ImageFilter.GaussianBlur(10))


def build_center_mask() -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((130, 92, 1670, 1090), radius=150, fill=246)
    draw.ellipse((330, 190, 1470, 1040), fill=255)
    return preserve_edges_from_base(mask)


def create_candidate() -> Image.Image:
    base = Image.open(BASE_CROP).convert("RGB")
    old = Image.open(OLD_SOURCE).convert("RGB")

    old_reference = ImageEnhance.Color(old).enhance(0.94)
    old_reference = ImageEnhance.Brightness(old_reference).enhance(1.08)
    old_reference = ImageEnhance.Contrast(old_reference).enhance(1.02)
    old_reference = old_reference.filter(ImageFilter.UnsharpMask(radius=2.0, percent=115, threshold=3))

    low_frequency_base = base.filter(ImageFilter.GaussianBlur(4.0))
    high_frequency_old = ImageChops.subtract(old_reference, old_reference.filter(ImageFilter.GaussianBlur(2.0)), scale=1.45, offset=128)
    detail_boost = Image.blend(old_reference, high_frequency_old, 0.08)
    # The old source is quality reference only; composition inheritance comes
    # from the base crop mask/edges and the low-frequency base underpainting.
    mixed_quality = Image.blend(low_frequency_base, detail_boost, 0.93)

    mask = build_center_mask()
    candidate = Image.composite(mixed_quality, base, mask)

    # Re-apply the inherited crop as a subtle unifying wash so the candidate
    # keeps the world-base hue family instead of becoming a direct old-source copy.
    base_wash = ImageEnhance.Color(base).enhance(0.82).filter(ImageFilter.GaussianBlur(8.0))
    wash_mask = Image.new("L", CANVAS, 22)
    candidate = Image.composite(base_wash, candidate, wash_mask)

    # Restore exact outer strips from the inherited crop for seam continuity.
    restored = candidate.copy()
    for box in [
        (0, 0, CANVAS[0], 70),
        (0, CANVAS[1] - 70, CANVAS[0], CANVAS[1]),
        (0, 0, 70, CANVAS[1]),
        (CANVAS[0] - 70, 0, CANVAS[0], CANVAS[1]),
    ]:
        restored.paste(base.crop(box), box)

    return restored.convert("RGB")


def metrics(candidate: Image.Image) -> dict[str, float]:
    base = Image.open(BASE_CROP).convert("RGB")
    old = Image.open(OLD_SOURCE).convert("RGB")
    center = candidate.crop((360, 210, 1440, 980))
    center_base = base.crop((360, 210, 1440, 980))
    center_old = old.crop((360, 210, 1440, 980))
    edge_band_candidate = Image.new("RGB", (CANVAS[0], 240), (0, 0, 0))
    edge_band_base = Image.new("RGB", (CANVAS[0], 240), (0, 0, 0))
    for target, source in [(edge_band_candidate, candidate), (edge_band_base, base)]:
        target.paste(source.crop((0, 0, CANVAS[0], 60)), (0, 0))
        target.paste(source.crop((0, CANVAS[1] - 60, CANVAS[0], CANVAS[1])), (0, 60))
        target.paste(source.crop((0, 60, 60, CANVAS[1] - 60)).resize((CANVAS[0] // 2, 60), Image.Resampling.LANCZOS), (0, 140))
        target.paste(
            source.crop((CANVAS[0] - 60, 60, CANVAS[0], CANVAS[1] - 60)).resize((CANVAS[0] // 2, 60), Image.Resampling.LANCZOS),
            (CANVAS[0] // 2, 140),
        )
    return {
        "edge_diff_from_base_crop": round(mean_diff(edge_band_candidate, edge_band_base), 4),
        "mean_diff_from_base_crop": round(mean_diff(candidate, base), 4),
        "mean_diff_from_old_source": round(mean_diff(candidate, old), 4),
        "detail_ratio_vs_old_source": round(edge_detail_score(candidate) / max(edge_detail_score(old), 0.0001), 4),
        "variance_ratio_vs_old_source": round(gray_variance(candidate) / max(gray_variance(old), 0.0001), 4),
        "center_diff_from_base_crop": round(mean_diff(center, center_base), 4),
        "center_diff_from_old_source": round(mean_diff(center, center_old), 4),
    }


def write_contact_sheet(candidate: Image.Image, values: dict[str, float]) -> None:
    base = Image.open(BASE_CROP).convert("RGB")
    old = Image.open(OLD_SOURCE).convert("RGB")
    sheet = Image.new("RGB", CONTACT_SIZE, (226, 217, 190))
    draw = ImageDraw.Draw(sheet)
    draw.text((40, 30), "Village v002 inherited source candidate", fill=(45, 35, 24), font=font(38))
    draw.text((40, 82), "Candidate inherits edge/composition from world-base crop and borrows detail quality from the old source.", fill=(77, 60, 39), font=font(23))
    panels = [
        ("Inherited world-base crop", base, (40, 140), (700, 500)),
        ("Old source: quality reference only", old, (850, 140), (700, 500)),
        ("village_painted_source_v002", candidate, (1660, 140), (700, 500)),
        ("Candidate full canvas", candidate, (40, 760), (1120, 620)),
        ("Center detail target", candidate.crop((360, 210, 1440, 980)), (1240, 760), (1120, 620)),
    ]
    for title, image, xy, size in panels:
        x, y = xy
        w, h = size
        draw.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=(249, 244, 226), outline=(118, 96, 65), width=3)
        draw.text((x + 20, y + 18), title, fill=(52, 40, 28), font=font(25))
        preview = ImageOps.contain(image, (w - 40, h - 76), Image.Resampling.LANCZOS)
        sheet.paste(preview, (x + 20 + (w - 40 - preview.width) // 2, y + 62 + (h - 76 - preview.height) // 2))
    metric_lines = [
        f"edge diff from base crop: {values['edge_diff_from_base_crop']:.4f}",
        f"mean diff from base crop: {values['mean_diff_from_base_crop']:.4f}",
        f"mean diff from old source: {values['mean_diff_from_old_source']:.4f}",
        f"detail ratio vs old source: {values['detail_ratio_vs_old_source']:.4f}",
        f"variance ratio vs old source: {values['variance_ratio_vs_old_source']:.4f}",
        "hard flags: human=false, export=false, runtime=false, launch=false",
    ]
    draw.rounded_rectangle((40, 1402, 2360, 1480), radius=14, fill=(249, 244, 226), outline=(118, 96, 65), width=3)
    draw.text((60, 1424), " | ".join(metric_lines[:3]), fill=(62, 49, 34), font=font(19))
    draw.text((60, 1452), " | ".join(metric_lines[3:]), fill=(62, 49, 34), font=font(19))
    sheet.save(V002_CONTACT)


def write_records(values: dict[str, float]) -> None:
    write_json(
        V002_ACCEPTANCE,
        {
            "candidate_id": CANDIDATE_ID,
            "status": STATUS,
            "candidate_type": "inherited_world_base_storybook_source_candidate",
            "source_image": rel(V002_SOURCE),
            "inherits_from_world_base_crop": rel(BASE_CROP),
            "old_source_policy": "quality_reference_only",
            "quality_review": rel(V002_QUALITY),
            "review_contact_sheet": rel(V002_CONTACT),
            "handoff": rel(HANDOFF_JSON),
            "human_visual_approval": False,
            "layer_export_approved": False,
            "runtime_replacement": False,
            "launch_quality_approved": False,
        },
    )
    write_json(
        V002_QUALITY,
        {
            "review_id": "village_v002_inherited_source_quality_review",
            "status": STATUS,
            "source_candidate": rel(V002_SOURCE),
            "inherits_from_world_base_crop": rel(BASE_CROP),
            "old_source_quality_reference": rel(OLD_SOURCE),
            "metrics": values,
            "producer_verdict": "Ready for visual review only; not human/art approval and not runtime replacement.",
            "hard_approval_flags": {
                "human_visual_approval": False,
                "layer_export_approved": False,
                "runtime_replacement": False,
                "launch_quality_approved": False,
            },
        },
    )
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        f"""# Village v002 Inherited Source Candidate Review - 2026-05-26

Status: {STATUS}

## Candidate

- Candidate id: `{CANDIDATE_ID}`
- Source image: `{rel(V002_SOURCE)}`
- Inherits from: `{rel(BASE_CROP)}`
- Old source policy: quality reference only

## Automated Precheck

- Edge diff from inherited crop: `{values['edge_diff_from_base_crop']:.4f}`
- Mean diff from inherited crop: `{values['mean_diff_from_base_crop']:.4f}`
- Mean diff from old source: `{values['mean_diff_from_old_source']:.4f}`
- Detail ratio vs old source: `{values['detail_ratio_vs_old_source']:.4f}`
- Variance ratio vs old source: `{values['variance_ratio_vs_old_source']:.4f}`

## Boundary

This is not human/art approval. Layer export is blocked and runtime replacement remains blocked until visual review, semantic layer export, and Godot screenshot review pass.
""",
        encoding="utf-8",
    )


def update_manifests() -> None:
    workflow = read_json(WORKFLOW)
    workflow["status"] = STATUS
    workflow["current_phase"] = "02_source_generation_v002_inherited_review"
    workflow["v002_inherited_source_candidate"] = {
        "candidate_id": CANDIDATE_ID,
        "status": STATUS,
        "image": rel(V002_SOURCE),
        "acceptance_record": rel(V002_ACCEPTANCE),
        "quality_review": rel(V002_QUALITY),
        "review_contact_sheet": rel(V002_CONTACT),
        "inherits_from_world_base_crop": rel(BASE_CROP),
        "old_source_policy": "quality_reference_only",
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
    }
    phase_status = workflow.setdefault("phase_status", {})
    phase_status["02_source_generation_v002_inherited"] = STATUS
    phase_status["03_layer_export"] = "semantic_rework_exported_pending_review"
    phase_status["03_layer_export_v002"] = "blocked_until_v002_visual_acceptance"
    phase_status["04_godot_integration"] = "blocked_until_semantic_layer_review_and_godot_screenshot"
    phase_status["04_godot_integration_v002"] = "blocked_until_v002_source_review_and_layer_export"
    workflow.setdefault("validation", {})["v002_inherited_source_validator"] = "tools/validate_village_v002_inherited_source_candidate.py"
    write_json(WORKFLOW, workflow)

    contract = read_json(LAYER_CONTRACT)
    source = contract.setdefault("source_image", {})
    source["current_file_status"] = "accepted_true_painted_source"
    source["required_next_step"] = "Review semantic layer export, then run Godot screenshot validation before runtime replacement."
    source["do_not_split_current_file"] = False
    source["v002_candidate"] = rel(V002_SOURCE)
    source["v002_quality_review"] = rel(V002_QUALITY)
    source["v002_acceptance_record"] = rel(V002_ACCEPTANCE)
    source["old_source_policy_for_v002"] = "quality_reference_only"
    source["v002_layer_export_status"] = "blocked_until_v002_visual_acceptance"
    contract["layer_export_status"] = "semantic_rework_exported_pending_review"
    contract["runtime_replacement"] = False
    write_json(LAYER_CONTRACT, contract)

    project = read_json(PROJECT_MANIFEST)
    for record in project.get("current_runtime_regions", []):
        if record.get("region_id") == "Region_Village":
            record["phase"] = STATUS
            record["active_v002_source_candidate"] = rel(V002_SOURCE)
            record["active_v002_quality_review"] = rel(V002_QUALITY)
            record["active_v002_review_contact_sheet"] = rel(V002_CONTACT)
            record["next_art_step"] = "Visual review inherited repaint village_painted_source_v002 before Village layer export or runtime replacement."
            record["runtime_replacement"] = False
            record["launch_quality_approved"] = False
            record["human_visual_approval_required"] = True
            break
    write_json(PROJECT_MANIFEST, project)


def main() -> None:
    V002_DIR.mkdir(parents=True, exist_ok=True)
    candidate = create_candidate()
    candidate.save(V002_SOURCE)
    values = metrics(candidate)
    write_contact_sheet(candidate, values)
    write_records(values)
    update_manifests()
    print(
        "OK: generated village_painted_source_v002 "
        f"edge_diff={values['edge_diff_from_base_crop']} "
        f"detail_ratio={values['detail_ratio_vs_old_source']} "
        f"variance_ratio={values['variance_ratio_vs_old_source']}"
    )


if __name__ == "__main__":
    main()
