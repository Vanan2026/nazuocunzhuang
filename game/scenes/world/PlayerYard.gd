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
@onready var time_weather_hud: Node = $TimeWeatherHUD
@onready var inventory_ui: Node = $InventoryUI
@onready var dialogue_box: Node = $DialogueBox
@onready var farm_plots: Node = $FarmPlots
@onready var bed: Node = $Bed


func _ready() -> void:
	_ensure_data_loaded()
	_ensure_starter_inventory()
	_bind_social_managers()
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
		time_weather_hud.refresh()


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
	if time_manager != null and relationship_manager != null:
		if time_manager.has_signal("day_started") and relationship_manager.has_method("reset_daily_social_state"):
			if not time_manager.day_started.is_connected(_on_day_started):
				time_manager.day_started.connect(_on_day_started)


func _on_bed_sleep_completed(_date_info: Dictionary, _weather_info: Dictionary) -> void:
	advance_farm_plots_for_new_day()


func _on_day_started(_date_info: Dictionary) -> void:
	if relationship_manager != null and relationship_manager.has_method("reset_daily_social_state"):
		relationship_manager.reset_daily_social_state()


func _bind_social_managers() -> void:
	if dialogue_manager != null:
		if dialogue_manager.has_method("bind_registry"):
			dialogue_manager.bind_registry(data_registry)
		if dialogue_manager.has_method("bind_relationship_manager"):
			dialogue_manager.bind_relationship_manager(relationship_manager)
