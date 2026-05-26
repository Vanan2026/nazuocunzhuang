class_name TimeWeatherHUD
extends CanvasLayer
const GreenfieldUITheme := preload("res://game/scenes/ui/GreenfieldUITheme.gd")

@export var time_manager_path: NodePath
@export var weather_manager_path: NodePath

@onready var panel: PanelContainer = get_node_or_null("Panel")
@onready var content: VBoxContainer = get_node_or_null("Panel/Content")
@onready var season_label: Label = get_node_or_null("Panel/Content/SeasonLabel")
@onready var day_label: Label = get_node_or_null("Panel/Content/DayLabel")
@onready var time_label: Label = get_node_or_null("Panel/Content/TimeLabel")
@onready var weather_label: Label = get_node_or_null("Panel/Content/WeatherLabel")
@onready var weather_row: HBoxContainer = get_node_or_null("Panel/Content/WeatherRow")
@onready var weather_icon: TextureRect = get_node_or_null("Panel/Content/WeatherRow/WeatherIcon")
@onready var tomorrow_weather_icon: TextureRect = get_node_or_null("Panel/Content/WeatherRow/TomorrowWeatherIcon")

var time_manager: Node = null
var weather_manager: Node = null


func _ready() -> void:
	if not time_manager_path.is_empty():
		time_manager = get_node_or_null(time_manager_path)
	if not weather_manager_path.is_empty():
		weather_manager = get_node_or_null(weather_manager_path)
	_apply_visual_theme()
	bind_managers(time_manager, weather_manager)
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


func refresh() -> void:
	_ensure_labels()
	if season_label == null or day_label == null or time_label == null or weather_label == null:
		return
	if time_manager != null and time_manager.has_method("get_date_info"):
		var date_info: Dictionary = time_manager.get_date_info()
		season_label.text = "季节: %s" % _season_text(String(date_info.get("season", "spring")))
		day_label.text = "第 %d 天" % int(date_info.get("day_of_season", 1))
		time_label.text = "时间: %s" % String(date_info.get("time_text", "06:00"))
	else:
		season_label.text = "季节: 春"
		day_label.text = "第 1 天"
		time_label.text = "时间: 06:00"

	if weather_manager != null and weather_manager.has_method("get_weather_info"):
		var weather_info: Dictionary = weather_manager.get_weather_info()
		var today_weather := String(weather_info.get("today", "sunny"))
		var tomorrow_weather := String(weather_info.get("tomorrow", "cloudy"))
		weather_label.text = "天气: %s / 明日 %s" % [
			_weather_text(today_weather),
			_weather_text(tomorrow_weather),
		]
		_set_weather_icon(weather_icon, today_weather)
		_set_weather_icon(tomorrow_weather_icon, tomorrow_weather)
	else:
		weather_label.text = "天气: 晴 / 明日 多云"
		_set_weather_icon(weather_icon, "sunny")
		_set_weather_icon(tomorrow_weather_icon, "cloudy")


func get_weather_icon_path(weather_id: String) -> String:
	return "res://assets/art/icons/weather_%s_64.png" % weather_id


func _on_time_changed(_date_info: Dictionary) -> void:
	refresh()


func _on_weather_changed(_weather_id: String) -> void:
	refresh()


func _ensure_labels() -> void:
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


func _apply_visual_theme() -> void:
	_ensure_labels()
	GreenfieldUITheme.apply_hud_panel(panel)
	GreenfieldUITheme.apply_body_label(season_label, 13)
	GreenfieldUITheme.apply_body_label(day_label, 13)
	GreenfieldUITheme.apply_body_label(time_label, 13)
	GreenfieldUITheme.apply_hint_label(weather_label, 12)
	if content != null:
		content.add_theme_constant_override("separation", 2)
	if weather_row != null:
		weather_row.add_theme_constant_override("separation", 6)


func _set_weather_icon(icon: TextureRect, weather_id: String) -> void:
	if icon == null:
		return
	var icon_path := get_weather_icon_path(weather_id)
	icon.texture = _load_texture(icon_path)


func _load_texture(path: String) -> Texture2D:
	if path.is_empty():
		return null
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	if FileAccess.file_exists(path):
		var image := Image.load_from_file(path)
		if image != null and not image.is_empty():
			return ImageTexture.create_from_image(image)
	return null


func _season_text(season_id: String) -> String:
	match season_id:
		"spring":
			return "春"
		"summer":
			return "夏"
		"autumn":
			return "秋"
		"winter":
			return "冬"
		_:
			return season_id


func _weather_text(weather_id: String) -> String:
	match weather_id:
		"sunny":
			return "晴"
		"cloudy":
			return "多云"
		"rainy":
			return "雨"
		_:
			return weather_id
