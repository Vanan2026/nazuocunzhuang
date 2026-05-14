extends Node
class_name RegionLoader

signal region_loading_started(region_id: String)
signal region_loading_completed(region_id: String)
signal region_loading_failed(region_id: String, error: String)
signal all_regions_unloaded()

const LOAD_BATCH_SIZE: int = 2

var regions: Dictionary = {}
var loaded_regions: Dictionary = {}
var active_regions: Array[String] = []
var region_scenes: Dictionary = {}

var current_region_id: String = ""
var player_ref: Node2D = null

var load_queue: Array[String] = []
var is_processing_queue: bool = false

func _ready() -> void:
	print("[RegionLoader] 初始化完成")

func _process(delta: float) -> void:
	if player_ref == null:
		return
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
		"preload_distance": def.get("preload_distance", 800.0),
		"unload_distance": def.get("unload_distance", 1500.0)
	}

func register_region_scene(region_id: String, scene_path: String) -> void:
	if regions.has(region_id):
		regions[region_id]["scene_path"] = scene_path
	else:
		regions[region_id] = {
			"scene_path": scene_path,
			"world_offset": Vector2.ZERO,
			"region_size": Vector2(4096, 4096),
			"adjacent_regions": [],
			"is_always_loaded": false,
			"display_name": region_id
		}
	region_scenes[region_id] = scene_path

func set_player(player: Node2D) -> void:
	player_ref = player
	if player != null:
		print("[RegionLoader] 玩家已绑定")

func load_region(region_id: String) -> bool:
	if loaded_regions.has(region_id):
		return true
	
	if not regions.has(region_id):
		push_warning("[RegionLoader] 区域未注册: " + region_id)
		return false
	
	var def = regions[region_id]
	var scene_path = def.get("scene_path", "")
	if scene_path.is_empty():
		push_warning("[RegionLoader] 区域没有场景路径: " + region_id)
		return false
	
	emit_signal("region_loading_started", region_id)
	print("[RegionLoader] 开始加载区域: ", region_id)
	
	var scene: PackedScene = load(scene_path)
	if scene == null:
		push_error("[RegionLoader] 无法加载场景文件: " + scene_path)
		emit_signal("region_loading_failed", region_id, "无法加载场景文件")
		return false
	
	_on_region_loaded(region_id, scene)
	return true

func _on_region_loaded(region_id: String, scene: PackedScene) -> void:
	if scene == null:
		emit_signal("region_loading_failed", region_id, "资源为空")
		return
	
	var instance: Node = scene.instantiate()
	if instance == null:
		emit_signal("region_loading_failed", region_id, "无法实例化场景")
		return
	
	instance.name = region_id
	loaded_regions[region_id] = instance
	
	var world_offset: Vector2 = Vector2.ZERO
	var region_size: Vector2 = Vector2(4096, 4096)
	var is_always_loaded: bool = false
	var region_display_name: String = region_id
	
	if regions.has(region_id):
		var def = regions[region_id]
		world_offset = def.get("world_offset", Vector2.ZERO)
		region_size = def.get("region_size", Vector2(4096, 4096))
		is_always_loaded = def.get("is_always_loaded", false)
		region_display_name = def.get("display_name", region_id)
	
	instance.position = world_offset
	
	instance.set("world_offset", world_offset)
	instance.set("region_size", region_size)
	instance.set("region_id", region_id)
	instance.set("region_display_name", region_display_name)
	
	add_child(instance)
	
	if is_always_loaded:
		if instance.has_method("load_region"):
			instance.load_region()
		if instance.has_method("activate"):
			instance.activate()
		active_regions.append(region_id)
	
	emit_signal("region_loading_completed", region_id)
	print("[RegionLoader] 区域加载完成: ", region_id)

func unload_region(region_id: String) -> bool:
	if not loaded_regions.has(region_id):
		return false
	
	var instance = loaded_regions[region_id]
	if instance.has_method("unload_region"):
		instance.unload_region()
	
	active_regions.erase(region_id)
	loaded_regions.erase(region_id)
	instance.queue_free()
	
	print("[RegionLoader] 区域已卸载: ", region_id)
	return true

func get_region(region_id: String) -> Node:
	return loaded_regions.get(region_id)

func get_current_region_id() -> String:
	return current_region_id

func set_current_region(region_id: String) -> void:
	if current_region_id != region_id:
		print("[RegionLoader] 当前区域: ", region_id)
	current_region_id = region_id

func _update_region_states(player_pos: Vector2) -> void:
	var to_load: Array[String] = []
	var new_active: Array[String] = []
	
	for region_id in regions.keys():
		if not loaded_regions.has(region_id):
			var def = regions[region_id]
			var offset: Vector2 = def.get("world_offset", Vector2.ZERO)
			var size: Vector2 = def.get("region_size", Vector2(4096, 4096))
			var bounds := Rect2(offset, size)
			var preload_dist: float = def.get("preload_distance", 800.0)
			var expanded_bounds := bounds.grow(preload_dist)
			
			if expanded_bounds.has_point(player_pos):
				to_load.append(region_id)
	
	for region_id in to_load:
		if not load_queue.has(region_id):
			load_queue.append(region_id)
	
	for region_id in regions.keys():
		var region = loaded_regions.get(region_id)
		if region != null and region.has_method("should_activate"):
			if region.should_activate(player_pos):
				new_active.append(region_id)
	
	for region_id in new_active:
		if not active_regions.has(region_id):
			var region = loaded_regions.get(region_id)
			if region != null and region.has_method("activate"):
				region.activate()
				print("[RegionLoader] 激活区域: ", region_id)
	
	for region_id in active_regions:
		if not new_active.has(region_id):
			var region = loaded_regions.get(region_id)
			if region != null and region.has_method("deactivate"):
				region.deactivate()
				print("[RegionLoader] 停用区域: ", region_id)
	
	active_regions = new_active

func _process_load_queue() -> void:
	if is_processing_queue:
		return
	if load_queue.is_empty():
		return
	
	is_processing_queue = true
	var count = 0
	
	while not load_queue.is_empty() and count < LOAD_BATCH_SIZE:
		var region_id = load_queue.pop_front() as String
		if region_id != null and not loaded_regions.has(region_id):
			load_region(region_id)
		count += 1
	
	is_processing_queue = false

func get_loaded_region_ids() -> Array[String]:
	return loaded_regions.keys()

func get_active_region_ids() -> Array[String]:
	return active_regions.duplicate()

func is_region_loaded(region_id: String) -> bool:
	return loaded_regions.has(region_id)

func is_region_active(region_id: String) -> bool:
	return active_regions.has(region_id)
