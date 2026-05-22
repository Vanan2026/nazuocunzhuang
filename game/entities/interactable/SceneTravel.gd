class_name SceneTravel
extends "res://game/entities/interactable/Interactable.gd"

@export var target_scene: String = ""
@export var arrival_flag_id: String = ""
@export var game_state_path: NodePath


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	if not arrival_flag_id.is_empty():
		var game_state := _get_game_state()
		if game_state != null and game_state.has_method("set_flag"):
			game_state.set_flag(arrival_flag_id, true)
	if target_scene.is_empty():
		push_warning("SceneTravel target_scene is empty.")
		return
	get_tree().call_deferred("change_scene_to_file", target_scene)


func _get_game_state() -> Node:
	var linked := get_node_or_null(game_state_path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null("GameState")
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	if get_tree() != null and get_tree().root != null:
		return get_tree().root.get_node_or_null("GameState")
	return null
