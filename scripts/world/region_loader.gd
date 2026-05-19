extends Node
class_name RegionLoader

signal current_region_changed(from_region: String, to_region: String)

var world: Node = null
var _loading: bool = false
var _load_queue: Array = []
var regions: Dictionary = {}
var loaded_regions: Dictionary = {}
var current_region_id: String = ""
var load_distance: float = 2048.0

func _ready() -> void:
	if world == null:
		world = get_parent()
	add_to_group("region_loader")
	print("[RegionLoader] 初始化完成")

func _process(_delta: float) -> void:
	if world and world.has_node("Player"):
		var player_ref = world.get_node("Player")
		_update_region_states(player_ref.global_position)
		_process_load_queue()

func initialize(region_definitions: Array[Dictionary]) -> void:
	for def in region_definitions:
		register_region_definition(def)
	print("[RegionLoader] 已注册 ", regions.size(), " 个区域定义")

func register_region_definition(def: Dictionary) -> void:
	var id: String = def.get("region_id", "")
	if id.is_empty():
		return

	regions[id] = {
		"scene_path": def.get("scene_path", ""),
		"world_offset": def.get("world_offset", Vector2.ZERO),
		"region_size": def.get("region_size", Vector2(4096, 4096)),
		"adjacent_regions": def.get("adjacent_regions", []),
		"is_always_loaded": def.get("is_always_loaded", false),
		"display_name": def.get("display_name", id),
		"spawn_points": def.get("spawn_points", {})
	}

func load_region(region_id: String) -> void:
	if region_id.is_empty() or loaded_regions.has(region_id):
		return
	if world == null:
		world = get_parent()
	if world == null:
		push_error("[RegionLoader] Missing world owner for region: " + region_id)
		return

	var region_def = regions.get(region_id, {})
	var scene_path = region_def.get("scene_path", "")
	if scene_path.is_empty():
		return

	var world_offset = region_def.get("world_offset", Vector2.ZERO)

	var packed_scene = load(scene_path)
	if packed_scene == null:
		return

	var instance = packed_scene.instantiate()
	instance.set("world_offset", world_offset)
	instance.set("region_size", region_def.get("region_size", Vector2(4096, 4096)))
	instance.set("region_id", region_id)
	instance.set("region_display_name", region_def.get("display_name", region_id))

	instance.position = world_offset
	instance.name = region_id

	if not world.has_node(region_id):
		world.add_child(instance)
		loaded_regions[region_id] = instance
		_on_region_loaded(region_id, instance)

func _on_region_loaded(region_id: String, instance: Node2D) -> void:
	if not is_instance_valid(instance):
		return
	if instance.has_method("load_region"):
		instance.load_region()
	print("[RegionLoader] 区域已加载: ", region_id)

func unload_region(region_id: String) -> void:
	if not loaded_regions.has(region_id):
		return

	var region = loaded_regions[region_id]
	var region_def = regions.get(region_id, {})
	var is_always_loaded = region_def.get("is_always_loaded", false)

	if is_always_loaded and region_id == current_region_id:
		return

	region.queue_free()
	loaded_regions.erase(region_id)
	print("[RegionLoader] 区域已卸载: ", region_id)

func _update_region_states(player_pos: Vector2) -> void:
	var nearest_region_id = ""
	var nearest_dist = INF

	for region_id in regions.keys():
		if not loaded_regions.has(region_id):
			continue

		var region_def = regions[region_id]
		var offset = region_def.get("world_offset", Vector2.ZERO)
		var size = region_def.get("region_size", Vector2(4096, 4096))
		var rect = Rect2(offset, size)
		var dist = player_pos.distance_to(rect.get_center())

		if dist < nearest_dist:
			nearest_dist = dist
			nearest_region_id = region_id

	if nearest_region_id != current_region_id and not nearest_region_id.is_empty():
		var old_region = current_region_id
		current_region_id = nearest_region_id
		emit_signal("current_region_changed", old_region, current_region_id)
		_update_region_visibility(current_region_id, old_region)

func _update_region_visibility(new_region: String, old_region: String) -> void:
	for region_id in loaded_regions.keys():
		var region = loaded_regions[region_id]
		var is_current = (region_id == new_region)
		var is_adjacent = _is_adjacent_region(new_region, region_id)

		if is_current or is_adjacent:
			if region.has_method("activate"):
				region.activate()
			else:
				if region.has_method("set_visible"):
					region.set_visible(true)
				elif region.has_method("_set_visibility"):
					region._set_visibility(true)
		else:
			if region.has_method("deactivate"):
				region.deactivate()
			else:
				if region.has_method("set_visible"):
					region.set_visible(false)
				elif region.has_method("_set_visibility"):
					region._set_visibility(false)

func _is_adjacent_region(region_a: String, region_b: String) -> bool:
	var def_a = regions.get(region_a, {})
	var adjacent = def_a.get("adjacent_regions", [])
	return region_b in adjacent

func _process_load_queue() -> void:
	if _loading or _load_queue.is_empty():
		return

	_loading = true
	var region_id = _load_queue.pop_front()
	load_region(region_id)
	_loading = false

	if not _load_queue.is_empty():
		_loading = false

func get_region(region_id: String) -> Node:
	return loaded_regions.get(region_id, null)

func is_region_loaded(region_id: String) -> bool:
	return loaded_regions.has(region_id)

func set_current_region(region_id: String) -> void:
	current_region_id = region_id
	_update_region_visibility(region_id, "")

func get_current_region() -> String:
	return current_region_id

func get_current_region_id() -> String:
	return current_region_id

func get_spawn_position(region_id: String, spawn_id: String = "default") -> Vector2:
	var def = regions.get(region_id, {})
	var spawn_points = def.get("spawn_points", {})

	if spawn_points.has(spawn_id):
		return spawn_points[spawn_id]

	var world_offset = def.get("world_offset", Vector2.ZERO)
	var size = def.get("region_size", Vector2(4096, 4096))
	return world_offset + size / 2
