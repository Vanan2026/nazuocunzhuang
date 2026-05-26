# Godot Integration Boundary

No Village World2D v001 runtime replacement is allowed in this prep pass.

## Current runtime

- Active scene: `res://game/scenes/world/OutdoorWorld.tscn`
- Current Village content owner: `game/scenes/world/OutdoorWorld.gd::_add_village_authored_slice`
- Existing gates:
  - `tools/validate_village_authored_slice.py`
  - `tools/validate_village_authored_slice.gd`
  - `tools/validate_village_normal_input_route_review.py`
  - `tools/capture_village_normal_input_route.gd -- --check-only`

## Replacement gate

Runtime replacement can only start after:

1. `village_painted_source.png` exists and passes human visual review.
2. Every runtime layer is exported from the same source image at `1800x1200`.
3. Layer stack review confirms no notice, seed stall, OldMaple clue, Aoi stand point, or return path is hidden.
4. Existing Village route validators still pass.
5. A separate implementation task updates runtime paths and captures fresh screenshots.
