from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "game/scenes/ui/HUD.tscn": [
        '[node name="HUD" type="CanvasLayer"]',
        "StatusPanel",
        "CoinLabel",
        "EnergyLabel",
        "HotbarPanel",
        "Slots",
        "res://game/scenes/ui/TimeWeatherHUD.gd",
    ],
    "game/scenes/ui/TimeWeatherHUD.tscn": [
        '[node name="TimeWeatherHUD" type="CanvasLayer"]',
        "StatusPanel",
        "CoinLabel",
        "EnergyLabel",
        "HotbarPanel",
        "Slots",
    ],
    "game/scenes/ui/TimeWeatherHUD.gd": [
        "class_name TimeWeatherHUD",
        "bind_managers",
        "bind_status_manager",
        "bind_inventory_manager",
        "_refresh_time_weather",
        "_refresh_status",
        "_refresh_hotbar",
        "ui_icon_coin.png",
        "ui_icon_heart.png",
        "ui_icon_bag.png",
        "GreenfieldUITheme.apply_hud_panel",
        "GreenfieldUITheme.apply_item_slot",
    ],
    "game/scenes/world/PlayerYard.gd": [
        "time_weather_hud.bind_managers(time_manager, weather_manager)",
        "time_weather_hud.bind_status_manager(game_state)",
        "time_weather_hud.bind_inventory_manager(inventory_manager, data_registry)",
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
    for relative_path, snippets in EXPECTED.items():
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

    text = (ROOT / "game/scenes/ui/HUD.tscn").read_text(encoding="utf-8")
    if "offset_top = 972.0" not in text:
        fail("HUD hotbar should remain low and edge-mounted")
    if "offset_top = 16.0" not in text:
        fail("HUD top panels should stay edge-mounted")

    print("OK: Greenfield P0 HUD static contract validates")


if __name__ == "__main__":
    main()
