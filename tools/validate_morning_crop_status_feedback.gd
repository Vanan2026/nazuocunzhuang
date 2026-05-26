extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 35.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: morning crop status feedback initialize")
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

	var house: Node = main.get_current_gameplay_scene()
	_expect(house != null and house.name == "PlayerHouse", "Main should start in PlayerHouse")
	var house_door: Node = house.get_node_or_null("DoorToYard")
	_expect(house_door != null, "PlayerHouse should include DoorToYard")
	if _has_failed:
		return
	house_door.on_interact(house.get_node_or_null("Player"))
	await _settle_route()

	var yard: Node = main.get_current_gameplay_scene()
	_expect(yard != null and yard.name == "PlayerYard", "Main should route to PlayerYard")
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
	_expect(farm_plot.plant_seed("seed_turnip"), "FarmPlot0 should plant")
	_expect(farm_plot.water(), "FarmPlot0 should water")
	main.sync_current_scene_state()
	await process_frame

	house_return.on_interact(yard.get_node_or_null("Player"))
	await _settle_route()
	_expect(String(main.get_current_gameplay_scene_id()) == "player_house", "HouseDoor should route to PlayerHouse")
	house = main.get_current_gameplay_scene()
	var house_bed: Node = house.get_node_or_null("Bed")
	_expect(house_bed != null, "PlayerHouse should include Bed")
	if _has_failed:
		return
	house_bed.on_interact(house.get_node_or_null("Player"))
	await _settle()
	_expect_crop_feedback(house, "菜地", "First sleep should show crop growth feedback in the house")
	if _has_failed:
		return

	for _day in range(1):
		main.change_scene("player_yard", "from_house")
		await _settle_route()
		yard = main.get_current_gameplay_scene()
		farm_plot = yard.get_node_or_null("FarmPlots/FarmPlot0")
		house_return = yard.get_node_or_null("HouseDoor")
		_expect(farm_plot != null, "Returned yard should include FarmPlot0")
		if _has_failed:
			return
		if String(farm_plot.get_state_name()) != "ready":
			_expect(farm_plot.water(), "Crop should be waterable before ready")
		main.sync_current_scene_state()
		await process_frame
		house_return.on_interact(yard.get_node_or_null("Player"))
		await _settle_route()
		house = main.get_current_gameplay_scene()
		house_bed = house.get_node_or_null("Bed")
		_expect(house_bed != null, "Returned PlayerHouse should include Bed")
		if _has_failed:
			return
		house_bed.on_interact(house.get_node_or_null("Player"))
		await _settle()

	_expect_crop_feedback(house, "成熟", "Final sleep should show harvest-ready feedback in the house")
	if _has_failed:
		return

	print("OK: morning crop status feedback runtime validation passed")
	_finish_deferred(0)


func _expect_crop_feedback(house: Node, needle: String, message: String) -> void:
	var dialogue_box: Node = house.get_node_or_null("DialogueBox")
	_expect(dialogue_box != null, "PlayerHouse should include DialogueBox")
	if _has_failed:
		return
	_expect(bool(dialogue_box.get("visible")), message)
	if _has_failed:
		return
	var line_label := dialogue_box.get_node_or_null("Panel/Content/TextColumn/LineLabel") as Label
	_expect(line_label != null, "DialogueBox should include LineLabel")
	if _has_failed:
		return
	_expect(line_label.text.contains(needle), message)


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
			_fail("Morning crop status feedback validation timed out")
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
