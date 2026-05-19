# HomeArea World2D v001 review gate

A source or layer package is not accepted until these checks pass by human review:

## Source image gate
- Structure matches camera_lock.json.
- House, paths, exits, left tree, right tree, well, mailbox, bench, and sign remain readable.
- No character, UI, combat, text, or copied franchise style is baked in.
- Player navigation space is visible and not visually blocked by broad foreground masses.

## Layer gate
- Every structural foreground layer is full-canvas transparent PNG.
- Base layer does not contain foreground occluders that should cover the player.
- No broad rectangle foreground plate is used.
- Props have pivot metadata if cropped.

## Godot gate
- Integration must wait until source and layer gates are accepted.
- Interactions and blockers are authored after approved art, not before.
