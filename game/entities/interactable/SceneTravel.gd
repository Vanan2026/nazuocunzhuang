class_name SceneTravel
extends "res://game/entities/interactable/Interactable.gd"

@export var target_scene: String = ""
@export var target_scene_id: String = ""
@export var target_spawn_id: String = "default"
@export var arrival_flag_id: String = ""
@export var game_state_path: NodePath


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	if not arrival_flag_id.is_empty():
		var game_state := _get_game_state()
		if game_state != null and game_state.has_method("set_flag"):
			game_state.set_flag(arrival_flag_id, true)
	var resolved_scene_id := _resolve_target_scene_id()
	var resolved_spawn_id := _resolve_target_spawn_id(resolved_scene_id)
	if not resolved_scene_id.is_empty():
		var route_host := _get_route_host()
		var scene_router := _get_scene_router()
		if scene_router != null and scene_router.has_method("request_scene_change"):
			scene_router.request_scene_change(resolved_scene_id, resolved_spawn_id)
			if route_host != null and route_host.has_method("get_current_gameplay_scene_id") and String(route_host.get_current_gameplay_scene_id()) != resolved_scene_id:
				route_host.change_scene(resolved_scene_id, resolved_spawn_id)
			return
		if route_host != null and route_host.has_method("change_scene"):
			route_host.change_scene(resolved_scene_id, resolved_spawn_id)
			return
	if target_scene.is_empty():
		push_warning("SceneTravel target_scene is empty.")
		return
	get_tree().call_deferred("change_scene_to_file", target_scene)


func _resolve_target_scene_id() -> String:
	if not target_scene_id.is_empty():
		return target_scene_id
	match target_scene:
		"res://game/scenes/home/PlayerHouse.tscn":
			return "player_house"
		"res://game/scenes/world/PlayerYard.tscn":
			return "player_yard"
		"res://game/scenes/world/ForestEdge.tscn":
			return "forest_edge"
		_:
			return ""


func _resolve_target_spawn_id(resolved_scene_id: String) -> String:
	if not target_spawn_id.is_empty() and target_spawn_id != "default":
		return target_spawn_id
	match resolved_scene_id:
		"player_house":
			return "inside_default"
		"player_yard":
			if arrival_flag_id == "returned_from_forest_edge":
				return "from_forest_edge"
			return "from_house"
		"forest_edge":
			return "from_yard"
		_:
			return "default"


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
	if get_tree() != null and get_tree().root != null:
		return get_tree().root.get_node_or_null("GameState")
	return null


func _get_scene_router() -> Node:
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null("SceneRouter")
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	if get_tree() != null and get_tree().root != null:
		return _find_node_named(get_tree().root, "SceneRouter")
	return null


func _get_route_host() -> Node:
	var parent_node := get_parent()
	while parent_node != null:
		if parent_node.has_method("change_scene") and parent_node.has_method("get_current_gameplay_scene_id"):
			return parent_node
		parent_node = parent_node.get_parent()
	if get_tree() != null and get_tree().root != null:
		return _find_route_host(get_tree().root)
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


func _find_route_host(node: Node) -> Node:
	if node == null:
		return null
	if node.has_method("change_scene") and node.has_method("get_current_gameplay_scene_id"):
		return node
	for child in node.get_children():
		var found := _find_route_host(child)
		if found != null:
			return found
	return null
