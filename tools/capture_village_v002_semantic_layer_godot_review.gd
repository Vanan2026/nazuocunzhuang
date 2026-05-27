extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DEFAULT_OUTPUT_DIR := "res://.codex/village_v002_semantic_layer_godot_review"
const V003_OUTPUT_DIR := "res://.codex/village_v003_semantic_layer_godot_review"
const LAYER_MANIFEST_PATH := "res://production/assets/regions/village_world2d/v001/03_layer_export/v002_inherited/layer_export_manifest_v002.json"
const V003_LAYER_MANIFEST_PATH := "res://production/assets/regions/village_world2d/v001/03_layer_export/v003_edge_continuity/layer_export_manifest_v003.json"
const MOUNTAIN_HUT_LAYER_MANIFEST_PATH := "res://production/assets/regions/mountain_hut_world2d/v001/03_layer_export/layer_export_manifest.json"
const WATCHDOG_TIMEOUT_SECONDS := 45.0
const VIEWPORT_SIZE := Vector2i(1280, 720)
const SEMANTIC_LAYER_SCALE := Vector2(0.18, 0.18)

const OUTPUT_FILENAMES := {
	"overview": "01_village_v002_semantic_overview.png",
	"old_maple_occlusion_focus": "02_village_v002_old_maple_occlusion_focus.png",
	"notice_stall_focus": "03_village_v002_notice_stall_focus.png",
	"east_continuity_focus": "04_village_v002_east_continuity_focus.png",
	"inherited_edge_focus": "05_village_v002_inherited_edge_focus.png",
	"player_scale_focus": "06_village_v002_player_scale_focus.png",
}

const V003_OUTPUT_FILENAMES := {
	"overview": "01_village_v003_semantic_overview.png",
	"old_maple_occlusion_focus": "02_village_v003_old_maple_occlusion_focus.png",
	"notice_stall_focus": "03_village_v003_notice_stall_focus.png",
	"east_continuity_focus": "04_village_v003_east_continuity_focus.png",
	"inherited_edge_focus": "05_village_v003_inherited_edge_focus.png",
	"player_scale_focus": "06_village_v003_player_scale_focus.png",
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
var _use_v3 := false
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
	print("PROGRESS: %s semantic layer Godot review initialize" % _review_label())
	if not _check_only and DisplayServer.get_name() == "headless":
		_fail("%s semantic layer Godot review capture requires a display server; rerun with --check-only for headless validation" % _review_label())
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
	main.change_scene("village", "village_default")
	await _settle()

	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and outdoor.has_method("get_active_region_id"), "review should load OutdoorWorld"):
		return
	if not _expect(String(outdoor.call("get_active_region_id")) == "village", "review should activate Village region"):
		return
	var village_section := outdoor.get_node_or_null("Village") as Node2D
	var mountain_hut_section := outdoor.get_node_or_null("MountainHut") as Node2D
	if not _expect(village_section != null, "OutdoorWorld should contain Village section"):
		return
	if not _expect(mountain_hut_section != null, "OutdoorWorld should contain MountainHut section for current adjacent reference"):
		return

	var manifest := _load_layer_manifest()
	if manifest.is_empty():
		return
	var mountain_hut_manifest := _load_mountain_hut_reference_manifest()
	if mountain_hut_manifest.is_empty():
		return
	if not _install_semantic_layers(village_section, manifest, _review_root_name()):
		return
	if not _install_semantic_layers(mountain_hut_section, mountain_hut_manifest, "MountainHutSemanticLayerReference"):
		return
	if not _validate_review_runtime_state(outdoor, village_section):
		return

	if not await _capture_overview(outdoor):
		return
	if not await _capture_old_maple_focus(outdoor, village_section):
		return
	if not await _capture_notice_stall_focus(outdoor, village_section):
		return
	if not await _capture_player_scale_focus(outdoor, village_section):
		return
	if not await _capture_east_continuity_focus(outdoor, village_section):
		return
	if not await _capture_inherited_edge_focus(outdoor, village_section):
		return

	if _check_only:
		print("OK: %s semantic layer Godot review check-only validated" % _review_label())
	else:
		print("OK: %s semantic layer Godot review screenshots saved to %s" % [_review_label(), ProjectSettings.globalize_path(_output_dir)])
	_finish_deferred(0)


func _load_layer_manifest() -> Dictionary:
	var manifest_path := _layer_manifest_path()
	var text := FileAccess.get_file_as_string(manifest_path)
	if text.is_empty():
		_fail("missing %s semantic layer manifest: %s" % [_review_label(), manifest_path])
		return {}
	var parsed: Variant = JSON.parse_string(text)
	if not (parsed is Dictionary):
		_fail("%s semantic layer manifest is not a JSON object" % _review_label())
		return {}
	var manifest: Dictionary = parsed
	var expected_status := _expected_manifest_status()
	if not _expect(manifest.get("status") == expected_status, "manifest must be %s" % expected_status):
		return {}
	if not _expect(manifest.get("runtime_replacement") is bool and manifest.get("runtime_replacement") == false, "manifest must keep runtime_replacement=false"):
		return {}
	if not _expect(manifest.get("launch_quality_approved") is bool and manifest.get("launch_quality_approved") == false, "manifest must keep launch_quality_approved=false"):
		return {}
	return manifest


func _load_mountain_hut_reference_manifest() -> Dictionary:
	var text := FileAccess.get_file_as_string(MOUNTAIN_HUT_LAYER_MANIFEST_PATH)
	if text.is_empty():
		_fail("missing MountainHut semantic layer reference manifest: %s" % MOUNTAIN_HUT_LAYER_MANIFEST_PATH)
		return {}
	var parsed: Variant = JSON.parse_string(text)
	if not (parsed is Dictionary):
		_fail("MountainHut semantic layer reference manifest is not a JSON object")
		return {}
	var manifest: Dictionary = parsed
	if not _expect(manifest.get("status") == "v004_semantic_layers_exported_pending_review", "MountainHut reference manifest must be v004_semantic_layers_exported_pending_review"):
		return {}
	if not _expect(manifest.get("runtime_replacement") is bool and manifest.get("runtime_replacement") == false, "MountainHut reference must keep runtime_replacement=false"):
		return {}
	if not _expect(manifest.get("launch_quality_approved") is bool and manifest.get("launch_quality_approved") == false, "MountainHut reference must keep launch_quality_approved=false"):
		return {}
	return manifest


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
			_fail("%s semantic layer record must be object" % root_name)
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


func _hide_existing_generated_layers(village_section: Node2D) -> void:
	for layer_name in GENERATED_LAYER_NAMES:
		var node := village_section.get_node_or_null(layer_name)
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
		_fail("could not load Village v002 semantic layer PNG %s: %s" % [path, error])
		return null
	return ImageTexture.create_from_image(image)


func _validate_review_runtime_state(outdoor: Node, village_section: Node2D) -> bool:
	var review_root := village_section.get_node_or_null(_review_root_name())
	if not _expect(review_root != null, "Village v002 semantic review root should be installed"):
		return false
	var base := review_root.get_node_or_null("BaseGround") as Sprite2D
	var foreground := review_root.get_node_or_null("ForegroundOcclusion") as Sprite2D
	if not _expect(base != null and base.texture != null, "Village v002 semantic review needs BaseGround texture"):
		return false
	if not _expect(foreground != null and foreground.texture != null, "Village v002 semantic review needs ForegroundOcclusion texture"):
		return false
	if not _expect(foreground.z_index > base.z_index, "ForegroundOcclusion should render above BaseGround"):
		return false
	var notice := village_section.get_node_or_null("VillageNotice")
	var stall := village_section.get_node_or_null("SeedStallProxy")
	var old_maple := village_section.get_node_or_null("OldMapleClue")
	if not _expect(notice != null and stall != null and old_maple != null, "Village interactables must remain present under v002 review art"):
		return false
	var active_id := String(outdoor.call("get_active_region_id"))
	return _expect(active_id == "village", "OutdoorWorld must remain in Village while reviewing v002 semantic layers")


func _capture_overview(outdoor: Node) -> bool:
	var bounds: Rect2 = outdoor.call("get_region_bounds", "village")
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for Village v002 semantic review"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(2.05, 2.05)
	camera.global_position = bounds.get_center() + Vector2(0.0, -4.0)
	await _capture_review_frame("overview")
	return not _has_failed


func _capture_old_maple_focus(outdoor: Node, village_section: Node2D) -> bool:
	var player := _get_player(outdoor)
	if not _expect(player != null, "Village v002 semantic review should have Player"):
		return false
	if player is CanvasItem:
		(player as CanvasItem).visible = true
	player.global_position = village_section.global_position + Vector2(224.0, 190.0)
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for old-maple focus"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(3.45, 3.45)
	camera.global_position = village_section.global_position + Vector2(236.0, 174.0)
	await _capture_review_frame("old_maple_occlusion_focus")
	return not _has_failed


func _capture_notice_stall_focus(outdoor: Node, village_section: Node2D) -> bool:
	var player := _get_player(outdoor)
	if not _expect(player != null, "Village v002 semantic review should have Player for notice focus"):
		return false
	if player is CanvasItem:
		(player as CanvasItem).visible = true
	player.global_position = village_section.global_position + Vector2(164.0, 112.0)
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for notice focus"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(3.8, 3.8)
	camera.global_position = village_section.global_position + Vector2(164.0, 100.0)
	await _capture_review_frame("notice_stall_focus")
	return not _has_failed


func _capture_player_scale_focus(outdoor: Node, village_section: Node2D) -> bool:
	var player := _get_player(outdoor)
	if not _expect(player != null, "Village v002 semantic review should have Player for player-scale focus"):
		return false
	if player is CanvasItem:
		(player as CanvasItem).visible = true
	player.global_position = village_section.global_position + Vector2(166.0, 146.0)
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for Village player-scale focus"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(4.4, 4.4)
	camera.global_position = village_section.global_position + Vector2(166.0, 130.0)
	await _capture_review_frame("player_scale_focus")
	return not _has_failed


func _capture_east_continuity_focus(outdoor: Node, village_section: Node2D) -> bool:
	var mountain_hut_section := outdoor.get_node_or_null("MountainHut") as Node2D
	if not _expect(mountain_hut_section != null, "OutdoorWorld should contain MountainHut section for east continuity review"):
		return false
	var player := _get_player(outdoor)
	if not _expect(player != null, "Village v002 semantic review should have Player for east continuity focus"):
		return false
	if player is CanvasItem:
		(player as CanvasItem).visible = false
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for east continuity focus"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(2.65, 2.65)
	var village_east_center := village_section.global_position + Vector2(324.0, 120.0)
	var mountain_hut_west_center := mountain_hut_section.global_position + Vector2(0.0, 120.0)
	camera.global_position = (village_east_center + mountain_hut_west_center) * 0.5
	await _capture_review_frame("east_continuity_focus")
	return not _has_failed


func _capture_inherited_edge_focus(outdoor: Node, village_section: Node2D) -> bool:
	var player := _get_player(outdoor)
	if not _expect(player != null, "Village v002 semantic review should have Player for inherited-edge focus"):
		return false
	if player is CanvasItem:
		(player as CanvasItem).visible = false
	var camera := _get_world_camera(outdoor)
	if not _expect(camera != null, "OutdoorWorld should expose WorldCamera for inherited-edge focus"):
		return false
	camera.enabled = true
	camera.make_current()
	camera.zoom = Vector2(3.0, 3.0)
	camera.global_position = village_section.global_position + Vector2(58.0, 48.0)
	await _capture_review_frame("inherited_edge_focus")
	return not _has_failed


func _capture_review_frame(key: String) -> void:
	_hide_collision_debug_shapes(root)
	_hide_persistent_review_ui(root)
	await process_frame
	await process_frame
	if _check_only:
		print("OK: checked %s semantic layer frame: %s" % [_review_label(), key])
		return
	var output_path := "%s/%s" % [_output_dir, String(_output_filenames().get(key, "%s.png" % key))]
	var image := root.get_texture().get_image()
	if not _validate_screenshot_image(image, key):
		return
	var error := image.save_png(output_path)
	if error != OK:
		_fail("could not save %s semantic layer screenshot %s: %s" % [_review_label(), output_path, error])
		return
	print("OK: captured %s semantic layer frame: %s" % [_review_label(), output_path])


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
		elif arg == "--v3":
			_use_v3 = true
			_output_dir = V003_OUTPUT_DIR
		elif arg.begins_with("--output-dir="):
			_output_dir = arg.trim_prefix("--output-dir=")



func _review_label() -> String:
	return "Village v003" if _use_v3 else "Village v002"


func _review_root_name() -> String:
	return "VillageV003SemanticLayerReview" if _use_v3 else "VillageV002SemanticLayerReview"


func _layer_manifest_path() -> String:
	return V003_LAYER_MANIFEST_PATH if _use_v3 else LAYER_MANIFEST_PATH


func _expected_manifest_status() -> String:
	return "v003_semantic_layers_exported_pending_review" if _use_v3 else "v002_semantic_layers_exported_pending_review"


func _output_filenames() -> Dictionary:
	return V003_OUTPUT_FILENAMES if _use_v3 else OUTPUT_FILENAMES

func _start_watchdog() -> void:
	_watchdog_timer = Timer.new()
	_watchdog_timer.one_shot = true
	_watchdog_timer.wait_time = WATCHDOG_TIMEOUT_SECONDS
	_watchdog_timer.timeout.connect(func() -> void:
		if not _finished:
			_fail("Village v002 semantic layer Godot review timed out")
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
