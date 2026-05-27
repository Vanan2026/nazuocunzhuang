from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCENE_PATHS = [
    "game/scenes/ui/InventoryUI.tscn",
    "game/scenes/ui/InventoryScreen.tscn",
]

REQUIRED_SCENE_TOKENS = [
    "visible = false",
    "CategoryTabs",
    "ItemGrid",
    "columns = 5",
    "SelectedNameLabel",
    "SelectedDescriptionLabel",
    "SelectedMetaLabel",
    "AmountRow",
    "DecreaseButton",
    "IncreaseButton",
    "ClearButton",
    "SeedCountLabel",
    "CropCountLabel",
    "res://ui/theme/greenfield_theme.tres",
]

REQUIRED_SCRIPT_TOKENS = [
    "const CATEGORIES",
    '"id": "all"',
    '"id": "seed"',
    '"id": "crop"',
    '"id": "gift"',
    "data_registry.get(\"items\")",
    "record.get(\"icon\"",
    "_load_texture",
    "GREENFIELD_UI_THEME.apply_tab_button",
    "GREENFIELD_UI_THEME.apply_item_slot",
    "GREENFIELD_UI_THEME.apply_surface_panel",
    "increase_amount",
    "decrease_amount",
]

FORBIDDEN_SCRIPT_TOKENS = [
    "wood_64.png",
    "stone_64.png",
    "seed_turnip_64.png",
    "crop_turnip_64.png",
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


def _validate_scenes() -> None:
    for scene_path in SCENE_PATHS:
        if not (ROOT / scene_path).exists():
            _fail(f"missing inventory scene: {scene_path}")
        _assert_contains(scene_path, REQUIRED_SCENE_TOKENS)

    player_yard_scene = _read("game/scenes/world/PlayerYard.tscn")
    if "res://game/scenes/ui/InventoryUI.tscn" not in player_yard_scene:
        _fail("PlayerYard should keep the compatible InventoryUI instance")


def _validate_script() -> None:
    script = _read("game/scenes/ui/InventoryUI.gd")
    for token in REQUIRED_SCRIPT_TOKENS:
        if token not in script:
            _fail(f"InventoryUI.gd missing token: {token}")
    for token in FORBIDDEN_SCRIPT_TOKENS:
        if token in script:
            _fail(f"InventoryUI.gd must not hardcode item icon asset: {token}")


def _validate_items_data() -> None:
    items_path = ROOT / "game/data/items.json"
    records = json.loads(items_path.read_text(encoding="utf-8"))
    if len(records) < 20:
        _fail("items.json should provide at least 20 P0 inventory records")

    categories = set()
    for record in records:
        item_id = str(record.get("item_id", ""))
        icon = str(record.get("icon", ""))
        category = str(record.get("category", ""))
        if not item_id:
            _fail("items.json contains an empty item_id")
        if not icon.startswith("res://"):
            _fail(f"{item_id} icon should use a res:// path")
        icon_path = ROOT / icon.replace("res://", "")
        if not icon_path.exists():
            _fail(f"{item_id} icon asset is missing: {icon}")
        categories.add(category)

    for category in ["seed", "crop", "food", "material"]:
        if category not in categories:
            _fail(f"items.json missing category used by InventoryScreen: {category}")


def main() -> None:
    _validate_scenes()
    _validate_script()
    _validate_items_data()
    print("OK: Greenfield P0 Inventory Screen static validation passed")


if __name__ == "__main__":
    main()
