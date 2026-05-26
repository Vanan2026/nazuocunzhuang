# Village layer export review

Status: semantic rework exported, pending review. This is not runtime replacement or launch approval.

## Files

- Accepted source: `../02_source_generation/village_painted_source.png`
- Layer manifest: `../03_layer_export/layer_export_manifest.json`
- Layer folder: `../03_layer_export/layers/`
- Review preview: `village_layer_export_review_preview_v001.png`
- Recomposite preview: `../03_layer_export/village_layer_recomposite_preview.png`

## Exported layers

- `village_base_ground.png`
- `village_terrain_details.png`
- `village_behind_player_structures.png`
- `village_ysort_props_structures.png`
- `village_foreground_occlusion.png`

## Review notes

- Every layer keeps the full `1800x1200` canvas and shared origin.
- Transparent layers use alpha outside painted areas and are not cropped.
- Layers are deterministic mask-assisted review exports from one accepted source.
- Runtime replacement stays blocked.
- Previous review finding: the first v001 split preserved registration, but broad patches combined houses, plants, props, and nearby ground texture, which would read as sticker-like runtime art if wired directly into Godot.
- Semantic rework result: `village_base_ground.png` is now the complete baked static scene; `terrain_details`, `behind_player_structures`, and `ysort_props_structures` are empty full-canvas runtime placeholders.
- The only visible transparent runtime layer in this pass is `foreground_occlusion`, limited to the old-maple foreground pixels that can cover the player.
- Next gate: human review this semantic preview before any Godot screenshot/integration task.
