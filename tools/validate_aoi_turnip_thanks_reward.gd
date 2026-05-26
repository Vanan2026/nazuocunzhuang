extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Aoi turnip thanks reward initialize")
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
	_expect(yard != null and yard.name == "PlayerYard", "Main should load PlayerYard")
	if _has_failed:
		return

	var local_game_state: Node = yard.get_node_or_null("GameState")
	var shared_game_state: Node = main.get_node_or_null("GameState")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	var aoi: Node = yard.get_node_or_null("NPCs/Aoi")
	var dialogue_box: Node = yard.get_node_or_null("DialogueBox")
	_expect(local_game_state != null, "Yard should include local GameState")
	_expect(shared_game_state != null, "Main should expose shared GameState")
	_expect(inventory != null, "Yard should include InventoryManager")
	_expect(aoi != null, "Yard should include Aoi")
	_expect(dialogue_box != null, "Yard should include DialogueBox")
	if _has_failed:
		return

	_set_pre_share_flags(local_game_state)
	var before_reward_count := int(inventory.get_count("seed_strawberry"))
	inventory.add_item("crop_turnip", 1)
	_expect(inventory.set_selected_item("crop_turnip"), "Player should select crop_turnip for Aoi")
	aoi.on_interact(null)
	await _settle()

	_expect(bool(local_game_state.get_flag("shared_first_turnip_day1", false)), "Aoi share should set first-week share flag")
	_expect(int(inventory.get_count("seed_strawberry")) == before_reward_count + 1, "Aoi should give one strawberry seed after first turnip")
	_expect(bool(dialogue_box.visible), "Aoi thanks should show feedback")
	_expect(_dialogue_contains(dialogue_box, "草莓") or _dialogue_contains(dialogue_box, "seed_strawberry"), "Aoi thanks feedback should mention strawberry seeds")
	if _has_failed:
		return

	inventory.add_item("crop_turnip", 1)
	_expect(inventory.set_selected_item("crop_turnip"), "Player should be able to select a second turnip")
	aoi.on_interact(null)
	await _settle()
	_expect(int(inventory.get_count("seed_strawberry")) == before_reward_count + 1, "Aoi thanks reward should not repeat")
	if _has_failed:
		return

	main.sync_current_scene_state()
	_expect(bool(shared_game_state.get_flag("shared_first_turnip_day1", false)), "Aoi share flag should sync after thanks reward")
	if _has_failed:
		return

	print("OK: aoi turnip thanks reward runtime validation passed")
	_finish_deferred(0)


func _set_pre_share_flags(game_state: Node) -> void:
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_restored("old_well", true)
	game_state.set_flag("watered_first_crop_day1", true)
	game_state.set_flag("harvested_first_crop_day1", true)
	game_state.set_flag("shared_first_turnip_day1", false)


func _dialogue_contains(dialogue_box: Node, needle: String) -> bool:
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	for line in dialogue.get("lines", []):
		if line is Dictionary and String(line.get("text", "")).contains(needle):
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
			_fail("Aoi turnip thanks reward validation timed out")
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
