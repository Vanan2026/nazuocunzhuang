from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPTURE_GD = ROOT / "tools" / "capture_village_v002_semantic_layer_godot_review.gd"
LAYER_MANIFEST = (
    ROOT
    / "production/assets/regions/village_world2d/v001/03_layer_export/v003_edge_continuity/layer_export_manifest_v003.json"
)
REVIEW_REPORT = ROOT / ".codex/reports/village_v003_semantic_layer_godot_review_2026-05-26.md"
SCREENSHOT_DIR = ROOT / ".codex/village_v003_semantic_layer_godot_review"
SCREENSHOT_FILES = [
    SCREENSHOT_DIR / "01_village_v003_semantic_overview.png",
    SCREENSHOT_DIR / "02_village_v003_old_maple_occlusion_focus.png",
    SCREENSHOT_DIR / "03_village_v003_notice_stall_focus.png",
    SCREENSHOT_DIR / "04_village_v003_east_continuity_focus.png",
    SCREENSHOT_DIR / "05_village_v003_inherited_edge_focus.png",
    SCREENSHOT_DIR / "06_village_v003_player_scale_focus.png",
]

REQUIRED_CAPTURE_TOKENS = [
    'V003_LAYER_MANIFEST_PATH := "res://production/assets/regions/village_world2d/v001/03_layer_export/v003_edge_continuity/layer_export_manifest_v003.json"',
    'V003_OUTPUT_DIR := "res://.codex/village_v003_semantic_layer_godot_review"',
    "v003_semantic_layers_exported_pending_review",
    "VillageV003SemanticLayerReview",
    "--v3",
    '"01_village_v003_semantic_overview.png"',
    '"05_village_v003_inherited_edge_focus.png"',
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    capture_text = read(CAPTURE_GD)
    read(LAYER_MANIFEST)
    report_text = read(REVIEW_REPORT)
    for screenshot in SCREENSHOT_FILES:
        require(screenshot.exists(), f"missing v003 review screenshot: {screenshot.relative_to(ROOT)}")
        require(screenshot.stat().st_size > 20_000, f"v003 review screenshot is unexpectedly small: {screenshot.relative_to(ROOT)}")
    for token in REQUIRED_CAPTURE_TOKENS:
        require(token in capture_text, f"capture script missing v003 token: {token}")
    require("runtime_replacement=false" in report_text, "v003 report must keep runtime replacement blocked")
    require("launch_quality_approved=false" in report_text, "v003 report must keep launch approval blocked")
    require("not launch-quality approval" in report_text, "v003 report must keep verdict conservative")
    require("edge continuity" in report_text, "v003 report must discuss edge continuity")
    require("05_village_v003_inherited_edge_focus.png" in report_text, "v003 report must list inherited-edge screenshot")
    print("OK: Village v003 semantic layer Godot review static validation passed")


if __name__ == "__main__":
    main()
