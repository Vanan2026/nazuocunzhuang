from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]

GAME_SCENE = ROOT / "game/scenes/world/PlayerYard.tscn"
REGEN_SCRIPT = ROOT / "game/systems/restoration/RestorationTarget.gd"
GAMESTATE = ROOT / "game/autoload/GameState.gd"
SAVEMANAGER = ROOT / "game/autoload/SaveManager.gd"
RESTORE_DATA = ROOT / "game/data/restoration_targets.json"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require_file(path: Path) -> str:
    if not path.is_file():
        fail(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require_snippet(path: Path, snippet: str) -> None:
    text = require_file(path)
    if snippet not in text:
        fail(f"{path.relative_to(ROOT)} missing snippet: {snippet}")


def main() -> None:
    require_snippet(REGEN_SCRIPT, "class_name RestorationTarget")
    require_snippet(REGEN_SCRIPT, "func on_interact")
    require_snippet(REGEN_SCRIPT, "emit_restoration_completed")
    require_snippet(REGEN_SCRIPT, "func _consume_requirements")
    require_snippet(REGEN_SCRIPT, "func _apply_visual_state")

    scene_text = require_file(GAME_SCENE)
    if 'script = ExtResource("20_restoration_target")' not in scene_text:
        fail("PlayerYard.tscn should use RestorationTarget for OldWell node")
    if '[node name="GameState" type="Node" parent="."' not in scene_text:
        fail("PlayerYard.tscn should include local GameState node for scaffold runtime")
    if '[node name="EventBus" type="Node" parent="."' not in scene_text:
        fail("PlayerYard.tscn should include local EventBus node for restoration signal wiring")
    if '[node name="SaveManager" type="Node" parent="."' not in scene_text:
        fail("PlayerYard.tscn should include local SaveManager node for restoration payload support")

    require_snippet(GAMESTATE, "func is_restored(restoration_id: String)")
    require_snippet(GAMESTATE, "func get_player_money() -> int")
    require_snippet(GAMESTATE, "func set_restoration_states(next_states: Dictionary)")
    require_snippet(SAVEMANAGER, "func build_runtime_payload")
    require_snippet(SAVEMANAGER, "func apply_runtime_payload")

    if not RESTORE_DATA.is_file():
        fail("restoration_targets.json missing")
    restoration_data = json.loads(RESTORE_DATA.read_text(encoding="utf-8"))
    if not isinstance(restoration_data, list):
        fail("restoration_targets.json should be a list")

    old_well = None
    for item in restoration_data:
        if item.get("restoration_id") == "old_well":
            old_well = item
            break
    if old_well is None:
        fail("restoration_targets.json missing old_well entry")
    if int(old_well.get("required_money", -1)) <= 0:
        fail("old_well required_money should be > 0 for the MVP")
    required_items = old_well.get("required_items", [])
    needed = {str(entry.get("item_id")): int(entry.get("count", 0)) for entry in required_items if isinstance(entry, dict)}
    if needed.get("wood", 0) < 20 or needed.get("stone", 0) < 10:
        fail("old_well should require at least 20 wood and 10 stone")
    unlocks = {str(v) for v in old_well.get("unlocks", [])}
    if "yard_water_source" not in unlocks or "rumor_old_well_bell" not in unlocks:
        fail("old_well unlocks should include yard_water_source and rumor_old_well_bell")
    visual_states = old_well.get("visual_states", {})
    if "broken" not in visual_states or "repaired" not in visual_states:
        fail("old_well visual_states should define broken and repaired")

    print("OK: Task 010 restoration data/schema contract validated")


if __name__ == "__main__":
    main()
