class_name SeasonManager
extends Node

signal season_changed(season_id: String)

const SEASONS: Array[String] = ["spring", "summer", "autumn", "winter"]

var current_season_index: int = 0


func get_current_season() -> String:
	return SEASONS[current_season_index]


func get_next_season() -> String:
	return SEASONS[(current_season_index + 1) % SEASONS.size()]


func advance_season() -> void:
	current_season_index = (current_season_index + 1) % SEASONS.size()
	season_changed.emit(get_current_season())
