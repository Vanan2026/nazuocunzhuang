# Village World2D v001 Review Gate

This package prepares formal art production. It does not approve launch-quality art and does not replace runtime art.

Current accepted source and layer review assets:

- Accepted source: `02_source_generation/village_painted_source.png`
- Layer export manifest: `03_layer_export/layer_export_manifest.json`
- Layer preview: `05_review_and_qa/village_layer_export_review_preview_v001.png`
- Approval gates: `human_visual_approval=true` for source acceptance, `human_layer_review=false`, `runtime_replacement=false`, `launch_quality_approved=false`.
- Current layer review result: semantic rework exported, pending review. The first split was rejected because it created broad sticker-like patches around houses, plants, props, and local ground texture.

## Source image gate

- The preserved structure/layout draft under `02_source_generation/layout_structure_drafts/` must not be split.
- The first true storybook candidate has been accepted as the canonical source for layer export.
- The OutdoorWorld seamless master blueprint remains the parent continuity reference for final Village source art.
- The source image uses the `1800x1200` registration blueprint.
- Roads, object zones, seam connectors, Aoi standing pocket, and return path remain readable.
- The village reads as a small plaza/social node, not a complete town.
- Hidden discovery is suggested by environment only.
- No character, UI, copied franchise style, readable quest text, weapon, monster, horror, or pressure imagery is baked into the art.

## Layer gate

- Semantic layer export has been generated for review from the accepted `village_painted_source`.
- Every runtime layer matches `1800x1200`.
- Every transparent runtime layer is full canvas with alpha outside painted areas.
- All layers derive from the accepted true `village_painted_source`.
- Weather, season, and time-of-day overlays are deferred to Godot/system-level treatment until seamless base continuity is stable.
- The current `base_ground` layer is the complete baked static scene.
- The current `terrain_details`, `behind_player_structures`, and `ysort_props_structures` layers are empty full-canvas runtime placeholders because those static pixels remain baked into the base.
- The current `foreground_occlusion` layer contains the old-maple foreground pixels that should visually cover the player.
- Any future Y-sort props must be split as semantic objects or authored groups, not rectangular scene patches.

## Godot gate

- Runtime replacement remains blocked until semantic layer review passes and a Godot screenshot pass is run.
- If integrated later, run Village authored slice, normal-input route, current objective, journal, and persistent main-flow validators.
- A display-backed screenshot pass is required before any launch-quality promotion.
