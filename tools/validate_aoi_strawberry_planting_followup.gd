extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Aoi strawberry planting follow-up initialize")
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

	var yard: Node = main.get_current_gameplay_scene()
	var shared_game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	var hud: Node = main.get_node_or_null("FirstWeekQuestHUD")
	_expect(yard != null and yard.name == "PlayerYard", "Main should load PlayerYard")
	_expect(shared_game_state != null, "Main should expose shared GameState")
	_expect(quest_manager != null, "Main should expose QuestManager")
	_expect(scene_router != null, "Main should expose SceneRouter")
	_expect(chip != null, "Main should include CurrentObjectiveChip")
	_expect(hud != null, "Main should include FirstWeekQuestHUD")
	_expect(main.get_node_or_null("QuestJournalUI") == null, "Main should not remount retired QuestJournalUI")
	_expect(not InputMap.has_action("open_journal"), "open_journal input action should stay retired")
	if _has_failed:
		return

	var local_game_state: Node = yard.get_node_or_null("GameState")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	var plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot1")
	_expect(local_game_state != null, "Yard should include local GameState")
	_expect(inventory != null, "Yard should include InventoryManager")
	_expect(plot != null, "PlayerYard should include second farm plot")
	if _has_failed:
		return

	_set_pre_strawberry_flags(local_game_state)
	main.sync_current_scene_state()
	quest_manager.update_first_week_progress(shared_game_state, scene_router)
	chip.refresh()
	hud.refresh()

	_expect(String(quest_manager.get_current_first_week_objective_id()) == "planted_aoi_strawberry_day1", "After Aoi share, objective should guide planting her strawberry seed")
	_expect(String(chip.get_progress_text()).contains("6 / 13"), "Objective chip should use 13-step first-week chain after Aoi share")
	_expect(not String(chip.get_current_hint_text()).is_empty(), "Objective chip should carry the second-plot follow-up hint")
	_expect(_contains_text(hud.get_visible_objective_texts(), "草莓") or _contains_text(hud.get_visible_objective_texts(), "strawberry"), "HUD should include the strawberry planting objective")
	if _has_failed:
		return

	inventory.add_item("seed_strawberry", 1)
	_expect(inventory.set_selected_item("seed_strawberry"), "Player should be able to select Aoi's strawberry seed")
	_expect(plot.till(), "Second farm plot should till")
	_expect(plot.plant_seed("seed_strawberry"), "Second farm plot should plant the strawberry seed")
	_expect(String(plot.get("crop_id")) == "strawberry_spring", "Second farm plot should resolve seed_strawberry to strawberry_spring")
	_expect(plot.water(), "Second farm plot should water the strawberry seed")
	await _settle()

	_expect(bool(local_game_state.get_flag("planted_aoi_strawberry_day1", false)), "Planting and watering Aoi's strawberry should set the local follow-up flag")
	_expect(String(inventory.get_selected_item_id()).is_empty(), "Completing strawberry planting follow-up should clear selected seed")
	main.sync_current_scene_state()
	_expect(bool(shared_game_state.get_flag("planted_aoi_strawberry_day1", false)), "Aoi strawberry planting flag should sync to shared GameState")
	quest_manager.update_first_week_progress(shared_game_state, scene_router)
	_expect(String(quest_manager.get_current_first_week_objective_id()) == "garden_bench_restored", "After planting Aoi's strawberry, objective should advance to bench repair")
	if _has_failed:
		return

	print("OK: aoi strawberry planting follow-up runtime validation passed")
	_finish_deferred(0)


func _set_pre_strawberry_flags(game_state: Node) -> void:
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_restored("old_well", true)
	game_state.set_flag("watered_first_crop_day1", true)
	game_state.set_flag("harvested_first_crop_day1", true)
	game_state.set_flag("shared_first_turnip_day1", true)
	game_state.set_flag("planted_aoi_strawberry_day1", false)


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
			_fail("Aoi strawberry planting follow-up validation timed out")
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
