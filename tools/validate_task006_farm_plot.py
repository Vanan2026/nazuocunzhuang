from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/systems/farming/FarmPlot.gd": [
        'extends "res://game/entities/interactable/Interactable.gd"',
        "class_name FarmPlot",
        "enum PlotState",
        "func till(",
        "func plant_seed(",
        "func water(",
        "func advance_day(",
        "func harvest(",
        "func on_interact(",
        "func get_state_name(",
        "crop_harvested.emit",
    ],
    "game/systems/farming/FarmPlot.tscn": [
        '[node name="FarmPlot" type="Area2D"',
        "res://game/systems/farming/FarmPlot.gd",
        '[node name="CollisionShape2D"',
        '[node name="StateMarker"',
    ],
    "game/scenes/world/PlayerYard.tscn": [
        "res://game/autoload/DataRegistry.gd",
        "res://game/autoload/InventoryManager.gd",
        "res://game/systems/farming/FarmPlot.tscn",
        '[node name="DataRegistry"',
        '[node name="InventoryManager"',
        '[node name="FarmPlots"',
        '[node name="FarmPlot0"',
        '[node name="FarmPlot1"',
        '[node name="FarmPlot2"',
        '[node name="FarmPlot3"',
        '[node name="FarmPlot4"',
        '[node name="FarmPlot5"',
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

    print("OK: validated Task 006 farm plot file contract")


if __name__ == "__main__":
    main()
