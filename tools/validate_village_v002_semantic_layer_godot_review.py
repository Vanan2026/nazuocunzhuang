from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPTURE_GD = ROOT / "tools" / "capture_village_v002_semantic_layer_godot_review.gd"
LAYER_MANIFEST = (
    ROOT
    / "production"
    / "assets"
    / "regions"
    / "village_world2d"
    / "v001"
    / "03_layer_export"
    / "v002_inherited"
    / "layer_export_manifest_v002.json"
)
VISUAL_REVIEW = (
    ROOT
    / "production"
    / "assets"
    / "regions"
    / "village_world2d"
    / "v001"
    / "02_source_generation"
    / "v002_inherited_world_base_repaint"
    / "source_visual_review_v002.json"
)
REVIEW_REPORT = ROOT / ".codex" / "reports" / "village_v002_semantic_layer_godot_review_2026-05-26.md"
SCREENSHOT_DIR = ROOT / ".codex" / "village_v002_semantic_layer_godot_review"
SCREENSHOT_FILES = [
    SCREENSHOT_DIR / "01_village_v002_semantic_overview.png",
    SCREENSHOT_DIR / "02_village_v002_old_maple_occlusion_focus.png",
    SCREENSHOT_DIR / "03_village_v002_notice_stall_focus.png",
    SCREENSHOT_DIR / "04_village_v002_east_continuity_focus.png",
    SCREENSHOT_DIR / "05_village_v002_inherited_edge_focus.png",
    SCREENSHOT_DIR / "06_village_v002_player_scale_focus.png",
]
TASK_PATHS = [
    ROOT / ".codex" / "tasks" / "open" / "2026-05-26-village-v002-semantic-layer-godot-review.md",
    ROOT / ".codex" / "tasks" / "done" / "2026-05-26-village-v002-semantic-layer-godot-review.md",
]

REQUIRED_CAPTURE_TOKENS = [
    'DEFAULT_OUTPUT_DIR := "res://.codex/village_v002_semantic_layer_godot_review"',
    'LAYER_MANIFEST_PATH := "res://production/assets/regions/village_world2d/v001/03_layer_export/v002_inherited/layer_export_manifest_v002.json"',
    'MOUNTAIN_HUT_LAYER_MANIFEST_PATH := "res://production/assets/regions/mountain_hut_world2d/v001/03_layer_export/layer_export_manifest.json"',
    '"01_village_v002_semantic_overview.png"',
    '"02_village_v002_old_maple_occlusion_focus.png"',
    '"03_village_v002_notice_stall_focus.png"',
    '"04_village_v002_east_continuity_focus.png"',
    '"05_village_v002_inherited_edge_focus.png"',
    '"06_village_v002_player_scale_focus.png"',
    "_capture_east_continuity_focus",
    "_capture_inherited_edge_focus",
    "_capture_player_scale_focus",
    "VillageV002SemanticLayerReview",
    "MountainHutSemanticLayerReference",
    "_install_semantic_layers",
    "_load_mountain_hut_reference_manifest",
    "_hide_existing_generated_layers",
    "_load_png_texture",
    "v002_semantic_layers_exported_pending_review",
    "v004_semantic_layers_exported_pending_review",
    "runtime_replacement",
    "launch_quality_approved",
    "ForegroundOcclusion",
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
    raise AssertionError("missing Village v002 semantic layer Godot review task record")


def main() -> None:
    capture_text = read(CAPTURE_GD)
    read(LAYER_MANIFEST)
    read(VISUAL_REVIEW)
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
    require("01_village_v002_semantic_overview.png" in report_text, "review report must list overview screenshot")
    require("02_village_v002_old_maple_occlusion_focus.png" in report_text, "review report must list old-maple screenshot")
    require("03_village_v002_notice_stall_focus.png" in report_text, "review report must list notice/stall screenshot")
    require("04_village_v002_east_continuity_focus.png" in report_text, "review report must list east-continuity screenshot")
    require("05_village_v002_inherited_edge_focus.png" in report_text, "review report must list inherited-edge screenshot")
    require("06_village_v002_player_scale_focus.png" in report_text, "review report must list player-scale screenshot")
    require("old-maple foreground occlusion" in report_text, "review report must discuss old-maple foreground occlusion")
    require("player scale/perspective" in report_text, "review report must discuss player scale/perspective")
    require("soft inherited edge" in report_text, "review report must discuss soft inherited edge")
    require("not launch-quality approval" in report_text, "review report must keep the verdict conservative")
    require("Village v002 semantic layer Godot review" in task_text, "task record should describe the review scope")
    print("OK: Village v002 semantic layer Godot review static validation passed")


if __name__ == "__main__":
    main()
