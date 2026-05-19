extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const WORLD_SCENE_PATH := "res://scenes/world/world.tscn"
const DEFAULT_OUTPUT := "user://home_area_runtime_prop_playtest_snapshot.png"
const TILE_SIZE := Vector2i(1280, 720)
const LOOK_AHEAD := Vector2(0, -120)

var _output_path := DEFAULT_OUTPUT
var _finishing := false


func _initialize() -> void:
	debug_collisions_hint = false
	debug_navigation_hint = false
	debug_paths_hint = false

	if DisplayServer.get_name() == "headless":
		printerr("FAIL: render_home_area_prop_playtest_snapshots.gd requires a display server; run without --headless.")
		_finish_deferred(2)
		return

	var args := OS.get_cmdline_user_args()
	if args.size() >= 1:
		_output_path = args[0]

	call_deferred("_run")


func _run() -> void:
	DisplayServer.window_set_size(TILE_SIZE)
	root.size = TILE_SIZE
	root.content_scale_size = TILE_SIZE

	var scene := HeadlessLifecycle.load_packed_scene(WORLD_SCENE_PATH)
	if scene == null:
		printerr("FAIL: could not load scene: %s" % WORLD_SCENE_PATH)
		_finish_deferred(1)
		return

	var world := scene.instantiate()
	root.add_child(world)
	_hide_snapshot_debug_shapes(root)
	await process_frame
	await process_frame
	await physics_frame

	var player := _get_world_player(world)
	var camera := _get_world_camera(world)
	var home_area := _get_home_area(world)
	if player == null or camera == null or home_area == null:
		printerr("FAIL: world did not initialize player/camera/HomeArea")
		_finish_deferred(1)
		return

	var shots := [
		{"interact": "MailboxInteract", "offset": Vector2(0, 48)},
		{"interact": "WellInteract", "offset": Vector2(0, 40)},
		{"interact": "BenchRestInteract", "offset": Vector2(0, 60)},
		{"interact": "RoadSignInteract", "offset": Vector2(0, 56)},
	]
	var sheet := Image.create(TILE_SIZE.x * 2, TILE_SIZE.y * 2, false, Image.FORMAT_RGBA8)
	for i in range(shots.size()):
		var interact := home_area.get_node_or_null("YSortWorld/Interactables/%s" % shots[i]["interact"]) as Area2D
		if interact == null:
			printerr("FAIL: missing interaction node for snapshot: %s" % shots[i]["interact"])
			_finish_deferred(1)
			return
		player.global_position = interact.global_position + (shots[i]["offset"] as Vector2)
		camera.global_position = player.global_position + LOOK_AHEAD
		_hide_snapshot_debug_shapes(root)
		await process_frame
		await process_frame
		await physics_frame
		if player.has_method("_update_nearest_interaction_hint"):
			player.call("_update_nearest_interaction_hint")
		await process_frame
		var expected_hint := ""
		if interact.has_method("get_interaction_hint"):
			expected_hint = String(interact.get_interaction_hint())
		var hint_ui := root.get_node_or_null("InteractionHintUI")
		if hint_ui != null and not expected_hint.is_empty() and String(hint_ui.get("current_hint")) != expected_hint:
			printerr("FAIL: snapshot hint mismatch for %s: got '%s', expected '%s'" % [shots[i]["interact"], String(hint_ui.get("current_hint")), expected_hint])
			_finish_deferred(1)
			return
		var image := root.get_texture().get_image()
		if image.get_format() != Image.FORMAT_RGBA8:
			image.convert(Image.FORMAT_RGBA8)
		var dest := Vector2i((i % 2) * TILE_SIZE.x, int(i / 2) * TILE_SIZE.y)
		sheet.blit_rect(image, Rect2i(Vector2i.ZERO, TILE_SIZE), dest)

	var err := sheet.save_png(_output_path)
	if err != OK:
		printerr("FAIL: could not save prop playtest snapshot: %s error=%s" % [_output_path, err])
		_finish_deferred(1)
		return

	print("OK: rendered HomeArea prop playtest snapshot: %s" % _output_path)
	_finish_deferred(0)


func _hide_snapshot_debug_shapes(node: Node) -> void:
	if node is Area2D or node is CollisionShape2D or node is CollisionPolygon2D or node.name == "WalkableZone":
		node.visible = false
	for child in node.get_children():
		_hide_snapshot_debug_shapes(child)


func _get_world_player(world: Node) -> CharacterBody2D:
	if world.has_method("get_player"):
		return world.get_player() as CharacterBody2D
	return null


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


func _finish_deferred(exit_code: int) -> void:
	if _finishing:
		return
	_finishing = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
