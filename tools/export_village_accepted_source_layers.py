from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
EXPORT_DIR = PACKAGE_DIR / "03_layer_export"
LAYER_DIR = EXPORT_DIR / "layers"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
DRAFT_DIR = SOURCE_DIR / "layout_structure_drafts"

CANONICAL_SOURCE = SOURCE_DIR / "village_painted_source.png"
SOURCE_ACCEPTANCE = SOURCE_DIR / "source_acceptance.json"
CANDIDATE_ID = "village_true_painted_source_candidate_v001"
CANDIDATE = SOURCE_DIR / "true_source_candidates" / f"{CANDIDATE_ID}.png"
CANDIDATE_META = SOURCE_DIR / "true_source_candidates" / f"{CANDIDATE_ID}.json"
LAYOUT_DRAFT = DRAFT_DIR / "village_layout_structure_draft_v001.png"
LAYOUT_DRAFT_ACCEPTANCE = DRAFT_DIR / "village_layout_structure_draft_v001_acceptance.json"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = EXPORT_DIR / "layer_contract.json"
LAYER_MANIFEST = EXPORT_DIR / "layer_export_manifest.json"
RECOMPOSITE_PREVIEW = EXPORT_DIR / "village_layer_recomposite_preview.png"
REVIEW_PREVIEW = REVIEW_DIR / "village_layer_export_review_preview_v001.png"

CANVAS = (1800, 1200)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def open_source(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    if image.size != CANVAS:
        raise SystemExit(f"FAIL: {rel(path)} must be {CANVAS}, got {image.size}")
    if image.getchannel("A").getextrema() != (255, 255):
        base = Image.new("RGBA", image.size, (0, 0, 0, 255))
        base.alpha_composite(image)
        image = base
    return image


def preserve_layout_draft() -> None:
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    if not LAYOUT_DRAFT.exists():
        if not CANONICAL_SOURCE.exists():
            raise SystemExit("FAIL: cannot preserve missing layout draft source")
        if ImageChops.difference(open_source(CANONICAL_SOURCE), open_source(CANDIDATE)).getbbox() is None:
            acceptance = read_json(SOURCE_ACCEPTANCE) if SOURCE_ACCEPTANCE.exists() else {}
            if acceptance.get("candidate_type") != "layout_structure_draft":
                raise SystemExit("FAIL: canonical source already matches candidate and no preserved layout draft exists")
            generator_path = ROOT / "tools" / "generate_village_painted_source_candidate.py"
            spec = importlib.util.spec_from_file_location("village_layout_draft_generator", generator_path)
            if spec is None or spec.loader is None:
                raise SystemExit("FAIL: unable to load Village layout draft generator")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.draw_source(module.load_layout()).save(LAYOUT_DRAFT)
        else:
            shutil.copy2(CANONICAL_SOURCE, LAYOUT_DRAFT)
    if SOURCE_ACCEPTANCE.exists() and not LAYOUT_DRAFT_ACCEPTANCE.exists():
        shutil.copy2(SOURCE_ACCEPTANCE, LAYOUT_DRAFT_ACCEPTANCE)
    if LAYOUT_DRAFT_ACCEPTANCE.exists():
        draft_acceptance = read_json(LAYOUT_DRAFT_ACCEPTANCE)
        draft_acceptance["source_image"] = rel(LAYOUT_DRAFT)
        draft_acceptance["preserved_from"] = "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
        draft_acceptance["do_not_split_layers_from_this_image"] = True
        draft_acceptance["not_final_painted_source"] = True
        write_json(LAYOUT_DRAFT_ACCEPTANCE, draft_acceptance)


def draw_rect(mask: Image.Image, rect: tuple[int, int, int, int], *, pad: int = 0) -> None:
    x, y, w, h = rect
    draw = ImageDraw.Draw(mask)
    draw.rectangle((x - pad, y - pad, x + w + pad, y + h + pad), fill=255)


def draw_ellipse(mask: Image.Image, box: tuple[int, int, int, int]) -> None:
    ImageDraw.Draw(mask).ellipse(box, fill=255)


def draw_polygon(mask: Image.Image, points: list[tuple[int, int]]) -> None:
    ImageDraw.Draw(mask).polygon(points, fill=255)


def draw_line(mask: Image.Image, points: list[tuple[int, int]], width: int) -> None:
    draw = ImageDraw.Draw(mask)
    draw.line(points, fill=255, width=width, joint="curve")
    radius = width // 2
    for x, y in points:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)


def build_masks(source: Image.Image) -> dict[str, Image.Image]:
    masks = {name: Image.new("L", CANVAS, 0) for name in ["terrain_details", "behind_player_structures", "ysort_props_structures", "foreground_occlusion"]}

    # Semantic rework: static scenery stays baked into the base image. Only the
    # front old-maple canopy/trunk pixels are exported as player occlusion.
    draw_ellipse(masks["foreground_occlusion"], (1225, 690, 1600, 980))
    draw_polygon(masks["foreground_occlusion"], [(1352, 900), (1468, 875), (1518, 1040), (1405, 1120), (1332, 1038)])

    return masks


def inpaint_base(source: Image.Image, removal_mask: Image.Image) -> Image.Image:
    # Review-quality deterministic fill: it removes separated object pixels from
    # the base while the overlaid layers preserve exact source pixels.
    blurred = source.convert("RGB").filter(ImageFilter.GaussianBlur(22))
    base = Image.composite(blurred, source.convert("RGB"), removal_mask)
    return base.convert("RGBA")


def layer_from_mask(source: Image.Image, mask: Image.Image) -> Image.Image:
    layer = source.copy()
    layer.putalpha(mask)
    return layer


def nontransparent_pixels(image: Image.Image) -> int:
    alpha = image.getchannel("A")
    return sum(1 for value in alpha.getdata() if value > 0)


def mean_rgb_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def paste_panel(sheet: Image.Image, image: Image.Image, label: str, index: int) -> None:
    thumb = image.convert("RGBA")
    if image.mode == "RGBA" and image.getchannel("A").getextrema()[0] == 0:
        checker = Image.new("RGBA", image.size, (232, 232, 232, 255))
        draw = ImageDraw.Draw(checker)
        step = 40
        for y in range(0, image.size[1], step):
            for x in range(0, image.size[0], step):
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
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    recomposite.convert("RGB").save(RECOMPOSITE_PREVIEW)
    sheet = Image.new("RGB", (1170, 870), (226, 224, 218))
    panels = [
        ("accepted source", source),
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


def write_layer_files(source: Image.Image) -> dict[str, Image.Image]:
    LAYER_DIR.mkdir(parents=True, exist_ok=True)
    masks = build_masks(source)
    layers = {
        "base_ground": source.copy(),
        "terrain_details": layer_from_mask(source, masks["terrain_details"]),
        "behind_player_structures": layer_from_mask(source, masks["behind_player_structures"]),
        "ysort_props_structures": layer_from_mask(source, masks["ysort_props_structures"]),
        "foreground_occlusion": layer_from_mask(source, masks["foreground_occlusion"]),
    }
    for layer_id, image in layers.items():
        image.save(LAYER_DIR / f"village_{layer_id}.png")
    return layers


def update_source_metadata() -> None:
    source_payload = {
        "candidate_id": CANDIDATE_ID,
        "status": "accepted_for_layer_export",
        "candidate_type": "true_storybook_painted_source",
        "source_image": rel(CANONICAL_SOURCE),
        "accepted_candidate_image": rel(CANDIDATE),
        "preserved_layout_structure_draft": rel(LAYOUT_DRAFT),
        "canvas": {"width": CANVAS[0], "height": CANVAS[1]},
        "alpha": "opaque",
        "human_visual_approval": True,
        "human_approval_note": "User accepted the candidate in-chat on 2026-05-24 and asked to proceed.",
        "layer_export_approved": True,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "notes": [
            "This is the accepted source for Village v001 layer export.",
            "Runtime art replacement remains blocked until layer review and Godot screenshot validation.",
        ],
    }
    write_json(SOURCE_ACCEPTANCE, source_payload)

    candidate_meta = read_json(CANDIDATE_META)
    candidate_meta["status"] = "accepted_for_layer_export"
    candidate_meta["human_visual_approval"] = True
    candidate_meta["human_approval_note"] = source_payload["human_approval_note"]
    candidate_meta["layer_export_approved"] = True
    candidate_meta["runtime_replacement"] = False
    candidate_meta["launch_quality_approved"] = False
    candidate_meta["canonical_source_image"] = rel(CANONICAL_SOURCE)
    write_json(CANDIDATE_META, candidate_meta)


def write_manifest(layers: dict[str, Image.Image], recomposite: Image.Image, recomposite_diff: float) -> None:
    layer_contract = read_json(LAYER_CONTRACT)
    contract_by_id = {layer["id"]: layer for layer in layer_contract["layers"]}
    semantic_roles = {
        "base_ground": "baked_static_scene",
        "terrain_details": "baked_into_base_empty_runtime_layer",
        "behind_player_structures": "baked_into_base_empty_runtime_layer",
        "ysort_props_structures": "baked_into_base_empty_runtime_layer",
        "foreground_occlusion": "player_foreground_occlusion",
    }
    records = []
    for layer_id, image in layers.items():
        contract = contract_by_id[layer_id]
        path = LAYER_DIR / f"village_{layer_id}.png"
        alpha = image.getchannel("A")
        records.append(
            {
                "id": layer_id,
                "path": rel(path),
                "runtime_path": contract["runtime_path"],
                "derived_from": rel(CANONICAL_SOURCE),
                "canvas": [CANVAS[0], CANVAS[1]],
                "alpha": contract["alpha"],
                "z_index": contract["z_index"],
                "semantic_role": semantic_roles[layer_id],
                "nontransparent_pixels": CANVAS[0] * CANVAS[1]
                if layer_id == "base_ground"
                else nontransparent_pixels(image),
                "alpha_range": list(alpha.getextrema()),
                "sha256": sha256(path),
            }
        )

    payload = {
        "package_id": "village_world2d_v001_layer_export",
        "status": "semantic_rework_exported_pending_review",
        "source_image": rel(CANONICAL_SOURCE),
        "source_sha256": sha256(CANONICAL_SOURCE),
        "accepted_candidate_id": CANDIDATE_ID,
        "canvas": {"width": CANVAS[0], "height": CANVAS[1], "origin": "top_left"},
        "layer_count": len(records),
        "layers": records,
        "recomposite_preview": rel(RECOMPOSITE_PREVIEW),
        "review_preview": rel(REVIEW_PREVIEW),
        "recomposite_mean_rgb_diff": round(recomposite_diff, 4),
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "human_layer_review": False,
        "semantic_layer_rework": True,
        "review_result": "semantic_rework_pending_review",
        "rework_required": False,
        "rework_target": "Review semantic baked-base layer export before any Godot integration.",
        "notes": [
            "Semantic rework keeps static scenery baked into the opaque base layer.",
            "Transparent layers keep the full 1800x1200 canvas and shared origin.",
            "Terrain, set-back structures, and current Y-sort props are empty runtime placeholders because their static pixels remain in the baked base.",
            "Only foreground player-occlusion pixels are exported as a visible runtime layer in this pass.",
            "Godot runtime replacement is intentionally blocked until semantic layer review.",
        ],
    }
    write_json(LAYER_MANIFEST, payload)


def update_contract_and_workflow() -> None:
    contract = read_json(LAYER_CONTRACT)
    contract["source_image"]["current_file_status"] = "accepted_true_painted_source"
    contract["source_image"]["do_not_split_current_file"] = False
    contract["source_image"]["required_next_step"] = "Review semantic layer export, then run Godot screenshot validation before runtime replacement."
    contract["source_image"]["human_visual_approval"] = True
    contract["source_image"]["accepted_candidate"] = CANDIDATE_ID
    contract["active_layer_manifest"] = rel(LAYER_MANIFEST)
    contract["layer_export_status"] = "semantic_rework_exported_pending_review"
    contract["review_result"] = "semantic_rework_pending_review"
    contract["runtime_replacement"] = False
    contract["global_rules"] = [
        "The preserved layout draft remains blocked from layer splitting.",
        "All runtime layers derive from the accepted true storybook village_painted_source.",
        "Transparent layers keep the full 1800x1200 canvas.",
        "No structural layer may be cropped, resized, rotated, or auto-trimmed.",
        "Layer alignment target is registration-perfect, not pixel-perfect brush tracing.",
        "Static scenery stays baked into the base image unless a layer needs player occlusion, dynamic state, interaction, or clean Y-sort behavior.",
        "Do not promote broad rectangular object patches; houses, vegetation, and nearby ground texture should not travel as one sticker-like runtime sprite.",
        "Runtime replacement waits for semantic layer review and Godot screenshot validation.",
        "Weather, season, and time-of-day overlays are deferred to global Godot/system-level treatment until seamless base continuity is stable.",
    ]
    content_by_id = {
        "base_ground": "Complete accepted painted source used as the baked static scene base.",
        "terrain_details": "Empty runtime layer in this semantic pass; terrain detail remains baked into the base.",
        "behind_player_structures": "Empty runtime layer in this semantic pass; static houses and distant vegetation remain baked into the base.",
        "ysort_props_structures": "Empty runtime layer in this semantic pass; current props remain baked into the base until a clean semantic Y-sort object is needed.",
        "foreground_occlusion": "Only old-maple foreground pixels that should visually cover the player.",
    }
    for layer in contract.get("layers", []):
        layer_id = layer.get("id")
        if layer_id in content_by_id:
            layer["content"] = content_by_id[layer_id]
    write_json(LAYER_CONTRACT, contract)

    workflow = read_json(WORKFLOW)
    workflow["status"] = "semantic_layer_rework_exported_pending_review"
    workflow["current_phase"] = "03_layer_export_semantic_review"
    workflow["runtime_replacement"] = False
    source_candidate = workflow.get("source_candidate", {})
    source_candidate["source_image"] = rel(LAYOUT_DRAFT)
    source_candidate["acceptance_record"] = rel(LAYOUT_DRAFT_ACCEPTANCE)
    source_candidate["not_final_painted_source"] = True
    source_candidate["do_not_split_layers_from_this_image"] = True
    workflow["source_candidate"] = source_candidate
    true_candidate = workflow.get("true_painted_source_candidate", {})
    true_candidate["status"] = "accepted_for_layer_export"
    true_candidate["human_visual_approval"] = True
    true_candidate["layer_export_approved"] = True
    true_candidate["runtime_replacement"] = False
    true_candidate["launch_quality_approved"] = False
    true_candidate["canonical_source_image"] = rel(CANONICAL_SOURCE)
    workflow["true_painted_source_candidate"] = true_candidate
    workflow["accepted_source"] = {
        "candidate_id": CANDIDATE_ID,
        "image": rel(CANONICAL_SOURCE),
        "acceptance_record": rel(SOURCE_ACCEPTANCE),
        "human_visual_approval": True,
        "layer_export_approved": True,
        "runtime_replacement": False,
        "launch_quality_approved": False,
    }
    workflow["active_layer_export"] = {
        "manifest": rel(LAYER_MANIFEST),
        "layer_count": 5,
        "status": "semantic_rework_exported_pending_review",
        "runtime_replacement": False,
        "human_layer_review": False,
        "review_result": "semantic_rework_pending_review",
    }
    phase_status = workflow.get("phase_status", {})
    phase_status["02_source_generation"] = "accepted_for_layer_export"
    phase_status["03_layer_export"] = "semantic_rework_exported_pending_review"
    phase_status["04_godot_integration"] = "blocked_until_semantic_layer_review_and_godot_screenshot"
    workflow["phase_status"] = phase_status
    workflow.setdefault("validation", {})["layer_export_validator"] = "tools/validate_village_layer_export.py"
    write_json(WORKFLOW, workflow)


def update_project_manifest() -> None:
    manifest_path = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"
    manifest = read_json(manifest_path)
    for region in manifest.get("current_runtime_regions", []):
        if region.get("region_id") != "Region_Village":
            continue
        region["phase"] = "village_semantic_layers_exported_pending_review"
        region["active_layer_manifest"] = rel(LAYER_MANIFEST)
        region["runtime_replacement"] = False
        region["launch_quality_approved"] = False
        region["human_visual_approval_required"] = True
        region["next_art_step"] = "Review semantic Village layers, then run Godot screenshot validation before runtime replacement."
    seamless = manifest.get("seamless_outdoor_world", {})
    seamless["next_art_step"] = "Review semantic Village layers against the OutdoorWorld master before runtime replacement."
    manifest["seamless_outdoor_world"] = seamless
    write_json(manifest_path, manifest)


def main() -> None:
    if not CANDIDATE.is_file():
        raise SystemExit(f"FAIL: missing accepted candidate: {rel(CANDIDATE)}")
    preserve_layout_draft()
    candidate = open_source(CANDIDATE)
    candidate.save(CANONICAL_SOURCE)
    layers = write_layer_files(candidate)
    recomposite = layers["base_ground"].copy()
    for layer_id in ["terrain_details", "behind_player_structures", "ysort_props_structures", "foreground_occlusion"]:
        recomposite.alpha_composite(layers[layer_id])
    recomposite_diff = mean_rgb_diff(candidate, recomposite)
    write_review_previews(candidate, layers, recomposite)
    write_manifest(layers, recomposite, recomposite_diff)
    update_source_metadata()
    update_contract_and_workflow()
    update_project_manifest()
    print(f"OK: exported Village accepted source layers diff={recomposite_diff:.4f}")
    print(f"OK: wrote {rel(LAYER_MANIFEST)}")


if __name__ == "__main__":
    main()
