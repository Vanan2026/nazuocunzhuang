# HomeArea World2D v001 production plan

## Current objective
Produce a clean HomeArea scene art source and true coordinate-stable layer package for Godot integration.

## Phase 1 - Source production
- Use camera_lock.json and object_mask_lock.json as fixed input.
- Produce source_full.png at 6144x4096.
- Review source against 05_review_and_qa/review_gate.md.

## Phase 2 - Layer export
- Export base_clean.png as full-canvas opaque base.
- Export structural foreground PNGs as full-canvas transparent layers.
- Export independent prop crops only with pivot metadata.

## Phase 3 - Godot integration
- Add source-derived layers to scenes/regions/region_home_area.tscn.
- Author blockers from approved visible structures.
- Author interactions after blockers.

## Stop conditions
- Stop if source image does not match locked camera/object structure.
- Stop if foreground layer looks like a sticker patch or broad rectangle.
- Stop if Godot integration requires guessing unapproved object positions.
