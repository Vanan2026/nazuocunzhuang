from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS_PATH = ROOT / ".codex" / "hooks.json"
SESSION_START_SCRIPT = ROOT / "tools" / "codex_session_start_hook.ps1"
ALLOWED_EVENTS = {
    "PreToolUsePermissionRequest",
    "PostToolUse",
    "PreCompact",
    "PostCompact",
    "SessionStart",
    "UserPromptSubmit",
    "Stop",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_hooks() -> dict:
    require(HOOKS_PATH.exists(), f"missing {HOOKS_PATH}")
    with HOOKS_PATH.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    require(isinstance(data, dict), "hooks.json must be an object")
    require(isinstance(data.get("hooks"), dict), "hooks.json requires hooks object")
    return data


def validate_hooks_shape(data: dict) -> None:
    hooks = data["hooks"]
    require("SessionStart" in hooks, "SessionStart hook is required")
    for event_name, groups in hooks.items():
        require(event_name in ALLOWED_EVENTS, f"unsupported hook event: {event_name}")
        require(isinstance(groups, list) and groups, f"{event_name} must be a non-empty list")
        for group in groups:
            require(isinstance(group, dict), f"{event_name} group must be an object")
            require(isinstance(group.get("hooks"), list) and group["hooks"], f"{event_name} group requires hooks")
            for hook in group["hooks"]:
                require(hook.get("type") == "command", "only command hooks are expected")
                command = hook.get("command")
                require(isinstance(command, str) and command.strip(), "command hook requires command")
                timeout = hook.get("timeout")
                if timeout is not None:
                    require(isinstance(timeout, int) and timeout > 0, "timeout must be a positive integer")


def validate_session_start_output() -> None:
    require(SESSION_START_SCRIPT.exists(), f"missing {SESSION_START_SCRIPT}")
    sample_input = json.dumps(
        {
            "session_id": "validate-codex-hooks",
            "transcript_path": "",
            "cwd": str(ROOT),
            "hook_event_name": "SessionStart",
            "source": "startup",
        }
    )
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SESSION_START_SCRIPT),
        ],
        input=sample_input,
        text=True,
        capture_output=True,
        cwd=ROOT,
        timeout=10,
        encoding="utf-8",
    )
    require(completed.returncode == 0, completed.stderr or completed.stdout)
    require(completed.stdout.strip(), "session start hook produced no stdout")
    payload = json.loads(completed.stdout)
    require(payload.get("continue") is True, "SessionStart output must continue")
    require(payload.get("suppressOutput") is False, "SessionStart output should stay visible to Codex")
    message = payload.get("systemMessage")
    require(isinstance(message, str) and "AGENTS.md" in message, "systemMessage must mention AGENTS.md")
    require(".codex/status.md" in message, "systemMessage must mention .codex/status.md")
    require("streamable-http" in message, "systemMessage must preserve Godot MCP probe rule")


def main() -> int:
    data = load_hooks()
    validate_hooks_shape(data)
    validate_session_start_output()
    print("validate_codex_hooks: ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - validation script should print concise failure.
        print(f"validate_codex_hooks: failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
