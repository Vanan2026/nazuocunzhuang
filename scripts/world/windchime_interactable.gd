extends "res://scripts/world/yard_interactable.gd"

@export var windchime_node_path: NodePath = NodePath("../Windchime")
@export var sway_angle: float = 0.22

var _is_swaying: bool = false


func on_interact(interactor: Node) -> void:
    super.on_interact(interactor)
    if _is_swaying:
        return

    var windchime_sprite := get_node_or_null(windchime_node_path)
    if windchime_sprite is not Node2D:
        return

    _is_swaying = true
    var tween := create_tween()
    tween.tween_property(windchime_sprite, "rotation", sway_angle, 0.12)
    tween.tween_property(windchime_sprite, "rotation", -sway_angle, 0.20)
    tween.tween_property(windchime_sprite, "rotation", 0.0, 0.12)
    tween.finished.connect(_on_sway_finished)


func _on_sway_finished() -> void:
    _is_swaying = false
