extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0
const ENTRY_OBJECTIVE_ID := "read_village_notice_day1"
const EXPLORATION_FLAGS: Array[String] = [
	"asked_seed_stall_advice_spring_day1",
	"found_village_soft_clue_day1",
	"heard_old_well_echo_after_village_clue_day1",
	"heard_mika_old_well_echo_day1",
]

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: village first-week exploration bridge initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main: Node = main_scene.instantiate()
	root.add_child(main)
	await _settle()

	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var game_state: Node = main.get_node_or_null("GameState")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	_expect(quest_manager != null, "Main should include QuestManager")
	_expect(game_state != null, "Main should include GameState")
	_expect(scene_router != null, "Main should include SceneRouter")
	if _has_failed:
		return

	_mark_pre_village_progress(game_state, scene_router)
	quest_manager.update_first_week_progress(game_state, scene_router)
	_expect_current_objective(main, quest_manager)
	if _has_failed:
		return

	await _complete_village_notice_bridge(main, quest_manager, game_state, scene_router)
	if _has_failed:
		return

	main.queue_free()
	await process_frame
	print("OK: village first-week exploration bridge runtime validation passed")
	_finish_deferred(0)


func _mark_pre_village_progress(game_state: Node, scene_router: Node) -> void:
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_flag("watered_first_crop_day1", true)
	game_state.set_flag("harvested_first_crop_day1", true)
	game_state.set_flag("shared_first_turnip_day1", true)
	game_state.set_flag("planted_aoi_strawberry_day1", true)
	game_state.set_flag("heard_forest_edge_notice", true)
	game_state.set_flag("visited_forest_edge", true)
	game_state.set_flag("heard_npc_forest_edge", true)
	game_state.set_restored("old_well", true)
	game_state.set_restored("garden_bench", true)
	game_state.set_restored("village_sign", true)
	for flag_id in EXPLORATION_FLAGS:
		game_state.set_flag(flag_id, false)
	scene_router.set_current_scene("forest_edge", "from_yard")


func _expect_current_objective(main: Node, quest_manager: Node) -> void:
	_expect(not bool(quest_manager.is_first_week_complete()), "First week should not complete before the Village notice bridge")
	_expect(
		String(quest_manager.get_current_first_week_objective_id()) == ENTRY_OBJECTIVE_ID,
		"Current objective should bridge to the Village notice only"
	)
	var progress: Dictionary = quest_manager.get_first_week_progress()
	_expect(int(progress.get("completed_count", 0)) == 12, "Pre-village first-week progress should be 12 of 13")
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	_expect(chip != null, "CurrentObjectiveChip should exist")
	if _has_failed:
		return
	chip.refresh()
	_expect(String(chip.get_progress_text()).contains("12 / 13"), "Chip should show the new 13-step first-week total")
	_expect(String(chip.get_current_goal_text()).contains("村") or String(chip.get_current_hint_text()).contains("村"), "Chip should point gently toward the Village")
	for flag_id in EXPLORATION_FLAGS:
		_expect(not _flag_is_set(main.get_node_or_null("GameState"), flag_id), "Exploration flag should remain unset before player discovery: %s" % flag_id)


func _complete_village_notice_bridge(main: Node, quest_manager: Node, game_state: Node, scene_router: Node) -> void:
	main.change_scene("village", "village_default")
	await _settle()
	var outdoor: Node = main.get_current_gameplay_scene()
	_expect(outdoor != null and outdoor.has_method("get_active_region_id"), "Village bridge should use OutdoorWorld")
	_expect(String(outdoor.call("get_active_region_id")) == "village", "OutdoorWorld should activate the Village region")
	if _has_failed:
		return
	var section: Node = outdoor.get_node_or_null("Village")
	var notice: Node = null
	if section != null:
		notice = section.get_node_or_null("VillageNotice")
	var player: Node = outdoor.get_node_or_null("Player")
	_expect(section != null, "OutdoorWorld should compose the Village section")
	_expect(notice != null, "Village should include VillageNotice")
	_expect(player != null, "OutdoorWorld should expose Player")
	if _has_failed:
		return
	notice.on_interact(player)
	await _settle()
	main.sync_current_scene_state()
	quest_manager.update_first_week_progress(game_state, scene_router)
	_expect(_flag_is_set(game_state, ENTRY_OBJECTIVE_ID), "VillageNotice should complete the light journal bridge")
	_expect(bool(quest_manager.is_first_week_complete()), "First week should complete after reading the Village notice")
	for flag_id in EXPLORATION_FLAGS:
		_expect(not _flag_is_set(game_state, flag_id), "Exploration flag should not be required for completion: %s" % flag_id)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _flag_is_set(game_state: Node, flag_id: String) -> bool:
	if game_state == null or not game_state.has_method("get_flag"):
		return false
	return bool(game_state.get_flag(flag_id, false))


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
			_fail("Village first-week exploration bridge validation timed out")
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
