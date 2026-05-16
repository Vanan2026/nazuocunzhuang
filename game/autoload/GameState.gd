class_name GameState
extends Node

signal flag_changed(flag_id: String, value: Variant)
signal money_changed(value: int)
signal energy_changed(value: int)

var flags: Dictionary = {}
var unlocked_areas: Dictionary = {}
var restoration_states: Dictionary = {}
var discovered_items: Dictionary = {}
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


func set_player_money(value: int) -> void:
	player_money = max(value, 0)
	money_changed.emit(player_money)


func set_player_energy(value: int) -> void:
	player_energy = clamp(value, 0, 100)
	energy_changed.emit(player_energy)
