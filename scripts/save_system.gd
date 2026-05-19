extends Node

const SAVE_VERSION: String = "1"


func create_save_data(world: Node, spawn_id: String = "") -> Dictionary:
	var current_region_id := _get_world_region_id(world)
	var current_spawn_id := spawn_id
	if current_spawn_id.is_empty():
		current_spawn_id = str(world.get("current_spawn_id")) if world != null else ""

	var inventory := _collect_inventory(world)
	return {
		"version": SAVE_VERSION,
		"player": {
			"region_id": current_region_id,
			"spawn_id": current_spawn_id,
		},
		"time": _collect_time_state(),
		"inventory": inventory,
		"regions": _collect_region_states(world),
	}


func apply_save_data(data: Dictionary, world: Node) -> void:
	_apply_time_state(data.get("time", {}) as Dictionary)

	var player_state := data.get("player", {}) as Dictionary
	var region_id := str(player_state.get("region_id", ""))
	var spawn_id := str(player_state.get("spawn_id", ""))
	if world != null and world.has_method("spawn_player_at") and not region_id.is_empty():
		await world.spawn_player_at(region_id, spawn_id)

	await get_tree().process_frame
	_apply_region_states(data.get("regions", {}) as Dictionary, world)


func _get_world_region_id(world: Node) -> String:
	if world == null:
		return ""
	if world.has_method("get_region_loader"):
		var loader: Variant = world.call("get_region_loader")
		if loader != null and loader.has_method("get_current_region_id"):
			return str(loader.call("get_current_region_id"))
	return str(world.get("current_region_id"))


func _collect_time_state() -> Dictionary:
	var time_system := get_node_or_null("/root/TimeSystem")
	if time_system == null:
		return {}
	return {
		"day": int(time_system.get("current_day")),
		"season": str(time_system.get("current_season")),
		"year": int(time_system.get("current_year")),
	}


func _apply_time_state(time_state: Dictionary) -> void:
	var time_system := get_node_or_null("/root/TimeSystem")
	if time_system == null:
		return
	if time_state.has("day"):
		time_system.set("current_day", int(time_state.get("day")))
	if time_state.has("season"):
		time_system.set("current_season", str(time_state.get("season")))
	if time_state.has("year"):
		time_system.set("current_year", int(time_state.get("year")))


func _collect_region_states(world: Node) -> Dictionary:
	var result: Dictionary = {}
	var loader := _get_region_loader(world)
	if loader == null:
		return result
	var loaded: Dictionary = loader.get("loaded_regions")
	for region_id in loaded.keys():
		var region := loaded[region_id] as Node
		if region == null:
			continue
		result[str(region_id)] = {"nodes": _collect_node_states(region)}
	return result


func _collect_node_states(region: Node) -> Dictionary:
	var nodes: Dictionary = {}
	var farm_system := region.get_node_or_null("FarmSystem")
	if farm_system != null and farm_system.has_method("save_state"):
		nodes["FarmSystem"] = farm_system.call("save_state")
	return nodes


func _apply_region_states(regions: Dictionary, world: Node) -> void:
	var loader := _get_region_loader(world)
	if loader == null:
		return
	for region_id in regions.keys():
		if not loader.call("is_region_loaded", str(region_id)):
			loader.call("load_region", str(region_id))
		var region := loader.call("get_region", str(region_id)) as Node
		if region == null:
			continue
		var region_state := regions[region_id] as Dictionary
		var nodes := region_state.get("nodes", {}) as Dictionary
		var farm_state := nodes.get("FarmSystem", {}) as Dictionary
		var farm_system := region.get_node_or_null("FarmSystem")
		if farm_system != null and farm_system.has_method("load_state"):
			farm_system.call("load_state", farm_state)


func _collect_inventory(world: Node) -> Dictionary:
	var inventory: Dictionary = {}
	var loader := _get_region_loader(world)
	if loader == null:
		return inventory
	var loaded: Dictionary = loader.get("loaded_regions")
	for region in loaded.values():
		if region is Node:
			var farm_system := (region as Node).get_node_or_null("FarmSystem")
			if farm_system != null and farm_system.has_method("get_inventory"):
				_merge_counts(inventory, farm_system.call("get_inventory") as Dictionary)
	return inventory


func _merge_counts(target: Dictionary, source: Dictionary) -> void:
	for key in source.keys():
		target[str(key)] = int(target.get(str(key), 0)) + int(source[key])


func _get_region_loader(world: Node) -> Node:
	if world == null or not world.has_method("get_region_loader"):
		return null
	return world.call("get_region_loader") as Node
