class_name SaveManager
extends Node

signal save_requested(path: String)
signal load_requested(path: String)
signal save_completed(path: String)
signal load_completed(path: String)
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
		"scene": {},
		"quests": {},
		"farm_plots": {},
		"restoration_states": {},
	}


func build_runtime_save_data(runtime_root: Node = null) -> Dictionary:
	var root_node := _resolve_runtime_root(runtime_root)
	var data := build_save_data()
	if root_node == null:
		return data

	var time_manager := _get_runtime_node(root_node, "TimeManager")
	if time_manager != null and time_manager.has_method("get_save_data"):
		data["time"] = time_manager.get_save_data()

	var weather_manager := _get_runtime_node(root_node, "WeatherManager")
	if weather_manager != null and weather_manager.has_method("get_save_data"):
		data["weather"] = weather_manager.get_save_data()

	var inventory_manager := _get_runtime_node(root_node, "InventoryManager")
	if inventory_manager != null and inventory_manager.has_method("get_save_data"):
		data["inventory"] = inventory_manager.get_save_data()

	var relationship_manager := _get_runtime_node(root_node, "RelationshipManager")
	if relationship_manager != null and relationship_manager.has_method("get_save_data"):
		data["relationships"] = relationship_manager.get_save_data()

	var scene_router := _get_runtime_node(root_node, "SceneRouter")
	if scene_router != null and scene_router.has_method("get_save_data"):
		data["scene"] = scene_router.get_save_data()

	var quest_manager := _get_runtime_node(root_node, "QuestManager")
	if quest_manager != null and quest_manager.has_method("get_save_data"):
		data["quests"] = quest_manager.get_save_data()

	var game_state := _get_runtime_node(root_node, "GameState")
	if game_state != null and game_state.has_method("get_save_data"):
		var game_state_data: Dictionary = game_state.get_save_data()
		data["flags"] = _dictionary_from(game_state_data.get("flags", {}))
		data["restoration_states"] = _dictionary_from(game_state_data.get("restoration_states", {}))
		data["game_state"] = game_state_data

	var player := _get_runtime_node(root_node, "Player")
	data["player"] = _build_player_save_data(player, game_state)
	data["farm_plots"] = _build_farm_plot_save_data(root_node)
	return data


func apply_save_data(data: Dictionary, runtime_root: Node = null) -> void:
	last_save_data = data.duplicate(true)
	if runtime_root != null:
		if runtime_root.has_method("apply_main_flow_save_data"):
			runtime_root.apply_main_flow_save_data(data)
		else:
			apply_runtime_save_data(runtime_root, data)
	save_data_applied.emit()


func apply_runtime_save_data(runtime_root: Node, data: Dictionary) -> void:
	if runtime_root == null:
		return

	var time_manager := _get_runtime_node(runtime_root, "TimeManager")
	if time_manager != null and time_manager.has_method("apply_save_data") and data.has("time"):
		time_manager.apply_save_data(_dictionary_from(data.get("time", {})))

	var weather_manager := _get_runtime_node(runtime_root, "WeatherManager")
	if weather_manager != null and weather_manager.has_method("apply_save_data") and data.has("weather"):
		weather_manager.apply_save_data(_dictionary_from(data.get("weather", {})))

	var inventory_manager := _get_runtime_node(runtime_root, "InventoryManager")
	if inventory_manager != null and inventory_manager.has_method("apply_save_data") and data.has("inventory"):
		inventory_manager.apply_save_data(_dictionary_from(data.get("inventory", {})))

	var relationship_manager := _get_runtime_node(runtime_root, "RelationshipManager")
	if relationship_manager != null and relationship_manager.has_method("apply_save_data") and data.has("relationships"):
		relationship_manager.apply_save_data(_dictionary_from(data.get("relationships", {})))

	var scene_router := _get_runtime_node(runtime_root, "SceneRouter")
	if scene_router != null and scene_router.has_method("apply_save_data") and data.has("scene"):
		scene_router.apply_save_data(_dictionary_from(data.get("scene", {})))

	var quest_manager := _get_runtime_node(runtime_root, "QuestManager")
	if quest_manager != null and quest_manager.has_method("apply_save_data") and data.has("quests"):
		quest_manager.apply_save_data(_dictionary_from(data.get("quests", {})))

	var game_state := _get_runtime_node(runtime_root, "GameState")
	if game_state != null and game_state.has_method("apply_save_data"):
		var game_state_data := _dictionary_from(data.get("game_state", {}))
		if data.has("flags"):
			game_state_data["flags"] = _dictionary_from(data.get("flags", {}))
		if data.has("restoration_states"):
			game_state_data["restoration_states"] = _dictionary_from(data.get("restoration_states", {}))
		var player_data := _dictionary_from(data.get("player", {}))
		if player_data.has("money"):
			game_state_data["player_money"] = int(player_data.get("money", 0))
		if player_data.has("energy"):
			game_state_data["player_energy"] = int(player_data.get("energy", 100))
		if not game_state_data.is_empty():
			game_state.apply_save_data(game_state_data)

	if data.has("player"):
		_apply_player_save_data(_get_runtime_node(runtime_root, "Player"), _dictionary_from(data.get("player", {})))

	if data.has("farm_plots"):
		_apply_farm_plot_save_data(runtime_root, _dictionary_from(data.get("farm_plots", {})))

	if runtime_root.has_method("refresh_runtime_ui"):
		runtime_root.refresh_runtime_ui()


func save_game(runtime_root: Node = null, path: String = DEFAULT_SAVE_PATH) -> bool:
	var data: Dictionary = {}
	if runtime_root != null and runtime_root.has_method("build_main_flow_save_data"):
		data = runtime_root.build_main_flow_save_data()
	else:
		data = build_runtime_save_data(runtime_root)
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		push_error("Could not open save file for writing: %s" % path)
		return false
	file.store_string(JSON.stringify(data, "\t"))
	file.close()
	last_save_data = data.duplicate(true)
	save_completed.emit(path)
	return true


func load_game(runtime_root: Node = null, path: String = DEFAULT_SAVE_PATH) -> bool:
	if not FileAccess.file_exists(path):
		return false
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("Could not open save file for reading: %s" % path)
		return false
	var text := file.get_as_text()
	file.close()
	var parsed: Variant = JSON.parse_string(text)
	if not (parsed is Dictionary):
		push_error("Save file does not contain a JSON object: %s" % path)
		return false
	var data: Dictionary = parsed
	apply_save_data(data, runtime_root)
	load_completed.emit(path)
	return true


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


func _resolve_runtime_root(runtime_root: Node = null) -> Node:
	if runtime_root != null:
		return runtime_root
	return get_parent()


func _get_runtime_node(runtime_root: Node, node_name: String) -> Node:
	if runtime_root == null:
		return null
	var direct := runtime_root.get_node_or_null(node_name)
	if direct != null:
		return direct
	if runtime_root.name == node_name:
		return runtime_root
	return null


func _build_player_save_data(player: Node, game_state: Node) -> Dictionary:
	var data: Dictionary = {
		"position": {"x": 0.0, "y": 0.0},
		"money": 0,
		"energy": 100,
	}
	if player is Node2D:
		var player_2d := player as Node2D
		data["position"] = {"x": player_2d.position.x, "y": player_2d.position.y}
	if game_state != null:
		if game_state.has_method("get_player_money"):
			data["money"] = int(game_state.get_player_money())
		if game_state.has_method("get_player_energy"):
			data["energy"] = int(game_state.get_player_energy())
	return data


func _apply_player_save_data(player: Node, data: Dictionary) -> void:
	if not (player is Node2D):
		return
	var position_data := _dictionary_from(data.get("position", {}))
	if position_data.is_empty():
		return
	var player_2d := player as Node2D
	player_2d.position = Vector2(
		float(position_data.get("x", player_2d.position.x)),
		float(position_data.get("y", player_2d.position.y))
	)


func _build_farm_plot_save_data(runtime_root: Node) -> Dictionary:
	var result: Dictionary = {}
	var farm_plots := _get_runtime_node(runtime_root, "FarmPlots")
	if farm_plots == null:
		return result
	for plot in farm_plots.get_children():
		if not plot.has_method("get_save_data"):
			continue
		var plot_index := str(plot.get("plot_index"))
		result[plot_index] = plot.get_save_data()
	return result


func _apply_farm_plot_save_data(runtime_root: Node, data: Dictionary) -> void:
	var farm_plots := _get_runtime_node(runtime_root, "FarmPlots")
	if farm_plots == null:
		return
	for plot in farm_plots.get_children():
		if not plot.has_method("apply_save_data"):
			continue
		var plot_index := str(plot.get("plot_index"))
		if data.has(plot_index):
			plot.apply_save_data(_dictionary_from(data.get(plot_index, {})))


func _dictionary_from(raw_value: Variant) -> Dictionary:
	if raw_value is Dictionary:
		var raw_dictionary: Dictionary = raw_value
		return raw_dictionary.duplicate(true)
	return {}
