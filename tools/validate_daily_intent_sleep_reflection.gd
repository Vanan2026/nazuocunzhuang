extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 35.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: daily intent sleep reflection initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	await _validate_no_reflection_before_first_week_complete()
	if _has_failed:
		return
	await _validate_post_week_reflection_after_sleep()
	if _has_failed:
		return
	await _validate_crop_feedback_keeps_first_line()
	if _has_failed:
		return

	print("OK: daily intent sleep reflection runtime validation passed")
	_finish_deferred(0)


func _validate_no_reflection_before_first_week_complete() -> void:
	var main: Node = await _instantiate_main()
	if _has_failed:
		return
	await _select_daily_intent(main, "visit_neighbor")
	var house: Node = main.get_current_gameplay_scene()
	var bed: Node = house.get_node_or_null("Bed") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	_expect(bed != null and dialogue_box != null, "PlayerHouse should expose bed and DialogueBox")
	if _has_failed:
		return
	if dialogue_box.has_method("close"):
		dialogue_box.close()
	bed.on_interact(house.get_node_or_null("Player"))
	await _settle()
	_expect(not bool(dialogue_box.visible), "Daily intent sleep reflection should not show before first-week completion")
	main.queue_free()


func _validate_post_week_reflection_after_sleep() -> void:
	var main: Node = await _instantiate_main()
	if _has_failed:
		return
	_mark_first_week_complete(main)
	await _select_daily_intent(main, "check_village_notice")
	var house: Node = main.get_current_gameplay_scene()
	var bed: Node = house.get_node_or_null("Bed") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var game_state: Node = main.get_node_or_null("GameState")
	var inventory: Node = main.get_node_or_null("InventoryManager")
	var time_manager: Node = main.get_node_or_null("TimeManager")
	_expect(bed != null and dialogue_box != null and quest_manager != null and game_state != null and inventory != null and time_manager != null, "Main should expose sleep reflection dependencies")
	if _has_failed:
		return

	var completed_count_before := int(quest_manager.get_first_week_progress().get("completed_count", 0))
	var money_before := int(game_state.get_player_money())
	var energy_before := int(game_state.get_player_energy())
	var seed_count_before := int(inventory.get_count("seed_turnip"))
	var total_day_before := int(time_manager.get_date_info().get("total_day", 1))
	if dialogue_box.has_method("close"):
		dialogue_box.close()

	bed.on_interact(house.get_node_or_null("Player"))
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(bool(dialogue_box.visible), "Post-first-week sleep should show a daily reflection")
	_expect(String(dialogue.get("dialogue_id", "")) == "daily_intent_sleep_reflection", "Reflection-only sleep should use daily_intent_sleep_reflection dialogue")
	_expect(_dialogue_contains(dialogue, "睡前想起"), "Reflection should read as a soft bedtime recollection")
	_expect(_dialogue_contains(dialogue, "村口"), "Reflection should mention the selected village-notice direction")
	_expect(int(time_manager.get_date_info().get("total_day", 1)) == total_day_before + 1, "Persistent TimeManager should advance after scene sleep")
	_expect(int(quest_manager.get_first_week_progress().get("completed_count", 0)) == completed_count_before, "Sleep reflection should not alter first-week quest completion")
	_expect(int(game_state.get_player_money()) == money_before, "Sleep reflection should not change money")
	_expect(int(game_state.get_player_energy()) == energy_before, "Sleep reflection should not change energy")
	_expect(int(inventory.get_count("seed_turnip")) == seed_count_before, "Sleep reflection should not grant or consume items")
	main.queue_free()


func _validate_crop_feedback_keeps_first_line() -> void:
	var main: Node = await _instantiate_main()
	if _has_failed:
		return
	_mark_first_week_complete(main)
	await _select_daily_intent(main, "tend_crops")
	await _prepare_watered_crop(main)
	if _has_failed:
		return
	var house: Node = main.get_current_gameplay_scene()
	var bed: Node = house.get_node_or_null("Bed") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	_expect(bed != null and dialogue_box != null, "PlayerHouse should expose bed and DialogueBox for crop/reflection sleep")
	if _has_failed:
		return
	if dialogue_box.has_method("close"):
		dialogue_box.close()
	bed.on_interact(house.get_node_or_null("Player"))
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	var line_label := dialogue_box.get_node_or_null("Panel/Content/TextColumn/LineLabel") as Label
	_expect(String(dialogue.get("dialogue_id", "")) == "crop_status_sleep", "Crop plus reflection sleep should keep crop_status_sleep dialogue id")
	_expect(line_label != null and line_label.text.contains("菜地"), "Crop feedback should remain the first visible sleep line")
	_expect(dialogue.get("lines", []).size() >= 2, "Crop plus reflection sleep should include a second reflection line")
	_expect(_dialogue_contains(dialogue, "睡前想起"), "Crop plus reflection sleep should preserve the daily reflection as an additional line")
	main.queue_free()


func _instantiate_main() -> Node:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return null
	var main: Node = main_scene.instantiate()
	root.add_child(main)
	await _settle()
	return main


func _select_daily_intent(main: Node, intent_id: String) -> void:
	var house: Node = main.get_current_gameplay_scene()
	var planner: Node = house.get_node_or_null("IntentDesk") if house != null else null
	var panel: Node = house.get_node_or_null("DailyIntentPanel") if house != null else null
	var player: Node = house.get_node_or_null("Player") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	_expect(planner != null and panel != null and player != null and dialogue_box != null, "PlayerHouse should expose daily intent planner")
	if _has_failed:
		return
	planner.on_interact(player)
	await _settle()
	_expect(bool(panel.select_intent(intent_id)), "Daily intent should be selectable: %s" % intent_id)
	await _settle()
	if dialogue_box.has_method("close"):
		dialogue_box.close()


func _prepare_watered_crop(main: Node) -> void:
	main.change_scene("player_yard", "from_house")
	await _settle()
	var yard: Node = main.get_current_gameplay_scene()
	var farm_plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot0") if yard != null else null
	var inventory: Node = yard.get_node_or_null("InventoryManager") if yard != null else null
	var game_state: Node = yard.get_node_or_null("GameState") if yard != null else null
	var house_return: Node = yard.get_node_or_null("HouseDoor") if yard != null else null
	_expect(farm_plot != null and inventory != null and game_state != null and house_return != null, "Yard should expose crop setup nodes")
	if _has_failed:
		return
	game_state.set_restored("old_well", true)
	inventory.add_item("seed_turnip", 1)
	inventory.set_selected_item("seed_turnip")
	_expect(farm_plot.till(), "FarmPlot0 should till")
	_expect(farm_plot.plant_seed("seed_turnip"), "FarmPlot0 should plant")
	_expect(farm_plot.water(), "FarmPlot0 should water")
	if _has_failed:
		return
	main.sync_current_scene_state()
	await process_frame
	house_return.on_interact(yard.get_node_or_null("Player"))
	await _settle()
	_expect(String(main.get_current_gameplay_scene_id()) == "player_house", "HouseDoor should return to PlayerHouse")


func _mark_first_week_complete(main: Node) -> void:
	var game_state := main.get_node_or_null("GameState")
	var scene_router := main.get_node_or_null("SceneRouter")
	var quest_manager := main.get_node_or_null("QuestManager")
	_expect(game_state != null and scene_router != null and quest_manager != null, "Main should expose first-week completion managers")
	if _has_failed:
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


func _dialogue_contains(dialogue: Dictionary, needle: String) -> bool:
	for line in dialogue.get("lines", []):
		if String(line.get("text", "")).contains(needle):
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
			_fail("Daily intent sleep reflection validation timed out")
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
