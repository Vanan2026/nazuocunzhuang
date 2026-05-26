# Village To MountainHut Seam Brief v001

Status: art_prep_ready_not_runtime_replacement

## Purpose

This brief defines the `village_to_mountain_hut` seam for the current `OutdoorWorld` layout. The seam exists to make the Village east edge and MountainHut west edge read as one calm countryside world, not two unrelated generated plates.

## Runtime Connection

- World: `OutdoorWorld`
- Connection id: `village_to_mountain_hut`
- From: `Village`
- To: `MountainHut`
- Runtime points from master layout:
  - Village east edge: `[1040, 108]`
  - MountainHut west edge: `[1060, 108]`
- Current role: future_east_village_extension

## Visual Continuity Contract

- Keep the road continuous across the seam. The Village east road should enter the MountainHut canvas from the west edge without a width jump.
- Match warm low-saturation storybook color, fixed 3/4 top-down perspective, and soft hand-painted edges.
- Preserve ground continuity: grass hue, road material, path shoulder softness, pebble density, flower density, and worn-footpath detail density should not visibly reset at the seam.
- Use the OutdoorWorld master blueprint as a spatial guide, not as a pixel-perfect brush tracing target.
- Target registration-perfect layer alignment: same full canvas, origin, perspective, composition, coordinate system, pivot, scale, and rotation across all MountainHut layers.

## MountainHut West Edge Requirements

- The west seam connector must land near the local runtime point `[0, 120]` on a `320x240` region, corresponding to source-canvas point `[0, 667]` at scale `0.18`.
- The path should bend gently toward the hut door rather than becoming a straight corridor.
- No tree trunk, fence, porch post, or foreground occlusion may block the seam travel readability.
- The road should remain wide enough for player movement and future NPC pathing, while staying visually quiet.

## Source And Layer Rules

- Produce one opaque `mountain_hut_painted_source` first.
- Derive every runtime layer from that same `painted_source`; do not independently regenerate layer compositions.
- Keep every transparent layer full canvas with alpha outside painted areas.
- Do not crop layers to an object bounding box.
- Keep `runtime replacement` blocked until source review, layer review, and Godot screenshot review pass.

## Review Gate

The seam is not approved until a regenerated east-continuity screenshot shows:

- Village east road and MountainHut west path connect without a visual jump.
- Ground color and detail density remain compatible.
- MountainHut reads as a quiet recovery/discovery place, not a combat, hazard, or pressure zone.
- No runtime replacement has been made before visual review.
