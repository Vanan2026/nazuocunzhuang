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
