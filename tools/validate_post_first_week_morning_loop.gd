extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: post-first-week morning loop initialize")
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

	_validate_first_week_still_owns_chip_before_completion(main)
	if _has_failed:
		return
	_validate_completed_week_prompts_daily_direction(main)
	if _has_failed:
		return
	await _validate_selected_intent_drives_chip(main)
	if _has_failed:
		return
	_validate_next_day_resets_daily_direction_prompt(main)
	if _has_failed:
		return

	print("OK: post-first-week morning loop runtime validation passed")
	_finish_deferred(0)


func _validate_first_week_still_owns_chip_before_completion(main: Node) -> void:
	var chip := main.get_node_or_null("CurrentObjectiveChip")
	var game_state := main.get_node_or_null("GameState")
	_expect(chip != null and game_state != null, "Main should expose chip and GameState")
	if _has_failed:
		return
	game_state.set_daily_intent("day_1", "tend_crops")
	chip.refresh()
	_expect(String(chip.get_current_goal_text()).contains("读邮箱"), "Before first-week completion, current objective should stay on first-week flow")
	_expect(String(chip.get_progress_text()).contains("0 / 13"), "Before first-week completion, progress should remain first-week progress")


func _validate_completed_week_prompts_daily_direction(main: Node) -> void:
	var quest_manager := main.get_node_or_null("QuestManager")
	var game_state := main.get_node_or_null("GameState")
	var scene_router := main.get_node_or_null("SceneRouter")
	var time_manager := main.get_node_or_null("TimeManager")
	var chip := main.get_node_or_null("CurrentObjectiveChip")
	_expect(quest_manager != null and game_state != null and scene_router != null and time_manager != null and chip != null, "Main should expose quest, state, router, time, and chip")
	if _has_failed:
		return
	time_manager.start_next_day()
	_mark_first_week_complete(game_state, scene_router)
	quest_manager.update_first_week_progress(game_state, scene_router)
	chip.refresh()
	_expect(bool(quest_manager.is_first_week_complete()), "First week should be complete for post-week loop")
	_expect(String(chip.get_current_goal_text()).contains("整理今日方向"), "Completed first week should prompt choosing a daily direction when none is selected today")
	_expect(String(chip.get_current_hint_text()).contains("晨间小桌"), "Completed first week prompt should point to the morning desk")
	_expect(String(chip.get_progress_text()) == "日常", "Completed first week chip should switch to daily-loop progress text")


func _validate_selected_intent_drives_chip(main: Node) -> void:
	var house: Node = main.get_current_gameplay_scene()
	var planner: Node = house.get_node_or_null("IntentDesk") if house != null else null
	var panel: Node = house.get_node_or_null("DailyIntentPanel") if house != null else null
	var player: Node = house.get_node_or_null("Player") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	var chip := main.get_node_or_null("CurrentObjectiveChip")
	var quest_manager := main.get_node_or_null("QuestManager")
	var game_state := main.get_node_or_null("GameState")
	var inventory := main.get_node_or_null("InventoryManager")
	_expect(planner != null and panel != null and player != null and dialogue_box != null and chip != null, "PlayerHouse should expose daily planner and chip")
	_expect(quest_manager != null and game_state != null and inventory != null, "Main should expose state managers")
	if _has_failed:
		return

	var completed_count_before := int(quest_manager.get_first_week_progress().get("completed_count", 0))
	var money_before := int(game_state.get_player_money())
	var energy_before := int(game_state.get_player_energy())
	var seed_count_before := int(inventory.get_count("seed_turnip"))

	planner.on_interact(player)
	await _settle()
	_expect(bool(panel.select_intent("check_village_notice")), "Daily planner should select village-notice intent")
	await _settle()
	if dialogue_box.has_method("close"):
		dialogue_box.close()
	chip.refresh()

	_expect(String(chip.get_current_goal_text()).contains("今日方向"), "Selected intent should turn chip into daily direction")
	_expect(String(chip.get_current_goal_text()).contains("村口"), "Selected village-notice intent should be visible on chip")
	_expect(String(chip.get_current_hint_text()).contains("公告"), "Selected intent hint should guide the chosen route softly")
	_expect(int(quest_manager.get_first_week_progress().get("completed_count", 0)) == completed_count_before, "Daily direction chip should not change quest completion")
	_expect(int(game_state.get_player_money()) == money_before, "Daily direction chip should not change money")
	_expect(int(game_state.get_player_energy()) == energy_before, "Daily direction chip should not change energy")
	_expect(int(inventory.get_count("seed_turnip")) == seed_count_before, "Daily direction chip should not grant or consume items")


func _validate_next_day_resets_daily_direction_prompt(main: Node) -> void:
	var time_manager := main.get_node_or_null("TimeManager")
	var chip := main.get_node_or_null("CurrentObjectiveChip")
	_expect(time_manager != null and chip != null, "Main should expose TimeManager and chip")
	if _has_failed:
		return
	time_manager.start_next_day()
	chip.refresh()
	_expect(String(chip.get_current_goal_text()).contains("整理今日方向"), "New day should ask for a fresh daily direction")
	_expect(not String(chip.get_current_goal_text()).contains("村口"), "New day should not carry yesterday's selected direction onto the chip")


func _mark_first_week_complete(game_state: Node, scene_router: Node) -> void:
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
			_fail("Post-first-week morning loop validation timed out")
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
