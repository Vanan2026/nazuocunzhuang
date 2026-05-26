# MountainHut World2D v001

Status: art_prep_ready_not_runtime_replacement

This package prepares the MountainHut region for future source art and layer export. It does not contain final painted art and does not replace runtime visuals.

## Why This Exists

Village semantic-layer review found that the east edge breaks world continuity because MountainHut still reads as generated/blockout art. This package defines the MountainHut source contract and the `village_to_mountain_hut` seam before any new painted image is produced.

## Production Order

1. Review this package and the seam brief.
2. Generate one opaque `mountain_hut_painted_source` using the layout lock and OutdoorWorld master.
3. Review the source against Village east continuity.
4. Export full-canvas layers from the accepted source only.
5. Run Godot screenshot review before any runtime replacement.

## Boundaries

- No combat, threat, damage, monster, weapon, or failure-state content.
- No runtime replacement until source/layer/Godot screenshot review passes.
- No independently generated runtime layers.
- No cropped transparent layers.

## Related

- `production/assets/seams/village_to_mountain_hut/v001/seam_brief.md`
- `production/assets/outdoor_world_world2d/v001/workflow_manifest.json`
- `production/assets/regions/village_world2d/v001/workflow_manifest.json`
