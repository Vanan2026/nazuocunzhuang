from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STYLE_MOTHER = "production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg"

DOCS = {
    "docs/GREENFIELD_P0_ART_ASSET_CODEX_EXECUTION.md": [
        STYLE_MOTHER,
        "可交互游戏壳",
        "Scene Assets",
        "UI Kit Assets",
        "Icon Assets",
        "Character Assets",
        "System Screens",
        "P0 Vertical Slice",
        "Phase 1: UI Kit",
        "full-canvas alpha",
        "不能独立重画成不同构图",
        "不要再让 Codex 按参考图即兴猜测",
    ],
    "docs/ART_BIBLE.md": [
        STYLE_MOTHER,
        "温暖低饱和",
        "3/4 top-down",
        "羊皮纸面板",
        "木质边框",
        "Q 版 3.5 到 4 头身",
        "不声明 launch quality",
    ],
    "docs/ASSET_MANIFEST.md": [
        STYLE_MOTHER,
        "scene_home_area_mother.png",
        "scene_home_area_base.png",
        "scene_home_area_foreground_occlusion.png",
        "ui_panel_paper_01.png",
        "ui_button_normal.png",
        "icon_flower_yellow.png",
        "portrait_npc_aya_neutral.png",
        "data/gifts.json",
        "scenes/ui/SettingsScreen.tscn",
    ],
    "docs/CODEX_TASKS.md": [
        "Task P0-01: UI Kit Foundation",
        "Task P0-02: HomeArea Scene Package",
        "Task P0-04: Inventory Screen",
        "Task P0-05: Dialogue + Gift",
        "Task P0-06: Map Screen",
        "Task P0-07: Settings Screen",
        "优先执行 `Task P0-01: UI Kit Foundation`",
    ],
}

FORBIDDEN = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bcombat\b",
        r"\bmonster\b",
        r"\bdamage\b",
        r"\bweapon\b",
        r"\bhp\b",
        r"\bkill\b",
        r"\bloot\b",
        r"TBD",
        r"TODO",
    ]
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def read_doc(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        fail(f"missing required doc: {relative_path}")
    return path.read_text(encoding="utf-8")


def validate_docs() -> None:
    if not (ROOT / STYLE_MOTHER).is_file():
        fail(f"missing style mother reference: {STYLE_MOTHER}")
    for relative_path, tokens in DOCS.items():
        text = read_doc(relative_path)
        for token in tokens:
            if token not in text:
                fail(f"{relative_path} missing required token: {token}")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                fail(f"{relative_path} contains forbidden or placeholder token: {pattern.pattern}")


def validate_task_order() -> None:
    text = read_doc("docs/CODEX_TASKS.md")
    ordered = [
        "Task P0-01: UI Kit Foundation",
        "Task P0-02: HomeArea Scene Package",
        "Task P0-03: HUD",
        "Task P0-04: Inventory Screen",
        "Task P0-05: Dialogue + Gift",
        "Task P0-06: Map Screen",
        "Task P0-07: Settings Screen",
    ]
    positions = [text.find(item) for item in ordered]
    if any(position < 0 for position in positions):
        fail("CODEX_TASKS is missing one or more P0 task headings")
    if positions != sorted(positions):
        fail("CODEX_TASKS P0 task order is not stable")


def main() -> None:
    validate_docs()
    validate_task_order()
    print("OK: Greenfield P0 execution docs validate")


if __name__ == "__main__":
    main()
