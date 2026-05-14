from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_region_home_area_bake_outputs.py"


def test_candidate_output_validator_exists() -> None:
    assert VALIDATOR.exists(), f"missing validator: {VALIDATOR}"
    text = VALIDATOR.read_text(encoding="utf-8")
    required_fragments = [
        "region_home_area_bake_candidate_manifest.json",
        "region_home_area_bake_candidate_preview.png",
        "OK: Region_HomeArea bake candidate outputs validated",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert not missing, f"validator missing fragments: {missing}"


if __name__ == "__main__":
    try:
        test_candidate_output_validator_exists()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)

    print("OK: Region_HomeArea bake output validator test passed")
