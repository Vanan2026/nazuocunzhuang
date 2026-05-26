class_name QuestManager
extends Node

signal quest_updated(quest_id: String, state: Dictionary)

const FIRST_WEEK_QUEST_ID: String = "first_week_restore_path"
const FIRST_WEEK_OBJECTIVES: Array[String] = [
	"read_mailbox_day1",
	"read_bulletin_day1",
	"old_well_restored",
	"watered_first_crop_day1",
	"harvested_first_crop_day1",
	"shared_first_turnip_day1",
	"planted_aoi_strawberry_day1",
	"garden_bench_restored",
	"village_sign_restored",
	"heard_forest_edge_notice",
	"visited_forest_edge",
	"heard_npc_forest_edge",
	"read_village_notice_day1",
]
const FIRST_WEEK_OBJECTIVE_LABELS: Dictionary = {
	"read_mailbox_day1": "读邮箱",
	"read_bulletin_day1": "看公告板",
	"old_well_restored": "修旧井",
	"watered_first_crop_day1": "给第一块作物浇水",
	"harvested_first_crop_day1": "收获第一棵作物",
	"shared_first_turnip_day1": "把第一根萝卜送给葵",
	"planted_aoi_strawberry_day1": "种下葵送的草莓",
	"garden_bench_restored": "修长椅",
	"village_sign_restored": "扶正路牌",
	"heard_forest_edge_notice": "读森林边缘公告",
	"visited_forest_edge": "去森林边缘",
	"heard_npc_forest_edge": "听 Mika 的传闻",
	"read_village_notice_day1": "去村口看公告",
}
const FIRST_WEEK_OBJECTIVE_HINTS: Dictionary = {
	"read_mailbox_day1": "屋内 · 出门到院子邮箱旁，按 E 查看",
	"read_bulletin_day1": "院子 · 邮箱右侧公告板，靠近后按 E",
	"old_well_restored": "院子右侧 · 旧水井，备好木石后按 E 修复",
	"watered_first_crop_day1": "院子左下菜地 · 整理土地、播种后按 E 浇水",
	"harvested_first_crop_day1": "回屋睡觉后继续浇水，成熟后按 E 收获",
	"shared_first_turnip_day1": "院子里 · 在背包选择春萝卜，再和葵交谈",
	"planted_aoi_strawberry_day1": "院子左下菜地 · 在第二块地种下草莓并浇水",
	"garden_bench_restored": "院子下方 · 院边长椅，带材料按 E 修复",
	"village_sign_restored": "院子右上 · 路牌，带材料按 E 扶正",
	"heard_forest_edge_notice": "公告板 · 再读森林边缘留言，按 E",
	"visited_forest_edge": "院子右侧 · 森林小路入口，按 E 前往",
	"heard_npc_forest_edge": "森林边缘 · 找美香交谈，按 E",
	"read_village_notice_day1": "院子东侧小路 · 去村口看公告，路上的小线索可以自己慢慢找",
}
const FIRST_WEEK_COMPLETED_LABEL: String = "第一周主线已完成"
const FIRST_WEEK_COMPLETED_HINT: String = "今日主线已经顺起来了，可以按自己的步子慢慢走"

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
		"watered_first_crop_day1": _get_flag(game_state, "watered_first_crop_day1"),
		"harvested_first_crop_day1": _get_flag(game_state, "harvested_first_crop_day1"),
		"shared_first_turnip_day1": _get_flag(game_state, "shared_first_turnip_day1"),
		"planted_aoi_strawberry_day1": _get_flag(game_state, "planted_aoi_strawberry_day1"),
		"garden_bench_restored": _is_restored(game_state, "garden_bench"),
		"village_sign_restored": _is_restored(game_state, "village_sign"),
		"heard_forest_edge_notice": _get_flag(game_state, "heard_forest_edge_notice"),
		"visited_forest_edge": _get_flag(game_state, "visited_forest_edge"),
		"heard_npc_forest_edge": _get_flag(game_state, "heard_npc_forest_edge"),
		"read_village_notice_day1": _get_flag(game_state, "read_village_notice_day1"),
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


func get_current_first_week_objective_id() -> String:
	var progress: Dictionary = get_first_week_progress()
	var raw_objectives: Variant = progress.get("objectives", {})
	var objectives: Dictionary = {}
	if raw_objectives is Dictionary:
		objectives = raw_objectives
	for objective_id in FIRST_WEEK_OBJECTIVES:
		if not bool(objectives.get(objective_id, false)):
			return objective_id
	return ""


func get_current_first_week_objective_label() -> String:
	var objective_id := get_current_first_week_objective_id()
	if objective_id.is_empty():
		return FIRST_WEEK_COMPLETED_LABEL
	return String(FIRST_WEEK_OBJECTIVE_LABELS.get(objective_id, objective_id))


func get_current_first_week_objective_hint() -> String:
	var objective_id := get_current_first_week_objective_id()
	if objective_id.is_empty():
		return FIRST_WEEK_COMPLETED_HINT
	return String(FIRST_WEEK_OBJECTIVE_HINTS.get(objective_id, "靠近目标后按 E 互动"))


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
