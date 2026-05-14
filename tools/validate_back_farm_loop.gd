extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const BACK_FARM_SCENE := "res://scenes/regions/region_back_farm.tscn"
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
	_mark_progress("load back farm")
	var packed := HeadlessLifecycle.load_packed_scene(BACK_FARM_SCENE)
	if packed == null:
		_fail("could not load %s" % BACK_FARM_SCENE)
		return

	var back_farm := packed.instantiate()
	root.add_child(back_farm)
	current_scene = back_farm
	await process_frame
	await process_frame

	var farm_system := back_farm.get_node_or_null("FarmSystem")
	if farm_system == null:
		_fail("Region_BackFarm missing FarmSystem")
		return
	if not farm_system.has_method("plant") or not farm_system.has_method("water") or not farm_system.has_method("harvest") or not farm_system.has_method("advance_day"):
		_fail("FarmSystem missing required farm lifecycle methods")
		return

	_mark_progress("validate plot nodes")
	var plots := []
	for index in range(4):
		var plot := back_farm.get_node_or_null("YSortWorld/Interactables/FarmPlot%d" % index)
		if plot == null:
			_fail("Region_BackFarm missing FarmPlot%d" % index)
			return
		if not plot.has_method("on_interact"):
			_fail("FarmPlot%d missing on_interact" % index)
			return
		if int(plot.get("plot_index")) != index:
			_fail("FarmPlot%d plot_index is %s" % [index, plot.get("plot_index")])
			return
		plots.append(plot)

	var plot0: Node = plots[0]
	var crops: Array = farm_system.call("get_available_crops")
	if crops.is_empty():
		_fail("FarmSystem returned no available crops")
		return
	var crop_type := str(crops[0])

	_mark_progress("plant through interaction")
	plot0.call("on_interact", null)
	var info: Dictionary = farm_system.call("get_plot_info", 0)
	if int(info.get("state", -1)) != 1:
		_fail("plot interaction did not plant crop; info=%s" % info)
		return
	if str(info.get("crop_type", "")) != crop_type:
		_fail("plot planted %s, expected %s" % [info.get("crop_type", ""), crop_type])
		return

	_mark_progress("water and advance growth")
	var max_days := int(farm_system.CROP_DATA.get(crop_type, {}).get("days", 1))
	for _day in range(max_days):
		info = farm_system.call("get_plot_info", 0)
		if int(info.get("state", -1)) == 3:
			break
		plot0.call("on_interact", null)
		info = farm_system.call("get_plot_info", 0)
		if not bool(info.get("is_watered", false)):
			_fail("plot interaction did not water crop; info=%s" % info)
			return
		farm_system.call("advance_day")

	info = farm_system.call("get_plot_info", 0)
	if int(info.get("state", -1)) != 3:
		_fail("crop did not become harvest-ready after %d days; info=%s" % [max_days, info])
		return

	_mark_progress("harvest through interaction")
	plot0.call("on_interact", null)
	info = farm_system.call("get_plot_info", 0)
	if int(info.get("state", -1)) != 0:
		_fail("plot did not reset after harvest; info=%s" % info)
		return

	var inventory: Dictionary = farm_system.call("get_inventory")
	if int(inventory.get(crop_type, 0)) != 1:
		_fail("harvest did not add crop to inventory; inventory=%s" % inventory)
		return

	print("OK: BackFarm plant-water-advance-harvest loop validated")
	plots.clear()
	plot0 = null
	farm_system = null
	back_farm = null
	packed = null
	_finish_deferred(0)


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
	print("PROGRESS: back farm loop %s" % stage)


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
