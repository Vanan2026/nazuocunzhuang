# 快速参考指南 - Globals AutoLoad 系统

## ? 快速开始

### 1. 配置 project.godot

打开 `project.godot` 文件，添加：

```ini
[autoload]
Globals="*res://scripts/core/globals.gd"
```

### 2. 在脚本中使用

```gdscript
extends Node

func _ready() -> void:
    # 获取任何全局系统
    var time_sys = Globals.get_time_system()
    var event_sys = Globals.get_event_system()
    var ui_mgr = Globals.get_ui_manager()
    var npc_mgr = Globals.get_npc_manager()
```

---

## ?? API 参考

### 系统注册

```gdscript
# 由各系统在 _ready() 中自动调用
Globals.register_time_system(system: Node)
Globals.register_event_system(system: Node)
Globals.register_ui_manager(manager: Node)
Globals.register_npc_manager(manager: Node)
Globals.register_interaction_hint_ui(ui: Node)
```

### 系统获取

```gdscript
# 获取已注册的系统（若未初始化会发出警告）
var time_sys: Node = Globals.get_time_system()
var event_sys: Node = Globals.get_event_system()
var ui_mgr: Node = Globals.get_ui_manager()
var npc_mgr: Node = Globals.get_npc_manager()
var hint_ui: Node = Globals.get_interaction_hint_ui()
```

### 调试控制

```gdscript
# 启用/禁用调试模式
Globals.set_debug_mode(true)
Globals.set_debug_mode(false)

# 检查调试模式状态
if Globals.is_debug_mode():
    print("调试信息输出...")
```

---

## ?? 使用示例

### 示例 1：访问时间系统

```gdscript
extends Node

func _ready() -> void:
    var time_sys = Globals.get_time_system()
    if time_sys:
        var time_info = time_sys.get_current_time_info()
        print("Day: ", time_info["day"])
        print("Season: ", time_info["season"])
        print("Year: ", time_info["year"])
```

### 示例 2：与 NPC 交互

```gdscript
extends CharacterBody2D

func interact_with_npc(npc_id: String) -> void:
    var npc_mgr = Globals.get_npc_manager()
    if npc_mgr:
        npc_mgr.interact(npc_id)
```

### 示例 3：显示对话框

```gdscript
extends Node

func show_npc_dialogue(name: String, text: String) -> void:
    var ui_mgr = Globals.get_ui_manager()
    if ui_mgr:
        ui_mgr.show_dialogue(name, text)
```

### 示例 4：调试信息

```gdscript
extends Node

func debug_print(message: String) -> void:
    if Globals.is_debug_mode():
        print("[DEBUG] ", message)

func _process(delta: float) -> void:
    debug_print("Frame time: " + str(delta))
```

---

## ?? 系统功能一览

| 系统 | 作用 | 主要方法 |
|------|------|--------|
| **TimeSystem** | 管理游戏时间 | `advance_day()`, `get_current_time_info()` |
| **EventSystem** | 管理游戏事件 | `check_events()`, `trigger_event()` |
| **UIManager** | 管理 UI 显示 | `show_dialogue()`, `hide_dialogue()` |
| **NPCManager** | 管理 NPC | `interact()`, `init_npcs()` |
| **InteractionHintUI** | 交互提示显示 | `show_hint()`, `hide_hint()` |

---

## ?? 常见问题

### Q: 为什么 `Globals.get_time_system()` 返回 null？
**A:** 系统还未初始化。确保：
1. `project.godot` 中注册了 `Globals` AutoLoad
2. 对应的系统类已经在场景中加载或自动初始化

### Q: 如何注册自定义系统？
**A:** 在 `globals.gd` 中添加 getter 和 register 方法：
```gdscript
var my_system: Node = null

func register_my_system(system: Node) -> void:
    my_system = system

func get_my_system() -> Node:
    if my_system == null:
        push_warning("[Globals] MySystem 未初始化")
    return my_system
```

### Q: 为什么还有日志输出？
**A:** 日志由调试模式控制。如果看到意外的日志输出：
1. 检查是否启用了调试模式 (`Globals.is_debug_mode()`)
2. 这些可能是错误或警告（由 `push_warning/push_error` 输出）

### Q: 如何在编辑器中测试？
**A:** 
1. 打开 Godot 编辑器，项目应该正常加载
2. 在 Script 编辑器中调试 Globals 的方法
3. 在 Output 窗口查看任何警告或错误

---

## ?? 相关文件

- `scripts/core/globals.gd` - Globals 系统实现
- `CODE_REVIEW_FIXES.md` - 详细修复说明
- `FIXES_SUMMARY.md` - 修复总结报告

---

**最后更新**: 2024  
**版本**: 1.0

