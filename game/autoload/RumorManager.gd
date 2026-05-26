class_name RumorManager
extends Node

signal daily_rumors_refreshed(source: String, rumor_ids: Array[String])
signal rumor_seen(rumor_id: String)

const MIN_DAILY_RUMORS: int = 1
const MAX_DAILY_RUMORS: int = 3

var data_registry: Node = null
var game_state: Node = null
var time_manager: Node = null
var weather_manager: Node = null
var _daily_cache: Dictionary = {}


func bind_registry(next_data_registry: Node) -> void:
	data_registry = next_data_registry
	_daily_cache.clear()


func bind_game_state(next_game_state: Node) -> void:
	if game_state != null and game_state.has_signal("flag_changed") and game_state.flag_changed.is_connected(_on_game_state_flag_changed):
		game_state.flag_changed.disconnect(_on_game_state_flag_changed)
	game_state = next_game_state
	if game_state != null and game_state.has_signal("flag_changed") and not game_state.flag_changed.is_connected(_on_game_state_flag_changed):
		game_state.flag_changed.connect(_on_game_state_flag_changed)
	_daily_cache.clear()


func bind_time_manager(next_time_manager: Node) -> void:
	time_manager = next_time_manager
	_daily_cache.clear()


func bind_weather_manager(next_weather_manager: Node) -> void:
	weather_manager = next_weather_manager
	_daily_cache.clear()


func refresh_daily_rumors() -> void:
	_daily_cache.clear()


func get_daily_rumors(source: String = "mailbox") -> Array[Dictionary]:
	var cache_key := "%s:%s" % [source, _get_day_key()]
	if _daily_cache.has(cache_key):
		return _filter_seen_rumors(_daily_cache[cache_key])

	var candidates := _get_matching_rumors(source)
	candidates.sort_custom(_sort_rumors)
	var limit: int = clamp(candidates.size(), MIN_DAILY_RUMORS, MAX_DAILY_RUMORS)
	var selected: Array[Dictionary] = []
	for index in range(min(limit, candidates.size())):
		selected.append(candidates[index].duplicate(true))
	_daily_cache[cache_key] = selected.duplicate(true)
	daily_rumors_refreshed.emit(source, _rumor_ids(selected))
	return _filter_seen_rumors(selected)


func build_rumor_dialogue(source: String = "mailbox") -> Dictionary:
	var rumors: Array[Dictionary] = get_daily_rumors(source)
	var lines: Array[Dictionary] = []
	for rumor in rumors:
		lines.append({
			"speaker": source,
			"text": String(rumor.get("text", "")),
		})
	if lines.is_empty():
		lines.append({
			"speaker": source,
			"text": "今天没有新的小道消息。慢慢过这一天吧。",
		})
	return {
		"dialogue_id": "%s_rumors_runtime" % source,
		"npc_id": source,
		"type": "event",
		"priority": 80,
		"conditions": {},
		"lines": lines,
		"sets_flags": [],
		"context": {"rumor_ids": _rumor_ids(rumors)},
	}


func mark_rumors_seen(rumors: Array) -> void:
	for rumor in rumors:
		if not (rumor is Dictionary):
			continue
		var rumor_id := String(rumor.get("rumor_id", ""))
		if rumor_id.is_empty():
			continue
		for flag_id in rumor.get("sets_flags", []):
			_set_flag(String(flag_id), true)
		rumor_seen.emit(rumor_id)


func mark_dialogue_rumors_seen(dialogue: Dictionary) -> void:
	var rumor_ids: Array = dialogue.get("context", {}).get("rumor_ids", [])
	var rumors: Array = []
	for rumor_id in rumor_ids:
		var rumor: Dictionary = _get_rumor(String(rumor_id))
		if not rumor.is_empty():
			rumors.append(rumor)
	mark_rumors_seen(rumors)


func _get_matching_rumors(source: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if data_registry == null or not data_registry.has_method("get"):
		return result
	var all_rumors: Dictionary = data_registry.get("rumors")
	for rumor_id in all_rumors.keys():
		var rumor: Dictionary = all_rumors[rumor_id]
		if String(rumor.get("source", "")) != source:
			continue
		if _matches_conditions(rumor):
			result.append(rumor.duplicate(true))
	return result


func _matches_conditions(rumor: Dictionary) -> bool:
	var conditions: Dictionary = rumor.get("conditions", {})
	if not _matches_text_condition(conditions, "season", _get_season()):
		return false
	if not _matches_text_condition(conditions, "weather", _get_weather()):
		return false
	var flag_set := String(conditions.get("flag_set", ""))
	if not flag_set.is_empty() and not _get_flag(flag_set):
		return false
	var flag_not_set := String(conditions.get("flag_not_set", ""))
	if not flag_not_set.is_empty() and _get_flag(flag_not_set):
		return false
	return true


func _matches_text_condition(conditions: Dictionary, key: String, current_value: String) -> bool:
	if not conditions.has(key):
		return true
	var expected := String(conditions.get(key, "any"))
	return expected.is_empty() or expected == "any" or expected == current_value


func _filter_seen_rumors(rumors: Array) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for rumor in rumors:
		if not (rumor is Dictionary):
			continue
		if _matches_conditions(rumor):
			result.append(rumor.duplicate(true))
	return result


func _sort_rumors(a: Dictionary, b: Dictionary) -> bool:
	var a_priority := int(a.get("priority", 0))
	var b_priority := int(b.get("priority", 0))
	if a_priority != b_priority:
		return a_priority > b_priority
	return String(a.get("rumor_id", "")) < String(b.get("rumor_id", ""))


func _rumor_ids(rumors: Array) -> Array[String]:
	var ids: Array[String] = []
	for rumor in rumors:
		if rumor is Dictionary:
			ids.append(String(rumor.get("rumor_id", "")))
	return ids


func _get_rumor(rumor_id: String) -> Dictionary:
	if data_registry != null and data_registry.has_method("get_rumor"):
		return data_registry.get_rumor(rumor_id)
	return {}


func _get_day_key() -> String:
	if time_manager != null and time_manager.has_method("get_date_info"):
		var date_info: Dictionary = time_manager.get_date_info()
		return "%s:%s:%s" % [date_info.get("year", 1), date_info.get("season", "spring"), date_info.get("day_of_season", 1)]
	return "default"


func _get_season() -> String:
	if time_manager != null and time_manager.has_method("get_date_info"):
		return String(time_manager.get_date_info().get("season", "spring"))
	return "spring"


func _get_weather() -> String:
	if weather_manager != null and weather_manager.has_method("get_today_weather"):
		return String(weather_manager.get_today_weather())
	return "sunny"


func _get_flag(flag_id: String) -> bool:
	if game_state != null and game_state.has_method("get_flag"):
		return bool(game_state.get_flag(flag_id, false))
	return false


func _set_flag(flag_id: String, value: bool) -> void:
	if game_state != null and game_state.has_method("set_flag"):
		game_state.set_flag(flag_id, value)


func _on_game_state_flag_changed(_flag_id: String, _value: Variant) -> void:
	_daily_cache.clear()
