extends Area2D

@export var target_scene: String = ""
@export var interaction_hint: String = "鎸?E 鍓嶅線鍚庨櫌鍐滃湴"


func _ready() -> void:
	add_to_group("interactable")
	add_to_group("scene_exit")
	if not body_entered.is_connected(_on_body_entered):
		body_entered.connect(_on_body_entered)
	if not body_exited.is_connected(_on_body_exited):
		body_exited.connect(_on_body_exited)
	_show_hint(false)


func on_interact(_interactor: Node) -> void:
	if target_scene.is_empty():
		push_warning("Backyard farmland scene is not wired yet.")
		return
	get_tree().call_deferred("change_scene_to_file", target_scene)


func get_interaction_hint() -> String:
	return interaction_hint


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
