extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: first-week harvest guidance initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene: PackedScene = load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return
	var main: Node = main_scene.instantiate()
	root.add_child(main)
	await _settle()
	main.change_scene("player_yard", "from_house")
	await _settle()

	var shared_game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	var hud: Node = main.get_node_or_null("FirstWeekQuestHUD")
	_expect(shared_game_state != null, "Main should expose GameState")
	_expect(quest_manager != null, "Main should expose QuestManager")
	_expect(scene_router != null, "Main should expose SceneRouter")
	_expect(chip != null, "Main should include CurrentObjectiveChip")
	_expect(hud != null, "Main should include FirstWeekQuestHUD")
	_expect(main.get_node_or_null("QuestJournalUI") == null, "Main should not remount retired QuestJournalUI")
	_expect(not InputMap.has_action("open_journal"), "open_journal input action should stay retired")
	if _has_failed:
		return

	shared_game_state.set_flag("read_mailbox_day1", true)
	shared_game_state.set_flag("read_bulletin_day1", true)
	shared_game_state.set_restored("old_well", true)
	shared_game_state.set_flag("watered_first_crop_day1", true)
	quest_manager.update_first_week_progress(shared_game_state, scene_router)
	chip.refresh()
	hud.refresh()

	_expect(String(quest_manager.get_current_first_week_objective_id()) == "harvested_first_crop_day1", "After watering, next objective should guide first crop harvest")
	_expect(String(chip.get_current_goal_text()).contains("收获"), "Objective chip should mention harvest")
	_expect(not String(chip.get_current_hint_text()).is_empty(), "Objective chip should explain repeated watering and maturity")
	_expect(String(chip.get_progress_text()).contains("4 / 13"), "Objective chip should use 13-step first-week chain")
	_expect(_contains_text(hud.get_visible_objective_texts(), "收获"), "HUD should list first crop harvest objective")
	if _has_failed:
		return

	var yard: Node = main.get_current_gameplay_scene()
	var local_game_state: Node = yard.get_node_or_null("GameState")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	var farm_plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot0")
	_expect(local_game_state != null, "Yard should include local GameState")
	_expect(inventory != null, "Yard should include InventoryManager")
	_expect(farm_plot != null, "Yard should include FarmPlot0")
	if _has_failed:
		return

	local_game_state.set_flag("read_mailbox_day1", true)
	local_game_state.set_flag("read_bulletin_day1", true)
	local_game_state.set_restored("old_well", true)
	local_game_state.set_flag("watered_first_crop_day1", true)
	inventory.add_item("seed_turnip", 1)
	_expect(farm_plot.till(), "FarmPlot0 should till")
	_expect(farm_plot.plant_seed("seed_turnip"), "FarmPlot0 should plant")
	_expect(farm_plot.water(), "FarmPlot0 should water")
	for _day in range(2):
		farm_plot.advance_day(false)
		if String(farm_plot.get_state_name()) != "ready":
			_expect(farm_plot.water(), "FarmPlot0 should be waterable until ready")
	if _has_failed:
		return
	_expect(String(farm_plot.get_state_name()) == "ready", "FarmPlot0 should become ready")
	_expect(farm_plot.harvest(), "FarmPlot0 should harvest")
	await _settle()
	_expect(bool(shared_game_state.get_flag("harvested_first_crop_day1", false)), "Harvesting first crop should persist first-week harvest flag")
	quest_manager.update_first_week_progress(shared_game_state, scene_router)
	_expect(String(quest_manager.get_current_first_week_objective_id()) == "shared_first_turnip_day1", "After harvest, objective should advance to first turnip sharing")
	if _has_failed:
		return

	print("OK: first-week harvest guidance runtime validation passed")
	_finish_deferred(0)


func _contains_text(texts: Array[String], needle: String) -> bool:
	for text in texts:
		if text.contains(needle):
			return true
	return false


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
			_fail("First-week harvest guidance validation timed out")
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
