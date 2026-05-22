extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"
const TEST_SAVE_PATH := "user://task011_save_load_test.json"
const WATCHDOG_TIMEOUT_SECONDS := 20.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: task011 save/load initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	_remove_test_save()
	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	if yard_scene == null:
		_fail("could not load PlayerYard")
		return

	var yard := yard_scene.instantiate() as Node
	root.add_child(yard)
	await process_frame
	await process_frame

	var save_manager := yard.get_node_or_null("SaveManager")
	var time_manager := yard.get_node_or_null("TimeManager")
	var weather_manager := yard.get_node_or_null("WeatherManager")
	var inventory_manager := yard.get_node_or_null("InventoryManager")
	var relationship_manager := yard.get_node_or_null("RelationshipManager")
	var game_state := yard.get_node_or_null("GameState")
	var player := yard.get_node_or_null("Player")
	var farm_plot := yard.get_node_or_null("FarmPlots/FarmPlot0")

	_expect(save_manager != null, "PlayerYard should include SaveManager")
	_expect(time_manager != null, "PlayerYard should include TimeManager")
	_expect(weather_manager != null, "PlayerYard should include WeatherManager")
	_expect(inventory_manager != null, "PlayerYard should include InventoryManager")
	_expect(relationship_manager != null, "PlayerYard should include RelationshipManager")
	_expect(game_state != null, "PlayerYard should include GameState")
	_expect(player != null, "PlayerYard should include Player")
	_expect(farm_plot != null, "PlayerYard should include FarmPlot0")
	if _has_failed:
		return
	for method_name in ["build_runtime_save_data", "apply_runtime_save_data", "save_game", "load_game"]:
		if not save_manager.has_method(method_name):
			_fail("SaveManager missing method: %s" % method_name)
			return

	_seed_runtime_state(yard)
	var snapshot := save_manager.build_runtime_save_data(yard) as Dictionary
	_expect(snapshot.has("time"), "runtime save data should include time")
	_expect(snapshot.has("weather"), "runtime save data should include weather")
	_expect(snapshot.has("player"), "runtime save data should include player")
	_expect(snapshot.has("inventory"), "runtime save data should include inventory")
	_expect(snapshot.has("relationships"), "runtime save data should include relationships")
	_expect(snapshot.has("flags"), "runtime save data should include flags")
	_expect(snapshot.has("farm_plots"), "runtime save data should include farm_plots")
	_expect(snapshot.has("restoration_states"), "runtime save data should include restoration_states")
	if _has_failed:
		return

	_expect(bool(save_manager.save_game(yard, TEST_SAVE_PATH)), "save_game should return true")
	_expect(FileAccess.file_exists(TEST_SAVE_PATH), "save_game should write the save file")
	if _has_failed:
		return

	var saved_text := FileAccess.get_file_as_string(TEST_SAVE_PATH)
	var parsed: Variant = JSON.parse_string(saved_text)
	_expect(parsed is Dictionary, "save file should contain JSON object")
	var saved_data: Dictionary = parsed if parsed is Dictionary else {}
	_expect(String(saved_data.get("version", "")) == save_manager.SAVE_VERSION, "save file should include save version")
	_expect(int(saved_data.get("time", {}).get("year", 0)) == 2, "save file should include mutated year")
	_expect(String(saved_data.get("weather", {}).get("today", "")) == "rainy", "save file should include weather")
	_expect(int(saved_data.get("inventory", {}).get("items", {}).get("wood", 0)) == 24, "save file should include inventory")
	_expect(bool(saved_data.get("flags", {}).get("yard_water_source", false)), "save file should include flags")
	_expect(bool(saved_data.get("restoration_states", {}).get("old_well", false)), "save file should include restoration state")
	if _has_failed:
		return

	_clear_runtime_state(yard)
	_expect(bool(save_manager.load_game(yard, TEST_SAVE_PATH)), "load_game should return true")
	await process_frame

	_expect(int(time_manager.year) == 2, "load should restore year")
	_expect(int(time_manager.season_index) == 2, "load should restore season index")
	_expect(int(time_manager.day_of_season) == 8, "load should restore day")
	_expect(int(time_manager.hour) == 18, "load should restore hour")
	_expect(String(weather_manager.get_today_weather()) == "rainy", "load should restore today weather")
	_expect(String(weather_manager.get_tomorrow_weather()) == "sunny", "load should restore tomorrow weather")
	_expect(int(inventory_manager.get_count("wood")) == 24, "load should restore inventory count")
	_expect(String(inventory_manager.get_selected_item_id()) == "wood", "load should restore selected item")
	_expect(int(relationship_manager.get_relationship("aoi")) == 7, "load should restore relationship")
	_expect(bool(relationship_manager.has_talked_today("aoi")), "load should restore talked_today")
	_expect(bool(relationship_manager.has_gifted_today("mika")), "load should restore gifted_today")
	_expect(bool(game_state.get_flag("yard_water_source", false)), "load should restore flags")
	_expect(game_state.is_restored("old_well"), "load should restore restoration states")
	_expect(game_state.get_player_money() == 333, "load should restore money")
	_expect(game_state.get_player_energy() == 77, "load should restore energy")
	_expect(player.position == Vector2(142, 133), "load should restore player position")
	_expect(farm_plot.get_state_name() == "watered", "load should restore farm plot state")
	_expect(String(farm_plot.crop_id) == "turnip_spring", "load should restore farm crop")
	_expect(int(farm_plot.growth_days) == 1, "load should restore farm growth days")
	if _has_failed:
		return

	var minimal_data := {
		"version": save_manager.SAVE_VERSION,
		"inventory": {"items": {"stone": 2}},
	}
	save_manager.apply_runtime_save_data(yard, minimal_data)
	await process_frame
	_expect(int(inventory_manager.get_count("stone")) == 2, "missing fields should keep defaults while applying provided inventory")
	_expect(int(time_manager.year) >= 1, "missing time data should fall back to valid defaults")

	_remove_test_save()
	print("OK: Task 011 save/load runtime validation passed")
	_finish_deferred(0)


func _seed_runtime_state(yard: Node) -> void:
	var time_manager := yard.get_node("TimeManager")
	time_manager.year = 2
	time_manager.season_index = 2
	time_manager.day_of_season = 8
	time_manager.day = 8
	time_manager.total_day = 64
	time_manager.hour = 18
	time_manager.minute = 30
	if time_manager.has_method("_update_time_block"):
		time_manager._update_time_block(false)

	var weather_manager := yard.get_node("WeatherManager")
	weather_manager.set_today_weather("rainy")
	weather_manager.set_tomorrow_weather("sunny")

	var player := yard.get_node("Player")
	player.position = Vector2(142, 133)

	var inventory_manager := yard.get_node("InventoryManager")
	inventory_manager.items.clear()
	inventory_manager.add_item("wood", 24)
	inventory_manager.add_item("stone", 12)
	inventory_manager.add_item("seed_turnip", 1)
	inventory_manager.set_selected_item("wood")

	var relationship_manager := yard.get_node("RelationshipManager")
	relationship_manager.relationships.clear()
	relationship_manager.talked_today.clear()
	relationship_manager.gifted_today.clear()
	relationship_manager.add_relationship("aoi", 7)
	relationship_manager.mark_talked_today("aoi")
	relationship_manager.mark_gifted_today("mika")

	var game_state := yard.get_node("GameState")
	game_state.flags.clear()
	game_state.restoration_states.clear()
	game_state.set_flag("yard_water_source", true)
	game_state.set_restored("old_well", true)
	game_state.set_player_money(333)
	game_state.set_player_energy(77)

	var farm_plot := yard.get_node("FarmPlots/FarmPlot0")
	farm_plot.till()
	farm_plot.plant_seed("seed_turnip")
	farm_plot.water()
	farm_plot.growth_days = 1


func _clear_runtime_state(yard: Node) -> void:
	var time_manager := yard.get_node("TimeManager")
	time_manager.year = 1
	time_manager.season_index = 0
	time_manager.day_of_season = 1
	time_manager.day = 1
	time_manager.total_day = 1
	time_manager.hour = 6
	time_manager.minute = 0
	if time_manager.has_method("_update_time_block"):
		time_manager._update_time_block(false)

	var weather_manager := yard.get_node("WeatherManager")
	weather_manager.set_today_weather("sunny")
	weather_manager.set_tomorrow_weather("cloudy")

	var player := yard.get_node("Player")
	player.position = Vector2.ZERO

	var inventory_manager := yard.get_node("InventoryManager")
	inventory_manager.items.clear()
	inventory_manager.set_selected_item("")

	var relationship_manager := yard.get_node("RelationshipManager")
	relationship_manager.relationships.clear()
	relationship_manager.talked_today.clear()
	relationship_manager.gifted_today.clear()

	var game_state := yard.get_node("GameState")
	game_state.flags.clear()
	game_state.restoration_states.clear()
	game_state.set_player_money(0)
	game_state.set_player_energy(1)

	var farm_plot := yard.get_node("FarmPlots/FarmPlot0")
	if farm_plot.has_method("apply_save_data"):
		farm_plot.apply_save_data({})
	else:
		farm_plot.state = 0
		farm_plot.crop_id = ""
		farm_plot.seed_item_id = ""
		farm_plot.harvest_item_id = ""
		farm_plot.growth_days = 0
		farm_plot.is_watered = false


func _remove_test_save() -> void:
	if not FileAccess.file_exists(TEST_SAVE_PATH):
		return
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE_PATH))


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	_remove_test_save()
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
			_fail("Task 011 save/load validation timed out")
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
