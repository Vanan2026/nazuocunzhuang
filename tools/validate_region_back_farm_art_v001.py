from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "production" / "assets" / "regions" / "back_farm_art" / "v001"
MANIFEST = ART_DIR / "region_back_farm_art_v001_manifest.json"
SCENE = ROOT / "scenes" / "regions" / "region_back_farm.tscn"
WORLD_CONTROLLER = ROOT / "scripts" / "world" / "world_controller.gd"
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


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    return image.convert("RGBA").getchannel("A").getbbox()


def alpha_stats(image: Image.Image) -> tuple[float, float, float, int]:
    alpha = image.convert("RGBA").getchannel("A")
    hist = alpha.histogram()
    total = image.width * image.height
    return hist[0] / total, sum(hist[1:255]) / total, hist[255] / total, alpha.getextrema()[1]


def validate_manifest() -> dict[str, dict[str, Any]]:
    require(MANIFEST.exists(), "missing BackFarm art manifest")
    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "BackFarm manifest")
    require(manifest.get("region_id") == "Region_BackFarm", "BackFarm manifest region mismatch")
    require(manifest.get("package_id") == "back_farm_art_v001", "BackFarm manifest package mismatch")
    require(manifest.get("runtime_replacement") is True, "BackFarm v001 must be a runtime replacement package")
    layers = manifest.get("required_layers")
    require(isinstance(layers, list), "BackFarm required_layers must be a list")
    by_id = {str(layer.get("asset_id")): require_dict(layer, "layer record") for layer in layers if isinstance(layer, dict)}
    require(set(by_id) == REQUIRED_IDS, f"BackFarm layer ids mismatch: {sorted(set(by_id))}")
    for asset_id, record in by_id.items():
        file_name = str(record.get("file"))
        require(file_name.endswith("_v001.png"), f"{asset_id} must use v001 PNG")
        path = ART_DIR / file_name
        require(path.exists(), f"missing BackFarm PNG: {file_name}")
        with Image.open(path) as raw:
            image = raw.convert("RGBA")
            size = require_dict(record.get("size_px"), f"{asset_id} size_px")
            require(image.size == (int(size["width"]), int(size["height"])), f"{asset_id} manifest size mismatch")
            require(alpha_bbox(image) is not None, f"{asset_id} has no visible pixels")
            transparent, semi, opaque, alpha_max = alpha_stats(image)
            if asset_id == "ground":
                require(image.size == CANVAS, "BackFarm ground must be full canvas")
                require(opaque > 0.85, "BackFarm ground must be mostly opaque")
            elif asset_id in {"shadow", "light"}:
                require(image.size == CANVAS, f"{asset_id} must be full canvas overlay")
                require(0 < alpha_max <= 90, f"{asset_id} must stay soft low alpha")
                require(semi > 0.001, f"{asset_id} must contain semi-transparent pixels")
            else:
                require(transparent > 0.08, f"{asset_id} must preserve transparent background")
    return by_id


def validate_scene(by_id: dict[str, dict[str, Any]]) -> None:
    require(SCENE.exists(), "missing BackFarm scene")
    scene_text = SCENE.read_text(encoding="utf-8-sig")
    require("鎸" not in scene_text and "鑿" not in scene_text and "鍚" not in scene_text, "BackFarm scene contains mojibake Chinese")
    root = node_block(scene_text, "Region_BackFarm")
    require('region_display_name = "后院菜园"' in root, "BackFarm display name must be clean Chinese")
    require('metadata/art_package = "back_farm_art_v001"' in root, "BackFarm scene must record active art package")
    require("world_offset = Vector2(10000, 8000)" in root, "BackFarm scene world_offset must not overlap HomeArea")
    for asset_id, record in by_id.items():
        file_name = str(record["file"])
        require(f"back_farm_art/v001/{file_name}" in scene_text, f"scene missing BackFarm art reference: {file_name}")
    for name, parent in GRAYBOX_NODES:
        block = node_block(scene_text, name, parent)
        require("visible = false" in block, f"{parent}/{name} must be hidden after BackFarm art replacement")
    for node_name in ("BackFarmGroundArtV001", "BackFarmPathArtV001", "BackFarmFieldRowsArtV001", "BackFarmShedArtV001", "BackFarmPondArtV001", "BackFarmFenceArtV001", "BackFarmForegroundGrassArtV001", "BackFarmShadowArtV001", "BackFarmLightArtV001"):
        node_block(scene_text, node_name)
    spawn = node_block(scene_text, "PlayerSpawn", "YSortWorld")
    require("position = Vector2(1000, 280)" in spawn, "BackFarm default spawn must be inside the entry path, not on y=0")
    exit_block = node_block(scene_text, "ExitToHomeArea", "YSortWorld/Interactables")
    require("position = Vector2(1000, 220)" in exit_block, "BackFarm exit hotspot must align with the revised entry path")
    require('interaction_hint = "按 E 返回庭院"' in exit_block, "BackFarm exit hint must be clean Chinese")
    for plot in ("FarmPlot0", "FarmPlot1", "FarmPlot2", "FarmPlot3"):
        block = node_block(scene_text, plot, "YSortWorld/Interactables")
        require('display_name = "菜地"' in block, f"{plot} display name must be clean Chinese")
        require('interaction_hint = "按 E 种植"' in block, f"{plot} hint must be clean Chinese")

    controller_text = WORLD_CONTROLLER.read_text(encoding="utf-8")
    require('"back_farm_default": Vector2(11000, 8280)' in controller_text, "WorldController back_farm_default spawn must match revised BackFarm PlayerSpawn")
    require('"back_farm_from_home": Vector2(11000, 8280)' in controller_text, "WorldController back_farm_from_home spawn must match revised BackFarm PlayerSpawn")


def main() -> None:
    by_id = validate_manifest()
    validate_scene(by_id)
    print("OK: Region_BackFarm v001 art package and scene integration validated")


if __name__ == "__main__":
    main()
