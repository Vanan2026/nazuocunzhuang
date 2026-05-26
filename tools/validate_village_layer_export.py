from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
SOURCE_IMAGE = PACKAGE_DIR / "02_source_generation" / "village_painted_source.png"
SOURCE_ACCEPTANCE = PACKAGE_DIR / "02_source_generation" / "source_acceptance.json"
CANDIDATE_IMAGE = (
    PACKAGE_DIR
    / "02_source_generation"
    / "true_source_candidates"
    / "village_true_painted_source_candidate_v001.png"
)
CANDIDATE_META = (
    PACKAGE_DIR
    / "02_source_generation"
    / "true_source_candidates"
    / "village_true_painted_source_candidate_v001.json"
)
LAYOUT_DRAFT = (
    PACKAGE_DIR
    / "02_source_generation"
    / "layout_structure_drafts"
    / "village_layout_structure_draft_v001.png"
)
LAYOUT_DRAFT_ACCEPTANCE = (
    PACKAGE_DIR
    / "02_source_generation"
    / "layout_structure_drafts"
    / "village_layout_structure_draft_v001_acceptance.json"
)
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export" / "layer_contract.json"
LAYER_MANIFEST = PACKAGE_DIR / "03_layer_export" / "layer_export_manifest.json"
REVIEW_PREVIEW = PACKAGE_DIR / "05_review_and_qa" / "village_layer_export_review_preview_v001.png"

CANVAS = (1800, 1200)
REQUIRED_LAYERS = {
    "base_ground": {"alpha": "opaque", "z_index": -30},
    "terrain_details": {"alpha": "transparent_full_canvas", "z_index": -25},
    "behind_player_structures": {"alpha": "transparent_full_canvas", "z_index": -10},
    "ysort_props_structures": {"alpha": "transparent_full_canvas", "z_index": 8},
    "foreground_occlusion": {"alpha": "transparent_full_canvas", "z_index": 40},
}
ALLOWED_LAYER_REVIEW_STATUSES = {
    "exported_pending_layer_review",
    "review_rejected_for_runtime_sticker_effect",
    "semantic_rework_exported_pending_review",
}
ALLOWED_WORKFLOW_STATUSES = {
    "accepted_source_layers_exported_pending_layer_review",
    "layer_review_rejected_semantic_rework_required",
    "semantic_layer_rework_exported_pending_review",
    "v002_inherited_crop_candidate_ready_for_visual_review",
    "v002_codex_visual_accepted_for_semantic_layer_export",
    "v002_semantic_layers_exported_pending_review",
}
ALLOWED_WORKFLOW_PHASES = {
    "03_layer_export_review",
    "03_layer_export_rework",
    "03_layer_export_semantic_review",
    "02_source_generation_v002_inherited_review",
    "02_source_visual_review_v002",
    "03_layer_export_v002_semantic_review",
}
ALLOWED_LAYER_PHASE_STATUSES = {
    "exported_pending_layer_review",
    "rejected_semantic_rework_required",
    "semantic_rework_exported_pending_review",
}
ALLOWED_GODOT_GATE_STATUSES = {
    "blocked_until_layer_review_and_godot_screenshot",
    "blocked_until_semantic_layer_rework_and_godot_screenshot",
    "blocked_until_semantic_layer_review_and_godot_screenshot",
}
SEMANTIC_REWORK_STATUS = "semantic_rework_exported_pending_review"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(path: Path) -> str:
    require(path.is_file(), f"missing required file: {rel(path)}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid json in {rel(path)}: {exc}")
    require(isinstance(value, dict), f"{rel(path)} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def open_rgba(path: Path) -> Image.Image:
    require(path.is_file(), f"missing image: {rel(path)}")
    image = Image.open(path)
    require(image.size == CANVAS, f"{rel(path)} must be {CANVAS}, got {image.size}")
    require(image.mode in {"RGB", "RGBA"}, f"{rel(path)} must be RGB/RGBA, got {image.mode}")
    return image.convert("RGBA")


def require_opaque(image: Image.Image, path: Path) -> None:
    require(image.getchannel("A").getextrema() == (255, 255), f"{rel(path)} must be fully opaque")


def require_transparent_layer(image: Image.Image, path: Path, min_pixels: int, *, allow_empty: bool = False) -> int:
    alpha = image.getchannel("A")
    alpha_range = alpha.getextrema()
    if allow_empty and alpha_range == (0, 0):
        return 0
    require(alpha_range[0] == 0 and alpha_range[1] == 255, f"{rel(path)} must use effective full-canvas alpha")
    bbox = alpha.getbbox()
    require(bbox is not None, f"{rel(path)} must contain visible pixels")
    histogram = alpha.histogram()
    nontransparent = sum(histogram[1:])
    require(nontransparent >= min_pixels, f"{rel(path)} has too few nontransparent pixels: {nontransparent}")
    return nontransparent


def mean_rgb_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def validate_source_state(manifest: dict[str, Any]) -> None:
    source = open_rgba(SOURCE_IMAGE)
    candidate = open_rgba(CANDIDATE_IMAGE)
    require_opaque(source, SOURCE_IMAGE)
    require_opaque(candidate, CANDIDATE_IMAGE)
    require(mean_rgb_diff(source, candidate) == 0.0, "canonical source must exactly match accepted true candidate")

    draft = open_rgba(LAYOUT_DRAFT)
    require_opaque(draft, LAYOUT_DRAFT)
    require(mean_rgb_diff(draft, source) > 1.0, "preserved layout draft should differ from accepted source")

    draft_acceptance = load_json(LAYOUT_DRAFT_ACCEPTANCE)
    require(draft_acceptance.get("candidate_type") == "layout_structure_draft", "layout draft acceptance type mismatch")
    require(draft_acceptance.get("do_not_split_layers_from_this_image") is True, "layout draft must remain blocked from splitting")

    acceptance = load_json(SOURCE_ACCEPTANCE)
    require(acceptance.get("candidate_id") == "village_true_painted_source_candidate_v001", "source acceptance candidate mismatch")
    require(acceptance.get("status") == "accepted_for_layer_export", "source acceptance status mismatch")
    require(acceptance.get("human_visual_approval") is True, "source acceptance must record human approval")
    require(acceptance.get("layer_export_approved") is True, "source acceptance must approve layer export")
    require(acceptance.get("runtime_replacement") is False, "source acceptance must not replace runtime art")
    require(acceptance.get("launch_quality_approved") is False, "source acceptance must not approve launch quality")
    require(acceptance.get("source_image") == rel(SOURCE_IMAGE), "source acceptance canonical source path mismatch")

    candidate_meta = load_json(CANDIDATE_META)
    require(candidate_meta.get("human_visual_approval") is True, "candidate metadata must record human approval")
    require(candidate_meta.get("layer_export_approved") is True, "candidate metadata must record layer-export approval")
    require(candidate_meta.get("runtime_replacement") is False, "candidate metadata must keep runtime_replacement=false")

    require(manifest.get("source_sha256") == sha256(SOURCE_IMAGE), "layer manifest source sha mismatch")


def validate_layers(manifest: dict[str, Any]) -> None:
    layers = manifest.get("layers")
    require(isinstance(layers, list), "layer manifest must contain layers list")
    by_id = {str(layer.get("id", "")): layer for layer in layers if isinstance(layer, dict)}
    require(set(by_id) == set(REQUIRED_LAYERS), f"layer ids mismatch: {sorted(by_id)}")

    base_image: Image.Image | None = None
    ordered: list[Image.Image] = []
    is_semantic_rework = manifest.get("status") == SEMANTIC_REWORK_STATUS
    max_semantic_pixels = {
        "terrain_details": 0,
        "behind_player_structures": 0,
        "ysort_props_structures": 0,
        "foreground_occlusion": 120_000,
    }

    for layer_id, expected in REQUIRED_LAYERS.items():
        layer = by_id[layer_id]
        path = ROOT / str(layer.get("path", ""))
        image = open_rgba(path)
        require(layer.get("canvas") == [CANVAS[0], CANVAS[1]], f"{layer_id} manifest canvas mismatch")
        require(layer.get("alpha") == expected["alpha"], f"{layer_id} alpha metadata mismatch")
        require(layer.get("z_index") == expected["z_index"], f"{layer_id} z_index mismatch")
        require(layer.get("sha256") == sha256(path), f"{layer_id} sha mismatch")
        require(layer.get("derived_from") == rel(SOURCE_IMAGE), f"{layer_id} must derive from canonical source")
        if layer_id == "base_ground":
            require_opaque(image, path)
            if is_semantic_rework:
                require(
                    mean_rgb_diff(open_rgba(SOURCE_IMAGE), image) <= 0.1,
                    "semantic rework base must preserve the complete accepted painted source",
                )
                require(
                    layer.get("semantic_role") == "baked_static_scene",
                    "semantic rework base must be marked as baked_static_scene",
                )
            base_image = image
        else:
            if is_semantic_rework:
                min_pixels = 20_000 if layer_id == "foreground_occlusion" else 0
                nontransparent = require_transparent_layer(image, path, min_pixels, allow_empty=layer_id != "foreground_occlusion")
                require(
                    nontransparent <= max_semantic_pixels[layer_id],
                    f"{layer_id} is too large for semantic rework: {nontransparent}",
                )
                expected_role = "player_foreground_occlusion" if layer_id == "foreground_occlusion" else "baked_into_base_empty_runtime_layer"
                require(layer.get("semantic_role") == expected_role, f"{layer_id} semantic role mismatch")
            else:
                min_pixels = 5_000 if layer_id == "terrain_details" else 20_000
                nontransparent = require_transparent_layer(image, path, min_pixels)
            require(layer.get("nontransparent_pixels") == nontransparent, f"{layer_id} nontransparent count mismatch")
            ordered.append(image)

    require(base_image is not None, "base layer was not loaded")
    composite = base_image.copy()
    for image in ordered:
        composite.alpha_composite(image)
    source = open_rgba(SOURCE_IMAGE)
    diff = mean_rgb_diff(source, composite)
    require(diff <= 8.0, f"layer recomposite differs too much from accepted source: {diff:.3f}")
    require(float(manifest.get("recomposite_mean_rgb_diff", 9999.0)) <= 8.0, "manifest recomposite diff too high")
    require((PACKAGE_DIR / "03_layer_export" / "village_layer_recomposite_preview.png").is_file(), "missing recomposite preview")
    require(REVIEW_PREVIEW.is_file(), "missing layer export review preview")


def validate_workflow_and_contract() -> None:
    workflow = load_json(WORKFLOW)
    require(workflow.get("status") in ALLOWED_WORKFLOW_STATUSES, "workflow status mismatch")
    require(workflow.get("current_phase") in ALLOWED_WORKFLOW_PHASES, "workflow phase mismatch")
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")
    true_candidate = workflow.get("true_painted_source_candidate")
    require(isinstance(true_candidate, dict), "workflow missing true candidate block")
    require(true_candidate.get("status") == "accepted_for_layer_export", "workflow true candidate status mismatch")
    require(true_candidate.get("human_visual_approval") is True, "workflow must record human source approval")
    require(true_candidate.get("layer_export_approved") is True, "workflow must record source layer-export approval")
    accepted_source = workflow.get("accepted_source")
    require(isinstance(accepted_source, dict), "workflow missing accepted_source")
    require(accepted_source.get("image") == rel(SOURCE_IMAGE), "workflow accepted source path mismatch")
    active_export = workflow.get("active_layer_export")
    require(isinstance(active_export, dict), "workflow missing active_layer_export")
    require(active_export.get("manifest") == rel(LAYER_MANIFEST), "workflow active layer manifest mismatch")
    require(active_export.get("layer_count") == 5, "workflow active layer count mismatch")
    require(active_export.get("status") in ALLOWED_LAYER_REVIEW_STATUSES, "workflow active layer status mismatch")
    require(active_export.get("runtime_replacement") is False, "workflow layer export must not replace runtime art")
    phase_status = workflow.get("phase_status")
    require(isinstance(phase_status, dict), "workflow phase_status missing")
    require(phase_status.get("03_layer_export") in ALLOWED_LAYER_PHASE_STATUSES, "workflow layer phase mismatch")
    require(phase_status.get("04_godot_integration") in ALLOWED_GODOT_GATE_STATUSES, "workflow Godot gate mismatch")

    contract = load_json(LAYER_CONTRACT)
    source_image = contract.get("source_image")
    require(isinstance(source_image, dict), "layer contract missing source_image")
    require(source_image.get("current_file_status") == "accepted_true_painted_source", "layer contract source status mismatch")
    require(source_image.get("do_not_split_current_file") is False, "layer contract should allow accepted source splitting")
    require(source_image.get("human_visual_approval") is True, "layer contract must record human source approval")
    require(contract.get("active_layer_manifest") == rel(LAYER_MANIFEST), "layer contract active manifest mismatch")
    require(contract.get("layer_export_status") in ALLOWED_LAYER_REVIEW_STATUSES, "layer contract export status mismatch")


def main() -> None:
    manifest = load_json(LAYER_MANIFEST)
    require(manifest.get("package_id") == "village_world2d_v001_layer_export", "layer manifest package_id mismatch")
    require(manifest.get("status") == SEMANTIC_REWORK_STATUS, "layer manifest must be a semantic rework export")
    require(manifest.get("runtime_replacement") is False, "layer manifest must keep runtime_replacement=false")
    require(manifest.get("launch_quality_approved") is False, "layer manifest must keep launch_quality_approved=false")
    validate_source_state(manifest)
    validate_layers(manifest)
    validate_workflow_and_contract()
    print("OK: Village accepted source layer export validates")


if __name__ == "__main__":
    main()
