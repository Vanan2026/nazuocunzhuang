# Protagonist GLB Export Contract (3D -> 2.5D Pipeline)

## Required Clip Names

- `idle`
- `walk`
- `interact`
- `sit_down`
- `sit_idle`
- `stand_up`

Each clip must be exported as either:
- one GLB containing all clips with these names, or
- multiple GLBs where each file clip still uses the exact name.

## Geometry + Rig

- Keep a single stable skeleton hierarchy across all clips.
- Required attributes on render mesh primitives:
  - `POSITION`
  - `NORMAL`
  - `JOINTS_0`
  - `WEIGHTS_0`
  - `TEXCOORD_0`
- Keep root transform and unit scale consistent across clips.

## Material + Texture

- Must include texture payload (`textures` + `images`) with base color.
- Split at least these material slots:
  - `skin`
  - `hair`
  - `cloth_top`
  - `cloth_bottom`
  - `shoes`

This is required for controllable recolor and style iteration.

## Naming + Metadata

- Avoid generic clip name `Armature`.
- Mesh and material names should be stable and human-readable.
- Keep clip FPS and duration intentional (loop clips should be loop-clean).

## Validation Command

Run after import/recolor staging:

```powershell
python tools\validate_protagonist_glb_contract.py
```

Pass condition: no `FAIL` output.
