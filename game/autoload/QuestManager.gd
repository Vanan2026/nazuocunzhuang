class_name QuestManager
extends Node

signal quest_updated(quest_id: String, state: Dictionary)

var quest_states: Dictionary = {}


func get_quest_state(quest_id: String) -> Dictionary:
	return quest_states.get(quest_id, {})


func set_quest_state(quest_id: String, state: Dictionary) -> void:
	quest_states[quest_id] = state.duplicate(true)
	quest_updated.emit(quest_id, get_quest_state(quest_id))


func clear_quest_state(quest_id: String) -> void:
	quest_states.erase(quest_id)
	quest_updated.emit(quest_id, {})
