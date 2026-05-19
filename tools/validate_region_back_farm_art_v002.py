from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "production/assets/regions/back_farm_art/v002"
MANIFEST = ART_DIR / "region_back_farm_art_v002_manifest.json"
SCENE = ROOT / "scenes/regions/region_back_farm.tscn"
WORLD_CONTROLLER = ROOT / "scripts/world/world_controller.gd"
CANVAS = (2000, 2000)
REQUIRED_IDS = {"ground", "path", "field_rows", "shed", "pond", "fence", "foreground_grass", "shadow", "light"}
GRAYBOX_NODES = {
    ("GroundBase", "TileMapLayer_Ground"),
    ("Field1", "TileMapLayer_Ground/FarmFields"),
    ("Field2", "TileMapLayer_Ground/FarmFields"),
    ("Field3", "TileMapLayer_Ground/FarmFields"),
    ("Field4", "TileMapLayer_Ground/FarmFields"),
    ("MainPath", "TileMapLayer_Path"),
    ("ShedBase", "YSortWorld/FarmStructures/ToolShed"),
    ("ShedRoof", "YSortWorld/FarmStructures/ToolShed"),
    ("PondBase", "YSortWorld/SmallPond"),
    ("ForegroundLeft", "ForegroundStatic"),
    ("ForegroundRight", "ForegroundStatic"),
}
REQUIRED_SCENE_NODES = {
    "ground": "BackFarmGroundArtV002",
    "path": "BackFarmPathArtV002",
    "field_rows": "BackFarmFieldRowsArtV002",
    "shed": "BackFarmShedArtV002",
    "pond": "BackFarmPondArtV002",
    "fence": "BackFarmFenceArtV002",
    "foreground_grass": "BackFarmForegroundGrassArtV002",
    "shadow": "BackFarmShadowArtV002",
    "light": "BackFarmLightArtV002",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def node_block(scene_text: str, name: str, parent: str | None = None) -> str:
    if parent is None:
        header = rf'\[node name="{re.escape(name)}" [^\]]*\]'
    else:
        header = rf'\[node name="{re.escape(name)}" [^\]]*parent="{re.escape(parent)}"[^\]]*\]'
    match = re.search(header + r".*?(?=\n\[node |\n\[connection |\Z)", scene_text, re.S)
    if match is None:
        location = f"{parent}/{name}" if parent else name
        fail(f"missing node: {location}")
    return match.group(0)


def require_image(path: Path, size: tuple[int, int] | None, label: str, needs_alpha: bool = False) -> Image.Image:
    require(path.exists(), f"missing {label}: {path.relative_to(ROOT).as_posix()}")
    image = Image.open(path).convert("RGBA")
    if size is not None:
        require(image.size == size, f"{label} size mismatch: expected {size}, got {image.size}")
    stat = ImageStat.Stat(image.getchannel("A"))
    require(stat.extrema[0][1] > 0, f"{label} must contain visible pixels")
    if needs_alpha:
        require(image.getchannel("A").getextrema()[0] < 255, f"{label} must preserve transparent pixels")
    return image


def validate_manifest() -> dict[str, dict[str, Any]]:
    require(MANIFEST.exists(), "missing BackFarm v002 manifest")
    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "BackFarm v002 manifest")
    require(manifest.get("region_id") == "Region_BackFarm", "BackFarm v002 region mismatch")
    require(manifest.get("package_id") == "back_farm_art_v002", "BackFarm v002 package mismatch")
    require(manifest.get("selected_route") == "single_full_source_then_split_layers", "BackFarm v002 route mismatch")
    require(manifest.get("status") == "runtime_structural_placeholder_not_launch_quality_v002", "BackFarm v002 must be marked as structural placeholder, not launch quality")
    require(manifest.get("runtime_replacement") is False, "BackFarm v002 must not claim final runtime replacement after launch-quality rejection")
    require(manifest.get("runtime_scene_reference_allowed") is True, "BackFarm v002 may stay scene-wired only as an active placeholder")
    require(manifest.get("active_runtime_placeholder") is True, "BackFarm v002 must record active placeholder usage")
    require(manifest.get("human_visual_approval_required") is True, "BackFarm v002 must require human visual approval before final promotion")
    require(manifest.get("launch_quality_approved") is False, "BackFarm v002 must not be launch-quality approved")
    blockers = manifest.get("launch_quality_blockers", [])
    require(isinstance(blockers, list) and len(blockers) >= 3, "BackFarm v002 must record launch-quality blockers")
    quality_gate = manifest.get("quality_gate", {})
    require(quality_gate.get("launch_status") == "rejected_not_launch_quality", "BackFarm v002 quality gate must record launch rejection")
    review = manifest.get("godot_review", {})
    require(review.get("final_promotion_allowed") is False, "BackFarm v002 godot_review must block final promotion")
    visual_report = ROOT / ".codex/reports/back_farm_v002_visual_review.md"
    require(visual_report.exists(), "BackFarm v002 requires visual rejection report")
    report_text = visual_report.read_text(encoding="utf-8")
    require("rejected_for_launch_quality_keep_as_structural_placeholder" in report_text, "BackFarm v002 visual report must reject launch quality")
    require("rejected_as_launch_art" in report_text, "BackFarm v002 visual report decision must reject launch art")
    source_assets = manifest.get("source_assets", [])
    require(source_assets and source_assets[0].get("sha256"), "BackFarm v002 source sha missing")
    source_sha = source_assets[0]["sha256"]
    require_image(ART_DIR / source_assets[0]["file"], CANVAS, "BackFarm v002 source")
    require_image(ART_DIR / source_assets[0]["review_file"], (1000, 1000), "BackFarm v002 source review")
    require_image(ART_DIR / manifest.get("runtime_preview", ""), CANVAS, "BackFarm v002 runtime preview")
    require_image(ART_DIR / manifest.get("contact_sheet", ""), None, "BackFarm v002 contact sheet")
    layers = manifest.get("required_layers")
    require(isinstance(layers, list), "BackFarm v002 required_layers must be a list")
    by_id = {str(layer.get("asset_id")): require_dict(layer, "layer record") for layer in layers if isinstance(layer, dict)}
    require(set(by_id) == REQUIRED_IDS, f"BackFarm v002 layer ids mismatch: {sorted(set(by_id))}")
    for asset_id, record in by_id.items():
        rel = str(record.get("file"))
        require(rel.startswith("layers/"), f"{asset_id} must live under layers/")
        require(rel.endswith("_v002.png"), f"{asset_id} must use v002 PNG")
        require(record.get("derived_from_source") is True, f"{asset_id} must be source-derived")
        require(record.get("source_sha256") == source_sha, f"{asset_id} source sha mismatch")
        require(record.get("source_rect_px"), f"{asset_id} missing source_rect_px")
        mask_file = str(record.get("mask_file"))
        require(mask_file.startswith("source/masks/") and mask_file.endswith("_mask.png"), f"{asset_id} mask path invalid")
        require((ART_DIR / mask_file).exists(), f"{asset_id} mask missing")
        size = require_dict(record.get("size_px"), f"{asset_id} size_px")
        image = require_image(ART_DIR / rel, (int(size["width"]), int(size["height"])), asset_id, needs_alpha=(asset_id != "ground"))
        if asset_id == "ground":
            require(image.size == CANVAS, "BackFarm ground must be full canvas")
        if asset_id in {"shadow", "light"}:
            require(image.size == CANVAS, f"{asset_id} overlay must be full canvas")
            require(image.getchannel("A").getextrema()[1] <= 90, f"{asset_id} alpha must stay subtle")
    return by_id


def validate_scene(by_id: dict[str, dict[str, Any]]) -> None:
    require(SCENE.exists(), "missing BackFarm scene")
    scene_text = SCENE.read_text(encoding="utf-8-sig")
    root = node_block(scene_text, "Region_BackFarm")
    require('metadata/art_package = "back_farm_art_v002"' in root, "BackFarm scene must record active v002 art package")
    require('metadata/art_status = "runtime_structural_placeholder_not_launch_quality_v002"' in root, "BackFarm scene must record v002 structural placeholder status")
    require('metadata/launch_quality_approved = false' in root, "BackFarm scene must block launch-quality approval metadata")
    require("back_farm_art/v001/region_back_farm_" not in scene_text, "BackFarm scene must not reference v001 art after v002 wiring")
    require("region_back_farm_full_composition_v002.png" not in scene_text, "BackFarm runtime must not reference v002 full source")
    require("region_back_farm_full_composition_v002_review.png" not in scene_text, "BackFarm runtime must not reference v002 review image")
    for asset_id, record in by_id.items():
        file_name = Path(str(record["file"])).name
        require(f"back_farm_art/v002/layers/{file_name}" in scene_text, f"scene missing BackFarm v002 art reference: {file_name}")
        node_block(scene_text, REQUIRED_SCENE_NODES[asset_id])
    for name, parent in GRAYBOX_NODES:
        block = node_block(scene_text, name, parent)
        require("visible = false" in block, f"{parent}/{name} must stay hidden")
    spawn = node_block(scene_text, "PlayerSpawn", "YSortWorld")
    require("position = Vector2(1000, 430)" in spawn, "BackFarm default spawn must stay on entry path")
    exit_block = node_block(scene_text, "ExitToHomeArea", "YSortWorld/Interactables")
    require('target_region_id = "Region_HomeArea"' in exit_block, "BackFarm exit target region mismatch")
    require('target_spawn_id = "home_area_from_back_farm"' in exit_block, "BackFarm exit target spawn mismatch")
    controller_text = WORLD_CONTROLLER.read_text(encoding="utf-8")
    require('"back_farm_default": Vector2(11000, 8430)' in controller_text, "WorldController back_farm_default spawn mismatch")


def main() -> None:
    by_id = validate_manifest()
    validate_scene(by_id)
    print("OK: Region_BackFarm v002 validates as active structural placeholder, not launch-quality art")


if __name__ == "__main__":
    main()
