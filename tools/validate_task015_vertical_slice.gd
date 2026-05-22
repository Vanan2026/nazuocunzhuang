extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const HOUSE_PATH := "res://game/scenes/home/PlayerHouse.tscn"
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"
const TEST_SAVE_PATH := "user://task015_vertical_slice_test.json"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: task015 vertical slice initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	_remove_test_save()
	var main_scene: PackedScene = load(MAIN_PATH) as PackedScene
	var house_scene: PackedScene = load(HOUSE_PATH) as PackedScene
	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	_expect(house_scene != null, "PlayerHouse scene should load")
	_expect(yard_scene != null, "PlayerYard scene should load")
	if _has_failed:
		return

	var main := main_scene.instantiate() as Node
	root.add_child(main)
	await process_frame
	_expect(main.get_node_or_null("PlayerHouse") != null, "Main should start in PlayerHouse")
	main.queue_free()
	await process_frame

	var house := house_scene.instantiate() as Node
	root.add_child(house)
	await process_frame
	var door := house.get_node_or_null("DoorToYard")
	_expect(door != null, "PlayerHouse should include DoorToYard")
	_expect(String(door.get("target_scene")) == PLAYER_YARD_PATH, "DoorToYard should target PlayerYard")
	house.queue_free()
	await process_frame

	var yard := yard_scene.instantiate() as Node
	root.add_child(yard)
	await process_frame
	await process_frame

	var data_registry := yard.get_node_or_null("DataRegistry")
	var inventory := yard.get_node_or_null("InventoryManager")
	var relationship := yard.get_node_or_null("RelationshipManager")
	var game_state := yard.get_node_or_null("GameState")
	var save_manager := yard.get_node_or_null("SaveManager")
	var time_manager := yard.get_node_or_null("TimeManager")
	var weather_manager := yard.get_node_or_null("WeatherManager")
	var dialogue_box := yard.get_node_or_null("DialogueBox")
	var player := yard.get_node_or_null("Player")
	var mailbox := yard.get_node_or_null("Mailbox")
	var village_path := yard.get_node_or_null("VillagePath")
	var wood_pile := yard.get_node_or_null("WoodPile")
	var stone_pile := yard.get_node_or_null("StonePile")
	var farm_plot := yard.get_node_or_null("FarmPlots/FarmPlot0")
	var aoi := yard.get_node_or_null("NPCs/Aoi")
	var gen := yard.get_node_or_null("NPCs/Gen")
	var old_well := yard.get_node_or_null("OldWell")
	var bed := yard.get_node_or_null("Bed")

	for pair in {
		"DataRegistry": data_registry,
		"InventoryManager": inventory,
		"RelationshipManager": relationship,
		"GameState": game_state,
		"SaveManager": save_manager,
		"TimeManager": time_manager,
		"WeatherManager": weather_manager,
		"DialogueBox": dialogue_box,
		"Player": player,
		"Mailbox": mailbox,
		"VillagePath": village_path,
		"WoodPile": wood_pile,
		"StonePile": stone_pile,
		"FarmPlot0": farm_plot,
		"Aoi": aoi,
		"Gen": gen,
		"OldWell": old_well,
		"Bed": bed,
	}.keys():
		var node: Node = {
			"DataRegistry": data_registry,
			"InventoryManager": inventory,
			"RelationshipManager": relationship,
			"GameState": game_state,
			"SaveManager": save_manager,
			"TimeManager": time_manager,
			"WeatherManager": weather_manager,
			"DialogueBox": dialogue_box,
			"Player": player,
			"Mailbox": mailbox,
			"VillagePath": village_path,
			"WoodPile": wood_pile,
			"StonePile": stone_pile,
			"FarmPlot0": farm_plot,
			"Aoi": aoi,
			"Gen": gen,
			"OldWell": old_well,
			"Bed": bed,
		}[pair]
		_expect(node != null, "PlayerYard missing vertical slice node: %s" % pair)
		if _has_failed:
			return

	# Read mailbox/weather.
	_expect(weather_manager.has_method("get_weather_info"), "WeatherManager should expose weather info")
	yard.show_mailbox_rumors()
	await process_frame
	_expect(bool(dialogue_box.visible), "Reading mailbox should show rumor dialogue")
	dialogue_box.close()

	# Plant and water crops.
	inventory.set_selected_item("seed_turnip")
	_expect(farm_plot.till(), "FarmPlot should till")
	_expect(farm_plot.plant_selected_seed(), "FarmPlot should plant selected seed")
	_expect(farm_plot.water(), "FarmPlot should water planted seed")
	_expect(farm_plot.get_state_name() == "watered", "FarmPlot should be watered")

	# Visit village path.
	village_path.on_interact(player)
	_expect(bool(game_state.get_flag("visited_village_path", false)), "VillagePath should set visited_village_path")

	# Talk to Aoi and Gen.
	inventory.set_selected_item("")
	aoi.on_interact(player)
	await process_frame
	_expect(int(relationship.get_relationship("aoi")) >= 1, "Talking to Aoi should affect relationship")
	gen.on_interact(player)
	await process_frame
	_expect(int(relationship.get_relationship("gen")) >= 1, "Talking to Gen should affect relationship")

	# Give a gift.
	inventory.add_item("food_persimmon_riceball", 1)
	inventory.set_selected_item("food_persimmon_riceball")
	var before_gift := int(relationship.get_relationship("aoi"))
	aoi.on_interact(player)
	await process_frame
	_expect(int(relationship.get_relationship("aoi")) > before_gift, "Gift should improve Aoi relationship")

	# Collect wood/stone placeholders and repair old well.
	wood_pile.on_interact(player)
	stone_pile.on_interact(player)
	_expect(int(inventory.get_count("wood")) >= 20, "WoodPile should provide old well wood")
	_expect(int(inventory.get_count("stone")) >= 10, "StonePile should provide old well stone")
	game_state.set_player_money(500)
	old_well.on_interact(player)
	await process_frame
	_expect(game_state.is_restored("old_well"), "Old well should be restored in vertical slice")
	_expect(bool(game_state.get_flag("rumor_old_well_bell", false)), "Old well should unlock rumor_old_well_bell")

	# Sleep, save, load, and trigger bell rumor after repair.
	var total_day_before_sleep := int(time_manager.get_date_info().get("total_day", 0))
	bed.on_interact(player)
	await process_frame
	var total_day_after_sleep := int(time_manager.get_date_info().get("total_day", 0))
	_expect(total_day_after_sleep > total_day_before_sleep, "Sleeping should advance to the next day")
	_expect(bool(save_manager.save_game(yard, TEST_SAVE_PATH)), "Vertical slice should save next-day state")

	time_manager.total_day = 1
	time_manager.day_of_season = 1
	time_manager.day = 1
	game_state.flags.clear()
	game_state.restoration_states.clear()
	_expect(bool(save_manager.load_game(yard, TEST_SAVE_PATH)), "Vertical slice should load saved next-day state")
	_expect(game_state.is_restored("old_well"), "Loaded state should keep old well restored")
	_expect(int(time_manager.get_date_info().get("total_day", 0)) == total_day_after_sleep, "Loaded state should keep next day")

	yard.show_mailbox_rumors()
	await process_frame
	_expect(_dialogue_contains(dialogue_box.dialogue, "铃"), "Bell rumor should appear after old well repair")
	_expect(bool(game_state.get_flag("heard_bell_rumor_01", false)), "Bell rumor should set heard_bell_rumor_01")

	_remove_test_save()
	print("OK: Task 015 vertical slice runtime validation passed")
	_finish_deferred(0)


func _dialogue_contains(dialogue: Dictionary, needle: String) -> bool:
	for line in dialogue.get("lines", []):
		if line is Dictionary and String(line.get("text", "")).contains(needle):
			return true
	return false


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
			_fail("Task 015 vertical slice validation timed out")
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
