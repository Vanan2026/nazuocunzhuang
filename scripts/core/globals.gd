extends Node

## 全局系统管理器
## 此脚本应在 project.godot 中作为 AutoLoad 注册（Globals）

var time_system: Node = null
var event_system: Node = null
var ui_manager: Node = null
var npc_manager: Node = null
var interaction_hint_ui: Node = null

var debug_mode: bool = false

func _ready() -> void:
    set_meta("script_class", "Globals")
    print("[Globals] 全局系统已初始化")

## 获取时间系统
func get_time_system() -> Node:
    if time_system == null:
        push_warning("[Globals] TimeSystem 未初始化")
    return time_system

## 获取事件系统
func get_event_system() -> Node:
    if event_system == null:
        push_warning("[Globals] EventSystem 未初始化")
    return event_system

## 获取 UI 管理器
func get_ui_manager() -> Node:
    if ui_manager == null:
        push_warning("[Globals] UIManager 未初始化")
    return ui_manager

## 获取 NPC 管理器
func get_npc_manager() -> Node:
    if npc_manager == null:
        push_warning("[Globals] NPCManager 未初始化")
    return npc_manager

## 获取交互提示 UI
func get_interaction_hint_ui() -> Node:
    if interaction_hint_ui == null:
        push_warning("[Globals] InteractionHintUI 未初始化")
    return interaction_hint_ui

## 注册系统
func register_time_system(system: Node) -> void:
    time_system = system

func register_event_system(system: Node) -> void:
    event_system = system

func register_ui_manager(manager: Node) -> void:
    ui_manager = manager

func register_npc_manager(manager: Node) -> void:
    npc_manager = manager

func register_interaction_hint_ui(ui: Node) -> void:
    interaction_hint_ui = ui

## 切换调试模式
func set_debug_mode(enabled: bool) -> void:
    debug_mode = enabled

func is_debug_mode() -> bool:
    return debug_mode
