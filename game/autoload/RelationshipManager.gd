class_name RelationshipManager
extends Node

signal relationship_changed(npc_id: String, value: int)
signal daily_social_state_reset()

var relationships: Dictionary = {}
var talked_today: Dictionary = {}
var gifted_today: Dictionary = {}


func get_relationship(npc_id: String) -> int:
	return int(relationships.get(npc_id, 0))


func add_relationship(npc_id: String, amount: int) -> void:
	var next_value := get_relationship(npc_id) + amount
	relationships[npc_id] = next_value
	relationship_changed.emit(npc_id, next_value)


func mark_talked_today(npc_id: String) -> void:
	talked_today[npc_id] = true


func has_talked_today(npc_id: String) -> bool:
	return bool(talked_today.get(npc_id, false))


func has_gifted_today(npc_id: String) -> bool:
	return bool(gifted_today.get(npc_id, false))


func mark_gifted_today(npc_id: String) -> void:
	gifted_today[npc_id] = true


func reset_daily_social_state() -> void:
	talked_today.clear()
	gifted_today.clear()
	daily_social_state_reset.emit()


func get_save_data() -> Dictionary:
	return {
		"relationships": relationships.duplicate(true),
		"talked_today": talked_today.duplicate(true),
		"gifted_today": gifted_today.duplicate(true),
	}


func apply_save_data(data: Dictionary) -> void:
	if data.is_empty():
		return
	relationships = _sanitize_int_dictionary(data.get("relationships", relationships))
	talked_today = _sanitize_bool_dictionary(data.get("talked_today", talked_today))
	gifted_today = _sanitize_bool_dictionary(data.get("gifted_today", gifted_today))
	for npc_id in relationships.keys():
		relationship_changed.emit(String(npc_id), int(relationships[npc_id]))


func _sanitize_int_dictionary(raw_value: Variant) -> Dictionary:
	var result: Dictionary = {}
	if not (raw_value is Dictionary):
		return result
	var raw_dictionary: Dictionary = raw_value
	for key in raw_dictionary.keys():
		var id := String(key)
		if id.is_empty():
			continue
		result[id] = int(raw_dictionary[key])
	return result


func _sanitize_bool_dictionary(raw_value: Variant) -> Dictionary:
	var result: Dictionary = {}
	if not (raw_value is Dictionary):
		return result
	var raw_dictionary: Dictionary = raw_value
	for key in raw_dictionary.keys():
		var id := String(key)
		if id.is_empty():
			continue
		result[id] = bool(raw_dictionary[key])
	return result
