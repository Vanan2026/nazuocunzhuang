from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
HANDOFF_DIR = PACKAGE_DIR / "02_source_generation" / "v002_inherited_world_base_repaint"
HANDOFF_JSON = HANDOFF_DIR / "village_inherited_repaint_handoff_v002.json"
HANDOFF_BRIEF = HANDOFF_DIR / "village_inherited_repaint_brief_v002.md"
REFERENCE_SHEET = HANDOFF_DIR / "village_inherited_repaint_reference_sheet_v002.png"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
PROJECT_MANIFEST = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"
WORLD_BASE_MANIFEST = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001" / "02_world_base_no_foreground" / "world_base_manifest.json"
WORLD_BASE_CROP = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001" / "02_world_base_no_foreground" / "region_base_crops" / "village_base_no_foreground.png"
OLD_ACCEPTED_SOURCE = PACKAGE_DIR / "02_source_generation" / "village_painted_source.png"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock" / "layout_lock.json"
OUTDOOR_WORKFLOW = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001" / "workflow_manifest.json"

HANDOFF_ID = "village_inherited_world_base_repaint_v002"
STATUS = "handoff_ready_for_artist_repaint_not_source_accepted"
CANVAS = [1800, 1200]
SHEET_SIZE = (2400, 1500)


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
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.convert("RGB")
    output = Image.new("RGB", size, (236, 228, 203))
    source_ratio = image.width / image.height
    target_ratio = size[0] / size[1]
    if source_ratio > target_ratio:
        width = size[0]
        height = int(round(width / source_ratio))
    else:
        height = size[1]
        width = int(round(height * source_ratio))
    resized = image.resize((width, height), Image.Resampling.LANCZOS)
    output.paste(resized, ((size[0] - width) // 2, (size[1] - height) // 2))
    return output


def make_card(
    sheet: Image.Image,
    title: str,
    image: Image.Image,
    xy: tuple[int, int],
    size: tuple[int, int],
    note: str,
) -> None:
    draw = ImageDraw.Draw(sheet)
    x, y = xy
    w, h = size
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=(249, 244, 226), outline=(118, 96, 65), width=3)
    draw.text((x + 22, y + 18), title, fill=(55, 43, 29), font=font(28))
    preview = fit(image, (w - 44, h - 120))
    sheet.paste(preview, (x + 22, y + 62))
    draw.text((x + 22, y + h - 48), note, fill=(79, 65, 45), font=font(20))


def build_difference_panel(base: Image.Image, reference: Image.Image) -> Image.Image:
    base_small = fit(base, (520, 346))
    ref_small = fit(reference, (520, 346))
    blend = Image.blend(base_small, ref_small, 0.45)
    draw = ImageDraw.Draw(blend)
    draw.rectangle((0, 0, blend.width - 1, blend.height - 1), outline=(70, 54, 35), width=2)
    draw.text((18, 16), "composition inheritance + quality target", fill=(53, 42, 30), font=font(22))
    return blend


def build_reference_sheet() -> None:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    base_crop = Image.open(WORLD_BASE_CROP).convert("RGB")
    old_source = Image.open(OLD_ACCEPTED_SOURCE).convert("RGB")
    sheet = Image.new("RGB", SHEET_SIZE, (226, 217, 190))
    draw = ImageDraw.Draw(sheet)
    draw.text((42, 32), "Village v002 inherited-crop repaint handoff", fill=(48, 37, 25), font=font(40))
    draw.text(
        (42, 86),
        "Use the inherited world-base crop for composition; use the old Village source as quality reference only.",
        fill=(78, 61, 39),
        font=font(24),
    )
    make_card(
        sheet,
        "Required composition source",
        base_crop,
        (42, 140),
        (720, 560),
        "Must preserve roads, hue, lighting, and edge continuity.",
    )
    make_card(
        sheet,
        "Quality reference only",
        old_source,
        (840, 140),
        (720, 560),
        "Do not promote or split this isolated old source.",
    )
    blend = build_difference_panel(base_crop, old_source)
    make_card(
        sheet,
        "Repaint target relationship",
        blend,
        (1638, 140),
        (720, 560),
        "Paint detail onto inherited structure, not a new layout.",
    )
    notes = [
        "Acceptance target: one opaque village_painted_source_v002 at 1800x1200.",
        "Future runtime layers must be full-canvas derivatives of that accepted source.",
        "foreground_occlusion is authored only after the inherited base repaint is accepted.",
        "No combat, no hazards, no pressure systems; keep the village calm and social.",
    ]
    y = 790
    draw.rounded_rectangle((42, 760, 2358, 1438), radius=18, fill=(248, 241, 218), outline=(118, 96, 65), width=3)
    draw.text((78, 798), "Production Rules", fill=(48, 37, 25), font=font(32))
    for note in notes:
        draw.text((92, y + 62), f"- {note}", fill=(68, 54, 36), font=font(24))
        y += 78
    draw.text(
        (92, 1246),
        "Registration: shared origin, full canvas, same perspective, no object-bound cropped layers.",
        fill=(68, 54, 36),
        font=font(24),
    )
    draw.text(
        (92, 1328),
        "Review boundary: handoff ready, not source accepted, not layer export, not runtime replacement.",
        fill=(99, 46, 35),
        font=font(24),
    )
    sheet.save(REFERENCE_SHEET)


def write_brief() -> None:
    HANDOFF_BRIEF.write_text(
        """# Village v002 Inherited World-Base Repaint Brief

## Goal

Create a high-quality `village_painted_source_v002` from the inherited world-base crop. This is an inherited world-base crop repaint, not a new isolated composition.

## Required Inputs

- Composition source: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/region_base_crops/village_base_no_foreground.png`
- Quality reference only: `production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png`
- Layout lock: `production/assets/regions/village_world2d/v001/01_layout_lock/layout_lock.json`
- Outdoor parent: `production/assets/outdoor_world_world2d/v001/workflow_manifest.json`

## Output Contract

- Output one opaque `village_painted_source_v002` at full-canvas `1800x1200`.
- Preserve the inherited crop's road continuation, terrain hue, lighting direction, perspective, and edge relationships.
- Use registration-perfect layer alignment rules: shared canvas, shared origin, shared pivot, shared scale, shared rotation, and shared perspective.
- Keep later runtime layers full-canvas. Do not crop transparent layers to object bounds.
- Produce `foreground_occlusion` only after the inherited repaint base is accepted.

## Visual Direction

- Warm low-saturation storybook 2D village art.
- Fixed 3/4 top-down rural view.
- Social hub: notice board, seed stall, old maple, bench/rest pocket, and readable footpaths.
- Keep the old Village source as quality reference only: detail density, material softness, foliage integration, and cozy tone.
- Do not copy it as runtime replacement and do not split layers from it.

## Must Avoid

- no combat, monsters, damage, weapons, loot, or threat language.
- No hard-edged pasted roads, isolated sticker-like props, or unrelated recomposed layout.
- Not runtime replacement, not final art approval, not layer export approval, and not launch-quality approval.
""",
        encoding="utf-8",
    )


def write_handoff_json() -> None:
    write_json(
        HANDOFF_JSON,
        {
            "handoff_id": HANDOFF_ID,
            "status": STATUS,
            "region_id": "village",
            "created_at": "2026-05-26",
            "runtime_replacement": False,
            "launch_quality_approved": False,
            "human_visual_approval": False,
            "layer_export_approved": False,
            "references": {
                "world_base_manifest": rel(WORLD_BASE_MANIFEST),
                "inherited_world_base_crop": rel(WORLD_BASE_CROP),
                "old_village_quality_reference_only": rel(OLD_ACCEPTED_SOURCE),
                "village_layout_lock": rel(LAYOUT_LOCK),
                "outdoor_world_workflow": rel(OUTDOOR_WORKFLOW),
                "brief": rel(HANDOFF_BRIEF),
                "reference_sheet": rel(REFERENCE_SHEET),
            },
            "output_contract": {
                "target_source_id": "village_painted_source_v002",
                "canvas": CANVAS,
                "must_inherit_composition_from_world_base_crop": True,
                "old_source_is_quality_reference_only": True,
                "full_canvas_layers_required_after_acceptance": True,
                "foreground_occlusion_after_base_acceptance_only": True,
                "registration_target": "registration-perfect layer alignment, not pixel-perfect brush tracing",
            },
            "forbidden_actions": [
                "Do not use the old isolated Village source as runtime replacement.",
                "Do not split foreground layers before the inherited base repaint is accepted.",
                "Do not crop transparent runtime layers to object bounds.",
            ],
        },
    )


def update_workflow() -> None:
    workflow = read_json(WORKFLOW)
    workflow["inherited_world_base_repaint_handoff"] = {
        "handoff_id": HANDOFF_ID,
        "status": STATUS,
        "manifest": rel(HANDOFF_JSON),
        "brief": rel(HANDOFF_BRIEF),
        "reference_sheet": rel(REFERENCE_SHEET),
        "inherits_from_world_base_crop": rel(WORLD_BASE_CROP),
        "old_source_policy": "quality_reference_only",
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "human_visual_approval": False,
        "layer_export_approved": False,
    }
    workflow.setdefault("validation", {})["inherited_crop_repaint_handoff_validator"] = (
        "tools/validate_village_inherited_crop_repaint_handoff.py"
    )
    write_json(WORKFLOW, workflow)


def update_project_manifest() -> None:
    project = read_json(PROJECT_MANIFEST)
    for record in project.get("current_runtime_regions", []):
        if record.get("region_id") == "Region_Village":
            record["active_inherited_repaint_handoff"] = rel(HANDOFF_JSON)
            record["next_art_step"] = (
                "Use the inherited world-base crop repaint handoff to produce village_painted_source_v002 before any runtime replacement."
            )
            break
    write_json(PROJECT_MANIFEST, project)


def main() -> None:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    write_brief()
    build_reference_sheet()
    write_handoff_json()
    update_workflow()
    update_project_manifest()
    print(f"OK: wrote {rel(HANDOFF_JSON)}")


if __name__ == "__main__":
    main()
