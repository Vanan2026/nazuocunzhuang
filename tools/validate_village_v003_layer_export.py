from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat


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
REQUIRED_LAYERS = {
    "base_ground": {"alpha": "opaque", "z_index": -30, "min_pixels": 2_160_000, "max_pixels": 2_160_000},
    "terrain_details": {"alpha": "transparent_full_canvas", "z_index": -25, "min_pixels": 0, "max_pixels": 0},
    "behind_player_structures": {"alpha": "transparent_full_canvas", "z_index": -10, "min_pixels": 0, "max_pixels": 0},
    "ysort_props_structures": {"alpha": "transparent_full_canvas", "z_index": 8, "min_pixels": 0, "max_pixels": 0},
    "foreground_occlusion": {"alpha": "transparent_full_canvas", "z_index": 40, "min_pixels": 40_000, "max_pixels": 260_000},
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
    data = json.loads(read(path))
    require(isinstance(data, dict), f"{rel(path)} must be a JSON object")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def open_rgba(path: Path) -> Image.Image:
    require(path.is_file(), f"missing image: {rel(path)}")
    image = Image.open(path).convert("RGBA")
    require(image.size == CANVAS, f"{rel(path)} must be {CANVAS}, got {image.size}")
    return image


def nontransparent_pixels(image: Image.Image) -> int:
    return sum(image.getchannel("A").histogram()[1:])


def mean_rgb_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def validate_layers(manifest: dict[str, Any]) -> None:
    source = open_rgba(SOURCE)
    require(source.getchannel("A").getextrema() == (255, 255), "v003 source must be opaque")
    require(manifest.get("source_image") == rel(SOURCE), "manifest source path mismatch")
    require(manifest.get("source_sha256") == sha256(SOURCE), "manifest source sha mismatch")
    layers = manifest.get("layers")
    require(isinstance(layers, list), "layer manifest must contain layers list")
    by_id = {str(layer.get("id", "")): layer for layer in layers if isinstance(layer, dict)}
    require(set(by_id) == set(REQUIRED_LAYERS), f"layer ids mismatch: {sorted(by_id)}")

    composite: Image.Image | None = None
    for layer_id, expected in REQUIRED_LAYERS.items():
        record = by_id[layer_id]
        path = ROOT / str(record.get("path", ""))
        image = open_rgba(path)
        require(record.get("canvas") == [CANVAS[0], CANVAS[1]], f"{layer_id} canvas mismatch")
        require(record.get("alpha") == expected["alpha"], f"{layer_id} alpha metadata mismatch")
        require(record.get("z_index") == expected["z_index"], f"{layer_id} z-index mismatch")
        require(record.get("derived_from") == rel(SOURCE), f"{layer_id} must derive from v003 source")
        require(record.get("sha256") == sha256(path), f"{layer_id} sha mismatch")
        pixel_count = nontransparent_pixels(image)
        require(pixel_count == record.get("nontransparent_pixels"), f"{layer_id} nontransparent count mismatch")
        require(expected["min_pixels"] <= pixel_count <= expected["max_pixels"], f"{layer_id} pixel count out of range: {pixel_count}")
        if layer_id == "base_ground":
            require(mean_rgb_diff(source, image) <= 0.1, "base layer must preserve complete v003 source")
            composite = image.copy()
        else:
            if expected["max_pixels"] == 0:
                require(image.getchannel("A").getextrema() == (0, 0), f"{layer_id} must be empty in semantic review")
            else:
                require(image.getchannel("A").getextrema() == (0, 255), "foreground must use full-canvas alpha")
            assert composite is not None
            composite.alpha_composite(image)

    assert composite is not None
    diff = mean_rgb_diff(source, composite)
    require(diff <= 1.0, f"layer recomposite differs from source: {diff:.4f}")
    require(float(manifest.get("recomposite_mean_rgb_diff", 999.0)) <= 1.0, "manifest recomposite diff too high")
    require(RECOMPOSITE_PREVIEW.is_file(), "missing recomposite preview")
    require(REVIEW_PREVIEW.is_file(), "missing review preview")


def validate_records() -> None:
    acceptance = load_json(SOURCE_ACCEPTANCE)
    export = acceptance.get("semantic_layer_export")
    require(isinstance(export, dict), "source acceptance missing semantic layer export block")
    require(export.get("status") == STATUS, "source acceptance semantic export status mismatch")
    require(export.get("manifest") == rel(LAYER_MANIFEST), "source acceptance semantic export manifest mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(acceptance.get(key) is False, f"source acceptance must keep {key}=false")

    workflow = load_json(WORKFLOW)
    require(workflow.get("status") == STATUS, "workflow status mismatch")
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime replacement false")
    block = workflow.get("v003_layer_export")
    require(isinstance(block, dict), "workflow missing v003 layer export block")
    require(block.get("manifest") == rel(LAYER_MANIFEST), "workflow v003 layer manifest mismatch")
    require(block.get("runtime_replacement") is False, "workflow v003 export must not replace runtime art")

    contract = load_json(LAYER_CONTRACT)
    require(contract.get("active_v003_layer_manifest") == rel(LAYER_MANIFEST), "contract active v003 manifest mismatch")
    require(contract.get("runtime_replacement") is False, "contract must keep runtime replacement false")

    project = load_json(PROJECT_MANIFEST)
    regions = project.get("current_runtime_regions", [])
    village = next((item for item in regions if isinstance(item, dict) and item.get("region_id") == "Region_Village"), None)
    require(isinstance(village, dict), "project manifest missing Region_Village")
    require(village.get("phase") == STATUS, "project manifest Village phase mismatch")
    require(village.get("active_v003_layer_manifest") == rel(LAYER_MANIFEST), "project manifest v003 layer manifest mismatch")
    require(village.get("runtime_replacement") is False, "project manifest must keep runtime_replacement=false")

    report = read(REPORT)
    for token in [STATUS, "not runtime replacement", "full-canvas"]:
        require(token in report, f"layer export report missing {token!r}")


def main() -> None:
    manifest = load_json(LAYER_MANIFEST)
    require(manifest.get("package_id") == "village_world2d_v003_edge_continuity_layer_export", "layer manifest package id mismatch")
    require(manifest.get("status") == STATUS, "layer manifest status mismatch")
    require(manifest.get("runtime_replacement") is False, "layer manifest must keep runtime replacement false")
    validate_layers(manifest)
    validate_records()
    print("OK: Village v003 semantic layer export validates")


if __name__ == "__main__":
    main()
