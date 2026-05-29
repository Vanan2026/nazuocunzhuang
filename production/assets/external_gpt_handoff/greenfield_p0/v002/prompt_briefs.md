# Greenfield P0 GPT Asset Requests v002

Use these as small copy-paste batches for external GPT image generation. Generate PNG only. Keep every output filename and size exact.

Incoming root:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/incoming/
```

Shared style lock for every batch:

```text
Warm low-saturation hand-painted storybook 2D art for a fixed 3/4 top-down cozy rural life simulation. Paper and wood UI language, soft foliage, readable silhouettes, rounded simple characters, gentle countryside mood, no combat.
```

Negative prompt for every batch:

```text
Do not copy any existing game, anime, movie, artist, map, character, or named style. No photorealism, no combat, no monsters, no weapons, no armor, no HP bars, no loot, no horror, no harsh neon, no sci-fi HUD, no watermark, no random text baked into UI or world art.
```

## Batch 01 UI Kit Core

Generate these 12 transparent PNGs. No text inside any UI asset.

```text
1. ui/core/ui_panel_paper_01.png, 512x512, transparent.
Paint a reusable parchment paper panel with subtle hand-painted fiber texture, soft uneven edges, warm cream color, no text. Must work as a 9-slice UI panel.

2. ui/core/ui_panel_wood_01.png, 512x512, transparent.
Paint a reusable warm wooden frame panel with paper inset feel, soft rural craft texture, no text. Must work as a 9-slice UI panel.

3. ui/core/ui_button_normal.png, 256x96, transparent.
Paint normal state of a small hand-made paper/wood button, no text, readable edge.

4. ui/core/ui_button_hover.png, 256x96, transparent.
Paint hover state of the same paper/wood button, slightly brighter and warmer, no text.

5. ui/core/ui_button_pressed.png, 256x96, transparent.
Paint pressed state of the same paper/wood button, slightly inset and darker, no text.

6. ui/core/ui_slot_item.png, 96x96, transparent.
Paint an empty inventory item slot, parchment center with small wooden edge, no icon, no text.

7. ui/core/ui_slot_selected.png, 96x96, transparent.
Paint selected inventory item slot state, same slot with warm highlighted edge, no icon, no text.

8. ui/core/ui_tab_normal.png, 160x72, transparent.
Paint inactive paper notebook tab, no text.

9. ui/core/ui_tab_active.png, 160x72, transparent.
Paint active paper notebook tab, no text, clear selected edge.

10. ui/core/ui_scrollbar.png, 64x256, transparent.
Paint a vertical parchment/wood scrollbar asset, no arrows, no text.

11. ui/core/ui_checkbox_on.png, 64x64, transparent.
Paint checked checkbox with hand-drawn green check mark, paper/wood frame, no text.

12. ui/core/ui_checkbox_off.png, 64x64, transparent.
Paint empty checkbox with paper/wood frame, no text.
```

## Batch 02 UI Icons Map Settings

Generate these 9 PNGs. Icons must be readable at 32 px. The map and settings screen are opaque review images.

```text
1. ui/icons/ui_icon_coin.png, 64x64, transparent. Cozy warm brass coin icon, no text.
2. ui/icons/ui_icon_heart.png, 64x64, transparent. Soft red relationship heart icon, no text.
3. ui/icons/ui_icon_weather_sun.png, 64x64, transparent. Gentle sun weather icon, no text.
4. ui/icons/ui_icon_weather_rain.png, 64x64, transparent. Soft rain cloud weather icon, no text.
5. ui/icons/ui_icon_bag.png, 64x64, transparent. Small cloth bag inventory icon, no text.
6. ui/icons/ui_icon_map.png, 64x64, transparent. Folded paper map icon, no text.
7. ui/icons/ui_icon_settings.png, 64x64, transparent. Wooden gear settings icon, no text.
8. ui/maps/ui_map_village_paper_01.png, 1024x640, opaque. Parchment village map background with roads, cottages, river, trees, fields, and blank space for numbered pins. No readable text and no baked numbers.
9. ui/screens/ui_settings_paper_preview.png, 1280x720, opaque. Full settings screen mother image: paper panel, wooden side tabs, sliders, checkboxes, note paper preview. No real readable text.
```

## Batch 03 HomeArea Component Pack

This batch **replaces the old HomeArea Full Canvas layer workflow**. Do not generate `scene_home_area_base.png`, `scene_home_area_foreground_occlusion.png`, `scene_home_area_collision_mask.png`, or `scene_home_area_review_contact.png` for this batch.

Generate these 12 standalone transparent PNG components for Godot assembly. Each component must be isolated, centered within its own canvas, and use real alpha transparency. Do not bake checkerboard, white, gray, or preview backgrounds into any transparent component.

All components must share the same visual language: fixed 3/4 top-down cozy rural game perspective, warm low-saturation hand-painted storybook style, no UI, no text, no characters, no combat.

```text
1. regions/home_area/components/home_house_body_01.png, 640x512, transparent.
Standalone cottage body component: plaster walls, wooden beams, green door, windows, shutters, stone foundation, front steps, and lower porch structure. No roof, no chimney, no ground, no background, no shadow plate.

2. regions/home_area/components/home_house_roof_01.png, 640x512, transparent.
Standalone cottage roof component matching the house body: warm terracotta tiles, chimney, roof ridge, roof eaves. No walls, no ground, no background.

3. regions/home_area/components/home_well_01.png, 256x256, transparent.
Standalone old stone well component with small wooden roof and bucket rope. No ground, no background.

4. regions/home_area/components/home_mailbox_01.png, 128x128, transparent.
Standalone rustic mailbox component on a wooden post. No readable text, no ground, no background.

5. regions/home_area/components/home_fence_horizontal_01.png, 256x128, transparent.
Standalone horizontal wooden fence segment. No ground, no background.

6. regions/home_area/components/home_fence_vertical_01.png, 128x256, transparent.
Standalone vertical wooden fence segment. No ground, no background.

7. regions/home_area/components/home_fence_corner_01.png, 192x192, transparent.
Standalone wooden fence corner component that connects horizontal and vertical fence pieces. No ground, no background.

8. regions/home_area/components/home_garden_plot_grown_01.png, 512x384, transparent.
Standalone mature garden plot component with tilled soil rows, leafy vegetables, and a small garden border. No surrounding ground, no background.

9. regions/home_area/components/home_tree_large_01.png, 512x512, transparent.
Standalone large leafy tree component with trunk and crown, suitable for YSort occlusion. No ground, no background.

10. regions/home_area/components/home_bush_flower_01.png, 192x160, transparent.
Standalone flowering bush component. No ground, no background.

11. regions/home_area/components/home_table_wood_01.png, 256x192, transparent.
Standalone small wooden yard table with simple rural details. No ground, no background.

12. regions/home_area/components/home_bridge_wood_01.png, 384x256, transparent.
Standalone small wooden bridge component for a stream crossing. No water, no ground, no background.
```

Recommended Godot assembly outputs after generation:

```text
regions/home_area/home_area_component_manifest.json
regions/home_area/home_area_godot_placement.json
regions/home_area/home_area_preview_mockup.png
```

These helper files can be authored after visual approval. They are not image-generation targets for this batch.

## Batch 04 P0 Portraits

Generate these 11 transparent 512x512 portraits. Keep each character internally consistent across expressions.

```text
1. characters/portraits/portrait_player_neutral.png - player neutral.
2. characters/portraits/portrait_player_happy.png - player happy.
3. characters/portraits/portrait_player_shy.png - player shy.
4. characters/portraits/npc_aoi_portrait_neutral_512.png - Aoi shopkeeper neutral.
5. characters/portraits/npc_aoi_portrait_happy_512.png - Aoi shopkeeper happy.
6. characters/portraits/npc_gen_portrait_neutral_512.png - Gen elder carpenter neutral.
7. characters/portraits/npc_gen_portrait_happy_512.png - Gen elder carpenter happy.
8. characters/portraits/npc_mika_portrait_neutral_512.png - Mika post runner neutral.
9. characters/portraits/npc_mika_portrait_happy_512.png - Mika post runner happy.
10. characters/portraits/npc_hana_portrait_neutral_512.png - Hana elder resident neutral.
11. characters/portraits/npc_hana_portrait_happy_512.png - Hana elder resident happy.
```

## Batch 05 Runtime Walk Sprites

Generate these 8 transparent sprite strips. Each strip is 512x128 with four 128x128 frames, fixed 3/4 top-down game proportions.

```text
1. characters/player/char_player_walk_down.png
2. characters/player/char_player_walk_up.png
3. characters/player/char_player_walk_left.png
4. characters/player/char_player_walk_right.png
5. characters/npc/npc_aoi_walk_down_4x128.png
6. characters/npc/npc_gen_walk_down_4x128.png
7. characters/npc/npc_mika_walk_down_4x128.png
8. characters/npc/npc_hana_walk_down_4x128.png
```

## Batch 06 Item Icons Core

Generate these 11 transparent 64x64 item icons. Readable at 32 px, centered, no background frame.

```text
1. items/icons/wood_64.png - small stack of wood.
2. items/icons/stone_64.png - rounded stone.
3. items/icons/wildflower_spring_64.png - spring wildflower gift.
4. items/icons/small_carp_64.png - small carp fish as a gentle food item.
5. items/icons/tea_leaf_64.png - tea leaves.
6. items/icons/persimmon_64.png - persimmon fruit.
7. items/icons/food_riceball_simple_64.png - simple riceball.
8. items/icons/food_persimmon_riceball_64.png - persimmon riceball.
9. items/icons/food_spring_soup_64.png - warm spring soup bowl.
10. items/icons/food_warm_tea_64.png - warm tea cup.
11. items/icons/old_bell_fragment_64.png - old bell fragment key item.
```

## Delivery

Place generated files under:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/incoming/
```

Preserve the relative paths exactly. After delivery, run:

```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py --manifest production\assets\external_gpt_handoff\greenfield_p0\v002\asset_request_manifest.json --allow-partial
```
