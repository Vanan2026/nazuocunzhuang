from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_region_home_area_art_runtime_integration.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_validator_contract_mentions_art_v001_ground_path() -> None:
    require(VALIDATOR.exists(), f"missing validator: {VALIDATOR}")
    text = VALIDATOR.read_text(encoding="utf-8")
    required_fragments = [
        "GroundYardArtV001",
        "VillageRoadArtV001",
        "BackFarmPathArtV001",
        "metadata/art_integration_group",
        "OK: Region_HomeArea art v001 runtime ground/path integration validated",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    require(not missing, f"validator missing fragments: {missing}")


if __name__ == "__main__":
    try:
        test_validator_contract_mentions_art_v001_ground_path()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)

    print("OK: Region_HomeArea art runtime integration validator test passed")
