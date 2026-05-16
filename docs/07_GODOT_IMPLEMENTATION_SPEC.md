# 07 — Godot 实现规格书

版本：v1.0  
目标引擎：Godot 4.x  
用途：给 Codex 实现项目骨架、系统、场景和数据驱动逻辑使用。

---

## 1. 总体架构

项目应采用数据驱动、系统模块化、scene 可复用的架构。

```text
Autoload Managers
  ↓
Data Registry
  ↓
Scenes / Entities / UI
  ↓
Save System
```

核心原则：

- 系统之间通过 signal 或 EventBus 通讯。
- 物品、作物、NPC、对话、修复目标通过数据表加载。
- 场景节点只负责表现和局部交互，不硬编码全局进度。
- 所有功能先做 MVP 最小可玩版，再扩展。

---

## 2. 推荐目录结构

```text
game/
  autoload/
    GameState.gd
    EventBus.gd
    TimeManager.gd
    SeasonManager.gd
    WeatherManager.gd
    DataRegistry.gd
    InventoryManager.gd
    RelationshipManager.gd
    QuestManager.gd
    DialogueManager.gd
    SaveManager.gd
    SceneRouter.gd
  systems/
    farming/
      FarmPlot.gd
      CropInstance.gd
    interaction/
      Interactable.gd
      InteractionArea.gd
    npc/
      NPC.gd
      NPCScheduleController.gd
    restoration/
      RestorationTarget.gd
    events/
      EventConditionEvaluator.gd
      NarrativeEventRunner.gd
  entities/
    player/
      Player.tscn
      Player.gd
    npc/
    animals/
  scenes/
    world/
      WorldRoot.tscn
      PlayerYard.tscn
      VillagePath.tscn
    home/
      PlayerHouseInterior.tscn
    ui/
      HUD.tscn
      InventoryUI.tscn
      DialogueBox.tscn
      CalendarUI.tscn
  data/
    crops.json
    items.json
    npcs.json
    dialogues.json
    recipes.json
    restoration_targets.json
assets/
  art/
  audio/
docs/
data/
```

---

## 3. Autoload 规格

### 3.1 EventBus.gd

集中 signal，降低系统耦合。

```gdscript
extends Node

signal day_started(date_info: Dictionary)
signal day_ended(date_info: Dictionary)
signal time_block_changed(block: String)
signal weather_changed(weather_id: String)
signal inventory_changed()
signal item_added(item_id: String, count: int)
signal relationship_changed(npc_id: String, value: int)
signal dialogue_started(npc_id: String)
signal dialogue_finished(npc_id: String)
signal restoration_completed(restoration_id: String)
signal narrative_event_triggered(event_id: String)
```

### 3.2 GameState.gd

全局进度与 flag。

字段建议：

```gdscript
var flags: Dictionary = {}
var unlocked_areas: Dictionary = {}
var restoration_states: Dictionary = {}
var discovered_items: Dictionary = {}
var player_money: int = 500
var player_energy: int = 100
```

### 3.3 DataRegistry.gd

加载 JSON/CSV 数据并提供查询。

```gdscript
func get_item(item_id: String) -> Dictionary
func get_crop(crop_id: String) -> Dictionary
func get_npc(npc_id: String) -> Dictionary
func get_recipe(recipe_id: String) -> Dictionary
func get_dialogue(dialogue_id: String) -> Dictionary
```

### 3.4 TimeManager.gd

职责：

- 管理分钟、小时、日期。
- 触发时间块变化。
- 跨日结算。
- 通知作物、NPC、天气。

### 3.5 SaveManager.gd

职责：

- 保存到 `user://save_slot_01.json`。
- 读取存档。
- 提供版本号。
- 对缺失字段使用默认值，避免未来扩展破坏旧存档。

---

## 4. 玩家控制器

### 4.1 Player.gd 职责

- 移动。
- 动画切换。
- 当前交互对象检测。
- 使用工具。
- 拾取物品。

不负责：

- 农作物成长。
- NPC 好感计算。
- 存档逻辑。
- 全局事件判定。

### 4.2 输入动作

```text
move_up
move_down
move_left
move_right
interact
use_tool
open_inventory
open_journal
open_map
cancel
```

### 4.3 交互流程

```text
Player enters InteractionArea
→ current_interactable = target
→ player presses interact
→ target.interact(player)
→ target decides behavior
→ EventBus emits relevant signal
```

---

## 5. Interactable 基类

```gdscript
class_name Interactable
extends Area2D

@export var interaction_id: String
@export var display_name: String
@export var prompt_text: String = "查看"

func can_interact(player: Node) -> bool:
    return true

func interact(player: Node) -> void:
    pass
```

派生类型：

```text
PickupItem
FarmPlot
NPCInteractable
DoorTransition
RestorationTarget
Signboard
Mailbox
FishingSpot
```

---

## 6. 农田实现

### 6.1 FarmPlot 节点

```gdscript
class_name FarmPlot
extends Node2D

@export var plot_id: String
var state: String = "empty"
var crop_id: String = ""
var growth_day: int = 0
var watered_today: bool = false
```

### 6.2 方法

```gdscript
func till() -> void
func plant(new_crop_id: String) -> bool
func water() -> void
func harvest() -> Array[Dictionary]
func on_day_started() -> void
func on_day_ended() -> void
```

### 6.3 跨日成长

```text
if crop exists and watered_today:
  growth_day += 1
if raining:
  watered_today = true before growth check
if growth_day >= crop.grow_days:
  state = ready
reset watered_today at next morning
```

---

## 7. 背包实现

### 7.1 数据结构

```gdscript
var items: Dictionary = {
  "wood": 20,
  "stone": 5,
  "seed_turnip": 10
}
```

工具和关键物品可使用单独字段：

```gdscript
var tools: Dictionary = {}
var key_items: Dictionary = {}
```

### 7.2 方法

```gdscript
func add_item(item_id: String, count: int = 1) -> void
func remove_item(item_id: String, count: int = 1) -> bool
func has_item(item_id: String, count: int = 1) -> bool
func get_count(item_id: String) -> int
```

---

## 8. NPC 实现

### 8.1 NPC.tscn 结构

```text
NPC (CharacterBody2D)
  Sprite2D / AnimatedSprite2D
  CollisionShape2D
  InteractionArea
  ScheduleController
```

### 8.2 NPC.gd 字段

```gdscript
@export var npc_id: String
var current_dialogue_context: Dictionary = {}
```

### 8.3 对话选择

对话由 DialogueManager 按优先级返回：

```text
event dialogue
> relationship milestone
> weather dialogue
> seasonal dialogue
> daily dialogue
> fallback dialogue
```

---

## 9. 修复系统实现

### 9.1 RestorationTarget.gd

```gdscript
class_name RestorationTarget
extends Interactable

@export var restoration_id: String

func interact(player: Node) -> void:
    var data = DataRegistry.get_restoration(restoration_id)
    if GameState.is_restored(restoration_id):
        show_restored_message()
        return
    if can_restore(data):
        show_restore_confirm(data)
    else:
        show_requirements(data)
```

### 9.2 完成修复

```text
扣除材料和金钱
→ 设置 restoration flag
→ 切换视觉状态
→ 解锁功能/区域/传闻
→ EventBus.restoration_completed.emit(id)
```

---

## 10. 事件系统实现

### 10.1 条件评估器

`EventConditionEvaluator.gd` 负责判断：

- 时间。
- 天气。
- 地点。
- 背包物品。
- 好感。
- 修复状态。
- flag。

### 10.2 事件执行器

`NarrativeEventRunner.gd` 负责执行：

- 显示对话。
- 添加物品。
- 设置 flag。
- 解锁地图。
- 播放简单 cutscene。
- 切换场景状态。

---

## 11. UI 实现

### 11.1 HUD

显示：

- 日期。
- 星期/季节。
- 时间块或时钟。
- 天气。
- 金钱。
- 当前工具。
- 体力条。

### 11.2 InventoryUI

功能：

- 显示物品网格。
- 显示选中物品名称和描述。
- 支持丢弃/使用/赠送的接口，但 MVP 可先只显示。

### 11.3 DialogueBox

功能：

- 显示 NPC 名称。
- 显示头像。
- 打字机效果可选。
- 支持选项。
- 支持事件结束回调。

---

## 12. 数据加载格式

建议 MVP 使用 JSON，方便 Codex 生成和 Godot 读取。

```text
game/data/items.json
game/data/crops.json
game/data/npcs.json
game/data/dialogues.json
game/data/recipes.json
game/data/restoration_targets.json
```

后期可转 Godot Resource，但早期 JSON 更适合 AI 批量维护。

---

## 13. 保存文件示例

```json
{
  "version": "0.1.0",
  "time": {"year": 1, "season": "spring", "day": 5, "hour": 6, "minute": 0},
  "weather": {"today": "rainy", "tomorrow": "cloudy"},
  "player": {"money": 820, "energy": 100, "scene": "PlayerYard", "position": [120, 220]},
  "inventory": {"wood": 24, "stone": 12, "crop_turnip": 5},
  "relationships": {"aoi": 120, "gen": 80},
  "flags": {"seen_intro": true, "repaired_old_well": true},
  "farm_plots": {"plot_001": {"state": "planted", "crop_id": "turnip_spring", "growth_day": 2, "watered_today": false}}
}
```

---

## 14. 垂直切片场景

Codex 首先应实现以下 scene：

```text
Main.tscn
WorldRoot.tscn
PlayerYard.tscn
PlayerHouseInterior.tscn
VillagePath.tscn
HUD.tscn
DialogueBox.tscn
InventoryUI.tscn
```

### 14.1 PlayerYard 必须包含

- 玩家出生点。
- 6 到 12 个 FarmPlot。
- 信箱。
- 旧水井修复目标。
- 出口到 VillagePath。
- 出口到 PlayerHouseInterior。

### 14.2 VillagePath 必须包含

- 2 个 NPC。
- 1 个可拾取采集物。
- 1 个公告板/传闻板。
- 1 个通向杂货店的占位门。

---

## 15. 测试方式

每次实现后至少提供：

```text
运行场景：res://game/scenes/world/WorldRoot.tscn
测试步骤：
1. 移动玩家
2. 与地块交互
3. 播种浇水
4. 跨日
5. 查看作物成长
6. 与 NPC 对话
7. 保存读取
预期结果：...
```

### 15.1 Godot MCP 优先验证

本项目已配置 Godot MCP / Godot AI 工具。涉及 Godot 工程状态、编辑器状态、场景树、资源、节点、场景操作或运行验证时，应按以下顺序处理：

1. 优先使用 Godot MCP / Godot AI。
2. 先按 streamable-http MCP 协议直接探测 `/mcp`，不要只依赖 Codex 包装层。
3. 成功 initialize 后，用 `tools/call` 读取 `session_manage(op="list")`、`editor_state`、`scene_get_hierarchy` 等编辑器状态。
4. 如果 streamable-http 初始化失败、拿不到 `Mcp-Session-Id`，或没有 ready 的 editor session，记录具体原因。
5. 回退到 Godot headless CLI 和项目验证脚本。

当前 Codex MCP 服务器名：

```text
godot-ai
```

当前地址：

```text
http://127.0.0.1:8000/mcp
```

注意：该端点使用 streamable-http MCP 协议，不应当作普通一次性 JSON-RPC POST 随意调用。

正确握手流程：

```text
POST /mcp
Headers:
  Accept: application/json, text/event-stream
  Content-Type: application/json
Body:
  {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"codex-probe","version":"1.0"}}}
```

然后：

1. 从响应头保存 `Mcp-Session-Id`。
2. 用同一 `Mcp-Session-Id` 发送 `notifications/initialized`。
3. 调 `tools/call`：
   - `session_manage` with `{"op":"list"}`
   - `session_activate`
   - `editor_state`
   - `scene_open`
   - `scene_get_hierarchy`
   - `logs_read`

已知坑：`codex mcp list`、`codex mcp get godot-ai` 或通用 `list_mcp_resources` 在当前 Codex 桌面会话里可能不显示这个 server，但 `/mcp` streamable-http 仍可能正常工作。不要把包装层失败等同于 Godot MCP 服务失败。

---

## 16. 性能原则

- 不要在每帧遍历全部 NPC 和全部事件。
- 时间变化时再更新 schedule。
- 天气/季节变化时再更新视觉。
- 资源点每天生成一次。
- 保存时只保存必要状态，不保存静态配置。

---

## 17. Codex 实现注意事项

- 不要一次性生成过大系统。
- 先用占位图和基本 UI 验证玩法。
- 不要因缺少美术而阻塞逻辑，可以生成 SVG/ColorRect 占位。
- 每个系统都必须可替换、可扩展。
- 新增数据时同步更新 `data/*.csv` 或 `game/data/*.json`。
