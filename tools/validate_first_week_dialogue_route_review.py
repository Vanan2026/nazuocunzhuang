from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SNIPPETS = {
    "tools/capture_first_week_dialogue_route.gd": [
        "const OUTPUT_FILENAMES",
        "first_week_mailbox_dialogue.png",
        "first_week_bulletin_dialogue.png",
        "first_week_mika_rumor_dialogue.png",
        "--check-only",
        "DisplayServer.get_name() == \"headless\"",
        "_prepare_mailbox_dialogue",
        "_prepare_bulletin_dialogue",
        "_prepare_mika_rumor_dialogue",
        "_expect_current_objective",
        '"watered_first_crop_day1"',
        '"harvested_first_crop_day1"',
        '"shared_first_turnip_day1"',
        '"planted_aoi_strawberry_day1"',
        '"heard_npc_forest_edge"',
        "_capture_review_frame",
        "first-week dialogue route review",
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
    print("OK: first-week dialogue route review static contract validated")


if __name__ == "__main__":
    main()
