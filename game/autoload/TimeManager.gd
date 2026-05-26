class_name TimeManager
extends Node

signal time_changed(date_info: Dictionary)
signal date_changed(date_info: Dictionary)
signal day_started(date_info: Dictionary)
signal day_ended(date_info: Dictionary)
signal time_block_changed(block: String)
signal season_changed(season_id: String)

const SEASONS: Array[String] = ["spring", "summer", "autumn", "winter"]
const DAY_START_HOUR: int = 6
const DAYS_PER_SEASON: int = 28
const MINUTES_PER_HOUR: int = 60

var year: int = 1
var season_index: int = 0
var day_of_season: int = 1
var day: int = 1
var total_day: int = 1
var hour: int = DAY_START_HOUR
var minute: int = 0
var current_block: String = "morning"


func _ready() -> void:
	_update_time_block(false)


func get_current_season() -> String:
	return SEASONS[season_index]


func get_next_season() -> String:
	return SEASONS[(season_index + 1) % SEASONS.size()]


func get_date_info() -> Dictionary:
	return {
		"year": year,
		"season": get_current_season(),
		"season_index": season_index,
		"day": day_of_season,
		"day_of_season": day_of_season,
		"total_day": total_day,
		"hour": hour,
		"minute": minute,
		"block": current_block,
		"time_text": get_time_text(),
	}


func get_save_data() -> Dictionary:
	return get_date_info()


func apply_save_data(data: Dictionary) -> void:
	if data.is_empty():
		return
	year = max(int(data.get("year", year)), 1)
	var saved_season := String(data.get("season", ""))
	if data.has("season_index"):
		season_index = clamp(int(data.get("season_index", season_index)), 0, SEASONS.size() - 1)
	elif saved_season in SEASONS:
		season_index = SEASONS.find(saved_season)
	day_of_season = clamp(int(data.get("day_of_season", data.get("day", day_of_season))), 1, DAYS_PER_SEASON)
	day = day_of_season
	total_day = max(int(data.get("total_day", total_day)), 1)
	hour = clamp(int(data.get("hour", hour)), 0, 23)
	minute = clamp(int(data.get("minute", minute)), 0, MINUTES_PER_HOUR - 1)
	_update_time_block(false)
	var info := get_date_info()
	date_changed.emit(info)
	time_changed.emit(info)


func get_time_text() -> String:
	return "%02d:%02d" % [hour, minute]


func advance_minutes(amount: int) -> void:
	var safe_amount: int = max(amount, 0)
	if safe_amount == 0:
		return
	minute += safe_amount
	while minute >= MINUTES_PER_HOUR:
		minute -= MINUTES_PER_HOUR
		hour += 1
	while hour >= 24:
		hour -= 24
		_advance_calendar_day(false)
	_update_time_block()
	time_changed.emit(get_date_info())


func sleep_to_next_day() -> Dictionary:
	start_next_day()
	return get_date_info()


func start_next_day() -> void:
	day_ended.emit(get_date_info())
	_advance_calendar_day(true)
	hour = DAY_START_HOUR
	minute = 0
	_update_time_block()
	var info := get_date_info()
	date_changed.emit(info)
	day_started.emit(info)
	time_changed.emit(info)


func _advance_calendar_day(_from_sleep: bool) -> void:
	total_day += 1
	day_of_season += 1
	if day_of_season > DAYS_PER_SEASON:
		day_of_season = 1
		season_index += 1
		if season_index >= SEASONS.size():
			season_index = 0
			year += 1
		season_changed.emit(get_current_season())
	day = day_of_season


func _update_time_block(emit_signal_on_change: bool = true) -> void:
	var next_block := "night"
	if hour < 9:
		next_block = "morning"
	elif hour < 12:
		next_block = "late_morning"
	elif hour < 17:
		next_block = "afternoon"
	elif hour < 20:
		next_block = "evening"
	if next_block != current_block:
		current_block = next_block
		if emit_signal_on_change:
			time_block_changed.emit(current_block)
