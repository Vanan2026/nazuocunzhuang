extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const DEFAULT_SCENE_PATH := "res://scenes/regions/region_home_area.tscn"

var output_path := "user://region_home_area_snapshot.png"
var _finishing := false


func _initialize() -> void:
    if DisplayServer.get_name() == "headless":
        printerr("FAIL: render_scene_snapshot.gd requires a display server; use it without --headless.")
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

    root.size = Vector2i(width, height)
    root.content_scale_size = Vector2i(width, height)

    var scene := HeadlessLifecycle.load_packed_scene(scene_path)
    if scene == null:
        printerr("FAIL: could not load scene: %s" % scene_path)
        _finish_deferred(1)
        return

    var instance: Node = scene.instantiate()
    root.add_child(instance)

    print("INFO: capturing viewport texture")
    var image := root.get_texture().get_image()
    print("INFO: saving snapshot")
    var error := image.save_png(output_path)
    if error != OK:
        printerr("FAIL: could not save snapshot: %s error=%s" % [output_path, error])
        image = null
        instance = null
        scene = null
        _finish_deferred(1)
        return

    print("OK: rendered snapshot: %s" % output_path)
    image = null
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
