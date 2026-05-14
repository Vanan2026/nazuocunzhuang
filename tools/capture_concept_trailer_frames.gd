extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const DEFAULT_MANIFEST := "res://docs/trailer/concept_trailer_2d_slice_2026-05-14.json"
const DEFAULT_OUTPUT_DIR := "res://.codex/trailer/concept_trailer_2d_slice_2026-05-14"
const WORLD_SCENE := "res://scenes/world/world.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 20.0

const POSE_STATE := {
	"idle": 0,
	"walk": 1,
	"interact": 2,
	"veranda_rest": 4,
	"farm_plant_water": 2,
	"farm_harvest_ready": 2,
}

var _manifest_path := DEFAULT_MANIFEST
var _output_dir := DEFAULT_OUTPUT_DIR
var _check_only := false
var _watchdog_timeout_seconds := WATCHDOG_TIMEOUT_SECONDS
var _watchdog_active := false
var _finishing := false
var _last_progress_msec := 0
var _last_progress_stage := "initialize"
var _manifest: Dictionary = {}


func _initialize() -> void:
	_parse_args()
	_start_watchdog()
	_mark_progress("initialize")
	call_deferred("_run")


func _run() -> void:
	_mark_progress("load manifest")
	if not _load_manifest():
		return
	if not _validate_manifest():
		return

	_mark_progress("load world")
	var error := change_scene_to_file(WORLD_SCENE)
	if error != OK:
		_fail("could not change scene to %s: %s" % [WORLD_SCENE, error])
		return

	await process_frame
	await process_frame

	var world_contract_ok := await _validate_world_contract()
	if not world_contract_ok:
		return

	if _check_only:
		print("OK: concept trailer capture contract validated")
		_finish_deferred(0)
		return

	if DisplayServer.get_name() == "headless":
		_fail("capture requires a display server; run without --headless or use --check-only")
		return

	root.size = _manifest_resolution()
	root.content_scale_size = _manifest_resolution()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(_output_dir))

	var shots: Array = _manifest.get("shots", [])
	for index in range(shots.size()):
		var shot: Dictionary = shots[index]
		_mark_progress("capture %s" % str(shot.get("id", "shot")))
		var shot_ready := await _prepare_shot(shot)
		if not shot_ready:
			return
		var captured := await _capture(shot)
		if not captured:
			return

	print("OK: concept trailer frames saved to %s" % ProjectSettings.globalize_path(_output_dir))
	_finish_deferred(0)


func _load_manifest() -> bool:
	if not FileAccess.file_exists(_manifest_path):
		_fail("manifest file does not exist: %s" % _manifest_path)
		return false

	var text := FileAccess.get_file_as_string(_manifest_path)
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		_fail("manifest is not a JSON object: %s" % _manifest_path)
		return false

	_manifest = parsed
	return true


func _validate_manifest() -> bool:
	var shots: Array = _manifest.get("shots", [])
	if shots.is_empty():
		_fail("manifest has no shots")
		return false

	var target_duration := float(_manifest.get("target_duration_seconds", 0.0))
	var total_duration := 0.0
	var has_home := false
	var has_back_farm := false
	var has_rest := false
	var has_farm := false
	var has_walk := false

	for shot in shots:
		total_duration += float(shot.get("duration_seconds", 0.0))
		var region_id := str(shot.get("region_id", ""))
		var pose := str(shot.get("pose", ""))
		has_home = has_home or region_id == "Region_HomeArea"
		has_back_farm = has_back_farm or region_id == "Region_BackFarm"
		has_rest = has_rest or pose == "veranda_rest"
		has_farm = has_farm or pose.begins_with("farm_")
		has_walk = has_walk or pose == "walk"

		if str(shot.get("id", "")).is_empty():
			_fail("manifest shot missing id")
			return false
		if str(shot.get("capture_file", "")).is_empty():
			_fail("manifest shot missing capture_file: %s" % shot.get("id", ""))
			return false

	if target_duration < 15.0 or target_duration > 20.0:
		_fail("target duration must be 15-20 seconds, got %.2f" % target_duration)
		return false
	if abs(total_duration - target_duration) > 0.01:
		_fail("shot durations total %.2f but target is %.2f" % [total_duration, target_duration])
		return false
	if total_duration < 15.0 or total_duration > 20.0:
		_fail("shot duration total must be 15-20 seconds, got %.2f" % total_duration)
		return false
	if not has_home or not has_back_farm or not has_rest or not has_farm or not has_walk:
		_fail("manifest must include HomeArea, BackFarm, veranda_rest, farm interaction, and walk pose")
		return false

	for source_path in _manifest.get("source_files", []):
		if not FileAccess.file_exists(str("res://%s" % source_path)):
			_fail("manifest source file does not exist: %s" % source_path)
			return false

	return true


func _validate_world_contract() -> bool:
	if current_scene == null or not current_scene.has_method("get_region_loader") or not current_scene.has_method("spawn_player_at"):
		_fail("current scene is not a WorldController-compatible world")
		return false

	var loader: Node = current_scene.call("get_region_loader")
	if loader == null:
		_fail("WorldController missing RegionLoader")
		return false

	var player := _player()
	if player == null:
		_fail("WorldController missing player")
		return false

	if not loader.call("is_region_loaded", "Region_HomeArea"):
		_fail("Region_HomeArea not loaded at startup")
		return false

	await _spawn_region("Region_BackFarm", "back_farm_default")
	var back_region := loader.call("get_region", "Region_BackFarm") as Node
	if back_region == null:
		_fail("Region_BackFarm did not load")
		return false
	if back_region.get_node_or_null("FarmSystem") == null:
		_fail("Region_BackFarm missing FarmSystem")
		return false
	if back_region.get_node_or_null("YSortWorld/Interactables/FarmPlot0") == null:
		_fail("Region_BackFarm missing FarmPlot0")
		return false

	await _spawn_region("Region_HomeArea", "home_area_default")
	var home_region := loader.call("get_region", "Region_HomeArea") as Node
	if home_region == null:
		_fail("Region_HomeArea did not load")
		return false
	if home_region.get_node_or_null("YSortWorld/Interactables/BenchRestInteract") == null:
		_fail("Region_HomeArea missing BenchRestInteract")
		return false

	return true


func _prepare_shot(shot: Dictionary) -> bool:
	var region_id := str(shot.get("region_id", "Region_HomeArea"))
	var spawn_id := str(shot.get("spawn_id", ""))
	await _spawn_region(region_id, spawn_id)

	var region := _region(region_id)
	if region == null:
		_fail("missing region for shot %s: %s" % [shot.get("id", ""), region_id])
		return false

	var player := _player()
	if player == null:
		_fail("missing player for shot %s" % shot.get("id", ""))
		return false

	if shot.has("player_local"):
		player.global_position = _local_to_global(region, shot.get("player_local", [0, 0]))

	var facing := _vector_from_array(shot.get("facing", [0, 1]))
	if facing != Vector2.ZERO:
		player.set("facing_direction", facing.normalized())

	var pose := str(shot.get("pose", "idle"))
	match pose:
		"veranda_rest":
			var rest_ready := await _prepare_veranda_rest(region, player)
			if not rest_ready:
				return false
		"farm_plant_water":
			var plant_ready := await _prepare_farm_plant_water(region, player)
			if not plant_ready:
				return false
		"farm_harvest_ready":
			var harvest_ready := await _prepare_farm_harvest_ready(region, player)
			if not harvest_ready:
				return false
		_:
			player.set("current_state", int(POSE_STATE.get(pose, 0)))

	_sync_player_visual(player)
	_focus_camera(region, shot, player)
	await process_frame
	await process_frame
	return true


func _prepare_veranda_rest(region: Node, player: Node2D) -> bool:
	var rest := region.get_node_or_null("YSortWorld/Interactables/BenchRestInteract")
	if rest == null or not rest.has_method("on_interact"):
		_fail("BenchRestInteract missing or not interactable")
		return false

	rest.call("on_interact", player)
	await process_frame
	player.set("current_state", int(POSE_STATE["veranda_rest"]))
	return true


func _prepare_farm_plant_water(region: Node, player: Node2D) -> bool:
	var plot := region.get_node_or_null("YSortWorld/Interactables/FarmPlot0")
	var farm := region.get_node_or_null("FarmSystem")
	if plot == null or farm == null or not plot.has_method("on_interact"):
		_fail("FarmPlot0/FarmSystem missing for plant-water shot")
		return false

	var info: Dictionary = farm.call("get_plot_info", 0)
	if int(info.get("state", 0)) == 0:
		plot.call("on_interact", player)
		await process_frame
	info = farm.call("get_plot_info", 0)
	if int(info.get("state", 0)) in [1, 2] and not bool(info.get("is_watered", false)):
		plot.call("on_interact", player)
		await process_frame

	player.set("current_state", int(POSE_STATE["farm_plant_water"]))
	return true


func _prepare_farm_harvest_ready(region: Node, player: Node2D) -> bool:
	var plot := region.get_node_or_null("YSortWorld/Interactables/FarmPlot0")
	var farm := region.get_node_or_null("FarmSystem")
	if plot == null or farm == null or not plot.has_method("on_interact"):
		_fail("FarmPlot0/FarmSystem missing for harvest shot")
		return false

	var guard := 20
	var info: Dictionary = farm.call("get_plot_info", 0)
	if int(info.get("state", 0)) == 0:
		plot.call("on_interact", player)
		await process_frame

	while guard > 0:
		info = farm.call("get_plot_info", 0)
		if int(info.get("state", 0)) == 3:
			break
		if not bool(info.get("is_watered", false)):
			plot.call("on_interact", player)
			await process_frame
		farm.call("advance_day")
		guard -= 1

	info = farm.call("get_plot_info", 0)
	if int(info.get("state", 0)) != 3:
		_fail("FarmPlot0 did not reach ready state for harvest shot")
		return false

	plot.call("on_interact", player)
	await process_frame
	player.set("current_state", int(POSE_STATE["farm_harvest_ready"]))
	return true


func _capture(shot: Dictionary) -> bool:
	var image := root.get_texture().get_image()
	if image == null:
		_fail("viewport screenshot unavailable")
		return false

	var output_path := "%s/%s" % [_output_dir, str(shot.get("capture_file", "shot.png"))]
	var error := image.save_png(output_path)
	if error != OK:
		_fail("could not save screenshot %s: %s" % [output_path, error])
		return false

	print("OK: captured %s" % output_path)
	return true


func _spawn_region(region_id: String, spawn_id: String) -> void:
	current_scene.call("spawn_player_at", region_id, spawn_id)
	await create_timer(0.2).timeout
	await process_frame
	await process_frame


func _focus_camera(region: Node, shot: Dictionary, player: Node2D) -> void:
	var camera := current_scene.call("get_camera") as Camera2D
	if camera == null:
		camera = current_scene.get_node_or_null("WorldCamera") as Camera2D
	if camera == null:
		return

	if shot.has("camera_focus_local"):
		camera.global_position = _local_to_global(region, shot.get("camera_focus_local", [0, 0]))
	else:
		camera.global_position = player.global_position

	camera.reset_smoothing()
	camera.force_update_scroll()


func _sync_player_visual(player: Node) -> void:
	if player.has_method("_sync_visual_scale"):
		player.call("_sync_visual_scale")
	if player.has_method("_sync_visual_animation"):
		player.call("_sync_visual_animation", true)


func _player() -> Node2D:
	if current_scene != null and current_scene.has_method("get_player"):
		return current_scene.call("get_player") as Node2D
	return null


func _region(region_id: String) -> Node:
	if current_scene == null or not current_scene.has_method("get_region_loader"):
		return null
	var loader: Node = current_scene.call("get_region_loader")
	if loader == null:
		return null
	return loader.call("get_region", region_id) as Node


func _local_to_global(region: Node, value) -> Vector2:
	var local := _vector_from_array(value)
	if region is Node2D:
		return (region as Node2D).global_position + local
	return local


func _vector_from_array(value) -> Vector2:
	if typeof(value) == TYPE_ARRAY and value.size() >= 2:
		return Vector2(float(value[0]), float(value[1]))
	return Vector2.ZERO


func _manifest_resolution() -> Vector2i:
	var resolution = _manifest.get("resolution", [1280, 720])
	if typeof(resolution) == TYPE_ARRAY and resolution.size() >= 2:
		return Vector2i(int(resolution[0]), int(resolution[1]))
	return Vector2i(1280, 720)


func _parse_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg == "--check-only":
			_check_only = true
		elif arg.begins_with("--manifest="):
			_manifest_path = arg.trim_prefix("--manifest=")
		elif arg.begins_with("--out="):
			_output_dir = arg.trim_prefix("--out=")
		elif arg.begins_with("--watchdog-timeout="):
			var value := arg.trim_prefix("--watchdog-timeout=")
			if value.is_valid_float():
				_watchdog_timeout_seconds = max(0.5, value.to_float())


func _start_watchdog() -> void:
	_watchdog_active = true
	_watchdog_loop()


func _watchdog_loop() -> void:
	while _watchdog_active:
		await create_timer(0.5).timeout
		var elapsed_seconds := float(Time.get_ticks_msec() - _last_progress_msec) / 1000.0
		if elapsed_seconds > _watchdog_timeout_seconds:
			printerr("FAIL: trailer capture watchdog timed out after %.1fs without progress; last stage: %s" % [elapsed_seconds, _last_progress_stage])
			_finish_deferred(124)
			return


func _mark_progress(stage: String) -> void:
	_last_progress_msec = Time.get_ticks_msec()
	_last_progress_stage = stage
	print("PROGRESS: concept trailer %s" % stage)


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
