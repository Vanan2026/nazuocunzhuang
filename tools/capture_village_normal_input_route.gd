extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DEFAULT_OUTPUT_DIR := "res://.codex/village_normal_input_route"
const WATCHDOG_TIMEOUT_SECONDS := 60.0
const VIEWPORT_SIZE := Vector2i(1280, 720)
const DRIVE_STOP_DISTANCE := 12.0
const DRIVE_AXIS_DEADZONE := 4.0
const DRIVE_MAX_SECONDS := 10.0

const OUTPUT_FILENAMES := {
	"walk_to_village_prompt": "01_walk_to_village_prompt.png",
	"notice_input_dialogue": "02_notice_input_dialogue.png",
	"seed_stall_input_dialogue": "03_seed_stall_input_dialogue.png",
	"old_maple_input_dialogue": "04_old_maple_input_dialogue.png",
	"old_well_input_echo": "05_old_well_input_echo.png",
	"mika_input_followup": "06_mika_input_followup.png",
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
var _watchdog_timer: Timer = null
var _finished := false
var _has_failed := false


func _initialize() -> void:
	debug_collisions_hint = false
	debug_navigation_hint = false
	debug_paths_hint = false
	_parse_args()
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	print("PROGRESS: village normal-input route review initialize")
	if not _check_only and DisplayServer.get_name() == "headless":
		_fail("village normal-input route capture requires a display server; rerun with --check-only for headless validation")
		return
	if not _check_only:
		DisplayServer.window_set_size(VIEWPORT_SIZE)
		root.size = VIEWPORT_SIZE
		root.content_scale_size = VIEWPORT_SIZE
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(_output_dir))

	var main_scene := load(MAIN_PATH) as PackedScene
	if main_scene == null:
		_fail("could not load Main scene")
		return
	var main := main_scene.instantiate()
	root.add_child(main)
	await _settle()
	main.change_scene("player_yard", "from_house")
	await _settle()

	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and outdoor.has_method("get_active_region_id"), "normal-input route should start in OutdoorWorld"):
		return
	_prepare_route_state(main, outdoor)

	if not await _prepare_walk_to_village_prompt(main):
		return
	if not await _capture_review_frame("walk_to_village_prompt"):
		return
	if not await _prepare_notice_input_dialogue(main):
		return
	if not await _capture_review_frame("notice_input_dialogue"):
		return
	if not await _prepare_seed_stall_input_dialogue(main):
		return
	if not await _capture_review_frame("seed_stall_input_dialogue"):
		return
	if not await _prepare_old_maple_input_dialogue(main):
		return
	if not await _capture_review_frame("old_maple_input_dialogue"):
		return
	if not await _prepare_old_well_input_echo(main):
		return
	if not await _capture_review_frame("old_well_input_echo"):
		return
	if not await _prepare_mika_input_followup(main):
		return
	if not await _capture_review_frame("mika_input_followup"):
		return

	_release_movement_actions()
	if _check_only:
		print("OK: village normal-input route review check-only validated")
	else:
		print("OK: village normal-input route screenshots saved to %s" % ProjectSettings.globalize_path(_output_dir))
	_finish_deferred(0)


func _prepare_route_state(main: Node, outdoor: Node) -> void:
	var local_game_state: Node = outdoor.get_node_or_null("GameState")
	var shared_game_state: Node = main.get_node_or_null("GameState")
	for game_state in [local_game_state, shared_game_state]:
		if game_state != null and game_state.has_method("set_restored"):
			game_state.set_restored("old_well", true)
	if main.has_method("sync_current_scene_state"):
		main.sync_current_scene_state()


func _prepare_walk_to_village_prompt(main: Node) -> bool:
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null, "walk-to-village prompt missing OutdoorWorld"):
		return false
	var village_path := await _walk_to_interactable(outdoor, "VillagePath")
	if village_path == null:
		return false
	if not _expect_prompt_for(village_path, "VillagePath"):
		return false
	await _press_interact_action()
	await _settle()
	var game_state: Node = outdoor.get_node_or_null("GameState")
	return _expect(_flag_is_set(game_state, "visited_village_path"), "VillagePath should set visited_village_path via player input")


func _prepare_notice_input_dialogue(main: Node) -> bool:
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null, "notice input route missing OutdoorWorld"):
		return false
	var notice_target := _find_node_named(outdoor, "VillageNotice") as Node2D
	if notice_target == null:
		_fail("notice input route missing VillageNotice")
		return false
	if not await _drive_player_to_global(_get_player(outdoor), notice_target.global_position, DRIVE_MAX_SECONDS):
		return false
	if not _expect(String(outdoor.call("get_active_region_id")) == "village", "walking to VillageNotice should activate village region"):
		return false
	if not _expect_nearest(outdoor, "VillageNotice"):
		return false
	if not _expect_prompt_for(notice_target, "VillageNotice"):
		return false
	await _press_interact_action()
	await _settle()
	var game_state: Node = outdoor.get_node_or_null("GameState")
	if not _expect(_flag_is_set(game_state, "read_village_notice_day1"), "VillageNotice should set read_village_notice_day1 via player input"):
		return false
	if not _expect_dialogue_id(outdoor, "village_notice_dialogue", "VillageNotice should show dialogue feedback after player input"):
		return false
	return _expect_prompt_hidden("VillageNotice dialogue")


func _prepare_seed_stall_input_dialogue(main: Node) -> bool:
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null, "seed-stall input route missing OutdoorWorld"):
		return false
	_close_dialogue(outdoor)
	var stall := await _walk_to_interactable(outdoor, "SeedStallProxy")
	if stall == null:
		return false
	await _press_interact_action()
	await _settle()
	var game_state: Node = outdoor.get_node_or_null("GameState")
	if not _expect(_flag_is_set(game_state, "asked_seed_stall_advice_spring_day1"), "SeedStallProxy should set advice flag via player input"):
		return false
	if not _expect_dialogue_prefix(outdoor, "seed_stall_daily_advice", "SeedStallProxy should show daily advice after player input"):
		return false
	return _expect_prompt_hidden("SeedStallProxy dialogue")


func _prepare_old_maple_input_dialogue(main: Node) -> bool:
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null, "old-maple input route missing OutdoorWorld"):
		return false
	_close_dialogue(outdoor)
	var clue := await _walk_to_interactable(outdoor, "OldMapleClue")
	if clue == null:
		return false
	await _press_interact_action()
	await _settle()
	var game_state: Node = outdoor.get_node_or_null("GameState")
	if not _expect(_flag_is_set(game_state, "found_village_soft_clue_day1"), "OldMapleClue should set clue flag via player input"):
		return false
	if not _expect_dialogue_id(outdoor, "old_maple_clue_dialogue", "OldMapleClue should show clue dialogue after player input"):
		return false
	return _expect_prompt_hidden("OldMapleClue dialogue")


func _prepare_old_well_input_echo(main: Node) -> bool:
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null, "old-well input route missing OutdoorWorld"):
		return false
	_close_dialogue(outdoor)
	var return_path := await _walk_to_interactable(outdoor, "VillageReturnPath")
	if return_path == null:
		return false
	await _press_interact_action()
	await _settle()
	outdoor = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and String(outdoor.call("get_active_region_id")) == "player_yard", "VillageReturnPath should return to player_yard via player input"):
		return false
	_close_dialogue(outdoor)
	var old_well := await _walk_to_interactable(outdoor, "OldWell")
	if old_well == null:
		return false
	await _press_interact_action()
	await _settle()
	var game_state: Node = outdoor.get_node_or_null("GameState")
	if not _expect(_flag_is_set(game_state, "heard_old_well_echo_after_village_clue_day1"), "OldWell should set village clue echo flag via player input"):
		return false
	if not _expect_dialogue_id(outdoor, "village_clue_old_well_echo", "OldWell should show village clue echo after player input"):
		return false
	return _expect_prompt_hidden("OldWell dialogue")


func _prepare_mika_input_followup(main: Node) -> bool:
	var outdoor: Node = main.get_current_gameplay_scene()
	if not _expect(outdoor != null, "Mika input route missing OutdoorWorld"):
		return false
	_close_dialogue(outdoor)
	var time_manager: Node = outdoor.get_node_or_null("TimeManager")
	if time_manager != null:
		time_manager.set("hour", 14)
		time_manager.set("minute", 0)
		if time_manager.has_method("_update_time_block"):
			time_manager.call("_update_time_block", false)
	if main.has_method("sync_current_scene_state"):
		main.sync_current_scene_state()
	var forest_gate := await _walk_to_interactable(outdoor, "ForestTrailGate")
	if forest_gate == null:
		return false
	await _press_interact_action()
	await _settle()
	outdoor = main.get_current_gameplay_scene()
	if not _expect(outdoor != null and String(outdoor.call("get_active_region_id")) == "forest_edge", "ForestTrailGate should enter forest_edge via player input"):
		return false
	var schedule_director: Node = outdoor.get_node_or_null("ScheduleDirector")
	if schedule_director != null and schedule_director.has_method("apply_schedule"):
		schedule_director.apply_schedule("afternoon")
	await _settle()
	_close_dialogue(outdoor)
	var inventory: Node = outdoor.get_node_or_null("InventoryManager")
	if inventory != null and inventory.has_method("set_selected_item"):
		inventory.set_selected_item("")
	var mika := await _walk_to_interactable(outdoor, "Mika")
	if mika == null:
		return false
	await _press_interact_action()
	await _settle()
	var game_state: Node = outdoor.get_node_or_null("GameState")
	if not _expect(_flag_is_set(game_state, "heard_mika_old_well_echo_day1"), "Mika should set follow-up seen flag via player input"):
		return false
	if not _expect_dialogue_id(outdoor, "mika_old_well_echo_followup", "Mika should show old-well follow-up after player input"):
		return false
	return _expect_prompt_hidden("Mika dialogue")


func _walk_to_interactable(outdoor: Node, node_name: String) -> Node2D:
	var target := _find_node_named(outdoor, node_name) as Node2D
	if target == null:
		_fail("normal-input route missing interactable: %s" % node_name)
		return null
	var player := _get_player(outdoor)
	if not await _drive_player_to_global(player, target.global_position, DRIVE_MAX_SECONDS):
		return null
	if not _expect_nearest(outdoor, node_name):
		return null
	if not _expect_prompt_for(target, node_name):
		return null
	return target


func _drive_player_to_global(player: Node2D, target_global: Vector2, max_seconds: float) -> bool:
	if player == null:
		_fail("normal-input route missing Player")
		return false
	var frame_budget := int(max_seconds * 60.0)
	for _i in range(frame_budget):
		var delta := target_global - player.global_position
		if delta.length() <= DRIVE_STOP_DISTANCE:
			_release_movement_actions()
			await _settle()
			return true
		_press_direction(delta)
		await physics_frame
	_release_movement_actions()
	return _expect(false, "player input drive could not reach target %.1f, %.1f from %.1f, %.1f" % [
		target_global.x,
		target_global.y,
		player.global_position.x,
		player.global_position.y,
	])


func _press_direction(delta: Vector2) -> void:
	_set_action_pressed("move_left", delta.x < -DRIVE_AXIS_DEADZONE)
	_set_action_pressed("move_right", delta.x > DRIVE_AXIS_DEADZONE)
	_set_action_pressed("move_up", delta.y < -DRIVE_AXIS_DEADZONE)
	_set_action_pressed("move_down", delta.y > DRIVE_AXIS_DEADZONE)


func _set_action_pressed(action_name: String, should_press: bool) -> void:
	if should_press:
		Input.action_press(action_name)
	else:
		Input.action_release(action_name)


func _release_movement_actions() -> void:
	Input.action_release("move_left")
	Input.action_release("move_right")
	Input.action_release("move_up")
	Input.action_release("move_down")


func _press_interact_action() -> void:
	var press := InputEventAction.new()
	press.action = "interact"
	press.pressed = true
	Input.parse_input_event(press)
	await process_frame
	var release := InputEventAction.new()
	release.action = "interact"
	release.pressed = false
	Input.parse_input_event(release)
	await process_frame


func _expect_nearest(outdoor: Node, node_name: String) -> bool:
	var player := _get_player(outdoor)
	if not _expect(player != null, "nearest check missing Player"):
		return false
	var interaction_area: Node = player.get_node_or_null("InteractionArea")
	if not _expect(interaction_area != null and interaction_area.has_method("get_nearest_interactable"), "Player should expose InteractionArea nearest target"):
		return false
	var nearest: Node = interaction_area.get_nearest_interactable()
	return _expect(nearest != null and String(nearest.name) == node_name, "expected nearest interactable %s, got %s" % [node_name, _node_name_or_null(nearest)])


func _expect_prompt_for(target: Node, label: String) -> bool:
	var hint_ui := _get_interaction_hint_ui()
	if not _expect(hint_ui != null, "InteractionHintUI should exist for %s prompt" % label):
		return false
	if not _expect(target != null and target.has_method("get_interaction_hint"), "%s should expose get_interaction_hint" % label):
		return false
	var expected_hint := String(target.call("get_interaction_hint"))
	var current_hint := String(hint_ui.get("current_hint"))
	if not _expect(not expected_hint.is_empty(), "%s should have non-empty interaction hint" % label):
		return false
	return _expect(current_hint == expected_hint, "%s prompt should show nearest target hint, expected %s, got %s" % [label, expected_hint, current_hint])


func _expect_prompt_hidden(label: String) -> bool:
	var hint_ui := _get_interaction_hint_ui()
	if not _expect(hint_ui != null, "InteractionHintUI should exist for %s prompt hiding" % label):
		return false
	var current_hint := String(hint_ui.get("current_hint"))
	var hint_label := hint_ui.get("hint_label") as Label
	var label_still_visible := hint_label != null and bool(hint_label.visible) and hint_label.modulate.a > 0.05 and not hint_label.text.is_empty()
	return _expect(current_hint.is_empty() and not label_still_visible, "%s should hide InteractionHintUI while dialogue is visible, got hint=%s visible=%s alpha=%.2f" % [
		label,
		current_hint,
		str(hint_label != null and bool(hint_label.visible)),
		hint_label.modulate.a if hint_label != null else 0.0,
	])


func _expect_dialogue_id(outdoor: Node, expected_dialogue_id: String, message: String) -> bool:
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox")
	if not _expect(dialogue_box != null and bool(dialogue_box.visible), "%s; DialogueBox should be visible" % message):
		return false
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	return _expect(String(dialogue.get("dialogue_id", "")) == expected_dialogue_id, "%s; expected %s, got %s" % [message, expected_dialogue_id, String(dialogue.get("dialogue_id", ""))])


func _expect_dialogue_prefix(outdoor: Node, expected_prefix: String, message: String) -> bool:
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox")
	if not _expect(dialogue_box != null and bool(dialogue_box.visible), "%s; DialogueBox should be visible" % message):
		return false
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	return _expect(String(dialogue.get("dialogue_id", "")).begins_with(expected_prefix), "%s; expected prefix %s, got %s" % [message, expected_prefix, String(dialogue.get("dialogue_id", ""))])


func _capture_review_frame(key: String) -> bool:
	_hide_collision_debug_shapes(root)
	_hide_persistent_review_ui(root)
	await process_frame
	await process_frame
	if _check_only:
		print("OK: checked village normal-input route state: %s" % key)
		return true
	var filename := String(OUTPUT_FILENAMES.get(key, "village_normal_input_%s.png" % key))
	var output_path := "%s/%s" % [_output_dir, filename]
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("viewport screenshot unavailable for %s" % key)
		return false
	var error := image.save_png(output_path)
	if error != OK:
		_fail("could not save village normal-input screenshot %s: %s" % [output_path, error])
		return false
	print("OK: captured village normal-input route frame: %s" % output_path)
	return true


func _get_player(outdoor: Node) -> Node2D:
	if outdoor == null:
		return null
	return outdoor.get_node_or_null("Player") as Node2D


func _get_interaction_hint_ui() -> Node:
	return root.get_node_or_null("InteractionHintUI")


func _close_dialogue(outdoor: Node) -> void:
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox")
	if dialogue_box != null and dialogue_box.has_method("close"):
		dialogue_box.close()


func _flag_is_set(game_state: Node, flag_id: String) -> bool:
	if game_state == null or not game_state.has_method("get_flag"):
		return false
	return bool(game_state.get_flag(flag_id, false))


func _find_node_named(node: Node, node_name: String) -> Node:
	if node == null:
		return null
	if String(node.name) == node_name:
		return node
	for child in node.get_children():
		var found := _find_node_named(child, node_name)
		if found != null:
			return found
	return null


func _node_name_or_null(node: Node) -> String:
	if node == null:
		return "<null>"
	return String(node.name)


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
	await create_timer(0.12).timeout
	await process_frame
	await physics_frame
	await process_frame
	_hide_collision_debug_shapes(root)
	_hide_persistent_review_ui(root)


func _expect(condition: bool, message: String) -> bool:
	if not condition:
		_fail(message)
		return false
	return true


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	_release_movement_actions()
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
			_fail("village normal-input route review timed out")
	)
	_watchdog_timer.start()


func _finish_deferred(exit_code: int) -> void:
	if _finished:
		return
	_finished = true
	_release_movement_actions()
	if _watchdog_timer != null:
		_watchdog_timer.stop()
		_watchdog_timer.queue_free()
		_watchdog_timer = null
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
