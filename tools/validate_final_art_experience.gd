extends SceneTree

const WORLD_SCENE_PATH := "res://scenes/world/world.tscn"
const HOME_AREA_SCENE_PATH := "res://scenes/regions/region_home_area.tscn"
const WORLD_CONTROLLER_PATH := "res://scripts/world/world_controller.gd"
const PLAYER_CONTROLLER_PATH := "res://scripts/player_controller.gd"
const INTERACTION_HINT_UI_PATH := "res://scripts/world/interaction_hint_ui.gd"
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


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var main_scene := String(ProjectSettings.get_setting("application/run/main_scene", ""))
	_expect(main_scene == WORLD_SCENE_PATH, "project main_scene must stay on the playable world entry")
	_expect(_file_contains(WORLD_CONTROLLER_PATH, "camera_look_ahead_offset: Vector2 = Vector2(0, -280)"), "world camera must keep an upward HomeArea composition offset")
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

	_expect(String(scene.get_meta("art_package", "")) == "home_area_art_v003", "HomeArea should record active art package")
	_expect(String(scene.get_meta("art_integration_group", "")) == "foundation_depth_v003", "HomeArea should record active art integration group")
	_expect(_sprite_has_texture(scene, "TileMapLayer_Ground/GroundModules/GroundYardArtV003"), "HomeArea should use v003 ground art")
	_expect(_sprite_has_texture(scene, "TileMapLayer_Path/PathModules/VillageRoadArtV003"), "HomeArea should use v003 village road art")
	_expect(_sprite_has_texture(scene, "TileMapLayer_Path/PathModules/BackFarmPathArtV003"), "HomeArea should use v003 BackFarm path art")
	_expect(_sprite_has_texture(scene, "TileMapLayer_Detail/VerandaFloorArtV003"), "HomeArea should use v003 veranda floor art")
	_expect(_sprite_has_texture(scene, "YSortWorld/Houses/CloudHouse/HouseBodyArtV003"), "HomeArea should use v003 house body art")
	_expect(_sprite_has_texture(scene, "YSortWorld/Trees/BigShadeTree/TreeLeftTrunkArtV003"), "HomeArea should use v003 left tree trunk art")
	_expect(_sprite_has_texture(scene, "YSortWorld/Trees/PersimmonTree/TreeRightTrunkArtV003"), "HomeArea should use v003 right tree trunk art")
	_expect(_sprite_has_texture(scene, "ForegroundStatic/Occluders/HouseRoofOccluderArtV003"), "HomeArea should use v003 house roof occluder art")
	_expect(_sprite_has_texture(scene, "ForegroundStatic/Occluders/TreeLeftCanopyOccluderArtV003"), "HomeArea should use v003 left canopy occluder art")
	_expect(_sprite_has_texture(scene, "ForegroundStatic/Occluders/TreeRightCanopyOccluderArtV003"), "HomeArea should use v003 right canopy occluder art")
	_expect(_sprite_has_texture(scene, "ForegroundStatic/ForegroundGrassArtV003"), "HomeArea should use v003 foreground grass art")
	_expect(_sprite_has_texture(scene, "LightAndWeather/ShadowDappledArtV003"), "HomeArea should use v003 dappled shadow art")
	_expect(_sprite_has_texture(scene, "LightAndWeather/LightOverlayArtV003"), "HomeArea should use v003 light overlay art")
	var prop_checks := {
		"YSortWorld/Props/Mailbox/MailboxArt": "res://assets/art/props/region_home_area_prop_mailbox_v001.png",
		"YSortWorld/Props/Well/WellArt": "res://assets/art/props/region_home_area_prop_well_broken_v001.png",
		"YSortWorld/Props/Bench/BenchArt": "res://assets/art/props/region_home_area_prop_bench_v001.png",
		"YSortWorld/Props/RoadSign/RoadSignArt": "res://assets/art/props/region_home_area_prop_road_sign_v001.png",
	}
	for sprite_path in prop_checks.keys():
		_expect(_runtime_prop_sprite_loads(scene, String(sprite_path), String(prop_checks[sprite_path])), "HomeArea runtime prop art should load: %s" % sprite_path)
		if _has_failed:
			return

	var prop_blockers := {
		"YSortWorld/Props/Mailbox/PropBlocker/CollisionShape2D": Vector2(70, 44),
		"YSortWorld/Props/Well/PropBlocker/CollisionShape2D": Vector2(140, 88),
		"YSortWorld/Props/Bench/PropBlocker/CollisionShape2D": Vector2(160, 40),
		"YSortWorld/Props/RoadSign/PropBlocker/CollisionShape2D": Vector2(48, 40),
	}
	for blocker_path in prop_blockers.keys():
		_expect(_rectangle_shape_at_least(scene, String(blocker_path), prop_blockers[blocker_path]), "HomeArea prop blocker should be sized for walking playtest: %s" % blocker_path)
		if _has_failed:
			return

	var cat_bed := scene.get_node_or_null("YSortWorld/Props/CatBed") as CanvasItem
	_expect(cat_bed != null and cat_bed.visible, "CatBed should be visible after runtime prop art is available")
	_expect(_runtime_prop_sprite_loads(scene, "YSortWorld/Props/CatBed/CatBedArt", "res://assets/art/props/region_home_area_prop_cat_bed_v001.png"), "CatBed runtime prop art should load")
	var cat_bed_graybox := scene.get_node_or_null("YSortWorld/Props/CatBed/Cushion") as CanvasItem
	_expect(cat_bed_graybox != null and not cat_bed_graybox.visible, "CatBed graybox cushion must stay hidden")

	var player_sprite := scene.get_node_or_null("YSortWorld/Player/PlayerSprite") as AnimatedSprite2D
	_expect(player_sprite != null and player_sprite.sprite_frames != null, "HomeArea should use the runtime protagonist AnimatedSprite2D")
	_expect(_protagonist_frames_use_gameplay_proportions(), "protagonist frames must use compact gameplay proportions, not tall illustration proportions")
	var house_door := scene.get_node_or_null("YSortWorld/Interactables/HouseDoorEntrance") as Area2D
	_expect(house_door != null and house_door.position.distance_to(Vector2(3300, 1900)) <= 48.0, "HomeArea default spawn must have a reachable launch interaction")

	for path in [
		"res://production/assets/regions/home_area_art/v003/region_home_area_ground_yard_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_path_village_road_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_path_back_farm_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_house_body_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_house_roof_occluder_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_veranda_floor_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_tree_left_trunk_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_tree_left_canopy_occluder_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_tree_right_trunk_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_tree_right_canopy_occluder_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_foreground_grass_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_shadow_dappled_v003.png",
		"res://production/assets/regions/home_area_art/v003/region_home_area_light_overlay_v003.png",
		"res://assets/art/props/region_home_area_prop_mailbox_v001.png",
		"res://assets/art/props/region_home_area_prop_well_broken_v001.png",
		"res://assets/art/props/region_home_area_prop_bench_v001.png",
		"res://assets/art/props/region_home_area_prop_road_sign_v001.png",
		"res://assets/art/props/region_home_area_prop_cat_bed_v001.png",
		"res://sprites/characters/protagonist/player_mvp_4dir_frames.tres",
	]:
		_expect(_asset_exists(path), "missing runtime asset: %s" % path)

	if _has_failed:
		return

	print("OK: final art experience uses playable world entry and HomeArea v003 foundation/depth layers")
	quit(0)


func _sprite_has_texture(root_node: Node, node_path: String) -> bool:
	var sprite := root_node.get_node_or_null(node_path) as Sprite2D
	return sprite != null and sprite.texture != null


func _runtime_prop_sprite_loads(root_node: Node, node_path: String, expected_path: String) -> bool:
	var sprite := root_node.get_node_or_null(node_path) as Sprite2D
	if sprite == null:
		return false
	if sprite.has_method("refresh_texture"):
		sprite.refresh_texture()
	return sprite.texture != null and String(sprite.get("texture_path")) == expected_path and _asset_exists(expected_path)


func _asset_exists(path: String) -> bool:
	return ResourceLoader.exists(path) or FileAccess.file_exists(path)


func _rectangle_shape_at_least(root_node: Node, node_path: String, min_size: Vector2) -> bool:
	var collision := root_node.get_node_or_null(node_path) as CollisionShape2D
	if collision == null:
		return false
	var shape := collision.shape as RectangleShape2D
	if shape == null:
		return false
	return shape.size.x >= min_size.x and shape.size.y >= min_size.y


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
	quit(1)
