extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const DEFAULT_SCENE_PATH := "res://scenes/dev/region_home_area_blockout_3d_v002.tscn"
const DEFAULT_OUTPUT := "res://.codex/home_area_blockout_v002_3d_review.png"

var _finishing := false


func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		printerr("FAIL: render_home_area_blockout_3d_review.gd requires a display server; run without --headless.")
		_finish_deferred(2)
		return

	var args := OS.get_cmdline_user_args()
	var output_path := DEFAULT_OUTPUT
	var width := 1600
	var height := 1000
	if args.size() >= 1:
		output_path = args[0]
	if args.size() >= 3:
		width = args[1].to_int()
		height = args[2].to_int()

	DisplayServer.window_set_size(Vector2i(width, height))
	root.size = Vector2i(width, height)
	root.content_scale_size = Vector2i(width, height)

	var packed := HeadlessLifecycle.load_packed_scene(DEFAULT_SCENE_PATH)
	if packed == null:
		printerr("FAIL: could not load scene: %s" % DEFAULT_SCENE_PATH)
		_finish_deferred(1)
		return

	var instance := packed.instantiate()
	root.add_child(instance)

	var camera := instance.get_node_or_null("BlockoutReviewCamera")
	if camera is Camera3D:
		camera.size = 42.0
		camera.current = true

	var label := Label.new()
	label.text = "HomeArea blockout v002 scale pass - 3D review, not v005 art"
	label.position = Vector2(18, 18)
	label.add_theme_color_override("font_color", Color("#2f281f"))
	root.add_child(label)

	await process_frame
	await process_frame
	await process_frame
	await process_frame

	var image := root.get_texture().get_image()
	var error := image.save_png(output_path)
	if error != OK:
		printerr("FAIL: could not save blockout 3D review: %s error=%s" % [output_path, error])
		_finish_deferred(1)
		return

	print("OK: rendered HomeArea blockout 3D review: %s" % output_path)
	_finish_deferred(0)


func _finish_deferred(exit_code: int) -> void:
	if _finishing:
		return
	_finishing = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
