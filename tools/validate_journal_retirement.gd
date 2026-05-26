extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: player-facing journal retirement initialize")
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

	_validate_no_player_facing_journal(main)
	if _has_failed:
		return
	await _validate_soft_guidance_surfaces_remain(main)
	if _has_failed:
		return

	print("OK: player-facing journal retirement runtime validation passed")
	_finish_deferred(0)


func _validate_no_player_facing_journal(main: Node) -> void:
	_expect(not InputMap.has_action("open_journal"), "open_journal input action should be retired")
	_expect(main.get_node_or_null("QuestJournalUI") == null, "Main should not mount QuestJournalUI")
	_expect(main.find_child("QuestJournalUI", true, false) == null, "Runtime tree should not expose a player-facing QuestJournalUI")


func _validate_soft_guidance_surfaces_remain(main: Node) -> void:
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	var game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	var time_manager: Node = main.get_node_or_null("TimeManager")
	_expect(chip != null and game_state != null and quest_manager != null and scene_router != null and time_manager != null, "Main should keep soft guidance managers and chip")
	if _has_failed:
		return

	_mark_first_week_complete(game_state, scene_router, quest_manager)
	time_manager.apply_save_data({
		"year": 1,
		"season": "spring",
		"season_index": 0,
		"day_of_season": 8,
		"total_day": 8,
		"hour": 6,
		"minute": 0,
	})
	chip.refresh()
	await _settle()
	var no_intent_hint := String(chip.get_current_hint_text())
	_expect(no_intent_hint.contains("晨间小桌"), "Post-week chip should point to the diegetic morning desk")
	_expect(no_intent_hint.contains("修整日"), "Post-week chip should retain weekly rhythm without the journal UI")
	_expect(not no_intent_hint.contains("手账"), "Post-week chip should not tell the player to use a hand-journal")

	game_state.set_daily_intent("day_8", "visit_neighbor")
	chip.refresh()
	await _settle()
	var selected_hint := String(chip.get_current_hint_text())
	_expect(selected_hint.contains("修整日"), "Selected daily direction should keep weekly rhythm context")
	_expect(not selected_hint.contains("手账"), "Selected daily direction should not mention a hand-journal")


func _mark_first_week_complete(game_state: Node, scene_router: Node, quest_manager: Node) -> void:
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
			_fail("Player-facing journal retirement validation timed out")
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
