# 《那座村庄》Greenfield P0 美术资产与 Codex 开发执行文档

版本：2026-05-27
参考母版：`production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg`
定位：项目美术圣经 + 体验目标图的可执行拆解，不把参考图当作逐像素复刻对象。

## 1. 执行原则

Codex 的职责不是“照图画一张图”，而是把已经明确的视觉语言、资产清单、UI 结构、交互规则落成 Godot 4.x 项目中的可运行内容。

本项目的 Greenfield P0 目标是一个可交互游戏壳：

- 玩家能在 3/4 俯视 HomeArea 中移动和交互。
- UI 统一使用纸张、木框、藤蔓、小图标的 Greenfield 风格。
- 背包、地图、对话、送礼、设置这些核心界面可打开、可验证、可替换美术。
- 所有资源路径、数据和场景层级面向后续批量替换，而不是写死在单个脚本中。

## 2. 视觉目标

核心风格：

- 温暖低饱和。
- 手绘纸感与轻绘本质感。
- 固定 3/4 top-down。
- 木质边框、羊皮纸面板、藤蔓装饰。
- 庭院、农田、水井、桥、树林、小屋等乡村慢生活元素。
- Q 版 3.5 到 4 头身小人，地图行走角色和半身立绘分开生产。

禁止方向：

- 不复制任何具体商业游戏或动画的画面。
- 不做战斗、怪物、武器、伤害、击杀或战利品掉落。
- 不使用科幻 HUD、霓虹高饱和、黑暗恐怖、写实照片风。
- 不把 manifest 坐标当作笔触级像素描摹要求；坐标是布局约束，绘画允许自然变化。

## 3. 五类可生产资产

### 3.1 Scene Assets

P0 先做 `home_area`，不要一次做全村。

```text
assets/scenes/home_area/
  scene_home_area_mother.png
  scene_home_area_base.png
  scene_home_area_foreground_occlusion.png
  scene_home_area_collision_mask.png
  scene_home_area_interaction_points.json
```

用途：

| 资产 | 用途 | 验收 |
|---|---|---|
| `mother` | 总设计母图，审美和布局对齐 | 非运行时源，可带完整前景 |
| `base` | 地面、道路、草地、水面、小屋主体等不可遮挡底图 | 玩家能站在其上，不含永久遮挡角色的树冠/屋檐 |
| `foreground_occlusion` | 树冠、屋檐、栅栏、花丛等可遮挡角色的前景 | 透明背景，和 base 同画布同原点 |
| `collision_mask` | 不可通行区域 | 与 base 布局一致，可脚本生成 CollisionPolygon2D |
| `interaction_points` | 门、水井、农田、信箱、NPC 点位 | JSON 数据驱动，不靠场景里散落命名猜测 |

Godot 场景目标：

```text
scenes/world/HomeArea.tscn
├── BaseSprite
├── YSortObjects
├── ForegroundOcclusion
├── CollisionLayer
├── InteractionPoints
├── NavigationRegion2D
└── PlayerSpawnPoint
```

注册规则：

- `mother/base/foreground_occlusion/collision_mask` 必须共享画布尺寸、原点、比例和透视。
- `foreground_occlusion` 不裁剪到物体 bbox，保持 full-canvas alpha。
- 后续分层必须从同一个 `mother` 或批准的 `base` 派生，不能独立重画成不同构图。

### 3.2 UI Kit Assets

UI Kit 优先级最高。先统一主题，再做具体界面。

```text
assets/ui/panels/ui_panel_paper_01.png
assets/ui/panels/ui_panel_wood_01.png
assets/ui/buttons/ui_button_normal.png
assets/ui/buttons/ui_button_hover.png
assets/ui/buttons/ui_button_pressed.png
assets/ui/slots/ui_slot_item.png
assets/ui/slots/ui_slot_selected.png
assets/ui/tabs/ui_tab_normal.png
assets/ui/tabs/ui_tab_active.png
assets/ui/widgets/ui_scrollbar.png
assets/ui/widgets/ui_checkbox_on.png
assets/ui/widgets/ui_checkbox_off.png
assets/ui/icons/ui_icon_coin.png
assets/ui/icons/ui_icon_heart.png
assets/ui/icons/ui_icon_weather_sun.png
assets/ui/icons/ui_icon_weather_rain.png
assets/ui/icons/ui_icon_bag.png
assets/ui/icons/ui_icon_map.png
assets/ui/icons/ui_icon_settings.png
```

Godot 目标：

```text
ui/theme/greenfield_theme.tres
ui/components/GFPanel.tscn
ui/components/GFButton.tscn
ui/components/GFItemSlot.tscn
ui/components/GFTabBar.tscn
ui/screens/InventoryScreen.tscn
ui/screens/MapScreen.tscn
ui/screens/DialogueScreen.tscn
ui/screens/SettingsScreen.tscn
```

规则：

- 不允许每个界面单独手写一套样式。
- 所有按钮、面板、格子、标签页复用 `GreenfieldTheme` 或 `GF*` 组件。
- HUD 必须保护游玩区：左上时间天气、右上状态、底部快捷栏；中心和下中区域不常驻大面板。

### 3.3 Icon Assets

第一批 P0 item icons：

```text
assets/items/icons/icon_log.png
assets/items/icons/icon_stone.png
assets/items/icons/icon_branch.png
assets/items/icons/icon_leaf.png
assets/items/icons/icon_flower_yellow.png
assets/items/icons/icon_mushroom_red.png
assets/items/icons/icon_mushroom_white.png
assets/items/icons/icon_berry_red.png
assets/items/icons/icon_orange.png
assets/items/icons/icon_grape.png
assets/items/icons/icon_egg.png
assets/items/icons/icon_milk.png
assets/items/icons/icon_cheese.png
assets/items/icons/icon_wheat.png
assets/items/icons/icon_fish.png
assets/items/icons/icon_meat.png
assets/items/icons/icon_cotton.png
assets/items/icons/icon_honey.png
assets/items/icons/icon_jam.png
assets/items/icons/icon_cookie.png
```

数据结构：

```json
{
  "id": "flower_yellow",
  "name": "野花",
  "icon": "res://assets/items/icons/icon_flower_yellow.png",
  "type": "gift",
  "stackable": true,
  "max_stack": 99,
  "sell_price": 12,
  "tags": ["flower", "spring", "gift"]
}
```

规则：

- 图标路径只从 `data/items.json` 读取。
- 背包和送礼界面不得硬编码单个图标路径。
- 暂缺图标可以用 placeholder，但 placeholder 必须占用正式路径。

### 3.4 Character Assets

地图角色和对话立绘分开：

```text
assets/characters/player/char_player_walk_down.png
assets/characters/player/char_player_walk_up.png
assets/characters/player/char_player_walk_left.png
assets/characters/player/char_player_walk_right.png
assets/characters/player/portrait_player_neutral.png
assets/characters/player/portrait_player_happy.png
assets/characters/player/portrait_player_shy.png

assets/characters/npc/aya/portrait_npc_aya_neutral.png
assets/characters/npc/aya/portrait_npc_aya_happy.png
assets/characters/npc/aya/portrait_npc_aya_surprised.png
```

Godot 目标：

```text
Player.tscn
NPC.tscn
DialoguePortrait.gd
RelationshipData.gd
```

规则：

- 行走角色：Q 版 3/4 俯视，脚底中心为 origin。
- 半身立绘：用于 DialogueScreen、GiftSelection、RelationshipFeedback。
- NPC 识别靠轮廓、服装色块和小物件，不靠复杂细节。

### 3.5 System Screens

参考图可拆成 5 个系统界面：

| 界面 | 系统 | P0 验收 |
|---|---|---|
| 主 HUD | 时间、季节、天气、金币、体力、快捷栏 | 默认可见，低遮挡 |
| 背包 | 物品、数量、分类、详情 | 可打开，数据驱动 |
| 地图 | 区域编号、地点、锁定状态 | 可打开，读取 `maps.json` |
| 对话/送礼 | NPC 文本、选项、礼物、反馈 | 可送礼并改变关系值 |
| 设置 | 音量、画面、语言、保存 | 可打开，控件风格统一 |

## 4. P0 Vertical Slice

P0 不追求完整村庄，先做一个风格壳 Demo：

1. 一个可行走的 `HomeArea` 场景。
2. 一个主 HUD。
3. 一个背包界面。
4. 一个 NPC 对话界面。
5. 一个送礼反馈界面。
6. 一个地图界面。
7. 一个设置界面。
8. 所有 UI 统一使用 Greenfield 风格。

## 5. 推荐目录

本项目已有 `game/` 与 `assets/` 路线，新增 P0 结构时优先对齐现有路径，避免大迁移。目标结构如下：

```text
assets/
  scenes/home_area/
  ui/panels/
  ui/buttons/
  ui/icons/
  ui/slots/
  items/icons/
  characters/player/
  characters/npc/
data/
  items.json
  npcs.json
  gifts.json
  maps.json
  dialogue/
scenes/
  world/HomeArea.tscn
  ui/HUD.tscn
  ui/InventoryScreen.tscn
  ui/MapScreen.tscn
  ui/DialogueScreen.tscn
  ui/SettingsScreen.tscn
scripts/
  core/
  inventory/
  dialogue/
  relationship/
  time/
  ui/
docs/
  ART_BIBLE.md
  ASSET_MANIFEST.md
  CODEX_TASKS.md
```

当前仓库存在 `game/scenes/...` 的可运行主流程。迁移时采用兼容策略：先在现有 `game/` route 内接入 P0 风格壳，再决定是否建立同名 `scenes/` 镜像目录。

## 6. Codex 执行顺序

### Phase 1: UI Kit

- `GreenfieldTheme`。
- `GFPanel`、`GFButton`、`GFItemSlot`、`GFTabBar`。
- HUD frame、dialogue box、inventory slot、map panel。
- 验证：所有当前 UI 入口使用统一主题，不再散落默认 Godot 样式。

### Phase 2: HomeArea

- `mother/base/foreground_occlusion/collision_mask/interaction_points`。
- `HomeArea.tscn` 层级。
- 可行走、可交互、可遮挡。
- 验证：玩家移动、碰撞、门/水井/农田/信箱交互、前景遮挡。

### Phase 3: Characters + Dialogue

- 主角四向行走。
- 第一名 NPC 地图 sprite 与三张立绘。
- `DialogueScreen`、`GiftSelection`、`RelationshipFeedback`。
- 验证：对话、送礼、关系变化。

### Phase 4: Items

- 20 个 P0 icons。
- `data/items.json` 路径接入。
- 背包分类、数量、详情。
- 验证：物品列表、图标加载、堆叠、选择。

### Phase 5: Map + Settings

- `MapScreen`。
- `SettingsScreen`。
- `maps.json`、设置存取。
- 验证：区域显示、锁定状态、音量/语言/画面控件。

## 7. 验收底线

P0 Demo 运行后必须满足：

1. 玩家可以进入 HomeArea 并移动。
2. 主 HUD 正常显示时间、季节、金币、体力、快捷栏。
3. 可以打开背包界面。
4. 可以打开地图界面。
5. 可以和一个 NPC 对话。
6. 可以给 NPC 送礼并看到关系反馈。
7. 可以打开设置界面。
8. 所有界面视觉统一为 Greenfield 手绘纸质木质风格。
9. 美术资源即使暂时是 placeholder，也保留正式路径和替换机制。

## 8. 当前仓库落地口径

当前已经存在的内容：

- `game/scenes/Main.tscn` 是当前可运行入口。
- `game/scenes/ui/GreenfieldUITheme.gd` 已做过一层 quiet UI polish。
- `assets/art/greenfield_p0/playable_scene_polish/` 是当前 Play 首屏 review-ready 资产。
- Village v003 是场景审查资产，不是运行时最终替换。

后续不要再让 Codex 按参考图即兴猜测。所有新增内容必须先落到：

- `docs/ART_BIBLE.md`
- `docs/ASSET_MANIFEST.md`
- `docs/CODEX_TASKS.md`
- 对应 validator

再进入 Godot 场景、脚本和资源接线。
