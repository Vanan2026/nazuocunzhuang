class_name QuestJournalUI
extends CanvasLayer
const DailyIntentContext := preload("res://game/systems/daily/DailyIntentContext.gd")
const WeeklyRhythmContext := preload("res://game/systems/daily/WeeklyRhythmContext.gd")

const QUEST_ID: String = "first_week_restore_path"
const COMPLETED_TEXT: String = "第一周主线已完成"
const OBJECTIVE_LABELS: Dictionary = {
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
const OBJECTIVE_DESCRIPTIONS: Dictionary = {
	"read_mailbox_day1": "先看看邮箱里的村务纸条。",
	"read_bulletin_day1": "去院子外的公告板确认今天的村里留言。",
	"old_well_restored": "用木柴和石块把旧井修稳。",
	"watered_first_crop_day1": "旧水井修好后，用刚得到的种子照料第一块地。",
	"harvested_first_crop_day1": "反复浇水、回屋休息，成熟后收获第一棵作物。",
	"shared_first_turnip_day1": "把第一次收成带给葵，让种植自然接到关系玩法。",
	"planted_aoi_strawberry_day1": "把葵回赠的草莓种子种到第二块地里，再浇一次水。",
	"garden_bench_restored": "把院边长椅修好，让路过的人能坐一会儿。",
	"village_sign_restored": "扶正村口路牌，找回森林边缘的方向。",
	"heard_forest_edge_notice": "再看公告板，确认森林边缘的小路线索。",
	"visited_forest_edge": "从路牌后的小路走到森林边缘。",
	"heard_npc_forest_edge": "在森林边缘听 Mika 说完她的传闻。",
	"read_village_notice_day1": "顺路去村口公告前停一下。公告只给今天的方向，村里的小线索留给你自己发现。",
}
const DAILY_INTENT_LABELS: Dictionary = {
	"tend_crops": "照看菜地",
	"check_village_notice": "去村口看看",
	"visit_neighbor": "找邻居说话",
	"gather_repair_material": "整理修复材料",
}
const DAILY_INTENT_SUMMARIES: Dictionary = {
	"tend_crops": "今天先照看菜地。浇水、收获或整理土地都算数，不用急着跑远。",
	"check_village_notice": "今天先去村口看看。公告、种子摊和旧枫树旁，可以慢慢找。",
	"visit_neighbor": "今天先找邻居说说话。路过的人也许会把村里的近况讲给你听。",
	"gather_repair_material": "今天先整理修复材料。木柴和石块会让旧东西一点点恢复原样。",
}
const OBJECTIVE_ORDER: Array[String] = [
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

@export var quest_manager_path: NodePath
@export var game_state_path: NodePath
@export var time_manager_path: NodePath
@export var weather_manager_path: NodePath

@onready var title_label: Label = get_node_or_null("Panel/Content/TitleLabel")
@onready var quest_title_label: Label = get_node_or_null("Panel/Content/QuestTitleLabel")
@onready var progress_label: Label = get_node_or_null("Panel/Content/ProgressLabel")
@onready var weekly_rhythm_label: Label = get_node_or_null("Panel/Content/WeeklyRhythmLabel")
@onready var daily_intent_label: Label = get_node_or_null("Panel/Content/DailyIntentLabel")
@onready var current_goal_label: Label = get_node_or_null("Panel/Content/CurrentGoalLabel")
@onready var objective_list: VBoxContainer = get_node_or_null("Panel/Content/ObjectiveList")

var quest_manager: Node = null
var game_state: Node = null
var time_manager: Node = null
var weather_manager: Node = null


func _ready() -> void:
	visible = false
	if not quest_manager_path.is_empty():
		quest_manager = get_node_or_null(quest_manager_path)
	if not game_state_path.is_empty():
		game_state = get_node_or_null(game_state_path)
	if not time_manager_path.is_empty():
		time_manager = get_node_or_null(time_manager_path)
	if not weather_manager_path.is_empty():
		weather_manager = get_node_or_null(weather_manager_path)
	bind_quest_manager(quest_manager)
	bind_game_state(game_state)
	bind_time_manager(time_manager)
	bind_weather_manager(weather_manager)
	refresh()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_journal"):
		toggle_journal()
		get_viewport().set_input_as_handled()


func bind_quest_manager(next_quest_manager: Node) -> void:
	if quest_manager != null and quest_manager.has_signal("quest_updated"):
		if quest_manager.quest_updated.is_connected(_on_quest_updated):
			quest_manager.quest_updated.disconnect(_on_quest_updated)
	quest_manager = next_quest_manager
	if quest_manager != null and quest_manager.has_signal("quest_updated"):
		if not quest_manager.quest_updated.is_connected(_on_quest_updated):
			quest_manager.quest_updated.connect(_on_quest_updated)
	refresh()


func bind_game_state(next_game_state: Node) -> void:
	if game_state != null and game_state.has_signal("flag_changed"):
		if game_state.flag_changed.is_connected(_on_game_state_flag_changed):
			game_state.flag_changed.disconnect(_on_game_state_flag_changed)
	game_state = next_game_state
	if game_state != null and game_state.has_signal("flag_changed"):
		if not game_state.flag_changed.is_connected(_on_game_state_flag_changed):
			game_state.flag_changed.connect(_on_game_state_flag_changed)
	refresh()


func bind_time_manager(next_time_manager: Node) -> void:
	if time_manager != null and time_manager.has_signal("date_changed"):
		if time_manager.date_changed.is_connected(_on_time_context_changed):
			time_manager.date_changed.disconnect(_on_time_context_changed)
	if time_manager != null and time_manager.has_signal("day_started"):
		if time_manager.day_started.is_connected(_on_time_context_changed):
			time_manager.day_started.disconnect(_on_time_context_changed)
	time_manager = next_time_manager
	if time_manager != null and time_manager.has_signal("date_changed"):
		if not time_manager.date_changed.is_connected(_on_time_context_changed):
			time_manager.date_changed.connect(_on_time_context_changed)
	if time_manager != null and time_manager.has_signal("day_started"):
		if not time_manager.day_started.is_connected(_on_time_context_changed):
			time_manager.day_started.connect(_on_time_context_changed)
	refresh()


func bind_weather_manager(next_weather_manager: Node) -> void:
	if weather_manager != null and weather_manager.has_signal("weather_changed"):
		if weather_manager.weather_changed.is_connected(_on_weather_context_changed):
			weather_manager.weather_changed.disconnect(_on_weather_context_changed)
	weather_manager = next_weather_manager
	if weather_manager != null and weather_manager.has_signal("weather_changed"):
		if not weather_manager.weather_changed.is_connected(_on_weather_context_changed):
			weather_manager.weather_changed.connect(_on_weather_context_changed)
	refresh()


func toggle_journal() -> void:
	if visible:
		hide_journal()
	else:
		show_journal()


func show_journal() -> void:
	_hide_daily_intent_panel()
	visible = true
	refresh()


func hide_journal() -> void:
	visible = false


func refresh() -> void:
	_ensure_nodes()
	if title_label != null:
		title_label.text = "村庄手账"
	if quest_title_label != null:
		quest_title_label.text = "第一周：修复回家的路"
	if progress_label != null:
		progress_label.text = _build_progress_text()
	if weekly_rhythm_label != null:
		var weekly_text := get_weekly_rhythm_text()
		weekly_rhythm_label.visible = not weekly_text.is_empty()
		weekly_rhythm_label.text = weekly_text
	if daily_intent_label != null:
		var intent_text := get_daily_intent_summary_text()
		daily_intent_label.visible = not intent_text.is_empty()
		daily_intent_label.text = intent_text
	if current_goal_label != null:
		current_goal_label.text = "当前目标：%s" % get_current_goal_text()
	_populate_objective_list()


func get_current_goal_text() -> String:
	var objectives := _get_objectives()
	for objective_id in OBJECTIVE_ORDER:
		if not bool(objectives.get(objective_id, false)):
			return String(OBJECTIVE_LABELS.get(objective_id, objective_id))
	return COMPLETED_TEXT


func get_visible_objective_texts() -> Array[String]:
	_ensure_nodes()
	var texts: Array[String] = []
	if objective_list == null:
		return texts
	for child in objective_list.get_children():
		if child is Label:
			texts.append((child as Label).text)
	return texts


func get_daily_intent_summary_text() -> String:
	var intent_id := _get_selected_daily_intent_id()
	if intent_id.is_empty():
		return ""
	var label := String(DAILY_INTENT_LABELS.get(intent_id, intent_id))
	var summary := String(DAILY_INTENT_SUMMARIES.get(intent_id, "今天先按这个方向慢慢来。"))
	var contextual_summary: String = DailyIntentContext.build_journal_summary(intent_id, summary, time_manager, weather_manager)
	return "今日方向：%s - %s" % [label, contextual_summary]


func get_weekly_rhythm_text() -> String:
	return WeeklyRhythmContext.build_journal_note("", time_manager)


func is_objective_complete(objective_id: String) -> bool:
	return bool(_get_objectives().get(objective_id, false))


func _populate_objective_list() -> void:
	if objective_list == null:
		return
	for child in objective_list.get_children():
		objective_list.remove_child(child)
		child.queue_free()
	var objectives := _get_objectives()
	var current_goal := get_current_goal_text()
	for objective_id in OBJECTIVE_ORDER:
		var is_complete := bool(objectives.get(objective_id, false))
		var row := Label.new()
		var label_text := String(OBJECTIVE_LABELS.get(objective_id, objective_id))
		var detail_text := String(OBJECTIVE_DESCRIPTIONS.get(objective_id, ""))
		var marker := _completion_marker(is_complete)
		if not is_complete and label_text == current_goal:
			marker = ">"
		row.text = "%s %s - %s" % [marker, label_text, detail_text]
		row.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		objective_list.add_child(row)


func _on_quest_updated(quest_id: String, _state: Dictionary) -> void:
	if quest_id == QUEST_ID:
		refresh()


func _on_game_state_flag_changed(flag_id: String, _value: Variant) -> void:
	if flag_id.begins_with("daily_intent_"):
		refresh()


func _on_time_context_changed(_date_info: Dictionary) -> void:
	refresh()


func _on_weather_context_changed(_weather_id: String) -> void:
	refresh()


func _hide_daily_intent_panel() -> void:
	if get_tree() == null or get_tree().root == null:
		return
	var panel := get_tree().root.find_child("DailyIntentPanel", true, false)
	if panel != null and panel.has_method("hide_planner"):
		panel.hide_planner()


func _get_progress() -> Dictionary:
	if quest_manager != null and quest_manager.has_method("get_first_week_progress"):
		return quest_manager.get_first_week_progress()
	return {
		"objectives": {},
		"completed_count": 0,
		"completed": false,
	}


func _get_objectives() -> Dictionary:
	var progress: Dictionary = _get_progress()
	var objectives: Variant = progress.get("objectives", {})
	if objectives is Dictionary:
		return objectives
	return {}


func _build_progress_text() -> String:
	var progress: Dictionary = _get_progress()
	var completed_count := int(progress.get("completed_count", 0))
	return "进度 %d / %d" % [completed_count, OBJECTIVE_ORDER.size()]


func _get_selected_daily_intent_id() -> String:
	if game_state == null or not game_state.has_method("get_daily_intent"):
		return ""
	return String(game_state.get_daily_intent(_get_current_day_key()))


func _get_current_day_key() -> String:
	if time_manager != null and time_manager.has_method("get_date_info"):
		var date_info: Dictionary = time_manager.get_date_info()
		return "day_%d" % int(date_info.get("total_day", 1))
	return "day_1"


func _completion_marker(is_complete: bool) -> String:
	if is_complete:
		return "[x]"
	return "[ ]"


func _ensure_nodes() -> void:
	if title_label == null:
		title_label = get_node_or_null("Panel/Content/TitleLabel")
	if quest_title_label == null:
		quest_title_label = get_node_or_null("Panel/Content/QuestTitleLabel")
	if progress_label == null:
		progress_label = get_node_or_null("Panel/Content/ProgressLabel")
	if weekly_rhythm_label == null:
		weekly_rhythm_label = get_node_or_null("Panel/Content/WeeklyRhythmLabel")
	if daily_intent_label == null:
		daily_intent_label = get_node_or_null("Panel/Content/DailyIntentLabel")
	if current_goal_label == null:
		current_goal_label = get_node_or_null("Panel/Content/CurrentGoalLabel")
	if objective_list == null:
		objective_list = get_node_or_null("Panel/Content/ObjectiveList")
