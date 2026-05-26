# Village v002 Inherited World-Base Repaint Brief

## Goal

Create a high-quality `village_painted_source_v002` from the inherited world-base crop. This is an inherited world-base crop repaint, not a new isolated composition.

## Required Inputs

- Composition source: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/region_base_crops/village_base_no_foreground.png`
- Quality reference only: `production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png`
- Layout lock: `production/assets/regions/village_world2d/v001/01_layout_lock/layout_lock.json`
- Outdoor parent: `production/assets/outdoor_world_world2d/v001/workflow_manifest.json`

## Output Contract

- Output one opaque `village_painted_source_v002` at full-canvas `1800x1200`.
- Preserve the inherited crop's road continuation, terrain hue, lighting direction, perspective, and edge relationships.
- Use registration-perfect layer alignment rules: shared canvas, shared origin, shared pivot, shared scale, shared rotation, and shared perspective.
- Keep later runtime layers full-canvas. Do not crop transparent layers to object bounds.
- Produce `foreground_occlusion` only after the inherited repaint base is accepted.

## Visual Direction

- Warm low-saturation storybook 2D village art.
- Fixed 3/4 top-down rural view.
- Social hub: notice board, seed stall, old maple, bench/rest pocket, and readable footpaths.
- Keep the old Village source as quality reference only: detail density, material softness, foliage integration, and cozy tone.
- Do not copy it as runtime replacement and do not split layers from it.

## Must Avoid

- no combat, monsters, damage, weapons, loot, or threat language.
- No hard-edged pasted roads, isolated sticker-like props, or unrelated recomposed layout.
- Not runtime replacement, not final art approval, not layer export approval, and not launch-quality approval.
