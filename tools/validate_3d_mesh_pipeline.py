from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRS = (
    ROOT / "assets" / "3d" / "raw",
    ROOT / "assets" / "3d" / "processed",
    ROOT / "assets" / "3d" / "modules",
    ROOT / "assets" / "3d" / "materials",
    ROOT / "assets" / "3d" / "textures",
    ROOT / "scenes" / "3d",
    ROOT / "scenes" / "dev",
    ROOT / "scripts" / "tools",
    ROOT / "docs" / "pipeline",
)

PREVIEW_SCENE = ROOT / "scenes" / "dev" / "dev_3d_mesh_preview.tscn"
PREVIEW_SCRIPT = ROOT / "scripts" / "tools" / "dev_3d_mesh_preview.gd"
INTAKE_SCRIPT = ROOT / "tools" / "intake_3d_mesh_batch.py"
GLB_CONTRACT_SCRIPT = ROOT / "tools" / "validate_protagonist_glb_contract.py"
PIPELINE_DOC = ROOT / "docs" / "pipeline" / "mesh_3d_first_batch_pipeline.md"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def require(cond: bool, msg: str) -> None:
    if not cond:
        fail(msg)


def main() -> None:
    for path in REQUIRED_DIRS:
        require(path.exists() and path.is_dir(), f"missing directory: {path}")

    for path in (PREVIEW_SCENE, PREVIEW_SCRIPT, INTAKE_SCRIPT, GLB_CONTRACT_SCRIPT, PIPELINE_DOC):
        require(path.exists(), f"missing required file: {path}")

    processed_glb = list((ROOT / "assets" / "3d" / "processed").glob("*.glb"))
    require(processed_glb, "no processed GLB files found in assets/3d/processed")

    report = ROOT / ".codex" / "mesh_3d_intake_report.md"
    if report.exists():
        require(report.stat().st_size > 0, "intake report .codex/mesh_3d_intake_report.md is empty")

    scene_text = PREVIEW_SCENE.read_text(encoding="utf-8")
    require("res://scripts/tools/dev_3d_mesh_preview.gd" in scene_text, "preview scene must attach dev preview script")

    script_text = PREVIEW_SCRIPT.read_text(encoding="utf-8")
    require('mesh_dir: String = "res://assets/3d/processed"' in script_text, "preview script must default to assets/3d/processed")

    print("OK: 3D mesh first-batch pipeline validated")


if __name__ == "__main__":
    main()
