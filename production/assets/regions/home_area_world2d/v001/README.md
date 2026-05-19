# HomeArea World2D v001 Production Line

Status: art production started on 2026-05-19.

This is the only active HomeArea scene-art production path. All older flattened, launch, formal, sticker-slice, and local patch attempts have been removed from the production path.

## Canonical workflow

1. Use the locked 3D blockout and camera as the structure authority.
2. Generate or paint one approved full-canvas source image from that locked blockout.
3. Export coordinate-stable layers from the approved source image.
4. Integrate visual layers in Godot only after layer approval.
5. Author interactions and blockers only after visual structure is stable.

## Non-negotiable rules

- Keep canvas and origin stable across source, base, foreground, and masks.
- Structural foreground layers must be full-canvas transparent PNGs.
- Cropped sprites are allowed only for independent props with explicit pivot metadata.
- Do not promote broad rectangle foreground plates.
- Do not derive final layers from rejected flattened review plates.
- Do not place gameplay blockers or interactions before visual layers are approved.

## Current production entry files

- 01_3d_blockout/camera_lock.json
- 01_3d_blockout/object_mask_lock.json
- 02_source_generation/source_image_brief.md
- 02_source_generation/prompt_home_area_source_v001.md
- 03_layer_export/layer_contract.json
- 03_layer_export/export_manifest_template.json
- 05_review_and_qa/review_gate.md
