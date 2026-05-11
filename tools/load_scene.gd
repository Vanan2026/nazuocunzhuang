extends SceneTree

const DEFAULT_SCENE_PATH := "res://scenes/regions/region_home_area.tscn"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var scene_path := DEFAULT_SCENE_PATH
	if not args.is_empty():
		scene_path = args[0]

	var scene := ResourceLoader.load(scene_path) as PackedScene
	if scene == null:
		printerr("FAIL: could not load scene: %s" % scene_path)
		quit(1)
		return

	var instance: Node = scene.instantiate()
	if instance == null:
		printerr("FAIL: could not instantiate scene: %s" % scene_path)
		quit(1)
		return

	instance.queue_free()
	print("OK: loaded scene: %s" % scene_path)
	quit(0)
