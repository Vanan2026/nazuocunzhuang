extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: current objective guidance initialize")
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

	_validate_objective_chip(main)
	if _has_failed:
		return
	_validate_house_guidance(main)
	if _has_failed:
		return

	main.change_scene("player_yard", "from_house")
	await _settle()
	_validate_yard_guidance(main)
	if _has_failed:
		return
	await _validate_mailbox_advances_chip(main)
	if _has_failed:
		return

	print("OK: current objective guidance runtime validation passed")
	_finish_deferred(0)


func _validate_objective_chip(main: Node) -> void:
	var chip := main.get_node_or_null("CurrentObjectiveChip")
	var hud := main.get_node_or_null("FirstWeekQuestHUD")
	var journal := main.get_node_or_null("QuestJournalUI")
	_expect(chip != null, "Main should include CurrentObjectiveChip")
	_expect(hud != null, "Main should include FirstWeekQuestHUD")
	_expect(journal == null, "Main should not mount the retired QuestJournalUI")
	_expect(not InputMap.has_action("open_journal"), "open_journal input action should stay retired")
	if _has_failed:
		return
	_expect(chip is CanvasLayer, "CurrentObjectiveChip should be a CanvasLayer")
	_expect(bool(chip.get("visible")), "CurrentObjectiveChip should be visible in normal play")
	_expect(not bool(hud.get("visible")), "FirstWeekQuestHUD should stay hidden in normal play")
	_expect(chip.has_method("get_current_goal_text"), "CurrentObjectiveChip should expose current goal text")
	_expect(chip.has_method("get_current_hint_text"), "CurrentObjectiveChip should expose current hint text")
	_expect(chip.has_method("get_progress_text"), "CurrentObjectiveChip should expose progress text")
	if _has_failed:
		return
	_expect(String(chip.get_current_goal_text()).contains("读邮箱"), "Initial chip goal should be read mailbox")
	_expect(String(chip.get_progress_text()).contains("0 / 13"), "Initial chip should show compact progress")
	var panel := chip.get_node_or_null("Panel") as Control
	_expect(panel != null, "CurrentObjectiveChip should include a Panel")
	if _has_failed:
		return
	var hint_label := chip.get_node_or_null("Panel/Content/HintLabel") as Label
	_expect(hint_label != null, "CurrentObjectiveChip should include a HintLabel")
	if _has_failed:
		return
	_expect(not String(chip.get_current_hint_text()).is_empty(), "CurrentObjectiveChip should provide a non-empty hint")
	_expect(String(chip.get_current_hint_text()).contains("E"), "Initial chip hint should include the action key")
	_expect(hint_label.text == String(chip.get_current_hint_text()), "HintLabel should display the current hint text")
	_expect(panel.offset_left >= 880.0, "CurrentObjectiveChip should sit near the top-right edge")
	_expect(panel.offset_top <= 24.0, "CurrentObjectiveChip should stay at the top edge")
	_expect(panel.offset_right <= 1272.0, "CurrentObjectiveChip should stay inside the 1280px UI frame")
	_expect(panel.offset_bottom <= 132.0, "CurrentObjectiveChip should not cover the lower playfield")
	_expect((panel.offset_right - panel.offset_left) <= 390.0, "CurrentObjectiveChip should stay compact")


func _validate_house_guidance(main: Node) -> void:
	_expect(String(main.get_current_gameplay_scene_id()) == "player_house", "Play should start in PlayerHouse")
	var house: Node = main.get_current_gameplay_scene()
	_expect(house != null, "PlayerHouse should be active")
	if _has_failed:
		return
	var guidance := house.get_node_or_null("HomeStartGuidance")
	var path := house.get_node_or_null("HomeStartGuidance/DoorGuidePath") as Polygon2D
	var focus := house.get_node_or_null("HomeStartGuidance/DoorFocusMarker") as Polygon2D
	var door := house.get_node_or_null("DoorToYard") as Node2D
	var player := house.get_node_or_null("Player") as Node2D
	_expect(guidance != null, "PlayerHouse should include HomeStartGuidance")
	_expect(path != null, "PlayerHouse should include DoorGuidePath")
	_expect(focus != null, "PlayerHouse should include DoorFocusMarker")
	_expect(door != null, "PlayerHouse should include DoorToYard")
	_expect(player != null, "PlayerHouse should include Player")
	if _has_failed:
		return
	_expect(bool(path.visible), "DoorGuidePath should be visible")
	_expect(bool(focus.visible), "DoorFocusMarker should be visible")
	_expect(player.position.distance_to(door.position) <= 120.0, "Door guidance should connect the start position to the yard exit")


func _validate_yard_guidance(main: Node) -> void:
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "Main should enter PlayerYard")
	var yard: Node = main.get_current_gameplay_scene()
	_expect(yard != null, "PlayerYard should be active")
	if _has_failed:
		return
	var guidance := yard.get_node_or_null("YardStructure/FirstStepGuidance")
	var path := yard.get_node_or_null("YardStructure/FirstStepGuidance/SpawnMailboxPath") as Polygon2D
	var focus := yard.get_node_or_null("YardStructure/FirstStepGuidance/MailboxFocusMarker") as Polygon2D
	var spawn := yard.get_node_or_null("SpawnFromHouse") as Node2D
	var mailbox := yard.get_node_or_null("Mailbox") as Node2D
	_expect(guidance != null, "PlayerYard should include FirstStepGuidance")
	_expect(path != null, "PlayerYard should include SpawnMailboxPath")
	_expect(focus != null, "PlayerYard should include MailboxFocusMarker")
	_expect(spawn != null, "PlayerYard should include SpawnFromHouse")
	_expect(mailbox != null, "PlayerYard should include Mailbox")
	if _has_failed:
		return
	_expect(bool(path.visible), "SpawnMailboxPath should be visible")
	_expect(bool(focus.visible), "MailboxFocusMarker should be visible")
	_expect(spawn.position.distance_to(mailbox.position) <= 80.0, "First-step guidance should connect yard spawn to mailbox")


func _validate_mailbox_advances_chip(main: Node) -> void:
	var yard: Node = main.get_current_gameplay_scene()
	var chip := main.get_node_or_null("CurrentObjectiveChip")
	var mailbox := yard.get_node_or_null("Mailbox")
	var player := yard.get_node_or_null("Player")
	_expect(chip != null, "CurrentObjectiveChip should still exist in yard")
	_expect(mailbox != null, "PlayerYard should include Mailbox")
	_expect(player != null, "PlayerYard should include Player")
	if _has_failed:
		return
	mailbox.on_interact(player)
	await _settle()
	_expect(String(chip.get_current_hint_text()).contains("E"), "Advanced chip hint should include the action key")
	_expect(String(chip.get_current_goal_text()).contains("看公告板"), "Chip goal should advance to bulletin board after reading mailbox")
	_expect(String(chip.get_progress_text()).contains("1 / 13"), "Chip progress should advance after reading mailbox")


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


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
			_fail("Current objective guidance validation timed out")
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
