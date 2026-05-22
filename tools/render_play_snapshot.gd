extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const DEFAULT_SCENE_PATH := "res://game/scenes/Main.tscn"

var output_path := "user://play_snapshot.png"
var _finishing := false


func _initialize() -> void:
	debug_collisions_hint = false
	debug_navigation_hint = false
	debug_paths_hint = false

	if DisplayServer.get_name() == "headless":
		printerr("FAIL: render_play_snapshot.gd requires a display server; use it without --headless.")
		_finish_deferred(2)
		return

	var args := OS.get_cmdline_user_args()
	var scene_path := DEFAULT_SCENE_PATH
	var width := 1280
	var height := 720

	if args.size() >= 1:
		scene_path = args[0]
	if args.size() >= 2:
		output_path = args[1]
	if args.size() >= 4:
		width = args[2].to_int()
		height = args[3].to_int()

	DisplayServer.window_set_size(Vector2i(width, height))
	root.size = Vector2i(width, height)
	root.content_scale_size = Vector2i(width, height)

	var scene := HeadlessLifecycle.load_packed_scene(scene_path)
	if scene == null:
		printerr("FAIL: could not load scene: %s" % scene_path)
		_finish_deferred(1)
		return

	var instance: Node = scene.instantiate()
	root.add_child(instance)
	_hide_collision_debug_shapes(root)

	await process_frame
	await process_frame
	await process_frame
	_hide_collision_debug_shapes(root)
	await process_frame

	var image := root.get_texture().get_image()
	var error := image.save_png(output_path)
	if error != OK:
		printerr("FAIL: could not save snapshot: %s error=%s" % [output_path, error])
		_finish_deferred(1)
		return

	print("OK: rendered play snapshot: %s" % output_path)
	_finish_deferred(0)


func _hide_collision_debug_shapes(node: Node) -> void:
	if node is CollisionShape2D or node is CollisionPolygon2D or node.name == "WalkableZone":
		node.visible = false
	for child in node.get_children():
		_hide_collision_debug_shapes(child)


func _finish_deferred(exit_code: int) -> void:
	if _finishing:
		return
	_finishing = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
