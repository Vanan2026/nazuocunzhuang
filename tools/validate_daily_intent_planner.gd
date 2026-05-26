extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const GAME_STATE_SCRIPT := preload("res://game/autoload/GameState.gd")
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: daily intent planner initialize")
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

	await _validate_house_planner(main)
	if _has_failed:
		return
	_validate_daily_intent_persistence(main)
	if _has_failed:
		return

	print("OK: daily intent planner runtime validation passed")
	_finish_deferred(0)


func _validate_house_planner(main: Node) -> void:
	_expect(String(main.get_current_gameplay_scene_id()) == "player_house", "Planner should be available at the morning house start")
	var house: Node = main.get_current_gameplay_scene()
	var game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var inventory: Node = main.get_node_or_null("InventoryManager")
	_expect(house != null, "PlayerHouse should be active")
	_expect(game_state != null, "Main should include shared GameState")
	_expect(quest_manager != null, "Main should include shared QuestManager")
	_expect(inventory != null, "Main should include shared InventoryManager")
	if _has_failed:
		return

	var planner := house.get_node_or_null("IntentDesk")
	var panel := house.get_node_or_null("DailyIntentPanel")
	var dialogue_box := house.get_node_or_null("DialogueBox")
	var player := house.get_node_or_null("Player")
	_expect(planner != null, "PlayerHouse should include an IntentDesk")
	_expect(panel != null, "PlayerHouse should include DailyIntentPanel")
	_expect(dialogue_box != null, "PlayerHouse should include DialogueBox for daily intent feedback")
	_expect(player != null, "PlayerHouse should include Player")
	if _has_failed:
		return

	_expect(not bool(panel.visible), "DailyIntentPanel should start hidden")
	_expect(planner.has_method("get_interaction_hint"), "IntentDesk should expose an interaction hint")
	_expect(String(planner.get_interaction_hint()).contains("E"), "IntentDesk hint should include the action key")
	_expect(panel.has_method("get_available_intent_ids"), "DailyIntentPanel should expose available intents")
	_expect(panel.has_method("select_intent"), "DailyIntentPanel should expose select_intent")
	_expect(panel.has_method("get_intent_feedback_text"), "DailyIntentPanel should expose feedback text")
	if _has_failed:
		return

	var money_before := int(game_state.get_player_money())
	var energy_before := int(game_state.get_player_energy())
	var seed_count_before := int(inventory.get_count("seed_turnip"))
	var objective_before := String(quest_manager.get_current_first_week_objective_id())

	planner.on_interact(player)
	await _settle()
	_expect(bool(panel.visible), "IntentDesk interaction should open the daily intent panel")
	var intent_ids: Array[String] = panel.get_available_intent_ids()
	_expect(intent_ids.size() == 4, "DailyIntentPanel should offer four gentle intent choices")
	_expect(intent_ids.has("check_village_notice"), "DailyIntentPanel should include the village notice intent")
	_expect(String(panel.get_intent_feedback_text("check_village_notice")).contains("村口"), "Village notice intent should provide soft feedback copy")
	if _has_failed:
		return

	var selected := bool(panel.select_intent("check_village_notice"))
	await _settle()
	_expect(selected, "Selecting a valid daily intent should return true")
	_expect(not bool(panel.visible), "DailyIntentPanel should close after a direction is selected")
	_expect(bool(dialogue_box.visible), "Daily intent selection should show immediate soft feedback")
	_expect(_dialogue_contains(dialogue_box.get("dialogue"), "村口"), "Daily intent feedback should echo the chosen direction")
	_expect(String(dialogue_box.get("dialogue").get("dialogue_id", "")) == "daily_intent_check_village_notice_feedback", "Daily intent feedback should have a stable dialogue id")
	_expect(String(panel.get_selected_intent_id()) == "check_village_notice", "Panel should report the selected intent")
	_expect(String(game_state.get_daily_intent("day_1")) == "check_village_notice", "Shared GameState should store the selected day intent")
	_expect(String(quest_manager.get_current_first_week_objective_id()) == objective_before, "Daily intent should not advance first-week objectives")
	_expect(int(game_state.get_player_money()) == money_before, "Daily intent should not change money")
	_expect(int(game_state.get_player_energy()) == energy_before, "Daily intent should not change energy")
	_expect(int(inventory.get_count("seed_turnip")) == seed_count_before, "Daily intent should not grant or consume items")

	dialogue_box.close()
	panel.hide_planner()
	await _settle()
	_expect(not bool(panel.visible), "DailyIntentPanel should be dismissible")


func _validate_daily_intent_persistence(main: Node) -> void:
	var game_state: Node = main.get_node_or_null("GameState")
	_expect(game_state != null, "Main should include GameState for persistence check")
	if _has_failed:
		return
	var save_data: Dictionary = game_state.get_save_data()
	_expect(save_data.has("daily_intents"), "GameState save data should include daily_intents")
	var daily_intents: Dictionary = save_data.get("daily_intents", {})
	_expect(String(daily_intents.get("day_1", "")) == "check_village_notice", "Save data should persist selected daily intent")
	var fresh_state: Node = GAME_STATE_SCRIPT.new()
	fresh_state.apply_save_data(save_data)
	_expect(String(fresh_state.get_daily_intent("day_1")) == "check_village_notice", "Loaded GameState should restore selected daily intent")
	fresh_state.free()


func _settle() -> void:
	await create_timer(0.1).timeout
	await process_frame
	await process_frame


func _dialogue_contains(dialogue: Dictionary, needle: String) -> bool:
	for line in dialogue.get("lines", []):
		if line is Dictionary and String(line.get("text", "")).contains(needle):
			return true
	return false


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
			_fail("Daily intent planner validation timed out")
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
