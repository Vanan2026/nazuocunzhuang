class_name FlagDialogueInteractable
extends "res://game/entities/interactable/FlagInteractable.gd"

@export var dialogue_id: String = ""
@export var speaker_id: String = "system"
@export var speaker_name: String = ""
@export_multiline var dialogue_text: String = ""
@export var portrait_path: String = ""
@export var dialogue_box_path: NodePath


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	var dialogue_box := _get_dialogue_box()
	if dialogue_box == null or not dialogue_box.has_method("show_dialogue"):
		push_warning("FlagDialogueInteractable missing DialogueBox for %s" % dialogue_id)
		return
	if dialogue_id.is_empty() or dialogue_text.is_empty():
		push_warning("FlagDialogueInteractable has incomplete dialogue data.")
		return
	dialogue_box.show_dialogue(_build_dialogue(), {"npc_name": speaker_name, "portrait": portrait_path})


func _build_dialogue() -> Dictionary:
	var resolved_speaker_id := speaker_id
	if resolved_speaker_id.is_empty():
		resolved_speaker_id = "system"
	return {
		"dialogue_id": dialogue_id,
		"npc_id": resolved_speaker_id,
		"lines": [
			{
				"speaker": resolved_speaker_id,
				"text": dialogue_text,
			},
		],
	}


func _get_dialogue_box() -> Node:
	var linked := get_node_or_null(dialogue_box_path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null("DialogueBox")
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	if get_tree() != null and get_tree().root != null:
		return _find_node_named(get_tree().root, "DialogueBox")
	return null


func _find_node_named(node: Node, node_name: String) -> Node:
	if node == null:
		return null
	if node.name == node_name:
		return node
	for child in node.get_children():
		var found := _find_node_named(child, node_name)
		if found != null:
			return found
	return null
