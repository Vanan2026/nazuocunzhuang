# Missing Assets Report

Date: 2026-05-29

## Scope

- Greenfield P0 external GPT handoff assets.
- Runtime/formal-path files may already contain placeholders or review candidates.
- `present` only means a file path exists; it does not mean the final art is approved.

## Summary

- v002 handoff assets: 63
- Missing runtime placeholder files: 0
- Final approved art missing: all v002 assets remain review-ready until human visual approval.

## Replacement Rule

- Generated PNGs must be delivered under `production/assets/external_gpt_handoff/greenfield_p0/v002/incoming/`.
- The intake validator copies approved assets to each asset's `final_runtime_path`.
- UI assets replace existing UI textures without changing Godot scripts.
- HomeArea now uses a component-based Godot assembly workflow, not the deprecated full-canvas base/foreground/collision layer workflow.

## batch_01_ui_kit_core

| Asset | Formal runtime path | Expected size | File status | Final art status |
|---|---|---:|---|---|
| `ui_panel_paper_01` | `assets/ui/panels/ui_panel_paper_01.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_panel_wood_01` | `assets/ui/panels/ui_panel_wood_01.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_button_normal` | `assets/ui/buttons/ui_button_normal.png` | 256x96 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_button_hover` | `assets/ui/buttons/ui_button_hover.png` | 256x96 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_button_pressed` | `assets/ui/buttons/ui_button_pressed.png` | 256x96 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_slot_item` | `assets/ui/slots/ui_slot_item.png` | 96x96 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_slot_selected` | `assets/ui/slots/ui_slot_selected.png` | 96x96 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_tab_normal` | `assets/ui/tabs/ui_tab_normal.png` | 160x72 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_tab_active` | `assets/ui/tabs/ui_tab_active.png` | 160x72 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_scrollbar` | `assets/ui/widgets/ui_scrollbar.png` | 64x256 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_checkbox_on` | `assets/ui/widgets/ui_checkbox_on.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_checkbox_off` | `assets/ui/widgets/ui_checkbox_off.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |

## batch_02_ui_icons_map_settings

| Asset | Formal runtime path | Expected size | File status | Final art status |
|---|---|---:|---|---|
| `ui_icon_coin` | `assets/ui/icons/ui_icon_coin.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_icon_heart` | `assets/ui/icons/ui_icon_heart.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_icon_weather_sun` | `assets/ui/icons/ui_icon_weather_sun.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_icon_weather_rain` | `assets/ui/icons/ui_icon_weather_rain.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_icon_bag` | `assets/ui/icons/ui_icon_bag.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_icon_map` | `assets/ui/icons/ui_icon_map.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_icon_settings` | `assets/ui/icons/ui_icon_settings.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_map_village_paper_01` | `assets/ui/maps/ui_map_village_paper_01.png` | 1024x640 | placeholder_or_current_file_present | missing_final_approved_art |
| `ui_settings_paper_preview` | `assets/ui/screens/ui_settings_paper_preview.png` | 1280x720 | placeholder_or_current_file_present | missing_final_approved_art |

## batch_03_home_area_component_pack

| Asset | Formal runtime path | Expected size | File status | Final art status |
|---|---|---:|---|---|
| `home_house_body_01` | `assets/art/greenfield_p0/regions/home_area/components/home_house_body_01.png` | 640x512 | pending_generation | missing_final_approved_art |
| `home_house_roof_01` | `assets/art/greenfield_p0/regions/home_area/components/home_house_roof_01.png` | 640x512 | pending_generation | missing_final_approved_art |
| `home_well_01` | `assets/art/greenfield_p0/regions/home_area/components/home_well_01.png` | 256x256 | pending_generation | missing_final_approved_art |
| `home_mailbox_01` | `assets/art/greenfield_p0/regions/home_area/components/home_mailbox_01.png` | 128x128 | pending_generation | missing_final_approved_art |
| `home_fence_horizontal_01` | `assets/art/greenfield_p0/regions/home_area/components/home_fence_horizontal_01.png` | 256x128 | pending_generation | missing_final_approved_art |
| `home_fence_vertical_01` | `assets/art/greenfield_p0/regions/home_area/components/home_fence_vertical_01.png` | 128x256 | pending_generation | missing_final_approved_art |
| `home_fence_corner_01` | `assets/art/greenfield_p0/regions/home_area/components/home_fence_corner_01.png` | 192x192 | pending_generation | missing_final_approved_art |
| `home_garden_plot_grown_01` | `assets/art/greenfield_p0/regions/home_area/components/home_garden_plot_grown_01.png` | 512x384 | pending_generation | missing_final_approved_art |
| `home_tree_large_01` | `assets/art/greenfield_p0/regions/home_area/components/home_tree_large_01.png` | 512x512 | pending_generation | missing_final_approved_art |
| `home_bush_flower_01` | `assets/art/greenfield_p0/regions/home_area/components/home_bush_flower_01.png` | 192x160 | pending_generation | missing_final_approved_art |
| `home_table_wood_01` | `assets/art/greenfield_p0/regions/home_area/components/home_table_wood_01.png` | 256x192 | pending_generation | missing_final_approved_art |
| `home_bridge_wood_01` | `assets/art/greenfield_p0/regions/home_area/components/home_bridge_wood_01.png` | 384x256 | pending_generation | missing_final_approved_art |

## batch_04_p0_portraits

| Asset | Formal runtime path | Expected size | File status | Final art status |
|---|---|---:|---|---|
| `portrait_player_neutral` | `assets/characters/player/portrait_player_neutral.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `portrait_player_happy` | `assets/characters/player/portrait_player_happy.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `portrait_player_shy` | `assets/characters/player/portrait_player_shy.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_aoi_portrait_neutral` | `assets/art/portraits/npc_aoi_portrait_neutral_512.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_aoi_portrait_happy` | `assets/art/portraits/npc_aoi_portrait_happy_512.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_gen_portrait_neutral` | `assets/art/portraits/npc_gen_portrait_neutral_512.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_gen_portrait_happy` | `assets/art/portraits/npc_gen_portrait_happy_512.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_mika_portrait_neutral` | `assets/art/portraits/npc_mika_portrait_neutral_512.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_mika_portrait_happy` | `assets/art/portraits/npc_mika_portrait_happy_512.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_hana_portrait_neutral` | `assets/art/portraits/npc_hana_portrait_neutral_512.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_hana_portrait_happy` | `assets/art/portraits/npc_hana_portrait_happy_512.png` | 512x512 | placeholder_or_current_file_present | missing_final_approved_art |

## batch_05_runtime_walk_sprites

| Asset | Formal runtime path | Expected size | File status | Final art status |
|---|---|---:|---|---|
| `char_player_walk_down` | `assets/characters/player/char_player_walk_down.png` | 512x128 | placeholder_or_current_file_present | missing_final_approved_art |
| `char_player_walk_up` | `assets/characters/player/char_player_walk_up.png` | 512x128 | placeholder_or_current_file_present | missing_final_approved_art |
| `char_player_walk_left` | `assets/characters/player/char_player_walk_left.png` | 512x128 | placeholder_or_current_file_present | missing_final_approved_art |
| `char_player_walk_right` | `assets/characters/player/char_player_walk_right.png` | 512x128 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_aoi_walk_down` | `assets/art/characters/npc/npc_aoi_walk_down_4x128.png` | 512x128 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_gen_walk_down` | `assets/art/characters/npc/npc_gen_walk_down_4x128.png` | 512x128 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_mika_walk_down` | `assets/art/characters/npc/npc_mika_walk_down_4x128.png` | 512x128 | placeholder_or_current_file_present | missing_final_approved_art |
| `npc_hana_walk_down` | `assets/art/characters/npc/npc_hana_walk_down_4x128.png` | 512x128 | placeholder_or_current_file_present | missing_final_approved_art |

## batch_06_item_icons_core

| Asset | Formal runtime path | Expected size | File status | Final art status |
|---|---|---:|---|---|
| `wood_64` | `assets/art/items/wood_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `stone_64` | `assets/art/items/stone_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `wildflower_spring_64` | `assets/art/items/wildflower_spring_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `small_carp_64` | `assets/art/items/small_carp_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `tea_leaf_64` | `assets/art/items/tea_leaf_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `persimmon_64` | `assets/art/items/persimmon_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `food_riceball_simple_64` | `assets/art/items/food_riceball_simple_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `food_persimmon_riceball_64` | `assets/art/items/food_persimmon_riceball_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `food_spring_soup_64` | `assets/art/items/food_spring_soup_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `food_warm_tea_64` | `assets/art/items/food_warm_tea_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |
| `old_bell_fragment_64` | `assets/art/items/old_bell_fragment_64.png` | 64x64 | placeholder_or_current_file_present | missing_final_approved_art |

## Deprecated / Removed From Active Demand

The following old HomeArea full-canvas layer assets are no longer part of the external GPT asset request because they caused ambiguity and poor generation reliability:

- `scene_home_area_base.png`
- `scene_home_area_foreground_occlusion.png`
- `scene_home_area_collision_mask.png`
- `scene_home_area_review_contact.png`

Use `batch_03_home_area_component_pack` instead.

## Current P0 Screen Coverage

- `game/scenes/ui/HUD.tscn`: present
- `game/scenes/ui/InventoryScreen.tscn`: present
- `game/scenes/ui/MapScreen.tscn`: present
- `game/scenes/ui/DialogueScreen.tscn`: present
- `game/scenes/ui/SettingsScreen.tscn`: present
- `game/scenes/world/HomeArea.tscn`: present as legacy review scene until component placement is integrated.

## Next Asset Demand

1. Batch 01 UI Kit Core: replace paper/wood panels, buttons, slots, tabs, scrollbar, checkboxes first.
2. Batch 02 UI Icons/Map/Settings: replace HUD icons, paper map, and settings preview next.
3. Batch 03 HomeArea Component Pack: produce standalone components for Godot assembly.
4. Batch 04/05 Characters: replace player portraits and runtime walk strips, then NPC variants.
5. Batch 06 Item Icons: replace core item icons after UI readability is stable.
