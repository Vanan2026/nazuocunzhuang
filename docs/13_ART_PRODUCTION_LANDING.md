# Art Production Landing - 2026-05-19

This is the project-level art production landing plan for the current playable route. It turns the art work into a tracked production system instead of isolated image batches.

## Current rule

Region art must use the source-first workflow:

1. lock layout or 3D blockout
2. create one source composition
3. export coordinate-stable layers
4. integrate into Godot scene
5. run scripted validation
6. require human visual review before launch-quality approval

A scene can be wired as a structural placeholder while `launch_quality_approved=false`. That state is useful for gameplay testing, but it is not final art approval.

## Active P0 packages

- HomeArea: `production/assets/regions/home_area_world2d/v001`, integrated but still pending Godot capture review.
- BackFarm: `production/assets/regions/back_farm_art/v002`, active structural placeholder, explicitly not launch-quality.
- Protagonist: `production/assets/protagonist/protagonist_runtime_manifest_v001.json`, runtime candidate with human visual review still required.
- Crops, weather icons, and minimal UI pieces: present for current runtime checks.

## Explicit gaps

- Item icons are incomplete: current crop icons exist, but seed/material/forage/fish/food/key icons in `game/data/items.json` still need runtime PNGs.
- Hana is present in NPC data but lacks current runtime portrait and idle sprite assets.
- Village, MountainPath, ForestEdge, Orchard, Pond, Mountain, MountainHut, and CliffView still need World2D source-first packages.

## Validation

Run:

```powershell
python tools/validate_project_art_production_landing.py
python tools/validate_home_area_world2d_v001.py
python tools/validate_region_back_farm_art_v002.py
python tools/validate_protagonist_runtime_manifest.py
```

The project-level validator checks that every runtime region has an art-production row, active packages do not claim launch approval, and known asset gaps are explicit instead of hidden.
