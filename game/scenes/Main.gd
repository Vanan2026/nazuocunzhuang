class_name MainFlow
extends Node
const DailyIntentContext := preload("res://game/systems/daily/DailyIntentContext.gd")

const SCENE_REGISTRY: Dictionary = {
	"player_house": {
		"path": "res://game/scenes/home/PlayerHouse.tscn",
		"default_spawn": "inside_default",
	},
	"player_yard": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "from_house",
		"outdoor": true,
	},
	"forest_edge": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "from_yard",
		"outdoor": true,
	},
	"village": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "village_default",
		"outdoor": true,
	},
	"back_farm": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "back_farm_default",
		"outdoor": true,
	},
	"orchard": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "orchard_default",
		"outdoor": true,
	},
	"pond": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "pond_default",
		"outdoor": true,
	},
	"mountain_path": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "mountain_path_default",
		"outdoor": true,
	},
	"mountain_hut": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "mountain_hut_default",
		"outdoor": true,
	},
	"mountain": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "mountain_default",
		"outdoor": true,
	},
	"cliff_view": {
		"path": "res://game/scenes/world/OutdoorWorld.tscn",
		"default_spawn": "cliff_view_default",
		"outdoor": true,
	},
}

const INITIAL_SCENE_ID: String = "player_house"
const INITIAL_SPAWN_ID: String = "inside_default"
const FIRST_WEEK_QUEST_HUD_SCENE_NAME: String = "FirstWeekQuestHUD"
const CURRENT_OBJECTIVE_CHIP_SCENE_NAME: String = "CurrentObjectiveChip"
const DAILY_INTENT_SLEEP_REFLECTIONS: Dictionary = {
	"tend_crops": "睡前想起今天照看过菜地，土和水都会慢慢回礼。",
	"check_village_notice": "睡前想起今天去过村口，公告和路边的小消息会留到明天继续想。",
	"visit_neighbor": "睡前想起今天停下来和人说了话，村里的名字又近了一点。",
	"gather_repair_material": "睡前想起今天整理过修复材料，旧东西以后会更容易慢慢补好。",
}

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
@onready var current_objective_chip: Node = $CurrentObjectiveChip
@onready var current_scene_container: Node = $CurrentScene

var current_gameplay_scene: Node = null
var current_gameplay_scene_id: String = ""
var current_spawn_id: String = ""
var farm_plot_states: Dictionary = {}


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

	var next_spawn_id := _resolve_spawn_id(scene_id, spawn_id)
	if _can_reuse_current_outdoor_scene(scene_id):
		if sync_before_change:
			sync_current_scene_state()
		current_gameplay_scene_id = scene_id
		current_spawn_id = next_spawn_id
		if current_gameplay_scene.has_method("set_active_region"):
			current_gameplay_scene.set_active_region(current_gameplay_scene_id, current_spawn_id)
		scene_router.set_current_scene(current_gameplay_scene_id, current_spawn_id)
		_apply_shared_state_to_current_scene(false)
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
	current_spawn_id = next_spawn_id
	if current_gameplay_scene.has_method("set_active_region"):
		current_gameplay_scene.set_active_region(current_gameplay_scene_id, current_spawn_id)
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
	_capture_farm_plot_states_from_scene(current_gameplay_scene)
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
	_apply_farm_plot_states_to_scene(current_gameplay_scene)
	_bind_scene_managers(current_gameplay_scene)
	_place_player_at_spawn(current_spawn_id)
	if current_gameplay_scene.has_method("refresh_runtime_ui"):
		current_gameplay_scene.refresh_runtime_ui()
	_update_first_week_quest_progress()


func build_main_flow_save_data() -> Dictionary:
	sync_current_scene_state()
	var data: Dictionary = save_manager.build_runtime_save_data(self)
	data["farm_plots"] = farm_plot_states.duplicate(true)
	data["scene"] = scene_router.get_save_data()
	data["quests"] = quest_manager.get_save_data()
	return data


func apply_main_flow_save_data(data: Dictionary) -> void:
	if save_manager != null and save_manager.has_method("apply_runtime_save_data"):
		save_manager.apply_runtime_save_data(self, data)
	if data.has("farm_plots"):
		farm_plot_states = _dictionary_from(data.get("farm_plots", {}))
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
	if current_objective_chip != null and current_objective_chip.has_method("bind_quest_manager"):
		current_objective_chip.bind_quest_manager(quest_manager)
	if current_objective_chip != null and current_objective_chip.has_method("bind_game_state"):
		current_objective_chip.bind_game_state(game_state)
	if current_objective_chip != null and current_objective_chip.has_method("bind_time_manager"):
		current_objective_chip.bind_time_manager(time_manager)
	if current_objective_chip != null and current_objective_chip.has_method("bind_weather_manager"):
		current_objective_chip.bind_weather_manager(weather_manager)


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
	if scene_root.has_signal("active_region_changed"):
		if not scene_root.active_region_changed.is_connected(_on_outdoor_active_region_changed):
			scene_root.active_region_changed.connect(_on_outdoor_active_region_changed)
	if scene_game_state != null and scene_game_state.has_signal("flag_changed"):
		if not scene_game_state.flag_changed.is_connected(_on_scene_game_state_flag_changed):
			scene_game_state.flag_changed.connect(_on_scene_game_state_flag_changed)
	_connect_scene_sleep_signals(scene_root)
	# Keep exported path fallback users anchored to scene-local state mirrors.
	if scene_inventory_manager == null:
		scene_inventory_manager = inventory_manager


func _connect_scene_sleep_signals(scene_root: Node) -> void:
	if scene_root == null or scene_root.name != "PlayerHouse":
		return
	var bed := scene_root.get_node_or_null("Bed")
	if bed == null or not bed.has_signal("sleep_completed"):
		return
	if not bed.sleep_completed.is_connected(_on_scene_sleep_completed):
		bed.sleep_completed.connect(_on_scene_sleep_completed)


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
	if current_objective_chip != null and current_objective_chip.has_method("refresh"):
		current_objective_chip.refresh()


func _on_scene_game_state_flag_changed(_flag_id: String, _value: Variant) -> void:
	sync_current_scene_state()


func _on_outdoor_active_region_changed(scene_id: String, spawn_id: String) -> void:
	if not _is_outdoor_scene_id(scene_id):
		return
	current_gameplay_scene_id = scene_id
	current_spawn_id = _resolve_spawn_id(scene_id, spawn_id)
	scene_router.set_current_scene(current_gameplay_scene_id, current_spawn_id)
	_update_first_week_quest_progress()


func _on_scene_sleep_completed(_date_info: Dictionary, weather_info: Dictionary) -> void:
	_copy_scene_state_to_shared("TimeManager", time_manager)
	_copy_scene_state_to_shared("WeatherManager", weather_manager)
	var auto_water := false
	if weather_info.has("auto_water_today"):
		auto_water = bool(weather_info.get("auto_water_today", false))
	elif weather_manager != null and weather_manager.has_method("should_auto_water_today"):
		auto_water = bool(weather_manager.should_auto_water_today())
	var advance_summary := _advance_farm_plot_states_for_new_day(auto_water)
	_apply_farm_plot_states_to_scene(current_gameplay_scene)
	_show_crop_status_feedback(advance_summary)


func _capture_farm_plot_states_from_scene(scene_root: Node) -> void:
	var farm_plots := _get_scene_farm_plots(scene_root)
	if farm_plots == null:
		return
	var next_states: Dictionary = {}
	for plot in farm_plots.get_children():
		if not plot.has_method("get_save_data"):
			continue
		var plot_index := str(int(plot.get("plot_index")))
		next_states[plot_index] = plot.get_save_data()
	farm_plot_states = next_states


func _apply_farm_plot_states_to_scene(scene_root: Node) -> void:
	if farm_plot_states.is_empty():
		return
	var farm_plots := _get_scene_farm_plots(scene_root)
	if farm_plots == null:
		return
	for plot in farm_plots.get_children():
		if not plot.has_method("apply_save_data"):
			continue
		var plot_index := str(int(plot.get("plot_index")))
		if farm_plot_states.has(plot_index):
			plot.apply_save_data(_dictionary_from(farm_plot_states.get(plot_index, {})))


func _advance_farm_plot_states_for_new_day(auto_water: bool = false) -> Dictionary:
	var summary: Dictionary = {
		"advanced_count": 0,
		"ready_count": 0,
	}
	if farm_plot_states.is_empty():
		_capture_farm_plot_states_from_scene(current_gameplay_scene)
	if farm_plot_states.is_empty():
		return summary
	for key in farm_plot_states.keys():
		var plot_data: Dictionary = _dictionary_from(farm_plot_states.get(key, {}))
		var state_name := String(plot_data.get("state", "empty"))
		if state_name != "planted" and state_name != "watered":
			continue
		summary["advanced_count"] = int(summary.get("advanced_count", 0)) + 1
		var is_watered := bool(plot_data.get("is_watered", state_name == "watered"))
		if auto_water:
			is_watered = true
		var growth_days: int = max(int(plot_data.get("growth_days", 0)), 0)
		if is_watered:
			growth_days += 1
		var crop_id := String(plot_data.get("crop_id", ""))
		var crop_data: Dictionary = {}
		if data_registry != null and data_registry.has_method("get_crop") and not crop_id.is_empty():
			crop_data = data_registry.get_crop(crop_id)
		var grow_days: int = max(int(crop_data.get("grow_days", 1)), 1)
		plot_data["growth_days"] = growth_days
		if growth_days >= grow_days:
			plot_data["state"] = "ready"
			plot_data["is_watered"] = false
			summary["ready_count"] = int(summary.get("ready_count", 0)) + 1
		else:
			plot_data["state"] = "planted"
			plot_data["is_watered"] = false
		farm_plot_states[str(key)] = plot_data
	return summary


func _show_crop_status_feedback(advance_summary: Dictionary) -> void:
	var feedback_text := _build_crop_status_feedback(advance_summary)
	var reflection_text := _build_daily_intent_sleep_reflection()
	if feedback_text.is_empty() and reflection_text.is_empty():
		return
	if current_gameplay_scene == null:
		return
	var dialogue_box := current_gameplay_scene.get_node_or_null("DialogueBox")
	if dialogue_box == null or not dialogue_box.has_method("show_dialogue"):
		return
	var lines: Array[Dictionary] = []
	if not feedback_text.is_empty():
		lines.append({
			"speaker": "system",
			"text": feedback_text,
		})
	if not reflection_text.is_empty():
		lines.append({
			"speaker": "daily_reflection",
			"text": reflection_text,
		})
	var dialogue_id := "daily_intent_sleep_reflection"
	var npc_name := "睡前回想"
	if not feedback_text.is_empty():
		dialogue_id = "crop_status_sleep"
		npc_name = "菜地"
	var dialogue := {
		"dialogue_id": dialogue_id,
		"npc_id": "system",
		"lines": lines,
	}
	dialogue_box.show_dialogue(dialogue, {"npc_name": npc_name, "portrait": ""})


func _build_crop_status_feedback(advance_summary: Dictionary) -> String:
	var ready_count := int(advance_summary.get("ready_count", 0))
	if ready_count > 0:
		return "作物已经成熟，可以去院子里收获了。"
	if int(advance_summary.get("advanced_count", 0)) > 0:
		return "菜地有新变化，今天再去看看、浇浇水。"
	return ""


func _build_daily_intent_sleep_reflection() -> String:
	if quest_manager == null or not quest_manager.has_method("is_first_week_complete"):
		return ""
	if not bool(quest_manager.is_first_week_complete()):
		return ""
	if game_state == null or not game_state.has_method("get_daily_intent"):
		return ""
	var intent_id := String(game_state.get_daily_intent(_get_previous_day_key()))
	if intent_id.is_empty():
		return ""
	var base_text: String = String(DAILY_INTENT_SLEEP_REFLECTIONS.get(intent_id, "睡前想起今天也慢慢过完了。"))
	return DailyIntentContext.build_sleep_reflection(intent_id, base_text, time_manager, weather_manager)


func _get_previous_day_key() -> String:
	if time_manager != null and time_manager.has_method("get_date_info"):
		var date_info: Dictionary = time_manager.get_date_info()
		return "day_%d" % max(1, int(date_info.get("total_day", 1)) - 1)
	return "day_1"


func _get_scene_farm_plots(scene_root: Node) -> Node:
	if scene_root == null:
		return null
	return scene_root.get_node_or_null("FarmPlots")


func _resolve_spawn_id(scene_id: String, spawn_id: String) -> String:
	if not spawn_id.is_empty() and spawn_id != "default":
		return spawn_id
	var scene_info: Dictionary = SCENE_REGISTRY.get(scene_id, {})
	return String(scene_info.get("default_spawn", "default"))


func _can_reuse_current_outdoor_scene(scene_id: String) -> bool:
	if current_gameplay_scene == null or not is_instance_valid(current_gameplay_scene):
		return false
	if not _is_outdoor_scene_id(scene_id) or not _is_outdoor_scene_id(current_gameplay_scene_id):
		return false
	return current_gameplay_scene.has_method("set_active_region")


func _is_outdoor_scene_id(scene_id: String) -> bool:
	var scene_info: Dictionary = SCENE_REGISTRY.get(scene_id, {})
	return bool(scene_info.get("outdoor", false))


func _place_player_at_spawn(spawn_id: String) -> void:
	if current_gameplay_scene == null or spawn_id.is_empty():
		return
	var player := current_gameplay_scene.get_node_or_null("Player") as Node2D
	var spawn := _find_spawn(current_gameplay_scene, spawn_id)
	if player == null or spawn == null:
		return
	player.global_position = spawn.global_position


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
