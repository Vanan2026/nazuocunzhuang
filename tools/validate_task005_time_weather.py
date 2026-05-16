from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = {
    "game/autoload/TimeManager.gd": [
        "const SEASONS",
        "const DAYS_PER_SEASON: int = 28",
        "const DAY_START_HOUR: int = 6",
        "func sleep_to_next_day(",
        "func get_current_season(",
        "func get_time_text(",
        "signal date_changed",
    ],
    "game/autoload/WeatherManager.gd": [
        "const WEATHER_IDS",
        "func advance_to_next_day(",
        "func should_auto_water_today(",
        "var auto_water_today: bool",
        "tomorrow_weather_changed.emit",
    ],
    "game/entities/interactable/BedInteractable.gd": [
        'extends "res://game/entities/interactable/Interactable.gd"',
        "class_name BedInteractable",
        "func on_interact(",
        "sleep_to_next_day",
        "advance_to_next_day",
    ],
    "game/scenes/ui/TimeWeatherHUD.gd": [
        "extends CanvasLayer",
        "class_name TimeWeatherHUD",
        "func bind_managers(",
        "func refresh(",
        "SeasonLabel",
        "WeatherLabel",
    ],
    "game/scenes/ui/TimeWeatherHUD.tscn": [
        '[node name="TimeWeatherHUD" type="CanvasLayer"]',
        '[node name="SeasonLabel"',
        '[node name="DayLabel"',
        '[node name="TimeLabel"',
        '[node name="WeatherLabel"',
    ],
    "game/scenes/world/PlayerYard.tscn": [
        "res://game/autoload/TimeManager.gd",
        "res://game/autoload/WeatherManager.gd",
        "res://game/entities/interactable/BedInteractable.gd",
        "res://game/scenes/ui/TimeWeatherHUD.tscn",
        '[node name="TimeManager"',
        '[node name="WeatherManager"',
        '[node name="TimeWeatherHUD"',
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

    print("OK: validated Task 005 time/weather file contract")


if __name__ == "__main__":
    main()
