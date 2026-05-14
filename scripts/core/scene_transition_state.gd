extends Node

var pending_target_scene: String = ""
var pending_spawn_id: String = ""
var pending_source_scene: String = ""
var pending_exit_id: String = ""


func set_pending_transition(target_scene: String, spawn_id: String, source_scene: String = "", exit_id: String = "") -> void:
	pending_target_scene = target_scene
	pending_spawn_id = spawn_id
	pending_source_scene = source_scene
	pending_exit_id = exit_id


func consume_spawn_id_for_scene(current_scene: String = "") -> String:
	if pending_spawn_id.is_empty():
		return ""
	if not current_scene.is_empty() and not pending_target_scene.is_empty() and current_scene != pending_target_scene:
		return ""

	var spawn_id := pending_spawn_id
	clear_pending_transition()
	return spawn_id


func clear_pending_transition() -> void:
	pending_target_scene = ""
	pending_spawn_id = ""
	pending_source_scene = ""
	pending_exit_id = ""
