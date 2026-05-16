# 02 — 核心系统规格书

版本：v1.0  
用途：为 Codex 实现系统、拆分任务、写数据结构提供规格。

---

## 1. 系统总览

《那座村庄》的系统应以“日常生活”和“村庄恢复”为中心，而不是以战斗或数值碾压为中心。

```text
TimeManager
SeasonManager
WeatherManager
↓
WorldState
↓
Farming / Foraging / Fishing / Cooking / Crafting
↓
Inventory / Economy / Relationship / Quest
↓
Restoration / MapUnlock / NarrativeEvent
↓
SaveManager
```

---

## 2. 时间系统

### 2.1 基础字段

| 字段 | 类型 | 示例 |
|---|---|---|
| year | int | 1 |
| season | enum | spring |
| day | int | 1-28 |
| hour | int | 6-24 |
| minute | int | 0/10/20... |
| time_block | enum | morning / noon / afternoon / evening / night |

### 2.2 规则

- 每季 28 天。
- 一年 4 季。
- 起床默认 6:00。
- 23:00 后进入深夜提示。
- 24:00 后可自动回家睡觉，扣少量体力或次日稍晚起床，不做死亡惩罚。
- 室内可选择暂停或慢速流逝；建议 MVP 室内不暂停，菜单暂停。

### 2.3 事件信号

```gdscript
signal minute_changed(hour: int, minute: int)
signal day_started(date_info: Dictionary)
signal day_ended(date_info: Dictionary)
signal season_changed(season: String)
signal time_block_changed(block: String)
```

---

## 3. 季节系统

### 3.1 季节特征

| 季节 | 视觉 | 主要玩法 | 代表资源 |
|---|---|---|---|
| 春 | 新绿、樱花、浅粉 | 播种、认识村民、整理庭院 | 草莓、萝卜、野花 |
| 夏 | 浓绿、蝉声、强日光 | 钓鱼、祭典、夜晚活动 | 番茄、黄瓜、西瓜 |
| 秋 | 金黄、柿子、落叶 | 果园、料理、丰收 | 南瓜、柿子、蘑菇 |
| 冬 | 雪、暖灯、室内生活 | 手作、旧物、深层剧情 | 萝卜、干货、热汤 |

### 3.2 实现要求

- 作物用 `allowed_seasons` 控制。
- 地图资源点用季节过滤。
- NPC 对话按季节分组。
- 场景背景可先使用同一场景+色调/覆盖物变体，后续扩展完整季节图。

---

## 4. 天气系统

### 4.1 天气类型

| 天气 | 效果 |
|---|---|
| sunny | 正常天气，适合外出 |
| cloudy | 柔和光线，部分 NPC 对话变化 |
| rainy | 作物自动浇水，蘑菇/蜗牛类资源增加 |
| windy | 落叶、风铃、特殊传闻 |
| snowy | 冬季天气，部分路线关闭或资源变化 |
| foggy | 后山/神社相关秘密事件 |

### 4.2 规则

- 第二天天气在睡觉时生成。
- 雨天作物无需浇水。
- 天气可触发 NPC 对话、传闻、特殊采集点。
- 极端天气不作为惩罚，只作为变化。

---

## 5. 体力系统

### 5.1 设计目的

体力用于控制节奏，不用于惩罚玩家。

### 5.2 规则

- 初始体力 100。
- 浇水、砍小树枝、采石、钓鱼消耗体力。
- 走路、对话、送礼不消耗体力。
- 体力过低时不能进行重体力动作，但仍可社交、整理、回家。
- 吃料理可恢复体力。
- 不设置饥饿死亡。

---

## 6. 农田系统

### 6.1 数据字段

```yaml
crop_id: turnip_spring
name: 春萝卜
allowed_seasons: [spring]
grow_days: 4
regrow_days: 0
seed_item_id: seed_turnip
harvest_item_id: crop_turnip
water_required: true
base_sell_price: 60
quality_enabled: true
preferred_weather: sunny
```

### 6.2 地块状态

| 状态 | 说明 |
|---|---|
| empty | 空地 |
| tilled | 已开垦 |
| planted | 已播种 |
| watered | 当日已浇水 |
| ready | 可收获 |
| withered | 季节不符或长期未照料，MVP 可不启用 |

### 6.3 规则

- 地块每日结算一次成长。
- 当日浇水或雨天才增加成长天数。
- 作物成熟后可收获。
- 连作作物使用 `regrow_days`。
- MVP 可先不做作物品质，正式版扩展。

---

## 7. 果树系统

### 7.1 设计定位

果树是中长期投资，不与基础作物竞争。

### 7.2 规则

- 果树占用 2x2 或 3x3 空间。
- 生长期长。
- 到季节后每天或每隔数天产果。
- 柿子树是项目标志性资产，应有剧情关联。

---

## 8. 采集系统

### 8.1 资源点字段

```yaml
forage_id: spring_wildflower
spawn_area: village_path
seasons: [spring]
weather_bonus: [rainy]
spawn_chance: 0.35
max_per_day: 3
item_id: wildflower_spring
```

### 8.2 规则

- 每天起床生成资源点。
- 同一地点资源数量有限。
- 稀有资源与天气/季节/村庄状态相关。
- 采集物可用于料理、礼物、修复、供奉、图鉴。

---

## 9. 钓鱼系统

### 9.1 MVP 方案

低压力钓鱼：

1. 玩家选择水域交互。
2. 投竿后等待提示。
3. 在宽松时间窗内按键。
4. 成功获得鱼；失败可重试，只消耗少量时间。

### 9.2 鱼类字段

```yaml
fish_id: small_carp
name: 小鲫鱼
locations: [river, pond]
seasons: [spring, summer, autumn]
weather: [sunny, cloudy, rainy]
time_blocks: [morning, afternoon]
difficulty: 1
sell_price: 45
```

---

## 10. 料理系统

### 10.1 设计目的

料理连接农田、采集、NPC、节日和体力。

### 10.2 配方字段

```yaml
recipe_id: persimmon_riceball
name: 柿子饭团
ingredients:
  - item_id: rice
    count: 1
  - item_id: persimmon
    count: 1
result_item_id: food_persimmon_riceball
energy_restore: 25
relationship_tags: [homey, autumn, sweet]
unlock_condition: kitchen_level_1
```

### 10.3 规则

- 玩家需要厨房或火炉。
- 配方可通过 NPC、节日、书、旧物发现解锁。
- 食物可吃、送礼、卖出、用于任务。
- NPC 喜好不只看物品 ID，也可看标签。

---

## 11. 背包与物品系统

### 11.1 物品分类

| 分类 | 示例 |
|---|---|
| crop | 作物 |
| seed | 种子 |
| forage | 采集物 |
| fish | 鱼 |
| food | 料理 |
| material | 木材、石材、布料 |
| tool | 工具 |
| key | 钥匙、旧信、铃铛碎片 |
| furniture | 家具 |
| gift | 特殊礼物 |

### 11.2 规则

- 同 ID 物品可堆叠，工具和关键物品不可堆叠。
- 背包初始容量有限，可升级。
- 关键物品不能卖出。
- 数据由 `item_catalog` 驱动。

---

## 12. NPC 作息系统

### 12.1 NPC 数据字段

```yaml
npc_id: aoi
name: 葵
role: 杂货店店主
home_scene: npc_home_aoi
schedule_profile: shopkeeper_basic
likes: [flower, tea, sweet]
dislikes: [fish_raw]
birthday: spring_12
heart_events: [aoi_heart_2, aoi_heart_4]
```

### 12.2 作息字段

```yaml
schedule_id: shopkeeper_basic
entries:
  - season: any
    weather: not_rainy
    day_type: weekday
    time: "08:00"
    scene: village_shop
    marker: counter
  - time: "18:00"
    scene: village_path
    marker: walk_home
```

### 12.3 规则

- NPC 位置按时间块更新即可，MVP 不要求每分钟寻路。
- NPC 对话按上下文过滤：季节、天气、好感、事件、地点。
- 每天第一次对话给好感，重复对话不给或给极少。
- 每周送礼次数有限，防刷。

---

## 13. 对话系统

### 13.1 对话类型

| 类型 | 作用 |
|---|---|
| daily | 日常问候 |
| weather | 天气反应 |
| seasonal | 季节文本 |
| relationship | 好感文本 |
| event | 剧情事件 |
| rumor | 今日传闻 |
| festival | 节日文本 |

### 13.2 文本风格

- 简短、生活化。
- 不用过度诗化。
- 村民说话要有个人差异。
- 神秘线索不要直白解释。

示例：

```text
“雨停之前，山路最好别去。不是危险，只是容易迷路。”
```

---

## 14. 好感系统

### 14.1 好感等级

| 心数 | 解锁 |
|---|---|
| 0-1 | 基础对话 |
| 2 | 小支线、喜欢的礼物提示 |
| 4 | 个人问题、特殊地点对话 |
| 6 | 旧记忆或家庭背景 |
| 8 | 重要支线完成、村庄变化 |

### 14.2 好感来源

- 每日对话。
- 喜欢的礼物。
- 生日礼物。
- 完成委托。
- 参加相关事件。

---

## 15. 村庄修复系统

### 15.1 修复目标字段

```yaml
restoration_id: old_well
name: 旧水井
state: locked
required_items:
  - item_id: wood
    count: 20
  - item_id: stone
    count: 10
required_money: 500
required_relationship: null
unlocks:
  - water_source_yard
  - rumor_well_bell
visual_state_scene: old_well_repaired
```

### 15.2 规则

- 修复有视觉反馈。
- 修复要解锁功能、路线或剧情。
- 修复不是单纯资源消耗，应尽量和 NPC 事件挂钩。

---

## 16. 传闻系统

### 16.1 设计目的

让玩家每天有理由去村里走一圈。

### 16.2 规则

- 每天随机 1 到 3 条传闻。
- 传闻来源为 NPC、公告板、信箱、收音机。
- 传闻可能是生活提示、资源提示、事件提示、神秘线索。

示例：

```text
“邮差说，今天有一封没有收件人的信。”
“雨后的后山会长出白色的小蘑菇。”
“昨晚旧神社的铃响了一下，可风明明停了。”
```

---

## 17. 事件系统

### 17.1 事件触发条件

事件可以由以下条件组合触发：

- 日期/季节。
- 时间块。
- 天气。
- 地点。
- 携带物品。
- NPC 好感。
- 修复状态。
- 主线状态。
- 是否已看过某事件。

### 17.2 事件字段

```yaml
event_id: shrine_rain_night_01
type: narrative
conditions:
  season: autumn
  weather: rainy
  time_block: night
  scene: old_shrine
  has_item: old_bell_fragment
  flags_not_set: [seen_shrine_rain_night_01]
actions:
  - show_dialogue: shrine_rain_night_01
  - set_flag: seen_shrine_rain_night_01
  - add_rumor: rumor_bell_without_wind
```

---

## 18. 图鉴系统

### 18.1 分类

- 作物图鉴。
- 鱼类图鉴。
- 昆虫图鉴。
- 鸟类图鉴。
- 料理图鉴。
- 旧物图鉴。
- 传闻图鉴。
- 村庄修复记录。

### 18.2 规则

- 图鉴是长期目标，不强迫。
- 每项有获得方式提示，但不完全剧透。
- 旧物图鉴服务主线。

---

## 19. 保存系统

### 19.1 保存内容

- 时间日期季节。
- 玩家位置、背包、金钱、体力。
- 地块状态、作物成长。
- NPC 好感、事件 flag、今日对话记录。
- 修复状态。
- 已解锁配方、图鉴、地图。
- 天气与明天天气。

### 19.2 存档时机

- 睡觉时自动保存。
- 菜单可手动保存，MVP 可后置。
- 切换场景不一定保存，但必须保证状态不丢。

---

## 20. MVP 验收用最小流程

玩家应能完成以下流程：

```text
新建游戏
→ 在老屋醒来
→ 查看天气和信箱
→ 出门到庭院
→ 开垦地块
→ 播种
→ 浇水
→ 到村道和 NPC 对话
→ 采集野花
→ 回家睡觉
→ 第二天作物成长
→ 雨天自动浇水
→ 收获作物
→ 送礼给 NPC
→ 修复旧水井
→ 触发一条关于神社铃声的传闻
→ 保存并读档后状态正确
```
