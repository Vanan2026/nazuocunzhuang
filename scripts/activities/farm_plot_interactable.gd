extends "res://scripts/world/yard_interactable.gd"

@export var plot_index: int = 0
@export var default_crop: String = ""
@export var farm_system_path: NodePath = NodePath("../../../FarmSystem")

var _farm_system: Node = null


func _ready() -> void:
	super._ready()
	_resolve_farm_system()
	_sync_prompt()


func on_interact(_interactor: Node) -> void:
	if not _resolve_farm_system():
		_show_feedback("菜地", "还没有连接种植系统。")
		return

	var info: Dictionary = _farm_system.call("get_plot_info", plot_index)
	match int(info.get("state", 0)):
		0:
			_plant_default_crop()
		1, 2:
			_water_crop(info)
		3:
			_harvest_crop(info)
		_:
			_show_feedback("菜地", "这块地的状态暂时无法识别。")

	_sync_prompt()


func get_interaction_hint() -> String:
	if not _resolve_farm_system():
		return "按 E 检查菜地"

	var info: Dictionary = _farm_system.call("get_plot_info", plot_index)
	match int(info.get("state", 0)):
		0:
			return "按 E 播种"
		1, 2:
			if bool(info.get("is_watered", false)):
				return "今天已经浇过水"
			return "按 E 浇水"
		3:
			return "按 E 收获"
	return "按 E 检查菜地"


func _plant_default_crop() -> void:
	var crop := _get_default_crop()
	if crop.is_empty():
		_show_feedback("菜地", "当前季节没有可种的作物。")
		return

	if _farm_system.call("plant", plot_index, crop):
		_show_feedback("播种", "在第 %d 块菜地种下了%s。" % [plot_index + 1, crop])
	else:
		_show_feedback("菜地", "这块地现在不能播种。")


func _water_crop(info: Dictionary) -> void:
	if bool(info.get("is_watered", false)):
		_show_feedback("菜地", "今天已经浇过水了，明天再来看看。")
		return

	if _farm_system.call("water", plot_index):
		_show_feedback("浇水", "第 %d 块菜地已经浇水。" % [plot_index + 1])
	else:
		_show_feedback("菜地", "这块地现在不能浇水。")


func _harvest_crop(info: Dictionary) -> void:
	var crop := str(info.get("crop_type", "作物"))
	if _farm_system.call("harvest", plot_index):
		_show_feedback("收获", "收获了%s。" % crop)
	else:
		_show_feedback("菜地", "作物还没有成熟。")


func _get_default_crop() -> String:
	if not default_crop.is_empty():
		return default_crop

	var crops: Array = _farm_system.call("get_available_crops")
	if crops.is_empty():
		return ""
	return str(crops[0])


func _resolve_farm_system() -> bool:
	if is_instance_valid(_farm_system):
		return true

	_farm_system = get_node_or_null(farm_system_path)
	if _farm_system == null:
		var tree := get_tree()
		if tree != null:
			_farm_system = tree.get_first_node_in_group("farm_system")

	return _farm_system != null


func _sync_prompt() -> void:
	interaction_hint = get_interaction_hint()
	var hint := get_node_or_null("HintLabel")
	if hint is Label:
		hint.text = interaction_hint


func _show_feedback(title: String, text: String) -> void:
	print("[BackFarmPlot:%d] %s" % [plot_index, text])
	if has_node("/root/UIManager"):
		get_node("/root/UIManager").show_dialogue(title, text)
