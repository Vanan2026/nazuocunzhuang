extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DEFAULT_OUTPUT_PATH := "res://.codex/daily_intent_npc_followup_snapshot.png"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _output_path := DEFAULT_OUTPUT_PATH
var _finished := false
var _has_failed := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	debug_collisions_hint = false
	debug_navigation_hint = false
	debug_paths_hint = false
	_parse_args()
	if DisplayServer.get_name() == "headless":
		_fail("daily intent NPC follow-up capture requires a display server")
		return
	DisplayServer.window_set_size(Vector2i(1280, 720))
	root.size = Vector2i(1280, 720)
	root.content_scale_size = Vector2i(1280, 720)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(_output_path).get_base_dir())
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	if main_scene == null:
		_fail("could not load Main scene")
		return
	var main: Node = main_scene.instantiate()
	root.add_child(main)
	await _settle()

	var selected_intent: bool = await _select_daily_intent(main, "check_village_notice")
	if not selected_intent:
		return
	main.change_scene("village", "village_default", true)
	await _settle()

	var outdoor: Node = main.get_current_gameplay_scene()
	var player: Node = outdoor.get_node_or_null("Player") if outdoor != null else null
	var mika: Node = outdoor.get_node_or_null("NPCs/Mika") if outdoor != null else null
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox") if outdoor != null else null
	if not _expect(outdoor != null and player != null and mika != null and dialogue_box != null, "missing village NPC follow-up capture nodes"):
		return

	mika.on_interact(player)
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	var scene_game_state: Node = outdoor.get_node_or_null("GameState")
	var scene_intent := ""
	if scene_game_state != null and scene_game_state.has_method("get_daily_intent"):
		scene_intent = String(scene_game_state.get_daily_intent("day_1"))
	var main_game_state: Node = main.get_node_or_null("GameState")
	var main_intent := ""
	if main_game_state != null and main_game_state.has_method("get_daily_intent"):
		main_intent = String(main_game_state.get_daily_intent("day_1"))
	var dialogue_id := String(dialogue.get("dialogue_id", ""))
	if not _expect(dialogue_id == "mika_daily_intent_village_notice_village_01", "Mika should show selected daily-intent follow-up before capture, got %s scene_intent=%s main_intent=%s" % [dialogue_id, scene_intent, main_intent]):
		return

	_hide_collision_debug_shapes(root)
	await process_frame

	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("viewport screenshot unavailable")
		return
	var error := image.save_png(_output_path)
	if error != OK:
		_fail("could not save daily intent NPC screenshot %s: %s" % [_output_path, error])
		return
	print("OK: captured daily intent NPC follow-up snapshot: %s" % ProjectSettings.globalize_path(_output_path))
	_finish_deferred(0)


func _select_daily_intent(main: Node, intent_id: String) -> bool:
	var house: Node = main.get_current_gameplay_scene()
	var planner: Node = house.get_node_or_null("IntentDesk") if house != null else null
	var player: Node = house.get_node_or_null("Player") if house != null else null
	var panel: Node = house.get_node_or_null("DailyIntentPanel") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	if not _expect(planner != null and player != null and panel != null and dialogue_box != null, "missing daily intent selection nodes"):
		return false
	planner.on_interact(player)
	await _settle()
	if not bool(panel.select_intent(intent_id)):
		_fail("could not select daily intent %s" % intent_id)
		return false
	await _settle()
	if dialogue_box.has_method("close"):
		dialogue_box.close()
	return true


func _parse_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--out="):
			_output_path = arg.trim_prefix("--out=")


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _hide_collision_debug_shapes(node: Node) -> void:
	if node is CollisionShape2D or node is CollisionPolygon2D or node.name == "WalkableZone":
		node.visible = false
	for child in node.get_children():
		_hide_collision_debug_shapes(child)


func _expect(condition: bool, message: String) -> bool:
	if not condition:
		_fail(message)
		return false
	return true


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
			_fail("Daily intent NPC follow-up capture timed out")
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
