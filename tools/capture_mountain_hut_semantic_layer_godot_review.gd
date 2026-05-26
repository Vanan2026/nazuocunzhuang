extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DEFAULT_OUTPUT_DIR := "res://.codex/mountain_hut_semantic_layer_godot_review"
const MOUNTAIN_HUT_LAYER_MANIFEST_PATH := "res://production/assets/regions/mountain_hut_world2d/v001/03_layer_export/layer_export_manifest.json"
const VILLAGE_V002_LAYER_MANIFEST_PATH := "res://production/assets/regions/village_world2d/v001/03_layer_export/v002_inherited/layer_export_manifest_v002.json"
const WATCHDOG_TIMEOUT_SECONDS := 45.0
const VIEWPORT_SIZE := Vector2i(1280, 720)
const SEMANTIC_LAYER_SCALE := Vector2(0.18, 0.18)

const OUTPUT_FILENAMES := {
	"overview": "01_mountain_hut_semantic_overview.png",
	"hut_door_focus": "02_hut_door_focus.png",
	"foreground_occlusion_focus": "03_foreground_occlusion_focus.png",
	"west_continuity_focus": "04_village_mountain_hut_west_continuity.png",
	"player_scale_focus": "05_mountain_hut_player_scale_focus.png",
}

const GENERATED_LAYER_NAMES: Array[String] = [
	"BaseGround",
	"TerrainDetails",
	"BehindPlayerStructures",
	"YSortPropsStructures",
	"ForegroundOcclusion",
]

const REVIEW_HIDDEN_UI_NODE_NAMES: Array[String] = [
	"TimeWeatherHUD",
	"FirstWeekQuestHUD",
	"QuestJournalUI",
	"CurrentObjectiveChip",
	"InventoryUI",
	"DialogueBox",
	"InteractionHintUI",
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
	print("PROGRESS: MountainHut semantic layer Godot review initialize")
	if not _check_only and DisplayServer.get_name() == "headless":
		_fail("MountainHut semantic layer Godot review capture requires a display server; rerun with --check-only for headless validation")
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
	main.change_scene("mountain_hut", "mountain_hut_default")
	await _settle()

	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and outdoor.has_method("get_active_region_id"), "review should load OutdoorWorld"):
		return
	if not _expect(String(outdoor.call("get_active_region_id")) == "mountain_hut", "review should activate MountainHut region"):
		return
	var mountain_hut_section := outdoor.get_node_or_null("MountainHut") as Node2D
	var village_section := outdoor.get_node_or_null("Village") as Node2D
	if not _expect(mountain_hut_section != null, "OutdoorWorld should contain MountainHut section"):
		return
	if not _expect(village_section != null, "OutdoorWorld should contain Village section"):
		return

	var mountain_hut_manifest := _load_mountain_hut_manifest()
	if mountain_hut_manifest.is_empty():
		return
	var village_manifest := _load_village_v002_reference_manifest()
	if village_manifest.is_empty():
		return
	if not _install_semantic_layers(mountain_hut_section, mountain_hut_manifest, "MountainHutSemanticLayerReview"):
		return
	if not _install_semantic_layers(village_section, village_manifest, "VillageV002SemanticLayerReference"):
		return
	if not _validate_review_runtime_state(outdoor, mountain_hut_section, village_section):
		return

	if not await _capture_overview(outdoor):
		return
	if not await _capture_hut_door_focus(outdoor, mountain_hut_section):
		return
	if not await _capture_player_scale_focus(outdoor, mountain_hut_section):
		return
	if not await _capture_foreground_occlusion_focus(outdoor, mountain_hut_section):
		return
	if not await _capture_west_continuity_focus(outdoor, mountain_hut_section, village_section):
		return

	if _check_only:
		print("OK: MountainHut semantic layer Godot review check-only validated")
	else:
		print("OK: MountainHut semantic layer Godot review screenshots saved to %s" % ProjectSettings.globalize_path(_output_dir))
	_finish_deferred(0)


func _load_mountain_hut_manifest() -> Dictionary:
	var manifest := _load_json_manifest(MOUNTAIN_HUT_LAYER_MANIFEST_PATH, "MountainHut semantic layer manifest")
	if manifest.is_empty():
		return {}
	if not _expect(manifest.get("status") == "v004_semantic_layers_exported_pending_review", "manifest must be v004_semantic_layers_exported_pending_review"):
		return {}
	if not _expect(manifest.get("runtime_replacement") is bool and manifest.get("runtime_replacement") == false, "manifest must keep runtime_replacement=false"):
		return {}
	if not _expect(manifest.get("launch_quality_approved") is bool and manifest.get("launch_quality_approved") == false, "manifest must keep launch_quality_approved=false"):
		return {}
	return manifest


func _load_village_v002_reference_manifest() -> Dictionary:
	var manifest := _load_json_manifest(VILLAGE_V002_LAYER_MANIFEST_PATH, "Village v002 semantic layer reference manifest")
	if manifest.is_empty():
		return {}
	if not _expect(manifest.get("status") == "v002_semantic_layers_exported_pending_review", "Village v002 reference manifest must be v002_semantic_layers_exported_pending_review"):
		return {}
	if not _expect(manifest.get("runtime_replacement") is bool and manifest.get("runtime_replacement") == false, "Village v002 reference must keep runtime_replacement=false"):
		return {}
	if not _expect(manifest.get("launch_quality_approved") is bool and manifest.get("launch_quality_approved") == false, "Village v002 reference must keep launch_quality_approved=false"):
		return {}
	return manifest


func _load_json_manifest(path: String, label: String) -> Dictionary:
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		_fail("missing %s: %s" % [label, path])
		return {}
	var parsed: Variant = JSON.parse_string(text)
	if not (parsed is Dictionary):
		_fail("%s is not a JSON object" % label)
		return {}
	return parsed


func _install_semantic_layers(section: Node2D, manifest: Dictionary, root_name: String) -> bool:
	# review-only integration: installed at runtime for screenshot evidence only.
	_hide_existing_generated_layers(section)
	_hide_authored_blockout_visuals(section)
	var existing := section.get_node_or_null(root_name)
	if existing != null:
		existing.queue_free()
	var root_node := Node2D.new()
	root_node.name = root_name
	root_node.z_as_relative = false
	section.add_child(root_node)

	var layers: Array = manifest.get("layers", [])
	if not _expect(layers.size() == 5, "%s expects five layer records" % root_name):
		return false
	for layer_record in layers:
		if not (layer_record is Dictionary):
			_fail("%s layer record must be object" % root_name)
			return false
		var layer: Dictionary = layer_record
		var layer_id := String(layer.get("id", ""))
		var texture := _load_png_texture("res://%s" % String(layer.get("path", "")))
		if texture == null:
			return false
		var sprite := Sprite2D.new()
		sprite.name = _sprite_name_for_layer(layer_id)
		sprite.texture = texture
		sprite.centered = false
		sprite.scale = SEMANTIC_LAYER_SCALE
		sprite.z_index = int(layer.get("z_index", 0))
		sprite.set_meta("semantic_role", String(layer.get("semantic_role", "")))
		sprite.set_meta("review_only", true)
		root_node.add_child(sprite)
	return true


func _hide_existing_generated_layers(section: Node2D) -> void:
	for layer_name in GENERATED_LAYER_NAMES:
		var node := section.get_node_or_null(layer_name)
		if node is CanvasItem:
			(node as CanvasItem).visible = false


func _hide_authored_blockout_visuals(node: Node) -> void:
	for child in node.get_children():
		if child is Polygon2D or child is Line2D or child is Label:
			(child as CanvasItem).visible = false
		_hide_authored_blockout_visuals(child)


func _load_png_texture(path: String) -> Texture2D:
	var image := Image.new()
	var error := image.load(ProjectSettings.globalize_path(path))
	if error != OK:
		_fail("could not load semantic layer PNG %s: %s" % [path, error])
		return null
	return ImageTexture.create_from_image(image)


func _validate_review_runtime_state(outdoor: Node, mountain_hut_section: Node2D, village_section: Node2D) -> bool:
	var review_root := mountain_hut_section.get_node_or_null("MountainHutSemanticLayerReview")
	var village_reference := village_section.get_node_or_null("VillageV002SemanticLayerReference")
	if not _expect(review_root != null, "MountainHut semantic review root should be installed"):
		return false
	if not _expect(village_reference != null, "Village semantic reference root should be installed"):
		return false
	var base := review_root.get_node_or_null("BaseGround") as Sprite2D
	var foreground := review_root.get_node_or_null("ForegroundOcclusion") as Sprite2D
	if not _expect(base != null and base.texture != null, "MountainHut semantic review needs BaseGround texture"):
		return false
	if not _expect(foreground != null and foreground.texture != null, "MountainHut semantic review needs ForegroundOcclusion texture"):
		return false
	if not _expect(foreground.z_index > base.z_index, "ForegroundOcclusion should render above BaseGround"):
		return false
	var spawn := mountain_hut_section.get_node_or_null("SpawnMountainHutDefault")
	if not _expect(spawn != null, "MountainHut default spawn must remain present under review art"):
		return false
	var active_id := String(outdoor.call("get_active_region_id"))
	return _expect(active_id == "mountain_hut", "OutdoorWorld must remain in MountainHut while reviewing semantic layers")


func _capture_overview(outdoor: Node) -> bool:
	var bounds: Rect2 = outdoor.call("get_region_bounds", "mountain_hut")
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for MountainHut semantic review"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(2.05, 2.05)
	camera.global_position = bounds.get_center() + Vector2(0.0, -8.0)
	await _capture_review_frame("overview")
	return not _has_failed


func _capture_hut_door_focus(outdoor: Node, mountain_hut_section: Node2D) -> bool:
	var player := _get_player(outdoor)
	if not _expect(player != null, "semantic review should have Player"):
		return false
	player.global_position = mountain_hut_section.global_position + Vector2(162.0, 104.0)
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for hut-door focus"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(3.8, 3.8)
	camera.global_position = mountain_hut_section.global_position + Vector2(162.0, 94.0)
	await _capture_review_frame("hut_door_focus")
	return not _has_failed


func _capture_player_scale_focus(outdoor: Node, mountain_hut_section: Node2D) -> bool:
	var player := _get_player(outdoor)
	if not _expect(player != null, "semantic review should have Player for player-scale focus"):
		return false
	if player is CanvasItem:
		(player as CanvasItem).visible = true
	player.global_position = mountain_hut_section.global_position + Vector2(162.0, 120.0)
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for MountainHut player-scale focus"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(4.6, 4.6)
	camera.global_position = mountain_hut_section.global_position + Vector2(162.0, 104.0)
	await _capture_review_frame("player_scale_focus")
	return not _has_failed


func _capture_foreground_occlusion_focus(outdoor: Node, mountain_hut_section: Node2D) -> bool:
	var player := _get_player(outdoor)
	if not _expect(player != null, "semantic review should have Player for foreground focus"):
		return false
	if player is CanvasItem:
		(player as CanvasItem).visible = true
	player.global_position = mountain_hut_section.global_position + Vector2(164.0, 186.0)
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for foreground focus"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(4.0, 4.0)
	camera.global_position = mountain_hut_section.global_position + Vector2(164.0, 178.0)
	await _capture_review_frame("foreground_occlusion_focus")
	return not _has_failed


func _capture_west_continuity_focus(outdoor: Node, mountain_hut_section: Node2D, village_section: Node2D) -> bool:
	var player := _get_player(outdoor)
	if player is CanvasItem:
		(player as CanvasItem).visible = false
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for west continuity focus"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(2.65, 2.65)
	var village_east_center := village_section.global_position + Vector2(324.0, 120.0)
	var mountain_hut_west_center := mountain_hut_section.global_position + Vector2(0.0, 120.0)
	camera.global_position = (village_east_center + mountain_hut_west_center) * 0.5
	await _capture_review_frame("west_continuity_focus")
	return not _has_failed


func _capture_review_frame(key: String) -> void:
	_hide_collision_debug_shapes(root)
	_hide_persistent_review_ui(root)
	await process_frame
	await process_frame
	if _check_only:
		print("OK: checked MountainHut semantic layer frame: %s" % key)
		return
	var output_path := "%s/%s" % [_output_dir, String(OUTPUT_FILENAMES.get(key, "%s.png" % key))]
	var image := root.get_texture().get_image()
	if not _validate_screenshot_image(image, key):
		return
	var error := image.save_png(output_path)
	if error != OK:
		_fail("could not save MountainHut semantic layer screenshot %s: %s" % [output_path, error])
		return
	print("OK: captured MountainHut semantic layer frame: %s" % output_path)


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


func _sprite_name_for_layer(layer_id: String) -> String:
	match layer_id:
		"base_ground":
			return "BaseGround"
		"terrain_details":
			return "TerrainDetails"
		"behind_player_structures":
			return "BehindPlayerStructures"
		"ysort_props_structures":
			return "YSortPropsStructures"
		"foreground_occlusion":
			return "ForegroundOcclusion"
		_:
			return layer_id.to_pascal_case()


func _get_world_camera(outdoor: Node) -> Camera2D:
	return outdoor.get_node_or_null("WorldCamera") as Camera2D


func _get_player(outdoor: Node) -> Node2D:
	return outdoor.get_node_or_null("Player") as Node2D


func _parse_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg == "--check-only":
			_check_only = true
		elif arg.begins_with("--output-dir="):
			_output_dir = arg.trim_prefix("--output-dir=")


func _start_watchdog() -> void:
	_watchdog_timer = Timer.new()
	_watchdog_timer.one_shot = true
	_watchdog_timer.wait_time = WATCHDOG_TIMEOUT_SECONDS
	_watchdog_timer.timeout.connect(func() -> void:
		if not _finished:
			_fail("MountainHut semantic layer Godot review timed out")
	)
	root.add_child(_watchdog_timer)
	_watchdog_timer.start()


func _settle() -> void:
	await process_frame
	await process_frame
	await create_timer(0.12).timeout
	await process_frame


func _hide_persistent_review_ui(node: Node) -> void:
	if REVIEW_HIDDEN_UI_NODE_NAMES.has(String(node.name)):
		if node is CanvasItem:
			(node as CanvasItem).visible = false
		else:
			node.set("visible", false)
	for child in node.get_children():
		_hide_persistent_review_ui(child)


func _hide_collision_debug_shapes(node: Node) -> void:
	if node is CollisionShape2D:
		(node as CollisionShape2D).visible = false
	for child in node.get_children():
		_hide_collision_debug_shapes(child)


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


func _finish_deferred(exit_code: int) -> void:
	if _finished:
		return
	_finished = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	if _watchdog_timer != null:
		_watchdog_timer.stop()
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
