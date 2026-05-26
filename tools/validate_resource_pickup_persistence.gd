extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DIALOGUE_BOX_PATH := "res://game/scenes/ui/DialogueBox.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: resource pickup persistence initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	var main := main_scene.instantiate()
	root.add_child(main)
	await _settle()

	await _validate_yard_pickups(main)
	if _has_failed:
		return
	await _validate_forest_pickups(main)
	if _has_failed:
		return
	await _validate_save_resume_claims(main)
	if _has_failed:
		return
	await _validate_dialogue_box_layout()
	if _has_failed:
		return

	print("OK: resource pickup persistence runtime validation passed")
	_finish_deferred(0)


func _validate_yard_pickups(main: Node) -> void:
	_expect(main.has_method("change_scene"), "Main should expose change_scene")
	main.change_scene("player_yard", "from_house")
	await _settle()
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "Main should enter player_yard")
	var yard: Node = main.get_current_gameplay_scene()
	await _collect_and_expect(main, yard, "WoodPile", "wood", 32, "resource_pickup_claimed_player_yard_wood_pile_day1")
	await _collect_and_expect(main, yard, "StonePile", "stone", 12, "resource_pickup_claimed_player_yard_stone_pile_day1")
	if _has_failed:
		return

	main.change_scene("forest_edge", "from_yard")
	await _settle()
	main.change_scene("player_yard", "from_forest_edge")
	await _settle()
	var returned_yard: Node = main.get_current_gameplay_scene()
	await _assert_claimed_pickup_does_not_add(main, returned_yard, "WoodPile", "wood", "yard wood pile should stay claimed after scene return")
	await _assert_claimed_pickup_does_not_add(main, returned_yard, "StonePile", "stone", "yard stone pile should stay claimed after scene return")


func _validate_forest_pickups(main: Node) -> void:
	main.change_scene("forest_edge", "from_yard")
	await _settle()
	_expect(String(main.get_current_gameplay_scene_id()) == "forest_edge", "Main should enter forest_edge")
	var forest: Node = main.get_current_gameplay_scene()
	await _collect_and_expect(main, forest, "FallenBranchBundle", "wood", 18, "resource_pickup_claimed_forest_edge_fallen_branch_bundle_day1")
	await _collect_and_expect(main, forest, "FlatStoneCache", "stone", 8, "resource_pickup_claimed_forest_edge_flat_stone_cache_day1")
	if _has_failed:
		return

	main.change_scene("player_yard", "from_forest_edge")
	await _settle()
	main.change_scene("forest_edge", "from_yard")
	await _settle()
	var returned_forest: Node = main.get_current_gameplay_scene()
	await _assert_claimed_pickup_does_not_add(main, returned_forest, "FallenBranchBundle", "wood", "forest wood bundle should stay claimed after scene return")
	await _assert_claimed_pickup_does_not_add(main, returned_forest, "FlatStoneCache", "stone", "forest stone cache should stay claimed after scene return")


func _validate_save_resume_claims(main: Node) -> void:
	var data: Dictionary = main.build_main_flow_save_data()
	main.queue_free()
	await _settle()

	var main_scene := load(MAIN_PATH) as PackedScene
	var fresh_main := main_scene.instantiate()
	root.add_child(fresh_main)
	await _settle()
	_expect(fresh_main.has_method("apply_main_flow_save_data"), "Fresh Main should accept main-flow save data")
	fresh_main.apply_main_flow_save_data(data)
	await _settle()
	_expect(String(fresh_main.get_current_gameplay_scene_id()) == "forest_edge", "Fresh Main should resume the saved forest scene")
	await _assert_claimed_pickup_does_not_add(fresh_main, fresh_main.get_current_gameplay_scene(), "FallenBranchBundle", "wood", "fresh forest wood bundle should stay claimed after save resume")
	await _assert_claimed_pickup_does_not_add(fresh_main, fresh_main.get_current_gameplay_scene(), "FlatStoneCache", "stone", "fresh forest stone cache should stay claimed after save resume")
	if _has_failed:
		return
	fresh_main.change_scene("player_yard", "from_forest_edge")
	await _settle()
	await _assert_claimed_pickup_does_not_add(fresh_main, fresh_main.get_current_gameplay_scene(), "WoodPile", "wood", "fresh yard wood pile should stay claimed after save resume")
	await _assert_claimed_pickup_does_not_add(fresh_main, fresh_main.get_current_gameplay_scene(), "StonePile", "stone", "fresh yard stone pile should stay claimed after save resume")


func _validate_dialogue_box_layout() -> void:
	var dialogue_scene := load(DIALOGUE_BOX_PATH) as PackedScene
	_expect(dialogue_scene != null, "DialogueBox scene should load")
	if _has_failed:
		return
	var dialogue_box := dialogue_scene.instantiate()
	root.add_child(dialogue_box)
	await process_frame
	var panel := dialogue_box.get_node_or_null("Panel") as Control
	_expect(panel != null, "DialogueBox should include a Panel")
	if _has_failed:
		return
	_expect(panel.offset_top >= 580.0, "DialogueBox panel should sit at the bottom edge, not mid-screen")
	_expect(panel.offset_bottom <= 712.0, "DialogueBox panel should stay inside the 720p UI frame")
	_expect(panel.offset_right <= 640.0, "DialogueBox panel should leave the lower-middle playfield mostly clear")
	_expect((panel.offset_bottom - panel.offset_top) <= 132.0, "DialogueBox panel should be a compact feedback strip")
	dialogue_box.queue_free()
	await process_frame


func _collect_and_expect(main: Node, scene: Node, pickup_name: String, item_id: String, expected_gain: int, flag_id: String) -> void:
	var pickup := scene.get_node_or_null(pickup_name)
	var inventory := scene.get_node_or_null("InventoryManager")
	var player := scene.get_node_or_null("Player")
	_expect(pickup != null, "Missing pickup: %s" % pickup_name)
	_expect(inventory != null, "Scene should include InventoryManager for %s" % pickup_name)
	_expect(player != null, "Scene should include Player for %s" % pickup_name)
	if _has_failed:
		return
	var before := int(inventory.get_count(item_id))
	pickup.on_interact(player)
	await _settle()
	var after := int(inventory.get_count(item_id))
	_expect(after == before + expected_gain, "%s should add %s x%d once" % [pickup_name, item_id, expected_gain])
	_expect(not bool(pickup.visible), "%s should hide after pickup" % pickup_name)
	if pickup is Area2D:
		_expect(not bool((pickup as Area2D).monitoring), "%s should stop monitoring after pickup" % pickup_name)
	var shared_game_state := main.get_node_or_null("GameState")
	_expect(shared_game_state != null, "Main should expose shared GameState")
	_expect(bool(shared_game_state.get_flag(flag_id, false)), "Shared GameState should record pickup claim flag: %s" % flag_id)


func _assert_claimed_pickup_does_not_add(main: Node, scene: Node, pickup_name: String, item_id: String, message: String) -> void:
	var pickup := scene.get_node_or_null(pickup_name)
	var inventory := scene.get_node_or_null("InventoryManager")
	var player := scene.get_node_or_null("Player")
	_expect(pickup != null, "%s missing pickup node %s" % [message, pickup_name])
	_expect(inventory != null, "%s missing inventory" % message)
	_expect(player != null, "%s missing player" % message)
	if _has_failed:
		return
	_expect(not bool(pickup.visible), "%s: pickup should be hidden" % message)
	if pickup is Area2D:
		_expect(not bool((pickup as Area2D).monitoring), "%s: pickup should not monitor" % message)
	if _has_failed:
		return
	var before := int(inventory.get_count(item_id))
	pickup.on_interact(player)
	await _settle()
	var after := int(inventory.get_count(item_id))
	_expect(after == before, "%s: claimed pickup should not add more %s" % [message, item_id])


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
			_fail("Resource pickup persistence validation timed out")
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
