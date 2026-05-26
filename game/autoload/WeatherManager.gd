class_name WeatherManager
extends Node

signal weather_changed(weather_id: String)
signal tomorrow_weather_changed(weather_id: String)
signal auto_water_flag_changed(enabled: bool)

const WEATHER_IDS: Array[String] = ["sunny", "cloudy", "rainy"]

var today_weather: String = "sunny"
var tomorrow_weather: String = "cloudy"
var auto_water_today: bool = false
var _weather_seed: int = 0


func _ready() -> void:
	_update_auto_water_flag()


func get_today_weather() -> String:
	return today_weather


func get_tomorrow_weather() -> String:
	return tomorrow_weather


func set_today_weather(weather_id: String) -> void:
	if weather_id not in WEATHER_IDS:
		return
	today_weather = weather_id
	_update_auto_water_flag()
	weather_changed.emit(today_weather)


func set_tomorrow_weather(weather_id: String) -> void:
	if weather_id not in WEATHER_IDS:
		return
	tomorrow_weather = weather_id
	tomorrow_weather_changed.emit(tomorrow_weather)


func generate_tomorrow_weather(seed_value: int = 0) -> String:
	_weather_seed = abs(seed_value + _weather_seed + 3)
	var index: int = _weather_seed % WEATHER_IDS.size()
	tomorrow_weather = WEATHER_IDS[index]
	tomorrow_weather_changed.emit(tomorrow_weather)
	return tomorrow_weather


func advance_to_next_day(date_info: Dictionary = {}) -> void:
	set_today_weather(tomorrow_weather)
	var seed_value := int(date_info.get("total_day", _weather_seed + 1))
	generate_tomorrow_weather(seed_value)


func should_auto_water_today() -> bool:
	return auto_water_today


func get_weather_info() -> Dictionary:
	return {
		"today": today_weather,
		"tomorrow": tomorrow_weather,
		"auto_water_today": auto_water_today,
	}


func get_save_data() -> Dictionary:
	var weather_info := get_weather_info()
	weather_info["weather_seed"] = _weather_seed
	return weather_info


func apply_save_data(data: Dictionary) -> void:
	if data.is_empty():
		return
	var saved_today := String(data.get("today", today_weather))
	var saved_tomorrow := String(data.get("tomorrow", tomorrow_weather))
	if saved_today in WEATHER_IDS:
		today_weather = saved_today
	if saved_tomorrow in WEATHER_IDS:
		tomorrow_weather = saved_tomorrow
	_weather_seed = int(data.get("weather_seed", _weather_seed))
	_update_auto_water_flag()
	weather_changed.emit(today_weather)
	tomorrow_weather_changed.emit(tomorrow_weather)


func _update_auto_water_flag() -> void:
	var next_value := today_weather == "rainy"
	if next_value != auto_water_today:
		auto_water_today = next_value
		auto_water_flag_changed.emit(auto_water_today)
