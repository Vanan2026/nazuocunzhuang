extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const WeeklyRhythmContext := preload("res://game/systems/daily/WeeklyRhythmContext.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: daily intent weekly rhythm initialize")
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

	await _validate_weekly_rhythm_context(main)
	if _has_failed:
		return
	await _validate_no_pressure_state_changes(main)
	if _has_failed:
		return

	print("OK: daily intent weekly rhythm runtime validation passed")
	_finish_deferred(0)


func _validate_weekly_rhythm_context(main: Node) -> void:
	var time_manager: Node = main.get_node_or_null("TimeManager")
	var game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	var journal: Node = main.get_node_or_null("QuestJournalUI")
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	_expect(time_manager != null and game_state != null and quest_manager != null and scene_router != null, "Main should expose weekly rhythm managers")
	_expect(journal == null and chip != null, "Main should retire journal and keep chip")
	if _has_failed:
		return

	_mark_first_week_complete(game_state, scene_router, quest_manager)
	_apply_day(time_manager, 8)
	await _settle()

	var house: Node = main.get_current_gameplay_scene()
	var panel: Node = house.get_node_or_null("DailyIntentPanel") if house != null else null
	_expect(panel != null, "PlayerHouse should expose DailyIntentPanel")
	if _has_failed:
		return

	var rhythm := WeeklyRhythmContext.get_rhythm_for_day(time_manager)
	_expect(String(rhythm.get("label", "")) == "修整日", "Day 8 should repeat the first weekly rhythm label")
	_expect(String(panel.get_weekly_rhythm_status_text()).contains("修整日"), "Planner weekly status should expose day rhythm")
	_expect(String(panel.get_weekly_rhythm_status_text()).contains("节奏"), "Planner weekly status should frame rhythm as guidance")

	chip.refresh()
	await _settle()
	_expect(String(chip.get_current_hint_text()).contains("修整日"), "Post-first-week chip should include weekly rhythm when no intent is selected")

	game_state.set_daily_intent("day_8", "visit_neighbor")
	chip.refresh()
	await _settle()
	_expect(String(chip.get_current_hint_text()).contains("修整日"), "Selected daily intent chip hint should keep weekly rhythm context")

	_apply_day(time_manager, 9)
	chip.refresh()
	await _settle()
	_expect(String(chip.get_current_hint_text()).contains("村口日"), "Day 9 should advance the chip to the second weekly rhythm")


func _validate_no_pressure_state_changes(main: Node) -> void:
	var game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var inventory: Node = main.get_node_or_null("InventoryManager")
	var time_manager: Node = main.get_node_or_null("TimeManager")
	var journal: Node = main.get_node_or_null("QuestJournalUI")
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	_expect(game_state != null and quest_manager != null and inventory != null and time_manager != null, "Main should expose state managers for no-pressure check")
	_expect(journal == null and chip != null, "Main should retire journal and keep chip for no-pressure check")
	if _has_failed:
		return

	var completed_count_before := int(quest_manager.get_first_week_progress().get("completed_count", 0))
	var money_before := int(game_state.get_player_money())
	var energy_before := int(game_state.get_player_energy())
	var seed_count_before := int(inventory.get_count("seed_turnip"))

	_apply_day(time_manager, 10)
	chip.refresh()
	WeeklyRhythmContext.build_planner_status("", time_manager)
	WeeklyRhythmContext.build_chip_hint("", time_manager)
	await _settle()

	_expect(int(quest_manager.get_first_week_progress().get("completed_count", 0)) == completed_count_before, "Weekly rhythm should not change quest completion")
	_expect(int(game_state.get_player_money()) == money_before, "Weekly rhythm should not change money")
	_expect(int(game_state.get_player_energy()) == energy_before, "Weekly rhythm should not change energy")
	_expect(int(inventory.get_count("seed_turnip")) == seed_count_before, "Weekly rhythm should not grant or consume items")


func _apply_day(time_manager: Node, total_day: int) -> void:
	time_manager.apply_save_data({
		"year": 1,
		"season": "spring",
		"season_index": 0,
		"day_of_season": total_day,
		"total_day": total_day,
		"hour": 6,
		"minute": 0,
	})


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
			_fail("Daily intent weekly rhythm validation timed out")
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
