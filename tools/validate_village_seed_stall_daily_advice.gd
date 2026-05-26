extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: village seed-stall daily advice initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main := main_scene.instantiate()
	root.add_child(main)
	await _settle()
	main.change_scene("player_yard", "from_house")
	await _settle()
	main.change_scene("village", "default")
	await _settle()

	var outdoor: Node = main.get_current_gameplay_scene()
	_expect(outdoor != null, "Village should load OutdoorWorld")
	_expect(String(outdoor.call("get_active_region_id")) == "village", "OutdoorWorld active region should be village")
	var section := outdoor.get_node_or_null("Village")
	var stall := section.get_node_or_null("SeedStallProxy") if section != null else null
	var player := outdoor.get_node_or_null("Player")
	var scene_game_state := outdoor.get_node_or_null("GameState")
	var shared_game_state := main.get_node_or_null("GameState")
	var scene_inventory := outdoor.get_node_or_null("InventoryManager")
	var shared_inventory := main.get_node_or_null("InventoryManager")
	var scene_time := outdoor.get_node_or_null("TimeManager")
	var dialogue_box := outdoor.get_node_or_null("DialogueBox")

	_expect(stall != null, "Village should include SeedStallProxy")
	_expect(stall != null and stall.has_method("get_today_advice_flag_id"), "SeedStallProxy should expose daily advice flag id")
	_expect(player != null, "OutdoorWorld should include Player")
	_expect(scene_game_state != null, "OutdoorWorld should include scene GameState")
	_expect(shared_game_state != null, "Main should include shared GameState")
	_expect(scene_inventory != null, "OutdoorWorld should include scene InventoryManager")
	_expect(shared_inventory != null, "Main should include shared InventoryManager")
	_expect(scene_time != null, "OutdoorWorld should include scene TimeManager")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	var scene_items_before: Dictionary = scene_inventory.get_save_data()
	var shared_items_before: Dictionary = shared_inventory.get_save_data()
	var scene_money_before := int(scene_game_state.get_player_money())
	var shared_money_before := int(shared_game_state.get_player_money())

	stall.on_interact(player)
	await _settle()

	_expect(_flag_is_set(scene_game_state, "visited_village_seed_stall_day1"), "SeedStallProxy should keep the first-visit village seed-stall flag")
	_expect(_flag_is_set(scene_game_state, "asked_seed_stall_advice_spring_day1"), "SeedStallProxy should set asked_seed_stall_advice_spring_day1")
	_expect(_flag_is_set(shared_game_state, "asked_seed_stall_advice_spring_day1"), "SeedStallProxy daily advice flag should sync to Main shared state")
	_expect(_same_dictionary(scene_inventory.get_save_data(), scene_items_before), "inventory should not change after seed-stall advice")
	_expect(_same_dictionary(shared_inventory.get_save_data(), shared_items_before), "shared inventory should not change after seed-stall advice")
	_expect(int(scene_game_state.get_player_money()) == scene_money_before, "money should not change after seed-stall advice")
	_expect(int(shared_game_state.get_player_money()) == shared_money_before, "shared money should not change after seed-stall advice")
	_expect(dialogue_box != null and bool(dialogue_box.visible), "SeedStallProxy should show advice dialogue")
	_expect(_dialogue_line_contains(dialogue_box, "院子"), "SeedStallProxy advice should point back to the yard")
	_expect(_dialogue_line_contains(dialogue_box, "浇水"), "SeedStallProxy advice should give a today farming reason")
	if _has_failed:
		main.queue_free()
		await process_frame
		return

	scene_time.start_next_day()
	await _settle()
	stall.on_interact(player)
	await _settle()
	_expect(_flag_is_set(scene_game_state, "asked_seed_stall_advice_spring_day2"), "SeedStallProxy should set asked_seed_stall_advice_spring_day2 on the next day")
	_expect(_flag_is_set(shared_game_state, "asked_seed_stall_advice_spring_day2"), "next-day seed-stall advice flag should sync to Main shared state")

	main.queue_free()
	await process_frame
	if _has_failed:
		return
	print("OK: village seed-stall daily advice runtime validation passed")
	_finish_deferred(0)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _flag_is_set(game_state: Node, flag_id: String) -> bool:
	if game_state == null or not game_state.has_method("get_flag"):
		return false
	return bool(game_state.get_flag(flag_id, false))


func _dialogue_line_contains(dialogue_box: Node, needle: String) -> bool:
	if dialogue_box == null:
		return false
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	var lines: Array = dialogue.get("lines", [])
	for line in lines:
		if not (line is Dictionary):
			continue
		if String(line.get("text", "")).contains(needle):
			return true
	return false


func _same_dictionary(left: Dictionary, right: Dictionary) -> bool:
	return JSON.stringify(left) == JSON.stringify(right)


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
			_fail("Village seed-stall daily advice validation timed out")
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
