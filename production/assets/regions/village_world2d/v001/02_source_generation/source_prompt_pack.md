# Village Plaza Source Prompt Pack

## Blueprint-first instruction

Before producing final art, use `01_layout_lock/registration_blueprint.svg` and `01_layout_lock/layout_lock.json` to confirm the spatial plan. The blueprint is a registration guide, not a pixel-perfect painting trace.

Also use the parent OutdoorWorld seamless art master package before generating final Village art:

- `production/assets/outdoor_world_world2d/v001/`

The current generated Village image at `village_painted_source.png` is a structure/layout draft only. Do not split it into runtime layers.

The first true candidate for review is:

- `true_source_candidates/village_true_painted_source_candidate_v001.png`

It is not approved for layer export or runtime replacement until human review explicitly accepts it.

## Source prompt

Warm low-saturation storybook 2D game art, fixed top-down 3/4 rural village plaza view, clear readable silhouettes, soft hand-painted texture, clean outlines, cozy countryside life simulation. Create the confirmed `village_painted_source` mother image for `Region_Village / VillagePlaza`, exact canvas 1800x1200 px, fully opaque PNG. Use the registration blueprint as spatial guide: a small village plaza node with a west return path, a notice object, a modest seed advice stall, an old maple clue area, Aoi standing pocket near the stall, a bench below the plaza path, clear road junctions, and set-back houses/props. Keep player walk lanes and interaction pockets readable. This image becomes the only composition source for all runtime layers.

## Negative prompt

No copied named game, anime, movie, or artist style. No photorealism, combat, weapons, monsters, horror, aggressive expressions, readable task text, UI arrows, watermark, harsh neon, heavy black shadows, random crop, wrong perspective, or independently recomposed layers.

## Layer split instruction

After a true storybook source image is accepted, split or mask runtime layers from that same source composition. Do not regenerate each layer as a new scene. Every exported layer remains full canvas `1800x1200` with the same origin, scale, rotation, and perspective.

For the seamless MVP, use only `base_ground`, `terrain_details`, `behind_player_structures`, `ysort_props_structures`, and `foreground_occlusion`. Keep weather, season, and time-of-day treatment in Godot/system-level logic until world seams are visually stable.
