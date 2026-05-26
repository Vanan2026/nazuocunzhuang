extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DEFAULT_OUTPUT_DIR := "res://.codex/outdoor_world_visual_calibration"
const WATCHDOG_TIMEOUT_SECONDS := 45.0
const VIEWPORT_SIZE := Vector2i(1600, 900)
const OVERVIEW_PADDING := Vector2(160.0, 120.0)
const OVERVIEW_MAX_ZOOM := 0.9
const REGION_CLOSEUP_ZOOM := Vector2(2.25, 2.25)

const REVIEW_HIDDEN_UI_NODE_NAMES: Array[String] = [
	"TimeWeatherHUD",
	"FirstWeekQuestHUD",
	"QuestJournalUI",
	"CurrentObjectiveChip",
	"InventoryUI",
	"DialogueBox",
]

const VISUAL_REVIEW_REGION_IDS: Array[String] = [
	"player_yard",
	"forest_edge",
	"village",
	"back_farm",
	"orchard",
	"pond",
	"mountain_path",
	"mountain_hut",
	"mountain",
	"cliff_view",
]

const GENERATED_REGION_NODE_NAMES: Dictionary = {
	"village": "Village",
	"back_farm": "BackFarm",
	"orchard": "Orchard",
	"pond": "Pond",
	"mountain_path": "MountainPath",
	"mountain_hut": "MountainHut",
	"mountain": "Mountain",
	"cliff_view": "CliffView",
}

const OUTPUT_FILENAMES: Dictionary = {
	"overview": "outdoor_world_overview.png",
	"player_yard": "outdoor_region_player_yard.png",
	"forest_edge": "outdoor_region_forest_edge.png",
	"village": "outdoor_region_village.png",
	"back_farm": "outdoor_region_back_farm.png",
	"orchard": "outdoor_region_orchard.png",
	"pond": "outdoor_region_pond.png",
	"mountain_path": "outdoor_region_mountain_path.png",
	"mountain_hut": "outdoor_region_mountain_hut.png",
	"mountain": "outdoor_region_mountain.png",
	"cliff_view": "outdoor_region_cliff_view.png",
}

const CONNECTIONS: Array[Array] = [
	["player_yard", "forest_edge"],
	["forest_edge", "village"],
	["player_yard", "back_farm"],
	["forest_edge", "orchard"],
	["orchard", "pond"],
	["village", "pond"],
	["village", "mountain_path"],
	["village", "mountain_hut"],
	["mountain_path", "mountain"],
	["mountain", "cliff_view"],
	["mountain", "mountain_hut"],
	["mountain_hut", "pond"],
]

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
	print("PROGRESS: outdoor world visual calibration initialize")
	if not _check_only and DisplayServer.get_name() == "headless":
		_fail("outdoor world visual calibration capture requires a display server; rerun with --check-only for headless validation")
		return
	if not _check_only:
		DisplayServer.window_set_size(VIEWPORT_SIZE)
		root.size = VIEWPORT_SIZE
		root.content_scale_size = VIEWPORT_SIZE
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(_output_dir))

	var main_scene := load(MAIN_PATH) as PackedScene
	if main_scene == null:
		_fail("could not load Main scene")
		return

	var main := main_scene.instantiate()
	root.add_child(main)
	await _settle()
	main.change_scene("player_yard", "from_house")
	await _settle()

	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and outdoor.has_method("get_outdoor_region_ids"), "Main should load OutdoorWorld for visual calibration"):
		return
	if not _validate_region_layout_contract(outdoor):
		return
	_install_calibration_overlay(outdoor)

	if not await _capture_overview(outdoor):
		return
	for region_id in VISUAL_REVIEW_REGION_IDS:
		if not await _capture_region_closeup(main, outdoor, region_id):
			return

	if _check_only:
		print("OK: outdoor world visual calibration check-only validated")
	else:
		print("OK: outdoor world visual calibration screenshots saved to %s" % ProjectSettings.globalize_path(_output_dir))
	_finish_deferred(0)


func _validate_region_layout_contract(outdoor: Node) -> bool:
	var ground_fill := outdoor.get_node_or_null("OutdoorGroundFill") as Polygon2D
	if not _expect(ground_fill != null, "OutdoorWorld visual review should include OutdoorGroundFill"):
		return false
	if not _expect(ground_fill.polygon.size() >= 4, "OutdoorGroundFill should cover the world review rect"):
		return false
	var region_ids: Array = outdoor.call("get_outdoor_region_ids")
	for region_id in VISUAL_REVIEW_REGION_IDS:
		if not _expect(region_ids.has(region_id), "OutdoorWorld missing visual review region id: %s" % region_id):
			return false
		var bounds: Rect2 = outdoor.call("get_region_bounds", region_id)
		if not _expect(bounds.has_area(), "OutdoorWorld region should expose non-empty visual bounds: %s" % region_id):
			return false
		var spawn_id := String(outdoor.call("get_active_spawn_id"))
		if region_id != String(outdoor.call("get_active_region_id")):
			spawn_id = _default_spawn_for_region(region_id)
		if not _expect(not spawn_id.is_empty(), "OutdoorWorld visual review should resolve a spawn id for: %s" % region_id):
			return false
		if GENERATED_REGION_NODE_NAMES.has(region_id):
			var section := outdoor.get_node_or_null(String(GENERATED_REGION_NODE_NAMES[region_id]))
			if not _expect(section != null, "generated region section missing: %s" % region_id):
				return false
			var base := section.get_node_or_null("BaseGround") as Sprite2D
			if not _expect(base != null and base.texture != null, "generated region missing BaseGround texture: %s" % region_id):
				return false
	return _validate_region_connections(outdoor)


func _validate_region_connections(outdoor: Node) -> bool:
	for pair in CONNECTIONS:
		var from_id := String(pair[0])
		var to_id := String(pair[1])
		var from_bounds: Rect2 = outdoor.call("get_region_bounds", from_id)
		var to_bounds: Rect2 = outdoor.call("get_region_bounds", to_id)
		var center_distance := from_bounds.get_center().distance_to(to_bounds.get_center())
		if not _expect(center_distance <= 560.0, "outdoor visual seam too far: %s -> %s distance %.1f" % [from_id, to_id, center_distance]):
			return false
	return true


func _capture_overview(outdoor: Node) -> bool:
	var world_rect := _get_world_visual_rect(outdoor)
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for overview capture"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.global_position = world_rect.get_center()
	camera.zoom = _overview_zoom_for_rect(world_rect)
	await _capture_review_frame("overview")
	return not _has_failed


func _capture_region_closeup(main: Node, outdoor: Node, region_id: String) -> bool:
	main.change_scene(region_id, "default")
	await _settle()
	if not _expect(main.get_current_gameplay_scene() == outdoor, "region closeup should reuse OutdoorWorld: %s" % region_id):
		return false
	if not _expect(String(outdoor.call("get_active_region_id")) == region_id, "region closeup should activate: %s" % region_id):
		return false
	var bounds: Rect2 = outdoor.call("get_region_bounds", region_id)
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for region capture"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = REGION_CLOSEUP_ZOOM
	camera.global_position = bounds.get_center() + Vector2(0.0, -24.0)
	await _capture_review_frame(region_id)
	return not _has_failed


func _capture_review_frame(key: String) -> void:
	_hide_collision_debug_shapes(root)
	_hide_persistent_review_ui(root)
	await process_frame
	await process_frame
	if _check_only:
		print("OK: checked outdoor visual calibration frame: %s" % key)
		return
	var filename := String(OUTPUT_FILENAMES.get(key, "outdoor_%s.png" % key))
	var output_path := "%s/%s" % [_output_dir, filename]
	var image := root.get_texture().get_image()
	if not _validate_screenshot_image(image, key):
		return
	var error := image.save_png(output_path)
	if error != OK:
		_fail("could not save outdoor visual calibration screenshot %s: %s" % [output_path, error])
		return
	print("OK: captured outdoor visual calibration frame: %s" % output_path)


func _validate_screenshot_image(image: Image, key: String) -> bool:
	if image == null or image.is_empty():
		_fail("viewport screenshot unavailable for %s" % key)
		return false
	var width := image.get_width()
	var height := image.get_height()
	if not _expect(width >= 640 and height >= 360, "%s screenshot is too small: %sx%s" % [key, width, height]):
		return false
	var samples := 0
	var varied_samples := 0
	var reference := image.get_pixel(width / 2, height / 2)
	for x in range(0, width, max(width / 16, 1)):
		for y in range(0, height, max(height / 9, 1)):
			samples += 1
			var color := image.get_pixel(x, y)
			if abs(color.r - reference.r) + abs(color.g - reference.g) + abs(color.b - reference.b) > 0.05:
				varied_samples += 1
	return _expect(samples > 0 and varied_samples >= 8, "%s screenshot appears too visually flat for review" % key)


func _install_calibration_overlay(outdoor: Node) -> void:
	var existing := outdoor.get_node_or_null("OutdoorVisualCalibrationOverlay")
	if existing != null:
		existing.queue_free()
	var overlay := Node2D.new()
	overlay.name = "OutdoorVisualCalibrationOverlay"
	overlay.z_index = 200
	outdoor.add_child(overlay)
	for pair in CONNECTIONS:
		var connection := Line2D.new()
		connection.name = "Connection_%s_%s" % [String(pair[0]), String(pair[1])]
		var from_bounds: Rect2 = outdoor.call("get_region_bounds", String(pair[0]))
		var to_bounds: Rect2 = outdoor.call("get_region_bounds", String(pair[1]))
		connection.points = PackedVector2Array([from_bounds.get_center(), to_bounds.get_center()])
		connection.width = 3.0
		connection.default_color = Color(0.26, 0.18, 0.09, 0.72)
		overlay.add_child(connection)
	for region_id in VISUAL_REVIEW_REGION_IDS:
		var bounds: Rect2 = outdoor.call("get_region_bounds", region_id)
		var outline := Line2D.new()
		outline.name = "Bounds_%s" % region_id
		outline.points = PackedVector2Array([
			bounds.position,
			Vector2(bounds.end.x, bounds.position.y),
			bounds.end,
			Vector2(bounds.position.x, bounds.end.y),
			bounds.position,
		])
		outline.width = 2.0
		outline.default_color = Color(0.10, 0.32, 0.26, 0.86)
		overlay.add_child(outline)
		var label := Label.new()
		label.name = "Label_%s" % region_id
		label.text = region_id
		label.position = bounds.position + Vector2(8.0, 8.0)
		label.scale = Vector2(0.55, 0.55)
		label.add_theme_color_override("font_color", Color(0.08, 0.13, 0.10, 1.0))
		overlay.add_child(label)


func _get_world_visual_rect(outdoor: Node) -> Rect2:
	var has_rect := false
	var result := Rect2()
	for region_id in VISUAL_REVIEW_REGION_IDS:
		var bounds: Rect2 = outdoor.call("get_region_bounds", region_id)
		if not has_rect:
			result = bounds
			has_rect = true
		else:
			result = result.merge(bounds)
	return result.grow_individual(OVERVIEW_PADDING.x, OVERVIEW_PADDING.y, OVERVIEW_PADDING.x, OVERVIEW_PADDING.y)


func _overview_zoom_for_rect(world_rect: Rect2) -> Vector2:
	var zoom_x: float = float(VIEWPORT_SIZE.x) / max(world_rect.size.x, 1.0)
	var zoom_y: float = float(VIEWPORT_SIZE.y) / max(world_rect.size.y, 1.0)
	var zoom: float = min(zoom_x, zoom_y, OVERVIEW_MAX_ZOOM)
	return Vector2(zoom, zoom)


func _get_world_camera(outdoor: Node) -> Camera2D:
	return outdoor.get_node_or_null("WorldCamera") as Camera2D


func _default_spawn_for_region(region_id: String) -> String:
	match region_id:
		"player_yard":
			return "from_house"
		"forest_edge":
			return "from_yard"
		_:
			return "%s_default" % region_id


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


func _hide_persistent_review_ui(node: Node) -> void:
	if REVIEW_HIDDEN_UI_NODE_NAMES.has(String(node.name)):
		if node is CanvasItem:
			(node as CanvasItem).visible = false
		elif node is CanvasLayer:
			(node as CanvasLayer).visible = false
	for child in node.get_children():
		_hide_persistent_review_ui(child)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame
	_hide_collision_debug_shapes(root)
	_hide_persistent_review_ui(root)


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
			_fail("outdoor world visual calibration timed out")
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
