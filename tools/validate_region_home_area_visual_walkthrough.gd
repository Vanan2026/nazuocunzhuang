extends SceneTree

const HOME_AREA := "res://scenes/regions/region_home_area.tscn"
const BACK_FARM := "res://scenes/regions/region_home_back_farm.tscn"
const OUTPUT_DIR := "res://.codex"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	root.size = Vector2i(1280, 720)
	root.content_scale_size = Vector2i(1280, 720)

	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT_DIR))

	await _load_scene_with_spawn(HOME_AREA, "")
	_place_player_at_marker("home_area_default")
	await _capture("region_home_area_walk_01_default_spawn.png")

	await _load_scene_with_spawn(BACK_FARM, "back_farm_from_home_area")
	await _capture("region_home_area_walk_02_back_farm_entry.png")

	await _load_scene_with_spawn(HOME_AREA, "home_area_from_back_farm")
	await _capture("region_home_area_walk_03_return_from_back_farm.png")

	_place_player(Vector2(980, 2740), Vector2.LEFT)
	await _capture("region_home_area_walk_04_foreground_grass_occlusion.png")

	print("OK: region visual walkthrough screenshots saved to %s" % ProjectSettings.globalize_path(OUTPUT_DIR))
	quit(0)


func _load_scene_with_spawn(scene_path: String, spawn_id: String) -> void:
	var transition_state := root.get_node_or_null("SceneTransitionState")
	if not spawn_id.is_empty():
		if transition_state == null:
			_fail("missing SceneTransitionState autoload")
			return
		transition_state.set_pending_transition(scene_path, spawn_id, "res://visual_walkthrough_source.tscn", "visual_walkthrough")

	var error := change_scene_to_file(scene_path)
	if error != OK:
		_fail("could not change scene to %s: %s" % [scene_path, error])
		return

	await process_frame
	await process_frame
	_snap_camera_to_player()


func _place_player_at_marker(spawn_id: String) -> void:
	var marker := _find_spawn_marker(current_scene, spawn_id)
	if marker == null:
		_fail("missing marker for visual walkthrough: %s" % spawn_id)
		return
	_place_player(marker.global_position, Vector2.DOWN)


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
	var camera := current_scene.get_node_or_null("CameraRig") as Camera2D
	if camera == null:
		return
	camera.global_position = player.global_position
	camera.reset_smoothing()
	camera.force_update_scroll()


func _player() -> Node2D:
	if current_scene == null:
		return null
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


func _fail(message: String) -> void:
	printerr("FAIL: %s" % message)
	quit(1)
