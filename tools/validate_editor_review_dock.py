from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SCRIPT = ROOT / "addons" / "village_layer_tool" / "village_layer_tool_plugin.gd"
PLUGIN_CFG = ROOT / "addons" / "village_layer_tool" / "plugin.cfg"


REQUIRED_SNIPPETS = [
    "const PROJECT_REVIEW_SCENES",
    "const VALIDATION_COMMANDS",
    "var review_dock: VBoxContainer",
    "var review_status_label: Label",
    "func _create_review_dock() -> void:",
    "func _open_review_scene(scene_path: String) -> void:",
    "func _copy_validation_commands() -> void:",
    "func _refresh_review_status() -> void:",
    "func _update_review_status(text: String) -> void:",
    "add_control_to_dock(DOCK_SLOT_RIGHT_UL, review_dock)",
    "remove_control_from_docks(review_dock)",
    "DisplayServer.clipboard_set",
    "FileAccess.open(\"res://.codex/status.md\", FileAccess.READ)",
]

REQUIRED_SCENES = [
    "res://game/scenes/Main.tscn",
    "res://game/scenes/world/PlayerYard.tscn",
    "res://scenes/dev/player_yard_layer_blueprint_review.tscn",
    "res://game/scenes/world/ForestEdge.tscn",
    "res://scenes/dev/greenfield_p0_reviews/greenfield_p0_region_review_all.tscn",
]

REQUIRED_COMMANDS = [
    "python tools\\\\validate_project_structure.py",
    "python tools\\\\validate_play_start_experience.py",
    "python tools\\\\validate_player_yard_layer_blueprint_review_scene.py",
    "python tools\\\\validate_yard_blockout_readability.py",
    "python tools\\\\validate_forest_edge_gameplay_layout.py",
    "git diff --check",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    require(PLUGIN_SCRIPT.exists(), f"Missing plugin script: {PLUGIN_SCRIPT}")
    require(PLUGIN_CFG.exists(), f"Missing plugin cfg: {PLUGIN_CFG}")

    source = PLUGIN_SCRIPT.read_text(encoding="utf-8")
    cfg = PLUGIN_CFG.read_text(encoding="utf-8")

    for snippet in REQUIRED_SNIPPETS:
        require(snippet in source, f"Missing review dock contract snippet: {snippet}")

    for scene_path in REQUIRED_SCENES:
        require(scene_path in source, f"Review dock missing scene shortcut: {scene_path}")

    for command in REQUIRED_COMMANDS:
        require(command in source, f"Review dock missing validation command: {command}")

    require('version="0.2.1"' in cfg, "Plugin version should be bumped to 0.2.1")
    require(
        "review" in cfg.lower() or "validation" in cfg.lower(),
        "Plugin description should mention review or validation workflow",
    )

    print("OK: editor review dock contract validates")


if __name__ == "__main__":
    main()
