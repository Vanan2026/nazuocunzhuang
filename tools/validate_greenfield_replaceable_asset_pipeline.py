from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
V002_MANIFEST = ROOT / "production/assets/external_gpt_handoff/greenfield_p0/v002/asset_request_manifest.json"

REQUIRED_DIRS = [
    "assets/scenes/home_area",
    "assets/ui/panels",
    "assets/ui/buttons",
    "assets/ui/icons",
    "assets/ui/slots",
    "assets/ui/tabs",
    "assets/ui/widgets",
    "assets/ui/maps",
    "assets/ui/screens",
    "assets/characters/player",
    "game/data",
    "game/scenes/world",
    "game/scenes/ui",
    "game/systems/assets",
    "docs",
]

REQUIRED_SCENES = [
    "game/scenes/world/HomeArea.tscn",
    "game/scenes/ui/HUD.tscn",
    "game/scenes/ui/InventoryScreen.tscn",
    "game/scenes/ui/MapScreen.tscn",
    "game/scenes/ui/DialogueScreen.tscn",
    "game/scenes/ui/SettingsScreen.tscn",
]

REQUIRED_DOCS = [
    "docs/ART_BIBLE.md",
    "docs/ASSET_MANIFEST.md",
    "docs/CODEX_TASKS.md",
    "docs/MISSING_ASSETS_REPORT.md",
    "docs/GREENFIELD_P0_GPT_ASSET_PRODUCTION_BRIEF.md",
]

FORBIDDEN_DIRECT_UI_PATH_TOKENS = {
    "game/scenes/ui/MapScreen.gd": [
        "res://assets/ui/maps/ui_map_village_paper_01.png",
        "MAP_TEXTURE_PATH",
    ],
    "game/scenes/ui/SettingsScreen.gd": [
        "res://assets/ui/screens/ui_settings_paper_preview.png",
    ],
}


def _fail(message: str) -> None:
    raise AssertionError(message)


def _read(path: str) -> str:
    full_path = ROOT / path
    if not full_path.exists():
        _fail(f"missing file: {path}")
    return full_path.read_text(encoding="utf-8")


def _validate_structure() -> None:
    for path in REQUIRED_DIRS:
        if not (ROOT / path).is_dir():
            _fail(f"missing required directory: {path}")
    for path in REQUIRED_SCENES + REQUIRED_DOCS:
        if not (ROOT / path).exists():
            _fail(f"missing required file: {path}")


def _validate_v002_paths() -> None:
    if not V002_MANIFEST.exists():
        _fail("missing v002 external asset manifest")
    manifest = json.loads(V002_MANIFEST.read_text(encoding="utf-8"))
    report = _read("docs/MISSING_ASSETS_REPORT.md")
    seen_paths: set[str] = set()
    for batch in manifest.get("batches", []):
        assets = batch.get("assets", [])
        if len(assets) > int(manifest.get("rules", {}).get("max_assets_per_batch", 12)):
            _fail(f"{batch.get('batch_id')} exceeds max small-batch size")
        for asset in assets:
            final_path = str(asset.get("final_runtime_path", ""))
            if not final_path:
                _fail(f"{asset.get('asset_id')} missing final_runtime_path")
            if final_path in seen_paths:
                _fail(f"duplicate final_runtime_path: {final_path}")
            seen_paths.add(final_path)
            full_path = ROOT / final_path
            if not full_path.exists():
                _fail(f"formal runtime placeholder is missing: {final_path}")
            if final_path not in report:
                _fail(f"MISSING_ASSETS_REPORT should list {final_path}")
            if full_path.suffix.lower() == ".png":
                expected_size = tuple(asset.get("expected_size", []))
                with Image.open(full_path) as image:
                    if expected_size and image.size != expected_size:
                        _fail(f"{final_path} expected {expected_size}, got {image.size}")
                    if image.mode != "RGBA":
                        _fail(f"{final_path} should be RGBA for stable Godot replacement")


def _validate_scene_contracts() -> None:
    home_area = _read("game/scenes/world/HomeArea.tscn")
    for token in ["BaseLayer", "BaseSprite", "YSortObjects", "ForegroundOcclusion", "CollisionLayer", "InteractionPoints"]:
        if token not in home_area:
            _fail(f"HomeArea missing required layer node: {token}")

    settings = _read("game/scenes/ui/SettingsScreen.tscn")
    for token in ["MusicSlider", "SfxSlider", "AmbienceSlider", "FullscreenCheckBox", "LanguageOption", "SaveButton", "CancelButton"]:
        if token not in settings:
            _fail(f"SettingsScreen missing required control: {token}")


def _validate_centralized_paths() -> None:
    registry = _read("game/systems/assets/GreenfieldAssetPaths.gd")
    for token in [
        "UI_MAP_VILLAGE_PAPER",
        "UI_SETTINGS_PAPER_PREVIEW",
        "HOME_AREA_BASE",
        "HOME_AREA_FOREGROUND_OCCLUSION",
        "static func item_icon_path",
        "static func load_texture",
    ]:
        if token not in registry:
            _fail(f"GreenfieldAssetPaths missing token: {token}")

    theme = _read("ui/theme/GreenfieldTheme.gd")
    for token in ["PAPER_PANEL_TEXTURE", "BUTTON_NORMAL_TEXTURE", "CHECKBOX_ON_TEXTURE", "static func apply_slider"]:
        if token not in theme:
            _fail(f"GreenfieldTheme missing centralized UI token: {token}")

    for path, forbidden_tokens in FORBIDDEN_DIRECT_UI_PATH_TOKENS.items():
        text = _read(path)
        for token in forbidden_tokens:
            if token in text:
                _fail(f"{path} should use GreenfieldAssetPaths instead of direct token {token}")


def _validate_data_driven_items() -> None:
    items = json.loads((ROOT / "game/data/items.json").read_text(encoding="utf-8"))
    if len(items) < 20:
        _fail("items.json should keep at least 20 P0 items")
    for item in items:
        item_id = str(item.get("item_id", ""))
        icon = str(item.get("icon", ""))
        if not item_id or not icon.startswith("res://"):
            _fail(f"item {item_id} has invalid icon path")
        if not (ROOT / icon.replace("res://", "")).exists():
            _fail(f"item icon file missing for {item_id}: {icon}")


def _validate_no_forbidden_gameplay_terms() -> None:
    combined = "\n".join(
        _read(path)
        for path in [
            "game/scenes/ui/SettingsScreen.gd",
            "game/scenes/ui/SettingsScreen.tscn",
            "game/systems/assets/GreenfieldAssetPaths.gd",
            "docs/MISSING_ASSETS_REPORT.md",
        ]
    )
    for pattern in [r"\bcombat\b", r"\bmonster\b", r"\bdamage\b", r"\bweapon\b", r"\bhp\b", r"\bkill\b", r"\bloot\b"]:
        if re.search(pattern, combined, re.IGNORECASE):
            _fail(f"new Greenfield pipeline files contain forbidden gameplay term: {pattern}")


def main() -> None:
    _validate_structure()
    _validate_v002_paths()
    _validate_scene_contracts()
    _validate_centralized_paths()
    _validate_data_driven_items()
    _validate_no_forbidden_gameplay_terms()
    print("OK: Greenfield replaceable asset pipeline validates")


if __name__ == "__main__":
    main()
