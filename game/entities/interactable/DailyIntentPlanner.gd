class_name DailyIntentPlanner
extends "res://game/entities/interactable/Interactable.gd"

@export var daily_intent_panel_path: NodePath


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	var panel := _get_daily_intent_panel()
	if panel != null and panel.has_method("show_planner"):
		panel.show_planner()


func _get_daily_intent_panel() -> Node:
	var linked := get_node_or_null(daily_intent_panel_path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var candidate := parent_node.get_node_or_null("DailyIntentPanel")
		if candidate != null:
			return candidate
		parent_node = parent_node.get_parent()
	if get_tree() != null and get_tree().root != null:
		return _find_node_named(get_tree().root, "DailyIntentPanel")
	return null


func _find_node_named(node: Node, node_name: String) -> Node:
	if node.name == node_name:
		return node
	for child in node.get_children():
		var found := _find_node_named(child, node_name)
		if found != null:
			return found
	return null
