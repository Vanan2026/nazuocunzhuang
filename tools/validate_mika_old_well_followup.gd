extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0
const FOLLOWUP_DIALOGUE_ID := "mika_old_well_echo_followup"
const SOURCE_FLAG := "heard_old_well_echo_after_village_clue_day1"
const SEEN_FLAG := "heard_mika_old_well_echo_day1"

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Mika old-well follow-up initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene: PackedScene = load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main: Node = main_scene.instantiate()
	root.add_child(main)
	await _settle()
	main.change_scene("player_yard", "from_house")
	await _settle()

	var yard: Node = main.get_current_gameplay_scene()
	_expect(yard != null and yard.has_method("set_active_region"), "Main should load OutdoorWorld for player_yard")
	if _has_failed:
		return
	var yard_game_state: Node = yard.get_node_or_null("GameState")
	var shared_game_state: Node = main.get_node_or_null("GameState")
	_expect(yard_game_state != null, "OutdoorWorld should expose local GameState")
	_expect(shared_game_state != null, "Main should expose shared GameState")
	if _has_failed:
		return

	_set_pre_followup_flags(yard_game_state)
	main.sync_current_scene_state()
	main.change_scene("forest_edge", "from_yard")
	await _settle()

	var outdoor: Node = main.get_current_gameplay_scene()
	_expect(outdoor == yard, "forest_edge should reuse the existing OutdoorWorld instance")
	_expect(String(outdoor.call("get_active_region_id")) == "forest_edge", "OutdoorWorld should activate forest_edge")
	var scene_game_state: Node = outdoor.get_node_or_null("GameState")
	var schedule_director: Node = outdoor.get_node_or_null("ScheduleDirector")
	if schedule_director != null and schedule_director.has_method("apply_schedule"):
		schedule_director.apply_schedule("afternoon")
	await _settle()

	var player: Node = outdoor.get_node_or_null("Player")
	var mika: Node = outdoor.get_node_or_null("NPCs/Mika")
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox")
	var inventory: Node = outdoor.get_node_or_null("InventoryManager")
	_expect(player != null, "OutdoorWorld should expose Player")
	_expect(mika != null, "OutdoorWorld should expose Mika")
	_expect(mika != null and bool(mika.get("visible")), "Mika should be visible in forest_edge afternoon")
	_expect(dialogue_box != null, "OutdoorWorld should expose DialogueBox")
	if _has_failed:
		return

	if inventory != null and inventory.has_method("set_selected_item"):
		inventory.set_selected_item("")
	if dialogue_box.has_method("close"):
		dialogue_box.close()
	mika.on_interact(player)
	await _settle()

	var first_dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(String(first_dialogue.get("dialogue_id", "")) == FOLLOWUP_DIALOGUE_ID, "Mika should play the old-well follow-up before generic NPC rumors")
	_expect(_flag_is_set(scene_game_state, SEEN_FLAG), "Mika follow-up should set its local one-shot flag")
	_expect(_flag_is_set(shared_game_state, SEEN_FLAG), "Mika follow-up flag should sync to Main shared state")
	if _has_failed:
		return

	if dialogue_box.has_method("close"):
		dialogue_box.close()
	mika.on_interact(player)
	await _settle()
	var second_dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(String(second_dialogue.get("dialogue_id", "")) != FOLLOWUP_DIALOGUE_ID, "Mika old-well follow-up should not repeat after its seen flag")
	if _has_failed:
		return

	main.queue_free()
	await process_frame
	print("OK: Mika old-well follow-up runtime validation passed")
	_finish_deferred(0)


func _set_pre_followup_flags(game_state: Node) -> void:
	if game_state == null:
		return
	if game_state.has_method("set_restored"):
		game_state.set_restored("old_well", true)
	if game_state.has_method("set_flag"):
		game_state.set_flag("read_mailbox_day1", true)
		game_state.set_flag("read_bulletin_day1", true)
		game_state.set_flag("watered_first_crop_day1", true)
		game_state.set_flag("harvested_first_crop_day1", true)
		game_state.set_flag("shared_first_turnip_day1", true)
		game_state.set_flag("planted_aoi_strawberry_day1", true)
		game_state.set_flag("forest_edge_hint", true)
		game_state.set_flag("heard_forest_edge_notice", true)
		game_state.set_flag("visited_forest_edge", true)
		game_state.set_flag("heard_npc_forest_edge", false)
		game_state.set_flag(SOURCE_FLAG, true)
		game_state.set_flag(SEEN_FLAG, false)


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
			_fail("Mika old-well follow-up validation timed out")
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
