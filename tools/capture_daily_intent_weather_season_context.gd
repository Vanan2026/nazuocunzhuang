extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DEFAULT_OUTPUT_PATH := "res://.codex/daily_intent_weather_season_context_snapshot.png"
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
		_fail("daily intent weather/season capture requires a display server")
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
	_setup_context(main)
	await _settle()

	var house: Node = main.get_current_gameplay_scene()
	var planner: Node = house.get_node_or_null("IntentDesk") if house != null else null
	var panel: Node = house.get_node_or_null("DailyIntentPanel") if house != null else null
	var player: Node = house.get_node_or_null("Player") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	if not _expect(planner != null and panel != null and player != null and dialogue_box != null, "missing weather/season capture nodes"):
		return
	planner.on_interact(player)
	await _settle()
	if not bool(panel.select_intent("tend_crops")):
		_fail("could not select crop-care intent for weather/season capture")
		return
	await _settle()
	if not _expect(bool(dialogue_box.visible), "daily intent weather/season feedback should be visible"):
		return
	if not _expect(_dialogue_contains(dialogue_box.get("dialogue"), "雨") and _dialogue_contains(dialogue_box.get("dialogue"), "夏天"), "capture dialogue should show rainy summer context"):
		return
	_hide_collision_debug_shapes(root)
	await process_frame
	if not _save_snapshot(_output_path):
		return
	print("OK: captured daily intent weather/season snapshot: %s" % ProjectSettings.globalize_path(_output_path))
	_finish_deferred(0)


func _setup_context(main: Node) -> void:
	var game_state: Node = main.get_node_or_null("GameState")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var time_manager: Node = main.get_node_or_null("TimeManager")
	var weather_manager: Node = main.get_node_or_null("WeatherManager")
	if game_state == null or scene_router == null or quest_manager == null or time_manager == null or weather_manager == null:
		_fail("missing setup managers for weather/season capture")
		return
	_mark_first_week_complete(game_state, scene_router, quest_manager)
	time_manager.apply_save_data({
		"year": 1,
		"season": "summer",
		"season_index": 1,
		"day_of_season": 3,
		"total_day": 3,
		"hour": 6,
		"minute": 0,
	})
	weather_manager.set_today_weather("rainy")
	weather_manager.set_tomorrow_weather("cloudy")


func _mark_first_week_complete(game_state: Node, scene_router: Node, quest_manager: Node) -> void:
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


func _dialogue_contains(dialogue: Dictionary, needle: String) -> bool:
	for line in dialogue.get("lines", []):
		if line is Dictionary and String(line.get("text", "")).contains(needle):
			return true
	return false


func _save_snapshot(path: String) -> bool:
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("viewport screenshot unavailable")
		return false
	var error := image.save_png(path)
	if error != OK:
		_fail("could not save daily intent weather/season screenshot %s: %s" % [path, error])
		return false
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
			_fail("Daily intent weather/season capture timed out")
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
