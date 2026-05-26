class_name RestorationTarget
extends "res://game/entities/interactable/Interactable.gd"

signal restoration_completed(restoration_id: String)

@export var restoration_id: String = ""
@export var data_registry_path: NodePath
@export var game_state_path: NodePath
@export var inventory_manager_path: NodePath
@export var event_bus_path: NodePath
@export var save_manager_path: NodePath
@export var dialogue_box_path: NodePath
@export var restoration_sprite_path: NodePath

var restoration_data: Dictionary = {}
var local_restored: Dictionary = {}
var pending_reward_feedback: Array[String] = []


func _ready() -> void:
	super._ready()
	if restoration_id.is_empty():
		restoration_id = interactable_id
		if restoration_id.is_empty():
			restoration_id = "old_well"
	if interaction_hint.is_empty():
		interaction_hint = "修复并查看"
	_load_data()
	if restoration_data.is_empty():
		call_deferred("_reload_from_data_registry")
	else:
		_apply_visual_state(_is_restored_target())


func _reload_from_data_registry() -> void:
	_load_data()
	if not restoration_data.is_empty():
		_apply_visual_state(_is_restored_target())


func on_interact(_interactor: Node) -> void:
	super.on_interact(_interactor)
	if restoration_data.is_empty():
		_show_feedback("修复目标数据未加载，暂时无法修复。")
		return
	if _is_restored_target():
		_show_feedback("%s 已经修复完成。" % _display_name())
		return

	var missing_resources: Array[String] = _get_missing_requirements()
	if not missing_resources.is_empty():
		_show_feedback("修复前置条件未满足。\n" + "\n".join(missing_resources))
		return

	if not _consume_requirements():
		_show_feedback("修复消耗失败，请稍后重试。")
		return

	pending_reward_feedback = _grant_completion_rewards()
	_set_restored_state(true)
	_apply_visual_state(true)
	emit_restoration_completed()
	_show_feedback("%s 已修复完成！村庄恢复了一点呼吸。" % _display_name())


func get_interaction_hint() -> String:
	if restoration_id.is_empty():
		return interaction_hint
	if _is_restored_target():
		return "查看%s" % _display_name()
	if _get_missing_requirements().is_empty():
		return "修复%s" % _display_name()
	return "先准备材料再修复"


func emit_restoration_completed() -> void:
	restoration_completed.emit(restoration_id)
	var event_bus := _get_event_bus()
	if event_bus != null and event_bus.has_signal("restoration_completed"):
		event_bus.restoration_completed.emit(restoration_id)


func _load_data() -> void:
	var data_registry := _get_data_registry()
	if data_registry == null or not data_registry.has_method("get_restoration"):
		return
	restoration_data = data_registry.get_restoration(restoration_id)


func _is_restored_target() -> bool:
	var game_state := _get_game_state()
	if game_state != null and game_state.has_method("is_restored"):
		return game_state.is_restored(restoration_id)
	return bool(local_restored.get(restoration_id, false))


func _set_restored_state(next_value: bool) -> void:
	var game_state := _get_game_state()
	if game_state != null and game_state.has_method("set_restored"):
		game_state.set_restored(restoration_id, next_value)
	else:
		local_restored[restoration_id] = next_value

	var game_state_flags: Array = restoration_data.get("unlocks", [])
	for unlock_id in game_state_flags:
		if game_state != null and game_state.has_method("set_flag"):
			game_state.set_flag(String(unlock_id), true)
	var save_manager := _get_save_manager()
	if save_manager != null and game_state != null and save_manager.has_method("set_restoration_states"):
		var states: Dictionary = {}
		if game_state.has_method("get_restoration_states"):
			states = game_state.get_restoration_states()
		states[restoration_id] = true
		save_manager.set_restoration_states(game_state, {"restoration_states": states})


func _consume_requirements() -> bool:
	if restoration_data.is_empty():
		return false
	if not _has_required_money():
		return false
	var inventory_manager := _get_inventory_manager()
	if inventory_manager == null or not inventory_manager.has_method("has_item"):
		return false

	var required_items_variant: Variant = restoration_data.get("required_items", [])
	var required_items: Array = required_items_variant if required_items_variant is Array else []
	for requirement in required_items:
		if not (requirement is Dictionary):
			continue
		var item_id := String(requirement.get("item_id", ""))
		var count := int(requirement.get("count", 0))
		if count <= 0:
			continue
		if not inventory_manager.has_item(item_id, count):
			return false

	for requirement in required_items:
		if not (requirement is Dictionary):
			continue
		var item_id := String(requirement.get("item_id", ""))
		var count := int(requirement.get("count", 0))
		if count <= 0:
			continue
		if not inventory_manager.remove_item(item_id, count):
			return false

	var game_state := _get_game_state()
	var required_money := int(restoration_data.get("required_money", 0))
	if required_money > 0 and game_state != null and game_state.has_method("set_player_money"):
		game_state.set_player_money(game_state.get_player_money() - required_money)
	return true


func _grant_completion_rewards() -> Array[String]:
	var granted: Array[String] = []
	var reward_items_variant: Variant = restoration_data.get("reward_items", [])
	var reward_items: Array = reward_items_variant if reward_items_variant is Array else []
	if reward_items.is_empty():
		return granted
	var inventory_manager := _get_inventory_manager()
	if inventory_manager == null or not inventory_manager.has_method("add_item"):
		return granted
	for reward_item in reward_items:
		if not (reward_item is Dictionary):
			continue
		var item_id := String(reward_item.get("item_id", ""))
		var count := int(reward_item.get("count", 0))
		if item_id.is_empty() or count <= 0:
			continue
		inventory_manager.add_item(item_id, count)
		granted.append(_format_item_stack(item_id, count))
	return granted


func _format_item_stack(item_id: String, count: int) -> String:
	var display_id := item_id
	var data_registry := _get_data_registry()
	if data_registry != null and data_registry.has_method("get_item"):
		var item_data: Dictionary = data_registry.get_item(item_id)
		var item_name := String(item_data.get("name", ""))
		if not item_name.is_empty():
			display_id = item_name
	return "%s x%d" % [display_id, count]


func _get_missing_requirements() -> Array[String]:
	var missing: Array[String] = []
	if restoration_data.is_empty():
		return ["修复目标配置缺失"]

	var required_flags_variant: Variant = restoration_data.get("required_flags", [])
	var required_flags: Array = required_flags_variant if required_flags_variant is Array else []
	if not required_flags.is_empty():
		for required_flag in required_flags:
			var game_state := _get_game_state()
			if game_state == null:
				continue
			var is_flag_set: bool = false
			if game_state.has_method("get_flag"):
				is_flag_set = game_state.get_flag(String(required_flag), false)
			if not is_flag_set:
				missing.append("缺少前置条件：%s" % String(required_flag))

	var required_items_variant: Variant = restoration_data.get("required_items", [])
	var required_items: Array = required_items_variant if required_items_variant is Array else []
	if not required_items.is_empty():
		var inventory_manager := _get_inventory_manager()
		for required_item in required_items:
			if required_item is Dictionary:
				var item_id := String(required_item.get("item_id", ""))
				var count := int(required_item.get("count", 0))
				if item_id.is_empty() or count <= 0:
					continue
				if inventory_manager == null:
					missing.append("需要 %s × %d（库存不足）" % [item_id, count])
				elif not inventory_manager.has_method("has_item"):
					missing.append("库存系统不可用")
				elif not inventory_manager.has_item(item_id, count):
					var have: int = int(inventory_manager.get_count(item_id)) if inventory_manager.has_method("get_count") else 0
					missing.append("缺少 %s × %d（当前: %d）" % [item_id, count, have])

	var required_money := int(restoration_data.get("required_money", 0))
	var game_state := _get_game_state()
	if required_money > 0:
		var current_money: int = int(game_state.get_player_money()) if game_state != null and game_state.has_method("get_player_money") else 0
		if current_money < required_money:
			missing.append("银币不足（需要 %d，当前 %d）" % [required_money, current_money])

	return missing


func _has_required_money() -> bool:
	var required_money := int(restoration_data.get("required_money", 0))
	if required_money <= 0:
		return true
	var game_state := _get_game_state()
	if game_state == null or not game_state.has_method("get_player_money"):
		return false
	return game_state.get_player_money() >= required_money


func _apply_visual_state(is_repaired: bool) -> void:
	var sprite := _get_restoration_sprite()
	if sprite == null:
		return
	var visual_states: Dictionary = restoration_data.get("visual_states", {})
	var state_key := "repaired" if is_repaired else "broken"
	var texture_path := String(visual_states.get(state_key, ""))
	var has_texture := false
	if not texture_path.is_empty() and ResourceLoader.exists(texture_path):
		has_texture = true
	if sprite is Node:
		if has_texture and sprite.has_method("set"):
			sprite.set("texture_path", texture_path)
			if sprite.has_method("refresh_texture"):
				sprite.refresh_texture()
		var repaired_modulate: Color = Color(1.0, 1.0, 1.0, 1.0) if is_repaired else Color(0.9, 0.9, 0.9, 1.0)
		sprite.modulate = repaired_modulate


func _show_feedback(message: String) -> void:
	if not pending_reward_feedback.is_empty():
		message += "\n获得：" + "、".join(pending_reward_feedback)
		pending_reward_feedback.clear()
	var dialogue_box := _get_dialogue_box()
	if dialogue_box == null or not dialogue_box.has_method("show_dialogue"):
		push_warning(message)
		return
	var dialogue := {
		"dialogue_id": "%s_restore_runtime" % restoration_id,
		"npc_id": "system",
		"type": "event",
		"priority": 90,
		"conditions": {},
		"lines": [{"speaker": "system", "text": message}],
		"sets_flags": [],
	}
	dialogue_box.show_dialogue(dialogue, {"npc_name": "系统", "portrait": ""})


func _display_name() -> String:
	var name_text := String(restoration_data.get("name", ""))
	if not name_text.is_empty():
		return name_text
	if not interactable_id.is_empty():
		return interactable_id
	return restoration_id


func _get_restoration_sprite() -> Node:
	var sprite_node := _get_linked_node(restoration_sprite_path, "OldWellArt")
	if sprite_node == null:
		return null
	return sprite_node


func _get_data_registry() -> Node:
	return _get_linked_node(data_registry_path, "DataRegistry")


func _get_game_state() -> Node:
	return _get_linked_node(game_state_path, "GameState")


func _get_inventory_manager() -> Node:
	return _get_linked_node(inventory_manager_path, "InventoryManager")


func _get_event_bus() -> Node:
	return _get_linked_node(event_bus_path, "EventBus")


func _get_save_manager() -> Node:
	return _get_linked_node(save_manager_path, "SaveManager")


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
	return null
