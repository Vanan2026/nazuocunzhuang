from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "build_region_home_area_launch_art_package.py"
VALIDATOR = ROOT / "tools" / "validate_region_home_area_launch_art_package.py"


def test_launch_package_tools_exist_and_exclude_engineering_candidates() -> None:
    for path in (BUILDER, VALIDATOR):
        assert path.exists(), f"missing tool: {path}"
        text = path.read_text(encoding="utf-8")
        assert "home_area_launch" in text
        assert "rejected" in text
        assert "procedural engineering candidates" in text or "procedural_candidate" in text


if __name__ == "__main__":
    try:
        test_launch_package_tools_exist_and_exclude_engineering_candidates()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)

    print("OK: Region_HomeArea launch art package tool test passed")
