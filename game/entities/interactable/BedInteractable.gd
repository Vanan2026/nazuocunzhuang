class_name BedInteractable
extends "res://game/entities/interactable/Interactable.gd"

signal sleep_completed(date_info: Dictionary, weather_info: Dictionary)

@export var time_manager_path: NodePath
@export var weather_manager_path: NodePath
@export var hud_path: NodePath


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	var time_manager := _get_linked_node(time_manager_path, "TimeManager")
	var weather_manager := _get_linked_node(weather_manager_path, "WeatherManager")
	if time_manager != null and time_manager.has_method("sleep_to_next_day"):
		time_manager.sleep_to_next_day()
	if weather_manager != null and weather_manager.has_method("advance_to_next_day"):
		var date_info: Dictionary = {}
		if time_manager != null and time_manager.has_method("get_date_info"):
			date_info = time_manager.get_date_info()
		weather_manager.advance_to_next_day(date_info)
	var hud := _get_linked_node(hud_path, "TimeWeatherHUD")
	if hud != null and hud.has_method("refresh"):
		hud.refresh()
	var final_date_info: Dictionary = {}
	if time_manager != null and time_manager.has_method("get_date_info"):
		final_date_info = time_manager.get_date_info()
	var weather_info: Dictionary = {}
	if weather_manager != null and weather_manager.has_method("get_weather_info"):
		weather_info = weather_manager.get_weather_info()
	sleep_completed.emit(final_date_info, weather_info)


func _get_linked_node(path: NodePath, fallback_name: String) -> Node:
	var linked := get_node_or_null(path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	if parent_node == null:
		return null
	return parent_node.get_node_or_null(fallback_name)
