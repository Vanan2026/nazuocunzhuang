from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPTURE_GD = ROOT / "tools" / "capture_village_semantic_layer_godot_review.gd"
LAYER_MANIFEST = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001" / "03_layer_export" / "layer_export_manifest.json"
REVIEW_REPORT = ROOT / ".codex" / "reports" / "village_semantic_layer_godot_review_2026-05-24.md"
SCREENSHOT_DIR = ROOT / ".codex" / "village_semantic_layer_godot_review"
SCREENSHOT_FILES = [
    SCREENSHOT_DIR / "01_village_semantic_overview.png",
    SCREENSHOT_DIR / "02_old_maple_occlusion_focus.png",
    SCREENSHOT_DIR / "03_seed_stall_notice_focus.png",
    SCREENSHOT_DIR / "04_village_east_continuity_focus.png",
]
TASK_PATHS = [
    ROOT / ".codex" / "tasks" / "open" / "2026-05-24-village-semantic-layer-godot-review.md",
    ROOT / ".codex" / "tasks" / "done" / "2026-05-24-village-semantic-layer-godot-review.md",
]

REQUIRED_CAPTURE_TOKENS = [
    "DEFAULT_OUTPUT_DIR := \"res://.codex/village_semantic_layer_godot_review\"",
    "LAYER_MANIFEST_PATH := \"res://production/assets/regions/village_world2d/v001/03_layer_export/layer_export_manifest.json\"",
    "\"01_village_semantic_overview.png\"",
    "\"02_old_maple_occlusion_focus.png\"",
    "\"03_seed_stall_notice_focus.png\"",
    "\"04_village_east_continuity_focus.png\"",
    "_capture_east_continuity_focus",
    "MountainHut",
    "_install_semantic_layers",
    "_hide_existing_generated_layers",
    "_load_png_texture",
    "semantic_rework_exported_pending_review",
    "runtime_replacement",
    "launch_quality_approved",
    "VillageSemanticLayerReview",
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
    raise AssertionError("missing semantic layer Godot review task record")


def main() -> None:
    capture_text = read(CAPTURE_GD)
    read(LAYER_MANIFEST)
    report_text = read(REVIEW_REPORT)
    task_text = read_task()
    for screenshot in SCREENSHOT_FILES:
        require(screenshot.exists(), f"missing review screenshot: {screenshot.relative_to(ROOT)}")
        require(screenshot.stat().st_size > 20_000, f"review screenshot is unexpectedly small: {screenshot.relative_to(ROOT)}")

    for token in REQUIRED_CAPTURE_TOKENS:
        require(token in capture_text, f"capture script missing token: {token}")
    require("review-only" in capture_text, "capture script must identify review-only integration")
    require("runtime_replacement=false" in report_text, "review report must keep runtime replacement blocked")
    require("01_village_semantic_overview.png" in report_text, "review report must list overview screenshot")
    require("02_old_maple_occlusion_focus.png" in report_text, "review report must list old-maple screenshot")
    require("03_seed_stall_notice_focus.png" in report_text, "review report must list notice/stall screenshot")
    require("04_village_east_continuity_focus.png" in report_text, "review report must list east continuity screenshot")
    require("adjacent-region continuity" in report_text, "review report must discuss adjacent-region continuity")
    require("not industrial-grade" in report_text, "review report must keep the verdict conservative")
    require("Village semantic layer Godot review" in task_text, "task record should describe the review scope")
    print("OK: Village semantic layer Godot review static validation passed")


if __name__ == "__main__":
    main()
