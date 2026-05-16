from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "tools" / "prepare_region_home_area_art_v002_base_plate.py"
VALIDATOR = ROOT / "tools" / "validate_region_home_area_art_v002.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_v002_tool_contract() -> None:
    require(PREPARE.exists(), f"missing v002 prepare tool: {PREPARE}")
    require(VALIDATOR.exists(), f"missing v002 validator: {VALIDATOR}")
    prepare_text = PREPARE.read_text(encoding="utf-8")
    validator_text = VALIDATOR.read_text(encoding="utf-8")
    required_prepare_fragments = [
        "home_area_art_v002",
        "visual_review_required_before_layer_split",
        "region_home_area_base_full_v002.png",
        "region_home_area_art_v002_preview.png",
        "Do not wire this single plate into runtime",
    ]
    required_validator_fragments = [
        "layer_split_ready",
        "v002 base plate must not claim runtime replacement",
        "manifest must require visual review before split",
        "OK: Region_HomeArea art v002 base plate package validated",
    ]
    missing_prepare = [fragment for fragment in required_prepare_fragments if fragment not in prepare_text]
    missing_validator = [fragment for fragment in required_validator_fragments if fragment not in validator_text]
    require(not missing_prepare, f"prepare tool missing fragments: {missing_prepare}")
    require(not missing_validator, f"validator missing fragments: {missing_validator}")


if __name__ == "__main__":
    try:
        test_v002_tool_contract()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)

    print("OK: Region_HomeArea art v002 tool contract test passed")
