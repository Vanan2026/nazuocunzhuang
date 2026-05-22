class_name QuestManager
extends Node

signal quest_updated(quest_id: String, state: Dictionary)

const FIRST_WEEK_QUEST_ID: String = "first_week_restore_path"
const FIRST_WEEK_OBJECTIVES: Array[String] = [
	"read_mailbox_day1",
	"read_bulletin_day1",
	"old_well_restored",
	"garden_bench_restored",
	"village_sign_restored",
	"heard_forest_edge_notice",
	"visited_forest_edge",
	"heard_npc_forest_edge",
]

var quest_states: Dictionary = {}


func get_quest_state(quest_id: String) -> Dictionary:
	return quest_states.get(quest_id, {})


func set_quest_state(quest_id: String, state: Dictionary) -> void:
	quest_states[quest_id] = state.duplicate(true)
	quest_updated.emit(quest_id, get_quest_state(quest_id))


func clear_quest_state(quest_id: String) -> void:
	quest_states.erase(quest_id)
	quest_updated.emit(quest_id, {})


func update_first_week_progress(game_state: Node = null, scene_router: Node = null) -> Dictionary:
	var objectives: Dictionary = {
		"read_mailbox_day1": _get_flag(game_state, "read_mailbox_day1"),
		"read_bulletin_day1": _get_flag(game_state, "read_bulletin_day1"),
		"old_well_restored": _is_restored(game_state, "old_well"),
		"garden_bench_restored": _is_restored(game_state, "garden_bench"),
		"village_sign_restored": _is_restored(game_state, "village_sign"),
		"heard_forest_edge_notice": _get_flag(game_state, "heard_forest_edge_notice"),
		"visited_forest_edge": _get_flag(game_state, "visited_forest_edge"),
		"heard_npc_forest_edge": _get_flag(game_state, "heard_npc_forest_edge"),
	}
	if scene_router != null and scene_router.has_method("get_current_scene_id") and String(scene_router.get_current_scene_id()) == "forest_edge":
		objectives["visited_forest_edge"] = bool(objectives["visited_forest_edge"]) or _get_flag(game_state, "visited_forest_edge")

	var completed_count := 0
	for objective_id in FIRST_WEEK_OBJECTIVES:
		if bool(objectives.get(objective_id, false)):
			completed_count += 1
	var completed := completed_count >= FIRST_WEEK_OBJECTIVES.size()
	var state: Dictionary = {
		"quest_id": FIRST_WEEK_QUEST_ID,
		"objectives": objectives,
		"completed_count": completed_count,
		"completed": completed,
	}
	set_quest_state(FIRST_WEEK_QUEST_ID, state)
	return state.duplicate(true)


func get_first_week_progress() -> Dictionary:
	var state: Dictionary = quest_states.get(FIRST_WEEK_QUEST_ID, {})
	if state.is_empty():
		return {
			"quest_id": FIRST_WEEK_QUEST_ID,
			"objectives": {},
			"completed_count": 0,
			"completed": false,
		}
	return state.duplicate(true)


func is_first_week_complete() -> bool:
	return bool(get_first_week_progress().get("completed", false))


func get_save_data() -> Dictionary:
	return quest_states.duplicate(true)


func apply_save_data(data: Dictionary) -> void:
	if data.is_empty():
		return
	if data.has("quest_states") and data.get("quest_states") is Dictionary:
		var nested_states: Dictionary = data.get("quest_states")
		quest_states = nested_states.duplicate(true)
	else:
		quest_states = data.duplicate(true)
	if not quest_states.has(FIRST_WEEK_QUEST_ID):
		quest_states[FIRST_WEEK_QUEST_ID] = get_first_week_progress()
	for quest_id in quest_states.keys():
		quest_updated.emit(String(quest_id), get_quest_state(String(quest_id)))


func _get_flag(game_state: Node, flag_id: String) -> bool:
	if game_state != null and game_state.has_method("get_flag"):
		return bool(game_state.get_flag(flag_id, false))
	return false


func _is_restored(game_state: Node, restoration_id: String) -> bool:
	if game_state != null and game_state.has_method("is_restored"):
		return bool(game_state.is_restored(restoration_id))
	return _get_flag(game_state, "restored_%s" % restoration_id)
