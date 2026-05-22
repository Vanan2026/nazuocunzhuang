class_name NpcScheduleDirector
extends Node

@export var scene_id: String = "player_yard"
@export var data_registry_path: NodePath
@export var time_manager_path: NodePath
@export var npc_root_path: NodePath

var current_assignments: Dictionary = {}


func _ready() -> void:
	_connect_time_manager()
	call_deferred("apply_schedule")


func apply_schedule(block_override: String = "") -> void:
	var registry := _get_data_registry()
	var npc_root := _get_npc_root()
	if registry == null or npc_root == null:
		return
	var block := block_override
	if block.is_empty():
		block = _get_current_block()
	current_assignments.clear()
	for npc_node in npc_root.get_children():
		var npc_id := _get_npc_id(npc_node)
		if npc_id.is_empty():
			continue
		var npc_data: Dictionary = registry.get_npc(npc_id) if registry.has_method("get_npc") else {}
		var schedule_id := String(npc_data.get("schedule_id", ""))
		if schedule_id.is_empty() or not registry.has_method("get_npc_schedule"):
			continue
		var schedule: Dictionary = registry.get_npc_schedule(schedule_id)
		var assignment := _find_assignment(schedule, block)
		if assignment.is_empty():
			continue
		current_assignments[npc_id] = assignment.duplicate(true)
		_apply_assignment(npc_node, assignment)


func get_current_assignment(npc_id: String) -> Dictionary:
	return current_assignments.get(npc_id, {}).duplicate(true)


func _find_assignment(schedule: Dictionary, block: String) -> Dictionary:
	var fallback: Dictionary = {}
	for entry in schedule.get("entries", []):
		if not (entry is Dictionary):
			continue
		var entry_scene := String(entry.get("scene_id", ""))
		if entry_scene == scene_id and fallback.is_empty():
			fallback = entry
		if String(entry.get("time_block", "")) == block and entry_scene == scene_id:
			return entry
	return fallback


func _apply_assignment(npc_node: Node, assignment: Dictionary) -> void:
	var entry_scene := String(assignment.get("scene_id", ""))
	npc_node.visible = entry_scene == scene_id
	if not npc_node.visible:
		return
	var position_data: Variant = assignment.get("position", [])
	if npc_node is Node2D and position_data is Array and position_data.size() == 2:
		(npc_node as Node2D).position = Vector2(float(position_data[0]), float(position_data[1]))


func _get_current_block() -> String:
	var time_manager := _get_time_manager()
	if time_manager != null and time_manager.has_method("get_date_info"):
		return String(time_manager.get_date_info().get("block", "morning"))
	return "morning"


func _connect_time_manager() -> void:
	var time_manager := _get_time_manager()
	if time_manager == null:
		return
	if time_manager.has_signal("time_block_changed") and not time_manager.time_block_changed.is_connected(_on_time_block_changed):
		time_manager.time_block_changed.connect(_on_time_block_changed)
	if time_manager.has_signal("day_started") and not time_manager.day_started.is_connected(_on_day_started):
		time_manager.day_started.connect(_on_day_started)


func _on_time_block_changed(block: String) -> void:
	apply_schedule(block)


func _on_day_started(_date_info: Dictionary) -> void:
	apply_schedule()


func _get_npc_id(npc_node: Node) -> String:
	if npc_node.has_method("get"):
		return String(npc_node.get("npc_id"))
	return ""


func _get_data_registry() -> Node:
	return _get_linked_node(data_registry_path, "DataRegistry")


func _get_time_manager() -> Node:
	return _get_linked_node(time_manager_path, "TimeManager")


func _get_npc_root() -> Node:
	var linked := get_node_or_null(npc_root_path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null("NPCs")
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	return null


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
