class_name SeedStallAdvice
extends "res://game/entities/interactable/Interactable.gd"

const PLAYER_VERB_TAG: String = "ask_seed_stall_advice"
const TODAY_REASON_TAG: String = "today_crop_care_tip"
const RETURN_REASON_TAG: String = "return_to_yard_water_or_plant"

@export var visit_flag_id: String = "visited_village_seed_stall_day1"
@export var advice_flag_template: String = "asked_seed_stall_advice_%s_day%d"
@export var game_state_path: NodePath
@export var time_manager_path: NodePath
@export var dialogue_box_path: NodePath


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	var game_state := _get_game_state()
	var advice_flag_id := get_today_advice_flag_id()
	if game_state != null and game_state.has_method("set_flag"):
		if not visit_flag_id.is_empty():
			game_state.set_flag(visit_flag_id, true)
		game_state.set_flag(advice_flag_id, true)
	var dialogue_box := _get_dialogue_box()
	if dialogue_box != null and dialogue_box.has_method("show_dialogue"):
		dialogue_box.show_dialogue(_build_advice_dialogue(), {"npc_name": "种子摊", "portrait": ""})


func get_today_advice_flag_id() -> String:
	var date_info := _get_date_info()
	var season := String(date_info.get("season", "spring"))
	var day_of_season := int(date_info.get("day_of_season", date_info.get("day", 1)))
	return advice_flag_template % [season, day_of_season]


func _build_advice_dialogue() -> Dictionary:
	var date_info := _get_date_info()
	var season := String(date_info.get("season", "spring"))
	var day_of_season := int(date_info.get("day_of_season", date_info.get("day", 1)))
	return {
		"dialogue_id": "seed_stall_daily_advice_%s_day%d" % [season, day_of_season],
		"npc_id": "seed_stall",
		"lines": [
			{
				"speaker": "seed_stall",
				"text": _build_advice_line(season),
			},
		],
	}


func _build_advice_line(season: String) -> String:
	match season:
		"summer":
			return "今天日头会高一些，院子里的夏季苗先少量试种，回去前记得浇水。"
		"autumn":
			return "今天适合整理院子里的空地，秋季苗不要排太满，回去前记得浇水。"
		"winter":
			return "今天先照看院子里耐冷的小苗，土面干了再轻轻浇水。"
		_:
			return "今天先看院子里的小地，春萝卜和草莓都适合慢慢试种，回去前记得浇水。"


func _get_date_info() -> Dictionary:
	var time_manager := _get_time_manager()
	if time_manager != null and time_manager.has_method("get_date_info"):
		return time_manager.get_date_info()
	return {
		"season": "spring",
		"day_of_season": 1,
	}


func _get_game_state() -> Node:
	return _get_linked_node(game_state_path, "GameState")


func _get_time_manager() -> Node:
	return _get_linked_node(time_manager_path, "TimeManager")


func _get_dialogue_box() -> Node:
	return _get_linked_node(dialogue_box_path, "DialogueBox")


func _get_linked_node(path: NodePath, fallback_name: String) -> Node:
	var linked := get_node_or_null(path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null(fallback_name)
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	if get_tree() != null and get_tree().root != null:
		return _find_node_named(get_tree().root, fallback_name)
	return null


func _find_node_named(node: Node, node_name: String) -> Node:
	if node == null:
		return null
	if node.name == node_name:
		return node
	for child in node.get_children():
		var found := _find_node_named(child, node_name)
		if found != null:
			return found
	return null
