# OutdoorWorld Seamless Art Review Gate

This package does not approve launch-quality art and does not replace runtime art.

## Before Region Source Generation

- Human review confirms world-level region placement and route continuity.
- Village current structure draft is treated only as a layout reference.
- Region source requests include this master blueprint plus local layout locks.

## Before Layer Export

- One true opaque `painted_source` exists for the region.
- The source reads as final storybook scene art, not a structure diagram.
- Layer export uses only that source composition.

## Before Runtime Replacement

- Full-canvas layers validate.
- Godot screenshot review confirms seams, prompts, NPC standing pockets, and player occlusion.
- `launch_quality_approved` remains false until explicit human visual approval.
