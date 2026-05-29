# Greenfield P0 Codex Tasks

目标：把 Greenfield style mother 拆成可生产资产、可开发系统和可验证 Godot P0 vertical slice。

## P0: 风格壳 Demo

### Task P0-01: UI Kit Foundation

交付：

- `ui/theme/greenfield_theme.tres`
- `ui/components/GFPanel.tscn`
- `ui/components/GFButton.tscn`
- `ui/components/GFItemSlot.tscn`
- `ui/components/GFTabBar.tscn`
- P0 UI Kit placeholder assets under `assets/ui/`

验收：

- 当前 HUD、Dialogue、Inventory 入口不再使用默认 Godot 裸样式。
- 所有 UI 组件复用 GreenfieldTheme 或 `GF*` 组件。
- 中心游玩区不被常驻 UI 遮挡。

### Task P0-02: HomeArea Component Scene Package

HomeArea 资产生产已切换为 **组件化生产 + Godot 拼装**。不要再按旧的 full-canvas `base/foreground_occlusion/collision_mask` 拆层方式生产新图。

交付：

- `assets/art/greenfield_p0/regions/home_area/components/home_house_body_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_house_roof_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_well_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_mailbox_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_fence_horizontal_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_fence_vertical_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_fence_corner_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_garden_plot_grown_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_tree_large_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_bush_flower_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_table_wood_01.png`
- `assets/art/greenfield_p0/regions/home_area/components/home_bridge_wood_01.png`
- `assets/scenes/home_area/scene_home_area_interaction_points.json`
- `assets/scenes/home_area/home_area_scene_manifest_v001.json`
- `game/scenes/world/HomeArea.tscn` or compatible `game/scenes/world/HomeArea.tscn`

验收：

- 玩家可移动。
- 门、水井、农田、信箱可交互。
- 碰撞阻止穿过小屋、水井、树、栅栏。
- 房屋 body / roof 分离，便于遮挡和 YSort。
- 组件均为独立透明 PNG，不带棋盘格、白底或灰底。
- Godot 拼装位置、pivot、collision 和 z/y-sort 可由 `home_area_godot_placement.json` 或场景节点维护。

### Task P0-03: HUD

交付：

- `scenes/ui/HUD.tscn`
- season/date/time/weather block
- coin/stamina/status block
- hotbar block

验收：

- HUD 使用纸木风格。
- 默认显示低遮挡。
- 与 Time/Weather/Inventory 数据连接。

### Task P0-04: Inventory Screen

交付：

- `scenes/ui/InventoryScreen.tscn`
- item grid
- category tabs
- item detail panel
- plus/minus or split amount controls
- `data/items.json` path-driven icon loading

验收：

- 可打开/关闭。
- 显示至少 20 个 P0 图标路径。
- 数量、分类、选中详情正常。
- 没有单个物品路径硬编码在 UI 脚本中。

### Task P0-05: Dialogue + Gift

交付：

- `scenes/ui/DialogueScreen.tscn`
- `GiftSelection` panel
- `RelationshipFeedback` panel
- `data/npcs.json`
- `data/gifts.json`

验收：

- 可与一个 NPC 对话。
- 可选择礼物。
- 送礼改变关系值。
- 显示好感反馈。
- 立绘路径从 NPC 数据读取。

### Task P0-06: Map Screen

交付：

- `scenes/ui/MapScreen.tscn`
- `data/maps.json`
- location pins
- lock/unlock display

验收：

- 可打开/关闭地图。
- 地点编号、名称、锁定状态来自数据。
- 视觉上像纸质村庄地图，而不是 debug list。

### Task P0-07: Settings Screen

交付：

- `scenes/ui/SettingsScreen.tscn`
- music/sfx/ambient sliders
- display/language controls
- save/apply/cancel buttons

验收：

- 控件使用 Greenfield UI Kit。
- 设置值可读写。
- 面板不影响正常游玩输入。

## P1: 内容扩展

- Village map integration.
- NPC schedule display on map.
- More NPC portraits and expressions.
- Seasonal variants for HomeArea components.
- Weather-specific scene overlays.
- Relationship journal.

## P2: 生产效率

- Asset intake validator.
- UI Kit screenshot regression.
- HomeArea component manifest validator.
- Map data validator.
- Gift balance validator.
- Batch request generator for external art production.

## 当前下一步

继续执行 `batch_03_home_area_component_pack`，先产出 HomeArea 12 个核心组件，再由 Codex/Godot 做 placement、pivot、collision、YSort 拼装。
