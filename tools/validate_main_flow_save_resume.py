from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/autoload/SaveManager.gd": [
        "class_name SaveManager",
        "func save_game(",
        "func load_game(",
        "func apply_save_data(",
        "build_main_flow_save_data",
        "apply_main_flow_save_data",
    ],
    "game/scenes/Main.gd": [
        "func build_main_flow_save_data(",
        "func apply_main_flow_save_data(",
        "current_gameplay_scene_id",
        "current_spawn_id",
    ],
    "game/autoload/SceneRouter.gd": [
        "func get_save_data(",
        "func apply_save_data(",
        "current_scene_id",
        "current_spawn_id",
    ],
    "tools/validate_main_flow_save_resume.gd": [
        "fresh_save.load_game(fresh_main, TEST_SAVE_PATH)",
        "forest_edge",
        "from_yard",
        "resume_test_marker",
    ],
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    for relative_path, snippets in EXPECTED_FILES.items():
        path = ROOT / relative_path
        if not path.is_file():
            fail(f"missing file: {relative_path}")
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                fail(f"{relative_path} missing required snippet: {snippet}")
    print("OK: main-flow save resume static contract validated")


if __name__ == "__main__":
    main()
