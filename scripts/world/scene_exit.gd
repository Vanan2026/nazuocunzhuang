extends Area2D

@export var target_scene: String = ""
@export var target_spawn_id: String = ""
@export var exit_id: String = ""
@export var interaction_hint: String = "按 E 前往"


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
		push_warning("Scene exit target is not wired yet.")
		return
	var transition_state := get_node_or_null("/root/SceneTransitionState")
	if transition_state != null and transition_state.has_method("set_pending_transition"):
		var source_scene := ""
		if get_tree().current_scene != null:
			source_scene = get_tree().current_scene.scene_file_path
		var resolved_exit_id := exit_id
		if resolved_exit_id.is_empty():
			resolved_exit_id = name
		transition_state.call("set_pending_transition", target_scene, target_spawn_id, source_scene, resolved_exit_id)
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
