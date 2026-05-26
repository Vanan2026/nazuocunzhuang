extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: first-week crop pacing initialize")
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

	var registry: Node = main.get_node_or_null("DataRegistry")
	_expect(registry != null, "Main should expose DataRegistry")
	if _has_failed:
		return
	var turnip_data: Dictionary = registry.get_crop("turnip_spring")
	_expect(int(turnip_data.get("grow_days", 0)) == 2, "Intro turnip grow_days should be 2")
	if _has_failed:
		return

	main.change_scene("player_yard", "from_house")
	await _settle_route()
	var yard: Node = main.get_current_gameplay_scene()
	var farm_plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot0")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	var game_state: Node = yard.get_node_or_null("GameState")
	var house_return: Node = yard.get_node_or_null("HouseDoor")
	_expect(farm_plot != null, "PlayerYard should include FarmPlot0")
	_expect(inventory != null, "PlayerYard should include InventoryManager")
	_expect(game_state != null, "PlayerYard should include GameState")
	_expect(house_return != null, "PlayerYard should include HouseDoor")
	if _has_failed:
		return

	game_state.set_restored("old_well", true)
	inventory.add_item("seed_turnip", 1)
	inventory.set_selected_item("seed_turnip")
	_expect(farm_plot.till(), "FarmPlot0 should till")
	_expect(farm_plot.plant_seed("seed_turnip"), "FarmPlot0 should plant turnip")
	_expect(farm_plot.water(), "FarmPlot0 should water turnip")
	main.sync_current_scene_state()
	await process_frame

	house_return.on_interact(yard.get_node_or_null("Player"))
	await _settle_route()
	var house: Node = main.get_current_gameplay_scene()
	var house_bed: Node = house.get_node_or_null("Bed")
	_expect(house_bed != null, "PlayerHouse should include Bed")
	if _has_failed:
		return
	house_bed.on_interact(house.get_node_or_null("Player"))
	await _settle()
	main.change_scene("player_yard", "from_house")
	await _settle_route()
	yard = main.get_current_gameplay_scene()
	farm_plot = yard.get_node_or_null("FarmPlots/FarmPlot0")
	house_return = yard.get_node_or_null("HouseDoor")
	_expect(String(farm_plot.get_state_name()) == "planted", "Turnip should still need one more watering after first sleep")
	_expect(farm_plot.water(), "Turnip should be waterable on second day")
	main.sync_current_scene_state()
	await process_frame

	house_return.on_interact(yard.get_node_or_null("Player"))
	await _settle_route()
	house = main.get_current_gameplay_scene()
	house_bed = house.get_node_or_null("Bed")
	house_bed.on_interact(house.get_node_or_null("Player"))
	await _settle()
	main.change_scene("player_yard", "from_house")
	await _settle_route()
	yard = main.get_current_gameplay_scene()
	farm_plot = yard.get_node_or_null("FarmPlots/FarmPlot0")
	_expect(String(farm_plot.get_state_name()) == "ready", "Turnip should be ready after two watered sleeps")
	if _has_failed:
		return

	print("OK: first-week crop pacing runtime validation passed")
	_finish_deferred(0)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _settle_route() -> void:
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
			_fail("First-week crop pacing validation timed out")
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
