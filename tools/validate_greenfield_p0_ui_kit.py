from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STYLE_REFERENCE = "production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg"

REQUIRED_ASSETS = {
    "assets/ui/panels/ui_panel_paper_01.png": (512, 512),
    "assets/ui/panels/ui_panel_wood_01.png": (512, 512),
    "assets/ui/buttons/ui_button_normal.png": (256, 96),
    "assets/ui/buttons/ui_button_hover.png": (256, 96),
    "assets/ui/buttons/ui_button_pressed.png": (256, 96),
    "assets/ui/slots/ui_slot_item.png": (96, 96),
    "assets/ui/slots/ui_slot_selected.png": (96, 96),
    "assets/ui/tabs/ui_tab_normal.png": (160, 72),
    "assets/ui/tabs/ui_tab_active.png": (160, 72),
    "assets/ui/widgets/ui_scrollbar.png": (64, 256),
    "assets/ui/widgets/ui_checkbox_on.png": (64, 64),
    "assets/ui/widgets/ui_checkbox_off.png": (64, 64),
    "assets/ui/icons/ui_icon_coin.png": (64, 64),
    "assets/ui/icons/ui_icon_heart.png": (64, 64),
    "assets/ui/icons/ui_icon_weather_sun.png": (64, 64),
    "assets/ui/icons/ui_icon_weather_rain.png": (64, 64),
    "assets/ui/icons/ui_icon_bag.png": (64, 64),
    "assets/ui/icons/ui_icon_map.png": (64, 64),
    "assets/ui/icons/ui_icon_settings.png": (64, 64),
}

REQUIRED_COMPONENTS = [
    "ui/components/GFPanel.tscn",
    "ui/components/GFButton.tscn",
    "ui/components/GFItemSlot.tscn",
    "ui/components/GFTabBar.tscn",
    "ui/components/GFPanel.gd",
    "ui/components/GFButton.gd",
    "ui/components/GFItemSlot.gd",
    "ui/components/GFTabBar.gd",
    "tools/validate_greenfield_p0_ui_kit.gd",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _fail(message: str) -> None:
    raise AssertionError(message)


def _assert_contains(path: str, tokens: list[str]) -> None:
    text = _read(path)
    for token in tokens:
        if token not in text:
            _fail(f"{path} missing token: {token}")


def _validate_assets() -> None:
    manifest_path = ROOT / "assets/ui/greenfield_p0_ui_kit_manifest_v001.json"
    if not manifest_path.exists():
        _fail("missing UI kit manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("style_reference") != STYLE_REFERENCE:
        _fail("UI kit manifest must point to the current style mother")
    if manifest.get("launch_quality_approved") is not False:
        _fail("placeholder UI kit must not claim launch approval")
    if manifest.get("human_visual_approval_required") is not True:
        _fail("UI kit manifest must require human visual approval")
    manifest_paths = {item.get("path") for item in manifest.get("assets", [])}
    for relative_path, expected_size in REQUIRED_ASSETS.items():
        if relative_path not in manifest_paths:
            _fail(f"manifest missing asset: {relative_path}")
        path = ROOT / relative_path
        if not path.exists():
            _fail(f"missing UI asset: {relative_path}")
        with Image.open(path) as image:
            if image.size != expected_size:
                _fail(f"{relative_path} has size {image.size}, expected {expected_size}")
            if image.mode != "RGBA":
                _fail(f"{relative_path} must be RGBA")


def _validate_theme_and_components() -> None:
    _assert_contains(
        "ui/theme/GreenfieldTheme.gd",
        [
            "class_name GFTheme",
            "ui_panel_paper_01.png",
            "ui_panel_wood_01.png",
            "ui_button_normal.png",
            "ui_slot_selected.png",
            "apply_item_slot",
            "apply_tab_button",
            "build_texture_stylebox",
        ],
    )
    _assert_contains(
        "ui/theme/greenfield_theme.tres",
        [
            'type="Theme"',
            "ui_panel_paper_01.png",
            "ui_button_hover.png",
            "Button/styles/normal",
            "PanelContainer/styles/panel",
        ],
    )
    for component in REQUIRED_COMPONENTS:
        if not (ROOT / component).exists():
            _fail(f"missing reusable UI component: {component}")
    _assert_contains("ui/components/GFPanel.gd", ["class_name GFPanel", "GFTheme.apply_paper_panel"])
    _assert_contains("ui/components/GFButton.gd", ["class_name GFButton", "GFTheme.apply_button"])
    _assert_contains("ui/components/GFItemSlot.gd", ["class_name GFItemSlot", "GFTheme.apply_item_slot", "set_item"])
    _assert_contains("ui/components/GFTabBar.gd", ["class_name GFTabBar", "tab_selected", "GFTheme.apply_tab_button"])
    for scene in REQUIRED_COMPONENTS[:4]:
        _assert_contains(scene, ["res://ui/theme/greenfield_theme.tres"])


def _validate_current_ui_bridge() -> None:
    bridge = _read("game/scenes/ui/GreenfieldUITheme.gd")
    if "res://assets/art/greenfield_p0/ui/" in bridge:
        _fail("legacy GreenfieldUITheme must bridge to the canonical UI kit instead of old one-off UI textures")
    for token in [
        'preload("res://ui/theme/GreenfieldTheme.gd")',
        "apply_surface_panel",
        "apply_button",
        "apply_item_slot",
        "apply_tab_button",
    ]:
        if token not in bridge:
            _fail(f"GreenfieldUITheme bridge missing token: {token}")

    _assert_contains(
        "game/scenes/ui/InventoryUI.gd",
        [
            'preload("res://ui/theme/greenfield_theme.tres")',
            'preload("res://game/scenes/ui/GreenfieldUITheme.gd")',
            "GREENFIELD_UI_THEME.apply_surface_panel",
            "GREENFIELD_UI_THEME.apply_item_slot",
            "GREENFIELD_UI_THEME.apply_button",
            "GREENFIELD_UI_THEME.apply_tab_button",
            "record.get(\"icon\"",
            "selected_item_id",
            "Clear",
        ],
    )
    _assert_contains(
        "game/scenes/ui/InventoryUI.tscn",
        [
            'res://ui/theme/greenfield_theme.tres',
            "CategoryTabs",
            "columns = 5",
            "AmountRow",
            "No item selected",
        ],
    )


def main() -> None:
    _validate_assets()
    _validate_theme_and_components()
    _validate_current_ui_bridge()
    print("OK: Greenfield P0 UI kit validates")


if __name__ == "__main__":
    main()
