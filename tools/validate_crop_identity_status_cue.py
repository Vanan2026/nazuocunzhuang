from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/systems/farming/FarmPlot.gd": [
        "@onready var crop_status_cue: Label = get_node_or_null(\"CropStatusCue\")",
        "func get_crop_status_text() -> String:",
        "func get_crop_display_name() -> String:",
        "func _update_crop_status_cue() -> void:",
        "crop_status_cue.visible",
        "crop_status_cue.text = get_crop_status_text()",
        "_update_crop_status_cue()",
    ],
    "game/systems/farming/FarmPlot.tscn": [
        '[node name="CropStatusCue" type="Label" parent="."]',
        "visible = false",
        "horizontal_alignment = 1",
        "vertical_alignment = 1",
    ],
    "tools/validate_crop_identity_status_cue.gd": [
        "crop identity status cue runtime validation passed",
        "FarmPlots/FarmPlot1",
        "seed_strawberry",
        "CropStatusCue",
        "get_crop_status_text",
    ],
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    for relative_path, snippets in EXPECTED_SNIPPETS.items():
        path = ROOT / relative_path
        if not path.is_file():
            fail(f"missing file: {relative_path}")
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")
    print("OK: crop identity status cue static contract validated")


if __name__ == "__main__":
    main()
