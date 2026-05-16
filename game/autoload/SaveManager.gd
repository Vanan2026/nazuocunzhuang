class_name SaveManager
extends Node

signal save_requested(path: String)
signal load_requested(path: String)
signal save_data_applied()

const SAVE_VERSION: String = "0.1.0"
const DEFAULT_SAVE_PATH: String = "user://save_slot_01.json"

var last_save_data: Dictionary = {}


func build_save_data() -> Dictionary:
	return {
		"version": SAVE_VERSION,
		"time": {},
		"weather": {},
		"player": {},
		"inventory": {},
		"relationships": {},
		"flags": {},
		"farm_plots": {},
		"restoration_states": {},
	}


func apply_save_data(data: Dictionary) -> void:
	last_save_data = data.duplicate(true)
	save_data_applied.emit()


func get_restoration_states(data: Dictionary = {}) -> Dictionary:
	if data.is_empty():
		return {}
	var raw_states: Variant = data.get("restoration_states", {})
	if raw_states is Dictionary:
		var restoration_states: Dictionary = raw_states
		return restoration_states.duplicate(true)
	return {}


func build_runtime_payload(game_state: Node = null) -> Dictionary:
	var payload: Dictionary = {"restoration_states": {}}
	if game_state != null and game_state.has_method("get_restoration_states"):
		payload["restoration_states"] = game_state.get_restoration_states()
	return payload


func apply_runtime_payload(game_state: Node, payload: Dictionary) -> void:
	if game_state == null or not game_state.has_method("set_restoration_states"):
		return
	var raw_states: Variant = payload.get("restoration_states", {})
	if raw_states is Dictionary:
		var states: Dictionary = raw_states
		game_state.set_restoration_states(states)


func set_restoration_states(game_state: Node, data: Dictionary) -> void:
	if game_state == null or not (game_state is Node):
		return
	if data.is_empty():
		return
	var raw_states: Variant = data.get("restoration_states", {})
	if raw_states is Dictionary and game_state.has_method("set_restoration_states"):
		var restored_payload: Dictionary = raw_states
		game_state.set_restoration_states(restored_payload)


func request_save(path: String = DEFAULT_SAVE_PATH) -> void:
	save_requested.emit(path)


func request_load(path: String = DEFAULT_SAVE_PATH) -> void:
	load_requested.emit(path)
