extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 20.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: task012 rumors initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	if yard_scene == null:
		_fail("could not load PlayerYard")
		return

	var yard := yard_scene.instantiate() as Node
	root.add_child(yard)
	await process_frame
	await process_frame

	var registry := yard.get_node_or_null("DataRegistry")
	var rumor_manager := yard.get_node_or_null("RumorManager")
	var game_state := yard.get_node_or_null("GameState")
	var time_manager := yard.get_node_or_null("TimeManager")
	var weather_manager := yard.get_node_or_null("WeatherManager")
	var mailbox := yard.get_node_or_null("Mailbox")
	var dialogue_box := yard.get_node_or_null("DialogueBox")

	_expect(registry != null, "PlayerYard should include DataRegistry")
	_expect(rumor_manager != null, "PlayerYard should include RumorManager")
	_expect(game_state != null, "PlayerYard should include GameState")
	_expect(time_manager != null, "PlayerYard should include TimeManager")
	_expect(weather_manager != null, "PlayerYard should include WeatherManager")
	_expect(mailbox != null, "PlayerYard should include Mailbox")
	_expect(dialogue_box != null, "PlayerYard should include DialogueBox")
	if _has_failed:
		return

	_expect(registry.has_method("get_rumor"), "DataRegistry should expose get_rumor")
	_expect(registry.get_rumor("rumor_old_well_bell").size() > 0, "DataRegistry should load bell rumor")
	_expect(rumor_manager.has_method("get_daily_rumors"), "RumorManager should expose get_daily_rumors")
	_expect(rumor_manager.has_method("build_rumor_dialogue"), "RumorManager should expose build_rumor_dialogue")
	_expect(yard.has_method("show_mailbox_rumors"), "PlayerYard should expose show_mailbox_rumors")
	if _has_failed:
		return

	time_manager.season_index = 0
	time_manager.day_of_season = 3
	time_manager.day = 3
	time_manager.total_day = 3
	weather_manager.set_today_weather("sunny")
	weather_manager.set_tomorrow_weather("cloudy")
	game_state.flags.clear()

	var before_repair: Array = rumor_manager.get_daily_rumors("mailbox")
	_expect(before_repair.size() >= 1 and before_repair.size() <= 3, "daily mailbox rumors should choose 1-3 rumors")
	_expect(not _contains_rumor(before_repair, "rumor_old_well_bell"), "bell rumor should not appear before old well unlock flag")
	var before_repair_again: Array = rumor_manager.get_daily_rumors("mailbox")
	_expect(_rumor_ids(before_repair_again) == _rumor_ids(before_repair), "daily rumors should remain stable within the same day")
	if _has_failed:
		return

	game_state.set_flag("rumor_old_well_bell", true)
	var after_repair: Array = rumor_manager.get_daily_rumors("mailbox")
	_expect(_contains_rumor(after_repair, "rumor_old_well_bell"), "bell rumor should appear after old well unlock flag")
	if _has_failed:
		return

	var dialogue: Dictionary = rumor_manager.build_rumor_dialogue("mailbox")
	_expect(String(dialogue.get("npc_id", "")) == "mailbox", "mailbox rumor dialogue should use mailbox npc_id")
	_expect(_dialogue_contains(dialogue, "铃"), "mailbox rumor dialogue should mention the bell")
	if _has_failed:
		return

	yard.show_mailbox_rumors()
	await process_frame
	_expect(bool(dialogue_box.visible), "Mailbox interaction should show DialogueBox")
	_expect(_dialogue_contains(dialogue_box.dialogue, "铃"), "DialogueBox should display bell rumor text")
	_expect(bool(game_state.get_flag("heard_bell_rumor_01", false)), "Showing bell rumor should set heard_bell_rumor_01")
	if _has_failed:
		return

	var after_seen: Array = rumor_manager.get_daily_rumors("mailbox")
	_expect(not _contains_rumor(after_seen, "rumor_old_well_bell"), "bell rumor should not repeat after being heard")
	if _has_failed:
		return

	time_manager.start_next_day()
	await process_frame
	var next_day: Array = rumor_manager.get_daily_rumors("mailbox")
	_expect(next_day.size() >= 1 and next_day.size() <= 3, "next day should still choose 1-3 mailbox rumors")

	print("OK: Task 012 rumor runtime validation passed")
	_finish_deferred(0)


func _contains_rumor(rumors: Array, rumor_id: String) -> bool:
	for rumor in rumors:
		if rumor is Dictionary and String(rumor.get("rumor_id", "")) == rumor_id:
			return true
	return false


func _rumor_ids(rumors: Array) -> Array[String]:
	var ids: Array[String] = []
	for rumor in rumors:
		if rumor is Dictionary:
			ids.append(String(rumor.get("rumor_id", "")))
	return ids


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
			_fail("Task 012 rumor validation timed out")
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
