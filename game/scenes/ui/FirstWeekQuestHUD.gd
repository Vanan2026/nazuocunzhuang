class_name FirstWeekQuestHUD
extends CanvasLayer

const QUEST_ID: String = "first_week_restore_path"
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

@onready var title_label: Label = get_node_or_null("Panel/Content/TitleLabel")
@onready var progress_label: Label = get_node_or_null("Panel/Content/ProgressLabel")
@onready var objective_list: VBoxContainer = get_node_or_null("Panel/Content/ObjectiveList")

var quest_manager: Node = null


func _ready() -> void:
	if not quest_manager_path.is_empty():
		quest_manager = get_node_or_null(quest_manager_path)
	bind_quest_manager(quest_manager)
	refresh()


func bind_quest_manager(next_quest_manager: Node) -> void:
	if quest_manager != null and quest_manager.has_signal("quest_updated"):
		if quest_manager.quest_updated.is_connected(_on_quest_updated):
			quest_manager.quest_updated.disconnect(_on_quest_updated)
	quest_manager = next_quest_manager
	if quest_manager != null and quest_manager.has_signal("quest_updated"):
		if not quest_manager.quest_updated.is_connected(_on_quest_updated):
			quest_manager.quest_updated.connect(_on_quest_updated)
	refresh()


func refresh() -> void:
	_ensure_nodes()
	if title_label != null:
		title_label.text = "第一周主线"
	if progress_label != null:
		progress_label.text = _build_progress_text()
	if objective_list == null:
		return
	for child in objective_list.get_children():
		objective_list.remove_child(child)
		child.queue_free()
	var objectives := _get_objectives()
	for objective_id in OBJECTIVE_ORDER:
		var row := Label.new()
		row.text = "%s %s" % [
			_completion_marker(bool(objectives.get(objective_id, false))),
			String(OBJECTIVE_LABELS.get(objective_id, objective_id)),
		]
		row.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		objective_list.add_child(row)


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
	if progress_label == null:
		progress_label = get_node_or_null("Panel/Content/ProgressLabel")
	if objective_list == null:
		objective_list = get_node_or_null("Panel/Content/ObjectiveList")
