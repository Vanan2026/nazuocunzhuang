class_name RumorBoard
extends "res://game/entities/interactable/Interactable.gd"

@export var rumor_source: String = "bulletin"
@export var rumor_manager_path: NodePath
@export var dialogue_box_path: NodePath
@export var speaker_name: String = "公告板"


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	show_rumors()


func show_rumors() -> Dictionary:
	var rumor_manager := _get_rumor_manager()
	var dialogue_box := _get_dialogue_box()
	if rumor_manager == null or not rumor_manager.has_method("build_rumor_dialogue"):
		return {}
	var dialogue: Dictionary = rumor_manager.build_rumor_dialogue(rumor_source)
	if dialogue_box != null and dialogue_box.has_method("show_dialogue"):
		dialogue_box.show_dialogue(dialogue, {
			"npc_name": speaker_name,
			"portrait": "",
		})
	if rumor_manager.has_method("mark_dialogue_rumors_seen"):
		rumor_manager.mark_dialogue_rumors_seen(dialogue)
	return dialogue


func _get_rumor_manager() -> Node:
	return _get_linked_node(rumor_manager_path, "RumorManager")


func _get_dialogue_box() -> Node:
	return _get_linked_node(dialogue_box_path, "DialogueBox")


func _get_linked_node(path: NodePath, fallback_name: String) -> Node:
	var linked := get_node_or_null(path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null(fallback_name)
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	if get_tree() != null and get_tree().root != null:
		return get_tree().root.get_node_or_null(fallback_name)
	return null
