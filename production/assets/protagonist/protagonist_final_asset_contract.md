# Protagonist Final Asset Contract

## Goal

Produce the final protagonist sprite set for the explorable 2D world. The asset must feel grounded in `Region_HomeArea` and `Region_HomeBackFarm`: stable foot anchor, no scale drift between states, readable side-step animation, soft hand-painted edges, and no background remnants.

## Runtime Frame Contract

- Final frame file format: PNG with real alpha channel.
- Runtime frame size: `192x288`.
- Foot anchor: bottom-center, `(96, 270)` in runtime frame space.
- Lowest visible character alpha must land at `y=270`.
- Transparent padding is required; do not crop tightly to the hair or feet.
- Standing height must stay stable across `walk`, `idle`, and `interact` for the same direction, with no more than `3px` median-height drift.
- Do not bake shadows into the character frames. The runtime owns the ground shadow.

## Animation Set

| Animation | Directions | Frames per direction | Loop |
| --- | --- | ---: | --- |
| `player_walk_{dir}` | 8 | 8 | yes |
| `player_idle_{dir}` | 8 | 4 | yes |
| `player_interact_{dir}` | 8 | 6 | no |
| `player_sit_down_side` | side only | 6 | no |
| `player_sit_idle_side` | side only | 6 | yes |
| `player_stand_up_side` | side only | 6 | no |

Direction tokens must be exactly:

```text
down
down_left
left
up_left
up
up_right
right
down_right
```

Runtime filenames must be exactly:

```text
player_walk_down_00.png ... player_walk_down_07.png
player_walk_down_left_00.png ... player_walk_down_left_07.png
player_walk_left_00.png ... player_walk_left_07.png
player_walk_up_left_00.png ... player_walk_up_left_07.png
player_walk_up_00.png ... player_walk_up_07.png
player_walk_up_right_00.png ... player_walk_up_right_07.png
player_walk_right_00.png ... player_walk_right_07.png
player_walk_down_right_00.png ... player_walk_down_right_07.png
```

The same naming pattern applies to `idle` and `interact` with their frame counts.

## Source Production Contract

Use 2x production canvases, then normalize down to runtime frames.

- Source slot size: `384x576`.
- Source foot anchor: `(192, 540)`.
- Source sheet layout: one animation strip per direction, one row, fixed slot grid.
- Source background: transparent only.
- Do not include labels, grid lines, scenery, cast shadows, checkerboard, or colored backdrops in final source sheets.
- Keep the face, hair bun, blouse, skirt volume, sandals, and palette consistent with `sprites/characters/protagonist/source/protagonist_design_sheet.png`.

## Side-Walk Quality Requirement

The left/right walk cycles must show visible footwork, not body translation.

Required motion beats for each 8-frame side walk:

```text
00 neutral contact
01 rear foot lifts, front foot bears weight
02 passing pose, lifted foot moves forward
03 forward contact begins
04 opposite neutral contact
05 other rear foot lifts
06 passing pose
07 returns into loop
```

Acceptance criteria:

- Sandals/feet visibly alternate in at least four frames.
- Skirt hem may sway, but it must not hide all leg motion.
- The lower-body silhouette must change enough to pass `tools/validate_protagonist_final_asset_quality.py`.
- Horizontal body bob should be subtle; do not solve walk motion by sliding the entire character.

## Production Prompt Base

Use this prompt as the base for each source strip:

```text
Create a production-ready transparent PNG sprite animation strip for a cozy hand-painted 2D farming life game.
Character: young Japanese rural girl, soft black hair in a loose bun, cream long-sleeve blouse, muted blue-green long skirt, simple sandals, gentle low-saturation watercolor/anime background-painting style.
Keep the same character identity, same outfit proportions, same palette, same silhouette family, and stable body scale in every frame.
Transparent background with real alpha channel only. No scenery, no floor, no shadow, no labels, no grid, no checkerboard.
Use one row of exactly [N] evenly spaced frames, each frame centered in a 384x576 slot, bottom-center foot anchor at x=192 y=540.
The feet must stay grounded on the same baseline. Do not change character height between frames.
For side-walk strips, show clear alternating sandal/leg motion with passing poses; avoid sliding or floating.
Output as one clean sprite strip suitable for automated slicing.
```

Replace `[N]` with the required frame count and append the direction/action-specific sentence.

## Direction Notes

- `down`: face and torso visible, small relaxed steps, sandals alternate below skirt.
- `up`: back view, bun and blouse back visible, feet still alternate under skirt.
- `left` / `right`: strongest foot-read requirement; do not hide both legs behind the skirt.
- Diagonals: use real three-quarter poses, not blended cardinal frames.
- `interact`: simple reach/check/pick-up gesture, same footprint as idle.
- `sit_down_side` / `stand_up_side`: must start/end at the side-walk standing height.

## Validation

Run in this order after replacing frames:

```powershell
python tools/validate_protagonist_animation_assets.py
python tools/validate_protagonist_final_asset_quality.py
python tools/build_protagonist_mvp_from_sheet.py
```

Then run Godot import and scene checks before accepting the batch.
