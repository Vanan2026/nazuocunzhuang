# Protagonist Launch-Quality Asset Spec

Date: 2026-05-14

## Goal

Produce a launch-quality protagonist sprite set for the current Godot 4.6 2D/2.5D village slice.

The asset must preserve the current runtime contract:

- Runtime frame size: `192x288`
- Source slot size: `384x576`
- Animation count: 27
- Runtime frame count: 162
- Runtime resource: `sprites/characters/protagonist/player_mvp_4dir_frames.tres`
- No changes to `scripts/player_controller.gd` animation names or state wiring

## Art Direction

The protagonist should read as a quiet Japanese countryside girl suitable for a healing/exploration game.

Required visual traits:

- Hand-painted animation look with watercolor texture, not flat vector art.
- Soft but clear silhouette at game scale.
- Warm natural palette that fits Cloud Village and HomeArea.
- Modest rural outfit with believable cloth folds and a grounded daily-life feel.
- Consistent face, hair shape, body proportions, costume, and palette across all directions and animations.
- Professional sprite readability: no distorted hands, broken feet, melted accessories, or inconsistent limb length.

Avoid:

- Generic mobile-game chibi look.
- Overly glossy anime rendering.
- Fashion-poster posing.
- Heavy outlines that do not match the current environment.
- Backgrounds, shadows, labels, grids, or scenery inside sprite strips.

## Production Route A

Use AI generation as the primary art source.

Gate sequence:

1. Generate a front standing seed frame.
2. Review seed against the launch-quality art direction.
3. Generate a small proof set:
   - `player_idle_down` 4 frames
   - `player_walk_down` 8 frames
   - `player_walk_left` 8 frames
   - `player_walk_right` 8 frames
4. Review proof set for style consistency, limb quality, foot contact, and readable motion.
5. Generate all 27 source strips only after the proof set passes.
6. Build runtime frames with `tools/build_protagonist_from_production_strips.py`.
7. Run asset, motion, Godot import, scene load, transition, and visual walkthrough validation.

## Quality Gates

The set is not launch-quality unless all gates pass:

- Visual gate: seed and proof strips are approved by inspection.
- Consistency gate: no major drift in face, hair, outfit, scale, or palette between frames.
- Motion gate: side walk has clear lower-body motion and stable foot contact.
- Alpha gate: transparent edges are clean enough for in-scene compositing.
- Runtime gate: existing validators pass without changing gameplay/controller contracts.
- Evidence gate: seed preview, motion preview, and runtime scene preview are saved under `.codex/`.

## Current Baseline

The previous generated set is accepted only as engineering-ready placeholder art.

It is not considered launch-quality final art because it was produced by a deterministic procedural generator and lacks professional character-art detail, polish, and frame-level drawing quality.
