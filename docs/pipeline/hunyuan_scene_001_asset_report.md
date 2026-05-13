# Hunyuan Scene 001 Asset Report

Date: 2026-05-12  
Project: 那座村庄 (Godot 4.x)

## Scope

Second Blender cleanup pass completed:

- semantic split with reduced overlap tendency (face-level unique assignment)
- stronger per-module decimation
- authored walkable/nav data and blocker collider data exported
- preview scene switched from raw proxy generation to authored runtime data

## Source

- Source mesh: `res://assets/3d/raw/hunyuan_scene_001/hunyuan_scene_001_raw.ply`

## Outputs

- Official semantic modules:
  - `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_module_ground.glb`
  - `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_module_architecture.glb`
  - `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_module_vegetation.glb`
  - `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_module_props.glb`
- Authored runtime assets:
  - `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_walkable_nav.glb`
  - `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_blockers.glb`
  - `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_authored_runtime.json`
- Reports:
  - `res://assets/3d/modules/hunyuan_scene_001/official/semantic_export_report.json`
  - `res://assets/3d/modules/hunyuan_scene_001/runtime_proxies.json`

## Active Runtime Wiring

- Active module pack: `official` (`res://assets/3d/modules/hunyuan_scene_001/manifest.json`)
- Preview scene: `res://scenes/dev/hunyuan_scene_001_preview.tscn`
- `CollisionProxy` and `NavigationRegion3D` now read authored data from:
  - `res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_authored_runtime.json`

## Current Metrics

- Official module count: `4`
- Official module triangles total: `155947`
- Authored nav vertices: `560`
- Authored nav polygons: `140`
- Floor collision boxes: `140`
- Blocker boxes: `1`

## Validation

```powershell
blender --background --python tools/blender_semantic_split_hunyuan_scene_001.py -- --input "D:/那个村庄/assets/3d/raw/hunyuan_scene_001/hunyuan_scene_001_raw.ply" --output-dir "D:/那个村庄/assets/3d/modules/hunyuan_scene_001/official"
python tools/switch_hunyuan_scene_001_to_official_modules.py
python tools/build_hunyuan_scene_001_runtime_proxies.py
python tools/validate_hunyuan_scene_001_characterbody3d.py
python tools/validate_3d_mesh_pipeline.py
Godot_v4.6.1-stable_win64_console.exe --headless --path D:/那个村庄 --import --quit
Godot_v4.6.1-stable_win64_console.exe --headless --path D:/那个村庄 --script res://tools/load_scene.gd -- res://scenes/dev/hunyuan_scene_001_preview.tscn
Godot_v4.6.1-stable_win64_console.exe --headless --path D:/那个村庄 --script res://tools/load_scene.gd -- res://scenes/dev/hunyuan_scene_001_characterbody3d_test.tscn
```

All validations passed in this run.

## Risks

- Semantic categorization is still heuristic; module meaning is stable enough for prototype but not final art-authored quality.
- Current blocker set only has one large blocker component; hand-authored fine blockers are still recommended.
- Navigation mesh is authored by Blender script heuristics, not by manual level-design pass.
