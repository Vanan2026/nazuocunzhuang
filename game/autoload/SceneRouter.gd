class_name SceneRouter
extends Node

signal scene_change_requested(scene_id: String, spawn_id: String)
signal scene_changed(scene_id: String)

var current_scene_id: String = ""
var current_spawn_id: String = ""


func request_scene_change(scene_id: String, spawn_id: String = "default") -> void:
	scene_change_requested.emit(scene_id, spawn_id)


func get_current_scene_id() -> String:
	return current_scene_id


func set_current_scene(scene_id: String, spawn_id: String = "default") -> void:
	current_scene_id = scene_id
	current_spawn_id = spawn_id
	scene_changed.emit(scene_id)


func get_current_spawn_id() -> String:
	return current_spawn_id


func get_save_data() -> Dictionary:
	return {
		"current_scene_id": current_scene_id,
		"current_spawn_id": current_spawn_id,
	}


func apply_save_data(data: Dictionary) -> void:
	if data.is_empty():
		return
	var next_scene_id := String(data.get("current_scene_id", current_scene_id))
	var next_spawn_id := String(data.get("current_spawn_id", current_spawn_id))
	if next_scene_id.is_empty():
		return
	set_current_scene(next_scene_id, next_spawn_id)
