extends Area2D

@export var object_id: String = ""
@export var display_name: String = ""
@export var interaction_hint: String = "鎸?E 璋冩煡"
@export var feedback_text: String = ""
@export var repeat_feedback_text: String = ""
@export var action_id: String = "inspect"
@export var one_shot: bool = false

var _used: bool = false


func _ready() -> void:
    add_to_group("interactable")
    if not body_entered.is_connected(_on_body_entered):
        body_entered.connect(_on_body_entered)
    if not body_exited.is_connected(_on_body_exited):
        body_exited.connect(_on_body_exited)
    _show_hint(false)


func on_interact(_interactor: Node) -> void:
    var text := feedback_text
    if one_shot and _used:
        text = repeat_feedback_text
    elif one_shot:
        _used = true

    if text.is_empty():
        text = display_name

    print("[YardInteractable:%s] %s" % [object_id, text])

    if has_node("/root/UIManager"):
        get_node("/root/UIManager").show_dialogue(display_name, text)


func get_interaction_hint() -> String:
    return interaction_hint


func was_used() -> bool:
    return _used


func _on_body_entered(body: Node) -> void:
    if body.is_in_group("player"):
        _show_hint(true)


func _on_body_exited(body: Node) -> void:
    if body.is_in_group("player"):
        _show_hint(false)


func _show_hint(show: bool) -> void:
    var hint := get_node_or_null("HintLabel")
    if hint is CanvasItem:
        hint.visible = show
