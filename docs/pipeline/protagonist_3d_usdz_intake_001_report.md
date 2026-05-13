# Protagonist 3D USDZ Intake Report 001

Date: 2026-05-12  
Source: `res://assets/3d/raw/characters/protagonist_3d/protagonist_source_001.usdz`

## Intake summary

- Imported source USDZ successfully.
- Source has skeleton + skinning:
  - armatures: `1`
  - bones: `28`
  - meshes: `1`
- Source contains no animation clips, so runtime clips were authored in Blender and exported to GLB.

## Output asset

- Processed GLB:
  - `res://assets/3d/processed/protagonist_3d/protagonist_rigged_anim_v001.glb`
- Generated clips:
  - `idle`
  - `walk`
  - `interact`
  - `sit_down`
  - `sit_idle`
  - `stand_up`

## Runtime integration

- Character scene:
  - `res://scenes/3d/protagonist_3d_character.tscn`
- Character controller script:
  - `res://scripts/world/protagonist_3d_controller.gd`
- Playtest scene (integrated with current Hunyuan preview world):
  - `res://scenes/dev/hunyuan_scene_001_protagonist_3d_playtest.tscn`

## Controls (playtest)

- Move: Arrow keys (uses `ui_left/right/up/down`)
- Interact animation: `E`
- Sit/stand toggle: `Q`

## Validation

- Godot import gate passed:
  - `Godot --headless --import --quit`
- Godot runtime load gate passed:
  - `Godot --headless --quit-after ...`
- Runtime contract gate passed:
  - `python tools/validate_protagonist_3d_runtime.py`

## Notes

- The six generated clips are prototype-level motion clips intended to unblock gameplay/camera/integration testing.
- If higher-fidelity body mechanics are needed, replace these clips with authored motion data while keeping clip names stable.

## 2026-05-12 Pass 2 update

- User QA feedback indicated first-pass motion readability was too weak (near A-pose impression).
- Updated `tools/blender_prepare_protagonist_usdz.py` with stronger frame-by-frame full-body keying and re-exported the same GLB path.
- Added clean animation QA scene:
  - `res://scenes/dev/protagonist_3d_animation_lab.tscn`
- Default run scene now points to the lab for motion validation, decoupled from fragmented world mesh visuals.

## 2026-05-12 Pass 3 update (real-motion retarget)

- Switched from procedural keyframing to real-motion retarget pipeline:
  - new script: `tools/blender_build_protagonist_from_real_motions.py`
  - target model: `protagonist_source_001.usdz`
  - source motions: `production/assets/protagonist_3d/recolored/*.glb`
- New output:
  - `res://assets/3d/processed/protagonist_3d/protagonist_rigged_anim_v002_real.glb`
- Character scene now binds to `v002_real` for runtime playtest.
