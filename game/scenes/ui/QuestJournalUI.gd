class_name QuestJournalUI
extends CanvasLayer

const QUEST_ID: String = "first_week_restore_path"
const COMPLETED_TEXT: String = "第一周主线已完成"
const OBJECTIVE_LABELS: Dictionary = {
	"read_mailbox_day1": "读邮箱",
	"read_bulletin_day1": "看公告板",
	"old_well_restored": "修旧井",
	"garden_bench_restored": "修长椅",
	"village_sign_restored": "扶正路牌",
	"heard_forest_edge_notice": "读森林边缘公告",
	"visited_forest_edge": "去森林边缘",
	"heard_npc_forest_edge": "听 Mika 的传闻",
}
const OBJECTIVE_DESCRIPTIONS: Dictionary = {
	"read_mailbox_day1": "先看看邮箱里的村务纸条。",
	"read_bulletin_day1": "去院子外的公告板确认今天的村里留言。",
	"old_well_restored": "用木柴和石块把旧井修稳。",
	"garden_bench_restored": "把院边长椅修好，让路过的人能坐一会儿。",
	"village_sign_restored": "扶正村口路牌，找回森林边缘的方向。",
	"heard_forest_edge_notice": "再看公告板，确认森林边缘的小路线索。",
	"visited_forest_edge": "从路牌后的小路走到森林边缘。",
	"heard_npc_forest_edge": "在森林边缘听 Mika 说完她的传闻。",
}
const OBJECTIVE_ORDER: Array[String] = [
	"read_mailbox_day1",
	"read_bulletin_day1",
	"old_well_restored",
	"garden_bench_restored",
	"village_sign_restored",
	"heard_forest_edge_notice",
	"visited_forest_edge",
	"heard_npc_forest_edge",
]

@export var quest_manager_path: NodePath

@onready var title_label: Label = get_node_or_null("Panel/Content/TitleLabel")
@onready var quest_title_label: Label = get_node_or_null("Panel/Content/QuestTitleLabel")
@onready var progress_label: Label = get_node_or_null("Panel/Content/ProgressLabel")
@onready var current_goal_label: Label = get_node_or_null("Panel/Content/CurrentGoalLabel")
@onready var objective_list: VBoxContainer = get_node_or_null("Panel/Content/ObjectiveList")

var quest_manager: Node = null


func _ready() -> void:
	visible = false
	if not quest_manager_path.is_empty():
		quest_manager = get_node_or_null(quest_manager_path)
	bind_quest_manager(quest_manager)
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


func toggle_journal() -> void:
	if visible:
		hide_journal()
	else:
		show_journal()


func show_journal() -> void:
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
	if current_goal_label == null:
		current_goal_label = get_node_or_null("Panel/Content/CurrentGoalLabel")
	if objective_list == null:
		objective_list = get_node_or_null("Panel/Content/ObjectiveList")
