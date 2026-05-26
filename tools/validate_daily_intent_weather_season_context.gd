extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: daily intent weather/season context initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main: Node = main_scene.instantiate()
	_expect(main.has_method("get_current_gameplay_scene"), "Main script should load and expose get_current_gameplay_scene")
	if _has_failed:
		return
	root.add_child(main)
	await _settle()

	await _validate_weather_and_season_context(main)
	if _has_failed:
		return

	print("OK: daily intent weather/season context runtime validation passed")
	_finish_deferred(0)


func _validate_weather_and_season_context(main: Node) -> void:
	var time_manager: Node = main.get_node_or_null("TimeManager")
	var weather_manager: Node = main.get_node_or_null("WeatherManager")
	var game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	var inventory: Node = main.get_node_or_null("InventoryManager")
	var journal: Node = main.get_node_or_null("QuestJournalUI")
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	_expect(time_manager != null and weather_manager != null and game_state != null, "Main should expose time/weather/state managers")
	_expect(quest_manager != null and scene_router != null and inventory != null, "Main should expose quest/router/inventory")
	_expect(journal == null and chip != null, "Main should retire journal and expose current objective chip")
	if _has_failed:
		return

	_mark_first_week_complete(game_state, scene_router, quest_manager)
	time_manager.apply_save_data({
		"year": 1,
		"season": "summer",
		"season_index": 1,
		"day_of_season": 3,
		"total_day": 3,
		"hour": 6,
		"minute": 0,
	})
	weather_manager.set_today_weather("rainy")
	weather_manager.set_tomorrow_weather("cloudy")
	await _settle()

	var house: Node = main.get_current_gameplay_scene()
	var panel: Node = house.get_node_or_null("DailyIntentPanel") if house != null else null
	var planner: Node = house.get_node_or_null("IntentDesk") if house != null else null
	var player: Node = house.get_node_or_null("Player") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	_expect(panel != null and planner != null and player != null and dialogue_box != null, "PlayerHouse should expose daily planner UI")
	if _has_failed:
		return

	var money_before := int(game_state.get_player_money())
	var energy_before := int(game_state.get_player_energy())
	var seed_count_before := int(inventory.get_count("seed_turnip"))
	var completed_count_before := int(quest_manager.get_first_week_progress().get("completed_count", 0))

	var preview_text := String(panel.get_intent_feedback_text("tend_crops"))
	_expect(preview_text.contains("雨"), "Planner feedback should react to rainy weather")
	_expect(preview_text.contains("夏天"), "Planner feedback should include summer season context")

	planner.on_interact(player)
	await _settle()
	_expect(bool(panel.select_intent("tend_crops")), "Daily planner should accept crop-care intent")
	await _settle()
	_expect(_dialogue_contains(dialogue_box.get("dialogue"), "雨"), "Immediate feedback should mention rainy weather")
	_expect(_dialogue_contains(dialogue_box.get("dialogue"), "夏天"), "Immediate feedback should mention summer context")
	if dialogue_box.has_method("close"):
		dialogue_box.close()

	chip.refresh()
	await _settle()
	var chip_hint := String(chip.get_current_hint_text())
	_expect(chip_hint.contains("雨"), "Current objective hint should include rainy context")
	_expect(chip_hint.contains("夏天"), "Current objective hint should include summer context")

	var bed: Node = house.get_node_or_null("Bed")
	_expect(bed != null, "PlayerHouse should expose Bed for sleep reflection")
	if _has_failed:
		return
	bed.on_interact(player)
	await _settle()
	var reflection_dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(_dialogue_contains(reflection_dialogue, "夏天"), "Sleep reflection should keep seasonal context")
	_expect(int(quest_manager.get_first_week_progress().get("completed_count", 0)) == completed_count_before, "Contextual daily intent should not change quest completion")
	_expect(int(game_state.get_player_money()) == money_before, "Contextual daily intent should not change money")
	_expect(int(game_state.get_player_energy()) == energy_before, "Contextual daily intent should not change energy")
	_expect(int(inventory.get_count("seed_turnip")) == seed_count_before, "Contextual daily intent should not grant or consume items")


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


func _dialogue_contains(dialogue: Dictionary, needle: String) -> bool:
	for line in dialogue.get("lines", []):
		if line is Dictionary and String(line.get("text", "")).contains(needle):
			return true
	return false


func _settle() -> void:
	await create_timer(0.12).timeout
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
			_fail("Daily intent weather/season context validation timed out")
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
