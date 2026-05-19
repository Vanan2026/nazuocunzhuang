from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VISUAL_SCRIPT = ROOT / "tools" / "validate_region_home_area_visual_walkthrough.gd"
TRANSITION_SCRIPT = ROOT / "tools" / "validate_scene_transition_spawn.gd"
HEADLESS_LIFECYCLE = ROOT / "tools" / "headless_lifecycle.gd"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _line_index(text: str, needle: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return index
    raise AssertionError(f"missing {needle!r}")


def _assert_common_watchdog_contract(text: str, script_name: str) -> None:
    required_fragments = [
        "HeadlessLifecycle",
        "const WATCHDOG_TIMEOUT_SECONDS",
        "var _check_only := false",
        "var _watchdog_timeout_seconds",
        "func _parse_validation_args()",
        '"--check-only"',
        '"--watchdog-timeout="',
        "func _start_watchdog()",
        "func _mark_progress(stage: String)",
        "func _finish_deferred(exit_code: int)",
        "validation watchdog timed out",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert not missing, f"{script_name} missing watchdog/check-only contract: {missing}"


def test_visual_walkthrough_has_watchdog_and_check_only_layer() -> None:
    text = _text(VISUAL_SCRIPT)

    _assert_common_watchdog_contract(text, VISUAL_SCRIPT.name)

    check_only_line = _line_index(text, "_run_check_only")
    first_capture_line = _line_index(text, '_capture_player_point("region_home_area_walk_01_default_spawn.png"')
    assert check_only_line < first_capture_line, "visual check-only must run before screenshot capture"


def test_transition_spawn_has_watchdog_and_check_only_layer() -> None:
    text = _text(TRANSITION_SCRIPT)

    _assert_common_watchdog_contract(text, TRANSITION_SCRIPT.name)

    check_only_line = _line_index(text, "_run_check_only")
    first_interact_line = _line_index(text, 'home_exit.call("on_interact", player)')
    assert check_only_line < first_interact_line, "transition check-only must run before live interaction flow"


def test_headless_lifecycle_helper_exists_for_scripted_quit_cleanup() -> None:
    text = _text(HEADLESS_LIFECYCLE)

    required_fragments = [
        "class_name HeadlessLifecycle",
        "static func load_packed_scene(path: String) -> PackedScene",
        "static func cleanup_and_quit(tree: SceneTree, exit_code: int = 0) -> void",
        "ResourceLoader.CACHE_MODE_IGNORE",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert not missing, f"{HEADLESS_LIFECYCLE.name} missing cleanup helper contract: {missing}"


if __name__ == "__main__":
    tests = [
        test_visual_walkthrough_has_watchdog_and_check_only_layer,
        test_transition_spawn_has_watchdog_and_check_only_layer,
        test_headless_lifecycle_helper_exists_for_scripted_quit_cleanup,
    ]
    failures: list[str] = []
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            failures.append(f"{test.__name__}: {exc}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)

    print("OK: validation script watchdog/check-only contract tests passed")
