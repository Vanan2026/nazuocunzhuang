# MountainHut v003 Full-Canvas Repaint Brief

Status: needs_v003_repaint_before_layer_export

## Goal

Create one high-quality `mountain_hut_painted_source_v003.png` as an opaque 1800x1200 full-canvas storybook source for the MountainHut region.

The target is registration-perfect layer alignment, not pixel-perfect brush tracing. Keep natural painted variation in grass, flowers, pebbles, leaves, road shoulders, and wall texture.

## Required References

- Use the accepted Village source as the quality target for foliage density, road softness, grass variation, and warm low-saturation storybook finish.
- Use the external handoff MountainHut image as a quality reference only. It has better painterly density, but its size and layout are wrong for this package.
- Use `mountain_hut_painted_source_v002.png` only for spatial lock: west seam entry, hut zone, door zone, woodpile zone, upper-right foreground bough, and north return path.

## Locked Spatial Contract

- Canvas must be exactly 1800x1200.
- The west seam path must enter at source point `[0, 667]` with roughly 76 px readable road width.
- The road should bend gently from the west edge toward the hut door and then continue softly toward the north return path.
- Hut mass stays in the right half of the scene, above the approach path, without blocking the west seam road.
- Door remains readable and approachable.
- Woodpile, herb shelf, porch shadow, and small repair hints are allowed.
- no combat, weapons, danger signs, monsters, gore, or high-pressure warning marks.

## Layer Future-Proofing

- Produce a single full-canvas painted source first.
- All future runtime layers must derive from that same source.
- Do not crop transparent runtime layers after export.
- Do not independently regenerate separate layer compositions.
- Preserve one shared origin, perspective, scale, rotation, and canvas.

## Visual Quality Bar

- Match the accepted Village source in integrated foliage, soft roads, small flower clusters, believable roof texture, and hand-painted grass.
- Avoid flat stamped tree blobs, procedural grass noise, outline-only roof arcs, isolated white flower dots, and uniform empty green fields.
- Keep the hut cozy, quiet, and repairable, not abandoned-horror or combat-adventure.
