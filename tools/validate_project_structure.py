from __future__ import annotations

from pathlib import Path

from audit_project_structure import ROOT, build_audit


REQUIRED_TOP_LEVEL = [
    "AGENTS.md",
    "README.md",
    "project.godot",
    "assets",
    "docs",
    "game",
    "production",
    "scenes",
    "scripts",
    "tools",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    audit = build_audit()
    errors: list[str] = []

    for name in REQUIRED_TOP_LEVEL:
        if not (ROOT / name).exists():
            errors.append(f"missing required top-level item: {name}")

    if audit["empty_root_dirs"]:
        errors.append(f"empty root template dirs remain: {audit['empty_root_dirs']}")

    if audit["deprecated_root_dirs"]:
        errors.append(f"deprecated root dirs remain: {audit['deprecated_root_dirs']}")

    required_docs = audit["required_docs"]
    for name, exists in required_docs.items():
        if not exists:
            errors.append(f"missing required structure doc: {name}")

    incoming = audit["incoming"]
    if incoming.get("exists"):
        expected = {
            "01_scene_mothers",
            "02_scene_base",
            "03_foreground_occlusion",
            "04_audit",
            "README.md",
            "_archive",
        }
        actual = set(incoming["top_level"])
        unexpected = sorted(actual - expected)
        if unexpected:
            errors.append(f"unexpected incoming top-level items: {unexpected}")

        for dirname, count in incoming["active_counts"].items():
            if count != 10:
                errors.append(f"incoming {dirname} expected 10 PNGs, found {count}")

        if incoming["deprecated_top_level"]:
            errors.append(f"deprecated incoming items remain at top level: {incoming['deprecated_top_level']}")
        if not incoming["audit_exists"]:
            errors.append("missing incoming 04_audit/scene_mother_layers.json")
        if not incoming["preview_contact_exists"]:
            errors.append("missing incoming 04_audit/previews/scene_layer_preview_contact.png")

    if errors:
        for error in errors:
            print(f"INVALID: {error}")
        fail(f"{len(errors)} project structure validation errors")

    print("OK: project structure validates")


if __name__ == "__main__":
    main()
