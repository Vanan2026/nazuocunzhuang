from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_MAIN_SCENE = "res://game/scenes/Main.tscn"
LEGACY_WORLD_SCENE = "res://scenes/world/world.tscn"


REQUIRED_FILES = [
    ".codex/status.md",
    ".codex/context/project_state.md",
    ".codex/context/roadmap.md",
    ".codex/context/decisions.md",
    ".codex/context/agent_workflow.md",
    ".codex/context/agent_roles.md",
    ".codex/learnings/errors.md",
    ".codex/learnings/improvements.md",
    ".codex/tasks/open/task_template.md",
    ".codex/tasks/open/agent_handoff_template.md",
]


DOCS_WITH_MAIN_ENTRY_CONTRACT = [
    ".codex/context/agent_workflow.md",
    ".codex/tasks/open/task_template.md",
]


OUTDATED_CURRENT_ENTRY_PHRASES = [
    f"Current entry: `{LEGACY_WORLD_SCENE}`",
    f"current entry at `{LEGACY_WORLD_SCENE}`",
    f"Keep the current main entry at `{LEGACY_WORLD_SCENE}`",
]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def validate_required_files(errors: list[str]) -> None:
    for relative_path in REQUIRED_FILES:
        path = ROOT / relative_path
        if not path.exists():
            errors.append(f"missing required process memory file: {relative_path}")


def validate_main_entry_contract(errors: list[str]) -> None:
    for relative_path in DOCS_WITH_MAIN_ENTRY_CONTRACT:
        text = read_text(relative_path)
        if CURRENT_MAIN_SCENE not in text:
            errors.append(f"{relative_path} must name current main scene {CURRENT_MAIN_SCENE}")
        for phrase in OUTDATED_CURRENT_ENTRY_PHRASES:
            if phrase in text:
                errors.append(f"{relative_path} still treats legacy scene as current: {phrase}")


def validate_status_recovery_shape(errors: list[str]) -> None:
    text = read_text(".codex/status.md")
    required_tokens = [
        "# Current Status",
        "## 当前任务",
        "## 当前阶段",
        "## 下一步",
        "## 验证状态",
        "## 风险 / 阻塞",
    ]
    for token in required_tokens:
        if token not in text:
            errors.append(f".codex/status.md missing recovery section: {token}")


def main() -> int:
    errors: list[str] = []
    validate_required_files(errors)
    if not errors:
        validate_main_entry_contract(errors)
        validate_status_recovery_shape(errors)

    if errors:
        print("Codex process memory validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Codex process memory validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
