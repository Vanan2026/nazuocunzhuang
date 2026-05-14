extends SceneTree

const TARGET_SCENE := "res://scenes/regions/region_home_area.tscn"
const EXPECTED_BGM := "res://audio/bgm/Sunlight_on_the_Veranda.mp3"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	await process_frame

	var audio_manager := root.get_node_or_null("AudioManager")
	if audio_manager == null:
		_fail("missing AudioManager autoload")
		return

	var err := change_scene_to_file(TARGET_SCENE)
	if err != OK:
		_fail("could not change scene to %s: %s" % [TARGET_SCENE, err])
		return

	await process_frame
	await process_frame

	audio_manager = root.get_node_or_null("AudioManager")
	if audio_manager == null:
		_fail("AudioManager disappeared after scene switch")
		return

	if str(audio_manager.current_bgm) != EXPECTED_BGM:
		_fail("current_bgm mismatch: %s" % str(audio_manager.current_bgm))
		return

	var bgm_player := audio_manager.get("bgm_player") as AudioStreamPlayer
	if bgm_player == null:
		_fail("AudioManager missing bgm_player")
		return

	if bgm_player.stream == null:
		_fail("bgm_player has no stream bound")
		return

	var stream_path := String(bgm_player.stream.resource_path)
	if stream_path != EXPECTED_BGM:
		_fail("bgm stream mismatch: %s" % stream_path)
		return

	print("OK: audio runtime validated (stream bound + current_bgm set)")
	quit(0)


func _fail(message: String) -> void:
	printerr("FAIL: %s" % message)
	quit(1)
