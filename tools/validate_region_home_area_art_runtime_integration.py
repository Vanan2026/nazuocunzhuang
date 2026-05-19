from __future__ import annotations

from validate_home_area_v006_godot_pre_review import main as validate_v006_godot_pre_review


def main() -> None:
    validate_v006_godot_pre_review()
    print("OK: current Region_HomeArea runtime art integration uses v006 controlled pre-review layers and keeps final approval blocked")


if __name__ == "__main__":
    main()