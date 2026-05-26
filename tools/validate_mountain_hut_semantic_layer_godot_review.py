from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPTURE_GD = ROOT / "tools" / "capture_mountain_hut_semantic_layer_godot_review.gd"
LAYER_MANIFEST = ROOT / "production" / "assets" / "regions" / "mountain_hut_world2d" / "v001" / "03_layer_export" / "layer_export_manifest.json"
VILLAGE_LAYER_MANIFEST = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001" / "03_layer_export" / "layer_export_manifest.json"
VILLAGE_V002_LAYER_MANIFEST = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001" / "03_layer_export" / "v002_inherited" / "layer_export_manifest_v002.json"
REVIEW_REPORT = ROOT / ".codex" / "reports" / "mountain_hut_semantic_layer_godot_review_2026-05-26.md"
SCREENSHOT_DIR = ROOT / ".codex" / "mountain_hut_semantic_layer_godot_review"
SCREENSHOT_FILES = [
    SCREENSHOT_DIR / "01_mountain_hut_semantic_overview.png",
    SCREENSHOT_DIR / "02_hut_door_focus.png",
    SCREENSHOT_DIR / "03_foreground_occlusion_focus.png",
    SCREENSHOT_DIR / "04_village_mountain_hut_west_continuity.png",
    SCREENSHOT_DIR / "05_mountain_hut_player_scale_focus.png",
]
TASK_PATHS = [
    ROOT / ".codex" / "tasks" / "open" / "2026-05-26-mountain-hut-semantic-layer-godot-review.md",
    ROOT / ".codex" / "tasks" / "done" / "2026-05-26-mountain-hut-semantic-layer-godot-review.md",
]

REQUIRED_CAPTURE_TOKENS = [
    "DEFAULT_OUTPUT_DIR := \"res://.codex/mountain_hut_semantic_layer_godot_review\"",
    "MOUNTAIN_HUT_LAYER_MANIFEST_PATH := \"res://production/assets/regions/mountain_hut_world2d/v001/03_layer_export/layer_export_manifest.json\"",
    "VILLAGE_V002_LAYER_MANIFEST_PATH := \"res://production/assets/regions/village_world2d/v001/03_layer_export/v002_inherited/layer_export_manifest_v002.json\"",
    "\"01_mountain_hut_semantic_overview.png\"",
    "\"02_hut_door_focus.png\"",
    "\"03_foreground_occlusion_focus.png\"",
    "\"04_village_mountain_hut_west_continuity.png\"",
    "\"05_mountain_hut_player_scale_focus.png\"",
    "_capture_west_continuity_focus",
    "_capture_player_scale_focus",
    "MountainHutSemanticLayerReview",
    "VillageV002SemanticLayerReference",
    "_install_semantic_layers",
    "_load_village_v002_reference_manifest",
    "_hide_existing_generated_layers",
    "_load_png_texture",
    "v004_semantic_layers_exported_pending_review",
    "v002_semantic_layers_exported_pending_review",
    "runtime_replacement=false",
    "launch_quality_approved=false",
    "--check-only",
    "save_png",
    "HeadlessLifecycle.cleanup_and_quit",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def read_task() -> str:
    for path in TASK_PATHS:
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise AssertionError("missing MountainHut semantic layer Godot review task record")


def main() -> None:
    capture_text = read(CAPTURE_GD)
    read(LAYER_MANIFEST)
    read(VILLAGE_LAYER_MANIFEST)
    read(VILLAGE_V002_LAYER_MANIFEST)
    report_text = read(REVIEW_REPORT)
    task_text = read_task()
    for screenshot in SCREENSHOT_FILES:
        require(screenshot.exists(), f"missing review screenshot: {screenshot.relative_to(ROOT)}")
        require(screenshot.stat().st_size > 20_000, f"review screenshot is unexpectedly small: {screenshot.relative_to(ROOT)}")

    for token in REQUIRED_CAPTURE_TOKENS:
        require(token in capture_text, f"capture script missing token: {token}")
    require("review-only" in capture_text, "capture script must identify review-only integration")
    require("runtime_replacement=false" in report_text, "review report must keep runtime replacement blocked")
    require("launch_quality_approved=false" in report_text, "review report must keep launch approval blocked")
    require("01_mountain_hut_semantic_overview.png" in report_text, "review report must list overview screenshot")
    require("02_hut_door_focus.png" in report_text, "review report must list hut-door screenshot")
    require("03_foreground_occlusion_focus.png" in report_text, "review report must list foreground-occlusion screenshot")
    require("04_village_mountain_hut_west_continuity.png" in report_text, "review report must list west-continuity screenshot")
    require("05_mountain_hut_player_scale_focus.png" in report_text, "review report must list player-scale screenshot")
    require("adjacent-region continuity" in report_text, "review report must discuss adjacent-region continuity")
    require("not launch-quality approval" in report_text, "review report must keep the verdict conservative")
    require("MountainHut semantic layer Godot review" in task_text, "task record should describe the review scope")
    print("OK: MountainHut semantic layer Godot review static validation passed")


if __name__ == "__main__":
    main()
