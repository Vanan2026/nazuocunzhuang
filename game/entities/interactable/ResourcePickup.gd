class_name ResourcePickup
extends "res://game/entities/interactable/Interactable.gd"

@export var item_id: String = ""
@export var count: int = 1
@export var inventory_manager_path: NodePath
@export var game_state_path: NodePath
@export var consume_on_pickup: bool = true
@export var pickup_id: String = ""
@export var claim_flag_id: String = ""

var picked: bool = false


func _ready() -> void:
	super._ready()
	_connect_game_state()
	refresh_claim_state()


func on_interact(interactor: Node) -> void:
	refresh_claim_state()
	if consume_on_pickup and picked:
		return
	super.on_interact(interactor)
	var inventory_manager := _get_inventory_manager()
	if inventory_manager == null or not inventory_manager.has_method("add_item"):
		push_warning("ResourcePickup missing InventoryManager for %s" % item_id)
		return
	if item_id.is_empty() or count <= 0:
		push_warning("ResourcePickup has invalid item config.")
		return
	inventory_manager.add_item(item_id, count)
	picked = true
	_set_claimed(true)
	if consume_on_pickup:
		_set_claimed_visual_state(true)


func get_interaction_hint() -> String:
	refresh_claim_state()
	if consume_on_pickup and picked:
		return ""
	return interaction_hint


func refresh_claim_state() -> void:
	if not consume_on_pickup:
		return
	picked = _is_claimed()
	_set_claimed_visual_state(picked)


func _get_inventory_manager() -> Node:
	var linked := get_node_or_null(inventory_manager_path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null("InventoryManager")
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	return null


func _get_game_state() -> Node:
	var linked := get_node_or_null(game_state_path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null("GameState")
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	return null


func _get_shared_game_state() -> Node:
	var parent_node := get_parent()
	while parent_node != null:
		if parent_node.has_method("get_current_gameplay_scene_id"):
			return parent_node.get_node_or_null("GameState")
		parent_node = parent_node.get_parent()
	return null


func _connect_game_state() -> void:
	var game_state := _get_game_state()
	if game_state == null or not game_state.has_signal("flag_changed"):
		return
	if not game_state.flag_changed.is_connected(_on_game_state_flag_changed):
		game_state.flag_changed.connect(_on_game_state_flag_changed)


func _on_game_state_flag_changed(flag_id: String, _value: Variant) -> void:
	if flag_id == _get_claim_flag_id():
		refresh_claim_state()


func _get_claim_flag_id() -> String:
	if not claim_flag_id.is_empty():
		return claim_flag_id
	var resolved_pickup_id := pickup_id
	if resolved_pickup_id.is_empty():
		resolved_pickup_id = interactable_id
	if resolved_pickup_id.is_empty():
		resolved_pickup_id = String(name)
	return "resource_pickup_claimed_%s" % resolved_pickup_id


func _is_claimed() -> bool:
	var flag_id := _get_claim_flag_id()
	var game_state := _get_game_state()
	if game_state != null and game_state.has_method("get_flag") and bool(game_state.get_flag(flag_id, false)):
		return true
	var shared_game_state := _get_shared_game_state()
	if shared_game_state != null and shared_game_state != game_state and shared_game_state.has_method("get_flag"):
		return bool(shared_game_state.get_flag(flag_id, false))
	return picked


func _set_claimed(value: bool) -> void:
	var flag_id := _get_claim_flag_id()
	var game_state := _get_game_state()
	if game_state != null and game_state.has_method("set_flag"):
		game_state.set_flag(flag_id, value)
	var shared_game_state := _get_shared_game_state()
	if shared_game_state != null and shared_game_state != game_state and shared_game_state.has_method("set_flag"):
		shared_game_state.set_flag(flag_id, value)


func _set_claimed_visual_state(claimed: bool) -> void:
	if not consume_on_pickup:
		return
	visible = not claimed
	set_deferred("monitoring", not claimed)
	set_deferred("monitorable", not claimed)
	_set_collision_shapes_disabled(claimed)


func _set_collision_shapes_disabled(disabled: bool) -> void:
	for child in get_children():
		if child is CollisionShape2D:
			child.set_deferred("disabled", disabled)
