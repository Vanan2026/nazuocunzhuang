extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: village authored slice initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main := main_scene.instantiate()
	root.add_child(main)
	await _settle()
	main.change_scene("player_yard", "from_house")
	await _settle()

	var outdoor_before: Node = main.get_current_gameplay_scene()
	_expect(outdoor_before != null and outdoor_before.has_method("set_active_region"), "player_yard should load OutdoorWorld")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	main.change_scene("village", "default")
	await _settle()

	var outdoor: Node = main.get_current_gameplay_scene()
	_expect(outdoor == outdoor_before, "Main.change_scene(\"village\") should reuse the current OutdoorWorld instance")
	_expect(String(main.get_current_gameplay_scene_id()) == "village", "Main public scene id should be village")
	_expect(String(outdoor.call("get_active_region_id")) == "village", "OutdoorWorld active region should be village")
	_expect(_player_is_at_spawn(outdoor, "village_default"), "Player should land at the village default spawn")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	var section := outdoor.get_node_or_null("Village")
	_expect(section != null, "OutdoorWorld should compose the Village section")
	_expect(section.get_node_or_null("VillagePlazaZone") != null, "Village should include a readable plaza zone")
	_expect(section.get_node_or_null("VillageNotice") != null, "Village should include a notice interactable")
	_expect(section.get_node_or_null("SeedStallProxy") != null, "Village should include a seed-stall or shop proxy")
	_expect(section.get_node_or_null("OldMapleClue") != null, "Village should include one soft clue interactable")
	_expect(section.get_node_or_null("VillageReturnPath") != null, "Village should include a calm return path")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	var notice := section.get_node_or_null("VillageNotice")
	var player := outdoor.get_node_or_null("Player")
	notice.on_interact(player)
	await _settle()
	var scene_game_state := outdoor.get_node_or_null("GameState")
	var shared_game_state := main.get_node_or_null("GameState")
	_expect(_flag_is_set(scene_game_state, "read_village_notice_day1"), "VillageNotice should set read_village_notice_day1 on scene state")
	_expect(_flag_is_set(shared_game_state, "read_village_notice_day1"), "VillageNotice flag should sync back to Main shared state")

	var stall := section.get_node_or_null("SeedStallProxy")
	stall.on_interact(player)
	await process_frame
	_expect(_flag_is_set(scene_game_state, "visited_village_seed_stall_day1"), "SeedStallProxy should set a non-economy visit flag")

	var clue := section.get_node_or_null("OldMapleClue")
	clue.on_interact(player)
	await process_frame
	_expect(_flag_is_set(scene_game_state, "found_village_soft_clue_day1"), "OldMapleClue should set the soft clue flag")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	var schedule_director := outdoor.get_node_or_null("ScheduleDirector")
	var aoi := outdoor.get_node_or_null("NPCs/Aoi") as Node2D
	_expect(schedule_director != null, "OutdoorWorld should expose one ScheduleDirector")
	_expect(aoi != null, "OutdoorWorld should include Aoi in the shared NPC root")
	if schedule_director != null:
		schedule_director.apply_schedule("late_morning")
	await process_frame
	var assignment: Dictionary = schedule_director.get_current_assignment("aoi") if schedule_director != null else {}
	var village_bounds: Rect2 = outdoor.call("get_region_bounds", "village")
	_expect(String(assignment.get("scene_id", "")) == "village", "Aoi should have an explicit late_morning village assignment")
	_expect(aoi != null and bool(aoi.visible), "Aoi should be visible for the village schedule proof")
	_expect(aoi != null and village_bounds.has_point(aoi.global_position), "Aoi should stand inside village bounds")

	main.queue_free()
	await process_frame
	if _has_failed:
		return
	print("OK: village authored slice runtime validation passed")
	_finish_deferred(0)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _flag_is_set(game_state: Node, flag_id: String) -> bool:
	if game_state == null or not game_state.has_method("get_flag"):
		return false
	return bool(game_state.get_flag(flag_id, false))


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
			_fail("Village authored slice validation timed out")
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
