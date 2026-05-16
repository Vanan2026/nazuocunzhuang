extends Node2D
class_name WorldController

signal world_initialized
signal player_spawned(spawn_id: String)
signal region_changed(from_region: String, to_region: String)

const WORLD_SIZE: Vector2 = Vector2(12000, 10000)
const STARTING_REGION: String = "Region_HomeArea"

@export_group("World Settings")
@export var world_bounds: Rect2 = Rect2(Vector2.ZERO, WORLD_SIZE)
@export var enable_boundaries: bool = true
@export var camera_look_ahead_offset: Vector2 = Vector2(0, -280)

@export_group("Initial Regions")
@export var initial_regions: Array[String] = ["Region_HomeArea"]
@export var load_all_regions_at_start: bool = false

@export_group("References")
@export var player_scene_path: String = "res://scenes/regions/region_home_area.tscn"
@export var default_spawn_id: String = "home_area_default"

var region_loader: RegionLoader
var player: CharacterBody2D = null
var camera: Camera2D = null
var current_region_id: String = ""
var spawn_positions: Dictionary = {}

func _ready() -> void:
	_initialize_world()
	print("[WorldController] 世界已初始化，大小 ", WORLD_SIZE)

func _initialize_world() -> void:
	region_loader = RegionLoader.new()
	region_loader.name = "RegionLoader"
	add_child(region_loader)

	_register_all_regions()

	if load_all_regions_at_start:
		_load_all_regions()
	else:
		_load_initial_regions()

	_setup_player()
	_setup_camera()

	emit_signal("world_initialized")

func _register_all_regions() -> void:
	var region_definitions: Array[Dictionary] = [
		{
			"region_id": "Region_HomeArea",
			"display_name": "庭院",
			"scene_path": "res://scenes/regions/region_home_area.tscn",
			"world_offset": Vector2(4000, 6000),
			"region_size": Vector2(6144, 4096),
			"adjacent_regions": ["Region_Village", "Region_BackFarm"],
			"is_always_loaded": true,
			"spawn_points": {
				"home_area_default": Vector2(7300, 7900),
				"home_area_from_back_farm": Vector2(8200, 9370),
				"home_area_from_village": Vector2(4000, 6000)
			}
		},
		{
			"region_id": "Region_Village",
			"display_name": "云村中心区",
			"scene_path": "res://scenes/regions/region_village.tscn",
			"world_offset": Vector2(0, 4000),
			"region_size": Vector2(6000, 4000),
			"adjacent_regions": ["Region_HomeArea", "Region_MountainPath", "Region_ForestEdge"],
			"is_always_loaded": false,
			"spawn_points": {
				"village_from_home": Vector2(4000, 6000),
				"village_shrine": Vector2(3000, 4500)
			}
		},
		{
			"region_id": "Region_BackFarm",
			"display_name": "后院菜园",
			"scene_path": "res://scenes/regions/region_back_farm.tscn",
			"world_offset": Vector2(6000, 8000),
			"region_size": Vector2(2000, 2000),
			"adjacent_regions": ["Region_HomeArea"],
			"is_always_loaded": false,
			"spawn_points": {
				"back_farm_default": Vector2(7000, 8000),
				"back_farm_from_home": Vector2(7000, 8000)
			}
		},
		{
			"region_id": "Region_MountainPath",
			"display_name": "后山小道",
			"scene_path": "res://scenes/regions/region_mountain_path.tscn",
			"world_offset": Vector2(0, 2000),
			"region_size": Vector2(4000, 3000),
			"adjacent_regions": ["Region_Village", "Region_MountainHut", "Region_Mountain"],
			"is_always_loaded": false,
			"spawn_points": {
				"path_from_village": Vector2(2000, 3000)
			}
		},
		{
			"region_id": "Region_MountainHut",
			"display_name": "后山1户",
			"scene_path": "res://scenes/regions/region_mountain_hut.tscn",
			"world_offset": Vector2(4000, 0),
			"region_size": Vector2(1500, 1500),
			"adjacent_regions": ["Region_MountainPath"],
			"is_always_loaded": false,
			"spawn_points": {
				"hut_from_path": Vector2(4750, 750)
			}
		},
		{
			"region_id": "Region_Mountain",
			"display_name": "后山区域",
			"scene_path": "res://scenes/regions/region_mountain.tscn",
			"world_offset": Vector2(0, 0),
			"region_size": Vector2(4000, 3000),
			"adjacent_regions": ["Region_MountainPath", "Region_CliffView"],
			"is_always_loaded": false,
			"spawn_points": {
				"mountain_from_path": Vector2(2000, 1500)
			}
		},
		{
			"region_id": "Region_CliffView",
			"display_name": "悬崖空地",
			"scene_path": "res://scenes/regions/region_cliff_view.tscn",
			"world_offset": Vector2(2000, 0),
			"region_size": Vector2(1500, 1500),
			"adjacent_regions": ["Region_Mountain"],
			"is_always_loaded": false,
			"spawn_points": {
				"cliff_from_mountain": Vector2(2750, 750)
			}
		},
		{
			"region_id": "Region_ForestEdge",
			"display_name": "听雨林",
			"scene_path": "res://scenes/regions/region_forest_edge.tscn",
			"world_offset": Vector2(6000, 2000),
			"region_size": Vector2(3000, 2500),
			"adjacent_regions": ["Region_Village", "Region_Orchard"],
			"is_always_loaded": false,
			"spawn_points": {
				"forest_from_village": Vector2(6000, 3500)
			}
		},
		{
			"region_id": "Region_Orchard",
			"display_name": "果园",
			"scene_path": "res://scenes/regions/region_orchard.tscn",
			"world_offset": Vector2(8500, 3000),
			"region_size": Vector2(2500, 2000),
			"adjacent_regions": ["Region_ForestEdge", "Region_Pond"],
			"is_always_loaded": false,
			"spawn_points": {
				"orchard_from_forest": Vector2(8500, 4000)
			}
		},
		{
			"region_id": "Region_Pond",
			"display_name": "池塘空地",
			"scene_path": "res://scenes/regions/region_pond.tscn",
			"world_offset": Vector2(10000, 5000),
			"region_size": Vector2(2000, 2000),
			"adjacent_regions": ["Region_Orchard"],
			"is_always_loaded": false,
			"spawn_points": {
				"pond_from_orchard": Vector2(10000, 6000)
			}
		}
	]

	for def in region_definitions:
		region_loader.register_region_definition(def)
		if def.has("spawn_points"):
			spawn_positions[def["region_id"]] = def["spawn_points"]

	print("[WorldController] 已注册 ", region_definitions.size(), " 个区域")

func _load_initial_regions() -> void:
	for region_id in initial_regions:
		region_loader.load_region(region_id)
		if region_loader.is_region_loaded(region_id):
			var region = region_loader.get_region(region_id)
			if region != null:
				region.activate()
				current_region_id = region_id

	print("[WorldController] 已加载初始区域 ", initial_regions)

func _load_all_regions() -> void:
	for region_id in region_loader.regions.keys():
		region_loader.load_region(region_id)

func _setup_player() -> void:
	var region = region_loader.get_region(STARTING_REGION)
	if region == null:
		push_error("[WorldController] 初始区域未加载")
		return

	var spawn_pos = _get_spawn_position(STARTING_REGION, default_spawn_id)

	var existing_player = region.get_node_or_null("YSortWorld/Player")
	if existing_player != null:
		existing_player.global_position = spawn_pos
		existing_player.collision_layer = 1
		existing_player.collision_mask = 1
		player = existing_player
		print("[WorldController] 使用场景中的玩家，位置: ", spawn_pos)
	else:
		player = CharacterBody2D.new()
		player.name = "Player"
		player.global_position = spawn_pos
		add_child(player)

		var collision := CollisionShape2D.new()
		var shape := RectangleShape2D.new()
		shape.size = Vector2(40, 20)
		collision.shape = shape
		collision.position = Vector2(0, -10)
		player.add_child(collision)
		print("[WorldController] 创建新玩家，位置: ", spawn_pos)

	emit_signal("player_spawned", default_spawn_id)

func _setup_player_components() -> void:
	var collision := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(40, 20)
	collision.shape = shape
	collision.position = Vector2(0, -10)
	player.add_child(collision)

	if player.has_method("set_walkable_zone"):
		pass

func _setup_camera() -> void:
	camera = Camera2D.new()
	camera.name = "WorldCamera"
	camera.limit_left = int(world_bounds.position.x)
	camera.limit_top = int(world_bounds.position.y)
	camera.limit_right = int(world_bounds.end.x)
	camera.limit_bottom = int(world_bounds.end.y)
	camera.limit_smoothed = true
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 10.0

	if player != null:
		camera.global_position = player.global_position + camera_look_ahead_offset
	else:
		camera.global_position = _get_spawn_position(STARTING_REGION, default_spawn_id) + camera_look_ahead_offset

	add_child(camera)
	camera.make_current()

	var region = region_loader.get_region(STARTING_REGION)
	if region != null:
		var region_camera = region.get_node_or_null("CameraRig")
		if region_camera != null and region_camera is Camera2D:
			region_camera.enabled = false

	print("[WorldController] 相机已设置，边界: ", world_bounds)

func _process(delta: float) -> void:
	if player != null and camera != null:
		_update_camera()
		_check_region_transition()

func _update_camera() -> void:
	var target_pos := player.global_position + camera_look_ahead_offset
	camera.global_position = camera.global_position.lerp(target_pos, 1.0 - exp(-6.0 * get_process_delta_time()))

func _check_region_transition() -> void:
	if player == null:
		return

	var player_pos = player.global_position
	var new_region_id = _get_region_at_position(player_pos)

	if new_region_id != current_region_id and not new_region_id.is_empty():
		var old_region = current_region_id
		current_region_id = new_region_id
		region_loader.set_current_region(new_region_id)
		emit_signal("region_changed", old_region, new_region_id)
		print("[WorldController] 区域切换: ", old_region, " -> ", new_region_id)

func _get_region_at_position(pos: Vector2) -> String:
	var best_region_id := ""
	var best_area := INF

	for region_id in region_loader.regions.keys():
		if not region_loader.is_region_loaded(region_id):
			continue
		var def = region_loader.regions[region_id]
		var offset: Vector2 = def.get("world_offset", Vector2.ZERO)
		var size: Vector2 = def.get("region_size", Vector2(4096, 4096))
		var bounds := Rect2(offset, size)

		if bounds.has_point(pos):
			var area := size.x * size.y
			if area < best_area:
				best_area = area
				best_region_id = region_id

	if not best_region_id.is_empty():
		return best_region_id

	return current_region_id

func _get_spawn_position(region_id: String, spawn_id: String) -> Vector2:
	if spawn_positions.has(region_id) and spawn_positions[region_id].has(spawn_id):
		return spawn_positions[region_id][spawn_id]

	var def = region_loader.regions.get(region_id)
	if def != null:
		var offset: Vector2 = def.get("world_offset", Vector2.ZERO)
		var size: Vector2 = def.get("region_size", Vector2(4096, 4096))
		return offset + size / 2

	return WORLD_SIZE / 2

func spawn_player_at(region_id: String, spawn_id: String = "") -> void:
	if not region_loader.is_region_loaded(region_id):
		region_loader.load_region(region_id)

	await get_tree().create_timer(0.1).timeout

	var pos = _get_spawn_position(region_id, spawn_id if not spawn_id.is_empty() else "default")

	if player != null:
		player.global_position = pos

	if camera != null:
		camera.global_position = pos

	current_region_id = region_id
	region_loader.set_current_region(region_id)

	emit_signal("player_spawned", spawn_id)
	print("[WorldController] 传送到 ", region_id, " / ", spawn_id, " (", pos, ")")

func get_player() -> CharacterBody2D:
	return player

func get_camera() -> Camera2D:
	return camera

func get_region_loader() -> RegionLoader:
	return region_loader

func get_world_bounds() -> Rect2:
	return world_bounds

func is_position_valid(pos: Vector2) -> bool:
	if not enable_boundaries:
		return true
	return world_bounds.has_point(pos)
