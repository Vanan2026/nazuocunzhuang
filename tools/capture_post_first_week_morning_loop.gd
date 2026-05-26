extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DEFAULT_OUTPUT_PATH := "res://.codex/post_first_week_morning_loop_snapshot.png"
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
		_fail("post-first-week morning loop capture requires a display server")
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

	_mark_first_week_complete(main)
	await _select_daily_intent(main, "check_village_notice")
	if _has_failed:
		return

	var chip := main.get_node_or_null("CurrentObjectiveChip")
	if not _expect(chip != null, "Main should include CurrentObjectiveChip"):
		return
	chip.refresh()
	var goal_text := String(chip.get_current_goal_text())
	if not _expect(goal_text.contains("今日方向") and goal_text.contains("村口"), "Chip should show post-first-week selected direction before capture"):
		return

	_hide_collision_debug_shapes(root)
	await process_frame

	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("viewport screenshot unavailable")
		return
	var error := image.save_png(_output_path)
	if error != OK:
		_fail("could not save post-first-week morning loop screenshot %s: %s" % [_output_path, error])
		return
	print("OK: captured post-first-week morning loop snapshot: %s" % ProjectSettings.globalize_path(_output_path))
	_finish_deferred(0)


func _mark_first_week_complete(main: Node) -> void:
	var game_state := main.get_node_or_null("GameState")
	var scene_router := main.get_node_or_null("SceneRouter")
	var quest_manager := main.get_node_or_null("QuestManager")
	if game_state == null or scene_router == null or quest_manager == null:
		_fail("Main should expose first-week completion managers")
		return
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_flag("watered_first_crop_day1", true)
	game_state.set_flag("harvested_first_crop_day1", true)
	game_state.set_flag("shared_first_turnip_day1", true)
	game_state.set_flag("planted_aoi_strawberry_day1", true)
	game_state.set_flag("heard_forest_edge_notice", true)
	game_state.set_flag("visited_forest_edge", true)
	game_state.set_flag("heard_npc_forest_edge", true)
	game_state.set_flag("read_village_notice_day1", true)
	game_state.set_restored("old_well", true)
	game_state.set_restored("garden_bench", true)
	game_state.set_restored("village_sign", true)
	scene_router.set_current_scene("forest_edge", "from_yard")
	quest_manager.update_first_week_progress(game_state, scene_router)


func _select_daily_intent(main: Node, intent_id: String) -> void:
	var house: Node = main.get_current_gameplay_scene()
	var planner: Node = house.get_node_or_null("IntentDesk") if house != null else null
	var player: Node = house.get_node_or_null("Player") if house != null else null
	var panel: Node = house.get_node_or_null("DailyIntentPanel") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	if not _expect(planner != null and player != null and panel != null and dialogue_box != null, "missing post-first-week daily intent selection nodes"):
		return
	planner.on_interact(player)
	await _settle()
	if not bool(panel.select_intent(intent_id)):
		_fail("could not select daily intent %s" % intent_id)
		return
	await _settle()
	if dialogue_box.has_method("close"):
		dialogue_box.close()


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
			_fail("Post-first-week morning loop capture timed out")
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
