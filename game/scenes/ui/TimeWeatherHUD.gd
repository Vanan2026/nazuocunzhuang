class_name TimeWeatherHUD
extends CanvasLayer

const GreenfieldUITheme := preload("res://game/scenes/ui/GreenfieldUITheme.gd")
const ICON_COIN: Texture2D = preload("res://assets/ui/icons/ui_icon_coin.png")
const ICON_HEART: Texture2D = preload("res://assets/ui/icons/ui_icon_heart.png")
const ICON_WEATHER_SUN: Texture2D = preload("res://assets/ui/icons/ui_icon_weather_sun.png")
const ICON_WEATHER_RAIN: Texture2D = preload("res://assets/ui/icons/ui_icon_weather_rain.png")
const ICON_BAG: Texture2D = preload("res://assets/ui/icons/ui_icon_bag.png")

@export var time_manager_path: NodePath
@export var weather_manager_path: NodePath
@export var game_state_path: NodePath
@export var inventory_manager_path: NodePath
@export var data_registry_path: NodePath

@onready var panel: PanelContainer = get_node_or_null("Panel")
@onready var content: VBoxContainer = get_node_or_null("Panel/Content")
@onready var season_label: Label = get_node_or_null("Panel/Content/SeasonLabel")
@onready var day_label: Label = get_node_or_null("Panel/Content/DayLabel")
@onready var time_label: Label = get_node_or_null("Panel/Content/TimeLabel")
@onready var weather_label: Label = get_node_or_null("Panel/Content/WeatherLabel")
@onready var weather_row: HBoxContainer = get_node_or_null("Panel/Content/WeatherRow")
@onready var weather_icon: TextureRect = get_node_or_null("Panel/Content/WeatherRow/WeatherIcon")
@onready var tomorrow_weather_icon: TextureRect = get_node_or_null("Panel/Content/WeatherRow/TomorrowWeatherIcon")
@onready var status_panel: PanelContainer = get_node_or_null("StatusPanel")
@onready var coin_label: Label = get_node_or_null("StatusPanel/Content/CoinRow/CoinLabel")
@onready var energy_label: Label = get_node_or_null("StatusPanel/Content/EnergyRow/EnergyLabel")
@onready var status_label: Label = get_node_or_null("StatusPanel/Content/StatusLabel")
@onready var hotbar_panel: PanelContainer = get_node_or_null("HotbarPanel")
@onready var hotbar_slots: HBoxContainer = get_node_or_null("HotbarPanel/Slots")

var time_manager: Node = null
var weather_manager: Node = null
var game_state: Node = null
var inventory_manager: Node = null
var data_registry: Node = null


func _ready() -> void:
	if not time_manager_path.is_empty():
		time_manager = get_node_or_null(time_manager_path)
	if not weather_manager_path.is_empty():
		weather_manager = get_node_or_null(weather_manager_path)
	if not game_state_path.is_empty():
		game_state = get_node_or_null(game_state_path)
	if not inventory_manager_path.is_empty():
		inventory_manager = get_node_or_null(inventory_manager_path)
	if not data_registry_path.is_empty():
		data_registry = get_node_or_null(data_registry_path)
	_apply_visual_theme()
	bind_managers(time_manager, weather_manager)
	bind_status_manager(game_state)
	bind_inventory_manager(inventory_manager, data_registry)
	refresh()


func bind_managers(next_time_manager: Node, next_weather_manager: Node) -> void:
	time_manager = next_time_manager
	weather_manager = next_weather_manager
	if time_manager != null:
		if time_manager.has_signal("time_changed") and not time_manager.time_changed.is_connected(_on_time_changed):
			time_manager.time_changed.connect(_on_time_changed)
		if time_manager.has_signal("date_changed") and not time_manager.date_changed.is_connected(_on_time_changed):
			time_manager.date_changed.connect(_on_time_changed)
	if weather_manager != null:
		if weather_manager.has_signal("weather_changed") and not weather_manager.weather_changed.is_connected(_on_weather_changed):
			weather_manager.weather_changed.connect(_on_weather_changed)
		if weather_manager.has_signal("tomorrow_weather_changed") and not weather_manager.tomorrow_weather_changed.is_connected(_on_weather_changed):
			weather_manager.tomorrow_weather_changed.connect(_on_weather_changed)


func bind_status_manager(next_game_state: Node) -> void:
	game_state = next_game_state
	if game_state == null:
		return
	if game_state.has_signal("money_changed") and not game_state.money_changed.is_connected(_on_status_changed):
		game_state.money_changed.connect(_on_status_changed)
	if game_state.has_signal("energy_changed") and not game_state.energy_changed.is_connected(_on_status_changed):
		game_state.energy_changed.connect(_on_status_changed)


func bind_inventory_manager(next_inventory_manager: Node, next_data_registry: Node = null) -> void:
	inventory_manager = next_inventory_manager
	data_registry = next_data_registry
	if inventory_manager == null:
		return
	if inventory_manager.has_signal("inventory_changed") and not inventory_manager.inventory_changed.is_connected(_on_inventory_changed):
		inventory_manager.inventory_changed.connect(_on_inventory_changed)
	if inventory_manager.has_signal("selected_item_changed") and not inventory_manager.selected_item_changed.is_connected(_on_selected_item_changed):
		inventory_manager.selected_item_changed.connect(_on_selected_item_changed)


func refresh() -> void:
	_ensure_nodes()
	_apply_visual_theme()
	_refresh_time_weather()
	_refresh_status()
	_refresh_hotbar()


func get_weather_icon_path(weather_id: String) -> String:
	if weather_id == "rainy":
		return "res://assets/ui/icons/ui_icon_weather_rain.png"
	return "res://assets/ui/icons/ui_icon_weather_sun.png"


func _refresh_time_weather() -> void:
	if season_label == null or day_label == null or time_label == null or weather_label == null:
		return
	if time_manager != null and time_manager.has_method("get_date_info"):
		var date_info: Dictionary = time_manager.get_date_info()
		season_label.text = "Spring %d" % int(date_info.get("day_of_season", 1)) if String(date_info.get("season", "spring")) == "spring" else "%s %d" % [_season_text(String(date_info.get("season", "spring"))), int(date_info.get("day_of_season", 1))]
		day_label.text = "Year %d  %s" % [int(date_info.get("year", 1)), _block_text(String(date_info.get("block", "morning")))]
		time_label.text = String(date_info.get("time_text", "06:00"))
	else:
		season_label.text = "Spring 1"
		day_label.text = "Year 1  Morning"
		time_label.text = "06:00"

	if weather_manager != null and weather_manager.has_method("get_weather_info"):
		var weather_info: Dictionary = weather_manager.get_weather_info()
		var today_weather := String(weather_info.get("today", "sunny"))
		var tomorrow_weather := String(weather_info.get("tomorrow", "cloudy"))
		weather_label.text = "%s today / %s tomorrow" % [
			_weather_text(today_weather),
			_weather_text(tomorrow_weather),
		]
		_set_weather_icon(weather_icon, today_weather)
		_set_weather_icon(tomorrow_weather_icon, tomorrow_weather)
	else:
		weather_label.text = "Sunny today / Cloudy tomorrow"
		_set_weather_icon(weather_icon, "sunny")
		_set_weather_icon(tomorrow_weather_icon, "cloudy")


func _refresh_status() -> void:
	var money := 0
	var energy := 100
	if game_state != null:
		if game_state.has_method("get_player_money"):
			money = int(game_state.get_player_money())
		if game_state.has_method("get_player_energy"):
			energy = int(game_state.get_player_energy())
	if coin_label != null:
		coin_label.text = "%d" % money
	if energy_label != null:
		energy_label.text = "%d / 100" % energy
	if status_label != null:
		status_label.text = "Settling in"


func _refresh_hotbar() -> void:
	if hotbar_slots == null:
		return
	for child in hotbar_slots.get_children():
		child.queue_free()
	var snapshot: Dictionary = {}
	var selected_item_id := ""
	if inventory_manager != null:
		if inventory_manager.has_method("get_inventory_snapshot"):
			snapshot = inventory_manager.get_inventory_snapshot()
		if inventory_manager.has_method("get_selected_item_id"):
			selected_item_id = String(inventory_manager.get_selected_item_id())
	var item_ids := snapshot.keys()
	item_ids.sort()
	for slot_index in range(8):
		var slot_button := Button.new()
		slot_button.focus_mode = Control.FOCUS_NONE
		slot_button.disabled = true
		slot_button.custom_minimum_size = Vector2(64, 64)
		if slot_index < item_ids.size():
			var item_id := String(item_ids[slot_index])
			slot_button.text = "%d\n%s" % [slot_index + 1, _short_item_name(item_id)]
			slot_button.tooltip_text = "%s x%d" % [_get_item_name(item_id), int(snapshot[item_id])]
			GreenfieldUITheme.apply_item_slot(slot_button, item_id == selected_item_id)
		else:
			slot_button.text = "%d" % (slot_index + 1)
			slot_button.tooltip_text = "Empty quick slot"
			GreenfieldUITheme.apply_item_slot(slot_button, false)
		hotbar_slots.add_child(slot_button)


func _on_time_changed(_date_info: Dictionary) -> void:
	refresh()


func _on_weather_changed(_weather_id: String) -> void:
	refresh()


func _on_status_changed(_value: int) -> void:
	refresh()


func _on_inventory_changed() -> void:
	refresh()


func _on_selected_item_changed(_item_id: String) -> void:
	refresh()


func _ensure_nodes() -> void:
	if panel == null:
		panel = get_node_or_null("Panel")
	if content == null:
		content = get_node_or_null("Panel/Content")
	if season_label == null:
		season_label = get_node_or_null("Panel/Content/SeasonLabel")
	if day_label == null:
		day_label = get_node_or_null("Panel/Content/DayLabel")
	if time_label == null:
		time_label = get_node_or_null("Panel/Content/TimeLabel")
	if weather_label == null:
		weather_label = get_node_or_null("Panel/Content/WeatherLabel")
	if weather_row == null:
		weather_row = get_node_or_null("Panel/Content/WeatherRow")
	if weather_icon == null:
		weather_icon = get_node_or_null("Panel/Content/WeatherRow/WeatherIcon")
	if tomorrow_weather_icon == null:
		tomorrow_weather_icon = get_node_or_null("Panel/Content/WeatherRow/TomorrowWeatherIcon")
	if status_panel == null:
		status_panel = get_node_or_null("StatusPanel")
	if coin_label == null:
		coin_label = get_node_or_null("StatusPanel/Content/CoinRow/CoinLabel")
	if energy_label == null:
		energy_label = get_node_or_null("StatusPanel/Content/EnergyRow/EnergyLabel")
	if status_label == null:
		status_label = get_node_or_null("StatusPanel/Content/StatusLabel")
	if hotbar_panel == null:
		hotbar_panel = get_node_or_null("HotbarPanel")
	if hotbar_slots == null:
		hotbar_slots = get_node_or_null("HotbarPanel/Slots")


func _apply_visual_theme() -> void:
	_ensure_nodes()
	GreenfieldUITheme.apply_hud_panel(panel)
	GreenfieldUITheme.apply_hud_panel(status_panel)
	GreenfieldUITheme.apply_hud_panel(hotbar_panel)
	for label in [season_label, day_label, time_label, coin_label, energy_label, status_label]:
		var typed_label := label as Label
		if typed_label != null:
			GreenfieldUITheme.apply_body_label(typed_label, 13)
	GreenfieldUITheme.apply_hint_label(weather_label, 12)
	if time_label != null:
		GreenfieldUITheme.apply_title_label(time_label, 18)
	if content != null:
		content.add_theme_constant_override("separation", 2)
	if weather_row != null:
		weather_row.add_theme_constant_override("separation", 6)
	if weather_icon != null:
		weather_icon.texture = ICON_WEATHER_SUN
	if tomorrow_weather_icon != null:
		tomorrow_weather_icon.texture = ICON_WEATHER_SUN
	var coin_icon := get_node_or_null("StatusPanel/Content/CoinRow/CoinIcon") as TextureRect
	if coin_icon != null:
		coin_icon.texture = ICON_COIN
	var energy_icon := get_node_or_null("StatusPanel/Content/EnergyRow/EnergyIcon") as TextureRect
	if energy_icon != null:
		energy_icon.texture = ICON_HEART
	var bag_icon := get_node_or_null("HotbarPanel/BagIcon") as TextureRect
	if bag_icon != null:
		bag_icon.texture = ICON_BAG


func _set_weather_icon(icon: TextureRect, weather_id: String) -> void:
	if icon == null:
		return
	icon.texture = ICON_WEATHER_RAIN if weather_id == "rainy" else ICON_WEATHER_SUN


func _season_text(season_id: String) -> String:
	match season_id:
		"spring":
			return "Spring"
		"summer":
			return "Summer"
		"autumn":
			return "Autumn"
		"winter":
			return "Winter"
		_:
			return season_id.capitalize()


func _weather_text(weather_id: String) -> String:
	match weather_id:
		"sunny":
			return "Sunny"
		"cloudy":
			return "Cloudy"
		"rainy":
			return "Rainy"
		_:
			return weather_id.capitalize()


func _block_text(block_id: String) -> String:
	match block_id:
		"late_morning":
			return "Late Morning"
		"afternoon":
			return "Afternoon"
		"evening":
			return "Evening"
		"night":
			return "Night"
		_:
			return "Morning"


func _get_item_name(item_id: String) -> String:
	if data_registry != null and data_registry.has_method("get_item"):
		var item_data: Dictionary = data_registry.get_item(item_id)
		var item_name := String(item_data.get("name", ""))
		if not item_name.is_empty():
			return item_name
	return item_id


func _short_item_name(item_id: String) -> String:
	var item_name := _get_item_name(item_id)
	if item_name.length() <= 8:
		return item_name
	return item_name.substr(0, 7)
