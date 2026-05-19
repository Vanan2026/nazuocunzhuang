# Region_HomeArea Blockout Prompt Pack v001

## Purpose
Use this after human approval of the 3D blockout. It is an art-production brief, not runtime content.

## Style Lock
Warm low-saturation Japanese countryside storybook feeling, fixed top-down 3/4 perspective, soft hand-painted texture, clear silhouettes, Godot-ready 2D layered PNGs. No combat, monsters, weapons, blood, dark fantasy, photorealism, neon, text, watermark, or imitation of any named existing game/anime.

## Blockout Source
- Scene: `res://scenes/dev/region_home_area_blockout_3d_v002.tscn`
- Layout: `production/assets/regions/home_area_design/region_home_area_layout_v001.json`
- Manifest: `production/assets/regions/home_area_blockout/v001/region_home_area_blockout_manifest.json`
- Review image: `production/assets/regions/home_area_blockout/v001/region_home_area_blockout_review.png`

## Required Output Policy
Generate one coherent HomeArea art package from the approved blockout. Do not collage v002-v004 repair layers. Full plate is review-only. Runtime uses separated transparent layers.

## Required v005 Layers
- `region_home_area_ground_yard_v005.png`
- `region_home_area_path_village_road_v005.png`
- `region_home_area_path_back_farm_v005.png`
- `region_home_area_house_body_v005.png`
- `region_home_area_house_roof_occluder_v005.png`
- `region_home_area_veranda_floor_v005.png`
- `region_home_area_tree_left_trunk_v005.png`
- `region_home_area_tree_left_canopy_occluder_v005.png`
- `region_home_area_tree_right_trunk_v005.png`
- `region_home_area_tree_right_canopy_occluder_v005.png`
- `region_home_area_foreground_grass_v005.png`
- `region_home_area_shadow_dappled_v005.png`
- `region_home_area_light_overlay_v005.png`

## Review Gates
- Player scale must read against the house, grass, trees, props, and paths.
- Foreground grass may frame only the edges and must not wash over the player or primary paths.
- Tree canopy occluders need real transparent holes between leaf clusters.
- BackFarm and Village exits remain visually readable.
- No baked player, NPC, animal, UI text, or watermark.
