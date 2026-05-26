extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const OUTDOOR_PATH := "res://game/scenes/world/OutdoorWorld.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0
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
const GENERATED_REGION_NODE_NAMES: Dictionary = {
	"village": "Village",
	"back_farm": "BackFarm",
	"orchard": "Orchard",
	"pond": "Pond",
	"mountain_path": "MountainPath",
	"mountain_hut": "MountainHut",
	"mountain": "Mountain",
	"cliff_view": "CliffView",
}
const VILLAGE_MOUNTAIN_HUT_SOCKET_BRIDGE_NODE := "VillageMountainHutSocketBridge"
const VILLAGE_MOUNTAIN_HUT_SOCKET_SPRITE_NODE := "PaintedSocketBridge"

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: outdoor world assembly initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	await _validate_outdoor_scene_contract()
	if _has_failed:
		return
	await _validate_main_reuses_outdoor_instance()
	if _has_failed:
		return
	print("OK: outdoor world assembly runtime validation passed")
	_finish_deferred(0)


func _validate_outdoor_scene_contract() -> void:
	var outdoor_scene := load(OUTDOOR_PATH) as PackedScene
	_expect(outdoor_scene != null, "OutdoorWorld scene should load")
	if _has_failed:
		return

	var outdoor := outdoor_scene.instantiate()
	root.add_child(outdoor)
	await process_frame
	await process_frame

	_expect(outdoor.has_method("set_active_region"), "OutdoorWorld should expose set_active_region")
	_expect(outdoor.has_method("get_active_region_id"), "OutdoorWorld should expose get_active_region_id")
	_expect(outdoor.has_method("get_outdoor_region_ids"), "OutdoorWorld should expose get_outdoor_region_ids")
	_expect(outdoor.has_method("get_region_offset"), "OutdoorWorld should expose get_region_offset")
	_expect(outdoor.has_method("get_region_bounds"), "OutdoorWorld should expose get_region_bounds")
	_expect(outdoor.get_node_or_null("Player") != null, "OutdoorWorld should expose one shared Player")
	_expect(outdoor.get_node_or_null("FarmPlots") != null, "OutdoorWorld should expose yard FarmPlots at root")
	_expect(outdoor.get_node_or_null("ForestTrailGate") != null, "OutdoorWorld should expose the yard-to-forest gate")
	_expect(outdoor.get_node_or_null("BackToYard") != null, "OutdoorWorld should expose the forest-to-yard return path")
	_expect(outdoor.get_node_or_null("FallenBranchBundle") != null, "OutdoorWorld should expose ForestEdge resource nodes")
	_expect(outdoor.get_node_or_null("QuietShrine") != null, "OutdoorWorld should expose ForestEdge discovery nodes")
	_expect(outdoor.get_node_or_null("SpawnFromHouse") != null, "OutdoorWorld should keep the house spawn")
	_expect(outdoor.get_node_or_null("SpawnFromYard") != null, "OutdoorWorld should keep the forest arrival spawn")
	if _has_failed:
		outdoor.queue_free()
		await process_frame
		return

	var region_ids: Array = outdoor.call("get_outdoor_region_ids")
	for region_id in OUTDOOR_REGION_IDS:
		_expect(region_ids.has(region_id), "OutdoorWorld should register outdoor region id: %s" % region_id)
		_expect(outdoor.call("get_region_bounds", region_id).has_area(), "OutdoorWorld should expose bounds for: %s" % region_id)
		if GENERATED_REGION_NODE_NAMES.has(region_id):
			var node_name := String(GENERATED_REGION_NODE_NAMES[region_id])
			var section := outdoor.get_node_or_null(node_name)
			_expect(section != null, "OutdoorWorld should compose generated section node: %s" % node_name)
			_expect(section != null and section.get_node_or_null("BaseGround") != null, "%s should include a base-ground visual layer" % node_name)
		outdoor.call("set_active_region", region_id, "default")
		await process_frame
		_expect(String(outdoor.call("get_active_region_id")) == region_id, "OutdoorWorld should switch active region to %s" % region_id)
		var spawn_id := String(outdoor.call("get_active_spawn_id"))
		_expect(_player_is_at_spawn(outdoor, spawn_id), "OutdoorWorld should place player at default spawn for %s" % region_id)
		_expect(outdoor.get_node_or_null("Player") != null, "OutdoorWorld should keep one shared Player after switching to %s" % region_id)

	var gate := outdoor.get_node("ForestTrailGate") as Node2D
	var back := outdoor.get_node("BackToYard") as Node2D
	_expect(gate.global_position.distance_to(back.global_position) <= 24.0, "Yard forest gate and forest return path should meet as one outdoor seam")
	_validate_village_mountain_hut_socket_contract(outdoor)
	if _has_failed:
		outdoor.queue_free()
		await process_frame
		return

	outdoor.call("set_active_region", "forest_edge", "from_yard")
	await process_frame
	_expect(String(outdoor.call("get_active_region_id")) == "forest_edge", "OutdoorWorld should switch active region to forest_edge")
	_expect(String(outdoor.name) == "ForestEdge", "OutdoorWorld should alias its root name to the active region for compatibility")
	_expect(_player_is_at_spawn(outdoor, "from_yard"), "OutdoorWorld should place the player at the forest arrival spawn")
	var schedule_director := outdoor.get_node_or_null("ScheduleDirector")
	var mika := outdoor.get_node_or_null("NPCs/Mika") as Node2D
	_expect(schedule_director != null, "OutdoorWorld should keep one active ScheduleDirector")
	_expect(mika != null, "OutdoorWorld should keep Mika in the shared outdoor NPC root")
	if schedule_director != null:
		schedule_director.apply_schedule("afternoon")
	_expect(mika == null or bool(mika.visible), "Mika should be visible for the ForestEdge afternoon schedule")
	_expect(mika == null or mika.position.x >= 480.0, "ForestEdge NPC schedule positions should be offset into the forest section")

	outdoor.queue_free()
	await process_frame


func _validate_village_mountain_hut_socket_contract(outdoor: Node) -> void:
	var village_bounds: Rect2 = outdoor.call("get_region_bounds", "village")
	var mountain_hut_bounds: Rect2 = outdoor.call("get_region_bounds", "mountain_hut")
	var horizontal_gap := mountain_hut_bounds.position.x - village_bounds.end.x
	_expect(horizontal_gap >= 0.0, "Village and MountainHut source bounds should not overlap enough to hide seam-registration problems")
	_expect(horizontal_gap >= -8.0, "Village and MountainHut should not overlap enough to hide seam-registration problems")
	_expect(abs(mountain_hut_bounds.position.y - village_bounds.position.y) <= 0.5, "Village and MountainHut socket rows should stay aligned")
	_expect(_socket_bridge_covers_gap(outdoor, village_bounds.end.x, mountain_hut_bounds.position.x), "VillageMountainHutSocketBridge should visually cover the OutdoorWorld fill gap")


func _socket_bridge_covers_gap(outdoor: Node, gap_start_x: float, gap_end_x: float) -> bool:
	if gap_end_x <= gap_start_x:
		return true
	var bridge := outdoor.get_node_or_null(VILLAGE_MOUNTAIN_HUT_SOCKET_BRIDGE_NODE)
	if bridge == null:
		return false
	var sprite := bridge.get_node_or_null(VILLAGE_MOUNTAIN_HUT_SOCKET_SPRITE_NODE) as Sprite2D
	if sprite == null or sprite.texture == null:
		return false
	var start_x := sprite.global_position.x
	var end_x := start_x + float(sprite.texture.get_width()) * sprite.global_scale.x
	return start_x <= gap_start_x and end_x >= gap_end_x


func _validate_main_reuses_outdoor_instance() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main := main_scene.instantiate()
	root.add_child(main)
	await _settle_route()

	var house: Node = main.get_current_gameplay_scene()
	_expect(house != null and house.name == "PlayerHouse", "Main should still start indoors")
	var house_door: Node = house.get_node_or_null("DoorToYard")
	_expect(house_door != null, "PlayerHouse should include DoorToYard")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	house_door.on_interact(house.get_node_or_null("Player"))
	await _settle_route()

	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "DoorToYard should enter the outdoor world as player_yard")
	var outdoor_before: Node = main.get_current_gameplay_scene()
	_expect(outdoor_before != null, "Main should expose the loaded outdoor world after leaving the house")
	_expect(outdoor_before.has_method("get_active_region_id"), "Main should load OutdoorWorld for player_yard")
	_expect(String(outdoor_before.call("get_active_region_id")) == "player_yard", "OutdoorWorld active region should be player_yard")
	_expect(_player_is_at_spawn(outdoor_before, "from_house"), "Player should land at the yard house spawn")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	for region_id in OUTDOOR_REGION_IDS:
		main.change_scene(region_id, "default")
		await _settle_route()
		var outdoor_for_region: Node = main.get_current_gameplay_scene()
		_expect(outdoor_for_region == outdoor_before, "Main should reuse OutdoorWorld instance for %s" % region_id)
		_expect(String(main.get_current_gameplay_scene_id()) == region_id, "Main public scene id should update to %s" % region_id)
		_expect(String(outdoor_for_region.call("get_active_region_id")) == region_id, "OutdoorWorld active id should update to %s" % region_id)

	var player := outdoor_before.get_node_or_null("Player") as Node2D
	_expect(player != null, "OutdoorWorld should still expose Player before walk-seam simulation")
	if player != null:
		var village_bounds: Rect2 = outdoor_before.call("get_region_bounds", "village")
		player.global_position = village_bounds.get_center()
		await process_frame
		await process_frame
		_expect(String(outdoor_before.call("get_active_region_id")) == "village", "Walking into the village section should update active region without loading a new scene")
		_expect(main.get_current_gameplay_scene() == outdoor_before, "Walk-seam region changes should keep the same OutdoorWorld instance")

	var forest_gate: Node = outdoor_before.get_node_or_null("ForestTrailGate")
	_expect(forest_gate != null, "OutdoorWorld should include ForestTrailGate")
	forest_gate.on_interact(outdoor_before.get_node_or_null("Player"))
	await _settle_route()

	var outdoor_after: Node = main.get_current_gameplay_scene()
	_expect(outdoor_after == outdoor_before, "Yard to ForestEdge should reuse the same OutdoorWorld instance")
	_expect(String(main.get_current_gameplay_scene_id()) == "forest_edge", "ForestTrailGate should update the public scene id to forest_edge")
	_expect(String(outdoor_after.call("get_active_region_id")) == "forest_edge", "OutdoorWorld should mark forest_edge active after using the gate")
	_expect(_player_is_at_spawn(outdoor_after, "from_yard"), "Player should land at the forest arrival spawn")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	var back_to_yard: Node = outdoor_after.get_node_or_null("BackToYard")
	_expect(back_to_yard != null, "OutdoorWorld should include BackToYard")
	back_to_yard.on_interact(outdoor_after.get_node_or_null("Player"))
	await _settle_route()

	_expect(main.get_current_gameplay_scene() == outdoor_before, "ForestEdge to yard should still reuse the same OutdoorWorld instance")
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "BackToYard should update the public scene id to player_yard")
	_expect(String(outdoor_before.call("get_active_region_id")) == "player_yard", "OutdoorWorld should reactivate player_yard after returning")
	_expect(_player_is_at_spawn(outdoor_before, "from_forest_edge"), "Player should land at the yard forest-return spawn")

	main.queue_free()
	await process_frame


func _settle_route() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _player_is_at_spawn(scene: Node, spawn_id: String) -> bool:
	if scene == null:
		return false
	var player := scene.get_node_or_null("Player") as Node2D
	var spawn := _find_spawn(scene, spawn_id)
	return player != null and spawn != null and player.global_position.distance_to(spawn.global_position) <= 1.0


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


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	_finish_deferred(1)


func _start_watchdog() -> void:
	if _finished:
		return
	_watchdog_timer = Timer.new()
	_watchdog_timer.one_shot = true
	_watchdog_timer.wait_time = WATCHDOG_TIMEOUT_SECONDS
	root.add_child(_watchdog_timer)
	_watchdog_timer.timeout.connect(func() -> void:
		if not _finished:
			_fail("Outdoor world assembly validation timed out")
	)
	_watchdog_timer.start()


func _finish_deferred(exit_code: int) -> void:
	if _finished:
		return
	_finished = true
	if _watchdog_timer != null:
		_watchdog_timer.stop()
		_watchdog_timer.queue_free()
		_watchdog_timer = null
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
