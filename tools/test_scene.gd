extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const DEFAULT_SCENE_PATH := "res://scenes/regions/region_home_area.tscn"

var _finishing := false


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var scene_path := DEFAULT_SCENE_PATH
	if not args.is_empty():
		scene_path = args[0]

	var scene := HeadlessLifecycle.load_packed_scene(scene_path)
	if scene == null:
		printerr("FAIL: 鍦烘櫙鏂囦欢鍔犺浇澶辫触: %s" % scene_path)
		_finish_deferred(1)
		return

	var instance := scene.instantiate()
	if instance == null:
		printerr("FAIL: 鍦烘櫙瀹炰緥鍖栧け璐? %s" % scene_path)
		scene = null
		_finish_deferred(1)
		return

	instance.queue_free()
	print("OK: 鍦烘櫙鍔犺浇鎴愬姛: %s" % scene_path)
	instance = null
	scene = null
	_finish_deferred(0)


func _finish_deferred(exit_code: int) -> void:
	if _finishing:
		return
	_finishing = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
