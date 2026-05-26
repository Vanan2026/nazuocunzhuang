# Village World2D v001 Production Prep

Status: accepted source with five exported review layers, not runtime replacement.

Current correction: the generated structure draft has been preserved under `02_source_generation/layout_structure_drafts/` and must not be split. The accepted storybook source now lives at `02_source_generation/village_painted_source.png`.

This package locks `Region_Village / VillagePlaza` as the next formal scene-art node. It prepares the source and layer contract for external or human art production, while keeping the active Godot route on the current authored blockout until human visual review approves a candidate.

## Canonical workflow

1. Use `01_layout_lock/layout_lock.json` and `01_layout_lock/registration_blueprint.svg` as the spatial contract.
2. Review the parent OutdoorWorld seamless master blueprint before final Village source art:
   - `production/assets/outdoor_world_world2d/v001/`.
3. Review the accepted source at `02_source_generation/village_painted_source.png`.
4. Review the five exported full-canvas layers under `03_layer_export/layers/`.
5. Confirm the recomposite and per-layer preview before any Godot runtime replacement.
6. Run Godot screenshot validation if runtime replacement is attempted later.

## Non-negotiable rules

- This package does not approve launch-quality art.
- `runtime_replacement` stays `false` until human visual review passes.
- Runtime layers must be registration-perfect with one shared canvas and origin.
- Transparent layers must not be cropped to object bounds.
- Hidden discovery remains environmental; do not bake quest labels or clue explanations into art.
- No combat, weapons, monsters, horror, copied franchise style, UI, or readable task text in runtime art.

## Current production entry files

- `workflow_manifest.json`
- `01_layout_lock/layout_lock.json`
- `01_layout_lock/registration_blueprint.md`
- `01_layout_lock/registration_blueprint.svg`
- `02_source_generation/source_brief.md`
- `02_source_generation/source_prompt_pack.md`
- `02_source_generation/layout_structure_drafts/village_layout_structure_draft_v001.png`
- `02_source_generation/true_source_candidates/village_true_painted_source_candidate_v001.png`
- `02_source_generation/true_source_candidates/village_true_painted_source_candidate_v001.json`
- `03_layer_export/layer_contract.json`
- `03_layer_export/layer_export_manifest.json`
- `03_layer_export/layers/`
- `05_review_and_qa/village_layer_export_review_preview_v001.png`
- `04_godot_integration/README.md`
- `05_review_and_qa/review_gate.md`
