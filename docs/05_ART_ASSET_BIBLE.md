# 05 — 美术资产圣经：Asset Bible

版本：v1.0  
用途：给 Codex、AI 资产生成流程、Godot 导入流程提供统一资产规范。

---

## 1. 资产生产原则

《那座村庄》的美术资产必须服务游戏开发，而不是只服务单张图效果。

优先级：

```text
可读性 > 统一性 > 可复用性 > 氛围 > 单张精致度
```

所有资产必须：

- 可被 Godot 导入。
- 命名清楚。
- 可替换。
- 透明背景正确。
- 遵循固定 3/4 俯视视角。
- 不直接依赖任何受版权保护的风格描述。

---

## 2. 资产分类

```text
characters/       主角、NPC、动物
characters/sheets 动画帧或 spritesheet
environments/     场景底图、建筑、地形
tiles/            地块、道路、水、墙、地板
props/            道具、家具、交互物
crops/            作物阶段、果树
items/            背包物品图标
ui/               面板、按钮、图标、日历
fx/               光斑、落叶、雨、雪、烟
portraits/        对话头像
cg/               关键剧情插图，非 MVP 优先
```

---

## 3. 文件命名规范

### 3.1 通用格式

```text
[category]_[object]_[variant]_[state]_[direction]_[size].png
```

示例：

```text
chr_player_base_idle_down_128.png
chr_player_base_walk_left_sheet_512.png
npc_aoi_portrait_neutral_512.png
prop_mailbox_wood_default_128.png
env_house_player_exterior_spring_1024.png
tile_grass_spring_a_64.png
crop_turnip_stage_03_64.png
ui_icon_weather_rainy_64.png
```

### 3.2 方向缩写

| 方向 | 缩写 |
|---|---|
| down | down |
| up | up |
| left | left |
| right | right |
| down_left | dl |
| down_right | dr |
| up_left | ul |
| up_right | ur |

MVP 只要求四方向：`down / up / left / right`。

---

## 4. 分辨率与尺寸建议

### 4.1 角色

| 用途 | 建议尺寸 |
|---|---|
| 游戏内单帧角色 | 128x128 或 160x160 |
| 主角 spritesheet | 512x512 起，根据帧数扩展 |
| NPC 单帧 | 128x128 |
| 对话头像 | 512x512 |
| 小动物 | 64x64 或 96x96 |

### 4.2 地图与道具

| 用途 | 建议尺寸 |
|---|---|
| 地块 tile | 64x64 |
| 大地块 tile | 128x128 |
| 小道具 | 64x64 或 128x128 |
| 中型家具 | 128x128 或 256x256 |
| 建筑模块 | 256x256 到 1024x1024 |
| 场景底图 | 按地图实际尺寸切片 |

### 4.3 UI

| 用途 | 建议尺寸 |
|---|---|
| 小图标 | 32x32 / 64x64 |
| 物品图标 | 64x64 |
| 大图标 | 128x128 |
| 对话框九宫格 | 256x256 或 512x512 |
| UI 面板 | 512x512 起，九宫格拉伸 |

---

## 5. 原点与碰撞建议

### 5.1 角色原点

角色原点应位于脚底中心。

```text
sprite visual center: 画面中心偏上
origin: 脚底中心
collision: 脚底小椭圆/矩形
```

### 5.2 道具原点

| 道具类型 | 原点 |
|---|---|
| 小物件 | 底部中心 |
| 家具 | 底部中心或占地 tile 中心 |
| 墙面装饰 | 几何中心 |
| 作物 | tile 中心底部 |
| UI 图标 | 几何中心 |

---

## 6. 角色资产要求

### 6.1 主角基础包

MVP 必须制作：

```text
chr_player_base_idle_down.png
chr_player_base_idle_up.png
chr_player_base_idle_left.png
chr_player_base_idle_right.png
chr_player_base_walk_down_sheet.png
chr_player_base_walk_up_sheet.png
chr_player_base_walk_left_sheet.png
chr_player_base_walk_right_sheet.png
chr_player_base_water_down_sheet.png
chr_player_base_pickup_down_sheet.png
chr_player_base_interact_down_sheet.png
```

### 6.2 NPC 基础包

每名 NPC 至少需要：

```text
npc_[id]_idle_down.png
npc_[id]_idle_up.png
npc_[id]_idle_left.png
npc_[id]_idle_right.png
npc_[id]_portrait_neutral.png
npc_[id]_portrait_happy.png
npc_[id]_portrait_thinking.png
```

MVP 可先只做 `idle_down` 与 `portrait_neutral`，但数据结构要支持完整方向。

---

## 7. 作物资产要求

### 7.1 作物阶段

每种作物至少 4 阶段：

```text
stage_00_seeded
stage_01_sprout
stage_02_growing
stage_03_ready
```

可选：

```text
stage_04_harvested_regrow
stage_dead
```

### 7.2 命名示例

```text
crop_turnip_stage_00_64.png
crop_turnip_stage_01_64.png
crop_turnip_stage_02_64.png
crop_turnip_stage_03_64.png
```

---

## 8. 地图 tile 资产要求

### 8.1 MVP tile

```text
tile_grass_spring_a_64.png
tile_grass_spring_b_64.png
tile_dirt_dry_64.png
tile_dirt_wet_64.png
tile_field_tilled_dry_64.png
tile_field_tilled_wet_64.png
tile_stone_path_a_64.png
tile_wood_floor_a_64.png
tile_water_edge_a_64.png
tile_shadow_soft_64.png
```

### 8.2 季节变体

同一 tile 可有季节后缀：

```text
tile_grass_spring_a_64.png
tile_grass_summer_a_64.png
tile_grass_autumn_a_64.png
tile_grass_winter_a_64.png
```

---

## 9. 场景资产要求

### 9.1 主角家外景

必须拆为模块：

```text
env_house_player_wall_front.png
env_house_player_roof.png
env_house_player_door.png
env_house_player_window_a.png
env_house_player_engawa.png
env_house_player_shadow.png
```

不要只做一张不可拆的大图。大图可作为概念或背景，但最终交互场景应模块化。

### 9.2 标志性道具

MVP 优先级最高：

```text
prop_mailbox_wood_default_128.png
prop_well_old_broken_256.png
prop_well_old_repaired_256.png
prop_wind_chime_default_64.png
prop_persimmon_tree_spring_512.png
prop_persimmon_tree_autumn_fruit_512.png
prop_wooden_bridge_broken_512.png
prop_wooden_bridge_repaired_512.png
prop_shrine_bell_old_128.png
```

---

## 10. UI 资产要求

MVP UI 包：

```text
ui_panel_paper_9slice.png
ui_panel_wood_9slice.png
ui_button_default.png
ui_button_hover.png
ui_button_pressed.png
ui_icon_bag_64.png
ui_icon_map_64.png
ui_icon_calendar_64.png
ui_icon_weather_sunny_64.png
ui_icon_weather_rainy_64.png
ui_icon_weather_cloudy_64.png
ui_icon_coin_64.png
ui_icon_heart_leaf_64.png
ui_dialogue_nameplate.png
```

---

## 11. AI 资产生成流程

### 11.1 每批资产必须包含

1. 资产列表。
2. 风格锁定 prompt。
3. 单资产 prompt。
4. negative prompt。
5. 输出尺寸。
6. 文件名。
7. 是否透明背景。
8. 验收标准。

### 11.2 不合格资产重做条件

- 风格像写实照片。
- 视角不是 3/4 俯视。
- 角色过度插画化无法动画。
- 背景透明失败。
- 尺寸不符。
- 可交互物读不清。
- 细节过多导致缩小后糊。

---

## 12. 导入 Godot 规则

### 12.1 Texture Import

- Filter：根据最终像素密度测试。非像素风通常可开线性过滤，但 UI 图标需保持清晰。
- Repeat：tile 需要可重复时开启。
- Mipmaps：大场景可开，小 UI 可关。

### 12.2 Collision

- 美术不直接决定碰撞。
- 碰撞由 Godot 场景中 CollisionShape2D 定义。
- 每个 prop prefab 应有对应交互区域和碰撞区域。

---

## 13. 资产验收表

| 检查项 | 通过标准 |
|---|---|
| 命名 | 符合规范 |
| 透明 | PNG alpha 正确 |
| 视角 | 固定 3/4 俯视 |
| 风格 | 低饱和、温暖、绘本感 |
| 可读 | 缩小到游戏尺寸仍清楚 |
| 可复用 | 不依赖一次性背景 |
| 版权安全 | 未要求复制具体作品风格 |
| Godot 可用 | 可导入，无异常边缘 |
