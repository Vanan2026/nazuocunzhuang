from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "production/assets/regions/home_area_launch_quality/v001"
MANIFEST = PKG / "region_home_area_launch_quality_v001_manifest.json"
SCENE = ROOT / "scenes/regions/region_home_area.tscn"
SOURCE = PKG / "source/region_home_area_launch_quality_full_source_v001.png"
REVIEW = PKG / "source/region_home_area_launch_quality_full_source_v001_review.png"
PREVIEW = PKG / "region_home_area_launch_quality_v001_runtime_preview.png"
CONTACT = PKG / "region_home_area_launch_quality_v001_layer_contact_sheet.png"
CANVAS = (6144, 4096)
EXPECTED_IDS = {
    "ground_yard",
    "path_village_road",
    "path_back_farm",
    "veranda_floor",
    "house_body",
    "house_roof_occluder",
    "tree_left_trunk",
    "tree_left_canopy_occluder",
    "tree_right_trunk",
    "tree_right_canopy_occluder",
    "foreground_grass",
    "shadow_dappled",
    "light_overlay",
    "prop_mailbox",
    "prop_well",
    "prop_bench",
    "prop_road_sign",
    "prop_cat_bed",
}
FORBIDDEN_SCENE_REFS = (
    "home_area_launch_quality/v001/source/",
    "region_home_area_launch_quality_full_source_v001.png",
    "region_home_area_launch_quality_full_source_v001_review.png",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def require_image(path: Path, size: tuple[int, int] | None, label: str, needs_alpha: bool = False) -> Image.Image:
    require(path.exists(), f"missing {label}: {path.relative_to(ROOT).as_posix()}")
    img = Image.open(path).convert("RGBA")
    if size is not None:
        require(img.size == size, f"{label} size mismatch: expected {size}, got {img.size}")
    stat = ImageStat.Stat(img.getchannel("A"))
    require(stat.extrema[0][1] > 0, f"{label} must contain visible pixels")
    if needs_alpha:
        require(img.getchannel("A").getextrema()[0] < 255, f"{label} must preserve transparency")
    return img


def node_block(scene_text: str, name: str) -> str:
    match = re.search(rf'\[node name="{re.escape(name)}" [^\]]*\].*?(?=\n\[node |\n\[connection |\Z)', scene_text, re.S)
    require(match is not None, f"missing node: {name}")
    return match.group(0)


def main() -> None:
    require(MANIFEST.exists(), "missing launch-quality v001 manifest")
    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "manifest")
    require(manifest.get("region_id") == "Region_HomeArea", "region mismatch")
    require(manifest.get("package_id") == "home_area_launch_quality_v001", "package mismatch")
    require(manifest.get("status") == "godot_review_candidate_needs_human_visual_approval", "v001 must stay review-gated")
    require(manifest.get("runtime_replacement") is False, "v001 must not claim final runtime replacement")
    require(manifest.get("runtime_scene_reference_allowed") is True, "v001 must explicitly allow review scene references")
    require(manifest.get("human_visual_approval_required") is True, "v001 must require human visual approval")
    require(manifest.get("launch_quality_approved") is False, "v001 must not be launch approved before review")
    gate = require_dict(manifest.get("quality_gate"), "quality_gate")
    require(gate.get("approval_status") == "needs_user_godot_visual_review", "quality gate approval status mismatch")
    require(gate.get("may_set_runtime_replacement_before_approval") is False, "quality gate must block pre-approval runtime replacement")

    require_image(SOURCE, CANVAS, "full source")
    require_image(REVIEW, (1536, 1024), "review source")
    require_image(PREVIEW, CANVAS, "runtime preview")
    require_image(CONTACT, None, "contact sheet")

    source_assets = manifest.get("source_assets")
    require(isinstance(source_assets, list) and source_assets and source_assets[0].get("sha256"), "source sha missing")
    source_sha = source_assets[0]["sha256"]
    layers = manifest.get("required_layers")
    require(isinstance(layers, list), "required_layers must be a list")
    by_id = {str(layer.get("asset_id")): require_dict(layer, "layer") for layer in layers if isinstance(layer, dict)}
    require(set(by_id) == EXPECTED_IDS, f"layer id mismatch: {sorted(set(by_id))}")

    for asset_id, layer in by_id.items():
        rel = str(layer.get("file"))
        require(rel.startswith("layers/"), f"{asset_id} must live under layers/")
        require(rel.endswith("_lq_v001.png"), f"{asset_id} must use launch-quality v001 filename")
        require(layer.get("derived_from_single_source") is True, f"{asset_id} must be derived from the single source")
        require(layer.get("source_sha256") == source_sha, f"{asset_id} source sha mismatch")
        require(layer.get("source_rect_px"), f"{asset_id} missing source rect")
        mask_file = str(layer.get("mask_file"))
        require(mask_file.startswith("source/masks/") and mask_file.endswith("_mask.png"), f"{asset_id} mask path invalid")
        require((PKG / mask_file).exists(), f"{asset_id} mask file missing")
        size = require_dict(layer.get("size_px"), f"{asset_id} size_px")
        needs_alpha = bool(layer.get("transparent_background"))
        require_image(PKG / rel, (int(size["width"]), int(size["height"])), asset_id, needs_alpha=needs_alpha)

    scene_text = SCENE.read_text(encoding="utf-8-sig")
    root = node_block(scene_text, "Region_HomeArea")
    require('metadata/art_package = "home_area_launch_quality_v001"' in root, "scene must record active launch-quality v001 package")
    require('metadata/status = "active_home_area_launch_quality_v001_godot_review_candidate"' in root, "scene must record v001 review candidate status")
    require('metadata/launch_quality_approved = false' in root, "scene must block launch approval before review")
    for forbidden in FORBIDDEN_SCENE_REFS:
        require(forbidden not in scene_text, f"scene must not reference review/full-source asset: {forbidden}")
    for asset_id, layer in by_id.items():
        file_name = Path(str(layer["file"])).name
        require(f"home_area_launch_quality/v001/layers/{file_name}" in scene_text, f"scene missing v001 layer reference: {file_name}")

    print("OK: HomeArea launch_quality/v001 package validates as Godot review candidate, not final launch approval")


if __name__ == "__main__":
    main()
