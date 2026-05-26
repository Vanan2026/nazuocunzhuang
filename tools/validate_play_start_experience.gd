extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0
const MIN_CAMERA_ZOOM := 2.5

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: play start experience initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main := main_scene.instantiate()
	root.add_child(main)
	await process_frame
	await process_frame

	var hud := main.get_node_or_null("FirstWeekQuestHUD")
	var journal := main.get_node_or_null("QuestJournalUI")
	var chip := main.get_node_or_null("CurrentObjectiveChip")
	_expect(hud != null, "Main should include FirstWeekQuestHUD")
	_expect(journal == null, "Main should not mount the retired QuestJournalUI")
	_expect(chip != null, "Main should include CurrentObjectiveChip")
	_expect(not InputMap.has_action("open_journal"), "open_journal input action should stay retired")
	if _has_failed:
		return

	_expect(not bool(hud.get("visible")), "FirstWeekQuestHUD should start hidden for normal play")
	_expect(bool(chip.get("visible")), "CurrentObjectiveChip should stay visible for soft guidance")
	_expect(String(main.get_current_gameplay_scene_id()) == "player_house", "Play should start in player_house")
	if _has_failed:
		return

	await _validate_scene_view(main, "player_house")
	if _has_failed:
		return

	main.change_scene("player_yard", "from_house")
	await process_frame
	await process_frame
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "Main should route to player_yard")
	await _validate_scene_view(main, "player_yard")
	if _has_failed:
		return

	main.change_scene("forest_edge", "from_yard")
	await process_frame
	await process_frame
	_expect(String(main.get_current_gameplay_scene_id()) == "forest_edge", "Main should route to forest_edge")
	await _validate_scene_view(main, "forest_edge")
	if _has_failed:
		return

	print("OK: Play start experience validation passed")
	_finish_deferred(0)


func _validate_scene_view(main: Node, scene_id: String) -> void:
	var scene: Node = main.get_current_gameplay_scene()
	_expect(scene != null, "%s should have an active gameplay scene" % scene_id)
	if _has_failed:
		return

	var camera := scene.get_node_or_null("WorldCamera") as Camera2D
	_expect(camera != null, "%s should include WorldCamera" % scene_id)
	if _has_failed:
		return
	_expect(bool(camera.enabled), "%s WorldCamera should be enabled" % scene_id)
	_expect(camera.zoom.x >= MIN_CAMERA_ZOOM and camera.zoom.y >= MIN_CAMERA_ZOOM, "%s WorldCamera should zoom into the playable area" % scene_id)
	_validate_player_visible(scene, scene_id)

	if scene_id == "player_house":
		_expect(scene.get_node_or_null("RoomBackdrop") != null, "PlayerHouse should cover the viewport with an interior backdrop")
	else:
		_expect(scene.get_node_or_null("WorldBackdrop") != null, "%s should cover the viewport with a world backdrop" % scene_id)


func _validate_player_visible(scene: Node, scene_id: String) -> void:
	var player := scene.get_node_or_null("Player")
	_expect(player != null, "%s should include Player" % scene_id)
	if _has_failed:
		return

	var sprite := player.get_node_or_null("PlayerSprite") as AnimatedSprite2D
	_expect(sprite != null, "%s Player should include AnimatedSprite2D PlayerSprite" % scene_id)
	if _has_failed:
		return
	_expect(bool(sprite.visible), "%s PlayerSprite should be visible" % scene_id)
	_expect(sprite.sprite_frames != null, "%s PlayerSprite should have SpriteFrames" % scene_id)
	_expect(not StringName(sprite.animation).is_empty(), "%s PlayerSprite should have a default idle animation" % scene_id)
	_expect(String(sprite.animation).begins_with("player_idle_"), "%s PlayerSprite should start on an idle animation" % scene_id)


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	_finish_deferred(1)


func _start_watchdog() -> void:
	if _finished:
		return
	_watchdog_timer = Timer.new()
	_watchdog_timer.one_shot = true
	_watchdog_timer.wait_time = WATCHDOG_TIMEOUT_SECONDS
	root.add_child(_watchdog_timer)
	_watchdog_timer.timeout.connect(func() -> void:
		if not _finished:
			_fail("Play start experience validation timed out")
	)
	_watchdog_timer.start()


func _finish_deferred(exit_code: int) -> void:
	if _finished:
		return
	_finished = true
	if _watchdog_timer != null:
		_watchdog_timer.stop()
		_watchdog_timer.queue_free()
		_watchdog_timer = null
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
