extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")

const WORLD_SCENE_PATH := "res://scenes/world/world.tscn"
const HOME_AREA_SCENE_PATH := "res://scenes/regions/region_home_area.tscn"
const WORLD_CONTROLLER_PATH := "res://scripts/world/world_controller.gd"
const PLAYER_CONTROLLER_PATH := "res://scripts/player_controller.gd"
const INTERACTION_HINT_UI_PATH := "res://scripts/world/interaction_hint_ui.gd"
const HOME_LAYER_DIR := "res://production/assets/regions/home_area_world2d/v001/03_layer_export/four_layer_package/"
const PROTAGONIST_MAX_STANDING_HEIGHT := 218
const PROTAGONIST_MIN_STANDING_HEIGHT := 185
const PROTAGONIST_MIN_TOP_PADDING := 45
const PROTAGONIST_MAX_WIDTH := 96
const PROTAGONIST_STYLE_FRAMES := [
	"res://sprites/characters/protagonist/frames/player_idle_down_00.png",
	"res://sprites/characters/protagonist/frames/player_walk_down_00.png",
	"res://sprites/characters/protagonist/frames/player_walk_left_00.png",
	"res://sprites/characters/protagonist/frames/player_idle_up_00.png",
]

var _has_failed := false
var _finishing := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var main_scene := String(ProjectSettings.get_setting("application/run/main_scene", ""))
	_expect(main_scene == WORLD_SCENE_PATH, "project main_scene must stay on the playable world entry")
	_expect(_file_contains(WORLD_CONTROLLER_PATH, "camera_look_ahead_offset: Vector2 = Vector2(0, -280)"), "world camera must keep an upward HomeArea composition offset")
	_expect(_file_contains(WORLD_CONTROLLER_PATH, "camera_review_zoom: Vector2 = Vector2(0.68, 0.68)"), "world camera must use the pulled-back review zoom")
	_expect(_file_contains(WORLD_CONTROLLER_PATH, "camera.zoom = camera_review_zoom"), "world camera must apply review zoom")
	_expect(_file_contains(PLAYER_CONTROLLER_PATH, "\"move_left\", \"ui_left\", \"move_right\", \"ui_right\""), "player controller must read move_* actions with ui_* fallback")
	_expect(_file_contains(PLAYER_CONTROLLER_PATH, "func _update_nearest_interaction_hint()"), "player controller must continuously refresh nearest interaction hint")
	_expect(_file_contains(INTERACTION_HINT_UI_PATH, "func _create_default_hint_label()"), "InteractionHintUI must create a visible autoload prompt label")
	if _has_failed:
		return

	var packed := load(HOME_AREA_SCENE_PATH) as PackedScene
	_expect(packed != null, "could not load HomeArea scene")
	if _has_failed:
		return

	var scene := packed.instantiate()
	root.add_child(scene)
	await process_frame
	await physics_frame

	_expect(String(scene.get_meta("art_package", "")) == "home_area_world2d_v001", "HomeArea should record active World2D art package")
	_expect(String(scene.get_meta("art_integration_group", "")) == "four_layer_regenerated_scene_art", "HomeArea should record active World2D integration group")
	_expect(String(scene.get_meta("status", "")) == "home_area_world2d_four_layer_integrated", "HomeArea should stay on the World2D four-layer integration status")
	_expect(scene.get_meta("launch_quality_approved", true) == false, "HomeArea World2D package must not claim launch-quality approval")
	_expect(scene.get_meta("art_canvas", Vector2i.ZERO) == Vector2i(1470, 1070), "HomeArea should record the World2D art canvas")

	var layer_contracts := {
		"ArtLayers/SourceReferenceHidden": HOME_LAYER_DIR + "home_area_01_source.png",
		"ArtLayers/BaseGroundPaths": HOME_LAYER_DIR + "home_area_02_base_ground_paths.png",
		"ArtLayers/MidgroundBehindPlayer": HOME_LAYER_DIR + "home_area_04_midground_behind_player.png",
		"ForegroundOcclusion": HOME_LAYER_DIR + "home_area_03_foreground_occlusion_v4_no_bottom_leaf_wall.png",
	}
	for node_path in layer_contracts.keys():
		_expect(_sprite_matches_texture(scene, String(node_path), String(layer_contracts[node_path])), "HomeArea World2D layer texture mismatch: %s" % node_path)
		if _has_failed:
			return
	var source_reference := scene.get_node_or_null("ArtLayers/SourceReferenceHidden") as CanvasItem
	_expect(source_reference != null and not source_reference.visible, "HomeArea source reference must stay hidden")

	var player_sprite := scene.get_node_or_null("YSortWorld/Player/PlayerSprite") as AnimatedSprite2D
	_expect(player_sprite != null and player_sprite.sprite_frames != null, "HomeArea should use the runtime protagonist AnimatedSprite2D")
	var home_player := scene.get_node_or_null("YSortWorld/Player") as Node2D
	_expect(home_player != null and absf(float(home_player.get("visual_base_scale")) - 0.55) <= 0.01, "HomeArea protagonist runtime scale must match the World2D scene scale")
	_expect(_protagonist_frames_use_gameplay_proportions(), "protagonist frames must use compact gameplay proportions, not tall illustration proportions")

	var default_spawn := _find_spawn_marker(scene, "home_area_default")
	_expect(default_spawn != null and default_spawn.position.distance_to(Vector2(790, 622)) <= 2.0, "HomeArea default spawn should match the World2D canvas position")
	var back_spawn := _find_spawn_marker(scene, "home_area_from_back_farm")
	_expect(back_spawn != null and back_spawn.position.distance_to(Vector2(1005, 880)) <= 2.0, "HomeArea BackFarm return spawn should match the World2D canvas position")
	var back_farm_exit := scene.get_node_or_null("YSortWorld/Interactables/BackyardFarmEntrance") as Area2D
	_expect(back_farm_exit != null, "HomeArea should expose the BackFarm entrance interaction")
	if back_farm_exit != null:
		_expect(String(back_farm_exit.get("target_region_id")) == "Region_BackFarm", "BackFarm entrance target_region_id mismatch")
		_expect(String(back_farm_exit.get("target_spawn_id")) == "back_farm_default", "BackFarm entrance target_spawn_id mismatch")
		_expect(back_farm_exit.get_node_or_null("CollisionShape2D") != null, "BackFarm entrance should have a collision hotspot")

	for path in [
		HOME_LAYER_DIR + "four_layer_manifest.json",
		HOME_LAYER_DIR + "home_area_01_source.png",
		HOME_LAYER_DIR + "home_area_02_base_ground_paths.png",
		HOME_LAYER_DIR + "home_area_03_foreground_occlusion_v4_no_bottom_leaf_wall.png",
		HOME_LAYER_DIR + "home_area_04_midground_behind_player.png",
		"res://sprites/characters/protagonist/player_mvp_4dir_frames.tres",
	]:
		_expect(_asset_exists(path), "missing runtime asset: %s" % path)

	if _has_failed:
		return

	print("OK: final art experience uses playable world entry and HomeArea World2D v001 four-layer package")
	_finish_deferred(0)


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


func _sprite_matches_texture(root_node: Node, node_path: String, expected_path: String) -> bool:
	var sprite := root_node.get_node_or_null(node_path) as Sprite2D
	if sprite == null or sprite.texture == null:
		return false
	if sprite.centered:
		return false
	return sprite.texture.resource_path == expected_path and _asset_exists(expected_path)


func _asset_exists(path: String) -> bool:
	return ResourceLoader.exists(path) or FileAccess.file_exists(path)


func _file_contains(path: String, needle: String) -> bool:
	if not FileAccess.file_exists(path):
		_fail("missing file for validation: %s" % path)
		return false
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_fail("could not open file for validation: %s" % path)
		return false
	var text := file.get_as_text()
	file = null
	return text.contains(needle)


func _protagonist_frames_use_gameplay_proportions() -> bool:
	for path in PROTAGONIST_STYLE_FRAMES:
		var texture := load(path) as Texture2D
		if texture == null:
			_fail("could not load protagonist frame texture for style validation: %s" % path)
			return false
		var image := texture.get_image()
		if image == null or image.is_empty():
			_fail("could not load protagonist frame for style validation: %s" % path)
			return false
		var bounds := _alpha_bounds(image)
		if bounds.size() != 4:
			_fail("empty protagonist frame alpha: %s" % path)
			return false
		var width := int(bounds[2]) - int(bounds[0]) + 1
		var height := int(bounds[3]) - int(bounds[1]) + 1
		var top_y := int(bounds[1])
		if height < PROTAGONIST_MIN_STANDING_HEIGHT or height > PROTAGONIST_MAX_STANDING_HEIGHT:
			_fail("%s visible height %d is outside gameplay range %d-%d" % [path, height, PROTAGONIST_MIN_STANDING_HEIGHT, PROTAGONIST_MAX_STANDING_HEIGHT])
			return false
		if top_y < PROTAGONIST_MIN_TOP_PADDING:
			_fail("%s top padding %d is too small; frame reads as tall illustration art" % [path, top_y])
			return false
		if width > PROTAGONIST_MAX_WIDTH:
			_fail("%s visible width %d is too wide for the compact gameplay sprite contract" % [path, width])
			return false
	return true


func _alpha_bounds(image: Image) -> Array[int]:
	var min_x := image.get_width()
	var min_y := image.get_height()
	var max_x := -1
	var max_y := -1
	for y in range(image.get_height()):
		for x in range(image.get_width()):
			if image.get_pixel(x, y).a > 0.04:
				min_x = mini(min_x, x)
				min_y = mini(min_y, y)
				max_x = maxi(max_x, x)
				max_y = maxi(max_y, y)
	if max_x < 0:
		return []
	return [min_x, min_y, max_x, max_y]


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	_finish_deferred(1)


func _finish_deferred(exit_code: int) -> void:
	if _finishing:
		return
	_finishing = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
