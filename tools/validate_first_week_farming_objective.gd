extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: first-week farming objective initialize")
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
	main.change_scene("player_yard", "from_house")
	await _settle()

	_validate_farming_objective_after_well(main)
	if _has_failed:
		return
	await _validate_watering_advances_objective(main)
	if _has_failed:
		return

	print("OK: first-week farming objective runtime validation passed")
	_finish_deferred(0)


func _validate_farming_objective_after_well(main: Node) -> void:
	var game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	_expect(game_state != null, "Main should expose shared GameState")
	_expect(quest_manager != null, "Main should expose QuestManager")
	_expect(scene_router != null, "Main should expose SceneRouter")
	_expect(chip != null, "Main should include CurrentObjectiveChip")
	if _has_failed:
		return

	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_restored("old_well", true)
	quest_manager.update_first_week_progress(game_state, scene_router)
	if chip.has_method("refresh"):
		chip.refresh()
	_expect(String(quest_manager.get_current_first_week_objective_id()) == "watered_first_crop_day1", "Current objective after old well should be first-crop watering")
	_expect(String(chip.get_current_goal_text()).contains("浇"), "Objective chip should mention watering after old well repair")
	_expect(String(chip.get_progress_text()).contains("3 / 13"), "Objective chip should show the expanded 13-step first-week chain")


func _validate_watering_advances_objective(main: Node) -> void:
	var yard: Node = main.get_current_gameplay_scene()
	var shared_game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	_expect(yard != null, "PlayerYard should be active")
	_expect(shared_game_state != null, "Main should expose shared GameState")
	_expect(quest_manager != null, "Main should expose QuestManager")
	_expect(scene_router != null, "Main should expose SceneRouter")
	if _has_failed:
		return
	yard = main.get_current_gameplay_scene()
	var plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot0")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	var local_game_state: Node = yard.get_node_or_null("GameState")
	_expect(plot != null, "PlayerYard should include FarmPlot0")
	_expect(inventory != null, "PlayerYard should include InventoryManager")
	_expect(local_game_state != null, "PlayerYard should include local GameState mirror")
	if _has_failed:
		return

	local_game_state.set_flag("read_mailbox_day1", true)
	local_game_state.set_flag("read_bulletin_day1", true)
	local_game_state.set_restored("old_well", true)
	if inventory.has_method("add_item"):
		inventory.add_item("seed_turnip", 1)
	if inventory.has_method("set_selected_item"):
		inventory.set_selected_item("seed_turnip")
	_expect(plot.till(), "FarmPlot0 should till from empty state")
	_expect(plot.plant_seed("seed_turnip"), "FarmPlot0 should plant a turnip seed")
	_expect(plot.water(), "FarmPlot0 should water the planted seed")
	await _settle()

	_expect(String(inventory.get_selected_item_id()).is_empty(), "Watering the first crop should clear selected seed to avoid accidental gifts")
	_expect(bool(shared_game_state.get_flag("watered_first_crop_day1", false)), "Watering the first crop after old well repair should persist a first-week flag")
	quest_manager.update_first_week_progress(shared_game_state, scene_router)
	_expect(String(quest_manager.get_current_first_week_objective_id()) == "harvested_first_crop_day1", "Current objective should advance to first crop harvest after watering")


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
			_fail("First-week farming objective validation timed out")
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
