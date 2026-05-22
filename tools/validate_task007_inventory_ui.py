from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/autoload/InventoryManager.gd": [
        "signal selected_item_changed",
        "var selected_item_id: String",
        "func set_selected_item(",
        "func get_selected_item_id(",
        "func get_inventory_snapshot(",
        "func get_items_by_category(",
    ],
    "game/scenes/ui/InventoryUI.gd": [
        "extends CanvasLayer",
        "class_name InventoryUI",
        "func bind_managers(",
        "func refresh(",
        "func select_item(",
        "func use_selected_on(",
        "ItemGrid",
        "SelectedNameLabel",
        "SelectedDescriptionLabel",
        "SeedCountLabel",
        "CropCountLabel",
    ],
    "game/scenes/ui/InventoryUI.tscn": [
        '[node name="InventoryUI" type="CanvasLayer"]',
        "res://game/scenes/ui/InventoryUI.gd",
        '[node name="ItemGrid"',
        '[node name="SelectedNameLabel"',
        '[node name="SelectedDescriptionLabel"',
        '[node name="SeedCountLabel"',
        '[node name="CropCountLabel"',
    ],
    "game/systems/farming/FarmPlot.gd": [
        "func plant_selected_seed(",
        "get_selected_item_id",
    ],
    "game/scenes/world/PlayerYard.gd": [
        "@onready var inventory_manager: Node = $InventoryManager",
        "@onready var data_registry: Node = $DataRegistry",
        "inventory_ui.bind_managers(inventory_manager, data_registry)",
    ],
    "game/scenes/world/PlayerYard.tscn": [
        '[node name="InventoryManager" type="Node"',
        '[node name="DataRegistry" type="Node"',
        "res://game/scenes/ui/InventoryUI.tscn",
        '[node name="InventoryUI"',
    ],
}

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
        for pattern in FORBIDDEN:
            if pattern.search(text):
                fail(f"{relative_path} contains forbidden gameplay term: {pattern.pattern}")

    tail_task_candidates = [
        ROOT / ".codex" / "tasks" / "open" / "2026-05-15-task-0075-tail-completion-pass.md",
        ROOT / ".codex" / "tasks" / "done" / "2026-05-15-task-0075-tail-completion-pass.md",
    ]
    tail_task = next((path for path in tail_task_candidates if path.is_file()), None)
    if tail_task is None:
        fail("missing Task 007.5 tail completion task record")
    tail_text = tail_task.read_text(encoding="utf-8")
    for phrase in ["Task 007.5", "Task 001-007", "编辑器", "PlayerYard", "HUD", "InventoryUI", "FarmPlot"]:
        if phrase not in tail_text:
            fail(f"tail completion task missing phrase: {phrase}")

    print("OK: validated Task 007 inventory UI file contract and tail checkpoint")


if __name__ == "__main__":
    main()
