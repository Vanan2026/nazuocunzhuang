extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const WORLD := "res://scenes/world/world.tscn"
const OUTPUT_DIR := "res://.codex"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

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
	if not _require_home_area_object_contracts():
		return

	await _capture_player_point("region_home_area_walk_01_default_spawn.png", Vector2(4790, 6622), Vector2.UP, "default spawn / house-front path")
	await _capture_player_point("region_home_area_walk_02_house_steps_walkable.png", Vector2(4710, 6460), Vector2.UP, "house steps and veranda approach")
	await _capture_player_point("region_home_area_walk_03_left_yard_depth.png", Vector2(4431, 6692), Vector2.LEFT, "left yard depth")
	await _capture_player_point("region_home_area_walk_04_center_yard_depth.png", Vector2(4723, 6831), Vector2.UP, "center yard depth")
	await _capture_player_point("region_home_area_walk_05_back_farm_gate.png", Vector2(5005, 6880), Vector2.UP, "back farm gate")
	await _capture_player_point("region_home_area_walk_06_right_path_edge.png", Vector2(4928, 6465), Vector2.RIGHT, "right path edge")
	await _capture_player_point("region_home_area_walk_07_left_tree_edge.png", Vector2(4182, 6580), Vector2.LEFT, "left tree edge")
	await _capture_player_point("region_home_area_walk_08_south_foreground_edge.png", Vector2(4919, 7019), Vector2.DOWN, "south foreground edge check")
	await _capture_player_point("region_home_area_walk_09_back_farm_return_anchor.png", Vector2(5005, 6880), Vector2.UP, "return anchor and gate")

	_mark_progress("load back farm entry")
	await _move_world_player("Region_BackFarm", "back_farm_default")
	_mark_progress("capture back farm entry")
	await _capture("region_home_area_walk_14_back_farm_entry.png")

	_mark_progress("load home area return")
	await _move_world_player("Region_HomeArea", "home_area_from_back_farm")
	_mark_progress("capture home area return")
	await _capture("region_home_area_walk_15_return_from_back_farm.png")

	print("OK: detailed region visual walkthrough screenshots saved to %s" % ProjectSettings.globalize_path(OUTPUT_DIR))
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
	if not _require_home_area_object_contracts():
		return

	_mark_progress("check-only load back farm")
	await _move_world_player("Region_BackFarm", "back_farm_default")
	if not _require_camera("World/BackFarm"):
		return
	if not _require_spawn_marker("back_farm_default"):
		return

	print("OK: detailed region visual walkthrough check-only contract validated")
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


func _capture_player_point(file_name: String, position: Vector2, facing: Vector2, label: String) -> void:
	_place_player(position, facing)
	_mark_progress("capture %s" % label)
	await _capture(file_name)


func _require_home_area_object_contracts() -> bool:
	var home_area := _home_area()
	if home_area == null:
		_fail("world should load Region_HomeArea for detailed visual walkthrough")
		return false

	var required_paths := [
		"ArtLayers/SourceReferenceHidden",
		"ArtLayers/BaseGroundPaths",
		"ArtLayers/MidgroundBehindPlayer",
		"ForegroundOcclusion",
		"YSortWorld/Player",
		"YSortWorld/Interactables",
		"YSortWorld/Interactables/BackyardFarmEntrance",
		"YSortWorld/Interactables/BackyardFarmEntrance/CollisionShape2D",
		"CameraRig",
	]
	for node_path in required_paths:
		if home_area.get_node_or_null(node_path) == null:
			_fail("missing HomeArea World2D QA node: %s" % node_path)
			return false

	var layer_contracts := {
		"ArtLayers/SourceReferenceHidden": "res://production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/home_area_01_source.png",
		"ArtLayers/BaseGroundPaths": "res://production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/home_area_02_base_ground_paths.png",
		"ArtLayers/MidgroundBehindPlayer": "res://production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/home_area_04_midground_behind_player.png",
		"ForegroundOcclusion": "res://production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/home_area_03_foreground_occlusion_v4_no_bottom_leaf_wall.png",
	}
	for node_path in layer_contracts.keys():
		var sprite := home_area.get_node_or_null(node_path) as Sprite2D
		if sprite == null:
			_fail("HomeArea World2D layer is not Sprite2D: %s" % node_path)
			return false
		if sprite.texture == null:
			_fail("HomeArea World2D layer failed to load texture: %s" % node_path)
			return false
		if sprite.texture.resource_path != layer_contracts[node_path]:
			_fail("HomeArea World2D layer texture mismatch for %s: %s" % [node_path, sprite.texture.resource_path])
			return false
		if sprite.centered:
			_fail("HomeArea World2D layer must use top-left canvas coordinates: %s" % node_path)
			return false

	var source_ref := home_area.get_node_or_null("ArtLayers/SourceReferenceHidden") as CanvasItem
	if source_ref == null or source_ref.visible:
		_fail("SourceReferenceHidden must stay hidden and review-only")
		return false

	var exit := home_area.get_node_or_null("YSortWorld/Interactables/BackyardFarmEntrance")
	if str(exit.get("target_region_id")) != "Region_BackFarm":
		_fail("BackyardFarmEntrance target_region_id must be Region_BackFarm")
		return false
	if str(exit.get("target_spawn_id")) != "back_farm_default":
		_fail("BackyardFarmEntrance target_spawn_id must be back_farm_default")
		return false

	return true

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
	camera.global_position = player.global_position + _camera_look_ahead_offset()
	camera.reset_smoothing()
	camera.force_update_scroll()


func _camera_look_ahead_offset() -> Vector2:
	if current_scene != null and current_scene.has_method("get_camera_target_offset"):
		var offset: Variant = current_scene.call("get_camera_target_offset")
		if offset is Vector2:
			return offset
	if current_scene != null:
		var value: Variant = current_scene.get("camera_look_ahead_offset")
		if value is Vector2:
			return value
	return Vector2.ZERO


func _player() -> Node2D:
	if current_scene == null:
		return null
	if current_scene.has_method("get_player"):
		return current_scene.call("get_player") as Node2D
	return current_scene.get_node_or_null("YSortWorld/Player") as Node2D


func _home_area() -> Node:
	if current_scene == null:
		return null
	if current_scene.has_method("get_region_loader"):
		var loader = current_scene.call("get_region_loader")
		if loader != null and loader.has_method("get_region"):
			return loader.call("get_region", "Region_HomeArea") as Node
	return current_scene.get_node_or_null("Region_HomeArea")


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
