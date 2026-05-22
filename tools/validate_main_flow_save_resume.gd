extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const TEST_SAVE_PATH := "user://main_flow_save_resume_test.json"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: main-flow save resume initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	_remove_test_save()
	var main_scene = load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var source_main = main_scene.instantiate()
	root.add_child(source_main)
	await process_frame
	await process_frame

	_expect(source_main.has_method("change_scene"), "Main should expose change_scene for save setup")
	source_main.change_scene("forest_edge", "from_yard")
	await _settle()
	_expect(String(source_main.get_current_gameplay_scene_id()) == "forest_edge", "Source Main should be at forest_edge before save")
	_expect(_player_is_at_spawn(source_main.get_current_gameplay_scene(), "from_yard"), "Source player should be at saved forest spawn")
	if _has_failed:
		return

	var source_forest: Node = source_main.get_current_gameplay_scene()
	var source_inventory: Node = source_forest.get_node("InventoryManager")
	var source_game_state: Node = source_forest.get_node("GameState")
	var source_quests := source_main.get_node("QuestManager")
	var source_save := source_main.get_node("SaveManager")
	source_inventory.add_item("wood", 7)
	source_game_state.set_flag("resume_test_marker", true)
	source_game_state.set_flag("visited_forest_edge", true)
	source_game_state.set_flag("heard_npc_forest_edge", true)
	source_main.sync_current_scene_state()
	source_quests.update_first_week_progress(source_main.get_node("GameState"), source_main.get_node("SceneRouter"))
	_expect(bool(source_save.save_game(source_main, TEST_SAVE_PATH)), "Source Main should save main-flow data")
	if _has_failed:
		return

	source_main.queue_free()
	await _settle()

	var fresh_main = main_scene.instantiate()
	root.add_child(fresh_main)
	await process_frame
	await process_frame
	_expect(String(fresh_main.get_current_gameplay_scene_id()) == "player_house", "Fresh Main should start at player_house before load")
	var fresh_save := fresh_main.get_node("SaveManager")
	_expect(bool(fresh_save.load_game(fresh_main, TEST_SAVE_PATH)), "Fresh Main should load save data")
	await _settle()

	_expect(String(fresh_main.get_current_gameplay_scene_id()) == "forest_edge", "Fresh Main should resume saved scene forest_edge")
	_expect(String(fresh_main.get_node("SceneRouter").get_current_spawn_id()) == "from_yard", "SceneRouter should resume saved spawn id")
	_expect(_player_is_at_spawn(fresh_main.get_current_gameplay_scene(), "from_yard"), "Fresh player should be placed at saved spawn")
	_expect(int(fresh_main.get_node("InventoryManager").get_count("wood")) == 7, "Fresh Main should keep saved inventory after route resume")
	_expect(bool(fresh_main.get_node("GameState").get_flag("resume_test_marker", false)), "Fresh Main should keep saved GameState flags after route resume")
	_expect(bool(fresh_main.get_node("QuestManager").get_first_week_progress().get("objectives", {}).get("visited_forest_edge", false)), "Fresh Main should restore quest progress after route resume")
	if _has_failed:
		return

	_remove_test_save()
	print("OK: main-flow save resume runtime validation passed")
	_finish_deferred(0)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _player_is_at_spawn(scene: Node, spawn_id: String) -> bool:
	if scene == null:
		return false
	var player = scene.get_node_or_null("Player") as Node2D
	var spawn = _find_spawn(scene, spawn_id)
	return player != null and spawn != null and player.position.distance_to(spawn.position) <= 1.0


func _find_spawn(node: Node, spawn_id: String) -> Node2D:
	if node == null:
		return null
	if node.has_method("get_spawn_id") and String(node.call("get_spawn_id")) == spawn_id and node is Node2D:
		return node as Node2D
	for child in node.get_children():
		var found = _find_spawn(child, spawn_id)
		if found != null:
			return found
	return null


func _remove_test_save() -> void:
	if FileAccess.file_exists(TEST_SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE_PATH))


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	_remove_test_save()
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
			_fail("Main-flow save resume validation timed out")
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
