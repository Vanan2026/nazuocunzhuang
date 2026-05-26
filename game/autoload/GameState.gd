class_name GameState
extends Node

signal flag_changed(flag_id: String, value: Variant)
signal money_changed(value: int)
signal energy_changed(value: int)

var flags: Dictionary = {}
var unlocked_areas: Dictionary = {}
var restoration_states: Dictionary = {}
var discovered_items: Dictionary = {}
var daily_intents: Dictionary = {}
var player_money: int = 500
var player_energy: int = 100


func set_flag(flag_id: String, value: Variant = true) -> void:
	flags[flag_id] = value
	flag_changed.emit(flag_id, value)


func get_flag(flag_id: String, default_value: Variant = false) -> Variant:
	return flags.get(flag_id, default_value)


func is_restored(restoration_id: String) -> bool:
	return bool(restoration_states.get(restoration_id, false))


func set_restored(restoration_id: String, value: bool = true) -> void:
	restoration_states[restoration_id] = value
	set_flag("restored_%s" % restoration_id, value)


func get_player_money() -> int:
	return player_money


func get_player_energy() -> int:
	return player_energy


func get_restoration_states() -> Dictionary:
	return restoration_states.duplicate(true)


func set_restoration_states(next_states: Dictionary) -> void:
	restoration_states = next_states.duplicate(true)
	for restoration_id in restoration_states.keys():
		if bool(restoration_states[restoration_id]):
			set_flag("restored_%s" % String(restoration_id), true)


func set_daily_intent(day_key: String, intent_id: String) -> void:
	if day_key.is_empty() or intent_id.is_empty():
		return
	daily_intents[day_key] = intent_id
	set_flag("daily_intent_%s" % day_key, intent_id)


func get_daily_intent(day_key: String) -> String:
	return String(daily_intents.get(day_key, ""))


func get_daily_intents() -> Dictionary:
	return daily_intents.duplicate(true)


func set_player_money(value: int) -> void:
	player_money = max(value, 0)
	money_changed.emit(player_money)


func set_player_energy(value: int) -> void:
	player_energy = clamp(value, 0, 100)
	energy_changed.emit(player_energy)


func get_save_data() -> Dictionary:
	return {
		"flags": flags.duplicate(true),
		"unlocked_areas": unlocked_areas.duplicate(true),
		"restoration_states": restoration_states.duplicate(true),
		"discovered_items": discovered_items.duplicate(true),
		"daily_intents": daily_intents.duplicate(true),
		"player_money": player_money,
		"player_energy": player_energy,
	}


func apply_save_data(data: Dictionary) -> void:
	if data.is_empty():
		return
	var previous_flags := flags.duplicate(true)
	var should_emit_loaded_flags := false
	if data.has("flags"):
		flags = _duplicate_dictionary(data.get("flags", flags))
		should_emit_loaded_flags = true
	if data.has("unlocked_areas"):
		unlocked_areas = _duplicate_dictionary(data.get("unlocked_areas", unlocked_areas))
	if data.has("restoration_states"):
		set_restoration_states(_duplicate_dictionary(data.get("restoration_states", restoration_states)))
	if data.has("discovered_items"):
		discovered_items = _duplicate_dictionary(data.get("discovered_items", discovered_items))
	if data.has("daily_intents"):
		daily_intents = _duplicate_dictionary(data.get("daily_intents", daily_intents))
	if data.has("player_money"):
		set_player_money(int(data.get("player_money", player_money)))
	if data.has("player_energy"):
		set_player_energy(int(data.get("player_energy", player_energy)))
	if should_emit_loaded_flags:
		_emit_loaded_flag_changes(previous_flags)


func _duplicate_dictionary(raw_value: Variant) -> Dictionary:
	if raw_value is Dictionary:
		var raw_dictionary: Dictionary = raw_value
		return raw_dictionary.duplicate(true)
	return {}


func _emit_loaded_flag_changes(previous_flags: Dictionary) -> void:
	for flag_id in previous_flags.keys():
		if not flags.has(flag_id):
			flag_changed.emit(String(flag_id), false)
	for flag_id in flags.keys():
		flag_changed.emit(String(flag_id), flags[flag_id])
