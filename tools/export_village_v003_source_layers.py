from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/village_world2d/v001"
V003_DIR = PACKAGE_DIR / "02_source_generation/v003_edge_continuity_repaint"
SOURCE = V003_DIR / "village_painted_source_v003.png"
SOURCE_ACCEPTANCE = V003_DIR / "source_acceptance_v003.json"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
V003_LAYER_DIR = PACKAGE_DIR / "03_layer_export/v003_edge_continuity"
LAYER_DIR = V003_LAYER_DIR / "layers"
LAYER_MANIFEST = V003_LAYER_DIR / "layer_export_manifest_v003.json"
RECOMPOSITE_PREVIEW = V003_LAYER_DIR / "village_v003_layer_recomposite_preview.png"
REVIEW_PREVIEW = PACKAGE_DIR / "05_review_and_qa/village_v003_layer_export_review_preview.png"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
REPORT = ROOT / ".codex/reports/village_v003_layer_export_review_2026-05-26.md"

CANVAS = (1800, 1200)
STATUS = "v003_semantic_layers_exported_pending_review"


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
    draw.ellipse((1235, 665, 1770, 1115), fill=255)
    draw.polygon([(1350, 850), (1800, 805), (1800, 1200), (1280, 1200), (1185, 1015)], fill=255)
    draw.ellipse((1055, 1000, 1325, 1210), fill=255)

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
    return sum(image.getchannel("A").histogram()[1:])


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
        image.save(LAYER_DIR / f"village_v003_{layer_id}.png")
    return layers


def write_review_previews(source: Image.Image, layers: dict[str, Image.Image], recomposite: Image.Image) -> None:
    V003_LAYER_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    recomposite.convert("RGB").save(RECOMPOSITE_PREVIEW)
    sheet = Image.new("RGB", (1170, 870), (226, 224, 218))
    labels = [
        ("v003 source", source),
        ("base_ground", layers["base_ground"]),
        ("terrain_details alpha", layers["terrain_details"]),
        ("behind_player_structures alpha", layers["behind_player_structures"]),
        ("ysort_props_structures alpha", layers["ysort_props_structures"]),
        ("foreground_occlusion alpha", layers["foreground_occlusion"]),
        ("recomposite", recomposite),
    ]
    for index, (label, image) in enumerate(labels):
        thumb = image.convert("RGBA")
        if image.getchannel("A").getextrema()[0] == 0:
            checker = Image.new("RGBA", image.size, (232, 232, 232, 255))
            draw = ImageDraw.Draw(checker)
            for y in range(0, image.height, 40):
                for x in range(0, image.width, 40):
                    if (x // 40 + y // 40) % 2:
                        draw.rectangle((x, y, x + 39, y + 39), fill=(198, 198, 198, 255))
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
        layer_path = LAYER_DIR / f"village_v003_{layer_id}.png"
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
    write_json(
        LAYER_MANIFEST,
        {
            "package_id": "village_world2d_v003_edge_continuity_layer_export",
            "status": STATUS,
            "source_image": rel(SOURCE),
            "source_sha256": sha256(SOURCE),
            "accepted_candidate_id": "village_painted_source_v003",
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
            "review_result": "v003_edge_continuity_semantic_layers_pending_review",
        },
    )


def update_records() -> None:
    acceptance = read_json(SOURCE_ACCEPTANCE)
    acceptance["semantic_layer_export"] = {
        "status": STATUS,
        "manifest": rel(LAYER_MANIFEST),
        "review_preview": rel(REVIEW_PREVIEW),
        "not_final_layer_approval": True,
        "runtime_replacement": False,
        "next_required_step": "review v003 semantic layers before Godot screenshot validation",
    }
    write_json(SOURCE_ACCEPTANCE, acceptance)

    workflow = read_json(WORKFLOW)
    workflow["status"] = STATUS
    workflow["current_phase"] = "03_layer_export_v003_semantic_review"
    workflow["runtime_replacement"] = False
    workflow["v003_layer_export"] = {
        "manifest": rel(LAYER_MANIFEST),
        "layer_count": 5,
        "status": STATUS,
        "runtime_replacement": False,
        "human_layer_review": False,
    }
    phase = workflow.setdefault("phase_status", {})
    phase["03_layer_export_v003"] = STATUS
    phase["04_godot_integration_v003"] = "blocked_until_v003_semantic_layer_review_and_godot_screenshot"
    workflow.setdefault("validation", {})["v003_layer_export_validator"] = "tools/validate_village_v003_layer_export.py"
    write_json(WORKFLOW, workflow)

    contract = read_json(LAYER_CONTRACT)
    source = contract.setdefault("source_image", {})
    source["v003_layer_export_status"] = STATUS
    source["v003_layer_manifest"] = rel(LAYER_MANIFEST)
    contract["active_v003_layer_manifest"] = rel(LAYER_MANIFEST)
    contract["v003_layer_export_status"] = STATUS
    contract["runtime_replacement"] = False
    write_json(LAYER_CONTRACT, contract)

    project = read_json(PROJECT_MANIFEST)
    for region in project.get("current_runtime_regions", []):
        if region.get("region_id") != "Region_Village":
            continue
        region["phase"] = STATUS
        region["active_v003_layer_manifest"] = rel(LAYER_MANIFEST)
        region["runtime_replacement"] = False
        region["launch_quality_approved"] = False
        region["human_visual_approval_required"] = True
        region["next_art_step"] = "Review Village v003 semantic layers, then run Godot screenshot validation before runtime replacement."
        break
    write_json(PROJECT_MANIFEST, project)


def write_report(diff: float, layers: dict[str, Image.Image]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    foreground_pixels = nontransparent_pixels(layers["foreground_occlusion"])
    REPORT.write_text(
        f"""# Village v003 Semantic Layer Export - 2026-05-26

Status: {STATUS}

## Source

- Source image: `{rel(SOURCE)}`
- Layer manifest: `{rel(LAYER_MANIFEST)}`

## Export

- Base layer preserves the full-canvas v003 source.
- Terrain, behind-player, and Y-sort layers are empty full-canvas placeholders.
- Foreground occlusion visible pixels: `{foreground_pixels}`.
- Recomposite mean RGB diff: `{diff:.4f}`.

## Boundary

This is not runtime replacement and not launch-quality approval. Full-canvas Godot screenshot review remains required.
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
    update_records()
    write_report(diff, layers)
    print(f"OK: exported Village v003 semantic layers diff={diff:.4f}")
    print(f"OK: wrote {rel(LAYER_MANIFEST)}")


if __name__ == "__main__":
    main()
