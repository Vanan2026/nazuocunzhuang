# Project Direction Change: 2D to 2D-Driven 3D Transition

Date: 2026-05-12  
Project: 《那座村庄》

## Previous State

The project has been developed as a 2D / 2.5D Godot pipeline:

- 2D scene painting workflow
- transparent PNG assets
- tile/layer scene composition
- 2D character frame animations

## New Stage (Current)

The project now enters a **2D concept-art-driven 3D scene prototype stage**:

- 2D key art remains the visual blueprint and style baseline.
- 3D scene meshes are introduced incrementally for playable prototype workflows.
- 3D character and 3D scene preview are now part of the runtime experiment scope.

## What Stays Unchanged

Legacy 2D assets are retained and continue to be valid:

- concept art references
- UI
- 2D narrative/cutscene backgrounds
- art reference overlays and style calibration

No destructive migration is performed for existing 2D folders/scenes.

## Pipeline Strategy

This transition is **additive**, not replacement:

- Keep existing 2D pipeline.
- Add 3D intake/conversion/preview/check/report pipeline in parallel.
- Avoid full-project architecture rewrite in this phase.

Godot project target capability is hybrid:

- 2D UI
- 2D story/cutscene presentation
- 3D scenes
- 3D characters

## Asset Acceptance Policy (Current Phase)

AI-generated large meshes are **not treated as final shipping assets** at this stage.

Current use is limited to:

- preview validation
- import stability checks
- split/cleanup suggestions
- GLB pipeline verification

Only after cleanup, modularization, collision/navigation authoring, and performance checks can assets move toward production usage.
