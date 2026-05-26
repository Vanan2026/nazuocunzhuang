class_name CurrentObjectiveChip
extends CanvasLayer
const GreenfieldUITheme := preload("res://game/scenes/ui/GreenfieldUITheme.gd")
const DailyIntentContext := preload("res://game/systems/daily/DailyIntentContext.gd")
const WeeklyRhythmContext := preload("res://game/systems/daily/WeeklyRhythmContext.gd")

const QUEST_ID: String = "first_week_restore_path"
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
const FALLBACK_LABELS: Dictionary = {
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
const FALLBACK_HINTS: Dictionary = {
	"read_mailbox_day1": "屋内 · 出门到院子邮箱旁，按 E 查看",
	"read_bulletin_day1": "院子 · 邮箱右侧公告板，靠近后按 E",
	"old_well_restored": "院子右侧 · 旧水井，备好木石后按 E 修复",
	"watered_first_crop_day1": "院子左下菜地 · 整理土地、播种后按 E 浇水",
	"harvested_first_crop_day1": "院子左下菜地 · 回屋睡觉后继续浇水，成熟后按 E 收获",
	"shared_first_turnip_day1": "院子里 · 在背包选择春萝卜，再和葵交谈",
	"planted_aoi_strawberry_day1": "院子左下菜地 · 第二块地，选择草莓种子后播种浇水",
	"garden_bench_restored": "院子下方 · 院边长椅，带材料按 E 修复",
	"village_sign_restored": "院子右上 · 路牌，带材料按 E 扶正",
	"heard_forest_edge_notice": "公告板 · 再读森林边缘留言，按 E",
	"visited_forest_edge": "院子右侧 · 森林小路入口，按 E 前往",
	"heard_npc_forest_edge": "森林边缘 · 找美香交谈，按 E",
	"read_village_notice_day1": "院子东侧小路 · 去村口看公告，路上的小线索可以自己慢慢找",
}
const COMPLETED_TEXT: String = "第一周主线已完成"
const COMPLETED_HINT: String = "今日主线已经顺起来了，可以按自己的步子慢慢走"
const DAILY_INTENT_LABELS: Dictionary = {
	"tend_crops": "照看菜地",
	"check_village_notice": "去村口看看",
	"visit_neighbor": "找邻居说说",
	"gather_repair_material": "整理修复材料",
}
const DAILY_INTENT_HINTS: Dictionary = {
	"tend_crops": "院子菜地 · 整理、浇水或收获，今天不用赶远路",
	"check_village_notice": "村口 · 公告、种子摊和旧枫树旁都可以慢慢看",
	"visit_neighbor": "院边或村口 · 找一位路过的人，先问候就好",
	"gather_repair_material": "附近小路 · 收起木柴、石块，看看能修补什么",
}
const DAILY_LOOP_NO_INTENT_TEXT: String = "整理今日方向"
const DAILY_LOOP_NO_INTENT_HINT: String = "屋内 · 晨间小桌，先选一个今天想走的方向"
const DAILY_LOOP_PROGRESS_TEXT: String = "日常"

@export var quest_manager_path: NodePath
@export var game_state_path: NodePath
@export var time_manager_path: NodePath
@export var weather_manager_path: NodePath

@onready var panel: PanelContainer = get_node_or_null("Panel")
@onready var content: VBoxContainer = get_node_or_null("Panel/Content")
@onready var title_label: Label = get_node_or_null("Panel/Content/TitleLabel")
@onready var objective_label: Label = get_node_or_null("Panel/Content/ObjectiveLabel")
@onready var hint_label: Label = get_node_or_null("Panel/Content/HintLabel")
@onready var progress_label: Label = get_node_or_null("Panel/Content/ProgressLabel")

var quest_manager: Node = null
var game_state: Node = null
var time_manager: Node = null
var weather_manager: Node = null


func _ready() -> void:
	visible = true
	if not quest_manager_path.is_empty():
		quest_manager = get_node_or_null(quest_manager_path)
	if not game_state_path.is_empty():
		game_state = get_node_or_null(game_state_path)
	if not time_manager_path.is_empty():
		time_manager = get_node_or_null(time_manager_path)
	if not weather_manager_path.is_empty():
		weather_manager = get_node_or_null(weather_manager_path)
	_apply_visual_theme()
	bind_quest_manager(quest_manager)
	bind_game_state(game_state)
	bind_time_manager(time_manager)
	bind_weather_manager(weather_manager)
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
	if time_manager != null:
		if time_manager.has_signal("date_changed") and time_manager.date_changed.is_connected(_on_time_context_changed):
			time_manager.date_changed.disconnect(_on_time_context_changed)
		if time_manager.has_signal("day_started") and time_manager.day_started.is_connected(_on_time_context_changed):
			time_manager.day_started.disconnect(_on_time_context_changed)
	time_manager = next_time_manager
	if time_manager != null:
		if time_manager.has_signal("date_changed") and not time_manager.date_changed.is_connected(_on_time_context_changed):
			time_manager.date_changed.connect(_on_time_context_changed)
		if time_manager.has_signal("day_started") and not time_manager.day_started.is_connected(_on_time_context_changed):
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


func refresh() -> void:
	_ensure_nodes()
	if title_label != null:
		if _should_show_daily_loop():
			title_label.text = "今日方向"
		else:
			title_label.text = "当前目标"
	if objective_label != null:
		objective_label.text = get_current_goal_text()
	if hint_label != null:
		hint_label.text = get_current_hint_text()
	if progress_label != null:
		progress_label.text = get_progress_text()


func get_current_goal_text() -> String:
	if _should_show_daily_loop():
		var intent_id := _get_selected_daily_intent_id()
		if intent_id.is_empty():
			return DAILY_LOOP_NO_INTENT_TEXT
		return "今日方向：%s" % String(DAILY_INTENT_LABELS.get(intent_id, intent_id))
	if quest_manager != null and quest_manager.has_method("get_current_first_week_objective_label"):
		return String(quest_manager.get_current_first_week_objective_label())
	var objective_id := _get_current_objective_id_fallback()
	if objective_id.is_empty():
		return COMPLETED_TEXT
	return String(FALLBACK_LABELS.get(objective_id, objective_id))


func get_current_hint_text() -> String:
	if _should_show_daily_loop():
		var intent_id := _get_selected_daily_intent_id()
		if intent_id.is_empty():
			return WeeklyRhythmContext.build_chip_hint(DAILY_LOOP_NO_INTENT_HINT, time_manager)
		var base_hint: String = String(DAILY_INTENT_HINTS.get(intent_id, "???????????????"))
		var contextual_hint := DailyIntentContext.build_chip_hint(intent_id, base_hint, time_manager, weather_manager)
		return WeeklyRhythmContext.build_chip_hint(contextual_hint, time_manager)
	if quest_manager != null and quest_manager.has_method("get_current_first_week_objective_hint"):
		return String(quest_manager.get_current_first_week_objective_hint())
	var objective_id := _get_current_objective_id_fallback()
	if objective_id.is_empty():
		return COMPLETED_HINT
	return String(FALLBACK_HINTS.get(objective_id, "靠近目标后按 E 互动"))


func get_progress_text() -> String:
	if _should_show_daily_loop():
		return DAILY_LOOP_PROGRESS_TEXT
	var progress: Dictionary = _get_progress()
	var completed_count := int(progress.get("completed_count", 0))
	return "%d / %d" % [completed_count, OBJECTIVE_ORDER.size()]


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


func _should_show_daily_loop() -> bool:
	var progress: Dictionary = _get_progress()
	return bool(progress.get("completed", false))


func _get_selected_daily_intent_id() -> String:
	if game_state == null or not game_state.has_method("get_daily_intent"):
		return ""
	return String(game_state.get_daily_intent(_get_current_day_key()))


func _get_current_day_key() -> String:
	if time_manager != null and time_manager.has_method("get_date_info"):
		var date_info: Dictionary = time_manager.get_date_info()
		return "day_%d" % int(date_info.get("total_day", 1))
	return "day_1"


func _get_current_objective_id_fallback() -> String:
	var objectives := _get_objectives()
	for objective_id in OBJECTIVE_ORDER:
		if not bool(objectives.get(objective_id, false)):
			return objective_id
	return ""


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
	var raw_objectives: Variant = progress.get("objectives", {})
	if raw_objectives is Dictionary:
		return raw_objectives
	return {}


func _ensure_nodes() -> void:
	if panel == null:
		panel = get_node_or_null("Panel")
	if content == null:
		content = get_node_or_null("Panel/Content")
	if title_label == null:
		title_label = get_node_or_null("Panel/Content/TitleLabel")
	if objective_label == null:
		objective_label = get_node_or_null("Panel/Content/ObjectiveLabel")
	if hint_label == null:
		hint_label = get_node_or_null("Panel/Content/HintLabel")
	if progress_label == null:
		progress_label = get_node_or_null("Panel/Content/ProgressLabel")


func _apply_visual_theme() -> void:
	_ensure_nodes()
	GreenfieldUITheme.apply_hud_panel(panel)
	GreenfieldUITheme.apply_title_label(title_label, 14)
	GreenfieldUITheme.apply_body_label(objective_label, 15)
	GreenfieldUITheme.apply_hint_label(hint_label, 13)
	GreenfieldUITheme.apply_hint_label(progress_label, 13)
	if content != null:
		content.add_theme_constant_override("separation", 2)
