extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: village return hook initialize")
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
	_expect(outdoor == outdoor_before, "village should reuse OutdoorWorld before return hook")
	_expect(String(outdoor.call("get_active_region_id")) == "village", "OutdoorWorld should activate village")
	var section := outdoor.get_node_or_null("Village")
	var player := outdoor.get_node_or_null("Player")
	_expect(section != null, "Village section should exist")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	section.get_node("VillageNotice").on_interact(player)
	await _settle()
	section.get_node("SeedStallProxy").on_interact(player)
	await process_frame
	section.get_node("OldMapleClue").on_interact(player)
	await process_frame

	var scene_game_state := outdoor.get_node_or_null("GameState")
	_expect(_flag_is_set(scene_game_state, "found_village_soft_clue_day1"), "OldMapleClue should set the soft clue flag before returning")
	if scene_game_state != null and scene_game_state.has_method("set_restored"):
		scene_game_state.set_restored("old_well", true)
	await process_frame

	section.get_node("VillageReturnPath").on_interact(player)
	await _settle()
	outdoor = main.get_current_gameplay_scene()
	_expect(outdoor == outdoor_before, "returning from village should keep the same OutdoorWorld instance")
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "VillageReturnPath should route back to player_yard")
	_expect(String(outdoor.call("get_active_region_id")) == "player_yard", "VillageReturnPath should reactivate player_yard")
	scene_game_state = outdoor.get_node_or_null("GameState")
	var shared_game_state := main.get_node_or_null("GameState")
	_expect(_flag_is_set(scene_game_state, "returned_from_village_day1"), "VillageReturnPath should set returned_from_village_day1 on scene state")
	_expect(_flag_is_set(shared_game_state, "returned_from_village_day1"), "VillageReturnPath should sync return flag to Main")

	var old_well := outdoor.get_node_or_null("OldWell")
	_expect(old_well != null, "PlayerYard should expose OldWell for the return hook")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	old_well.on_interact(player)
	await _settle()
	_expect(_flag_is_set(scene_game_state, "heard_old_well_echo_after_village_clue_day1"), "OldWell should set the village clue echo flag after return")
	_expect(_flag_is_set(shared_game_state, "heard_old_well_echo_after_village_clue_day1"), "OldWell echo flag should sync to Main shared state")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	var dialogue_box := outdoor.get_node_or_null("DialogueBox")
	_expect(dialogue_box != null, "OutdoorWorld should expose DialogueBox for return-hook feedback")
	if dialogue_box != null:
		var current_dialogue: Dictionary = dialogue_box.get("dialogue")
		_expect(String(current_dialogue.get("dialogue_id", "")) == "village_clue_old_well_echo", "OldWell return hook should show its own feedback dialogue")

	main.queue_free()
	await process_frame
	if _has_failed:
		return
	print("OK: village return hook runtime validation passed")
	_finish_deferred(0)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _flag_is_set(game_state: Node, flag_id: String) -> bool:
	if game_state == null or not game_state.has_method("get_flag"):
		return false
	return bool(game_state.get_flag(flag_id, false))


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
			_fail("Village return hook validation timed out")
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
