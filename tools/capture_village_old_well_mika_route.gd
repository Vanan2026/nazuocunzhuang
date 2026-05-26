extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DEFAULT_OUTPUT_DIR := "res://.codex/village_old_well_mika_route"
const WATCHDOG_TIMEOUT_SECONDS := 40.0
const OUTPUT_FILENAMES := {
	"seed_stall_advice": "01_seed_stall_advice.png",
	"village_clue": "02_village_clue.png",
	"old_well_echo": "03_old_well_echo.png",
	"mika_followup": "04_mika_followup.png",
}
const REVIEW_HIDDEN_UI_NODE_NAMES: Array[String] = [
	"TimeWeatherHUD",
	"FirstWeekQuestHUD",
	"QuestJournalUI",
	"CurrentObjectiveChip",
	"InventoryUI",
]

var _output_dir := DEFAULT_OUTPUT_DIR
var _check_only := false
var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	debug_collisions_hint = false
	debug_navigation_hint = false
	debug_paths_hint = false
	_parse_args()
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	print("PROGRESS: village old-well Mika route review initialize")
	if not _check_only and DisplayServer.get_name() == "headless":
		_fail("village old-well Mika route capture requires a display server; rerun with --check-only for headless validation")
		return
	if not _check_only:
		DisplayServer.window_set_size(Vector2i(1280, 720))
		root.size = Vector2i(1280, 720)
		root.content_scale_size = Vector2i(1280, 720)
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(_output_dir))

	var main_scene: PackedScene = load(MAIN_PATH) as PackedScene
	if main_scene == null:
		_fail("could not load Main scene")
		return
	var main: Node = main_scene.instantiate()
	root.add_child(main)
	_hide_collision_debug_shapes(root)
	await _settle()

	if not await _prepare_seed_stall_advice(main):
		return
	if not await _capture_review_frame("seed_stall_advice"):
		return
	if not await _prepare_village_clue(main):
		return
	if not await _capture_review_frame("village_clue"):
		return
	if not await _prepare_old_well_echo(main):
		return
	if not await _capture_review_frame("old_well_echo"):
		return
	if not await _prepare_mika_followup(main):
		return
	if not await _capture_review_frame("mika_followup"):
		return

	main.queue_free()
	await process_frame
	if _check_only:
		print("OK: village old-well Mika route review check-only validated")
	else:
		print("OK: village old-well Mika route screenshots saved to %s" % ProjectSettings.globalize_path(_output_dir))
	_finish_deferred(0)


func _prepare_seed_stall_advice(main: Node) -> bool:
	main.change_scene("player_yard", "from_house")
	await _settle()
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and outdoor.has_method("set_active_region"), "review should start in OutdoorWorld"):
		return false
	var game_state: Node = outdoor.get_node_or_null("GameState")
	if game_state != null and game_state.has_method("set_restored"):
		game_state.set_restored("old_well", true)
	if main.has_method("sync_current_scene_state"):
		main.sync_current_scene_state()

	main.change_scene("village", "village_default")
	await _settle()
	outdoor = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and String(outdoor.call("get_active_region_id")) == "village", "review should enter village region"):
		return false
	var section: Node = outdoor.get_node_or_null("Village")
	var player: Node = outdoor.get_node_or_null("Player")
	if not _expect(section != null and player != null, "village review missing section or player"):
		return false
	var notice: Node = section.get_node_or_null("VillageNotice")
	var stall: Node = section.get_node_or_null("SeedStallProxy")
	if not _expect(notice != null and stall != null, "village review missing notice or seed-stall advice interactable"):
		return false
	notice.on_interact(player)
	stall.on_interact(player)
	await _settle()
	game_state = outdoor.get_node_or_null("GameState")
	var shared_game_state: Node = main.get_node_or_null("GameState")
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox")
	if not _expect(_flag_is_set(game_state, "visited_village_seed_stall_day1"), "SeedStallProxy should keep the first seed-stall visit flag"):
		return false
	if not _expect(_flag_is_set(game_state, "asked_seed_stall_advice_spring_day1"), "SeedStallProxy should set asked_seed_stall_advice_spring_day1"):
		return false
	if not _expect(_flag_is_set(shared_game_state, "asked_seed_stall_advice_spring_day1"), "SeedStallProxy advice flag should sync to Main"):
		return false
	if not _expect(dialogue_box != null and bool(dialogue_box.visible), "SeedStallProxy should show advice dialogue in the route frame"):
		return false
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	if not _expect(String(dialogue.get("dialogue_id", "")).begins_with("seed_stall_daily_advice"), "SeedStallProxy should show seed_stall_daily_advice dialogue"):
		return false
	if not _expect(_dialogue_contains(dialogue, "院子") and _dialogue_contains(dialogue, "浇水"), "SeedStallProxy advice should point back to yard crop care"):
		return false
	return true


func _prepare_village_clue(main: Node) -> bool:
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and String(outdoor.call("get_active_region_id")) == "village", "village clue frame should continue in village"):
		return false
	var section: Node = outdoor.get_node_or_null("Village")
	var player: Node = outdoor.get_node_or_null("Player")
	if not _expect(section != null and player != null, "village clue frame missing section or player"):
		return false
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox")
	if dialogue_box != null and dialogue_box.has_method("close"):
		dialogue_box.close()
	var clue: Node = section.get_node_or_null("OldMapleClue")
	if not _expect(clue != null, "village clue frame missing OldMapleClue"):
		return false
	clue.on_interact(player)
	await _settle()
	var game_state: Node = outdoor.get_node_or_null("GameState")
	if not _expect(_flag_is_set(game_state, "found_village_soft_clue_day1"), "OldMapleClue should set the soft clue flag"):
		return false
	if not _expect(dialogue_box != null and bool(dialogue_box.visible), "OldMapleClue should show clue dialogue"):
		return false
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	return _expect(String(dialogue.get("dialogue_id", "")) == "old_maple_clue_dialogue", "OldMapleClue should show old_maple_clue_dialogue")


func _prepare_old_well_echo(main: Node) -> bool:
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null, "old-well review missing OutdoorWorld"):
		return false
	var section: Node = outdoor.get_node_or_null("Village")
	var player: Node = outdoor.get_node_or_null("Player")
	if not _expect(section != null and player != null, "old-well review missing village section or player"):
		return false
	var return_path: Node = section.get_node_or_null("VillageReturnPath")
	if not _expect(return_path != null, "VillageReturnPath should exist"):
		return false
	return_path.on_interact(player)
	await _settle()
	outdoor = main.get_current_gameplay_scene()
	if not _expect(String(outdoor.call("get_active_region_id")) == "player_yard", "VillageReturnPath should return to player_yard"):
		return false
	var game_state: Node = outdoor.get_node_or_null("GameState")
	if game_state != null and game_state.has_method("set_restored"):
		game_state.set_restored("old_well", true)
	var old_well: Node = outdoor.get_node_or_null("OldWell")
	player = outdoor.get_node_or_null("Player")
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox")
	if dialogue_box != null and dialogue_box.has_method("close"):
		dialogue_box.close()
	if not _expect(old_well != null and player != null and dialogue_box != null, "old-well review missing OldWell, player, or DialogueBox"):
		return false
	old_well.on_interact(player)
	await _settle()
	if not _expect(_flag_is_set(game_state, "heard_old_well_echo_after_village_clue_day1"), "OldWell should set the village clue echo flag"):
		return false
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	return _expect(String(dialogue.get("dialogue_id", "")) == "village_clue_old_well_echo", "OldWell should show the village clue echo dialogue")


func _prepare_mika_followup(main: Node) -> bool:
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null, "Mika review missing OutdoorWorld"):
		return false
	var time_manager: Node = outdoor.get_node_or_null("TimeManager")
	if time_manager != null:
		time_manager.set("hour", 14)
		time_manager.set("minute", 0)
		if time_manager.has_method("_update_time_block"):
			time_manager.call("_update_time_block", false)
	if main.has_method("sync_current_scene_state"):
		main.sync_current_scene_state()
	main.change_scene("forest_edge", "from_yard")
	await _settle()
	outdoor = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and String(outdoor.call("get_active_region_id")) == "forest_edge", "Mika review should enter forest_edge"):
		return false
	var schedule_director: Node = outdoor.get_node_or_null("ScheduleDirector")
	if schedule_director != null and schedule_director.has_method("apply_schedule"):
		schedule_director.apply_schedule("afternoon")
	await _settle()
	var inventory: Node = outdoor.get_node_or_null("InventoryManager")
	if inventory != null and inventory.has_method("set_selected_item"):
		inventory.set_selected_item("")
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox")
	if dialogue_box != null and dialogue_box.has_method("close"):
		dialogue_box.close()
	var player: Node = outdoor.get_node_or_null("Player")
	var mika: Node = outdoor.get_node_or_null("NPCs/Mika")
	if not _expect(player != null and mika != null and dialogue_box != null, "Mika review missing player, Mika, or DialogueBox"):
		return false
	if not _expect(bool(mika.get("visible")), "Mika should be visible for the afternoon follow-up"):
		return false
	mika.on_interact(player)
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	if not _expect(String(dialogue.get("dialogue_id", "")) == "mika_old_well_echo_followup", "Mika follow-up should play from the actual village-old-well route"):
		return false
	var game_state: Node = outdoor.get_node_or_null("GameState")
	var shared_game_state: Node = main.get_node_or_null("GameState")
	if not _expect(_flag_is_set(game_state, "heard_mika_old_well_echo_day1"), "Mika follow-up should set local seen flag"):
		return false
	return _expect(_flag_is_set(shared_game_state, "heard_mika_old_well_echo_day1"), "Mika follow-up should sync seen flag to Main")


func _capture_review_frame(key: String) -> bool:
	_hide_collision_debug_shapes(root)
	_hide_persistent_review_ui(root)
	await process_frame
	if _check_only:
		print("OK: checked village old-well Mika route state: %s" % key)
		return true
	var filename: String = String(OUTPUT_FILENAMES.get(key, "village_old_well_mika_%s.png" % key))
	var output_path: String = "%s/%s" % [_output_dir, filename]
	var image: Image = root.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("viewport screenshot unavailable for %s" % key)
		return false
	var error: Error = image.save_png(output_path)
	if error != OK:
		_fail("could not save village old-well Mika route screenshot %s: %s" % [output_path, error])
		return false
	print("OK: captured village old-well Mika route frame: %s" % output_path)
	return true


func _parse_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg == "--check-only":
			_check_only = true
		elif arg.begins_with("--out="):
			_output_dir = arg.trim_prefix("--out=")


func _hide_collision_debug_shapes(node: Node) -> void:
	if node is CollisionShape2D or node is CollisionPolygon2D or node.name == "WalkableZone":
		node.visible = false
	for child in node.get_children():
		_hide_collision_debug_shapes(child)


func _hide_persistent_review_ui(node: Node) -> void:
	if REVIEW_HIDDEN_UI_NODE_NAMES.has(String(node.name)):
		if node is CanvasItem:
			(node as CanvasItem).visible = false
		elif node is CanvasLayer:
			(node as CanvasLayer).visible = false
	for child in node.get_children():
		_hide_persistent_review_ui(child)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame
	_hide_collision_debug_shapes(root)
	_hide_persistent_review_ui(root)


func _flag_is_set(game_state: Node, flag_id: String) -> bool:
	if game_state == null or not game_state.has_method("get_flag"):
		return false
	return bool(game_state.get_flag(flag_id, false))


func _dialogue_contains(dialogue: Dictionary, needle: String) -> bool:
	var lines: Array = dialogue.get("lines", [])
	for line in lines:
		if not (line is Dictionary):
			continue
		if String(line.get("text", "")).contains(needle):
			return true
	return false


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
			_fail("village old-well Mika route review timed out")
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
