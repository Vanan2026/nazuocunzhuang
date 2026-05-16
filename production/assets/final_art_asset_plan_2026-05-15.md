# Final Art Asset Production Plan - 2026-05-15

## Goal
Produce launch-quality, game-ready art assets for the current vertical slice without replacing runtime references until each batch passes manifest, visual, and Godot load checks.

## Source Of Truth
- Art direction: `docs/04_ART_DIRECTION_BIBLE.md`
- Asset rules: `docs/05_ART_ASSET_BIBLE.md`
- Prompt library: `docs/06_AI_ASSET_PROMPT_LIBRARY.md`
- Palette: `data/style_palette.json`
- Catalog: `data/asset_catalog.csv`
- HomeArea design: `production/assets/regions/home_area_design/region_home_area_layout_v001.json`

## Pipeline Status
There was no separate pipeline status before this task. The art pipeline status is now:

- `.codex/art_assets_status.md`

## Production Route
Use the existing HomeArea design-first route:

1. Audit existing production art.
2. Mark each asset as `reuse`, `repair`, or `regenerate`.
3. Build a batch manifest before generating or modifying images.
4. Produce or normalize PNGs into `production/assets/final_art/`.
5. Generate a contact sheet and alpha/readability report.
6. Only after approval, copy or reference assets from runtime scenes.

## Batch A - HomeArea Foundation
Target folder: `production/assets/final_art/home_area/foundation/`

| Asset | Size | Source | Gate |
|---|---:|---|---|
| `region_home_area_base_full_v001.png` | 6144x4096 | reuse/repair from v002 or regenerate from design | no baked characters, readable walkable space |
| `region_home_area_ground_yard_v001.png` | 6144x4096 | reuse/repair | low clutter, supports central walkable area |
| `region_home_area_path_village_road_v001.png` | 6144x4096 | reuse/repair | north exit readable |
| `region_home_area_path_back_farm_v001.png` | 6144x4096 | reuse/repair | southeast exit readable |
| `region_home_area_house_body_v001.png` | transparent layer | reuse/repair | house identity clear |
| `region_home_area_house_roof_occluder_v001.png` | transparent layer | reuse/repair | can occlude torso/head, not feet |
| `region_home_area_veranda_floor_v001.png` | transparent layer | reuse/repair | rest point readable |

## Batch B - Depth And Occlusion
Target folder: `production/assets/final_art/home_area/depth/`

| Asset | Source | Gate |
|---|---|---|
| `region_home_area_tree_left_trunk_v001.png` | reuse/repair | YSort trunk anchor defined |
| `region_home_area_tree_left_canopy_occluder_v001.png` | reuse/repair | edge alpha clean |
| `region_home_area_tree_right_trunk_v001.png` | reuse/repair | seasonal fruit tree identity |
| `region_home_area_tree_right_canopy_occluder_v001.png` | reuse/repair | occlusion limited |
| `region_home_area_foreground_grass_v001.png` | reuse/repair | edge-only foreground |
| `region_home_area_shadow_dappled_v001.png` | reuse/repair | transparent overlay |
| `region_home_area_light_overlay_v001.png` | reuse/repair | transparent overlay |

## Batch C - Interactable Props
Target folder: `production/assets/final_art/home_area/props/`

| Asset | Size | Gate |
|---|---:|---|
| `region_home_area_prop_mailbox_v001.png` | 128-256 | readable as mailbox at gameplay zoom |
| `region_home_area_prop_well_broken_v001.png` | 256-384 | restoration state clear |
| `region_home_area_prop_well_repaired_v001.png` | 256-384 | same footprint as broken |
| `region_home_area_prop_bench_v001.png` | 256 | rest point readable |
| `region_home_area_prop_road_sign_v001.png` | 128-256 | no readable text baked in |

## Batch D - NPC P0
Target folder: `production/assets/final_art/characters/npc/`

| NPC | Sprite | Portraits | Gate |
|---|---|---|---|
| Aoi | `npc_aoi_idle_down_128.png` | neutral, happy, thinking | grocery owner silhouette, warm and careful |
| Gen | `npc_gen_idle_down_128.png` | neutral, happy, thinking | old carpenter silhouette, tools as non-weapon craft props |
| Mika | `npc_mika_idle_down_128.png` | neutral, happy, thinking | post carrier silhouette, bag/hat/mail anchor |

## Batch E - Vertical Slice UI And Farming Gaps
Target folder: `production/assets/final_art/ui_and_crops/`

| Asset Group | Gate |
|---|---|
| sunny/cloudy/rainy weather icons | 64x64, no text, readable on HUD |
| turnip and strawberry crop stages | 64x64, 4 stages each |
| inventory slot/paper panel/wood button | nine-slice or scalable contract |

## Validation Plan
- Manifest check: every output has path, size, source, anchor, runtime layer, status.
- Alpha check: reject obvious matte/fringe and non-transparent backgrounds for sprite/prop/UI layers.
- Readability check: create 100%, 50%, and gameplay-scale contact sheets.
- Godot check: after runtime references are touched, load the target scene headlessly and render a snapshot.

## Current Next Step
Run the asset audit against existing `production/assets/regions/home_area_art/`, `production/assets/regions/home_area_launch/`, `sprites/environments/homeyard/`, and protagonist/NPC folders. Produce a reuse/repair/regenerate table before creating or changing image assets.
