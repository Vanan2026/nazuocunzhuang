extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 35.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: main-flow crop sleep/harvest initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene: PackedScene = load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return
	var main: Node = main_scene.instantiate()
	root.add_child(main)
	await process_frame
	await process_frame

	_expect(main.has_method("change_scene"), "Main should expose change_scene")
	_expect(main.has_method("sync_current_scene_state"), "Main should sync current scene state")
	if _has_failed:
		return

	var house: Node = main.get_current_gameplay_scene()
	_expect(house != null and house.name == "PlayerHouse", "Main should start in PlayerHouse")
	var house_door: Node = house.get_node_or_null("DoorToYard")
	var house_bed: Node = house.get_node_or_null("Bed")
	_expect(house_door != null, "PlayerHouse should include DoorToYard")
	_expect(house_bed != null, "PlayerHouse should include a bed for sleeping")
	if _has_failed:
		return
	_expect(house_bed.has_signal("sleep_completed"), "PlayerHouse bed should emit sleep_completed")
	if _has_failed:
		return

	house_door.on_interact(house.get_node_or_null("Player"))
	await _settle_route()
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "DoorToYard should route to yard")
	var yard: Node = main.get_current_gameplay_scene()
	_expect(yard != null and yard.name == "PlayerYard", "Main should instantiate PlayerYard")
	var yard_player: Node = yard.get_node_or_null("Player")
	var house_return: Node = yard.get_node_or_null("HouseDoor")
	var farm_plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot0")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	var game_state: Node = yard.get_node_or_null("GameState")
	_expect(house_return != null, "PlayerYard should include HouseDoor to return home")
	_expect(farm_plot != null, "PlayerYard should include FarmPlot0")
	_expect(inventory != null, "PlayerYard should include InventoryManager")
	_expect(game_state != null, "PlayerYard should include GameState")
	if _has_failed:
		return

	game_state.set_restored("old_well", true)
	inventory.add_item("seed_turnip", 1)
	inventory.set_selected_item("seed_turnip")
	_expect(farm_plot.till(), "FarmPlot0 should till")
	_expect(farm_plot.plant_seed("seed_turnip"), "FarmPlot0 should plant turnip seed")
	_expect(farm_plot.water(), "FarmPlot0 should water after planting")
	if _has_failed:
		return
	main.sync_current_scene_state()
	await process_frame
	var planted_save_data: Dictionary = main.build_main_flow_save_data()
	var saved_plot_data: Dictionary = _dictionary_from(planted_save_data.get("farm_plots", {}).get("0", {}))
	_expect(String(saved_plot_data.get("state", "")) == "watered", "Main-flow save data should include watered FarmPlot0")
	_expect(String(saved_plot_data.get("crop_id", "")) == "turnip_spring", "Main-flow save data should include planted crop id")
	if _has_failed:
		return

	for day_index in range(2):
		house_return.on_interact(yard_player)
		await _settle_route()
		_expect(String(main.get_current_gameplay_scene_id()) == "player_house", "HouseDoor should route back to PlayerHouse")
		house = main.get_current_gameplay_scene()
		house_bed = house.get_node_or_null("Bed")
		_expect(house_bed != null, "Returned PlayerHouse should include Bed")
		if _has_failed:
			return
		house_bed.on_interact(house.get_node_or_null("Player"))
		await process_frame
		main.change_scene("player_yard", "from_house")
		await _settle_route()
		yard = main.get_current_gameplay_scene()
		yard_player = yard.get_node_or_null("Player")
		house_return = yard.get_node_or_null("HouseDoor")
		farm_plot = yard.get_node_or_null("FarmPlots/FarmPlot0")
		_expect(farm_plot != null, "Returned yard should include FarmPlot0")
		if _has_failed:
			return
		if day_index < 1:
			_expect(String(farm_plot.get_state_name()) == "planted", "Crop should keep growing before final watered day")
			_expect(farm_plot.water(), "Crop should be waterable again on growth day %d" % (day_index + 2))
			main.sync_current_scene_state()
			await process_frame

	_expect(String(farm_plot.get_state_name()) == "ready", "Turnip should be ready after two watered sleeps")
	var shared_inventory: Node = main.get_node_or_null("InventoryManager")
	var before_count := int(shared_inventory.get_count("crop_turnip"))
	_expect(farm_plot.harvest(), "Ready turnip should harvest")
	await process_frame
	main.sync_current_scene_state()
	await process_frame
	_expect(int(shared_inventory.get_count("crop_turnip")) == before_count + 1, "Harvest should add crop_turnip to persistent inventory")
	_expect(String(farm_plot.get_state_name()) == "empty", "Harvested non-regrow turnip plot should reset to empty")
	if _has_failed:
		return

	print("OK: main-flow crop sleep/harvest runtime validation passed")
	_finish_deferred(0)


func _settle_route() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _dictionary_from(raw_value: Variant) -> Dictionary:
	if raw_value is Dictionary:
		var raw_dictionary: Dictionary = raw_value
		return raw_dictionary.duplicate(true)
	return {}


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
			_fail("Main-flow crop sleep/harvest validation timed out")
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
