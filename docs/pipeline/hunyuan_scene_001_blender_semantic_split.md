# Hunyuan Scene 001 Blender Semantic Split Step

## Purpose

Convert the current engineering module split into a Blender semantic module package with unified pivot and decimated export.

## Script

- `res://tools/blender_semantic_split_hunyuan_scene_001.py`

## Command

```powershell
blender --background --python tools/blender_semantic_split_hunyuan_scene_001.py -- `
  --input "D:/那个村庄/assets/3d/raw/hunyuan_scene_001/hunyuan_scene_001_raw.ply" `
  --output-dir "D:/那个村庄/assets/3d/modules/hunyuan_scene_001/official"
```

## Output

- `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_module_ground.glb`
- `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_module_architecture.glb`
- `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_module_vegetation.glb`
- `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_module_props.glb`
- `res://assets/3d/modules/hunyuan_scene_001/official/semantic_export_report.json`

## Notes

- This script uses first-pass semantic heuristics from loose-part AABB and height footprint.
- Export keeps the `hunyuan_scene_001_module_*` naming prefix.
- After export, replace the module paths in preview/runtime scenes and rerun:
  - `python tools/build_hunyuan_scene_001_runtime_proxies.py`
  - `python tools/validate_hunyuan_scene_001_characterbody3d.py`
  - Godot import/load checks.
