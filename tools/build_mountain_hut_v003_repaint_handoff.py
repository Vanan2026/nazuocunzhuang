from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
V002_DIR = SOURCE_DIR / "v002"
V003_DIR = SOURCE_DIR / "v003"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock/layout_lock.json"
VILLAGE_SOURCE = ROOT / "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
V002_SOURCE = V002_DIR / "mountain_hut_painted_source_v002.png"
V002_ACCEPTANCE = V002_DIR / "source_acceptance_v002.json"
VISUAL_REVIEW = REVIEW_DIR / "source_visual_review_v002.json"
V003_BRIEF = V003_DIR / "mountain_hut_repaint_v003_brief.md"
V003_REFERENCE_SHEET = REVIEW_DIR / "mountain_hut_v003_repaint_reference_sheet.png"
V002_REPORT = ROOT / ".codex/reports/mountain_hut_v002_visual_review_2026-05-25.md"
EXTERNAL_REFERENCE = (
    ROOT
    / "production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_scene_mothers/regions/mountain_hut/mountain_hut_scene_mother.png"
)

STATUS = "needs_v003_repaint_before_layer_export"
PHASE = "mountain_hut_v002_visual_review_rejected_needs_v003_repaint"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def font(size: int) -> ImageFont.ImageFont:
    for name in ["arial.ttf", "DejaVuSans.ttf", "seguiemj.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit_image(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    return ImageOps.contain(image, size, Image.Resampling.LANCZOS)


def paste_panel(
    sheet: Image.Image,
    draw: ImageDraw.ImageDraw,
    path: Path,
    xy: tuple[int, int],
    size: tuple[int, int],
    title: str,
    subtitle: str,
    outline: tuple[int, int, int],
) -> None:
    x, y = xy
    w, h = size
    draw.rounded_rectangle((x, y, x + w, y + h), radius=10, fill=(246, 239, 214), outline=outline, width=3)
    draw.text((x + 18, y + 14), title, fill=(48, 44, 35), font=font(24))
    draw.text((x + 18, y + 48), subtitle, fill=(83, 74, 54), font=font(16))
    image = fit_image(path, (w - 36, h - 92))
    px = x + 18 + (w - 36 - image.width) // 2
    py = y + 78 + (h - 92 - image.height) // 2
    sheet.alpha_composite(image, (px, py))


def draw_layout_panel(sheet: Image.Image, draw: ImageDraw.ImageDraw, layout: dict[str, Any]) -> None:
    x, y = 930, 795
    w, h = 820, 520
    draw.rounded_rectangle((x, y, x + w, y + h), radius=10, fill=(246, 239, 214), outline=(116, 82, 46), width=3)
    draw.text((x + 18, y + 14), "V003 LOCKED CANVAS REQUIREMENTS", fill=(48, 44, 35), font=font(24))
    draw.text((x + 18, y + 48), "Use this as spatial lock, not pixel tracing.", fill=(83, 74, 54), font=font(16))

    canvas = (520, 347)
    ox, oy = x + 36, y + 112
    draw.rectangle((ox, oy, ox + canvas[0], oy + canvas[1]), fill=(83, 116, 60), outline=(60, 77, 43), width=2)
    sx = canvas[0] / 1800.0
    sy = canvas[1] / 1200.0

    for road in layout.get("road_paths", []):
        points = road.get("source_points", [])
        scaled = [(round(ox + px * sx), round(oy + py * sy)) for px, py in points]
        if len(scaled) >= 2:
            width = max(8, round(float(road.get("source_width", 54)) * sx))
            draw.line(scaled, fill=(226, 184, 104), width=width + 9, joint="curve")
            draw.line(scaled, fill=(105, 91, 61), width=max(2, width + 14), joint="curve")
            draw.line(scaled, fill=(226, 184, 104), width=width, joint="curve")

    for zone in layout.get("object_zones", []):
        rect = zone.get("source_rect", [])
        if len(rect) == 4:
            rx, ry, rw, rh = rect
            color = (196, 81, 67) if zone.get("id") == "MountainHutExterior" else (73, 124, 172)
            draw.rectangle(
                (
                    round(ox + rx * sx),
                    round(oy + ry * sy),
                    round(ox + (rx + rw) * sx),
                    round(oy + (ry + rh) * sy),
                ),
                outline=color,
                width=3,
            )

    notes = [
        "Canvas: 1800x1200 opaque source.",
        "West seam path source point `[0, 667]`.",
        "Path bends to hut door, no straight corridor.",
        "Every runtime layer later derives from this one source.",
        "Do not crop transparent layers after export.",
    ]
    ty = y + 116
    for note in notes:
        draw.text((x + 590, ty), f"- {note}", fill=(48, 44, 35), font=font(17))
        ty += 48


def write_reference_sheet(layout: dict[str, Any]) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (1800, 1400), (230, 219, 185, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((36, 28), "MountainHut v003 Repaint Handoff", fill=(42, 38, 32), font=font(32))
    draw.text(
        (36, 70),
        "v002 is rejected for visual quality. Use accepted Village and external handoff only as references; preserve the locked MountainHut canvas.",
        fill=(82, 71, 51),
        font=font(18),
    )
    paste_panel(
        sheet,
        draw,
        VILLAGE_SOURCE,
        (36, 120),
        (545, 500),
        "ACCEPTED STYLE TARGET",
        "Village source: painterly density, roads, grass, foliage.",
        (87, 115, 63),
    )
    paste_panel(
        sheet,
        draw,
        V002_SOURCE,
        (628, 120),
        (545, 500),
        "V002 REJECTED",
        "Good metrics, but still reads programmatic and flat.",
        (179, 76, 58),
    )
    paste_panel(
        sheet,
        draw,
        EXTERNAL_REFERENCE,
        (1219, 120),
        (545, 500),
        "QUALITY REFERENCE ONLY",
        "External handoff has richer art, but wrong dimension/layout.",
        (125, 88, 45),
    )
    paste_panel(
        sheet,
        draw,
        V002_SOURCE,
        (36, 700),
        (820, 620),
        "WHAT TO KEEP FROM V002",
        "Canvas lock, west seam entry, hut/door/woodpile zones.",
        (116, 82, 46),
    )
    draw_layout_panel(sheet, draw, layout)
    sheet.convert("RGB").save(V003_REFERENCE_SHEET)


def write_visual_review() -> None:
    review = {
        "review_id": "mountain_hut_v002_visual_review",
        "reviewed_at": "2026-05-25",
        "status": STATUS,
        "v002_source": rel(V002_SOURCE),
        "accepted_village_reference": rel(VILLAGE_SOURCE),
        "external_quality_reference": rel(EXTERNAL_REFERENCE),
        "v003_repaint_brief": rel(V003_BRIEF),
        "v003_reference_sheet": rel(V003_REFERENCE_SHEET),
        "v002_visual_accepted": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "rejection_reasons": [
            "v002 still reads as programmatic art: grass strokes, pebble marks, flower clusters, and roof strokes are visibly algorithmic at full-canvas review scale.",
            "v002 is less cohesive than the accepted Village source; the accepted Village image has richer foliage grouping, softer road shoulders, and more integrated painterly detail.",
            "The tree canopy clusters read as repeated flat stamps instead of natural layered foliage.",
            "The roof line and roof-tile strokes are noisy and less believable than the accepted Village building roofs.",
            "The external handoff MountainHut image has stronger painterly quality, but its dimension is 1572x1001 and its layout does not match the 1800x1200 MountainHut seam, door, and source-canvas locks.",
        ],
        "next_required_step": "produce_v003_full_canvas_repaint",
        "hard_approval_flags": {
            "human_visual_approval": False,
            "layer_export_approved": False,
            "runtime_replacement": False,
            "launch_quality_approved": False,
        },
    }
    write_json(VISUAL_REVIEW, review)


def write_v003_brief() -> None:
    V003_DIR.mkdir(parents=True, exist_ok=True)
    text = """# MountainHut v003 Full-Canvas Repaint Brief

Status: needs_v003_repaint_before_layer_export

## Goal

Create one high-quality `mountain_hut_painted_source_v003.png` as an opaque 1800x1200 full-canvas storybook source for the MountainHut region.

The target is registration-perfect layer alignment, not pixel-perfect brush tracing. Keep natural painted variation in grass, flowers, pebbles, leaves, road shoulders, and wall texture.

## Required References

- Use the accepted Village source as the quality target for foliage density, road softness, grass variation, and warm low-saturation storybook finish.
- Use the external handoff MountainHut image as a quality reference only. It has better painterly density, but its size and layout are wrong for this package.
- Use `mountain_hut_painted_source_v002.png` only for spatial lock: west seam entry, hut zone, door zone, woodpile zone, upper-right foreground bough, and north return path.

## Locked Spatial Contract

- Canvas must be exactly 1800x1200.
- The west seam path must enter at source point `[0, 667]` with roughly 76 px readable road width.
- The road should bend gently from the west edge toward the hut door and then continue softly toward the north return path.
- Hut mass stays in the right half of the scene, above the approach path, without blocking the west seam road.
- Door remains readable and approachable.
- Woodpile, herb shelf, porch shadow, and small repair hints are allowed.
- no combat, weapons, danger signs, monsters, gore, or high-pressure warning marks.

## Layer Future-Proofing

- Produce a single full-canvas painted source first.
- All future runtime layers must derive from that same source.
- Do not crop transparent runtime layers after export.
- Do not independently regenerate separate layer compositions.
- Preserve one shared origin, perspective, scale, rotation, and canvas.

## Visual Quality Bar

- Match the accepted Village source in integrated foliage, soft roads, small flower clusters, believable roof texture, and hand-painted grass.
- Avoid flat stamped tree blobs, procedural grass noise, outline-only roof arcs, isolated white flower dots, and uniform empty green fields.
- Keep the hut cozy, quiet, and repairable, not abandoned-horror or combat-adventure.
"""
    V003_BRIEF.write_text(text, encoding="utf-8")


def update_workflow() -> None:
    data = read_json(WORKFLOW)
    data["status"] = PHASE
    data["current_phase"] = "02_source_generation_v003_handoff"
    data["next_art_step"] = "produce a v003 full-canvas repaint before layer export or runtime replacement."
    phase_status = data.setdefault("phase_status", {})
    phase_status["02_source_visual_review_v002"] = STATUS
    phase_status["02_source_generation_v003"] = "handoff_ready_for_external_or_manual_repaint"
    data["v002_visual_review"] = {
        "status": STATUS,
        "review": rel(VISUAL_REVIEW),
        "report": rel(V002_REPORT),
        "v002_visual_accepted": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
    }
    data["v003_repaint_handoff"] = {
        "status": "handoff_ready_for_external_or_manual_repaint",
        "brief": rel(V003_BRIEF),
        "reference_sheet": rel(V003_REFERENCE_SHEET),
        "expected_source": "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/v003/mountain_hut_painted_source_v003.png",
    }
    write_json(WORKFLOW, data)


def update_layer_contract() -> None:
    data = read_json(LAYER_CONTRACT)
    source = data.setdefault("source_image", {})
    source["current_file_status"] = "v002_visual_review_rejected"
    source["required_next_step"] = "Produce a v003 full-canvas repaint before layer export."
    source["v002_visual_review"] = rel(VISUAL_REVIEW)
    source["v003_repaint_brief"] = rel(V003_BRIEF)
    source["v003_reference_sheet"] = rel(V003_REFERENCE_SHEET)
    data["layer_export_status"] = "blocked_until_v003_source_acceptance"
    data["runtime_replacement"] = False
    write_json(LAYER_CONTRACT, data)


def update_v002_acceptance() -> None:
    data = read_json(V002_ACCEPTANCE)
    data["status"] = PHASE
    data["human_visual_approval"] = False
    data["layer_export_approved"] = False
    data["runtime_replacement"] = False
    data["launch_quality_approved"] = False
    data["codex_visual_review"] = {
        "status": STATUS,
        "review": rel(VISUAL_REVIEW),
        "not_human_visual_approval": True,
        "v002_visual_accepted": False,
        "next_required_step": "produce_v003_full_canvas_repaint",
    }
    write_json(V002_ACCEPTANCE, data)


def update_project_manifest() -> None:
    data = read_json(PROJECT_MANIFEST)
    for region in data.get("current_runtime_regions", []):
        if not isinstance(region, dict) or region.get("region_id") != "Region_MountainHut":
            continue
        region["phase"] = PHASE
        region["runtime_replacement"] = False
        region["launch_quality_approved"] = False
        region["human_visual_approval_required"] = True
        region["next_art_step"] = "Produce a v003 full-canvas repaint before MountainHut layer export or runtime replacement."
        region["active_v002_visual_review"] = rel(VISUAL_REVIEW)
        region["active_v003_repaint_brief"] = rel(V003_BRIEF)
        region["active_v003_reference_sheet"] = rel(V003_REFERENCE_SHEET)
        break
    write_json(PROJECT_MANIFEST, data)


def write_report() -> None:
    V002_REPORT.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# MountainHut v002 Visual Review - 2026-05-25

Status: {STATUS}

## Verdict

v002 rejected for visual promotion. runtime replacement remains blocked, layer export remains blocked, and launch-quality approval remains false.

## Why v002 is rejected

- It passes the automated source-quality precheck, but it still reads as programmatic at full review scale.
- It is visibly below the accepted Village source in foliage integration, road softness, roof believability, and natural grass/flower detail.
- The external handoff MountainHut image proves the desired painterly density is possible, but that file has the wrong dimension and layout for this 1800x1200 seam-locked package.

## Produced next handoff

- Visual review JSON: `{rel(VISUAL_REVIEW)}`
- v003 repaint brief: `{rel(V003_BRIEF)}`
- v003 reference sheet: `{rel(V003_REFERENCE_SHEET)}`

## Boundary

No runtime replacement, source acceptance, layer export, or launch approval happened in this review. The next valid production step is v003 full-canvas repaint, then visual review before any layer derivation.
"""
    V002_REPORT.write_text(text, encoding="utf-8")


def main() -> None:
    layout = read_json(LAYOUT_LOCK)
    write_visual_review()
    write_v003_brief()
    write_reference_sheet(layout)
    write_report()
    update_workflow()
    update_layer_contract()
    update_v002_acceptance()
    update_project_manifest()
    print("OK: MountainHut v002 visual review recorded and v003 repaint handoff generated")


if __name__ == "__main__":
    main()
