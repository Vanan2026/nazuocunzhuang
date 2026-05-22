class_name FlagInteractable
extends "res://game/entities/interactable/Interactable.gd"

@export var flag_id: String = ""
@export var flag_value: bool = true
@export var game_state_path: NodePath


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	var game_state := _get_game_state()
	if game_state == null or not game_state.has_method("set_flag"):
		push_warning("FlagInteractable missing GameState for %s" % flag_id)
		return
	if flag_id.is_empty():
		push_warning("FlagInteractable has empty flag_id.")
		return
	game_state.set_flag(flag_id, flag_value)


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
	return null
