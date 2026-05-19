from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_RUNTIME_FILES = [
    "project.godot",
    "scenes/regions/region_home_area.tscn",
    "scenes/world/world.tscn",
    "scripts/core/audio_manager.gd",
    "scripts/interaction_component.gd",
    "scripts/main.gd",
    "scripts/props/interactable_prop.gd",
    "scripts/ui/ui_manager.gd",
    "scripts/world/backyard_entrance.gd",
    "scripts/world/interaction_hint_ui.gd",
    "scripts/world/region.gd",
    "scripts/world/scene_exit.gd",
    "scripts/world/scene_exit_v2.gd",
    "scripts/world/scene_switch_area.gd",
    "scripts/world/veranda_rest_area.gd",
    "scripts/world/world_controller.gd",
    "scripts/world/yard_interactable.gd",
]

FORBIDDEN_MARKERS = [
    "鎸",
    "搴",
    "閭",
    "锛",
    "銆",
    "鈥",
    "鈮",
    "�",
]

QUESTIONABLE_PATTERNS = [
    re.compile(r"\?\s*E\b"),
    re.compile(r"\?{2,}"),
]

ALLOWED_QUESTION_MARK_SNIPPETS = {
    "scripts/npc_manager.gd": ["???"],
}


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def scan_file(path: Path) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        return [f"{rel}: cannot decode as UTF-8: {exc}"]
    findings: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for marker in FORBIDDEN_MARKERS:
            if marker in line:
                findings.append(f"{rel}:{line_no}: mojibake marker {marker!r}: {line.strip()}")
        for pattern in QUESTIONABLE_PATTERNS:
            if pattern.search(line):
                allowed = any(snippet in line for snippet in ALLOWED_QUESTION_MARK_SNIPPETS.get(rel, []))
                if not allowed:
                    findings.append(f"{rel}:{line_no}: suspicious question-mark mojibake: {line.strip()}")
    return findings


def main() -> None:
    missing = [rel for rel in ACTIVE_RUNTIME_FILES if not (ROOT / rel).exists()]
    require(not missing, f"active runtime encoding check references missing files: {missing}")

    findings: list[str] = []
    for rel in ACTIVE_RUNTIME_FILES:
        findings.extend(scan_file(ROOT / rel))

    if findings:
        print("FAIL: active runtime files contain mojibake or suspicious screenshot text")
        for finding in findings[:80]:
            print(f"- {finding}")
        if len(findings) > 80:
            print(f"- ... {len(findings) - 80} more findings")
        raise SystemExit(1)

    print("OK: active runtime text is UTF-8 clean for HomeArea screenshots")


if __name__ == "__main__":
    main()