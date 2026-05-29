# Greenfield P0 Asset Manifest

参考母版：`production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg`

状态说明：

- `required`: P0 必须有正式路径。
- `placeholder_allowed`: 可先占位，但路径和替换机制必须正确。
- `review_ready`: 已有可审查资产，但不是最终审批。
- `approved`: 需要人工明确审批后才能使用。

## Scene / Region Assets

### HomeArea Component Pack

HomeArea 已切换为 **组件化生产 + Godot 拼装**。旧的 `mother/base/foreground_occlusion/collision_mask` 全画布拆层工作流不再作为当前外部 GPT 生产需求。

| Asset | Path | Size | Status | Purpose |
|---|---|---:|---|---|
| `home_house_body_01` | `assets/art/greenfield_p0/regions/home_area/components/home_house_body_01.png` | 640x512 | required | 小屋墙体、门窗、地基、台阶 |
| `home_house_roof_01` | `assets/art/greenfield_p0/regions/home_area/components/home_house_roof_01.png` | 640x512 | required | 小屋屋顶、烟囱、屋檐 |
| `home_well_01` | `assets/art/greenfield_p0/regions/home_area/components/home_well_01.png` | 256x256 | required | 老井组件 |
| `home_mailbox_01` | `assets/art/greenfield_p0/regions/home_area/components/home_mailbox_01.png` | 128x128 | required | 信箱组件 |
| `home_fence_horizontal_01` | `assets/art/greenfield_p0/regions/home_area/components/home_fence_horizontal_01.png` | 256x128 | required | 横向围栏 |
| `home_fence_vertical_01` | `assets/art/greenfield_p0/regions/home_area/components/home_fence_vertical_01.png` | 128x256 | required | 纵向围栏 |
| `home_fence_corner_01` | `assets/art/greenfield_p0/regions/home_area/components/home_fence_corner_01.png` | 192x192 | required | 围栏转角 |
| `home_garden_plot_grown_01` | `assets/art/greenfield_p0/regions/home_area/components/home_garden_plot_grown_01.png` | 512x384 | required | 成熟菜地组件 |
| `home_tree_large_01` | `assets/art/greenfield_p0/regions/home_area/components/home_tree_large_01.png` | 512x512 | required | 大树组件，可用于 YSort 遮挡 |
| `home_bush_flower_01` | `assets/art/greenfield_p0/regions/home_area/components/home_bush_flower_01.png` | 192x160 | required | 花灌木组件 |
| `home_table_wood_01` | `assets/art/greenfield_p0/regions/home_area/components/home_table_wood_01.png` | 256x192 | required | 木桌组件 |
| `home_bridge_wood_01` | `assets/art/greenfield_p0/regions/home_area/components/home_bridge_wood_01.png` | 384x256 | required | 小木桥组件 |

Supporting files:

| Asset | Path | Status | Purpose |
|---|---|---|---|
| HomeArea interaction points | `assets/scenes/home_area/scene_home_area_interaction_points.json` | required | 门、水井、农田、信箱、NPC 点 |
| HomeArea component manifest | `assets/scenes/home_area/home_area_scene_manifest_v001.json` | active | Component contract and active asset list |
| HomeArea Godot scene | `game/scenes/world/HomeArea.tscn` | legacy_review_scene | Current scene remains available until component placement is integrated |

Deprecated HomeArea full-canvas assets are legacy placeholders only and must not be used as current GPT production targets:

- `assets/scenes/home_area/scene_home_area_base.png`
- `assets/scenes/home_area/scene_home_area_foreground_occlusion.png`
- `assets/scenes/home_area/scene_home_area_collision_mask.png`

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
| Paper map | `assets/ui/maps/ui_map_village_paper_01.png` | 1024x640 | required |
| Settings preview | `assets/ui/screens/ui_settings_paper_preview.png` | 1280x720 | required |

## Item Icons

Current item icon production source is `game/data/items.json` and the active external request is Batch 06 in:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/asset_request_manifest.json
```

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
| Aoi portrait neutral | `assets/art/portraits/npc_aoi_portrait_neutral_512.png` | required |
| Aoi portrait happy | `assets/art/portraits/npc_aoi_portrait_happy_512.png` | required |
| Gen portrait neutral | `assets/art/portraits/npc_gen_portrait_neutral_512.png` | required |
| Gen portrait happy | `assets/art/portraits/npc_gen_portrait_happy_512.png` | required |
| Mika portrait neutral | `assets/art/portraits/npc_mika_portrait_neutral_512.png` | required |
| Mika portrait happy | `assets/art/portraits/npc_mika_portrait_happy_512.png` | required |
| Hana portrait neutral | `assets/art/portraits/npc_hana_portrait_neutral_512.png` | required |
| Hana portrait happy | `assets/art/portraits/npc_hana_portrait_happy_512.png` | required |

## Data Files

| File | Purpose | Status |
|---|---|---|
| `game/data/items.json` | Item metadata and icon paths | required |
| `game/data/npcs.json` | NPC identity, portrait paths, schedule hooks | required |
| `game/data/gifts.json` | Gift preference and relationship deltas | required |
| `game/data/maps.json` | Area map data, unlock state, labels | required |

## Godot Scenes

| Scene | Purpose | Status |
|---|---|---|
| `game/scenes/world/HomeArea.tscn` | P0 explorable home area; currently legacy/full-canvas review scene until component placement is integrated | legacy_review_scene |
| `game/scenes/ui/HUD.tscn` | Main HUD | required |
| `game/scenes/ui/InventoryScreen.tscn` | Inventory | required |
| `game/scenes/ui/MapScreen.tscn` | Map | required |
| `game/scenes/ui/DialogueScreen.tscn` | Dialogue and choices | required |
| `game/scenes/ui/SettingsScreen.tscn` | Settings | required |

## Current External GPT Handoff

| File | Path | Status |
|---|---|---|
| Small-batch handoff README | `production/assets/external_gpt_handoff/greenfield_p0/v002/README.md` | active |
| Small-batch request manifest | `production/assets/external_gpt_handoff/greenfield_p0/v002/asset_request_manifest.json` | active |
| Copy-paste prompt briefs | `production/assets/external_gpt_handoff/greenfield_p0/v002/prompt_briefs.md` | active |
| Handoff validator | `tools/validate_greenfield_p0_gpt_asset_handoff_v002.py` | active |

Notes:

- Use v002 for new GPT asset production.
- Batch 03 is now component-based.
- The old full-canvas HomeArea generator is removed from active use.
