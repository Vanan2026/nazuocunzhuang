class_name DialogueManager
extends Node

signal dialogue_started(npc_id: String)
signal dialogue_finished(npc_id: String)

const TYPE_PRIORITY: Dictionary = {
	"event": 0,
	"relationship": 1,
	"weather": 2,
	"seasonal": 3,
	"daily": 4,
	"fallback": 5,
}

var active_npc_id: String = ""
var active_dialogue: Dictionary = {}
var data_registry: Node = null
var relationship_manager: Node = null
var flags: Dictionary = {}


func get_dialogue(npc_id: String, context: Dictionary = {}) -> Dictionary:
	var candidates := _get_dialogue_candidates(npc_id)
	var merged_context := _build_context(npc_id, context)
	var matches: Array[Dictionary] = []
	for dialogue in candidates:
		if _matches_conditions(dialogue, merged_context):
			matches.append(dialogue)
	if matches.is_empty():
		return _fallback_dialogue(npc_id, merged_context)
	matches.sort_custom(_sort_dialogues)
	var selected := matches[0].duplicate(true)
	selected["context"] = merged_context
	return selected


func get_daily_intent_dialogue(npc_id: String, context: Dictionary = {}) -> Dictionary:
	var merged_context := _build_context(npc_id, context)
	var required_daily_intent := String(merged_context.get("daily_intent", ""))
	if required_daily_intent.is_empty():
		return {}
	var matches: Array[Dictionary] = []
	for dialogue in _get_dialogue_candidates(npc_id):
		var conditions: Dictionary = dialogue.get("conditions", {})
		if String(conditions.get("daily_intent", "")) != required_daily_intent:
			continue
		if _matches_conditions(dialogue, merged_context):
			matches.append(dialogue)
	if matches.is_empty():
		return {}
	matches.sort_custom(_sort_dialogues)
	var selected := matches[0].duplicate(true)
	selected["context"] = merged_context
	return selected


func bind_registry(next_data_registry: Node) -> void:
	data_registry = next_data_registry


func bind_relationship_manager(next_relationship_manager: Node) -> void:
	relationship_manager = next_relationship_manager


func start_dialogue(npc_id: String, dialogue: Dictionary = {}) -> void:
	active_npc_id = npc_id
	active_dialogue = dialogue.duplicate(true)
	dialogue_started.emit(npc_id)


func finish_dialogue() -> void:
	var finished_npc_id := active_npc_id
	for flag_id in active_dialogue.get("sets_flags", []):
		set_flag(String(flag_id), true)
	active_npc_id = ""
	active_dialogue.clear()
	dialogue_finished.emit(finished_npc_id)


func set_flag(flag_id: String, value: bool = true) -> void:
	if flag_id.is_empty():
		return
	flags[flag_id] = value


func has_flag(flag_id: String) -> bool:
	return bool(flags.get(flag_id, false))


func clear_flags() -> void:
	flags.clear()


func _get_dialogue_candidates(npc_id: String) -> Array[Dictionary]:
	var candidates: Array[Dictionary] = []
	if data_registry == null:
		return candidates
	for dialogue_id in data_registry.dialogues.keys():
		var dialogue: Dictionary = data_registry.dialogues[dialogue_id]
		if String(dialogue.get("npc_id", "")) == npc_id:
			candidates.append(dialogue)
	return candidates


func _build_context(npc_id: String, context: Dictionary) -> Dictionary:
	var merged := context.duplicate(true)
	if not merged.has("flags"):
		merged["flags"] = flags
	if not merged.has("hearts"):
		var relationship_value := 0
		if relationship_manager != null and relationship_manager.has_method("get_relationship"):
			relationship_value = int(relationship_manager.get_relationship(npc_id))
		merged["hearts"] = relationship_value
	return merged


func _matches_conditions(dialogue: Dictionary, context: Dictionary) -> bool:
	var conditions: Dictionary = dialogue.get("conditions", {})
	if not _matches_text_condition(conditions, context, "season"):
		return false
	if not _matches_text_condition(conditions, context, "weather"):
		return false
	if not _matches_text_condition(conditions, context, "time_block"):
		return false
	if not _matches_text_condition(conditions, context, "daily_intent"):
		return false
	if not _matches_text_condition(conditions, context, "scene_id"):
		return false
	var min_hearts := int(conditions.get("min_hearts", 0))
	if int(context.get("hearts", 0)) < min_hearts:
		return false
	var max_hearts := int(conditions.get("max_hearts", 999999))
	if int(context.get("hearts", 0)) > max_hearts:
		return false
	var flag_set := String(conditions.get("flag_set", ""))
	if not flag_set.is_empty() and not _context_has_flag(context, flag_set):
		return false
	var flag_not_set := String(conditions.get("flag_not_set", ""))
	if not flag_not_set.is_empty() and _context_has_flag(context, flag_not_set):
		return false
	return true


func _matches_text_condition(conditions: Dictionary, context: Dictionary, key: String) -> bool:
	if not conditions.has(key):
		return true
	var expected := String(conditions.get(key, "any"))
	if expected == "any" or expected.is_empty():
		return true
	return String(context.get(key, "any")) == expected


func _context_has_flag(context: Dictionary, flag_id: String) -> bool:
	var context_flags: Dictionary = context.get("flags", {})
	return bool(context_flags.get(flag_id, flags.get(flag_id, false)))


func _sort_dialogues(a: Dictionary, b: Dictionary) -> bool:
	var a_type := String(a.get("type", "fallback"))
	var b_type := String(b.get("type", "fallback"))
	var a_type_rank := int(TYPE_PRIORITY.get(a_type, 99))
	var b_type_rank := int(TYPE_PRIORITY.get(b_type, 99))
	if a_type_rank != b_type_rank:
		return a_type_rank < b_type_rank
	return int(a.get("priority", 0)) > int(b.get("priority", 0))


func _fallback_dialogue(npc_id: String, context: Dictionary) -> Dictionary:
	return {
		"dialogue_id": "%s_fallback_runtime" % npc_id,
		"npc_id": npc_id,
		"type": "fallback",
		"priority": 0,
		"conditions": {},
		"lines": [
			{"speaker": npc_id, "text": "今天也慢慢来吧。"},
		],
		"sets_flags": [],
		"context": context,
	}
