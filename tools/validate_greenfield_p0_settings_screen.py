from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SCENE_TOKENS = [
    "SettingsScreen",
    "visible = false",
    "res://game/scenes/ui/SettingsScreen.gd",
    "res://ui/theme/greenfield_theme.tres",
    "SideTabs",
    "AudioTab",
    "DisplayTab",
    "LanguageTab",
    "SaveTab",
    "MusicSlider",
    "SfxSlider",
    "AmbienceSlider",
    "FullscreenCheckBox",
    "SoftLightCheckBox",
    "ResolutionOption",
    "LanguageOption",
    "PreviewTexture",
    "SaveButton",
    "CancelButton",
]

REQUIRED_SCRIPT_TOKENS = [
    "class_name SettingsScreen",
    "func open_settings()",
    "func close_settings()",
    "func set_section(",
    "func get_settings_snapshot()",
    "GREENFIELD_UI_THEME.apply_surface_panel",
    "GREENFIELD_UI_THEME.apply_tab_button",
    "GREENFIELD_UI_THEME.apply_checkbox",
    "GREENFIELD_UI_THEME.apply_slider",
    "ASSET_PATHS.UI_SETTINGS_PAPER_PREVIEW",
    "ASSET_PATHS.load_texture",
]

REQUIRED_THEME_TOKENS = [
    "CHECKBOX_ON_TEXTURE",
    "CHECKBOX_OFF_TEXTURE",
    "static func apply_checkbox",
    "static func apply_slider",
]

FORBIDDEN = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bcombat\b",
        r"\bmonster\b",
        r"\bdamage\b",
        r"\bweapon\b",
        r"\bhp\b",
        r"\bkill\b",
        r"\bloot\b",
    ]
]


def _fail(message: str) -> None:
    raise AssertionError(message)


def _read(path: str) -> str:
    full_path = ROOT / path
    if not full_path.exists():
        _fail(f"missing file: {path}")
    return full_path.read_text(encoding="utf-8")


def _assert_contains(path: str, tokens: list[str]) -> None:
    text = _read(path)
    for token in tokens:
        if token not in text:
            _fail(f"{path} missing token: {token}")
    for pattern in FORBIDDEN:
        if pattern.search(text):
            _fail(f"{path} contains forbidden gameplay term: {pattern.pattern}")


def _validate_settings_asset() -> None:
    asset_path = ROOT / "assets/ui/screens/ui_settings_paper_preview.png"
    if not asset_path.exists():
        _fail("missing settings preview placeholder at formal runtime path")
    with Image.open(asset_path) as image:
        if image.size != (1280, 720):
            _fail(f"settings preview should be 1280x720, got {image.size}")
        if image.mode != "RGBA":
            _fail("settings preview should be RGBA")

    manifest_path = ROOT / "assets/ui/screens/greenfield_p0_settings_screen_assets_manifest_v001.json"
    if not manifest_path.exists():
        _fail("missing settings screen asset manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("launch_quality_approved") is not False:
        _fail("settings screen asset manifest must not claim launch approval")
    if manifest.get("human_visual_approval_required") is not True:
        _fail("settings screen asset manifest must require human visual approval")
    if manifest.get("assets", {}).get("settings_paper_preview") != "assets/ui/screens/ui_settings_paper_preview.png":
        _fail("settings screen manifest must point to the formal runtime path")


def main() -> None:
    _assert_contains("game/scenes/ui/SettingsScreen.tscn", REQUIRED_SCENE_TOKENS)
    _assert_contains("game/scenes/ui/SettingsScreen.gd", REQUIRED_SCRIPT_TOKENS)
    _assert_contains("ui/theme/GreenfieldTheme.gd", REQUIRED_THEME_TOKENS)
    _assert_contains("game/scenes/ui/GreenfieldUITheme.gd", ["static func apply_checkbox", "static func apply_slider"])
    _assert_contains("game/systems/assets/GreenfieldAssetPaths.gd", ["UI_SETTINGS_PAPER_PREVIEW", "static func load_texture"])
    _validate_settings_asset()
    print("OK: Greenfield P0 Settings Screen static validation passed")


if __name__ == "__main__":
    main()
