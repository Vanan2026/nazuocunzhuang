extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")

var _finishing := false


func _initialize() -> void:
    if DisplayServer.get_name() == "headless":
        printerr("FAIL: render_final_art_phase2_preview.gd requires a display server; use it without --headless.")
        _finish_deferred(2)
        return

    var args := OS.get_cmdline_user_args()
    var output_path := "res://.codex/final_art_phase2_godot_snapshot.png"
    if args.size() >= 1:
        output_path = args[0]

    var width := 1440
    var height := 960
    DisplayServer.window_set_size(Vector2i(width, height))
    root.size = Vector2i(width, height)
    root.content_scale_size = Vector2i(width, height)

    var preview := Node2D.new()
    root.add_child(preview)

    var background := ColorRect.new()
    background.color = Color("#f3e7d1")
    background.size = Vector2(width, height)
    root.add_child(background)
    root.move_child(background, 0)

    var assets := [
        "res://production/assets/final_art/home_area/props/region_home_area_prop_mailbox_v001.png",
        "res://production/assets/final_art/home_area/props/region_home_area_prop_well_broken_v001.png",
        "res://production/assets/final_art/home_area/props/region_home_area_prop_well_repaired_v001.png",
        "res://production/assets/final_art/home_area/props/region_home_area_prop_bench_v001.png",
        "res://production/assets/final_art/home_area/props/region_home_area_prop_road_sign_v001.png",
        "res://production/assets/final_art/characters/npc/npc_aoi_idle_down_128.png",
        "res://production/assets/final_art/characters/npc/npc_gen_idle_down_128.png",
        "res://production/assets/final_art/characters/npc/npc_mika_idle_down_128.png",
        "res://production/assets/final_art/characters/npc/npc_aoi_portrait_neutral_512.png",
        "res://production/assets/final_art/characters/npc/npc_gen_portrait_neutral_512.png",
        "res://production/assets/final_art/characters/npc/npc_mika_portrait_neutral_512.png",
    ]
    var positions := [
        Vector2(120, 210),
        Vector2(360, 250),
        Vector2(650, 250),
        Vector2(900, 230),
        Vector2(1150, 220),
        Vector2(210, 520),
        Vector2(330, 520),
        Vector2(450, 520),
        Vector2(720, 560),
        Vector2(940, 560),
        Vector2(1160, 560),
    ]
    var scales := [
        1.0, 0.72, 0.72, 1.0, 1.0,
        1.0, 1.0, 1.0,
        0.34, 0.34, 0.34,
    ]

    for i in assets.size():
        var image := Image.load_from_file(ProjectSettings.globalize_path(assets[i]))
        if image == null or image.is_empty():
            printerr("FAIL: missing image: %s" % assets[i])
            _finish_deferred(1)
            return
        var texture := ImageTexture.create_from_image(image)
        var sprite := Sprite2D.new()
        sprite.texture = texture
        sprite.position = positions[i]
        sprite.scale = Vector2.ONE * float(scales[i])
        preview.add_child(sprite)

    await process_frame
    await process_frame
    await process_frame

    var image := root.get_texture().get_image()
    var error := image.save_png(output_path)
    if error != OK:
        printerr("FAIL: could not save snapshot: %s error=%s" % [output_path, error])
        _finish_deferred(1)
        return

    print("OK: rendered final art phase2 preview: %s" % output_path)
    _finish_deferred(0)


func _finish_deferred(exit_code: int) -> void:
    if _finishing:
        return
    _finishing = true
    call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
    await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
