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

### Task P0-02: HomeArea Scene Package

交付：

- `assets/scenes/home_area/scene_home_area_mother.png`
- `assets/scenes/home_area/scene_home_area_base.png`
- `assets/scenes/home_area/scene_home_area_foreground_occlusion.png`
- `assets/scenes/home_area/scene_home_area_collision_mask.png`
- `assets/scenes/home_area/scene_home_area_interaction_points.json`
- `scenes/world/HomeArea.tscn` or compatible `game/scenes/world/HomeArea.tscn`

验收：

- 玩家可移动。
- 门、水井、农田、信箱可交互。
- 碰撞阻止穿过小屋、水井、树、栅栏。
- 前景遮挡可以盖住角色。
- 所有层共享画布和原点。

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
- Seasonal variants for HomeArea.
- Weather-specific scene overlays.
- Relationship journal.

## P2: 生产效率

- Asset intake validator.
- UI Kit screenshot regression.
- HomeArea layer alignment validator.
- Map data validator.
- Gift balance validator.
- Batch request generator for external art production.

## 当前下一步

优先执行 `Task P0-01: UI Kit Foundation`。原因：UI Kit 统一后，HUD、背包、地图、对话、送礼、设置都会立刻获得一致 Greenfield 视觉语言，也能减少后续每个界面单独修样式的返工。

## Current Next Step - 2026-05-27

`Task P0-01: UI Kit Foundation` and `Task P0-02: HomeArea Scene Package` now have executable assets, Godot scenes, and validators.

Next implementation priority: `Task P0-03: HUD`, followed by `Task P0-04: Inventory Screen`.

Reason: HomeArea now exists as a canonical scene package, so the next visible lift is a complete HUD/hotbar shell and then the full inventory screen using the canonical Greenfield UI Kit.

## Current Next Step - 2026-05-27 HUD Update

`Task P0-03: HUD` now has a complete Greenfield HUD shell, a canonical `game/scenes/ui/HUD.tscn`, and runtime validation.

Next implementation priority: `Task P0-04: Inventory Screen`.

Reason: the current route now has edge-mounted time/weather, money/energy/status, and hotbar surfaces. The next visible UI gap is the full inventory screen with category tabs, detail panel, data-driven item icons, and amount controls.

## Current Next Step - 2026-05-27 Inventory Update

`Task P0-04: Inventory Screen` now has a full Greenfield inventory shell, a canonical `game/scenes/ui/InventoryScreen.tscn`, and runtime validation.

Next implementation priority: `Task P0-05: Dialogue + Gift`.

Reason: the current route now has a data-driven item catalog, category tabs, item details, and quantity controls. The next visible experience gap is the style-mother dialogue/gift flow with NPC portrait, gift selection, and relationship feedback.

## Current Next Step - 2026-05-27 Dialogue Gift Update

`Task P0-05: Dialogue + Gift` now has a canonical `game/scenes/ui/DialogueScreen.tscn`, a data-driven `game/data/gifts.json`, and runtime validation.

Next implementation priority: `Task P0-06: Map Screen`, followed by `Task P0-07: Settings Screen`.

Reason: dialogue/gift now has NPC portrait space, gift selection, relationship feedback, and gifts data wiring. The next visible P0 gaps are map navigation/unlock presentation and the settings surface from the style mother.

## Current Next Step - 2026-05-27 Map Screen Update

`Task P0-06: Map Screen` now has a canonical `game/scenes/ui/MapScreen.tscn`, a paper village map asset, a data-driven `game/data/maps.json`, and runtime validation.

Next implementation priority: `Task P0-07: Settings Screen`.

Reason: MapScreen now displays numbered location pins, location list rows, locked/unlocked state, NPC names, descriptions, and travel hints from data. The remaining P0 UI surface from the style mother is Settings.

## Current Next Step - 2026-05-27 Replaceable Asset Pipeline Update

`Task P0-07: Settings Screen` now has a canonical `game/scenes/ui/SettingsScreen.tscn`, `game/scenes/ui/SettingsScreen.gd`, Greenfield checkbox/slider styling, and static/runtime validation.

Next implementation priority: run external art production in v002 small batches and replace approved PNGs at their `final_runtime_path`.

Reason: the P0 vertical-slice shell now covers HomeArea, HUD, Inventory, Dialogue/Gift, Map, and Settings with placeholder art at stable paths. The remaining work is final art production and visual approval, tracked in `docs/MISSING_ASSETS_REPORT.md`.
