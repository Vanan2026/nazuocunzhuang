from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "build_region_home_area_art_v001.py"
VALIDATOR = ROOT / "tools" / "validate_region_home_area_art_v001.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_builder_and_validator_contract() -> None:
    require(BUILDER.exists(), f"missing builder: {BUILDER}")
    require(VALIDATOR.exists(), f"missing validator: {VALIDATOR}")
    builder_text = BUILDER.read_text(encoding="utf-8")
    validator_text = VALIDATOR.read_text(encoding="utf-8")
    required_builder_fragments = [
        "region_home_area_art_v001_manifest.json",
        "visual_review_required_before_runtime_integration",
        "runtime_replacement",
        "region_home_area_base_full_v001.png",
        "region_home_area_light_overlay_v001.png",
    ]
    required_validator_fragments = [
        "REQUIRED_FILES",
        "base full plate must be full canvas 6144x4096",
        "art package must not claim runtime replacement",
        "OK: Region_HomeArea art v001 package validated",
    ]
    missing_builder = [fragment for fragment in required_builder_fragments if fragment not in builder_text]
    missing_validator = [fragment for fragment in required_validator_fragments if fragment not in validator_text]
    require(not missing_builder, f"builder missing fragments: {missing_builder}")
    require(not missing_validator, f"validator missing fragments: {missing_validator}")


if __name__ == "__main__":
    try:
        test_builder_and_validator_contract()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)

    print("OK: Region_HomeArea art v001 tool contract test passed")
