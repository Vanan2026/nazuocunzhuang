from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_world_layout" / "outdoor_world_layout_lock.json"
SOURCE_STRATEGY = PACKAGE_DIR / "02_source_strategy" / "source_generation_strategy.md"
BASE_DIR = PACKAGE_DIR / "02_world_base_no_foreground"
WORLD_BASE = BASE_DIR / "outdoor_world_base_no_foreground.png"
WORLD_BASE_PREVIEW = BASE_DIR / "outdoor_world_base_no_foreground_review.png"
BASE_MANIFEST = BASE_DIR / "world_base_manifest.json"
REGION_CROP_DIR = BASE_DIR / "region_base_crops"
GENERATOR = ROOT / "tools" / "generate_outdoor_world_base_map.py"
PROJECT_MANIFEST = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"

EXPECTED_REGION_IDS = [
    "player_yard",
    "forest_edge",
    "village",
    "back_farm",
    "orchard",
    "pond",
    "mountain_path",
    "mountain_hut",
    "mountain",
    "cliff_view",
]
EXPECTED_PHASE = "02_world_base_no_foreground"
WORLD_CANVAS = [9900, 4950]
REGION_CANVAS = [1800, 1200]


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
    require(isinstance(data, dict), f"{rel(path)} must be a JSON object")
    return data


def as_list(value: Any, label: str) -> list[Any]:
    require(isinstance(value, list), f"{label} must be a list")
    return value


def as_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def open_rgb(path: Path, expected_size: list[int]) -> Image.Image:
    require(path.is_file(), f"missing image: {rel(path)}")
    image = Image.open(path).convert("RGB")
    require(list(image.size) == expected_size, f"{rel(path)} size mismatch: {image.size}, expected {expected_size}")
    return image


def mean_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def validate_manifest() -> dict[str, Any]:
    manifest = load_json(BASE_MANIFEST)
    require(manifest.get("package_id") == "outdoor_world_base_no_foreground_v001", "base manifest package id mismatch")
    require(manifest.get("status") == "world_base_no_foreground_ready_for_region_crop_review", "base manifest status mismatch")
    require(manifest.get("world_base_image") == rel(WORLD_BASE), "base manifest world image path mismatch")
    require(manifest.get("review_preview") == rel(WORLD_BASE_PREVIEW), "base manifest review path mismatch")
    require(manifest.get("world_canvas") == WORLD_CANVAS, "base manifest world canvas mismatch")
    require(manifest.get("region_canvas") == REGION_CANVAS, "base manifest region canvas mismatch")
    require(manifest.get("runtime_replacement") is False, "base manifest must keep runtime_replacement=false")
    require(manifest.get("launch_quality_approved") is False, "base manifest must keep launch_quality_approved=false")
    require(manifest.get("foreground_policy") == "foreground_occlusion_is_per_region_separate_layer", "foreground policy mismatch")
    require(manifest.get("high_quality_region_rule") == "region repaint starts from inherited world_base crop", "high-quality region rule mismatch")
    region_crops = as_list(manifest.get("region_crops"), "base manifest region_crops")
    require(len(region_crops) == len(EXPECTED_REGION_IDS), "base manifest region crop count mismatch")
    by_id = {str(as_dict(item, "region crop").get("region_id")): as_dict(item, "region crop") for item in region_crops}
    require(list(by_id) == EXPECTED_REGION_IDS, "base manifest region crop order mismatch")
    return manifest


def validate_images(manifest: dict[str, Any]) -> None:
    world = open_rgb(WORLD_BASE, WORLD_CANVAS)
    preview = open_rgb(WORLD_BASE_PREVIEW, [2200, 1100])
    require(sum(ImageStat.Stat(world).var) > 250.0, "world base appears too flat")
    require(sum(ImageStat.Stat(preview).var) > 250.0, "world base review preview appears too flat")

    for item in as_list(manifest.get("region_crops"), "region_crops"):
        crop = as_dict(item, "region crop")
        region_id = str(crop.get("region_id"))
        crop_path = ROOT / str(crop.get("path", ""))
        image = open_rgb(crop_path, REGION_CANVAS)
        require(crop.get("derived_from") == rel(WORLD_BASE), f"{region_id} must derive from whole-world base")
        require(crop.get("canvas") == REGION_CANVAS, f"{region_id} crop canvas mismatch")
        require(crop.get("foreground_removed") is True, f"{region_id} crop must be marked foreground_removed")
        require(crop.get("repaint_status") == "base_crop_only_not_final_scene_art", f"{region_id} repaint status mismatch")
        require(sum(ImageStat.Stat(image).var) > 120.0, f"{region_id} crop appears too flat")

        crop_box = as_list(crop.get("world_base_crop_box"), f"{region_id}.world_base_crop_box")
        require(len(crop_box) == 4, f"{region_id} crop box must have 4 values")
        expected = world.crop(tuple(int(v) for v in crop_box))
        expected = expected.resize(tuple(REGION_CANVAS), Image.Resampling.BICUBIC)
        require(mean_diff(image, expected) <= 0.6, f"{region_id} crop no longer matches whole-world base inheritance")


def validate_workflow_and_docs() -> None:
    workflow = load_json(WORKFLOW)
    require(workflow.get("current_phase") == EXPECTED_PHASE, "workflow must move to whole-world base phase")
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime replacement false")
    artifacts = as_dict(workflow.get("artifacts"), "workflow.artifacts")
    require(artifacts.get("world_base_no_foreground") == rel(WORLD_BASE), "workflow world base artifact mismatch")
    require(artifacts.get("world_base_manifest") == rel(BASE_MANIFEST), "workflow base manifest artifact mismatch")
    require(artifacts.get("region_base_crops_dir") == rel(REGION_CROP_DIR), "workflow crop dir artifact mismatch")
    decision = as_dict(workflow.get("art_pipeline_decision"), "workflow.art_pipeline_decision")
    require(decision.get("pipeline") == "world_blueprint_to_world_base_to_region_crops_to_foreground_layers", "workflow pipeline decision mismatch")
    require(decision.get("single_region_repaint_rule") == "must inherit from world_base crop", "workflow repaint inheritance rule mismatch")

    strategy = read(SOURCE_STRATEGY)
    strategy_normalized = strategy.lower()
    for token in [
        "world_base_no_foreground",
        "whole-world base",
        "region crop",
        "foreground_occlusion",
        "must start from the inherited crop",
        "do not independently recompose region bases",
    ]:
        require(token in strategy_normalized, f"source strategy missing token: {token}")

    generator_text = read(GENERATOR)
    for token in ["WORLD_CANVAS", "write_world_base", "write_region_crops", "write_base_manifest", "update_workflow"]:
        require(token in generator_text, f"base-map generator missing token: {token}")

    project = load_json(PROJECT_MANIFEST)
    master = as_dict(project.get("seamless_outdoor_world"), "project manifest seamless_outdoor_world")
    require(master.get("phase") == EXPECTED_PHASE, "project manifest seamless phase mismatch")
    require(master.get("world_base_no_foreground") == rel(WORLD_BASE), "project manifest world base pointer mismatch")
    require(master.get("runtime_replacement") is False, "project manifest must keep runtime replacement false")


def main() -> None:
    manifest = validate_manifest()
    validate_images(manifest)
    validate_workflow_and_docs()
    print("OK: OutdoorWorld whole-world base-map pipeline validates")


if __name__ == "__main__":
    main()
