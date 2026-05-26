extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: forest edge gameplay layout initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main: Node = main_scene.instantiate()
	root.add_child(main)
	await _settle()

	await _validate_visit_completion_on_travel(main)
	if _has_failed:
		return
	_validate_forest_layout_structure(main)
	if _has_failed:
		return

	print("OK: forest edge gameplay layout runtime validation passed")
	_finish_deferred(0)


func _validate_visit_completion_on_travel(main: Node) -> void:
	main.change_scene("player_yard", "from_house")
	await _settle()

	var yard: Node = main.get_current_gameplay_scene()
	_expect(yard != null and yard.name == "PlayerYard", "Main should enter PlayerYard")
	if _has_failed:
		return

	var yard_game_state := yard.get_node_or_null("GameState")
	var player := yard.get_node_or_null("Player")
	var forest_gate := yard.get_node_or_null("ForestTrailGate")
	var chip := main.get_node_or_null("CurrentObjectiveChip")
	for pair in {
		"GameState": yard_game_state,
		"Player": player,
		"ForestTrailGate": forest_gate,
		"CurrentObjectiveChip": chip,
	}.keys():
		var node: Node = {
			"GameState": yard_game_state,
			"Player": player,
			"ForestTrailGate": forest_gate,
			"CurrentObjectiveChip": chip,
		}[pair]
		_expect(node != null, "Missing visit-completion node: %s" % pair)
		if _has_failed:
			return

	_set_first_week_before_forest(yard_game_state)
	main.sync_current_scene_state()
	await _settle()
	_expect(String(chip.get_current_goal_text()).contains("去森林边缘"), "Chip should ask the player to go to ForestEdge before travel")
	if _has_failed:
		return

	forest_gate.on_interact(player)
	await _settle()
	_expect(String(main.get_current_gameplay_scene_id()) == "forest_edge", "ForestTrailGate should route to ForestEdge")
	var shared_game_state := main.get_node_or_null("GameState")
	_expect(shared_game_state != null, "Main should own shared GameState")
	if _has_failed:
		return
	_expect(bool(shared_game_state.get_flag("visited_forest_edge", false)), "Forest travel should complete visited_forest_edge immediately")
	_expect(String(chip.get_current_goal_text()).contains("Mika"), "Chip should advance from visit ForestEdge to Mika's rumor after travel")


func _validate_forest_layout_structure(main: Node) -> void:
	var forest: Node = main.get_current_gameplay_scene()
	_expect(forest != null and forest.name == "ForestEdge", "ForestEdge should be active")
	if _has_failed:
		return

	var structure := forest.get_node_or_null("ForestStructure")
	var route_network := forest.get_node_or_null("ForestStructure/RoutePathNetwork")
	_expect(structure != null, "ForestEdge should include ForestStructure")
	_expect(route_network != null, "ForestStructure should include RoutePathNetwork")
	if _has_failed:
		return

	for path_name in [
		"ArrivalReturnPath",
		"ShrineResourcePath",
		"MikaClearingPath",
	]:
		var path := route_network.get_node_or_null(path_name) as Polygon2D
		_expect(path != null, "Forest route network missing path: %s" % path_name)
		_expect(path == null or bool(path.visible), "Forest route path should be visible: %s" % path_name)
		if _has_failed:
			return

	for zone_name in [
		"ArrivalTrailZone",
		"QuietClearingZone",
		"ResourceCacheZone",
		"MikaMeetingZone",
		"ShrineFocusMarker",
		"ReturnFocusMarker",
	]:
		_expect(structure.get_node_or_null(zone_name) != null, "ForestStructure missing zone: %s" % zone_name)
		if _has_failed:
			return

	var spawn := forest.get_node_or_null("SpawnFromYard") as Node2D
	var return_gate := forest.get_node_or_null("BackToYard") as Node2D
	var shrine := forest.get_node_or_null("QuietShrine") as Node2D
	var fallen_branch := forest.get_node_or_null("FallenBranchBundle") as Node2D
	var flat_stone := forest.get_node_or_null("FlatStoneCache") as Node2D
	var mika := forest.get_node_or_null("NPCs/Mika") as Node2D
	for pair in {
		"SpawnFromYard": spawn,
		"BackToYard": return_gate,
		"QuietShrine": shrine,
		"FallenBranchBundle": fallen_branch,
		"FlatStoneCache": flat_stone,
		"NPCs/Mika": mika,
	}.keys():
		var node: Node = {
			"SpawnFromYard": spawn,
			"BackToYard": return_gate,
			"QuietShrine": shrine,
			"FallenBranchBundle": fallen_branch,
			"FlatStoneCache": flat_stone,
			"NPCs/Mika": mika,
		}[pair]
		_expect(node != null, "ForestEdge missing layout node: %s" % pair)
		if _has_failed:
			return

	_expect(spawn.position.distance_to(return_gate.position) <= 72.0, "Forest arrival should keep return path close and legible")
	_expect(shrine.position.x > return_gate.position.x + 180.0, "Quiet shrine should read as the far-side discovery point")
	_expect(fallen_branch.position.distance_to(flat_stone.position) <= 72.0, "Forest resources should read as one small cache")
	_expect(mika.position.distance_to(shrine.position) <= 96.0, "Mika meeting spot should stay near the forest discovery point")


func _set_first_week_before_forest(game_state: Node) -> void:
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_restored("old_well", true)
	game_state.set_flag("watered_first_crop_day1", true)
	game_state.set_flag("harvested_first_crop_day1", true)
	game_state.set_flag("shared_first_turnip_day1", true)
	game_state.set_flag("planted_aoi_strawberry_day1", true)
	game_state.set_restored("garden_bench", true)
	game_state.set_restored("village_sign", true)
	game_state.set_flag("heard_forest_edge_notice", true)
	game_state.set_flag("visited_forest_edge", false)
	game_state.set_flag("heard_npc_forest_edge", false)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


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
			_fail("ForestEdge gameplay layout validation timed out")
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
