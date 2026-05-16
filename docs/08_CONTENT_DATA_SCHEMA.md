# 08 — 内容数据结构与示例

版本：v1.0  
用途：给 Codex 生成 JSON、CSV、Godot 数据加载器和内容表使用。

---

## 1. 设计原则

- 内容数据与逻辑分离。
- 所有 ID 使用英文 snake_case。
- 中文名称只用于显示。
- 数据表必须可扩展。
- 不在脚本中硬编码作物、物品、NPC、对话。

---

## 2. 通用 ID 规则

```text
item_id: crop_turnip
crop_id: turnip_spring
npc_id: aoi
dialogue_id: aoi_daily_spring_01
recipe_id: riceball_persimmon
quest_id: repair_old_well
restoration_id: old_well
event_id: shrine_rain_night_01
```

---

## 3. items.json

### 3.1 Schema

```json
{
  "item_id": "string",
  "name": "string",
  "category": "seed|crop|forage|fish|food|material|tool|key|furniture",
  "description": "string",
  "stackable": true,
  "max_stack": 99,
  "sell_price": 0,
  "tags": ["string"],
  "icon": "res://assets/art/items/item_id.png"
}
```

### 3.2 示例

```json
[
  {
    "item_id": "seed_turnip",
    "name": "春萝卜种子",
    "category": "seed",
    "description": "适合春天种下的小种子。",
    "stackable": true,
    "max_stack": 99,
    "sell_price": 10,
    "tags": ["seed", "spring"],
    "icon": "res://assets/art/items/seed_turnip_64.png"
  },
  {
    "item_id": "crop_turnip",
    "name": "春萝卜",
    "category": "crop",
    "description": "带着泥土香气的白萝卜。",
    "stackable": true,
    "max_stack": 99,
    "sell_price": 60,
    "tags": ["vegetable", "spring", "simple_food"],
    "icon": "res://assets/art/items/crop_turnip_64.png"
  }
]
```

---

## 4. crops.json

```json
[
  {
    "crop_id": "turnip_spring",
    "seed_item_id": "seed_turnip",
    "harvest_item_id": "crop_turnip",
    "name": "春萝卜",
    "allowed_seasons": ["spring"],
    "grow_days": 4,
    "regrow_days": 0,
    "water_required": true,
    "stages": 4,
    "stage_sprites": [
      "res://assets/art/crops/crop_turnip_stage_00_64.png",
      "res://assets/art/crops/crop_turnip_stage_01_64.png",
      "res://assets/art/crops/crop_turnip_stage_02_64.png",
      "res://assets/art/crops/crop_turnip_stage_03_64.png"
    ]
  }
]
```

---

## 5. npcs.json

```json
[
  {
    "npc_id": "aoi",
    "name": "葵",
    "role": "杂货店店主",
    "birthday": {"season": "spring", "day": 12},
    "home_scene": "res://game/scenes/world/NpcHomeAoi.tscn",
    "default_scene": "res://game/scenes/world/VillageShop.tscn",
    "portrait": "res://assets/art/portraits/npc_aoi_portrait_neutral_512.png",
    "likes": ["tea", "flower", "sweet", "vegetable"],
    "dislikes": ["raw_fish", "trash"],
    "schedule_id": "shopkeeper_basic",
    "heart_events": ["aoi_heart_2", "aoi_heart_4"]
  }
]
```

---

## 6. schedules.json

```json
[
  {
    "schedule_id": "shopkeeper_basic",
    "entries": [
      {"season": "any", "weather": "any", "day_type": "weekday", "time": "07:30", "scene": "VillagePath", "marker": "aoi_walk_shop"},
      {"season": "any", "weather": "any", "day_type": "weekday", "time": "08:00", "scene": "VillageShop", "marker": "counter"},
      {"season": "any", "weather": "any", "day_type": "weekday", "time": "18:00", "scene": "VillagePath", "marker": "aoi_walk_home"}
    ]
  }
]
```

---

## 7. dialogues.json

```json
[
  {
    "dialogue_id": "aoi_daily_spring_01",
    "npc_id": "aoi",
    "type": "daily",
    "priority": 10,
    "conditions": {"season": "spring", "weather": "any", "min_hearts": 0},
    "lines": [
      {"speaker": "aoi", "text": "春天的种子卖得最快。你要是第一次种，萝卜最稳。"}
    ],
    "sets_flags": []
  },
  {
    "dialogue_id": "hana_rumor_bell_01",
    "npc_id": "hana",
    "type": "rumor",
    "priority": 50,
    "conditions": {"weather": "rainy", "time_block": "evening", "flag_not_set": "heard_bell_rumor_01"},
    "lines": [
      {"speaker": "hana", "text": "雨天别急着关窗。有时候，远处的铃声会顺着水声过来。"}
    ],
    "sets_flags": ["heard_bell_rumor_01"]
  }
]
```

---

## 8. recipes.json

```json
[
  {
    "recipe_id": "riceball_persimmon",
    "name": "柿子饭团",
    "ingredients": [
      {"item_id": "rice", "count": 1},
      {"item_id": "persimmon", "count": 1}
    ],
    "result": {"item_id": "food_persimmon_riceball", "count": 1},
    "energy_restore": 25,
    "tags": ["sweet", "autumn", "homey"],
    "unlock_condition": {"kitchen_level": 1}
  }
]
```

---

## 9. restoration_targets.json

```json
[
  {
    "restoration_id": "old_well",
    "name": "旧水井",
    "description": "院子里的老水井，井绳已经断了。",
    "required_items": [
      {"item_id": "wood", "count": 20},
      {"item_id": "stone", "count": 10}
    ],
    "required_money": 500,
    "required_flags": [],
    "unlocks": ["yard_water_source", "rumor_old_well_bell"],
    "visual_states": {
      "broken": "res://assets/art/props/prop_well_old_broken_256.png",
      "repaired": "res://assets/art/props/prop_well_old_repaired_256.png"
    }
  }
]
```

---

## 10. events.json

```json
[
  {
    "event_id": "shrine_rain_night_01",
    "type": "narrative",
    "conditions": {
      "season": "autumn",
      "weather": "rainy",
      "time_block": "night",
      "scene": "OldShrine",
      "has_item": {"item_id": "old_bell_fragment", "count": 1},
      "flags_not_set": ["seen_shrine_rain_night_01"]
    },
    "actions": [
      {"action": "show_dialogue", "dialogue_id": "shrine_rain_night_01_dialogue"},
      {"action": "set_flag", "flag": "seen_shrine_rain_night_01"},
      {"action": "add_codex_entry", "entry_id": "old_bell_rain"}
    ]
  }
]
```

---

## 11. quests.json

任务不应像传统 RPG 打怪任务，应更生活化。

```json
[
  {
    "quest_id": "repair_old_well",
    "title": "让水井重新有水声",
    "description": "院子里的旧水井还能用，只是需要木材和石头修好井架。",
    "type": "restoration",
    "steps": [
      {"type": "collect", "item_id": "wood", "count": 20},
      {"type": "collect", "item_id": "stone", "count": 10},
      {"type": "interact", "target_id": "old_well"}
    ],
    "rewards": [
      {"type": "unlock", "id": "yard_water_source"},
      {"type": "relationship", "npc_id": "gen", "value": 20}
    ]
  }
]
```

---

## 12. 数据验证规则

Codex 生成数据后必须检查：

- 所有 ID 唯一。
- 所有引用 ID 存在。
- 中文显示名不为空。
- 资产路径符合命名规范。
- 不出现 combat、weapon、monster、damage、hp 等字段。
- 作物季节合法。
- NPC birthday 合法。
- 配方材料存在。
- 修复奖励不引用不存在的 unlock。
