class_name PlayerYard
extends Node2D

@export var starter_seed_item_id: String = "seed_turnip"
@export var starter_seed_count: int = 6

@onready var data_registry: Node = $DataRegistry
@onready var inventory_manager: Node = $InventoryManager
@onready var weather_manager: Node = $WeatherManager
@onready var time_manager: Node = $TimeManager
@onready var dialogue_manager: Node = $DialogueManager
@onready var relationship_manager: Node = $RelationshipManager
@onready var rumor_manager: Node = $RumorManager
@onready var game_state: Node = $GameState
@onready var save_manager: Node = $SaveManager
@onready var time_weather_hud: Node = $TimeWeatherHUD
@onready var inventory_ui: Node = $InventoryUI
@onready var dialogue_box: Node = $DialogueBox
@onready var farm_plots: Node = $FarmPlots
@onready var bed: Node = $Bed
@onready var mailbox: Node = $Mailbox
@onready var bulletin_board: Node = $BulletinBoard
@onready var schedule_director: Node = $ScheduleDirector
@onready var player: Node = $Player


func _ready() -> void:
	_ensure_data_loaded()
	_ensure_starter_inventory()
	_bind_social_managers()
	_bind_rumor_manager()
	_connect_runtime_signals()
	refresh_runtime_ui()


func advance_farm_plots_for_new_day() -> void:
	var auto_water := false
	if weather_manager != null and weather_manager.has_method("should_auto_water_today"):
		auto_water = bool(weather_manager.should_auto_water_today())
	for plot in farm_plots.get_children():
		if plot.has_method("advance_day"):
			plot.advance_day(auto_water)
	refresh_runtime_ui()


func refresh_runtime_ui() -> void:
	if inventory_ui != null:
		if inventory_ui.has_method("bind_managers"):
			inventory_ui.bind_managers(inventory_manager, data_registry)
		if inventory_ui.has_method("refresh"):
			inventory_ui.refresh()
	if time_weather_hud != null and time_weather_hud.has_method("refresh"):
		if time_weather_hud.has_method("bind_managers"):
			time_weather_hud.bind_managers(time_manager, weather_manager)
		time_weather_hud.refresh()


func save_game(path: String = SaveManager.DEFAULT_SAVE_PATH) -> bool:
	if save_manager == null or not save_manager.has_method("save_game"):
		return false
	return bool(save_manager.save_game(self, path))


func load_game(path: String = SaveManager.DEFAULT_SAVE_PATH) -> bool:
	if save_manager == null or not save_manager.has_method("load_game"):
		return false
	var did_load := bool(save_manager.load_game(self, path))
	if did_load:
		refresh_runtime_ui()
	return did_load


func _unhandled_input(_event: InputEvent) -> void:
	if Input.is_action_just_pressed("debug_save"):
		save_game()
	elif Input.is_action_just_pressed("debug_load"):
		load_game()


func show_mailbox_rumors() -> void:
	if rumor_manager == null or dialogue_box == null:
		return
	if not rumor_manager.has_method("build_rumor_dialogue"):
		return
	var dialogue: Dictionary = rumor_manager.build_rumor_dialogue("mailbox")
	if dialogue_box.has_method("show_dialogue"):
		dialogue_box.show_dialogue(dialogue, {
			"npc_name": "邮箱",
			"portrait": "",
		})
	if rumor_manager.has_method("mark_dialogue_rumors_seen"):
		rumor_manager.mark_dialogue_rumors_seen(dialogue)


func show_bulletin_rumors() -> Dictionary:
	if bulletin_board != null and bulletin_board.has_method("show_rumors"):
		return bulletin_board.show_rumors()
	if rumor_manager == null or dialogue_box == null:
		return {}
	if not rumor_manager.has_method("build_rumor_dialogue"):
		return {}
	var dialogue: Dictionary = rumor_manager.build_rumor_dialogue("bulletin")
	if dialogue_box.has_method("show_dialogue"):
		dialogue_box.show_dialogue(dialogue, {
			"npc_name": "公告板",
			"portrait": "",
		})
	if rumor_manager.has_method("mark_dialogue_rumors_seen"):
		rumor_manager.mark_dialogue_rumors_seen(dialogue)
	return dialogue


func _ensure_data_loaded() -> void:
	if data_registry == null:
		return
	if data_registry.has_method("load_all_data") and not bool(data_registry.get("is_loaded")):
		data_registry.load_all_data()
	if data_registry.has_method("validate_all_data"):
		data_registry.validate_all_data()


func _ensure_starter_inventory() -> void:
	if inventory_manager == null:
		return
	if inventory_manager.has_method("get_count") and inventory_manager.get_count(starter_seed_item_id) < starter_seed_count:
		var missing_count: int = starter_seed_count - int(inventory_manager.get_count(starter_seed_item_id))
		inventory_manager.add_item(starter_seed_item_id, missing_count)
	if inventory_manager.has_method("set_selected_item"):
		inventory_manager.set_selected_item(starter_seed_item_id)


func _connect_runtime_signals() -> void:
	if bed != null and bed.has_signal("sleep_completed") and not bed.sleep_completed.is_connected(_on_bed_sleep_completed):
		bed.sleep_completed.connect(_on_bed_sleep_completed)
	if mailbox != null and mailbox.has_signal("interacted") and not mailbox.interacted.is_connected(_on_mailbox_interacted):
		mailbox.interacted.connect(_on_mailbox_interacted)
	if time_manager != null and relationship_manager != null:
		if time_manager.has_signal("day_started") and relationship_manager.has_method("reset_daily_social_state"):
			if not time_manager.day_started.is_connected(_on_day_started):
				time_manager.day_started.connect(_on_day_started)


func _on_bed_sleep_completed(_date_info: Dictionary, _weather_info: Dictionary) -> void:
	advance_farm_plots_for_new_day()


func _on_mailbox_interacted(_interactor: Node, _interactable_id: String) -> void:
	show_mailbox_rumors()


func _on_day_started(_date_info: Dictionary) -> void:
	if relationship_manager != null and relationship_manager.has_method("reset_daily_social_state"):
		relationship_manager.reset_daily_social_state()
	if rumor_manager != null and rumor_manager.has_method("refresh_daily_rumors"):
		rumor_manager.refresh_daily_rumors()
	if schedule_director != null and schedule_director.has_method("apply_schedule"):
		schedule_director.apply_schedule()


func _bind_social_managers() -> void:
	if dialogue_manager != null:
		if dialogue_manager.has_method("bind_registry"):
			dialogue_manager.bind_registry(data_registry)
		if dialogue_manager.has_method("bind_relationship_manager"):
			dialogue_manager.bind_relationship_manager(relationship_manager)


func _bind_rumor_manager() -> void:
	if rumor_manager == null:
		return
	if rumor_manager.has_method("bind_registry"):
		rumor_manager.bind_registry(data_registry)
	if rumor_manager.has_method("bind_game_state"):
		rumor_manager.bind_game_state(game_state)
	if rumor_manager.has_method("bind_time_manager"):
		rumor_manager.bind_time_manager(time_manager)
	if rumor_manager.has_method("bind_weather_manager"):
		rumor_manager.bind_weather_manager(weather_manager)
