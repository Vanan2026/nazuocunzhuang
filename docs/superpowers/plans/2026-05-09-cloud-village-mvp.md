# 云村 MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建「云村」治愈系游戏 MVP，实现核心框架 + 视觉呈现 + 基础内容

**Architecture:** 
- Godot 4.4 引擎，2D 渲染 + GDScript
- 手绘 2D 美术资源 + Godot Shader 实现新海诚式动态光影
- 模块化游戏系统（时间/事件/场景/玩家）

**Tech Stack:**
- Godot 4.4+ (engine)
- GDScript (scripting)
- Godot Shader (visual effects)
- Claude Code Game Studios (workflow)
- Godot MCP (scene operations)

---

## 文件结构

```
d:\那个村庄\
├── project.godot              # Godot 项目配置（已存在）
├── scenes/                    # 场景
│   ├── main.tscn              # 主场景（已存在）
│   ├── world/
│   │   ├── cloud_village.tscn # 云村主场景
│   │   ├── cloud_house.tscn   # 云屋场景
│   │   └── transition.tscn    # 场景过渡
│   ├── ui/
│   │   └── main_ui.tscn       # 主 UI
│   └── characters/
│       └── player.tscn        # 玩家角色
├── scripts/                   # GDScript 脚本
│   ├── main.gd                # 主入口（已存在）
│   ├── game_manager.gd        # 游戏管理器
│   ├── time_system.gd         # 时间/季节系统
│   ├── event_system.gd        # 事件触发系统
│   ├── scene_manager.gd       # 场景切换
│   ├── player_controller.gd   # 玩家控制
│   ├── npc_manager.gd         # NPC 管理
│   ├── ui_manager.gd          # UI 管理
│   └── activities/
│       ├── farm_system.gd     # 后院田地系统
│       ├── cooking_system.gd  # 烹饪系统
│       ├── meditation_system.gd  # 冥想系统
│       └── pet_system.gd      # 宠物系统
├── sprites/                   # 美术资源
│   ├── characters/            # 角色
│   ├── environments/          # 环境背景
│   │   └── cloud_village/     # 云村环境
│   └── effects/              # 光效/粒子
├── shaders/                   # Shader 文件
│   ├── sky_gradient.gdshader    # 动态天空
│   ├── cloud_flow.gdshader       # 云影流动
│   ├── light_flcker.gdshader    # 光影斑驳
│   └── season_tint.gdshader      # 季节色调
├── design/                    # 设计文档（已存在）
│   └── 2026-05-09-game-design.md
└── .claude/                   # Claude Code Game Studios
```

---

## 实施阶段

### Phase 1: 核心框架（1-2周）

#### Task 1: 项目初始化与基础架构

**Files:**
- Create: `scripts/game_manager.gd`
- Create: `scripts/time_system.gd`
- Create: `scripts/event_system.gd`
- Create: `scripts/scene_manager.gd`
- Modify: `project.godot` (确认配置)
- Modify: `scripts/main.gd` (初始化游戏)

- [ ] **Step 1: 创建游戏管理器 GameManager**

```gdscript
# scripts/game_manager.gd
extends Node

signal game_initialized
signal day_changed(day: int)
signal season_changed(season: String)

var current_day: int = 1
var current_season: String = "spring"  # spring/summer/autumn/winter
var time_of_day: float = 0.0  # 0.0 - 1.0

func _ready() -> void:
    initialize_systems()

func initialize_systems() -> void:
    TimeSystem.init()
    EventSystem.init()
    SceneManager.init()
    emit_signal("game_initialized")
```

- [ ] **Step 2: 创建时间系统 TimeSystem**

```gdscript
# scripts/time_system.gd
extends Node

const SEASONS = ["spring", "summer", "autumn", "winter"]
const DAYS_PER_SEASON = 30

var current_day: int = 1
var current_season: String = "spring"
var time_progress: float = 0.0

func _process(delta: float) -> void:
    time_progress += delta / 60.0  # 1分钟 = 1天
    if time_progress >= 1.0:
        advance_day()

func advance_day() -> void:
    time_progress = 0.0
    current_day += 1
    if current_day > DAYS_PER_SEASON:
        advance_season()

func advance_season() -> void:
    var season_index = SEASONS.find(current_season)
    season_index = (season_index + 1) % SEASONS.size()
    current_season = SEASONS[season_index]
    GameManager.emit_signal("season_changed", current_season)
```

- [ ] **Step 3: 创建事件系统 EventSystem**

```gdscript
# scripts/event_system.gd
extends Node

var event_queue: Array = []
var active_events: Dictionary = {}

func init() -> void:
    register_events()

func register_events() -> void:
    # 季节事件
    add_event("spring_cherry_blossom", {
        "trigger": "season",
        "condition": func(): return TimeSystem.current_season == "spring",
        "weight": 5,
        "message": "樱花瓣随风飘落..."
    })
    # 更多事件...

func add_event(name: String, config: Dictionary) -> void:
    event_queue.append({"name": name, "config": config})

func check_events() -> void:
    for event in event_queue:
        if event["config"]["condition"].call():
            trigger_event(event)
```

- [ ] **Step 4: 创建场景管理器 SceneManager**

```gdscript
# scripts/scene_manager.gd
extends Node

var current_scene: Node = null
var transition_scene: PackedScene = preload("res://scenes/world/transition.tscn")

func init() -> void:
    load_main_scene()

func load_main_scene() -> void:
    var scene = preload("res://scenes/world/cloud_village.tscn")
    current_scene = scene.instantiate()
    get_tree().root.add_child(current_scene)

func transition_to(scene_path: String) -> void:
    # 场景过渡动画
    var t = transition_scene.instantiate()
    get_tree().root.add_child(t)
    t.play_transition()
    await t.transition_complete
    current_scene.queue_free()
    current_scene = load(scene_path).instantiate()
    get_tree().root.add_child(current_scene)
```

- [ ] **Step 5: 修改 project.godot 添加新脚本**

Run: 打开 `project.godot` 确认 `config_version=2` 和基础配置正确

- [ ] **Step 6: 提交代码**

```bash
git add scripts/game_manager.gd scripts/time_system.gd scripts/event_system.gd scripts/scene_manager.gd
git commit -m "feat: add core game systems (manager, time, events, scene)"
```

---

#### Task 2: 玩家控制系统

**Files:**
- Create: `scripts/player_controller.gd`
- Create: `scenes/characters/player.tscn` (Node2D + Sprite)
- Modify: `scenes/world/cloud_village.tscn` (添加 Player 节点)

- [ ] **Step 1: 创建玩家控制器**

```gdscript
# scripts/player_controller.gd
extends CharacterBody2D

const SPEED = 200.0
var current_direction: Vector2 = Vector2.ZERO
var is_interacting: bool = false

func _ready() -> void:
    pass

func _physics_process(delta: float) -> void:
    if is_interacting:
        return
    var direction = Vector2(
        Input.get_axis("ui_left", "ui_right"),
        Input.get_axis("ui_up", "ui_down")
    )
    if direction != Vector2.ZERO:
        current_direction = direction
        velocity = direction * SPEED
        move_and_slide()
    else:
        velocity = Vector2.ZERO

func interact() -> void:
    # 检测可交互对象
    var targets = get_tree().get_nodes_in_group("interactable")
    for target in targets:
        if position.distance_to(target.position) < 64:
            target.trigger(self)
```

- [ ] **Step 2: 创建 Player 场景**

在 Godot 中创建 `scenes/characters/player.tscn`：
- Node2D 作为根节点
- CollisionShape2D
- Sprite2D (暂时用占位符)

- [ ] **Step 3: 提交代码**

```bash
git add scripts/player_controller.gd scenes/characters/player.tscn
git commit -m "feat: add player controller with movement and interaction"
```

---

### Phase 2: 视觉呈现（2-3周）

#### Task 3: 动态天空 Shader

**Files:**
- Create: `shaders/sky_gradient.gdshader`
- Create: `shaders/cloud_flow.gdshader`
- Create: `shaders/season_tint.gdshader`
- Modify: `scenes/world/cloud_village.tscn` (应用 Shader)

- [ ] **Step 1: 创建天空渐变 Shader**

```glsl
// shaders/sky_gradient.gdshader
shader_type canvas_item;

uniform vec4 sky_color_top : source_color = vec4(0.5, 0.7, 0.9, 1.0);
uniform vec4 sky_color_bottom : source_color = vec4(0.9, 0.85, 0.8, 1.0);
uniform float time_offset : hint_range(0.0, 1.0) = 0.0;

void fragment() {
    float gradient = UV.y + sin(TIME * 0.1 + time_offset) * 0.02;
    vec4 sky = mix(sky_color_bottom, sky_color_top, gradient);
    COLOR = sky;
}
```

- [ ] **Step 2: 创建云影流动 Shader**

```glsl
// shaders/cloud_flow.gdshader
shader_type canvas_item;

uniform float cloud_speed : hint_range(0.0, 1.0) = 0.3;
uniform float cloud_density : hint_range(0.0, 1.0) = 0.5;
uniform vec4 cloud_color : source_color = vec4(1.0, 1.0, 1.0, 0.6);

float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

void fragment() {
    vec2 uv = UV;
    uv.x += TIME * cloud_speed * 0.1;
    float noise = random(floor(uv * 10.0));
    float alpha = step(1.0 - cloud_density, noise) * cloud_color.a;
    COLOR = cloud_color;
    COLOR.a *= alpha;
}
```

- [ ] **Step 3: 创建季节色调 Shader**

```glsl
// shaders/season_tint.gdshader
shader_type canvas_item;

uniform vec4 spring_tint : source_color = vec4(1.0, 0.95, 0.9, 1.0);
uniform vec4 summer_tint : source_color = vec4(1.0, 1.0, 0.9, 1.0);
uniform vec4 autumn_tint : source_color = vec4(1.0, 0.85, 0.7, 1.0);
uniform vec4 winter_tint : source_color = vec4(0.9, 0.9, 1.0, 1.0);
uniform float season_progress : hint_range(0.0, 1.0) = 0.0;

void fragment() {
    vec4 tint = spring_tint;
    // 根据季节切换 tint
    COLOR = texture(TEXTURE, UV);
    COLOR.rgb *= tint.rgb;
}
```

- [ ] **Step 4: 提交代码**

```bash
git add shaders/sky_gradient.gdshader shaders/cloud_flow.gdshader shaders/season_tint.gdshader
git commit -m "feat: add dynamic sky and season shaders"
```

---

#### Task 4: 云村主场景搭建

**Files:**
- Create: `scenes/world/cloud_village.tscn`
- Create: `sprites/environments/cloud_village/` (占位符)
- Modify: `scripts/scene_manager.gd` (加载此场景)

- [ ] **Step 1: 创建云村主场景**

在 Godot 中创建场景结构：
```
cloud_village (Node2D)
├── Background (CanvasLayer)
│   ├── Sky (ColorRect + sky_gradient shader)
│   ├── Clouds (ParallaxLayer + cloud_flow shader)
│   └── Mountains (Sprite2D)
├── Ground (TileMap or Sprite2D)
├── Objects (Node2D)
│   ├── Houses (Sprite2D group)
│   ├── Trees (Sprite2D group)
│   └── Props (Sprite2D group)
├── Characters (Node2D)
│   └── Player (instance player.tscn)
├── Effects (CanvasLayer)
│   ├── LightParticles (CPUParticles2D)
│   └── Weather (CPUParticles2D for rain/snow)
└── UI (CanvasLayer)
    └── MainUI (instance main_ui.tscn)
```

- [ ] **Step 2: 创建基础占位符精灵**

使用 Godot MCP 创建简单的占位符精灵用于测试

- [ ] **Step 3: 提交代码**

```bash
git add scenes/world/cloud_village.tscn
git commit -m "feat: create cloud village main scene"
```

---

### Phase 3: 内容填充（2-3周）

#### Task 5: 后院田地系统

**Files:**
- Create: `scripts/activities/farm_system.gd`
- Create: `scenes/activities/farm_plot.tscn`
- Modify: `scenes/world/cloud_house.tscn` (添加农场)

- [ ] **Step 1: 创建农场系统**

```gdscript
# scripts/activities/farm_system.gd
extends Node2D

signal crop_harvested(crop_type: String, amount: int)

const PLOT_COUNT = 9
const SEASON_CROPS = {
    "spring": ["萝卜", "白菜", "草莓"],
    "summer": ["番茄", "黄瓜", "西瓜"],
    "autumn": ["南瓜", "玉米", "苹果"],
    "winter": ["白菜", "萝卜"]
}

var plots: Array = []
var inventory: Dictionary = {}

func _ready() -> void:
    init_plots()

func init_plots() -> void:
    for i in PLOT_COUNT:
        plots.append({
            "state": "empty",  # empty/planted/growing/ready
            "crop": null,
            "growth": 0.0,
            "water": 0.0
        })

func plant(plot_index: int, crop_type: String) -> bool:
    if plots[plot_index]["state"] != "empty":
        return false
    var current_season = TimeSystem.current_season
    if crop_type not in SEASON_CROPS[current_season]:
        return false
    plots[plot_index] = {
        "state": "planted",
        "crop": crop_type,
        "growth": 0.0,
        "water": 50.0
    }
    return true

func water(plot_index: int) -> void:
    if plots[plot_index]["state"] == "empty":
        return
    plots[plot_index]["water"] = min(100.0, plots[plot_index]["water"] + 20.0)

func _process(delta: float) -> void:
    for plot in plots:
        if plot["state"] == "empty":
            continue
        if plot["water"] > 0:
            plot["growth"] += delta * 0.1 * (plot["water"] / 100.0)
        if plot["growth"] >= 1.0:
            plot["state"] = "ready"

func harvest(plot_index: int) -> bool:
    if plots[plot_index]["state"] != "ready":
        return false
    var crop = plots[plot_index]["crop"]
    inventory[crop] = inventory.get(crop, 0) + 1
    plots[plot_index] = {"state": "empty", "crop": null, "growth": 0.0, "water": 0.0}
    emit_signal("crop_harvested", crop, 1)
    return true
```

- [ ] **Step 2: 创建农场 UI 和交互**

创建可点击的田地格子 UI，以及种植/浇水/收获的交互逻辑

- [ ] **Step 3: 提交代码**

```bash
git add scripts/activities/farm_system.gd scenes/activities/farm_plot.tscn
git commit -m "feat: add farm system with planting and harvesting"
```

---

#### Task 6: 居民/NPC 系统

**Files:**
- Create: `scripts/npc_manager.gd`
- Create: `scripts/npc_behavior.gd`
- Create: `scenes/characters/npc.tscn`

- [ ] **Step 1: 创建 NPC 管理器**

```gdscript
# scripts/npc_manager.gd
extends Node

signal npc_interaction(npc_id: String, type: String)

const NPC_DATA = {
    "neighbor_aya": {
        "name": "绫",
        "description": "热心的中年妇人，常送自家种的菜",
        "schedule": {
            "morning": "market",
            "afternoon": "home",
            "evening": "square"
        }
    },
    "elder_takeshi": {
        "name": "武志",
        "description": "沉默寡言的老人，喜欢在树下下棋",
        "schedule": {
            "morning": "home",
            "afternoon": "park",
            "evening": "home"
        }
    }
    # 更多 NPC...
}

var npcs: Dictionary = {}

func _ready() -> void:
    init_npcs()

func init_npcs() -> void:
    for npc_id in NPC_DATA:
        var npc_scene = preload("res://scenes/characters/npc.tscn")
        var npc = npc_scene.instantiate()
        npc.npc_id = npc_id
        npc.display_name = NPC_DATA[npc_id]["name"]
        add_child(npc)
        npcs[npc_id] = npc

func interact(npc_id: String) -> void:
    if npc_id in npcs:
        var dialogue = generate_dialogue(npc_id)
        UIManager.show_dialogue(npc_id, dialogue)
        emit_signal("npc_interaction", npc_id, "talk")

func generate_dialogue(npc_id: String) -> Array:
    # 简单的对话生成逻辑
    return [
        {"speaker": NPC_DATA[npc_id]["name"], "text": "今天天气真好呢。"},
        {"speaker": NPC_DATA[npc_id]["name"], "text": "欢迎来到云村。"}
    ]
```

- [ ] **Step 2: 提交代码**

```bash
git add scripts/npc_manager.gd scripts/npc_behavior.gd scenes/characters/npc.tscn
git commit -m "feat: add NPC manager and basic villagers"
```

---

## 验证步骤

### 验证 1: 核心框架运行

```bash
# 启动游戏，确认无报错
# 按 WASD 移动玩家
# 确认时间系统正常运行（日/季节切换）
```

### 验证 2: 视觉呈现

```bash
# 确认动态天空 Shader 正常显示
# 确认云影流动效果
# 确认季节色调切换正常
```

### 验证 3: 内容功能

```bash
# 玩家可以与 NPC 对话
# 后院田地可以种植/浇水/收获
# 事件系统正常触发
```

---

## 里程碑交付物

| Phase | 交付物 | 验收标准 |
|-------|--------|----------|
| Phase 1 | 可运行的核心框架 | 玩家可移动，时间/季节系统运行 |
| Phase 2 | 视觉呈现完整 | 天空/云影/季节效果可见 |
| Phase 3 | 基础内容填充 | 1个可玩场景 + 3个NPC + 田地系统 |

---

**计划版本**: v1.0  
**创建日期**: 2026-05-09  
**下一步**: 等待用户确认后开始实施