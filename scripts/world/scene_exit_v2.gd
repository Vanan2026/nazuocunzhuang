extends Area2D

@export var target_region_id: String = ""
@export var target_spawn_id: String = ""
@export var exit_id: String = ""
@export var interaction_hint: String = "按 E 前往"

var is_used: bool = false

func _ready() -> void:
    add_to_group("interactable")
    add_to_group("scene_exit")
    if not body_entered.is_connected(_on_body_entered):
        body_entered.connect(_on_body_entered)
    if not body_exited.is_connected(_on_body_exited):
        body_exited.connect(_on_body_exited)
    _show_hint(false)


func on_interact(interactor: Node) -> void:
    if target_region_id.is_empty():
        push_warning("Scene exit target_region_id is not set.")
        return

    if is_used:
        return
    is_used = true

    var world_controller = get_world_controller()
    if world_controller != null:
        world_controller.spawn_player_at(target_region_id, target_spawn_id)
        print("[SceneExit] 传送到区域: ", target_region_id, " / spawn: ", target_spawn_id)
    else:
        print("[SceneExit] 警告: 找不到 WorldController，使用传统场景切换")
        get_tree().call_deferred("change_scene_to_file", "res://scenes/world/world.tscn")


func get_world_controller() -> Node:
    var root = get_tree().root
    if root.has_node("World/WorldController"):
        return root.get_node("World/WorldController")
    if root.has_node("WorldController"):
        return root.get_node("WorldController")
    if root.has_node("World"):
        var world = root.get_node("World")
        if world.has_node("WorldController"):
            return world.get_node("WorldController")
    return null


func get_interaction_hint() -> String:
    return interaction_hint


func _on_body_entered(body: Node) -> void:
    if body.is_in_group("player"):
        _show_hint(true)


func _on_body_exited(body: Node) -> void:
    if body.is_in_group("player"):
        _show_hint(false)


func _show_hint(show: bool) -> void:
    var hint = get_node_or_null("HintLabel")
    if hint is CanvasItem:
        hint.visible = show


func _reset() -> void:
    is_used = false