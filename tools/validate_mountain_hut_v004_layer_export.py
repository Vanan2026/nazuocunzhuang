from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE = PACKAGE_DIR / "02_source_generation/v004/mountain_hut_painted_source_v004.png"
SOURCE_ACCEPTANCE = PACKAGE_DIR / "02_source_generation/v004/source_acceptance_v004.json"
VISUAL_REVIEW = PACKAGE_DIR / "05_review_and_qa/source_visual_review_v004.json"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
LAYER_MANIFEST = PACKAGE_DIR / "03_layer_export/layer_export_manifest.json"
RECOMPOSITE_PREVIEW = PACKAGE_DIR / "03_layer_export/mountain_hut_layer_recomposite_preview.png"
REVIEW_PREVIEW = PACKAGE_DIR / "05_review_and_qa/mountain_hut_layer_export_review_preview_v004.png"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"

CANVAS = (1800, 1200)
STATUS = "v004_semantic_layers_exported_pending_review"
WORKFLOW_PHASE = "03_layer_export_v004_semantic_review"
REQUIRED_LAYERS = {
    "base_ground": {"alpha": "opaque", "z_index": -30, "min_pixels": 2_160_000, "max_pixels": 2_160_000},
    "terrain_details": {"alpha": "transparent_full_canvas", "z_index": -25, "min_pixels": 0, "max_pixels": 0},
    "behind_player_structures": {"alpha": "transparent_full_canvas", "z_index": -10, "min_pixels": 0, "max_pixels": 0},
    "ysort_props_structures": {"alpha": "transparent_full_canvas", "z_index": 8, "min_pixels": 0, "max_pixels": 0},
    "foreground_occlusion": {"alpha": "transparent_full_canvas", "z_index": 40, "min_pixels": 40_000, "max_pixels": 320_000},
}


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
    return path.read_text(encoding="utf-8-sig")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid json in {rel(path)}: {exc}")
    require(isinstance(data, dict), f"{rel(path)} must contain a JSON object")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def open_rgba(path: Path) -> Image.Image:
    require(path.is_file(), f"missing image: {rel(path)}")
    image = Image.open(path)
    require(image.size == CANVAS, f"{rel(path)} must be {CANVAS}, got {image.size}")
    require(image.mode in {"RGB", "RGBA"}, f"{rel(path)} must be RGB/RGBA, got {image.mode}")
    return image.convert("RGBA")


def nontransparent_pixels(image: Image.Image) -> int:
    return sum(1 for value in image.getchannel("A").getdata() if value > 0)


def mean_rgb_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def validate_source_records(manifest: dict[str, Any]) -> None:
    source = open_rgba(SOURCE)
    require(source.getchannel("A").getextrema() == (255, 255), "v004 source must be opaque")
    require(manifest.get("source_image") == rel(SOURCE), "manifest source path mismatch")
    require(manifest.get("source_sha256") == sha256(SOURCE), "manifest source sha mismatch")

    acceptance = load_json(SOURCE_ACCEPTANCE)
    require(acceptance.get("candidate_id") == "mountain_hut_painted_source_candidate_v004", "source candidate id mismatch")
    require(acceptance.get("status") == "v004_accepted_for_semantic_layer_export_review", "source acceptance status mismatch")
    require(acceptance.get("human_visual_approval") is False, "v004 acceptance must not claim human approval")
    require(acceptance.get("layer_export_approved") is False, "v004 acceptance must not claim final layer approval")
    review = acceptance.get("codex_visual_review", {})
    require(review.get("status") == "accepted_for_semantic_layer_export_review", "acceptance visual review status mismatch")

    visual = load_json(VISUAL_REVIEW)
    require(visual.get("status") == "accepted_for_semantic_layer_export_review", "visual review status mismatch")
    require(visual.get("v004_visual_accepted_for_layer_export_review") is True, "visual review must accept v004 for semantic layer export review")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(visual.get(key) is False, f"visual review must keep {key}=false")


def validate_layers(manifest: dict[str, Any]) -> None:
    layers = manifest.get("layers")
    require(isinstance(layers, list), "layer manifest must contain layers list")
    by_id = {str(layer.get("id", "")): layer for layer in layers if isinstance(layer, dict)}
    require(set(by_id) == set(REQUIRED_LAYERS), f"layer ids mismatch: {sorted(by_id)}")

    source = open_rgba(SOURCE)
    ordered: list[Image.Image] = []
    base: Image.Image | None = None
    for layer_id, expected in REQUIRED_LAYERS.items():
        record = by_id[layer_id]
        path = ROOT / str(record.get("path", ""))
        image = open_rgba(path)
        require(record.get("canvas") == [CANVAS[0], CANVAS[1]], f"{layer_id} canvas mismatch")
        require(record.get("alpha") == expected["alpha"], f"{layer_id} alpha metadata mismatch")
        require(record.get("z_index") == expected["z_index"], f"{layer_id} z-index mismatch")
        require(record.get("derived_from") == rel(SOURCE), f"{layer_id} must derive from v004 source")
        require(record.get("sha256") == sha256(path), f"{layer_id} sha mismatch")
        pixel_count = nontransparent_pixels(image)
        require(pixel_count == record.get("nontransparent_pixels"), f"{layer_id} nontransparent count mismatch")
        require(expected["min_pixels"] <= pixel_count <= expected["max_pixels"], f"{layer_id} pixel count out of range: {pixel_count}")
        if layer_id == "base_ground":
            require(image.getchannel("A").getextrema() == (255, 255), "base layer must be opaque")
            require(mean_rgb_diff(source, image) <= 0.1, "base layer must preserve the complete v004 source")
            require(record.get("semantic_role") == "baked_static_scene", "base semantic role mismatch")
            base = image
        else:
            if expected["max_pixels"] == 0:
                require(image.getchannel("A").getextrema() == (0, 0), f"{layer_id} must be empty in semantic review")
                require(record.get("semantic_role") == "baked_into_base_empty_runtime_layer", f"{layer_id} semantic role mismatch")
            else:
                require(image.getchannel("A").getextrema() == (0, 255), f"{layer_id} must use full-canvas alpha")
                require(record.get("semantic_role") == "player_foreground_occlusion", "foreground semantic role mismatch")
            ordered.append(image)

    require(base is not None, "base layer not loaded")
    composite = base.copy()
    for image in ordered:
        composite.alpha_composite(image)
    diff = mean_rgb_diff(source, composite)
    require(diff <= 1.0, f"layer recomposite differs from source: {diff:.4f}")
    require(float(manifest.get("recomposite_mean_rgb_diff", 9999.0)) <= 1.0, "manifest recomposite diff too high")
    require(RECOMPOSITE_PREVIEW.is_file(), "missing recomposite preview")
    require(REVIEW_PREVIEW.is_file(), "missing review preview")


def validate_workflow_contract_project() -> None:
    workflow = load_json(WORKFLOW)
    require(workflow.get("status") == STATUS, "workflow status mismatch")
    require(workflow.get("current_phase") == WORKFLOW_PHASE, "workflow phase mismatch")
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime replacement false")
    phase_status = workflow.get("phase_status", {})
    require(phase_status.get("03_layer_export") == STATUS, "workflow layer phase mismatch")
    require(phase_status.get("04_godot_integration") == "blocked_until_v004_semantic_layer_review_and_godot_screenshot", "workflow Godot gate mismatch")
    active = workflow.get("active_layer_export", {})
    require(active.get("manifest") == rel(LAYER_MANIFEST), "workflow active layer manifest mismatch")
    require(active.get("runtime_replacement") is False, "workflow active layer export must not replace runtime art")

    contract = load_json(LAYER_CONTRACT)
    source = contract.get("source_image", {})
    require(source.get("current_file_status") == "v004_codex_visual_accepted_for_semantic_layer_export", "contract source status mismatch")
    require(source.get("human_visual_approval") is False, "contract must not claim human approval")
    require(source.get("layer_export_approved") is False, "contract must not claim final layer approval")
    require(contract.get("active_layer_manifest") == rel(LAYER_MANIFEST), "contract active manifest mismatch")
    require(contract.get("layer_export_status") == STATUS, "contract layer export status mismatch")
    require(contract.get("runtime_replacement") is False, "contract must keep runtime replacement false")

    project = load_json(PROJECT_MANIFEST)
    regions = project.get("current_runtime_regions", [])
    hut = next((item for item in regions if isinstance(item, dict) and item.get("region_id") == "Region_MountainHut"), None)
    require(isinstance(hut, dict), "project manifest missing Region_MountainHut")
    require(hut.get("phase") == STATUS, "project manifest MountainHut phase mismatch")
    require(hut.get("active_layer_manifest") == rel(LAYER_MANIFEST), "project manifest layer manifest mismatch")
    require(hut.get("runtime_replacement") is False, "project manifest must keep runtime replacement false")
    require(hut.get("launch_quality_approved") is False, "project manifest must keep launch approval false")


def main() -> None:
    manifest = load_json(LAYER_MANIFEST)
    require(manifest.get("package_id") == "mountain_hut_world2d_v001_layer_export", "layer manifest package id mismatch")
    require(manifest.get("status") == STATUS, "layer manifest status mismatch")
    require(manifest.get("runtime_replacement") is False, "layer manifest must keep runtime replacement false")
    require(manifest.get("launch_quality_approved") is False, "layer manifest must keep launch approval false")
    validate_source_records(manifest)
    validate_layers(manifest)
    validate_workflow_contract_project()
    print("OK: MountainHut v004 semantic layer export validates")


if __name__ == "__main__":
    main()
