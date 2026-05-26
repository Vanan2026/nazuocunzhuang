from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPTURE_SCRIPT = ROOT / "tools" / "capture_outdoor_world_visual_calibration.gd"
OUTDOOR_SCRIPT = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"

REGION_IDS = [
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    capture_text = read(CAPTURE_SCRIPT)
    outdoor_text = read(OUTDOOR_SCRIPT)

    required_capture_tokens = [
        "VISUAL_REVIEW_REGION_IDS",
        "OUTPUT_FILENAMES",
        "REVIEW_HIDDEN_UI_NODE_NAMES",
        "outdoor_world_overview.png",
        "func _capture_overview",
        "func _capture_region_closeup",
        "func _validate_region_layout_contract",
        "func _validate_screenshot_image",
        "func _hide_persistent_review_ui",
        "--check-only",
        "--out=",
    ]
    for token in required_capture_tokens:
        require(token in capture_text, f"capture script missing token: {token}")

    for region_id in REGION_IDS:
        require(f'"{region_id}"' in capture_text, f"capture script should cover region: {region_id}")
        require(f'"{region_id}"' in outdoor_text, f"OutdoorWorld should still register region: {region_id}")

    required_outdoor_tokens = [
        "OUTDOOR_GROUND_FILL_NODE",
        "OUTDOOR_GROUND_FILL_COLOR",
        "REGION_OFFSETS",
        "REGION_SIZES",
        "GENERATED_REGION_TEXTURE_SCALE",
        "get_region_bounds",
        "func _compose_world_ground_fill",
    ]
    for token in required_outdoor_tokens:
        require(token in outdoor_text, f"OutdoorWorld visual layout missing token: {token}")

    print("OK: outdoor world visual calibration static contract validated")


if __name__ == "__main__":
    main()
