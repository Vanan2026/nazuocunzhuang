extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const WORLD_SCENE := "res://scenes/world/world.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 20.0

var _watchdog_timeout_seconds := WATCHDOG_TIMEOUT_SECONDS
var _watchdog_active := false
var _finishing := false
var _last_progress_msec := 0
var _last_progress_stage := "initialize"


func _initialize() -> void:
	_parse_validation_args()
	_start_watchdog()
	_mark_progress("initialize")
	call_deferred("_run")


func _run() -> void:
	var save_system := root.get_node_or_null("SaveSystem")
	if save_system == null:
		_fail("missing SaveSystem autoload")
		return
	if not save_system.has_method("create_save_data") or not save_system.has_method("apply_save_data"):
		_fail("SaveSystem missing create_save_data/apply_save_data")
		return

	_mark_progress("load world")
	var packed := HeadlessLifecycle.load_packed_scene(WORLD_SCENE)
	if packed == null:
		_fail("could not load %s" % WORLD_SCENE)
		return

	var world := packed.instantiate()
	root.add_child(world)
	current_scene = world
	await process_frame
	await process_frame

	_mark_progress("move to back farm")
	world.call("spawn_player_at", "Region_BackFarm", "back_farm_default")
	await create_timer(0.2).timeout

	var loader: Node = world.call("get_region_loader")
	var back_farm := loader.call("get_region", "Region_BackFarm") as Node
	if back_farm == null:
		_fail("Region_BackFarm not loaded for save validation")
		return

	var farm_system := back_farm.get_node_or_null("FarmSystem")
	if farm_system == null:
		_fail("Region_BackFarm missing FarmSystem")
		return

	_mark_progress("seed runtime state")
	var time_system := root.get_node_or_null("TimeSystem")
	if time_system == null:
		_fail("missing TimeSystem autoload")
		return
	time_system.set("current_day", 12)
	time_system.set("current_season", "summer")

	var crops: Array = farm_system.call("get_available_crops")
	if crops.is_empty():
		_fail("FarmSystem returned no available crops")
		return
	var crop_type := str(crops[0])

	if not farm_system.call("plant", 0, crop_type):
		_fail("could not plant crop for save validation")
		return
	if not farm_system.call("water", 0):
		_fail("could not water crop for save validation")
		return
	if not farm_system.call("plant", 1, crop_type):
		_fail("could not plant second crop for save validation")
		return
	farm_system.call("add_inventory_item", "test_seed", 3)

	_mark_progress("save state")
	var saved: Dictionary = save_system.call("create_save_data", world, "back_farm_default")
	_require_saved_payload(saved, crop_type)

	_mark_progress("mutate after save")
	time_system.set("current_day", 1)
	time_system.set("current_season", "spring")
	farm_system.call("reset_state")
	world.call("spawn_player_at", "Region_HomeArea", "home_area_default")
	await create_timer(0.2).timeout

	_mark_progress("load state")
	await save_system.call("apply_save_data", saved, world)
	await create_timer(0.2).timeout

	loader = world.call("get_region_loader")
	if str(loader.call("get_current_region_id")) != "Region_BackFarm":
		_fail("load did not restore current region; got %s" % loader.call("get_current_region_id"))
		return
	if str(world.get("current_spawn_id")) != "back_farm_default":
		_fail("load did not restore spawn; got %s" % world.get("current_spawn_id"))
		return

	if int(time_system.get("current_day")) != 12:
		_fail("load did not restore current day; got %s" % time_system.get("current_day"))
		return
	if str(time_system.get("current_season")) != "summer":
		_fail("load did not restore current season; got %s" % time_system.get("current_season"))
		return

	back_farm = loader.call("get_region", "Region_BackFarm") as Node
	farm_system = back_farm.get_node_or_null("FarmSystem")
	var plot0: Dictionary = farm_system.call("get_plot_info", 0)
	if int(plot0.get("state", -1)) != 1 or str(plot0.get("crop_type", "")) != crop_type or not bool(plot0.get("is_watered", false)):
		_fail("load did not restore plot 0 state; info=%s" % plot0)
		return

	var plot1: Dictionary = farm_system.call("get_plot_info", 1)
	if int(plot1.get("state", -1)) != 1 or str(plot1.get("crop_type", "")) != crop_type:
		_fail("load did not restore plot 1 state; info=%s" % plot1)
		return

	var inventory: Dictionary = farm_system.call("get_inventory")
	if int(inventory.get("test_seed", 0)) != 3:
		_fail("load did not restore inventory; inventory=%s" % inventory)
		return

	print("OK: save/load boundary restored region/spawn, day/season, BackFarm plots, and inventory")
	farm_system = null
	back_farm = null
	world = null
	packed = null
	_finish_deferred(0)


func _require_saved_payload(saved: Dictionary, crop_type: String) -> void:
	if str(saved.get("version", "")) != "1":
		_fail("save payload missing version=1; payload=%s" % saved)
		return
	var player := saved.get("player", {}) as Dictionary
	if str(player.get("region_id", "")) != "Region_BackFarm":
		_fail("save payload missing player region; player=%s" % player)
		return
	if str(player.get("spawn_id", "")) != "back_farm_default":
		_fail("save payload missing player spawn; player=%s" % player)
		return
	var time_state := saved.get("time", {}) as Dictionary
	if int(time_state.get("day", 0)) != 12 or str(time_state.get("season", "")) != "summer":
		_fail("save payload missing time state; time=%s" % time_state)
		return
	var inventory := saved.get("inventory", {}) as Dictionary
	if int(inventory.get("test_seed", 0)) != 3:
		_fail("save payload missing inventory; inventory=%s" % inventory)
		return
	var regions := saved.get("regions", {}) as Dictionary
	var back_farm := regions.get("Region_BackFarm", {}) as Dictionary
	var nodes := back_farm.get("nodes", {}) as Dictionary
	var farm := nodes.get("FarmSystem", {}) as Dictionary
	var plots := farm.get("plots", []) as Array
	if plots.size() < 2:
		_fail("save payload missing BackFarm plots; farm=%s" % farm)
		return
	var plot0 := plots[0] as Dictionary
	if int(plot0.get("state", -1)) != 1 or str(plot0.get("crop_type", "")) != crop_type:
		_fail("save payload missing plot 0 crop; plot=%s" % plot0)
		return


func _parse_validation_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--watchdog-timeout="):
			var value := arg.trim_prefix("--watchdog-timeout=")
			if not value.is_valid_float():
				_fail("invalid --watchdog-timeout value: %s" % value)
				return
			_watchdog_timeout_seconds = max(0.5, value.to_float())


func _start_watchdog() -> void:
	_watchdog_active = true
	_watchdog_loop()


func _watchdog_loop() -> void:
	while _watchdog_active:
		await create_timer(0.5).timeout
		var elapsed_seconds := float(Time.get_ticks_msec() - _last_progress_msec) / 1000.0
		if elapsed_seconds > _watchdog_timeout_seconds:
			printerr("FAIL: validation watchdog timed out after %.1fs without progress; last stage: %s" % [elapsed_seconds, _last_progress_stage])
			_finish_deferred(124)
			return


func _mark_progress(stage: String) -> void:
	_last_progress_msec = Time.get_ticks_msec()
	_last_progress_stage = stage
	print("PROGRESS: save/load boundary %s" % stage)


func _fail(message: String) -> void:
	printerr("FAIL: %s" % message)
	_finish_deferred(1)


func _finish_deferred(exit_code: int) -> void:
	if _finishing:
		return
	_finishing = true
	_watchdog_active = false
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)

