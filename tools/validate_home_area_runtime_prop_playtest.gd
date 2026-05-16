extends SceneTree

const WORLD_SCENE_PATH := "res://scenes/world/world.tscn"
const EXPECTED_MAIN_SCENE := "res://scenes/world/world.tscn"
const INTERACTION_RANGE := 64.0

var _has_failed := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var main_scene := String(ProjectSettings.get_setting("application/run/main_scene", ""))
	_expect(main_scene == EXPECTED_MAIN_SCENE, "project main_scene must stay on world.tscn for HomeArea prop playtest")

	var packed := load(WORLD_SCENE_PATH) as PackedScene
	_expect(packed != null, "could not load world scene")
	if _has_failed:
		return

	var world := packed.instantiate()
	root.add_child(world)
	await process_frame
	await process_frame
	await physics_frame

	var player := _get_world_player(world)
	_expect(player != null, "world should expose a player after initialization")
	var home_area := _get_home_area(world)
	_expect(home_area != null, "world should load Region_HomeArea through RegionLoader")
	var camera := _get_world_camera(world)
	_expect(camera != null, "world should expose a runtime camera")
	if _has_failed:
		return

	_expect(player.global_position.distance_to(Vector2(7300, 7900)) <= 2.0, "player should spawn at HomeArea default spawn through world route")
	_expect(camera.global_position.distance_to(player.global_position + Vector2(0, -280)) <= 320.0, "camera should follow player with upward HomeArea look-ahead")

	var checks := [
		{
			"name": "Mailbox",
			"art": "MailboxArt",
			"interact": "MailboxInteract",
			"hint": "按 E 查看邮箱",
			"min_blocker": Vector2(70, 44),
			"max_hotspot_offset": 40.0,
			"approach": Vector2(0, 48),
		},
		{
			"name": "Well",
			"art": "WellArt",
			"interact": "WellInteract",
			"hint": "按 E 打水",
			"min_blocker": Vector2(140, 88),
			"max_hotspot_offset": 48.0,
			"approach": Vector2(0, 56),
		},
		{
			"name": "Bench",
			"art": "BenchArt",
			"interact": "BenchRestInteract",
			"hint": "按 E 坐下",
			"min_blocker": Vector2(160, 40),
			"max_hotspot_offset": 72.0,
			"approach": Vector2(0, 56),
		},
		{
			"name": "RoadSign",
			"art": "RoadSignArt",
			"interact": "RoadSignInteract",
			"hint": "按 E 查看路牌",
			"min_blocker": Vector2(48, 40),
			"max_hotspot_offset": 48.0,
			"approach": Vector2(0, 56),
		},
	]

	for check in checks:
		await _validate_prop(home_area, player, check)
		if _has_failed:
			return

	var cat_bed := home_area.get_node_or_null("YSortWorld/Props/CatBed") as CanvasItem
	_expect(cat_bed != null and cat_bed.visible, "CatBed should be visible after runtime prop art is available")
	_expect(_runtime_prop_sprite_loads(home_area, "YSortWorld/Props/CatBed/CatBedArt", "res://assets/art/props/region_home_area_prop_cat_bed_v001.png"), "CatBed runtime prop art should load")
	var cat_bed_graybox := home_area.get_node_or_null("YSortWorld/Props/CatBed/Cushion") as CanvasItem
	_expect(cat_bed_graybox != null and not cat_bed_graybox.visible, "CatBed graybox cushion must stay hidden after runtime art integration")

	if _has_failed:
		return

	print("OK: HomeArea runtime prop playtest contract passed through world.tscn")
	quit(0)


func _validate_prop(home_area: Node, player: CharacterBody2D, check: Dictionary) -> void:
	var prop := home_area.get_node_or_null("YSortWorld/Props/%s" % check["name"]) as Node2D
	_expect(prop != null, "%s prop node must exist" % check["name"])
	if prop == null:
		return

	var art := prop.get_node_or_null(String(check["art"])) as Sprite2D
	_expect(art != null, "%s runtime art sprite must exist" % check["name"])
	if art == null:
		return
	if art.has_method("refresh_texture"):
		art.refresh_texture()
	_expect(art.texture != null, "%s runtime art sprite must load its texture" % check["name"])
	_expect(absf(_sprite_bottom_offset(art)) <= 14.0, "%s runtime art foot anchor should land near prop origin" % check["name"])

	var blocker_collision := prop.get_node_or_null("PropBlocker/CollisionShape2D") as CollisionShape2D
	_expect(blocker_collision != null, "%s should have a walking blocker collision shape" % check["name"])
	if blocker_collision != null:
		var shape := blocker_collision.shape as RectangleShape2D
		_expect(shape != null, "%s blocker should use RectangleShape2D" % check["name"])
		if shape != null:
			var min_size := check["min_blocker"] as Vector2
			_expect(shape.size.x >= min_size.x and shape.size.y >= min_size.y, "%s blocker should cover the prop foot/base" % check["name"])
		_expect(blocker_collision.global_position.distance_to(prop.global_position) <= 36.0, "%s blocker should stay anchored to prop base" % check["name"])

	var interact := home_area.get_node_or_null("YSortWorld/Interactables/%s" % check["interact"]) as Area2D
	_expect(interact != null, "%s interaction area must exist" % check["name"])
	if interact == null:
		return
	_expect(interact.global_position.distance_to(prop.global_position) <= float(check["max_hotspot_offset"]), "%s interaction hotspot should stay close to the visual prop" % check["name"])
	_expect(interact.has_method("get_interaction_hint") and String(interact.get_interaction_hint()) == String(check["hint"]), "%s interaction hint should match runtime text" % check["name"])

	player.global_position = interact.global_position + (check["approach"] as Vector2)
	await physics_frame
	if player.has_method("_update_nearest_interaction_hint"):
		player.call("_update_nearest_interaction_hint")
	_expect(player.global_position.distance_to(interact.global_position) <= INTERACTION_RANGE, "%s approach point should be inside player interaction range" % check["name"])
	var hint_ui := root.get_node_or_null("InteractionHintUI")
	if hint_ui != null:
		_expect(String(hint_ui.get("current_hint")) == String(check["hint"]), "%s should refresh the autoload interaction hint while standing near it" % check["name"])
		if interact.has_method("_on_body_entered"):
			interact.call("_on_body_entered", player)
		var local_hint := interact.get_node_or_null("HintLabel") as CanvasItem
		_expect(local_hint == null or not local_hint.visible, "%s local HintLabel should stay hidden when the autoload interaction prompt is active" % check["name"])


func _sprite_bottom_offset(sprite: Sprite2D) -> float:
	if sprite.texture == null:
		return INF
	var height := sprite.texture.get_size().y * absf(sprite.scale.y)
	if sprite.centered:
		return sprite.position.y + height * 0.5
	return sprite.position.y + height

func _runtime_prop_sprite_loads(root_node: Node, node_path: String, expected_path: String) -> bool:
	var sprite := root_node.get_node_or_null(node_path) as Sprite2D
	if sprite == null:
		return false
	if sprite.has_method("refresh_texture"):
		sprite.refresh_texture()
	return sprite.texture != null and String(sprite.get("texture_path")) == expected_path and _asset_exists(expected_path)


func _asset_exists(path: String) -> bool:
	return ResourceLoader.exists(path) or FileAccess.file_exists(path)



func _get_world_player(world: Node) -> CharacterBody2D:
	if world.has_method("get_player"):
		return world.get_player() as CharacterBody2D
	return world.get_node_or_null("Player") as CharacterBody2D


func _get_world_camera(world: Node) -> Camera2D:
	if world.has_method("get_camera"):
		return world.get_camera() as Camera2D
	return null


func _get_home_area(world: Node) -> Node:
	if world.has_method("get_region_loader"):
		var loader = world.get_region_loader()
		if loader != null and loader.has_method("get_region"):
			return loader.get_region("Region_HomeArea")
	return world.get_node_or_null("Region_HomeArea")


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

