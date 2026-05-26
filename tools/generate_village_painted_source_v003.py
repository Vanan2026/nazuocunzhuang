from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/village_world2d/v001"
V003_DIR = PACKAGE_DIR / "02_source_generation/v003_edge_continuity_repaint"
V003_SOURCE = V003_DIR / "village_painted_source_v003.png"
V003_ACCEPTANCE = V003_DIR / "source_acceptance_v003.json"
V003_QUALITY = V003_DIR / "source_quality_review_v003.json"
V003_CONTACT = V003_DIR / "village_v003_edge_continuity_contact_sheet.png"
V002_SOURCE = PACKAGE_DIR / "02_source_generation/v002_inherited_world_base_repaint/village_painted_source_v002.png"
OLD_SOURCE = PACKAGE_DIR / "02_source_generation/village_painted_source.png"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
REPORT = ROOT / ".codex/reports/village_v003_edge_continuity_source_review_2026-05-26.md"

CANVAS = (1800, 1200)
CONTACT_SIZE = (2400, 1500)
STATUS = "v003_edge_continuity_candidate_ready_for_visual_review"
CANDIDATE_ID = "village_painted_source_v003"


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


def edge_mask() -> Image.Image:
    mask = Image.new("L", CANVAS, 0)
    pixels = mask.load()
    for y in range(CANVAS[1]):
        for x in range(CANVAS[0]):
            distance = min(x, y, CANVAS[0] - 1 - x, CANVAS[1] - 1 - y)
            edge_strength = max(0.0, 1.0 - distance / 330.0)
            pixels[x, y] = int(255 * edge_strength * edge_strength)
    draw = ImageDraw.Draw(mask)
    # v002's visible blocker is the rounded pale crop edge. Keep the repair
    # scoped to the edge halo; center composition and object layout stay stable.
    draw.rounded_rectangle((104, 66, 1694, 1120), radius=160, outline=210, width=84)
    return mask.filter(ImageFilter.GaussianBlur(18))


def center_unify_mask() -> Image.Image:
    mask = Image.new("L", CANVAS, 16)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((260, 170, 1530, 930), radius=180, fill=52)
    return mask.filter(ImageFilter.GaussianBlur(30))


def create_candidate() -> Image.Image:
    v002 = Image.open(V002_SOURCE).convert("RGB")
    old = Image.open(OLD_SOURCE).convert("RGB")

    old_edge = ImageEnhance.Brightness(old).enhance(0.98)
    old_edge = ImageEnhance.Color(old_edge).enhance(0.92)
    old_edge = ImageEnhance.Contrast(old_edge).enhance(0.98)
    old_edge = old_edge.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=3))
    repaired = Image.composite(old_edge, v002, edge_mask())

    # Lightly reintroduce v002's accepted center so this is an edge-continuity
    # candidate, not a new isolated composition.
    candidate = Image.composite(v002, repaired, center_unify_mask())
    return candidate.convert("RGB")


def edge_detail_score(image: Image.Image) -> float:
    gray = image.convert("L")
    edges = ImageChops.difference(gray, gray.filter(ImageFilter.GaussianBlur(2.2)))
    return float(sum(ImageStat.Stat(edges).mean))


def mean_rgb_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def edge_review_band(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    band = Image.new("RGB", (1800, 960), (0, 0, 0))
    band.paste(rgb.crop((0, 0, 1800, 220)), (0, 0))
    band.paste(rgb.crop((0, 980, 1800, 1200)), (0, 240))
    band.paste(rgb.crop((0, 120, 260, 1080)).resize((900, 240), Image.Resampling.LANCZOS), (0, 500))
    band.paste(rgb.crop((1540, 120, 1800, 1080)).resize((900, 240), Image.Resampling.LANCZOS), (900, 500))
    return band


def metrics(candidate: Image.Image) -> dict[str, float]:
    v002 = Image.open(V002_SOURCE).convert("RGB")
    old = Image.open(OLD_SOURCE).convert("RGB")
    center = candidate.crop((360, 210, 1440, 930))
    center_v002 = v002.crop((360, 210, 1440, 930))
    center_old = old.crop((360, 210, 1440, 930))
    return {
        "edge_luminance_v003": round(float(ImageStat.Stat(edge_review_band(candidate).convert("L")).mean[0]), 4),
        "edge_luminance_v002": round(float(ImageStat.Stat(edge_review_band(v002).convert("L")).mean[0]), 4),
        "edge_detail_v003": round(edge_detail_score(edge_review_band(candidate)), 4),
        "edge_detail_v002": round(edge_detail_score(edge_review_band(v002)), 4),
        "edge_diff_from_v002": round(mean_rgb_diff(edge_review_band(candidate), edge_review_band(v002)), 4),
        "center_diff_from_v002": round(mean_rgb_diff(center, center_v002), 4),
        "center_diff_from_old_source": round(mean_rgb_diff(center, center_old), 4),
    }


def write_contact_sheet(candidate: Image.Image, values: dict[str, float]) -> None:
    v002 = Image.open(V002_SOURCE).convert("RGB")
    old = Image.open(OLD_SOURCE).convert("RGB")
    sheet = Image.new("RGB", CONTACT_SIZE, (226, 217, 190))
    draw = ImageDraw.Draw(sheet)
    draw.text((40, 30), "Village v003 edge-continuity source candidate", fill=(45, 35, 24), font=font(38))
    draw.text((40, 82), "Repair scope: edge_continuity_only. Full-canvas source stays registration-perfect; runtime flags stay false.", fill=(77, 60, 39), font=font(23))
    panels = [
        ("v002 current source: soft inherited edge", v002, (40, 140), (700, 500)),
        ("old Village source: edge detail reference", old, (850, 140), (700, 500)),
        ("v003 candidate", candidate, (1660, 140), (700, 500)),
        ("v002 edge review band", edge_review_band(v002), (40, 760), (1120, 420)),
        ("v003 edge review band", edge_review_band(candidate), (1240, 760), (1120, 420)),
    ]
    for title, image, xy, size in panels:
        x, y = xy
        w, h = size
        draw.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=(249, 244, 226), outline=(118, 96, 65), width=3)
        draw.text((x + 20, y + 18), title, fill=(52, 40, 28), font=font(24))
        preview = ImageOps.contain(image, (w - 40, h - 76), Image.Resampling.LANCZOS)
        sheet.paste(preview, (x + 20 + (w - 40 - preview.width) // 2, y + 62 + (h - 76 - preview.height) // 2))
    metric_text = (
        f"edge luminance v003/v002: {values['edge_luminance_v003']:.2f}/{values['edge_luminance_v002']:.2f} | "
        f"edge detail v003/v002: {values['edge_detail_v003']:.2f}/{values['edge_detail_v002']:.2f} | "
        f"center diff from v002: {values['center_diff_from_v002']:.2f} | "
        "human=false, layer=false, runtime=false, launch=false"
    )
    draw.rounded_rectangle((40, 1280, 2360, 1456), radius=14, fill=(249, 244, 226), outline=(118, 96, 65), width=3)
    draw.text((60, 1328), metric_text, fill=(62, 49, 34), font=font(23))
    sheet.save(V003_CONTACT)


def write_records(values: dict[str, float]) -> None:
    write_json(
        V003_ACCEPTANCE,
        {
            "candidate_id": CANDIDATE_ID,
            "status": STATUS,
            "repair_scope": "edge_continuity_only",
            "source_image": rel(V003_SOURCE),
            "derived_from": rel(V002_SOURCE),
            "edge_detail_reference": rel(OLD_SOURCE),
            "quality_review": rel(V003_QUALITY),
            "review_contact_sheet": rel(V003_CONTACT),
            "human_visual_approval": False,
            "layer_export_approved": False,
            "runtime_replacement": False,
            "launch_quality_approved": False,
            "next_required_step": "visual review, then export v003 semantic layers before Godot screenshot validation",
        },
    )
    write_json(
        V003_QUALITY,
        {
            "review_id": "village_v003_edge_continuity_source_quality_review",
            "status": STATUS,
            "source_candidate": rel(V003_SOURCE),
            "metrics": values,
            "producer_verdict": "Ready for visual review only; not runtime replacement.",
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
        f"""# Village v003 Edge Continuity Source Review - 2026-05-26

Status: {STATUS}

## Candidate

- Candidate id: `{CANDIDATE_ID}`
- Source image: `{rel(V003_SOURCE)}`
- Repair scope: `edge_continuity_only`
- Derived from: `{rel(V002_SOURCE)}`

## Automated Precheck

- Edge luminance v003: `{values['edge_luminance_v003']:.4f}`
- Edge luminance v002: `{values['edge_luminance_v002']:.4f}`
- Edge detail v003: `{values['edge_detail_v003']:.4f}`
- Edge detail v002: `{values['edge_detail_v002']:.4f}`
- Edge diff from v002: `{values['edge_diff_from_v002']:.4f}`
- Center diff from v002: `{values['center_diff_from_v002']:.4f}`

## Boundary

This is edge continuity source evidence, not runtime replacement and not launch-quality approval. Full-canvas layer export and Godot screenshot review remain required.
""",
        encoding="utf-8",
    )


def update_manifests() -> None:
    workflow = read_json(WORKFLOW)
    workflow["status"] = STATUS
    workflow["current_phase"] = "02_source_generation_v003_edge_continuity_review"
    workflow["v003_edge_continuity_source_candidate"] = {
        "candidate_id": CANDIDATE_ID,
        "status": STATUS,
        "image": rel(V003_SOURCE),
        "acceptance_record": rel(V003_ACCEPTANCE),
        "quality_review": rel(V003_QUALITY),
        "review_contact_sheet": rel(V003_CONTACT),
        "repair_scope": "edge_continuity_only",
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
    }
    phase_status = workflow.setdefault("phase_status", {})
    phase_status["02_source_generation_v003_edge_continuity"] = STATUS
    phase_status["03_layer_export_v003"] = "blocked_until_v003_visual_acceptance"
    phase_status["04_godot_integration_v003"] = "blocked_until_v003_layer_export_and_godot_screenshot"
    workflow.setdefault("validation", {})["v003_edge_continuity_source_validator"] = "tools/validate_village_v003_edge_continuity_source.py"
    workflow["runtime_replacement"] = False
    write_json(WORKFLOW, workflow)

    contract = read_json(LAYER_CONTRACT)
    source = contract.setdefault("source_image", {})
    source["v003_candidate"] = rel(V003_SOURCE)
    source["v003_quality_review"] = rel(V003_QUALITY)
    source["v003_acceptance_record"] = rel(V003_ACCEPTANCE)
    source["v003_layer_export_status"] = "blocked_until_v003_visual_acceptance"
    contract["runtime_replacement"] = False
    write_json(LAYER_CONTRACT, contract)

    project = read_json(PROJECT_MANIFEST)
    for record in project.get("current_runtime_regions", []):
        if record.get("region_id") != "Region_Village":
            continue
        record["phase"] = STATUS
        record["active_v003_source_candidate"] = rel(V003_SOURCE)
        record["active_v003_quality_review"] = rel(V003_QUALITY)
        record["active_v003_review_contact_sheet"] = rel(V003_CONTACT)
        record["next_art_step"] = "Visual review Village v003 edge-continuity source, then export v003 semantic layers before runtime replacement."
        record["runtime_replacement"] = False
        record["launch_quality_approved"] = False
        record["human_visual_approval_required"] = True
        break
    write_json(PROJECT_MANIFEST, project)


def main() -> None:
    V003_DIR.mkdir(parents=True, exist_ok=True)
    candidate = create_candidate()
    candidate.save(V003_SOURCE)
    values = metrics(candidate)
    write_contact_sheet(candidate, values)
    write_records(values)
    update_manifests()
    print(
        "OK: generated village_painted_source_v003 "
        f"edge_luma={values['edge_luminance_v003']} "
        f"edge_detail={values['edge_detail_v003']} "
        f"center_diff={values['center_diff_from_v002']}"
    )


if __name__ == "__main__":
    main()
