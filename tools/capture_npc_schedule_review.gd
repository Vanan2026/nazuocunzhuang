extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"
const FOREST_EDGE_PATH := "res://game/scenes/world/ForestEdge.tscn"
const DEFAULT_OUTPUT_DIR := "res://.codex/npc_schedule_review"
const WATCHDOG_TIMEOUT_SECONDS := 30.0
# Matches PlayerYard/FarmGardenZone. NPC feet inside this rect make the body read as standing in the crop beds.
const FARM_GARDEN_EXCLUSION_RECT := Rect2(Vector2(20.0, 150.0), Vector2(138.0, 92.0))
const OUTPUT_FILENAMES := {
	"yard_morning": "npc_yard_morning.png",
	"yard_late_morning": "npc_yard_late_morning.png",
	"yard_afternoon": "npc_yard_afternoon.png",
	"forest_afternoon": "npc_forest_afternoon.png",
}

var _output_dir := DEFAULT_OUTPUT_DIR
var _check_only := false
var _watchdog_timer: Timer = null
var _finished := false
var _has_failed := false


func _initialize() -> void:
	debug_collisions_hint = false
	debug_navigation_hint = false
	debug_paths_hint = false
	_parse_args()
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	print("PROGRESS: npc schedule review initialize")
	if not _check_only and DisplayServer.get_name() == "headless":
		_fail("npc schedule review capture requires a display server; rerun with --check-only for headless validation")
		return
	if not _check_only:
		DisplayServer.window_set_size(Vector2i(1280, 720))
		root.size = Vector2i(1280, 720)
		root.content_scale_size = Vector2i(1280, 720)
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(_output_dir))

	var yard := await _load_scene(PLAYER_YARD_PATH)
	if yard == null:
		return
	if not await _review_scene_state(yard, "morning", "yard_morning", ["Hana"]):
		return
	if not await _review_scene_state(yard, "late_morning", "yard_late_morning", ["Aoi", "Gen", "Mika", "Hana"]):
		return
	if not await _review_scene_state(yard, "afternoon", "yard_afternoon", ["Aoi", "Hana"]):
		return
	_remove_scene(yard)

	var forest := await _load_scene(FOREST_EDGE_PATH)
	if forest == null:
		return
	if not await _review_scene_state(forest, "afternoon", "forest_afternoon", ["Mika"]):
		return

	if _check_only:
		print("OK: npc schedule review check-only validated")
	else:
		print("OK: npc schedule review screenshots saved to %s" % ProjectSettings.globalize_path(_output_dir))
	_finish_deferred(0)


func _load_scene(scene_path: String) -> Node:
	var scene := load(scene_path) as PackedScene
	if scene == null:
		_fail("could not load scene: %s" % scene_path)
		return null
	var instance := scene.instantiate()
	root.add_child(instance)
	_hide_collision_debug_shapes(root)
	await _settle()
	return instance


func _review_scene_state(scene_root: Node, time_block: String, capture_key: String, expected_visible_names: Array[String]) -> bool:
	var schedule_director: Node = scene_root.get_node_or_null("ScheduleDirector")
	if not _expect(schedule_director != null, "%s missing ScheduleDirector" % capture_key):
		return false
	if not _set_review_time_block(scene_root, time_block, capture_key):
		return false
	if schedule_director.has_method("apply_schedule"):
		schedule_director.apply_schedule(time_block)
	await _settle()
	if not _expect_review_time_block(scene_root, time_block, capture_key):
		return false
	if not _expect_visible_npcs(scene_root, expected_visible_names, capture_key):
		return false
	return await _capture_review_frame(capture_key)


func _expect_visible_npcs(scene_root: Node, expected_visible_names: Array[String], capture_key: String) -> bool:
	var npc_root: Node = scene_root.get_node_or_null("NPCs")
	if not _expect(npc_root != null, "%s missing NPC root" % capture_key):
		return false
	var visible_npcs: Array[Node2D] = []
	for npc in npc_root.get_children():
		if npc is Node2D and bool(npc.visible):
			visible_npcs.append(npc as Node2D)
	var visible_names: Array[String] = []
	for npc in visible_npcs:
		visible_names.append(npc.name)
		var sprite := npc.get_node_or_null("Sprite2D") as Sprite2D
		if not _expect(sprite != null, "%s visible NPC missing Sprite2D: %s" % [capture_key, npc.name]):
			return false
		if not _expect(sprite.scale.x <= 0.55 and sprite.scale.y <= 0.55, "%s NPC sprite scale too large: %s" % [capture_key, npc.name]):
			return false
		if capture_key.begins_with("yard_") and not _expect(not FARM_GARDEN_EXCLUSION_RECT.has_point(npc.position), "%s visible NPC stands inside FarmGardenZone: %s at %s" % [capture_key, npc.name, npc.position]):
			return false
	if visible_names.size() != expected_visible_names.size():
		return _expect(false, "%s expected visible NPCs %s, got %s" % [capture_key, expected_visible_names, visible_names])
	for expected_name in expected_visible_names:
		if not visible_names.has(expected_name):
			return _expect(false, "%s missing expected visible NPC: %s; got %s" % [capture_key, expected_name, visible_names])
	for left_index in range(visible_npcs.size()):
		for right_index in range(left_index + 1, visible_npcs.size()):
			var left := visible_npcs[left_index]
			var right := visible_npcs[right_index]
			if not _expect(left.position.distance_to(right.position) >= 64.0, "%s visible NPCs overlap: %s/%s" % [capture_key, left.name, right.name]):
				return false
	return true


func _set_review_time_block(scene_root: Node, time_block: String, capture_key: String) -> bool:
	var target_hour := _hour_for_time_block(time_block)
	if target_hour < 0:
		return _expect(false, "%s unknown review time block: %s" % [capture_key, time_block])
	var time_manager := scene_root.get_node_or_null("TimeManager")
	if time_manager == null:
		return true
	var date_info: Dictionary = {}
	if time_manager.has_method("get_date_info"):
		date_info = time_manager.get_date_info().duplicate(true)
	date_info["hour"] = target_hour
	date_info["minute"] = 0
	if time_manager.has_method("apply_save_data"):
		time_manager.apply_save_data(date_info)
	else:
		time_manager.set("hour", target_hour)
		time_manager.set("minute", 0)
		if time_manager.has_method("_update_time_block"):
			time_manager.call("_update_time_block", false)
		if time_manager.has_signal("time_changed") and time_manager.has_method("get_date_info"):
			time_manager.time_changed.emit(time_manager.get_date_info())
	_refresh_review_hud(scene_root)
	return true


func _hour_for_time_block(time_block: String) -> int:
	match time_block:
		"morning":
			return 6
		"late_morning":
			return 9
		"afternoon":
			return 14
		"evening":
			return 18
		_:
			return -1


func _refresh_review_hud(scene_root: Node) -> void:
	var hud := scene_root.get_node_or_null("TimeWeatherHUD")
	if hud != null and hud.has_method("refresh"):
		hud.refresh()


func _expect_review_time_block(scene_root: Node, expected_time_block: String, capture_key: String) -> bool:
	var time_manager := scene_root.get_node_or_null("TimeManager")
	if time_manager == null or not time_manager.has_method("get_date_info"):
		return true
	var date_info: Dictionary = time_manager.get_date_info()
	var actual_block := String(date_info.get("block", ""))
	var time_text := String(date_info.get("time_text", ""))
	if time_manager.has_method("get_time_text"):
		time_text = String(time_manager.get_time_text())
	return _expect(actual_block == expected_time_block, "%s review time mismatch: expected %s, got %s at %s" % [capture_key, expected_time_block, actual_block, time_text])


func _capture_review_frame(capture_key: String) -> bool:
	_hide_collision_debug_shapes(root)
	await process_frame
	if _check_only:
		print("OK: checked npc schedule state: %s" % capture_key)
		return true
	var filename := String(OUTPUT_FILENAMES.get(capture_key, "npc_%s.png" % capture_key))
	var output_path := "%s/%s" % [_output_dir, filename]
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("viewport screenshot unavailable for %s" % capture_key)
		return false
	var error := image.save_png(output_path)
	if error != OK:
		_fail("could not save npc schedule screenshot %s: %s" % [output_path, error])
		return false
	print("OK: captured npc schedule frame: %s" % output_path)
	return true


func _remove_scene(scene_root: Node) -> void:
	if scene_root == null:
		return
	root.remove_child(scene_root)
	scene_root.queue_free()


func _parse_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg == "--check-only":
			_check_only = true
		elif arg.begins_with("--out="):
			_output_dir = arg.trim_prefix("--out=")


func _hide_collision_debug_shapes(node: Node) -> void:
	if node is CollisionShape2D or node is CollisionPolygon2D or node.name == "WalkableZone":
		node.visible = false
	for child in node.get_children():
		_hide_collision_debug_shapes(child)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame
	_hide_collision_debug_shapes(root)


func _expect(condition: bool, message: String) -> bool:
	if not condition:
		_fail(message)
		return false
	return true


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
			_fail("npc schedule review timed out")
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
