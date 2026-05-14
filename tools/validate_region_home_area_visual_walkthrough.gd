extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const WORLD := "res://scenes/world/world.tscn"
const OUTPUT_DIR := "res://.codex"
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
	root.size = Vector2i(1280, 720)
	root.content_scale_size = Vector2i(1280, 720)

	if _check_only:
		await _run_check_only()
		return

	_mark_progress("prepare output directory")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT_DIR))

	_mark_progress("load home area default")
	await _load_world()
	_mark_progress("capture home area default")
	await _capture("region_home_area_walk_01_default_spawn.png")

	_mark_progress("load back farm entry")
	await _move_world_player("Region_BackFarm", "back_farm_default")
	_mark_progress("capture back farm entry")
	await _capture("region_home_area_walk_02_back_farm_entry.png")

	_mark_progress("load home area return")
	await _move_world_player("Region_HomeArea", "home_area_from_back_farm")
	_mark_progress("capture home area return")
	await _capture("region_home_area_walk_03_return_from_back_farm.png")

	_place_player(Vector2(4980, 8740), Vector2.LEFT)
	_mark_progress("capture foreground occlusion")
	await _capture("region_home_area_walk_04_foreground_grass_occlusion.png")

	print("OK: region visual walkthrough screenshots saved to %s" % ProjectSettings.globalize_path(OUTPUT_DIR))
	_finish_deferred(0)


func _run_check_only() -> void:
	_mark_progress("check-only load home area")
	await _load_world()
	if not _require_player_and_camera("World/HomeArea"):
		return
	if not _require_spawn_marker("home_area_default"):
		return
	if not _require_spawn_marker("home_area_from_back_farm"):
		return

	_mark_progress("check-only load back farm")
	await _move_world_player("Region_BackFarm", "back_farm_default")
	if not _require_camera("World/BackFarm"):
		return
	if not _require_spawn_marker("back_farm_default"):
		return

	print("OK: region visual walkthrough check-only contract validated")
	_finish_deferred(0)


func _load_world() -> void:
	var error := change_scene_to_file(WORLD)
	if error != OK:
		_fail("could not change scene to %s: %s" % [WORLD, error])
		return

	await process_frame
	await process_frame
	_snap_camera_to_player()


func _move_world_player(region_id: String, spawn_id: String) -> void:
	if current_scene == null or not current_scene.has_method("spawn_player_at"):
		_fail("current scene is not WorldController")
		return
	current_scene.call("spawn_player_at", region_id, spawn_id)
	await create_timer(0.2).timeout
	await process_frame
	await process_frame
	_snap_camera_to_player()


func _require_spawn_marker(spawn_id: String) -> bool:
	if _find_spawn_marker(current_scene, spawn_id) == null:
		_fail("missing marker for visual walkthrough: %s" % spawn_id)
		return false
	return true


func _require_player_and_camera(scene_label: String) -> bool:
	if _player() == null:
		_fail("%s missing YSortWorld/Player" % scene_label)
		return false
	return _require_camera(scene_label)


func _require_camera(scene_label: String) -> bool:
	var camera := current_scene.get_node_or_null("WorldCamera") as Camera2D
	if camera == null:
		camera = current_scene.get_node_or_null("CameraRig") as Camera2D
	if camera == null:
		_fail("%s missing Camera2D" % scene_label)
		return false
	return true


func _place_player(position: Vector2, facing: Vector2) -> void:
	var player := _player()
	if player == null:
		_fail("missing player in visual walkthrough")
		return
	player.global_position = position
	player.set("facing_direction", facing)
	if player.has_method("_sync_visual_scale"):
		player.call("_sync_visual_scale")
	if player.has_method("_sync_visual_animation"):
		player.call("_sync_visual_animation", true)
	_snap_camera_to_player()


func _capture(file_name: String) -> void:
	await process_frame
	await process_frame
	var image := root.get_texture().get_image()
	if image == null:
		_fail("viewport screenshot is unavailable; run without --headless for display-backed capture")
		return
	var output_path := "%s/%s" % [OUTPUT_DIR, file_name]
	var error := image.save_png(output_path)
	if error != OK:
		_fail("could not save screenshot %s: %s" % [output_path, error])


func _snap_camera_to_player() -> void:
	var player := _player()
	if player == null:
		return
	var camera := current_scene.get_node_or_null("WorldCamera") as Camera2D
	if camera == null:
		camera = current_scene.get_node_or_null("CameraRig") as Camera2D
	if camera == null:
		return
	camera.global_position = player.global_position
	camera.reset_smoothing()
	camera.force_update_scroll()


func _player() -> Node2D:
	if current_scene == null:
		return null
	if current_scene.has_method("get_player"):
		return current_scene.call("get_player") as Node2D
	return current_scene.get_node_or_null("YSortWorld/Player") as Node2D


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
	print("PROGRESS: visual walkthrough %s" % stage)


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
