extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const DEFAULT_OUTPUT_DIR := "res://.codex/first_week_dialogue_route"
const WATCHDOG_TIMEOUT_SECONDS := 35.0
const OUTPUT_FILENAMES := {
	"mailbox": "first_week_mailbox_dialogue.png",
	"bulletin": "first_week_bulletin_dialogue.png",
	"mika": "first_week_mika_rumor_dialogue.png",
}

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
	print("PROGRESS: first-week dialogue route review initialize")
	if not _check_only and DisplayServer.get_name() == "headless":
		_fail("first-week dialogue route review capture requires a display server; rerun with --check-only for headless validation")
		return

	if not _check_only:
		DisplayServer.window_set_size(Vector2i(1280, 720))
		root.size = Vector2i(1280, 720)
		root.content_scale_size = Vector2i(1280, 720)
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(_output_dir))

	var main_scene := load(MAIN_PATH) as PackedScene
	if main_scene == null:
		_fail("could not load Main scene")
		return

	var main := main_scene.instantiate()
	root.add_child(main)
	_hide_collision_debug_shapes(root)
	await _settle()

	var mailbox_ready := await _prepare_mailbox_dialogue(main)
	if not mailbox_ready:
		return
	if not await _capture_review_frame("mailbox"):
		return

	var bulletin_ready := await _prepare_bulletin_dialogue(main)
	if not bulletin_ready:
		return
	if not await _capture_review_frame("bulletin"):
		return

	var mika_ready := await _prepare_mika_rumor_dialogue(main)
	if not mika_ready:
		return
	if not await _capture_review_frame("mika"):
		return

	if _check_only:
		print("OK: first-week dialogue route review check-only validated")
	else:
		print("OK: first-week dialogue route review screenshots saved to %s" % ProjectSettings.globalize_path(_output_dir))
	_finish_deferred(0)


func _prepare_mailbox_dialogue(main: Node) -> bool:
	main.change_scene("player_yard", "from_house")
	await _settle()
	var yard: Node = main.get_current_gameplay_scene()
	if not _expect(yard != null and yard.name == "PlayerYard", "mailbox review should enter PlayerYard"):
		return false
	var mailbox: Node = yard.get_node_or_null("Mailbox")
	var player: Node = yard.get_node_or_null("Player")
	var dialogue_box: Node = yard.get_node_or_null("DialogueBox")
	if not _expect(mailbox != null and player != null and dialogue_box != null, "mailbox review missing required nodes"):
		return false
	mailbox.on_interact(player)
	await _settle()
	return _expect_dialogue(dialogue_box, "邮箱", "村务")


func _prepare_bulletin_dialogue(main: Node) -> bool:
	var yard: Node = main.get_current_gameplay_scene()
	if yard == null or yard.name != "PlayerYard":
		main.change_scene("player_yard", "from_house")
		await _settle()
		yard = main.get_current_gameplay_scene()
	if not _expect(yard != null and yard.name == "PlayerYard", "bulletin review should use PlayerYard"):
		return false
	var dialogue_box: Node = yard.get_node_or_null("DialogueBox")
	if dialogue_box != null and dialogue_box.has_method("close"):
		dialogue_box.close()
	var game_state: Node = yard.get_node_or_null("GameState")
	if game_state != null and game_state.has_method("set_flag"):
		game_state.set_flag("forest_edge_hint", true)
		game_state.set_flag("heard_forest_edge_notice", false)
	var bulletin: Node = yard.get_node_or_null("BulletinBoard")
	var player: Node = yard.get_node_or_null("Player")
	if not _expect(bulletin != null and player != null and dialogue_box != null, "bulletin review missing required nodes"):
		return false
	bulletin.on_interact(player)
	await _settle()
	return _expect_dialogue(dialogue_box, "公告板", "森林边缘")


func _prepare_mika_rumor_dialogue(main: Node) -> bool:
	var yard: Node = main.get_current_gameplay_scene()
	if yard == null or yard.name != "PlayerYard":
		main.change_scene("player_yard", "from_house")
		await _settle()
		yard = main.get_current_gameplay_scene()
	if not _expect(yard != null and yard.name == "PlayerYard", "Mika review should stage from PlayerYard"):
		return false

	var yard_dialogue: Node = yard.get_node_or_null("DialogueBox")
	if yard_dialogue != null and yard_dialogue.has_method("close"):
		yard_dialogue.close()
	var yard_game_state: Node = yard.get_node_or_null("GameState")
	var yard_time: Node = yard.get_node_or_null("TimeManager")
	_set_pre_mika_flags(yard_game_state)
	if yard_time != null:
		yard_time.set("hour", 14)
		yard_time.set("minute", 0)
		if yard_time.has_method("_update_time_block"):
			yard_time.call("_update_time_block", false)
	main.sync_current_scene_state()
	main.change_scene("forest_edge", "from_yard")
	await _settle()
	if not _expect_current_objective(main, "heard_npc_forest_edge"):
		return false

	var forest: Node = main.get_current_gameplay_scene()
	if not _expect(forest != null and forest.name == "ForestEdge", "Mika review should enter ForestEdge"):
		return false
	var forest_inventory: Node = forest.get_node_or_null("InventoryManager")
	if forest_inventory != null and forest_inventory.has_method("set_selected_item"):
		forest_inventory.set_selected_item("")
	var schedule_director: Node = forest.get_node_or_null("ScheduleDirector")
	if schedule_director != null and schedule_director.has_method("apply_schedule"):
		schedule_director.apply_schedule("afternoon")
	var dialogue_box: Node = forest.get_node_or_null("DialogueBox")
	var player: Node = forest.get_node_or_null("Player")
	var mika: Node = forest.get_node_or_null("NPCs/Mika")
	if not _expect(dialogue_box != null and player != null and mika != null, "Mika review missing required nodes"):
		return false
	mika.on_interact(player)
	await _settle()
	return _expect_dialogue(dialogue_box, "美香", "树根小龛")


func _capture_review_frame(key: String) -> bool:
	_hide_collision_debug_shapes(root)
	await process_frame
	if _check_only:
		print("OK: checked first-week dialogue route state: %s" % key)
		return true
	var filename := String(OUTPUT_FILENAMES.get(key, "first_week_%s_dialogue.png" % key))
	var output_path := "%s/%s" % [_output_dir, filename]
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("viewport screenshot unavailable for %s" % key)
		return false
	var error := image.save_png(output_path)
	if error != OK:
		_fail("could not save first-week dialogue route screenshot %s: %s" % [output_path, error])
		return false
	print("OK: captured first-week dialogue route frame: %s" % output_path)
	return true


func _expect_dialogue(dialogue_box: Node, expected_speaker: String, required_text: String) -> bool:
	if not _expect(dialogue_box != null, "dialogue box should exist"):
		return false
	if not _expect(bool(dialogue_box.get("visible")), "dialogue box should be visible"):
		return false
	var speaker_label := dialogue_box.get_node_or_null("Panel/Content/TextColumn/SpeakerLabel") as Label
	var line_label := dialogue_box.get_node_or_null("Panel/Content/TextColumn/LineLabel") as Label
	if not _expect(speaker_label != null and line_label != null, "dialogue labels should exist"):
		return false
	if not _expect(speaker_label.text.contains(expected_speaker), "dialogue speaker should contain %s, got %s" % [expected_speaker, speaker_label.text]):
		return false
	return _expect(line_label.text.contains(required_text), "dialogue line should contain %s, got %s" % [required_text, line_label.text])


func _set_pre_mika_flags(game_state: Node) -> void:
	if game_state == null:
		return
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
	if game_state.has_method("set_restored"):
		game_state.set_restored("old_well", true)
		game_state.set_restored("garden_bench", true)
		game_state.set_restored("village_sign", true)


func _expect_current_objective(main: Node, expected_objective_id: String) -> bool:
	var quest_manager: Node = main.get_node_or_null("QuestManager")
	var game_state: Node = main.get_node_or_null("GameState")
	var scene_router: Node = main.get_node_or_null("SceneRouter")
	if not _expect(quest_manager != null and game_state != null and scene_router != null, "objective review missing shared quest state"):
		return false
	if quest_manager.has_method("update_first_week_progress"):
		quest_manager.update_first_week_progress(game_state, scene_router)
	if not quest_manager.has_method("get_current_first_week_objective_id"):
		return _expect(false, "QuestManager should expose current objective id for review")
	var actual_objective_id := String(quest_manager.get_current_first_week_objective_id())
	return _expect(actual_objective_id == expected_objective_id, "expected current objective %s, got %s" % [expected_objective_id, actual_objective_id])


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


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame
	_hide_collision_debug_shapes(root)


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
			_fail("first-week dialogue route review timed out")
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
