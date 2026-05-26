class_name OutdoorWorld
extends "res://game/scenes/world/PlayerYard.gd"

signal active_region_changed(scene_id: String, spawn_id: String)

const PLAYER_YARD_SCENE: String = "res://game/scenes/world/PlayerYard.tscn"
const FOREST_EDGE_SCENE: String = "res://game/scenes/world/ForestEdge.tscn"
const FLAG_INTERACTABLE_SCRIPT: Script = preload("res://game/entities/interactable/FlagInteractable.gd")
const FLAG_DIALOGUE_INTERACTABLE_SCRIPT: Script = preload("res://game/entities/interactable/FlagDialogueInteractable.gd")
const SEED_STALL_ADVICE_SCRIPT: Script = preload("res://game/entities/interactable/SeedStallAdvice.gd")
const SCENE_TRAVEL_SCRIPT: Script = preload("res://game/entities/interactable/SceneTravel.gd")
const FOREST_EDGE_OFFSET: Vector2 = Vector2(380.0, -12.0)
const GENERATED_REGION_SIZE: Vector2 = Vector2(320.0, 240.0)
const GENERATED_REGION_TEXTURE_SCALE: Vector2 = Vector2(0.18, 0.18)
const GENERATED_REGION_DEFAULT_SPAWN: Vector2 = Vector2(160.0, 132.0)
const VILLAGE_INTERACTABLE_SHAPE_SIZE: Vector2 = Vector2(48.0, 30.0)
const PLAYER_YARD_BOUNDS: Rect2 = Rect2(Vector2(-40.0, -96.0), Vector2(372.0, 408.0))
const OUTDOOR_GROUND_FILL_NODE: String = "OutdoorGroundFill"
const OUTDOOR_GROUND_FILL_COLOR: Color = Color(0.47, 0.59, 0.39, 1.0)
const OUTDOOR_GROUND_FILL_MARGIN: Vector2 = Vector2(960.0, 720.0)
const VILLAGE_MOUNTAIN_HUT_SOCKET_BRIDGE_NODE: String = "VillageMountainHutSocketBridge"
const VILLAGE_MOUNTAIN_HUT_SOCKET_TEXTURE_PATH: String = "res://assets/art/greenfield_p0/world/socket_bridges/village_mountain_hut_socket_bridge.png"
const VILLAGE_MOUNTAIN_HUT_SOCKET_TEXTURE_POSITION: Vector2 = Vector2(1018.0, -12.0)
const VILLAGE_MOUNTAIN_HUT_SOCKET_POINTS: Array[Vector2] = [
	Vector2(1036.0, 108.0),
	Vector2(1064.0, 108.0),
]

const REGION_NAMES: Dictionary = {
	"player_yard": "PlayerYard",
	"forest_edge": "ForestEdge",
	"village": "Village",
	"back_farm": "BackFarm",
	"orchard": "Orchard",
	"pond": "Pond",
	"mountain_path": "MountainPath",
	"mountain_hut": "MountainHut",
	"mountain": "Mountain",
	"cliff_view": "CliffView",
}

const OUTDOOR_REGION_IDS: Array[String] = [
	"player_yard",
	"forest_edge",
	"village",
	"back_farm",
	"orchard",
	"pond",
	"mountain_path",
	"mountain_hut",
	"mountain",
	"cliff_view",
]

const GENERATED_REGION_IDS: Array[String] = [
	"village",
	"back_farm",
	"orchard",
	"pond",
	"mountain_path",
	"mountain_hut",
	"mountain",
	"cliff_view",
]

const REGION_OFFSETS: Dictionary = {
	"player_yard": Vector2.ZERO,
	"forest_edge": FOREST_EDGE_OFFSET,
	"village": Vector2(720.0, -12.0),
	"back_farm": Vector2(0.0, 324.0),
	"orchard": Vector2(380.0, 324.0),
	"pond": Vector2(720.0, 324.0),
	"mountain_path": Vector2(720.0, -316.0),
	"mountain_hut": Vector2(1060.0, -12.0),
	"mountain": Vector2(1060.0, -316.0),
	"cliff_view": Vector2(1400.0, -316.0),
}

const REGION_SIZES: Dictionary = {
	"player_yard": PLAYER_YARD_BOUNDS.size,
	"forest_edge": Vector2(340.0, 320.0),
	"village": GENERATED_REGION_SIZE,
	"back_farm": GENERATED_REGION_SIZE,
	"orchard": GENERATED_REGION_SIZE,
	"pond": GENERATED_REGION_SIZE,
	"mountain_path": GENERATED_REGION_SIZE,
	"mountain_hut": GENERATED_REGION_SIZE,
	"mountain": GENERATED_REGION_SIZE,
	"cliff_view": GENERATED_REGION_SIZE,
}

const DEFAULT_SPAWNS: Dictionary = {
	"player_yard": "from_house",
	"forest_edge": "from_yard",
	"village": "village_default",
	"back_farm": "back_farm_default",
	"orchard": "orchard_default",
	"pond": "pond_default",
	"mountain_path": "mountain_path_default",
	"mountain_hut": "mountain_hut_default",
	"mountain": "mountain_default",
	"cliff_view": "cliff_view_default",
}

const GENERATED_REGION_TEXTURE_LAYERS: Array[Dictionary] = [
	{"name": "BaseGround", "suffix": "base_ground", "z_index": -30},
	{"name": "TerrainDetails", "suffix": "terrain_details", "z_index": -25},
	{"name": "BehindPlayerStructures", "suffix": "behind_player_structures", "z_index": -10},
	{"name": "YSortPropsStructures", "suffix": "ysort_props_structures", "z_index": 8},
	{"name": "ForegroundOcclusion", "suffix": "foreground_occlusion", "z_index": 40},
]

const FOREST_EDGE_NPC_REVIEW_POSITIONS: Dictionary = {
	"Mika": Vector2(136.0, 88.0),
}

const FOREST_EDGE_SKIP_NODES: Array[String] = [
	"WorldCamera",
	"DataRegistry",
	"TimeManager",
	"WeatherManager",
	"InventoryManager",
	"RelationshipManager",
	"DialogueManager",
	"RumorManager",
	"GameState",
	"DialogueBox",
	"Player",
	"NPCs",
	"ScheduleDirector",
]

const FOREST_EDGE_RENAMED_NODES: Dictionary = {
	"WorldBackdrop": "ForestWorldBackdrop",
	"Ground": "ForestGround",
}

var active_region_id: String = "player_yard"
var active_spawn_id: String = "from_house"
var _is_composed: bool = false
var _camera_snap_next_frame: bool = true


func _ready() -> void:
	_compose_player_yard()
	_compose_forest_edge()
	_compose_generated_region_sections()
	_compose_world_ground_fill()
	_compose_world_socket_bridges()
	_refresh_player_yard_references()
	super._ready()
	set_active_region(active_region_id, active_spawn_id)


func _process(delta: float) -> void:
	_update_active_region_from_player()
	_update_world_camera(delta)


func set_active_region(scene_id: String, spawn_id: String = "default") -> void:
	_activate_region(scene_id, spawn_id, true)


func get_active_region_id() -> String:
	return active_region_id


func get_active_spawn_id() -> String:
	return active_spawn_id


func get_outdoor_region_ids() -> Array:
	return OUTDOOR_REGION_IDS.duplicate()


func get_region_offset(scene_id: String) -> Vector2:
	return _get_region_offset(scene_id)


func get_region_bounds(scene_id: String) -> Rect2:
	if scene_id == "player_yard":
		return PLAYER_YARD_BOUNDS
	var offset := _get_region_offset(scene_id)
	var size := _get_region_size(scene_id)
	if scene_id == "forest_edge":
		return Rect2(offset + Vector2(-48.0, -96.0), size)
	return Rect2(offset, size)


func _activate_region(scene_id: String, spawn_id: String = "default", should_place_player: bool = true) -> void:
	if not REGION_NAMES.has(scene_id):
		push_warning("OutdoorWorld unknown active region: %s" % scene_id)
		return
	active_region_id = scene_id
	active_spawn_id = _resolve_outdoor_spawn(scene_id, spawn_id)
	name = String(REGION_NAMES.get(scene_id, "OutdoorWorld"))
	if schedule_director != null:
		schedule_director.set("scene_id", active_region_id)
		schedule_director.set("position_offset", _get_region_offset(active_region_id))
		if schedule_director.has_method("apply_schedule"):
			schedule_director.apply_schedule()
	_apply_inactive_region_review_positions()
	if should_place_player:
		_place_player_at_spawn(active_spawn_id)
	_camera_snap_next_frame = true
	_update_world_camera(0.0)
	active_region_changed.emit(active_region_id, active_spawn_id)


func refresh_runtime_ui() -> void:
	super.refresh_runtime_ui()
	if schedule_director != null:
		schedule_director.set("scene_id", active_region_id)
		schedule_director.set("position_offset", _get_region_offset(active_region_id))
		if schedule_director.has_method("apply_schedule"):
			schedule_director.apply_schedule()
	_apply_inactive_region_review_positions()


func _compose_player_yard() -> void:
	if _is_composed:
		return
	var packed_scene := load(PLAYER_YARD_SCENE) as PackedScene
	if packed_scene == null:
		push_error("OutdoorWorld could not load PlayerYard scene.")
		return
	var section := packed_scene.instantiate()
	section.set_script(null)
	_move_all_children_to_root(section, Vector2.ZERO, "player_yard")
	section.free()
	_is_composed = true


func _compose_forest_edge() -> void:
	var packed_scene := load(FOREST_EDGE_SCENE) as PackedScene
	if packed_scene == null:
		push_error("OutdoorWorld could not load ForestEdge scene.")
		return
	var section := packed_scene.instantiate()
	section.set_script(null)
	var children := section.get_children()
	for child in children:
		if FOREST_EDGE_SKIP_NODES.has(String(child.name)):
			continue
		var target_name := String(FOREST_EDGE_RENAMED_NODES.get(String(child.name), String(child.name)))
		_move_child_to_root(section, child, FOREST_EDGE_OFFSET, target_name, "forest_edge")
	section.free()


func _compose_generated_region_sections() -> void:
	for region_id in GENERATED_REGION_IDS:
		var section_name := String(REGION_NAMES.get(region_id, region_id))
		if get_node_or_null(section_name) != null:
			continue
		var section := Node2D.new()
		section.name = section_name
		section.position = _get_region_offset(region_id)
		section.set_meta("region_id", region_id)
		section.set_meta("section_role", "seamless_outdoor_region")
		add_child(section)
		_add_generated_region_layers(section, region_id)
		_add_generated_region_spawns(section, region_id)
		if region_id == "village":
			_add_village_authored_slice(section)


func _compose_world_ground_fill() -> void:
	if get_node_or_null(OUTDOOR_GROUND_FILL_NODE) != null:
		return
	var rect := _get_merged_region_bounds().grow_individual(
		OUTDOOR_GROUND_FILL_MARGIN.x,
		OUTDOOR_GROUND_FILL_MARGIN.y,
		OUTDOOR_GROUND_FILL_MARGIN.x,
		OUTDOOR_GROUND_FILL_MARGIN.y
	)
	var fill := Polygon2D.new()
	fill.name = OUTDOOR_GROUND_FILL_NODE
	fill.z_index = -90
	fill.color = OUTDOOR_GROUND_FILL_COLOR
	fill.polygon = PackedVector2Array([
		rect.position,
		Vector2(rect.end.x, rect.position.y),
		rect.end,
		Vector2(rect.position.x, rect.end.y),
	])
	add_child(fill)


func _compose_world_socket_bridges() -> void:
	if get_node_or_null(VILLAGE_MOUNTAIN_HUT_SOCKET_BRIDGE_NODE) != null:
		return
	_add_village_mountain_hut_socket_bridge()


func _add_village_mountain_hut_socket_bridge() -> Node2D:
	var bridge := Node2D.new()
	bridge.name = VILLAGE_MOUNTAIN_HUT_SOCKET_BRIDGE_NODE
	bridge.z_as_relative = false
	bridge.set_meta("socket_bridge", "village_to_mountain_hut")
	bridge.set_meta("review_role", "world_assembly_gap_cover_not_region_source_art")
	add_child(bridge)
	var texture := _load_socket_bridge_texture(VILLAGE_MOUNTAIN_HUT_SOCKET_TEXTURE_PATH)
	if texture == null:
		return bridge
	var sprite := Sprite2D.new()
	sprite.name = "PaintedSocketBridge"
	sprite.texture = texture
	sprite.centered = false
	sprite.position = VILLAGE_MOUNTAIN_HUT_SOCKET_TEXTURE_POSITION
	sprite.z_index = -29
	bridge.add_child(sprite)
	return bridge


func _load_socket_bridge_texture(path: String) -> Texture2D:
	var image := Image.new()
	var error := image.load(ProjectSettings.globalize_path(path))
	if error != OK:
		push_warning("OutdoorWorld could not load socket bridge texture: %s" % path)
		return null
	return ImageTexture.create_from_image(image)


func _add_generated_region_layers(section: Node2D, region_id: String) -> void:
	for layer_def in GENERATED_REGION_TEXTURE_LAYERS:
		var suffix := String(layer_def.get("suffix", ""))
		var texture_path := "res://assets/art/greenfield_p0/regions/%s/layers/%s_%s.png" % [region_id, region_id, suffix]
		var texture := load(texture_path) as Texture2D
		if texture == null:
			continue
		var sprite := Sprite2D.new()
		sprite.name = String(layer_def.get("name", suffix))
		sprite.texture = texture
		sprite.centered = false
		sprite.scale = GENERATED_REGION_TEXTURE_SCALE
		sprite.z_index = int(layer_def.get("z_index", 0))
		section.add_child(sprite)


func _add_generated_region_spawns(section: Node2D, region_id: String) -> void:
	var spawn := Marker2D.new()
	spawn.name = "Spawn%sDefault" % String(REGION_NAMES.get(region_id, region_id))
	spawn.set_script(preload("res://game/systems/scene/SpawnPoint.gd"))
	spawn.set("spawn_id", String(DEFAULT_SPAWNS.get(region_id, "%s_default" % region_id)))
	spawn.position = GENERATED_REGION_DEFAULT_SPAWN
	section.add_child(spawn)


func _add_village_authored_slice(section: Node2D) -> void:
	if section.get_node_or_null("VillagePlazaZone") != null:
		return
	_add_village_polygon(
		section,
		"VillagePlazaZone",
		PackedVector2Array([
			Vector2(66.0, 54.0),
			Vector2(228.0, 48.0),
			Vector2(270.0, 112.0),
			Vector2(226.0, 176.0),
			Vector2(72.0, 170.0),
			Vector2(42.0, 104.0),
		]),
		Color(0.68, 0.59, 0.40, 0.72),
		-6
	)
	_add_village_polygon(
		section,
		"VillageNoticeZone",
		PackedVector2Array([
			Vector2(78.0, 60.0),
			Vector2(142.0, 58.0),
			Vector2(150.0, 116.0),
			Vector2(74.0, 124.0),
		]),
		Color(0.58, 0.46, 0.30, 0.82),
		-4
	)
	_add_village_polygon(
		section,
		"VillageSeedStallZone",
		PackedVector2Array([
			Vector2(174.0, 72.0),
			Vector2(248.0, 70.0),
			Vector2(262.0, 134.0),
			Vector2(178.0, 144.0),
		]),
		Color(0.50, 0.58, 0.36, 0.82),
		-4
	)
	_add_village_polygon(
		section,
		"VillageSoftClueZone",
		PackedVector2Array([
			Vector2(220.0, 136.0),
			Vector2(286.0, 136.0),
			Vector2(292.0, 196.0),
			Vector2(216.0, 204.0),
		]),
		Color(0.40, 0.50, 0.36, 0.76),
		-4
	)
	_add_village_path_network(section)
	_add_village_flag_interactable(
		section,
		"VillageNotice",
		Vector2(112.0, 88.0),
		"village_notice",
		"村口公告",
		"按 E 查看村口公告",
		"公告写着：今天广场只收拾种子摊和旧枫树旁的小牌，别急着跑远。",
		"read_village_notice_day1",
		Color(0.50, 0.32, 0.18, 1.0)
	)
	_add_village_flag_interactable(
		section,
		"SeedStallProxy",
		Vector2(210.0, 104.0),
		"seed_stall_proxy",
		"种子摊",
		"按 E 看看种子摊",
		"摊位还没有正式营业，只摆着几包试种标签，像是在等葵回来整理。",
		"visited_village_seed_stall_day1",
		Color(0.58, 0.42, 0.24, 1.0)
	)
	_add_village_flag_interactable(
		section,
		"OldMapleClue",
		Vector2(256.0, 168.0),
		"old_maple_clue",
		"旧枫树小牌",
		"按 E 看看旧枫树小牌",
		"小牌背面刻着一行很浅的字：井声轻的时候，去问问会记路的人。",
		"found_village_soft_clue_day1",
		Color(0.44, 0.30, 0.20, 1.0)
	)
	_add_village_return_path(section)


func _add_village_path_network(section: Node2D) -> void:
	var path_root := Node2D.new()
	path_root.name = "VillageRoutePathNetwork"
	path_root.z_index = -5
	section.add_child(path_root)
	_add_village_polygon(
		path_root,
		"VillageWestArrivalPath",
		PackedVector2Array([
			Vector2(0.0, 126.0),
			Vector2(86.0, 104.0),
			Vector2(118.0, 132.0),
			Vector2(22.0, 156.0),
		]),
		Color(0.62, 0.53, 0.36, 0.86),
		0
	)
	_add_village_polygon(
		path_root,
		"VillageNoticeStallPath",
		PackedVector2Array([
			Vector2(106.0, 96.0),
			Vector2(210.0, 92.0),
			Vector2(220.0, 124.0),
			Vector2(112.0, 128.0),
		]),
		Color(0.66, 0.56, 0.37, 0.82),
		0
	)
	_add_village_polygon(
		path_root,
		"VillageSoftCluePath",
		PackedVector2Array([
			Vector2(202.0, 120.0),
			Vector2(258.0, 150.0),
			Vector2(250.0, 178.0),
			Vector2(190.0, 140.0),
		]),
		Color(0.60, 0.53, 0.38, 0.74),
		0
	)


func _add_village_polygon(parent: Node, node_name: String, points: PackedVector2Array, color: Color, z_index: int) -> Polygon2D:
	var polygon := Polygon2D.new()
	polygon.name = node_name
	polygon.color = color
	polygon.z_index = z_index
	polygon.polygon = points
	parent.add_child(polygon)
	return polygon


func _add_village_flag_interactable(
	section: Node2D,
	node_name: String,
	local_position: Vector2,
	interactable_id: String,
	display_name: String,
	interaction_hint: String,
	interaction_text: String,
	flag_id: String,
	marker_color: Color
) -> Area2D:
	if node_name == "SeedStallProxy":
		return _add_village_seed_stall_advice(section)
	if node_name == "VillageNotice":
		return _add_village_notice_dialogue(section)
	if node_name == "OldMapleClue":
		return _add_village_old_maple_clue(section)
	var area := Area2D.new()
	area.name = node_name
	area.add_to_group("interactable")
	area.position = local_position
	area.set_script(FLAG_INTERACTABLE_SCRIPT)
	area.set("interactable_id", interactable_id)
	area.set("display_name", display_name)
	area.set("interaction_hint", interaction_hint)
	area.set("interaction_text", interaction_text)
	area.set("flag_id", flag_id)
	_add_village_interactable_shape(area, "%sShape" % node_name)
	_add_village_interactable_marker(area, "%sMarker" % node_name, marker_color)
	section.add_child(area)
	return area


func _add_village_notice_dialogue(section: Node2D) -> Area2D:
	var area := Area2D.new()
	area.name = "VillageNotice"
	area.add_to_group("interactable")
	area.position = Vector2(112.0, 88.0)
	area.set_script(FLAG_DIALOGUE_INTERACTABLE_SCRIPT)
	area.set("interactable_id", "village_notice")
	area.set("display_name", "村口公告")
	area.set("interaction_hint", "按 E 查看村口公告")
	area.set("interaction_text", "公告写着：今天广场只收拾种子摊和旧枫树旁的小牌，别急着跑远。")
	area.set("flag_id", "read_village_notice_day1")
	area.set("dialogue_id", "village_notice_dialogue")
	area.set("speaker_id", "village_notice")
	area.set("speaker_name", "村口公告")
	area.set("dialogue_text", "公告写着：今天广场只收拾种子摊和旧枫树旁的小牌，别急着跑远。")
	_add_village_interactable_shape(area, "VillageNoticeShape")
	_add_village_interactable_marker(area, "VillageNoticeMarker", Color(0.50, 0.32, 0.18, 1.0))
	section.add_child(area)
	return area


func _add_village_old_maple_clue(section: Node2D) -> Area2D:
	var area := Area2D.new()
	area.name = "OldMapleClue"
	area.add_to_group("interactable")
	area.position = Vector2(256.0, 168.0)
	area.set_script(FLAG_DIALOGUE_INTERACTABLE_SCRIPT)
	area.set("interactable_id", "old_maple_clue")
	area.set("display_name", "旧枫树小牌")
	area.set("interaction_hint", "按 E 查看旧枫树小牌")
	area.set("interaction_text", "小牌背面刻着一行很浅的字：井声轻的时候，去问问会记路的人。")
	area.set("flag_id", "found_village_soft_clue_day1")
	area.set("dialogue_id", "old_maple_clue_dialogue")
	area.set("speaker_id", "old_maple_clue")
	area.set("speaker_name", "旧枫树小牌")
	area.set("dialogue_text", "小牌背面刻着一行很浅的字：井声轻的时候，去问问会记路的人。")
	_add_village_interactable_shape(area, "OldMapleClueShape")
	_add_village_interactable_marker(area, "OldMapleClueMarker", Color(0.44, 0.30, 0.20, 1.0))
	section.add_child(area)
	return area


func _add_village_seed_stall_advice(section: Node2D) -> Area2D:
	var area := Area2D.new()
	area.name = "SeedStallProxy"
	area.add_to_group("interactable")
	area.position = Vector2(210.0, 104.0)
	area.set_script(SEED_STALL_ADVICE_SCRIPT)
	area.set("interactable_id", "seed_stall_proxy")
	area.set("display_name", "种子摊")
	area.set("interaction_hint", "按 E 问今天种什么")
	area.set("interaction_text", "")
	area.set("visit_flag_id", "visited_village_seed_stall_day1")
	_add_village_interactable_shape(area, "SeedStallProxyShape")
	_add_village_interactable_marker(area, "SeedStallProxyMarker", Color(0.58, 0.42, 0.24, 1.0))
	section.add_child(area)
	return area


func _add_village_return_path(section: Node2D) -> Area2D:
	var area := Area2D.new()
	area.name = "VillageReturnPath"
	area.add_to_group("interactable")
	area.position = Vector2(22.0, 136.0)
	area.set_script(SCENE_TRAVEL_SCRIPT)
	area.set("interactable_id", "village_return_path")
	area.set("display_name", "回院子的小路")
	area.set("interaction_hint", "按 E 沿小路回院子")
	area.set("interaction_text", "广场西边的小路接回自家院门，走起来不远。")
	area.set("target_scene_id", "player_yard")
	area.set("target_spawn_id", "from_house")
	area.set("arrival_flag_id", "returned_from_village_day1")
	_add_village_interactable_shape(area, "VillageReturnPathShape")
	_add_village_interactable_marker(area, "VillageReturnPathMarker", Color(0.62, 0.52, 0.36, 1.0))
	section.add_child(area)
	return area


func _add_village_interactable_shape(area: Area2D, node_name: String) -> void:
	var shape := CollisionShape2D.new()
	shape.name = node_name
	var rectangle := RectangleShape2D.new()
	rectangle.size = VILLAGE_INTERACTABLE_SHAPE_SIZE
	shape.shape = rectangle
	area.add_child(shape)


func _add_village_interactable_marker(area: Area2D, node_name: String, color: Color) -> void:
	var marker := Polygon2D.new()
	marker.name = node_name
	marker.color = color
	marker.z_index = 44
	marker.polygon = PackedVector2Array([
		Vector2(-20.0, -12.0),
		Vector2(20.0, -12.0),
		Vector2(20.0, 12.0),
		Vector2(-20.0, 12.0),
	])
	area.add_child(marker)


func _move_all_children_to_root(section: Node, offset: Vector2, region_id: String = "") -> void:
	var children := section.get_children()
	for child in children:
		_move_child_to_root(section, child, offset, String(child.name), region_id)


func _move_child_to_root(section: Node, child: Node, offset: Vector2, target_name: String, region_id: String = "") -> void:
	section.remove_child(child)
	child.name = target_name
	if child is Node2D:
		var node_2d := child as Node2D
		node_2d.position += offset
	_clear_owner_recursive(child)
	_assign_outdoor_region_meta(child, region_id)
	add_child(child)


func _assign_outdoor_region_meta(node: Node, region_id: String) -> void:
	if region_id.is_empty():
		return
	if node.is_in_group("interactable") and not (node is NPC):
		node.set_meta("outdoor_region_id", region_id)
	for child in node.get_children():
		_assign_outdoor_region_meta(child, region_id)


func _clear_owner_recursive(node: Node) -> void:
	node.owner = null
	for child in node.get_children():
		_clear_owner_recursive(child)


func _refresh_player_yard_references() -> void:
	data_registry = get_node_or_null("DataRegistry")
	inventory_manager = get_node_or_null("InventoryManager")
	weather_manager = get_node_or_null("WeatherManager")
	time_manager = get_node_or_null("TimeManager")
	dialogue_manager = get_node_or_null("DialogueManager")
	relationship_manager = get_node_or_null("RelationshipManager")
	rumor_manager = get_node_or_null("RumorManager")
	game_state = get_node_or_null("GameState")
	save_manager = get_node_or_null("SaveManager")
	time_weather_hud = get_node_or_null("TimeWeatherHUD")
	inventory_ui = get_node_or_null("InventoryUI")
	dialogue_box = get_node_or_null("DialogueBox")
	farm_plots = get_node_or_null("FarmPlots")
	npcs = get_node_or_null("NPCs")
	bed = get_node_or_null("Bed")
	mailbox = get_node_or_null("Mailbox")
	bulletin_board = get_node_or_null("BulletinBoard")
	old_well = get_node_or_null("OldWell")
	schedule_director = get_node_or_null("ScheduleDirector")
	player = get_node_or_null("Player")


func _resolve_outdoor_spawn(scene_id: String, spawn_id: String) -> String:
	if not spawn_id.is_empty() and spawn_id != "default":
		return spawn_id
	return String(DEFAULT_SPAWNS.get(scene_id, "from_house"))


func _place_player_at_spawn(spawn_id: String) -> void:
	if player == null or spawn_id.is_empty():
		return
	var spawn := _find_spawn(self, spawn_id)
	if spawn == null:
		return
	(player as Node2D).global_position = spawn.global_position


func _find_spawn(node: Node, spawn_id: String) -> Node2D:
	if node == null:
		return null
	if node.has_method("get_spawn_id") and String(node.call("get_spawn_id")) == spawn_id and node is Node2D:
		return node as Node2D
	for child in node.get_children():
		var found := _find_spawn(child, spawn_id)
		if found != null:
			return found
	return null


func _get_region_offset(scene_id: String) -> Vector2:
	return REGION_OFFSETS.get(scene_id, Vector2.ZERO)


func _get_region_size(scene_id: String) -> Vector2:
	return REGION_SIZES.get(scene_id, GENERATED_REGION_SIZE)


func _get_merged_region_bounds() -> Rect2:
	var has_rect := false
	var result := Rect2()
	for region_id in OUTDOOR_REGION_IDS:
		var bounds := get_region_bounds(region_id)
		if not has_rect:
			result = bounds
			has_rect = true
		else:
			result = result.merge(bounds)
	return result


func _apply_inactive_region_review_positions() -> void:
	if active_region_id != "forest_edge" or npcs == null:
		return
	for npc_name in FOREST_EDGE_NPC_REVIEW_POSITIONS.keys():
		var npc := npcs.get_node_or_null(String(npc_name)) as Node2D
		if npc == null or bool(npc.visible):
			continue
		npc.position = FOREST_EDGE_OFFSET + (FOREST_EDGE_NPC_REVIEW_POSITIONS[npc_name] as Vector2)


func _update_active_region_from_player() -> void:
	if player == null or not (player is Node2D):
		return
	var next_region_id := _get_region_id_at_position((player as Node2D).global_position)
	if next_region_id.is_empty() or next_region_id == active_region_id:
		return
	_activate_region(next_region_id, String(DEFAULT_SPAWNS.get(next_region_id, "default")), false)


func _get_region_id_at_position(position: Vector2) -> String:
	var best_region_id := ""
	var best_area := INF
	for region_id in OUTDOOR_REGION_IDS:
		var bounds := get_region_bounds(region_id)
		if not bounds.has_point(position):
			continue
		var area := bounds.size.x * bounds.size.y
		if area < best_area:
			best_area = area
			best_region_id = region_id
	return best_region_id


func _update_world_camera(delta: float) -> void:
	var world_camera := get_node_or_null("WorldCamera") as Camera2D
	if world_camera == null or player == null or not (player is Node2D):
		return
	world_camera.enabled = true
	world_camera.make_current()
	var target := (player as Node2D).position + _camera_offset_for_region(active_region_id)
	if _camera_snap_next_frame or delta <= 0.0:
		world_camera.position = target
		_camera_snap_next_frame = false
	else:
		world_camera.position = world_camera.position.lerp(target, 1.0 - exp(-6.0 * delta))


func _camera_offset_for_region(scene_id: String) -> Vector2:
	if scene_id == "forest_edge":
		return Vector2(48.0, -32.0)
	if GENERATED_REGION_IDS.has(scene_id):
		return Vector2(96.0, -40.0)
	return Vector2(64.0, -24.0)
