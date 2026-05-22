class_name MainFlow
extends Node

const SCENE_REGISTRY: Dictionary = {
	"player_house": {
		"path": "res://game/scenes/home/PlayerHouse.tscn",
		"default_spawn": "inside_default",
	},
	"player_yard": {
		"path": "res://game/scenes/world/PlayerYard.tscn",
		"default_spawn": "from_house",
	},
	"forest_edge": {
		"path": "res://game/scenes/world/ForestEdge.tscn",
		"default_spawn": "from_yard",
	},
}

const INITIAL_SCENE_ID: String = "player_house"
const INITIAL_SPAWN_ID: String = "inside_default"
const FIRST_WEEK_QUEST_HUD_SCENE_NAME: String = "FirstWeekQuestHUD"

@onready var scene_router: Node = $SceneRouter
@onready var data_registry: Node = $DataRegistry
@onready var time_manager: Node = $TimeManager
@onready var weather_manager: Node = $WeatherManager
@onready var inventory_manager: Node = $InventoryManager
@onready var relationship_manager: Node = $RelationshipManager
@onready var dialogue_manager: Node = $DialogueManager
@onready var rumor_manager: Node = $RumorManager
@onready var game_state: Node = $GameState
@onready var save_manager: Node = $SaveManager
@onready var quest_manager: Node = $QuestManager
@onready var first_week_quest_hud: Node = $FirstWeekQuestHUD
@onready var current_scene_container: Node = $CurrentScene

var current_gameplay_scene: Node = null
var current_gameplay_scene_id: String = ""
var current_spawn_id: String = ""


func _ready() -> void:
	_ensure_persistent_data_loaded()
	_bind_persistent_managers()
	_connect_scene_router()
	_adopt_initial_scene()
	if current_gameplay_scene == null:
		change_scene(INITIAL_SCENE_ID, INITIAL_SPAWN_ID)
		return
	scene_router.set_current_scene(current_gameplay_scene_id, current_spawn_id)
	_apply_shared_state_to_current_scene(false)


func get_current_gameplay_scene_id() -> String:
	return current_gameplay_scene_id


func get_current_gameplay_scene() -> Node:
	return current_gameplay_scene


func change_scene(scene_id: String, spawn_id: String = "default", sync_before_change: bool = true) -> void:
	if not SCENE_REGISTRY.has(scene_id):
		push_warning("Unknown main-flow scene id: %s" % scene_id)
		return

	if sync_before_change:
		sync_current_scene_state()
	_remove_current_scene()

	var scene_info: Dictionary = SCENE_REGISTRY[scene_id]
	var scene_path := String(scene_info.get("path", ""))
	var scene_resource := load(scene_path) as PackedScene
	if scene_resource == null:
		push_error("Could not load main-flow scene: %s" % scene_path)
		return

	current_gameplay_scene = scene_resource.instantiate()
	add_child(current_gameplay_scene)
	current_gameplay_scene_id = scene_id
	current_spawn_id = _resolve_spawn_id(scene_id, spawn_id)
	scene_router.set_current_scene(current_gameplay_scene_id, current_spawn_id)
	_apply_shared_state_to_current_scene(false)


func sync_current_scene_state() -> void:
	if current_gameplay_scene == null:
		_update_first_week_quest_progress()
		return
	_copy_scene_state_to_shared("TimeManager", time_manager)
	_copy_scene_state_to_shared("WeatherManager", weather_manager)
	_copy_scene_state_to_shared("InventoryManager", inventory_manager)
	_copy_scene_state_to_shared("RelationshipManager", relationship_manager)
	_copy_scene_state_to_shared("GameState", game_state)
	_update_first_week_quest_progress()


func apply_shared_state_to_current_scene() -> void:
	sync_current_scene_state()
	_apply_shared_state_to_current_scene(false)


func _apply_shared_state_to_current_scene(sync_before_apply: bool = false) -> void:
	if sync_before_apply:
		sync_current_scene_state()
	if current_gameplay_scene == null:
		_update_first_week_quest_progress()
		return
	_ensure_scene_data_loaded(current_gameplay_scene)
	_copy_shared_state_to_scene(time_manager, "TimeManager")
	_copy_shared_state_to_scene(weather_manager, "WeatherManager")
	_copy_shared_state_to_scene(inventory_manager, "InventoryManager")
	_copy_shared_state_to_scene(relationship_manager, "RelationshipManager")
	_copy_shared_state_to_scene(game_state, "GameState")
	_bind_scene_managers(current_gameplay_scene)
	_place_player_at_spawn(current_spawn_id)
	if current_gameplay_scene.has_method("refresh_runtime_ui"):
		current_gameplay_scene.refresh_runtime_ui()
	_update_first_week_quest_progress()


func build_main_flow_save_data() -> Dictionary:
	sync_current_scene_state()
	var data: Dictionary = save_manager.build_runtime_save_data(self)
	data["scene"] = scene_router.get_save_data()
	data["quests"] = quest_manager.get_save_data()
	return data


func apply_main_flow_save_data(data: Dictionary) -> void:
	if save_manager != null and save_manager.has_method("apply_runtime_save_data"):
		save_manager.apply_runtime_save_data(self, data)
	var scene_data: Dictionary = _dictionary_from(data.get("scene", {}))
	var next_scene_id := String(scene_data.get("current_scene_id", current_gameplay_scene_id))
	var next_spawn_id := String(scene_data.get("current_spawn_id", current_spawn_id))
	if not next_scene_id.is_empty() and next_scene_id != current_gameplay_scene_id:
		change_scene(next_scene_id, next_spawn_id, false)
	else:
		current_spawn_id = _resolve_spawn_id(next_scene_id, next_spawn_id)
		scene_router.set_current_scene(current_gameplay_scene_id, current_spawn_id)
		_apply_shared_state_to_current_scene(false)


func _adopt_initial_scene() -> void:
	var existing := get_node_or_null("PlayerHouse")
	if existing == null:
		return
	current_gameplay_scene = existing
	current_gameplay_scene_id = INITIAL_SCENE_ID
	current_spawn_id = INITIAL_SPAWN_ID


func _remove_current_scene() -> void:
	if current_gameplay_scene == null:
		return
	if is_instance_valid(current_gameplay_scene):
		if current_gameplay_scene.get_parent() == self:
			remove_child(current_gameplay_scene)
		current_gameplay_scene.queue_free()
	current_gameplay_scene = null


func _connect_scene_router() -> void:
	if scene_router == null or not scene_router.has_signal("scene_change_requested"):
		return
	if not scene_router.scene_change_requested.is_connected(_on_scene_change_requested):
		scene_router.scene_change_requested.connect(_on_scene_change_requested)


func _on_scene_change_requested(scene_id: String, spawn_id: String) -> void:
	change_scene(scene_id, spawn_id)


func _ensure_persistent_data_loaded() -> void:
	if data_registry == null:
		return
	if data_registry.has_method("load_all_data") and not bool(data_registry.get("is_loaded")):
		data_registry.load_all_data()
	if data_registry.has_method("validate_all_data"):
		data_registry.validate_all_data()


func _ensure_scene_data_loaded(scene_root: Node) -> void:
	var scene_data_registry := scene_root.get_node_or_null("DataRegistry")
	if scene_data_registry == null:
		return
	if scene_data_registry.has_method("load_all_data") and not bool(scene_data_registry.get("is_loaded")):
		scene_data_registry.load_all_data()
	if scene_data_registry.has_method("validate_all_data"):
		scene_data_registry.validate_all_data()


func _bind_persistent_managers() -> void:
	if dialogue_manager != null:
		if dialogue_manager.has_method("bind_registry"):
			dialogue_manager.bind_registry(data_registry)
		if dialogue_manager.has_method("bind_relationship_manager"):
			dialogue_manager.bind_relationship_manager(relationship_manager)
	if rumor_manager != null:
		if rumor_manager.has_method("bind_registry"):
			rumor_manager.bind_registry(data_registry)
		if rumor_manager.has_method("bind_game_state"):
			rumor_manager.bind_game_state(game_state)
		if rumor_manager.has_method("bind_time_manager"):
			rumor_manager.bind_time_manager(time_manager)
		if rumor_manager.has_method("bind_weather_manager"):
			rumor_manager.bind_weather_manager(weather_manager)
	if first_week_quest_hud != null and first_week_quest_hud.has_method("bind_quest_manager"):
		first_week_quest_hud.bind_quest_manager(quest_manager)


func _bind_scene_managers(scene_root: Node) -> void:
	var scene_data_registry := scene_root.get_node_or_null("DataRegistry")
	var scene_time_manager := scene_root.get_node_or_null("TimeManager")
	var scene_weather_manager := scene_root.get_node_or_null("WeatherManager")
	var scene_inventory_manager := scene_root.get_node_or_null("InventoryManager")
	var scene_relationship_manager := scene_root.get_node_or_null("RelationshipManager")
	var scene_game_state := scene_root.get_node_or_null("GameState")
	var scene_dialogue_manager := scene_root.get_node_or_null("DialogueManager")
	var scene_rumor_manager := scene_root.get_node_or_null("RumorManager")
	var scene_schedule_director := scene_root.get_node_or_null("ScheduleDirector")

	if scene_dialogue_manager != null:
		if scene_dialogue_manager.has_method("bind_registry"):
			scene_dialogue_manager.bind_registry(scene_data_registry)
		if scene_dialogue_manager.has_method("bind_relationship_manager"):
			scene_dialogue_manager.bind_relationship_manager(scene_relationship_manager)
	if scene_rumor_manager != null:
		if scene_rumor_manager.has_method("bind_registry"):
			scene_rumor_manager.bind_registry(scene_data_registry)
		if scene_rumor_manager.has_method("bind_game_state"):
			scene_rumor_manager.bind_game_state(scene_game_state)
		if scene_rumor_manager.has_method("bind_time_manager"):
			scene_rumor_manager.bind_time_manager(scene_time_manager)
		if scene_rumor_manager.has_method("bind_weather_manager"):
			scene_rumor_manager.bind_weather_manager(scene_weather_manager)
	if scene_schedule_director != null and scene_schedule_director.has_method("apply_schedule"):
		scene_schedule_director.apply_schedule()
	# Keep exported path fallback users anchored to scene-local state mirrors.
	if scene_inventory_manager == null:
		scene_inventory_manager = inventory_manager


func _copy_scene_state_to_shared(scene_node_name: String, shared_manager: Node) -> void:
	if shared_manager == null or current_gameplay_scene == null:
		return
	var scene_manager := current_gameplay_scene.get_node_or_null(scene_node_name)
	if scene_manager == null:
		return
	if scene_manager == shared_manager:
		return
	if scene_manager.has_method("get_save_data") and shared_manager.has_method("apply_save_data"):
		shared_manager.apply_save_data(scene_manager.get_save_data())


func _copy_shared_state_to_scene(shared_manager: Node, scene_node_name: String) -> void:
	if shared_manager == null or current_gameplay_scene == null:
		return
	var scene_manager := current_gameplay_scene.get_node_or_null(scene_node_name)
	if scene_manager == null:
		return
	if scene_manager == shared_manager:
		return
	if shared_manager.has_method("get_save_data") and scene_manager.has_method("apply_save_data"):
		scene_manager.apply_save_data(shared_manager.get_save_data())


func _update_first_week_quest_progress() -> void:
	if quest_manager != null and quest_manager.has_method("update_first_week_progress"):
		quest_manager.update_first_week_progress(game_state, scene_router)
	if first_week_quest_hud != null and first_week_quest_hud.has_method("refresh"):
		first_week_quest_hud.refresh()


func _resolve_spawn_id(scene_id: String, spawn_id: String) -> String:
	if not spawn_id.is_empty() and spawn_id != "default":
		return spawn_id
	var scene_info: Dictionary = SCENE_REGISTRY.get(scene_id, {})
	return String(scene_info.get("default_spawn", "default"))


func _place_player_at_spawn(spawn_id: String) -> void:
	if current_gameplay_scene == null or spawn_id.is_empty():
		return
	var player := current_gameplay_scene.get_node_or_null("Player") as Node2D
	var spawn := _find_spawn(current_gameplay_scene, spawn_id)
	if player == null or spawn == null:
		return
	player.position = spawn.position


func _find_spawn(node: Node, spawn_id: String) -> Node2D:
	if node == null:
		return null
	if node.has_method("get_spawn_id") and String(node.call("get_spawn_id")) == spawn_id and node is Node2D:
		return node as Node2D
	for child in node.get_children():
		var found := _find_spawn(child, spawn_id)
		if found != null:
			return found
	return null


func _dictionary_from(raw_value: Variant) -> Dictionary:
	if raw_value is Dictionary:
		var raw_dictionary: Dictionary = raw_value
		return raw_dictionary.duplicate(true)
	return {}
