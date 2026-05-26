extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const EXPECTED_MAIN_SCENE := "res://scenes/world/world.tscn"
const GAME_MAIN_SCENE_PATH := "res://game/scenes/Main.tscn"
const WORLD_SCENE := "res://scenes/world/world.tscn"
const BACK_FARM_SCENE := "res://scenes/regions/region_back_farm.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 20.0

var _check_only := false
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
	_mark_progress("validate project settings")
	var main_scene: String = ProjectSettings.get_setting("application/run/main_scene", "")
	if main_scene != EXPECTED_MAIN_SCENE and main_scene != GAME_MAIN_SCENE_PATH:
		_fail("project main_scene is %s, expected %s or %s" % [main_scene, EXPECTED_MAIN_SCENE, GAME_MAIN_SCENE_PATH])
		return

	var main_script := FileAccess.get_file_as_string("res://scripts/main.gd")
	if main_script.contains("res://scenes/regions/region_home_area.tscn"):
		_fail("scripts/main.gd still boots Region_HomeArea directly instead of world.tscn")
		return

	_mark_progress("load world scene")
	var packed := HeadlessLifecycle.load_packed_scene(WORLD_SCENE)
	if packed == null:
		_fail("could not load %s" % WORLD_SCENE)
		return

	var world := packed.instantiate()
	root.add_child(world)
	current_scene = world

	_mark_progress("settle world startup")
	await process_frame
	await process_frame

	var world_controller := current_scene as Node
	if world_controller == null or not world_controller.has_method("get_region_loader"):
		_fail("world scene root is not a WorldController")
		return

	var loader: Node = world_controller.call("get_region_loader")
	if loader == null:
		_fail("WorldController missing RegionLoader")
		return

	if not loader.call("is_region_loaded", "Region_HomeArea"):
		_fail("Region_HomeArea was not loaded at startup")
		return

	var player := world_controller.call("get_player") as Node2D
	if player == null:
		_fail("WorldController did not spawn a player")
		return

	var home_region := loader.call("get_region", "Region_HomeArea") as Node
	var home_exit := home_region.get_node_or_null("YSortWorld/Interactables/BackyardFarmEntrance")
	if home_exit == null:
		_fail("Region_HomeArea missing BackyardFarmEntrance")
		return
	if str(home_exit.get("target_region_id")) != "Region_BackFarm":
		_fail("BackyardFarmEntrance target_region_id is not Region_BackFarm")
		return
	if str(home_exit.get("target_spawn_id")) != "back_farm_default":
		_fail("BackyardFarmEntrance target_spawn_id is not back_farm_default")
		return

	if _check_only:
		_run_check_only()
		return

	_mark_progress("interact home exit")
	home_exit.call("_reset")
	home_exit.call("on_interact", player)
	await _settle_transition()

	if not loader.call("is_region_loaded", "Region_BackFarm"):
		_fail("Region_BackFarm was not loaded after HomeArea exit")
		return
	if str(loader.call("get_current_region_id")) != "Region_BackFarm":
		_fail("current region after HomeArea exit is %s" % loader.call("get_current_region_id"))
		return

	var back_region := loader.call("get_region", "Region_BackFarm") as Node
	var back_spawn := _find_spawn_marker(back_region, "back_farm_default")
	if back_spawn == null:
		_fail("Region_BackFarm missing spawn_id=back_farm_default")
		return
	if player.global_position.distance_to(back_spawn.global_position) > 0.5:
		_fail("player did not land at back_farm_default: got %s expected %s" % [player.global_position, back_spawn.global_position])
		return

	var back_exit := back_region.get_node_or_null("YSortWorld/Interactables/ExitToHomeArea")
	if back_exit == null:
		_fail("Region_BackFarm missing ExitToHomeArea")
		return

	_mark_progress("interact back farm exit")
	back_exit.call("_reset")
	back_exit.call("on_interact", player)
	await _settle_transition()

	if str(loader.call("get_current_region_id")) != "Region_HomeArea":
		_fail("current region after BackFarm return is %s" % loader.call("get_current_region_id"))
		return

	var home_spawn := _find_spawn_marker(home_region, "home_area_from_back_farm")
	if home_spawn == null:
		_fail("Region_HomeArea missing spawn_id=home_area_from_back_farm")
		return
	if player.global_position.distance_to(home_spawn.global_position) > 0.5:
		_fail("player did not land at home_area_from_back_farm: got %s expected %s" % [player.global_position, home_spawn.global_position])
		return

	print("OK: world entry and HomeArea/BackFarm transition spawn validated")
	back_exit = null
	back_region = null
	home_exit = null
	home_region = null
	player = null
	loader = null
	world_controller = null
	world = null
	packed = null
	_finish_deferred(0)


func _run_check_only() -> void:
	_mark_progress("check-only validate back farm scene")
	var packed := HeadlessLifecycle.load_packed_scene(BACK_FARM_SCENE)
	if packed == null:
		_fail("could not load %s" % BACK_FARM_SCENE)
		return

	var back_region := packed.instantiate()
	root.add_child(back_region)

	if _find_spawn_marker(back_region, "back_farm_default") == null:
		_fail("Region_BackFarm missing spawn_id=back_farm_default")
		return

	var back_exit := back_region.get_node_or_null("YSortWorld/Interactables/ExitToHomeArea")
	if back_exit == null:
		_fail("Region_BackFarm missing ExitToHomeArea")
		return
	if str(back_exit.get("target_region_id")) != "Region_HomeArea":
		_fail("ExitToHomeArea target_region_id is not Region_HomeArea")
		return
	if str(back_exit.get("target_spawn_id")) != "home_area_from_back_farm":
		_fail("ExitToHomeArea target_spawn_id is not home_area_from_back_farm")
		return

	print("OK: world entry and transition spawn check-only contract validated")
	back_exit = null
	back_region = null
	packed = null
	_finish_deferred(0)


func _settle_transition() -> void:
	_mark_progress("settle transition")
	await create_timer(0.2).timeout
	await process_frame
	await process_frame


func _find_spawn_marker(root_node: Node, spawn_id: String) -> Marker2D:
	if root_node == null:
		return null
	if root_node is Marker2D and str(root_node.get_meta("spawn_id", "")) == spawn_id:
		return root_node as Marker2D

	for child in root_node.get_children():
		var marker := _find_spawn_marker(child, spawn_id)
		if marker != null:
			return marker

	return null


func _parse_validation_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg == "--check-only":
			_check_only = true
		elif arg.begins_with("--watchdog-timeout="):
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
	print("PROGRESS: transition spawn %s" % stage)


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
