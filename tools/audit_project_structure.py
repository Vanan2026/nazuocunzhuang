from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / ".codex" / "reports"

EMPTY_ROOT_DIR_CANDIDATES = [
    "export_templates",
    "feature_profiles",
    "script_templates",
    "text_editor_themes",
]

DEPRECATED_ROOT_DIRS = [
    ".superpowers",
    "Claude-Code-Game-Studios-main",
]

ACTIVE_INCOMING_DIRS = [
    "01_scene_mothers",
    "02_scene_base",
    "03_foreground_occlusion",
    "04_audit",
    "_archive",
]


def count_files(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def count_dirs(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_dir())


def dir_is_empty(path: Path) -> bool:
    return path.exists() and path.is_dir() and not any(path.iterdir())


def top_level_summary() -> list[dict]:
    rows = []
    for item in sorted(ROOT.iterdir(), key=lambda p: p.name.lower()):
        if item.name == ".git":
            continue
        if item.is_dir():
            rows.append(
                {
                    "name": item.name,
                    "type": "dir",
                    "files": count_files(item),
                    "dirs": count_dirs(item),
                }
            )
        else:
            rows.append(
                {
                    "name": item.name,
                    "type": "file",
                    "bytes": item.stat().st_size,
                }
            )
    return rows


def incoming_status() -> dict:
    incoming = ROOT / "production" / "assets" / "external_gpt_handoff" / "greenfield_p0" / "v001" / "incoming"
    if not incoming.exists():
        return {"exists": False}

    top_level = sorted(item.name for item in incoming.iterdir())
    active_counts = {}
    for dirname in ["01_scene_mothers", "02_scene_base", "03_foreground_occlusion"]:
        active_counts[dirname] = len(list((incoming / dirname / "regions").glob("*/*.png")))

    deprecated_top_level = [
        name
        for name in ["01_mother_images", "02_runtime_exports", "audit_previews", "audit_scene_mother_layers.json"]
        if (incoming / name).exists()
    ]

    return {
        "exists": True,
        "top_level": top_level,
        "active_counts": active_counts,
        "deprecated_top_level": deprecated_top_level,
        "audit_exists": (incoming / "04_audit" / "scene_mother_layers.json").exists(),
        "preview_contact_exists": (incoming / "04_audit" / "previews" / "scene_layer_preview_contact.png").exists(),
    }


def build_audit() -> dict:
    empty_root_dirs = [name for name in EMPTY_ROOT_DIR_CANDIDATES if dir_is_empty(ROOT / name)]
    deprecated_root_dirs = [name for name in DEPRECATED_ROOT_DIRS if (ROOT / name).exists()]
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(ROOT),
        "top_level": top_level_summary(),
        "empty_root_dirs": empty_root_dirs,
        "deprecated_root_dirs": deprecated_root_dirs,
        "incoming": incoming_status(),
        "required_docs": {
            "project_structure": (ROOT / "docs" / "16_PROJECT_STRUCTURE.md").exists(),
            "external_handoff": (ROOT / "docs" / "15_EXTERNAL_GPT_ASSET_HANDOFF.md").exists(),
            "runtime_migration": (ROOT / "docs" / "12_RUNTIME_MIGRATION_PLAN.md").exists(),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    audit = build_audit()
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = args.out or REPORTS / "project_structure_audit_2026-05-22.json"
    out.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: wrote project structure audit to {out}")


if __name__ == "__main__":
    main()
