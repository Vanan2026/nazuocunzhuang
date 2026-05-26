extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: post-harvest Aoi share initialize")
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
	var shared_game_state: Node = main.get_node_or_null("GameState")
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	var chip: Node = main.get_node_or_null("CurrentObjectiveChip")
	var hud: Node = main.get_node_or_null("FirstWeekQuestHUD")
	_expect(yard != null and yard.name == "PlayerYard", "Main should load PlayerYard")
	_expect(shared_game_state != null, "Main should expose shared GameState")
	_expect(quest_manager != null, "Main should expose QuestManager")
	_expect(scene_router != null, "Main should expose SceneRouter")
	_expect(chip != null, "Main should include CurrentObjectiveChip")
	_expect(hud != null, "Main should include FirstWeekQuestHUD")
	_expect(main.get_node_or_null("QuestJournalUI") == null, "Main should not remount retired QuestJournalUI")
	_expect(not InputMap.has_action("open_journal"), "open_journal input action should stay retired")
	if _has_failed:
		return

	var local_game_state: Node = yard.get_node_or_null("GameState")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	var relationship: Node = yard.get_node_or_null("RelationshipManager")
	var aoi: Node = yard.get_node_or_null("NPCs/Aoi")
	var dialogue_box: Node = yard.get_node_or_null("DialogueBox")
	_expect(local_game_state != null, "Yard should include local GameState")
	_expect(inventory != null, "Yard should include InventoryManager")
	_expect(relationship != null, "Yard should include RelationshipManager")
	_expect(aoi != null, "Yard should include Aoi")
	_expect(dialogue_box != null, "Yard should include DialogueBox")
	if _has_failed:
		return

	_set_pre_share_flags(local_game_state)
	main.sync_current_scene_state()
	quest_manager.update_first_week_progress(shared_game_state, scene_router)
	chip.refresh()
	hud.refresh()

	_expect(String(quest_manager.get_current_first_week_objective_id()) == "shared_first_turnip_day1", "After first harvest, next objective should guide sharing the turnip with Aoi")
	_expect(String(chip.get_current_goal_text()).contains("萝卜"), "Objective chip should mention the turnip handoff")
	_expect(String(chip.get_current_hint_text()).contains("葵"), "Objective chip hint should point to Aoi")
	_expect(String(chip.get_progress_text()).contains("5 / 13"), "Objective chip should use 13-step first-week chain")
	_expect(_contains_text(hud.get_visible_objective_texts(), "葵"), "HUD should include the Aoi share objective")
	if _has_failed:
		return

	inventory.add_item("crop_turnip", 1)
	_expect(inventory.set_selected_item("crop_turnip"), "Player should be able to select the harvested turnip")
	var before_relationship := int(relationship.get_relationship("aoi"))
	aoi.on_interact(null)
	await _settle()

	_expect(bool(local_game_state.get_flag("shared_first_turnip_day1", false)), "Gifting first turnip to Aoi should set local first-week share flag")
	_expect(int(inventory.get_count("crop_turnip")) == 0, "Aoi share should consume one harvested turnip through the gift system")
	_expect(int(relationship.get_relationship("aoi")) > before_relationship, "Aoi share should improve relationship")
	_expect(bool(dialogue_box.visible), "Aoi share should show dialogue feedback")
	if _has_failed:
		return

	main.sync_current_scene_state()
	_expect(bool(shared_game_state.get_flag("shared_first_turnip_day1", false)), "Aoi share flag should sync to shared GameState")
	quest_manager.update_first_week_progress(shared_game_state, scene_router)
	_expect(String(quest_manager.get_current_first_week_objective_id()) == "planted_aoi_strawberry_day1", "After sharing the first turnip, objective should advance to Aoi strawberry planting")
	if _has_failed:
		return

	print("OK: post-harvest Aoi share runtime validation passed")
	_finish_deferred(0)


func _set_pre_share_flags(game_state: Node) -> void:
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_restored("old_well", true)
	game_state.set_flag("watered_first_crop_day1", true)
	game_state.set_flag("harvested_first_crop_day1", true)
	game_state.set_flag("shared_first_turnip_day1", false)


func _contains_text(texts: Array[String], needle: String) -> bool:
	for text in texts:
		if text.contains(needle):
			return true
	return false


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
			_fail("Post-harvest Aoi share validation timed out")
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
