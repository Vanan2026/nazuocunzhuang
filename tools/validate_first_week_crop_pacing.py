from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "game/data/crops.json": [
        '"crop_id": "turnip_spring"',
        '"grow_days": 2',
    ],
    "tools/validate_first_week_crop_pacing.gd": [
        "first-week crop pacing runtime validation passed",
        "after two watered sleeps",
        "grow_days",
        "2",
    ],
    "tools/validate_task006_farm_plot.gd": [
        "range(2)",
        "after 2 watered days",
    ],
    "tools/validate_main_flow_crop_sleep_harvest.gd": [
        "range(2)",
        "after two watered sleeps",
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
    for relative_path, snippets in EXPECTED_SNIPPETS.items():
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
    print("OK: first-week crop pacing static contract validated")


if __name__ == "__main__":
    main()
