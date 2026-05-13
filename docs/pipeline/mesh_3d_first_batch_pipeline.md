# Mesh 3D First Batch Pipeline (2D-Compatible)

This project now runs a mixed pipeline:
- Existing 2D pipeline remains untouched.
- New 3D mesh intake is additive and isolated.

## Directory Contract

- `res://assets/3d/raw/`: raw GLB imports from external generators.
- `res://assets/3d/processed/`: processed first-pass GLBs for preview.
- `res://assets/3d/modules/`: reserved for modular scene-ready GLB wrappers.
- `res://assets/3d/materials/`: reusable `.tres`/shader resources.
- `res://assets/3d/textures/`: baked and hand-painted textures.
- `res://scenes/dev/`: dev-only preview and diagnostics scenes.
- `res://scenes/3d/`: runtime 3D scene work.
- `res://scripts/tools/`: in-engine tool scripts.
- `res://docs/pipeline/`: pipeline docs.

## First Batch Intake

Input files currently expected:
- `C:/Users/23732/Downloads/cb790243ea4e7e4dbf40fc8d995eff5d.glb`
- `C:/Users/23732/Downloads/c01097343d578a9b755a7c0c07a89795.glb`
- `C:/Users/23732/Downloads/effad4009179ed5681340ba9adc2b0a0.glb`
- `C:/Users/23732/Downloads/5571ddffb0e493df35384702913f5f41.glb`

Run:

```powershell
python tools\intake_3d_mesh_batch.py
```

Output:
- raw copies in `res://assets/3d/raw/`
- first-pass tinted GLBs in `res://assets/3d/processed/`
- report at `res://.codex/mesh_3d_intake_report.md`

## Preview

Open:
- `res://scenes/dev/dev_3d_mesh_preview.tscn`

Behavior:
- auto-loads GLB/GLTF/TSCN assets from `res://assets/3d/processed`
- places them in a simple grid
- uses warm, low-contrast lighting for style fit checks

## Validation

```powershell
python tools\validate_3d_mesh_pipeline.py
python tools\validate_protagonist_glb_contract.py
```

Optional Godot load checks:

```powershell
C:\Users\23732\AppData\Local\Programs\Godot\4.6.1\Godot_v4.6.1-stable_win64_console.exe --headless --path D:\那个村庄 --script res://tools/load_scene.gd -- res://scenes/dev/dev_3d_mesh_preview.tscn
```

## Current Known Gaps

- Some intake GLBs still miss UV (`TEXCOORD_0`) and texture payload.
- One file has no animation clip.
- Clip naming is still generic (`Armature`) on animated files.

These are source-export issues; keep fixing them at the generator/Blender stage.
