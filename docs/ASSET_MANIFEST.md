# Greenfield P0 Asset Manifest

参考母版：`production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg`

状态说明：

- `required`: P0 必须有正式路径。
- `placeholder_allowed`: 可先占位，但路径和替换机制必须正确。
- `review_ready`: 已有可审查资产，但不是最终审批。
- `approved`: 需要人工明确审批后才能使用。

## Scene Assets

| Asset | Path | Size | Status | Purpose |
|---|---|---:|---|---|
| HomeArea mother | `assets/scenes/home_area/scene_home_area_mother.png` | 1920x1080 或区域画布 | required | 总设计母图 |
| HomeArea base | `assets/scenes/home_area/scene_home_area_base.png` | 同 mother | required | 地面、小屋、道路、水面底图 |
| HomeArea foreground | `assets/scenes/home_area/scene_home_area_foreground_occlusion.png` | 同 mother | required | 树冠、屋檐、栅栏、花丛遮挡 |
| HomeArea collision mask | `assets/scenes/home_area/scene_home_area_collision_mask.png` | 同 mother | placeholder_allowed | 不可通行区域 |
| HomeArea points | `assets/scenes/home_area/scene_home_area_interaction_points.json` | n/a | required | 门、水井、农田、信箱、NPC 点 |

Current review assets:

| Asset | Path | Status |
|---|---|---|
| Play-start house polish | `assets/art/greenfield_p0/playable_scene_polish/player_house_warm_room_v001.png` | review_ready |
| Play-start yard polish | `assets/art/greenfield_p0/playable_scene_polish/player_yard_storybook_ground_v001.png` | review_ready |
| Play-start bulletin prop | `assets/art/greenfield_p0/playable_scene_polish/player_yard_bulletin_board_v001.png` | review_ready |

## UI Kit Assets

| Asset | Path | Size | Status |
|---|---|---:|---|
| Paper panel | `assets/ui/panels/ui_panel_paper_01.png` | 512x512 9-slice | required |
| Wood panel | `assets/ui/panels/ui_panel_wood_01.png` | 512x512 9-slice | required |
| Button normal | `assets/ui/buttons/ui_button_normal.png` | 256x96 | required |
| Button hover | `assets/ui/buttons/ui_button_hover.png` | 256x96 | required |
| Button pressed | `assets/ui/buttons/ui_button_pressed.png` | 256x96 | required |
| Item slot | `assets/ui/slots/ui_slot_item.png` | 96x96 | required |
| Selected slot | `assets/ui/slots/ui_slot_selected.png` | 96x96 | required |
| Tab normal | `assets/ui/tabs/ui_tab_normal.png` | 160x72 | required |
| Tab active | `assets/ui/tabs/ui_tab_active.png` | 160x72 | required |
| Scrollbar | `assets/ui/widgets/ui_scrollbar.png` | 64x256 | placeholder_allowed |
| Checkbox on | `assets/ui/widgets/ui_checkbox_on.png` | 64x64 | placeholder_allowed |
| Checkbox off | `assets/ui/widgets/ui_checkbox_off.png` | 64x64 | placeholder_allowed |
| Coin icon | `assets/ui/icons/ui_icon_coin.png` | 64x64 | required |
| Heart icon | `assets/ui/icons/ui_icon_heart.png` | 64x64 | required |
| Sun icon | `assets/ui/icons/ui_icon_weather_sun.png` | 64x64 | required |
| Rain icon | `assets/ui/icons/ui_icon_weather_rain.png` | 64x64 | required |
| Bag icon | `assets/ui/icons/ui_icon_bag.png` | 64x64 | required |
| Map icon | `assets/ui/icons/ui_icon_map.png` | 64x64 | required |
| Settings icon | `assets/ui/icons/ui_icon_settings.png` | 64x64 | required |

## Item Icons

| Id | Path | Status |
|---|---|---|
| log | `assets/items/icons/icon_log.png` | required |
| stone | `assets/items/icons/icon_stone.png` | required |
| branch | `assets/items/icons/icon_branch.png` | required |
| leaf | `assets/items/icons/icon_leaf.png` | required |
| flower_yellow | `assets/items/icons/icon_flower_yellow.png` | required |
| mushroom_red | `assets/items/icons/icon_mushroom_red.png` | required |
| mushroom_white | `assets/items/icons/icon_mushroom_white.png` | required |
| berry_red | `assets/items/icons/icon_berry_red.png` | required |
| orange | `assets/items/icons/icon_orange.png` | required |
| grape | `assets/items/icons/icon_grape.png` | required |
| egg | `assets/items/icons/icon_egg.png` | required |
| milk | `assets/items/icons/icon_milk.png` | required |
| cheese | `assets/items/icons/icon_cheese.png` | required |
| wheat | `assets/items/icons/icon_wheat.png` | required |
| fish | `assets/items/icons/icon_fish.png` | required |
| meat | `assets/items/icons/icon_meat.png` | required |
| cotton | `assets/items/icons/icon_cotton.png` | required |
| honey | `assets/items/icons/icon_honey.png` | required |
| jam | `assets/items/icons/icon_jam.png` | required |
| cookie | `assets/items/icons/icon_cookie.png` | required |

## Character Assets

| Asset | Path | Status |
|---|---|---|
| Player walk down | `assets/characters/player/char_player_walk_down.png` | required |
| Player walk up | `assets/characters/player/char_player_walk_up.png` | required |
| Player walk left | `assets/characters/player/char_player_walk_left.png` | required |
| Player walk right | `assets/characters/player/char_player_walk_right.png` | required |
| Player portrait neutral | `assets/characters/player/portrait_player_neutral.png` | required |
| Player portrait happy | `assets/characters/player/portrait_player_happy.png` | required |
| Player portrait shy | `assets/characters/player/portrait_player_shy.png` | placeholder_allowed |
| Aya portrait neutral | `assets/characters/npc/aya/portrait_npc_aya_neutral.png` | required |
| Aya portrait happy | `assets/characters/npc/aya/portrait_npc_aya_happy.png` | required |
| Aya portrait surprised | `assets/characters/npc/aya/portrait_npc_aya_surprised.png` | required |

## Data Files

| File | Purpose | Status |
|---|---|---|
| `data/items.json` | Item metadata and icon paths | required |
| `data/npcs.json` | NPC identity, portrait paths, schedule hooks | required |
| `data/gifts.json` | Gift preference and relationship deltas | required |
| `data/maps.json` | Area map data, unlock state, labels | required |

## Godot Scenes

| Scene | Purpose | Status |
|---|---|---|
| `scenes/world/HomeArea.tscn` | P0 explorable home area | required |
| `scenes/ui/HUD.tscn` | Main HUD | required |
| `scenes/ui/InventoryScreen.tscn` | Inventory | required |
| `scenes/ui/MapScreen.tscn` | Map | required |
| `scenes/ui/DialogueScreen.tscn` | Dialogue and choices | required |
| `scenes/ui/SettingsScreen.tscn` | Settings | required |

Current compatible route:

- `game/scenes/Main.tscn`
- `game/scenes/home/PlayerHouse.tscn`
- `game/scenes/world/PlayerYard.tscn`
- `game/scenes/ui/*`

These stay valid until a controlled migration creates the canonical `scenes/` mirror.

## Current HomeArea Package - 2026-05-27

| Asset | Path | Status |
|---|---|---|
| HomeArea mother | `assets/scenes/home_area/scene_home_area_mother.png` | review_ready_placeholder |
| HomeArea base | `assets/scenes/home_area/scene_home_area_base.png` | review_ready_placeholder |
| HomeArea foreground | `assets/scenes/home_area/scene_home_area_foreground_occlusion.png` | review_ready_placeholder |
| HomeArea collision mask | `assets/scenes/home_area/scene_home_area_collision_mask.png` | review_ready_placeholder |
| HomeArea points | `assets/scenes/home_area/scene_home_area_interaction_points.json` | review_ready_placeholder |
| HomeArea manifest | `assets/scenes/home_area/home_area_scene_manifest_v001.json` | review_ready_placeholder |
| HomeArea Godot scene | `game/scenes/world/HomeArea.tscn` | review_ready_placeholder |

## Current HUD Package - 2026-05-27

| Asset / Scene | Path | Status |
|---|---|---|
| Canonical HUD scene | `game/scenes/ui/HUD.tscn` | review_ready_placeholder |
| Current route HUD scene | `game/scenes/ui/TimeWeatherHUD.tscn` | review_ready_placeholder |
| HUD behavior script | `game/scenes/ui/TimeWeatherHUD.gd` | review_ready_placeholder |
| HUD validator | `tools/validate_greenfield_p0_hud.py` | active |
| HUD runtime validator | `tools/validate_greenfield_p0_hud.gd` | active |

## Current Inventory Screen Package - 2026-05-27

| Asset / Scene | Path | Status |
|---|---|---|
| Canonical inventory scene | `game/scenes/ui/InventoryScreen.tscn` | review_ready_placeholder |
| Current route inventory scene | `game/scenes/ui/InventoryUI.tscn` | review_ready_placeholder |
| Inventory behavior script | `game/scenes/ui/InventoryUI.gd` | review_ready_placeholder |
| Inventory data source | `game/data/items.json` | active |
| Inventory validator | `tools/validate_greenfield_p0_inventory_screen.py` | active |
| Inventory runtime validator | `tools/validate_greenfield_p0_inventory_screen.gd` | active |

Notes:

- Item icons are loaded from each item record's `icon` field instead of being hardcoded in the UI script.
- The full inventory screen remains hidden by default and is intended as a toggled screen, not persistent HUD density.

## Current Dialogue + Gift Package - 2026-05-27

| Asset / Scene / Data | Path | Status |
|---|---|---|
| Canonical dialogue screen | `game/scenes/ui/DialogueScreen.tscn` | review_ready_placeholder |
| Current route dialogue box | `game/scenes/ui/DialogueBox.tscn` | active |
| Dialogue behavior script | `game/scenes/ui/DialogueBox.gd` | active |
| Gift response data | `game/data/gifts.json` | active |
| NPC data with portraits | `game/data/npcs.json` | active |
| Dialogue gift validator | `tools/validate_greenfield_p0_dialogue_gift.py` | active |
| Dialogue gift runtime validator | `tools/validate_greenfield_p0_dialogue_gift.gd` | active |

Notes:

- `DialogueScreen.tscn` provides the P0 style-mother layout: NPC portrait, talk/gift/close options, GiftSelection, and RelationshipFeedback.
- Gift reactions are data-driven through `game/data/gifts.json`; NPC code falls back to existing like/dislike tags when no explicit gift row exists.

## Current Map Screen Package - 2026-05-27

| Asset / Scene / Data | Path | Status |
|---|---|---|
| Canonical map screen | `game/scenes/ui/MapScreen.tscn` | review_ready_placeholder |
| Map behavior script | `game/scenes/ui/MapScreen.gd` | active |
| Paper village map asset | `assets/ui/maps/ui_map_village_paper_01.png` | review_ready_placeholder |
| Map asset manifest | `assets/ui/maps/greenfield_p0_map_assets_manifest_v001.json` | active |
| Map data | `game/data/maps.json` | active |
| Map asset generator | `tools/generate_greenfield_p0_map_assets.py` | active |
| Map validator | `tools/validate_greenfield_p0_map_screen.py` | active |
| Map runtime validator | `tools/validate_greenfield_p0_map_screen.gd` | active |

Notes:

- MapScreen uses `game/data/maps.json` for numbered pins, location names, locked/unlocked state, NPC references, descriptions, and travel hints.
- The paper map PNG is a review-ready placeholder with `launch_quality_approved=false`; final hand-painted map art should replace the same asset path or update the manifest and validators together.

## Current External GPT Handoff - 2026-05-27

| File | Path | Status |
|---|---|---|
| Copyable production brief | `docs/GREENFIELD_P0_GPT_ASSET_PRODUCTION_BRIEF.md` | active |
| Small-batch handoff README | `production/assets/external_gpt_handoff/greenfield_p0/v002/README.md` | active |
| Small-batch request manifest | `production/assets/external_gpt_handoff/greenfield_p0/v002/asset_request_manifest.json` | active |
| Copy-paste prompt briefs | `production/assets/external_gpt_handoff/greenfield_p0/v002/prompt_briefs.md` | active |
| Handoff validator | `tools/validate_greenfield_p0_gpt_asset_handoff_v002.py` | active |

Notes:

- Use v002 for new GPT asset production. It splits requests into batches of 12 or fewer assets.
- v001 remains historical reference data and strict intake still supports it, but v002 is the current production handoff.
- The intake validator supports `--manifest`, so incoming art can be checked against v002 without changing the old v1 flow.

## Current Settings Screen Package - 2026-05-27

| Asset / Scene / Data | Path | Status |
|---|---|---|
| Canonical settings screen | `game/scenes/ui/SettingsScreen.tscn` | review_ready_placeholder |
| Settings behavior script | `game/scenes/ui/SettingsScreen.gd` | active |
| Settings preview placeholder | `assets/ui/screens/ui_settings_paper_preview.png` | review_ready_placeholder |
| Settings asset manifest | `assets/ui/screens/greenfield_p0_settings_screen_assets_manifest_v001.json` | active |
| Settings validator | `tools/validate_greenfield_p0_settings_screen.py` | active |
| Settings runtime validator | `tools/validate_greenfield_p0_settings_screen.gd` | active |

Notes:

- SettingsScreen uses the canonical Greenfield UI theme and shared UI Kit checkbox/slider styling.
- `assets/ui/screens/ui_settings_paper_preview.png` is a replaceable placeholder at the formal runtime path. A final approved PNG can overwrite the same file without code changes.

## Current Replaceable Asset Pipeline - 2026-05-27

| File | Path | Status |
|---|---|---|
| Central visual path registry | `game/systems/assets/GreenfieldAssetPaths.gd` | active |
| Missing/final-art demand report | `docs/MISSING_ASSETS_REPORT.md` | active |
| Pipeline validator | `tools/validate_greenfield_replaceable_asset_pipeline.py` | active |

Notes:

- Placeholder files now exist for every v002 `final_runtime_path`; this proves the stable replacement path contract before final art production.
- `docs/MISSING_ASSETS_REPORT.md` remains the authoritative list of art still missing final approval. File presence is not the same as human visual approval.
