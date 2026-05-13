# Hunyuan 3D Source Regeneration Spec (v1)

Date: 2026-05-12  
Scope: `hunyuan_scene_001` replacement source mesh intake

## Why

Current source mesh is not semantically readable as a courtyard scene in Godot preview, so downstream split/decimate/pivot/collision steps cannot recover production-usable structure.

## Target

Regenerate source mesh first, then re-enter existing Blender/Godot pipeline.

## Required upstream output

For each candidate source mesh (PLY/GLB), provide:

1. One full scene mesh file (`.ply` or `.glb`)
2. One texture-packed variant if available (preferred `.glb`)
3. Four orthographic screenshots from DCC:
   - front
   - back
   - left
   - top
4. One perspective screenshot with grid and axis visible
5. One short note:
   - generation model/version
   - prompt
   - reconstruction mode/options

## Hard acceptance gates (before Blender semantic split)

Candidate must pass all:

1. Human readability gate:
   - In orthographic and perspective previews, the courtyard layout is recognizable (ground plane, house mass, vegetation masses).
2. Structural continuity gate:
   - No dominant “salt-and-pepper” fragmented face cloud look.
3. Scale sanity gate:
   - Main scene bounds are not collapsed into tiny micro-cluster.
4. Pipeline compatibility gate:
   - Godot imports without parse/resource errors.

## Fail-fast rule

If candidate fails readability gate, do **not** continue with:

- semantic split
- decimation tuning
- nav/blocker authoring

Regenerate source instead.

## Recommended regeneration settings

1. Keep scene scope focused:
   - one courtyard composition
   - avoid excessive depth ambiguity
2. Prefer stable coarse forms:
   - prioritize readable macro masses over micro detail
3. Run 2-3 independent generations and pick best candidate by readability, not by polygon count.

## Re-entry command sequence (after new source selected)

```powershell
python tools/prepare_hunyuan_scene_001.py
python tools/validate_hunyuan_source_mesh_quality.py
blender --background --python tools/blender_semantic_split_hunyuan_scene_001.py -- --input "D:/那个村庄/assets/3d/raw/hunyuan_scene_001/hunyuan_scene_001_raw.ply" --output-dir "D:/那个村庄/assets/3d/modules/hunyuan_scene_001/official"
python tools/switch_hunyuan_scene_001_to_official_modules.py
python tools/build_hunyuan_scene_001_runtime_proxies.py
python tools/validate_hunyuan_scene_001_characterbody3d.py
```
