# MountainHut Review Gate v001

Status: art_prep_ready_not_runtime_replacement

## Required Review Evidence

- Static package validation passes.
- `village_to_mountain_hut` seam brief exists and is referenced by the package and project manifest.
- Source generation uses the OutdoorWorld master blueprint, MountainHut layout lock, and Village reference.
- Future east-continuity screenshot includes both Village and MountainHut edges.
- runtime replacement remains blocked while this package is only art prep.

## Approval Rules

- `launch_quality_approved=false` until human review explicitly approves final art.
- `runtime_replacement=false` until source review, layer review, and Godot screenshot validation pass.
- `human visual review` is required before layer export.
- Runtime layers must derive from one accepted `mountain_hut_painted_source`.

## Rejection Conditions

- Road width, road material, ground color, or detail density visibly resets at the `village_to_mountain_hut` seam.
- Hut or props block the west seam path or future interaction prompt.
- Any art introduces combat, danger, damage, monster, weapon, hard survival, or pressure-read content.
- Transparent layers are cropped, auto-trimmed, or independently recomposed.
## Source Quality Gate Extension
- The current source candidate is marked `needs_repaint_before_layer_export` by `production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/source_quality_review_v001.json`.
- A passing structural validator is not enough to export layers.
- Before layer export, the team must either accept a source explicitly in human/art review or produce a v002 repaint from `production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/mountain_hut_repaint_v002_reference_board.png` and `production/assets/regions/mountain_hut_world2d/v001/02_source_generation/mountain_hut_repaint_v002_brief.md`.
- Runtime layers still must derive from one accepted full-canvas `painted_source`.
