class_name DailyIntentPanel
extends CanvasLayer
const GreenfieldUITheme := preload("res://game/scenes/ui/GreenfieldUITheme.gd")
const DailyIntentContext := preload("res://game/systems/daily/DailyIntentContext.gd")
const WeeklyRhythmContext := preload("res://game/systems/daily/WeeklyRhythmContext.gd")

signal intent_selected(day_key: String, intent_id: String)

const INTENT_OPTIONS: Array[Dictionary] = [
	{
		"id": "tend_crops",
		"label": "照看菜地",
		"description": "先整理、浇水或收获院子里的作物。",
		"feedback": "今天先照看菜地。土和水都慢慢来，不急着跑远。",
	},
	{
		"id": "check_village_notice",
		"label": "去村口看看",
		"description": "去村口公告和种子摊旁慢慢找今天的线索。",
		"feedback": "今天先去村口看看。公告、种子摊和旧枫树旁，也许都有一点线索。",
	},
	{
		"id": "visit_neighbor",
		"label": "找邻居说话",
		"description": "和一位路过的人聊聊，不急着完成别的事。",
		"feedback": "今天先找邻居说说话。有人在院边或村口停下时，可以慢慢听。",
	},
	{
		"id": "gather_repair_material",
		"label": "整理修复材料",
		"description": "收起附近的木柴、石块，看看能修补什么。",
		"feedback": "今天先整理修复材料。木柴和石块会让旧东西一点点恢复原样。",
	},
]

@export var game_state_path: NodePath
@export var time_manager_path: NodePath
@export var weather_manager_path: NodePath
@export var dialogue_box_path: NodePath

@onready var panel: PanelContainer = get_node_or_null("Panel")
@onready var content: VBoxContainer = get_node_or_null("Panel/Content")
@onready var title_label: Label = get_node_or_null("Panel/Content/TitleLabel")
@onready var status_label: Label = get_node_or_null("Panel/Content/StatusLabel")
@onready var choice_buttons: VBoxContainer = get_node_or_null("Panel/Content/ChoiceButtons")
@onready var close_button: Button = get_node_or_null("Panel/Content/CloseButton")

var last_selected_intent_id: String = ""


func _ready() -> void:
	visible = false
	_build_choice_buttons()
	_apply_visual_theme()
	if close_button != null and not close_button.pressed.is_connected(hide_planner):
		close_button.pressed.connect(hide_planner)
	_refresh_status()


func show_planner() -> void:
	_build_choice_buttons()
	_apply_visual_theme()
	_refresh_status()
	visible = true


func hide_planner() -> void:
	visible = false


func select_intent(intent_id: String) -> bool:
	if not get_available_intent_ids().has(intent_id):
		return false
	var day_key := get_current_day_key()
	var game_state := _get_game_state()
	if game_state != null and game_state.has_method("set_daily_intent"):
		game_state.set_daily_intent(day_key, intent_id)
	last_selected_intent_id = intent_id
	_refresh_status()
	intent_selected.emit(day_key, intent_id)
	hide_planner()
	_show_intent_feedback(intent_id)
	return true


func get_available_intent_ids() -> Array[String]:
	var ids: Array[String] = []
	for option in INTENT_OPTIONS:
		ids.append(String(option.get("id", "")))
	return ids


func get_selected_intent_id() -> String:
	var game_state := _get_game_state()
	if game_state != null and game_state.has_method("get_daily_intent"):
		return String(game_state.get_daily_intent(get_current_day_key()))
	return last_selected_intent_id


func get_current_day_key() -> String:
	var time_manager := _get_time_manager()
	if time_manager != null and time_manager.has_method("get_date_info"):
		var date_info: Dictionary = time_manager.get_date_info()
		return "day_%d" % int(date_info.get("total_day", 1))
	return "day_1"


func get_intent_feedback_text(intent_id: String) -> String:
	for option in INTENT_OPTIONS:
		if String(option.get("id", "")) == intent_id:
			var base_text: String = String(option.get("feedback", option.get("description", "")))
			return DailyIntentContext.build_planner_feedback(intent_id, base_text, _get_time_manager(), _get_weather_manager())
	return ""


func get_weekly_rhythm_status_text() -> String:
	return WeeklyRhythmContext.build_planner_status("", _get_time_manager())


func _build_choice_buttons() -> void:
	if choice_buttons == null:
		choice_buttons = get_node_or_null("Panel/Content/ChoiceButtons")
	if choice_buttons == null:
		return
	for child in choice_buttons.get_children():
		choice_buttons.remove_child(child)
		child.queue_free()
	for option in INTENT_OPTIONS:
		choice_buttons.add_child(_create_choice_button(option))


func _create_choice_button(option: Dictionary) -> Button:
	var button := Button.new()
	var intent_id := String(option.get("id", ""))
	button.name = "IntentButton%s" % intent_id.to_pascal_case()
	button.text = String(option.get("label", intent_id))
	button.tooltip_text = String(option.get("description", ""))
	button.focus_mode = Control.FOCUS_ALL
	button.custom_minimum_size = Vector2(320.0, 44.0)
	GreenfieldUITheme.apply_button(button, 14, 44.0)
	button.pressed.connect(select_intent.bind(intent_id))
	return button


func _refresh_status() -> void:
	if title_label != null:
		title_label.text = "今天想先做什么"
	var selected_id := get_selected_intent_id()
	if selected_id.is_empty():
		if status_label != null:
			status_label.text = WeeklyRhythmContext.build_planner_status("这是提醒，不是任务。选一个方向，今天慢慢来。", _get_time_manager())
		return
	if status_label != null:
		status_label.text = WeeklyRhythmContext.build_planner_status("今天先：" + _label_for_intent(selected_id), _get_time_manager())


func _label_for_intent(intent_id: String) -> String:
	for option in INTENT_OPTIONS:
		if String(option.get("id", "")) == intent_id:
			return String(option.get("label", intent_id))
	return intent_id


func _show_intent_feedback(intent_id: String) -> void:
	var feedback_text := get_intent_feedback_text(intent_id)
	if feedback_text.is_empty():
		return
	var dialogue_box := _get_dialogue_box()
	if dialogue_box == null or not dialogue_box.has_method("show_dialogue"):
		return
	var dialogue := {
		"dialogue_id": "daily_intent_%s_feedback" % intent_id,
		"npc_id": "daily_intent",
		"lines": [
			{
				"speaker": "daily_intent",
				"text": feedback_text,
			},
		],
	}
	dialogue_box.show_dialogue(dialogue, {"npc_name": "晨间小桌", "portrait": ""})


func _apply_visual_theme() -> void:
	GreenfieldUITheme.apply_surface_panel(panel)
	GreenfieldUITheme.apply_title_label(title_label, 17)
	GreenfieldUITheme.apply_body_label(status_label, 13)
	GreenfieldUITheme.apply_hint_label(status_label, 13)
	GreenfieldUITheme.apply_button(close_button, 14, 42.0)
	if content != null:
		content.add_theme_constant_override("separation", 10)
	if choice_buttons != null:
		choice_buttons.add_theme_constant_override("separation", 8)


func _get_game_state() -> Node:
	return _get_linked_node(game_state_path, "GameState")


func _get_time_manager() -> Node:
	return _get_linked_node(time_manager_path, "TimeManager")


func _get_weather_manager() -> Node:
	return _get_linked_node(weather_manager_path, "WeatherManager")


func _get_dialogue_box() -> Node:
	return _get_linked_node(dialogue_box_path, "DialogueBox")


func _get_linked_node(path: NodePath, node_name: String) -> Node:
	var linked := get_node_or_null(path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var candidate := parent_node.get_node_or_null(node_name)
		if candidate != null:
			return candidate
		parent_node = parent_node.get_parent()
	if get_tree() != null and get_tree().root != null:
		return _find_node_named(get_tree().root, node_name)
	return null


func _find_node_named(node: Node, node_name: String) -> Node:
	if node.name == node_name:
		return node
	for child in node.get_children():
		var found := _find_node_named(child, node_name)
		if found != null:
			return found
	return null
