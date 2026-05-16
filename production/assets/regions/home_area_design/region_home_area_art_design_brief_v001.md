# Region_HomeArea Art Design Brief v0.1

## Decision
Do not continue from engineering composites or arbitrary source-asset overlays.

The preview in `production/assets/regions/home_area_launch/v001/region_home_area_launch_preview.png` is rejected as a scene composition. It is visually high-detail in parts, but it is not a usable `Region_HomeArea` production base because it lacks a planned map composition, readable playable space, correct scale, and clean alpha edges.

## Production Goal
Create a launch-quality 2D/2.5D HomeArea scene for the current Godot runtime:

- Region: `Region_HomeArea`
- Runtime architecture: current 2D/2.5D `Node2D`, `Camera2D`, `YSortWorld`, `TileMapLayer`, `AnimatedSprite2D`
- Visual target: quiet Japanese countryside home yard, summer afternoon, warm low-saturation hand-painted anime background
- Gameplay target: readable walkable yard, house/veranda rest point, road to village, path to BackFarm, props/interactions, foreground occlusion

## Correct Workflow
Use one of two valid workflows:

1. Design first -> 3D blockout -> high-quality art production -> layer split -> Godot integration.
2. Design first -> high-quality full-scene base plate plus modular assets -> scene stitching/layering in Godot.

Do not:

- Use procedural engineering art as a mainline visual candidate.
- Stack unrelated existing image fragments and call the result launch-quality.
- Integrate assets before the scene composition and camera are approved.

## Scene Composition
The scene should be a playable wide home-yard map, not a close-up veranda illustration.

Required composition zones:

| Zone | Purpose | Visual Notes | Runtime Notes |
| --- | --- | --- | --- |
| House and veranda | Home identity, rest interaction, main landmark | One-story old wooden countryside house, porch/veranda, sliding doors, roof/eaves | YSort structure, roof/eaves can occlude player |
| Front yard | Main movement/readability space | Grass, packed soil, stepping stones, sparse flowers | Clear walkable zone, no dense visual clutter |
| North/village road | Exit direction and world continuity | Dirt/stone road leading out of yard | Must visually support village transition |
| BackFarm path | South/east path to farm | Narrow path behind/around house | Must align with BackFarm transition |
| Garden/props | Interaction density | well, mailbox/sign, bench, small garden details | Props separate with foot anchors/colliders |
| Trees/foreground | Depth and mood | 1-2 trees, foreground grass/leaves, dappled shadows | Split trunk/canopy/foreground occluders |
| Light/weather overlays | Atmosphere | soft dappled sunlight, optional dust/leaf particles | Transparent overlays only |

## Camera And Scale
- Use the current region canvas as the production reference: `6144 x 4096`.
- Maintain a fixed oblique 2D/2.5D camera language compatible with current protagonist scale.
- Preserve playable negative space around the player. The scene must read at gameplay zoom, not only as an illustration.
- The protagonist frame contract remains `192 x 288`, foot anchor `(96, 280)`.

## Required Deliverables
Produce high-quality art, not placeholders:

### Base Scene
- `region_home_area_base_full_v001.png`
  - Full source-space base plate or composition reference.
  - No baked player/NPC/animal.
  - Can include non-occluding ground, distant background, and fixed terrain.

### Runtime Layers
- Ground/path/detail:
  - `region_home_area_ground_yard_v001.png`
  - `region_home_area_path_village_road_v001.png`
  - `region_home_area_path_back_farm_v001.png`
  - `region_home_area_detail_ground_decals_v001.png`
- Structures:
  - `region_home_area_house_body_v001.png`
  - `region_home_area_house_roof_occluder_v001.png`
  - `region_home_area_veranda_v001.png`
- Trees/occlusion:
  - `region_home_area_tree_left_trunk_v001.png`
  - `region_home_area_tree_left_canopy_occluder_v001.png`
  - `region_home_area_tree_right_trunk_v001.png`
  - `region_home_area_tree_right_canopy_occluder_v001.png`
- Foreground/FX:
  - `region_home_area_foreground_grass_v001.png`
  - `region_home_area_foreground_leaves_v001.png`
  - `region_home_area_shadow_dappled_v001.png`
  - `region_home_area_light_overlay_v001.png`
- Props:
  - well, bench, mailbox/sign, small garden props as separate transparent PNGs with anchors.

## Layer Contract
Every runtime layer must include:

- file path
- origin in region pixels
- anchor type
- intended Godot parent
- z-index or YSort role
- occlusion role
- whether it can cover player feet/torso/head
- collision/walkable implication

## Acceptance Gate
Before Godot integration:

- The design composition is approved.
- The art package preview is visually acceptable at gameplay scale.
- PNG alpha is clean: no magenta/green/white matte fringe.
- No characters are baked into environment layers.
- Walkable space is readable.
- Occluders are intentionally split.
- Source files or generation prompts are stored beside exports.

After Godot integration:

- `Region_HomeArea` loads.
- Player scale and foot placement look correct.
- YSort and foreground occlusion work.
- Walkable/collision zones still match the art.
- HomeArea -> BackFarm and HomeArea -> Village exits remain readable.
