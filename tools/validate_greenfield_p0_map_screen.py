from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SCENE_TOKENS = [
    "MapScreen",
    "visible = false",
    "res://game/scenes/ui/MapScreen.gd",
    "res://ui/theme/greenfield_theme.tres",
    "MapTexture",
    "Pins",
    "LocationList",
    "SelectedNumberLabel",
    "SelectedNameLabel",
    "SelectedStateLabel",
    "SelectedDescriptionLabel",
    "SelectedHintLabel",
    "SelectedNpcsLabel",
]

REQUIRED_SCRIPT_TOKENS = [
    "class_name MapScreen",
    "func open_map()",
    "func close_map()",
    "func select_location(",
    "func _rebuild_pins(",
    "func _rebuild_location_list(",
    "data_registry.get_map_locations(true)",
    "GREENFIELD_UI_THEME.apply_surface_panel",
    "GREENFIELD_UI_THEME.apply_tab_button",
    "GREENFIELD_UI_THEME.apply_button",
    "ASSET_PATHS.UI_MAP_VILLAGE_PAPER",
    "GreenfieldAssetPaths.gd",
    "ASSET_PATHS.load_texture",
]

REQUIRED_REGISTRY_TOKENS = [
    '"maps": {"path": "res://game/data/maps.json", "id_key": "map_id"}',
    "var maps: Dictionary = {}",
    "func get_map_location(",
    "func get_map_locations(",
    "func _validate_maps()",
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


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _fail(message: str) -> None:
    raise AssertionError(message)


def _assert_contains(path: str, tokens: list[str]) -> None:
    text = _read(path)
    for token in tokens:
        if token not in text:
            _fail(f"{path} missing token: {token}")
    for pattern in FORBIDDEN:
        if pattern.search(text):
            _fail(f"{path} contains forbidden gameplay term: {pattern.pattern}")


def _load_json_array(relative_path: str) -> list[dict]:
    path = ROOT / relative_path
    if not path.exists():
        _fail(f"missing JSON file: {relative_path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        _fail(f"{relative_path} must contain a JSON array")
    return data


def _validate_map_asset() -> None:
    asset_path = ROOT / "assets/ui/maps/ui_map_village_paper_01.png"
    if not asset_path.exists():
        _fail("missing paper map asset")
    with Image.open(asset_path) as image:
        if image.size != (1024, 640):
            _fail(f"map asset size should be 1024x640, got {image.size}")
        if image.mode != "RGBA":
            _fail("map asset should be RGBA")

    manifest_path = ROOT / "assets/ui/maps/greenfield_p0_map_assets_manifest_v001.json"
    if not manifest_path.exists():
        _fail("missing map asset manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("launch_quality_approved") is not False:
        _fail("map asset manifest must not claim launch approval")
    if manifest.get("human_visual_approval_required") is not True:
        _fail("map asset manifest must require human visual approval")


def _validate_maps_data() -> None:
    npcs = {record["npc_id"] for record in _load_json_array("game/data/npcs.json")}
    records = _load_json_array("game/data/maps.json")
    if len(records) < 10:
        _fail("maps.json should provide at least 10 P0 map locations")

    seen_ids: set[str] = set()
    seen_numbers: set[int] = set()
    locked_count = 0
    unlocked_count = 0
    for record in records:
        for field in ["map_id", "location_number", "name", "region_id", "scene_path", "position", "unlocked", "unlock_flag", "npc_ids", "description", "travel_hint"]:
            if field not in record:
                _fail(f"map record missing field: {field}")
        map_id = str(record["map_id"])
        if map_id in seen_ids:
            _fail(f"duplicate map_id: {map_id}")
        seen_ids.add(map_id)
        location_number = int(record["location_number"])
        if location_number <= 0 or location_number in seen_numbers:
            _fail(f"invalid or duplicate location_number: {location_number}")
        seen_numbers.add(location_number)
        position = record["position"]
        if not isinstance(position, list) or len(position) != 2:
            _fail(f"{map_id} position must be [x, y]")
        if not all(0.0 <= float(value) <= 1.0 for value in position):
            _fail(f"{map_id} position values should be normalized 0..1")
        if bool(record["unlocked"]):
            unlocked_count += 1
        else:
            locked_count += 1
            if not str(record["unlock_flag"]):
                _fail(f"locked map {map_id} should define unlock_flag")
        for npc_id in record["npc_ids"]:
            if str(npc_id) not in npcs:
                _fail(f"{map_id} references missing npc: {npc_id}")
        if not str(record["description"]).strip():
            _fail(f"{map_id} should have description")

    if locked_count < 3 or unlocked_count < 3:
        _fail("maps.json should include both locked and unlocked locations")


def main() -> None:
    _assert_contains("game/scenes/ui/MapScreen.tscn", REQUIRED_SCENE_TOKENS)
    _assert_contains("game/scenes/ui/MapScreen.gd", REQUIRED_SCRIPT_TOKENS)
    _assert_contains("game/autoload/DataRegistry.gd", REQUIRED_REGISTRY_TOKENS)
    _validate_map_asset()
    _validate_maps_data()
    print("OK: Greenfield P0 Map Screen static validation passed")


if __name__ == "__main__":
    main()
