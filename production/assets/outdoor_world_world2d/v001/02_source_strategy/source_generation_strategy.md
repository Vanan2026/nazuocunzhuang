# Source Generation Strategy

## Corrected Pipeline

The current project uses one seamless 2D `OutdoorWorld`, so art production must start from world continuity rather than isolated region beauty.

1. Keep the world blueprint as the spatial contract.
2. Produce one `world_base_no_foreground` whole-world base. It may be lower precision, but it must unify roads, ground hue, lighting, and region relationships.
3. Export `region crop` base images from that whole-world base.
4. Every high-quality region repaint must start from the inherited crop and must not independently recompose region bases.
5. Add `foreground_occlusion` as a separate per-region layer only after the region base is accepted.
6. Validate layer registration and Godot screenshots before runtime replacement.

## Current Base-Map Artifacts

- Whole-world base: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/outdoor_world_base_no_foreground.png`
- Review preview: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/outdoor_world_base_no_foreground_review.png`
- Region crops: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/region_base_crops/`
- Manifest: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/world_base_manifest.json`

## Village And MountainHut Correction

The existing Village and MountainHut high-detail images are useful review references, but they came from isolated region production. Future promotion should inherit from the whole-world base crop first, then repaint detail inside that inherited composition.

The previous Village layout draft remains a layout draft only. It is not final `village_painted_source` art and should not be split or promoted ahead of the world-base inheritance review.

Do not independently recompose region bases. If a region needs higher quality, repaint over the inherited crop while preserving roads, terrain color, lighting, edge continuation, and camera perspective.

## Layer Scope For Seamless MVP

Use this smaller layer stack until world continuity is stable:

- `base_ground`
- `terrain_details`
- `behind_player_structures`
- `ysort_props_structures`
- `foreground_occlusion`

Keep weather, season, and time-of-day in Godot/system-level tinting first. Avoid per-region weather overlays until base seams pass review.
