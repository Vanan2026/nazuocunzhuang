from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/village_world2d/v001"
V002_DIR = PACKAGE_DIR / "02_source_generation/v002_inherited_world_base_repaint"
SOURCE = V002_DIR / "village_painted_source_v002.png"
SOURCE_ACCEPTANCE = V002_DIR / "source_acceptance_v002.json"
VISUAL_REVIEW = V002_DIR / "source_visual_review_v002.json"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
V002_LAYER_DIR = PACKAGE_DIR / "03_layer_export/v002_inherited"
LAYER_DIR = V002_LAYER_DIR / "layers"
LAYER_MANIFEST = V002_LAYER_DIR / "layer_export_manifest_v002.json"
RECOMPOSITE_PREVIEW = V002_LAYER_DIR / "village_v002_layer_recomposite_preview.png"
REVIEW_PREVIEW = PACKAGE_DIR / "05_review_and_qa/village_v002_layer_export_review_preview.png"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
REPORT = ROOT / ".codex/reports/village_v002_layer_export_review_2026-05-26.md"

CANVAS = (1800, 1200)
STATUS = "v002_semantic_layers_exported_pending_review"
WORKFLOW_PHASE = "03_layer_export_v002_semantic_review"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def open_source() -> Image.Image:
    image = Image.open(SOURCE).convert("RGBA")
    if image.size != CANVAS:
        raise SystemExit(f"FAIL: {rel(SOURCE)} must be {CANVAS}, got {image.size}")
    if image.getchannel("A").getextrema() != (255, 255):
        base = Image.new("RGBA", CANVAS, (0, 0, 0, 255))
        base.alpha_composite(image)
        image = base
    return image


def layer_from_mask(source: Image.Image, mask: Image.Image) -> Image.Image:
    layer = source.copy()
    layer.putalpha(mask)
    return layer


def build_foreground_mask(source: Image.Image) -> Image.Image:
    region_mask = Image.new("L", CANVAS, 0)
    draw = ImageDraw.Draw(region_mask)

    # Review-only player occlusion: the near-camera old maple and its lower
    # foreground shrubs. Distant houses, paths, and stalls stay baked into base.
    draw.ellipse((1175, 610, 1795, 1118), fill=255)
    draw.polygon([(1295, 820), (1800, 760), (1800, 1200), (1220, 1200), (1130, 990)], fill=255)
    draw.ellipse((1010, 965, 1355, 1210), fill=255)

    mask = Image.new("L", CANVAS, 0)
    source_rgb = source.convert("RGB")
    source_px = source_rgb.load()
    region_px = region_mask.load()
    mask_px = mask.load()
    for y in range(CANVAS[1]):
        for x in range(CANVAS[0]):
            if region_px[x, y] == 0:
                continue
            r, g, b = source_px[x, y]
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            is_leaf = g >= r * 0.78 and g >= b * 0.88 and luminance < 145
            is_dark_wood_or_shadow = luminance < 95 and r > b * 0.72
            is_foreground_flower = g >= 82 and r > 132 and b > 95 and luminance < 170
            if is_leaf or is_dark_wood_or_shadow or is_foreground_flower:
                mask_px[x, y] = 255
    return mask


def nontransparent_pixels(image: Image.Image) -> int:
    histogram = image.getchannel("A").histogram()
    return sum(histogram[1:])


def mean_rgb_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def write_layers(source: Image.Image) -> dict[str, Image.Image]:
    LAYER_DIR.mkdir(parents=True, exist_ok=True)
    empty = Image.new("L", CANVAS, 0)
    masks = {
        "terrain_details": empty,
        "behind_player_structures": empty,
        "ysort_props_structures": empty,
        "foreground_occlusion": build_foreground_mask(source),
    }
    layers = {
        "base_ground": source.copy(),
        "terrain_details": layer_from_mask(source, masks["terrain_details"]),
        "behind_player_structures": layer_from_mask(source, masks["behind_player_structures"]),
        "ysort_props_structures": layer_from_mask(source, masks["ysort_props_structures"]),
        "foreground_occlusion": layer_from_mask(source, masks["foreground_occlusion"]),
    }
    for layer_id, image in layers.items():
        image.save(LAYER_DIR / f"village_v002_{layer_id}.png")
    return layers


def paste_panel(sheet: Image.Image, image: Image.Image, label: str, index: int) -> None:
    thumb = image.convert("RGBA")
    if image.mode == "RGBA" and image.getchannel("A").getextrema()[0] == 0:
        checker = Image.new("RGBA", image.size, (232, 232, 232, 255))
        draw = ImageDraw.Draw(checker)
        step = 40
        for y in range(0, image.height, step):
            for x in range(0, image.width, step):
                if (x // step + y // step) % 2:
                    draw.rectangle((x, y, x + step - 1, y + step - 1), fill=(198, 198, 198, 255))
        thumb = Image.alpha_composite(checker, thumb)
    thumb = thumb.convert("RGB")
    thumb.thumbnail((360, 240), Image.Resampling.LANCZOS)
    x = (index % 3) * 390
    y = (index // 3) * 290
    tile = Image.new("RGB", (390, 290), (246, 244, 238))
    tile.paste(thumb, ((390 - thumb.width) // 2, 14))
    draw = ImageDraw.Draw(tile)
    draw.text((12, 260), label, fill=(45, 38, 30), font=ImageFont.load_default())
    sheet.paste(tile, (x, y))


def write_review_previews(source: Image.Image, layers: dict[str, Image.Image], recomposite: Image.Image) -> None:
    V002_LAYER_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    recomposite.convert("RGB").save(RECOMPOSITE_PREVIEW)
    sheet = Image.new("RGB", (1170, 870), (226, 224, 218))
    panels = [
        ("v002 source", source),
        ("base_ground", layers["base_ground"]),
        ("terrain_details alpha", layers["terrain_details"]),
        ("behind_player_structures alpha", layers["behind_player_structures"]),
        ("ysort_props_structures alpha", layers["ysort_props_structures"]),
        ("foreground_occlusion alpha", layers["foreground_occlusion"]),
        ("recomposite", recomposite),
    ]
    for index, (label, image) in enumerate(panels):
        paste_panel(sheet, image, label, index)
    sheet.save(REVIEW_PREVIEW)


def write_manifest(layers: dict[str, Image.Image], recomposite_diff: float) -> None:
    contract = read_json(LAYER_CONTRACT)
    contract_by_id = {layer["id"]: layer for layer in contract["layers"]}
    roles = {
        "base_ground": "baked_static_scene",
        "terrain_details": "baked_into_base_empty_runtime_layer",
        "behind_player_structures": "baked_into_base_empty_runtime_layer",
        "ysort_props_structures": "baked_into_base_empty_runtime_layer",
        "foreground_occlusion": "player_foreground_occlusion",
    }
    records = []
    for layer_id, image in layers.items():
        layer_path = LAYER_DIR / f"village_v002_{layer_id}.png"
        alpha = image.getchannel("A")
        contract_layer = contract_by_id[layer_id]
        records.append(
            {
                "id": layer_id,
                "path": rel(layer_path),
                "runtime_path": contract_layer["runtime_path"],
                "derived_from": rel(SOURCE),
                "canvas": [CANVAS[0], CANVAS[1]],
                "alpha": contract_layer["alpha"],
                "z_index": contract_layer["z_index"],
                "semantic_role": roles[layer_id],
                "nontransparent_pixels": nontransparent_pixels(image),
                "alpha_range": list(alpha.getextrema()),
                "sha256": sha256(layer_path),
            }
        )

    payload = {
        "package_id": "village_world2d_v002_inherited_layer_export",
        "status": STATUS,
        "source_image": rel(SOURCE),
        "source_sha256": sha256(SOURCE),
        "accepted_candidate_id": "village_painted_source_v002",
        "canvas": {"width": CANVAS[0], "height": CANVAS[1], "origin": "top_left"},
        "layer_count": len(records),
        "layers": records,
        "recomposite_preview": rel(RECOMPOSITE_PREVIEW),
        "review_preview": rel(REVIEW_PREVIEW),
        "recomposite_mean_rgb_diff": round(recomposite_diff, 4),
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "human_visual_approval": False,
        "human_layer_review": False,
        "semantic_layer_rework": True,
        "review_result": "semantic_rework_pending_review",
        "notes": [
            "v002 is accepted only for Codex semantic layer export review, not final art approval.",
            "Static scenery stays baked into the opaque base layer.",
            "Transparent layers keep the full 1800x1200 canvas and shared origin.",
            "Terrain, set-back structures, and Y-sort props are empty runtime placeholders in this pass.",
            "Only the near-camera old maple/lower foreground occlusion is exported as a visible runtime layer.",
            "Godot runtime replacement is intentionally blocked until semantic layer review and screenshot validation.",
        ],
    }
    write_json(LAYER_MANIFEST, payload)


def update_source_records() -> None:
    acceptance = read_json(SOURCE_ACCEPTANCE)
    acceptance["human_visual_approval"] = False
    acceptance["layer_export_approved"] = False
    acceptance["runtime_replacement"] = False
    acceptance["launch_quality_approved"] = False
    acceptance["semantic_layer_export"] = {
        "status": STATUS,
        "manifest": rel(LAYER_MANIFEST),
        "review_preview": rel(REVIEW_PREVIEW),
        "not_final_layer_approval": True,
        "runtime_replacement": False,
        "next_required_step": "review v002 semantic layers before Godot screenshot validation",
    }
    write_json(SOURCE_ACCEPTANCE, acceptance)


def update_contract_workflow_project() -> None:
    contract = read_json(LAYER_CONTRACT)
    source = contract.setdefault("source_image", {})
    source["v002_current_file_status"] = STATUS
    source["v002_visual_review"] = rel(VISUAL_REVIEW)
    source["v002_required_next_step"] = "Review v002 semantic layer export, then run Godot screenshot validation before runtime replacement."
    source["v002_human_visual_approval"] = False
    source["v002_layer_export_approved"] = False
    source["v002_layer_manifest"] = rel(LAYER_MANIFEST)
    contract["active_v002_layer_manifest"] = rel(LAYER_MANIFEST)
    contract["v002_layer_export_status"] = STATUS
    contract["runtime_replacement"] = False
    write_json(LAYER_CONTRACT, contract)

    workflow = read_json(WORKFLOW)
    workflow["status"] = STATUS
    workflow["current_phase"] = WORKFLOW_PHASE
    workflow["runtime_replacement"] = False
    workflow["next_art_step"] = "review v002 semantic layers before any runtime replacement."
    workflow["v002_layer_export"] = {
        "manifest": rel(LAYER_MANIFEST),
        "layer_count": 5,
        "status": STATUS,
        "runtime_replacement": False,
        "human_layer_review": False,
        "review_result": "semantic_rework_pending_review",
    }
    phase = workflow.setdefault("phase_status", {})
    phase["03_layer_export_v002"] = STATUS
    phase["04_godot_integration_v002"] = "blocked_until_v002_semantic_layer_review_and_godot_screenshot"
    workflow.setdefault("validation", {})["v002_layer_export_validator"] = "tools/validate_village_v002_layer_export.py"
    write_json(WORKFLOW, workflow)

    project = read_json(PROJECT_MANIFEST)
    for region in project.get("current_runtime_regions", []):
        if not isinstance(region, dict) or region.get("region_id") != "Region_Village":
            continue
        region["phase"] = STATUS
        region["active_v002_visual_review"] = rel(VISUAL_REVIEW)
        region["active_v002_layer_manifest"] = rel(LAYER_MANIFEST)
        region["runtime_replacement"] = False
        region["launch_quality_approved"] = False
        region["human_visual_approval_required"] = True
        region["next_art_step"] = "Review Village v002 semantic layers, then run Village and OutdoorWorld Godot screenshot validation before runtime replacement."
        break
    write_json(PROJECT_MANIFEST, project)


def write_report(diff: float, layers: dict[str, Image.Image]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    foreground_pixels = nontransparent_pixels(layers["foreground_occlusion"])
    REPORT.write_text(
        f"""# Village v002 Semantic Layer Export - 2026-05-26

Status: {STATUS}

## Source

- Source image: `{rel(SOURCE)}`
- Visual review: `{rel(VISUAL_REVIEW)}`
- Layer manifest: `{rel(LAYER_MANIFEST)}`

## Export

- Base layer preserves the full v002 source.
- Terrain, behind-player, and Y-sort layers are empty full-canvas placeholders.
- Foreground occlusion visible pixels: `{foreground_pixels}`.
- Recomposite mean RGB diff: `{diff:.4f}`.

## Boundary

This is not human/art approval and not runtime replacement. runtime replacement remains blocked until semantic layer review and Godot screenshot validation.
""",
        encoding="utf-8",
    )


def main() -> None:
    source = open_source()
    layers = write_layers(source)
    recomposite = layers["base_ground"].copy()
    for layer_id in ["terrain_details", "behind_player_structures", "ysort_props_structures", "foreground_occlusion"]:
        recomposite.alpha_composite(layers[layer_id])
    diff = mean_rgb_diff(source, recomposite)
    write_review_previews(source, layers, recomposite)
    write_manifest(layers, diff)
    update_source_records()
    update_contract_workflow_project()
    write_report(diff, layers)
    print(f"OK: exported Village v002 semantic layers diff={diff:.4f}")
    print(f"OK: wrote {rel(LAYER_MANIFEST)}")


if __name__ == "__main__":
    main()
