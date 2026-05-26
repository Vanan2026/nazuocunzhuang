extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: retired daily intent journal follow-up initialize")
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

	var journal: Node = main.get_node_or_null("QuestJournalUI")
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	var game_state: Node = main.get_node_or_null("GameState")
	var time_manager: Node = main.get_node_or_null("TimeManager")
	_expect(journal == null, "Daily intent journal follow-up should stay retired from Main")
	_expect(chip != null and game_state != null and time_manager != null, "Main should keep chip/state/time for daily intent follow-up")
	if _has_failed:
		return

	time_manager.apply_save_data({
		"year": 1,
		"season": "spring",
		"season_index": 0,
		"day_of_season": 8,
		"total_day": 8,
		"hour": 6,
		"minute": 0,
	})
	_mark_first_week_complete(main)
	game_state.set_daily_intent("day_8", "check_village_notice")
	chip.refresh()
	await _settle()
	_expect(String(chip.get_current_hint_text()).contains("公告"), "Daily intent follow-up should remain visible through the chip/world direction")
	_expect(not String(chip.get_current_hint_text()).contains("手账"), "Daily intent follow-up should not mention hand-journal")
	if _has_failed:
		return

	print("OK: retired daily intent journal follow-up validation passed")
	_finish_deferred(0)


func _mark_first_week_complete(main: Node) -> void:
	var game_state: Node = main.get_node_or_null("GameState")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	if game_state == null or scene_router == null or quest_manager == null:
		_fail("Main should expose completion managers")
		return
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_flag("watered_first_crop_day1", true)
	game_state.set_flag("harvested_first_crop_day1", true)
	game_state.set_flag("shared_first_turnip_day1", true)
	game_state.set_flag("planted_aoi_strawberry_day1", true)
	game_state.set_flag("heard_forest_edge_notice", true)
	game_state.set_flag("visited_forest_edge", true)
	game_state.set_flag("heard_npc_forest_edge", true)
	game_state.set_flag("read_village_notice_day1", true)
	game_state.set_restored("old_well", true)
	game_state.set_restored("garden_bench", true)
	game_state.set_restored("village_sign", true)
	scene_router.set_current_scene("forest_edge", "from_yard")
	quest_manager.update_first_week_progress(game_state, scene_router)


func _settle() -> void:
	await create_timer(0.1).timeout
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
			_fail("Retired daily intent journal follow-up validation timed out")
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
