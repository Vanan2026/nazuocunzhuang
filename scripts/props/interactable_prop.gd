extends Area2D
class_name InteractableProp

signal interaction_available(target: Node)
signal interaction_unavailable

@export var prop_name: String = "道具"
@export var interaction_hint: String = "按 E 交互"

var is_nearby: bool = false
var current_interactor: Node = null

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node) -> void:
    if body.is_in_group("player"):
        is_nearby = true
        current_interactor = body
        emit_signal("interaction_available", self)
        show_interaction_hint(true)

func _on_body_exited(body: Node) -> void:
    if body.is_in_group("player"):
        is_nearby = false
        current_interactor = null
        emit_signal("interaction_unavailable")
        show_interaction_hint(false)

func on_interact(interactor: Node) -> void:
    pass

func show_interaction_hint(show: bool) -> void:
    var hint_label = get_node_or_null("InteractionHint")
    if hint_label:
        hint_label.visible = show

func get_interaction_hint() -> String:
    return interaction_hint

func play_interaction_effect() -> void:
    var tween = create_tween()
    tween.tween_property(self, "scale", Vector2(1.1, 1.1), 0.1)
    tween.tween_property(self, "scale", Vector2(1.0, 1.0), 0.1)