extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: restoration reward loop initialize")
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
	main.change_scene("player_yard", "from_house")
	await _settle()

	await _validate_old_well_rewards(main)
	if _has_failed:
		return
	await _validate_save_resume_keeps_reward_single(main)
	if _has_failed:
		return

	print("OK: restoration reward loop runtime validation passed")
	_finish_deferred(0)


func _validate_old_well_rewards(main: Node) -> void:
	var yard: Node = main.get_current_gameplay_scene()
	_expect(yard != null, "PlayerYard should be active")
	if _has_failed:
		return

	var old_well: Node = yard.get_node_or_null("OldWell")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	var game_state: Node = yard.get_node_or_null("GameState")
	var player: Node = yard.get_node_or_null("Player")
	_expect(old_well != null, "PlayerYard should include OldWell")
	_expect(inventory != null, "PlayerYard should include InventoryManager")
	_expect(game_state != null, "PlayerYard should include GameState")
	_expect(player != null, "PlayerYard should include Player")
	if _has_failed:
		return

	inventory.add_item("wood", 20)
	inventory.add_item("stone", 10)
	var seed_before := int(inventory.get_count("seed_turnip"))
	var fragment_before := int(inventory.get_count("old_bell_fragment"))
	old_well.on_interact(player)
	await _settle()

	_expect(bool(game_state.is_restored("old_well")), "Old well should be restored after meeting requirements")
	_expect(int(inventory.get_count("wood")) == 0, "Old well repair should consume required wood")
	_expect(int(inventory.get_count("stone")) == 0, "Old well repair should consume required stone")
	_expect(int(game_state.get_player_money()) == 0, "Old well repair should consume required money")
	_expect(int(inventory.get_count("seed_turnip")) == seed_before + 3, "Old well repair should grant turnip seeds once")
	_expect(int(inventory.get_count("old_bell_fragment")) == fragment_before + 1, "Old well repair should grant the bell fragment once")
	if _has_failed:
		return

	old_well.on_interact(player)
	await _settle()
	_expect(int(inventory.get_count("seed_turnip")) == seed_before + 3, "Restored old well should not grant more turnip seeds")
	_expect(int(inventory.get_count("old_bell_fragment")) == fragment_before + 1, "Restored old well should not grant more bell fragments")


func _validate_save_resume_keeps_reward_single(main: Node) -> void:
	var yard: Node = main.get_current_gameplay_scene()
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	_expect(inventory != null, "Active yard should keep InventoryManager before save")
	if _has_failed:
		return
	var saved_seed_count := int(inventory.get_count("seed_turnip"))
	var saved_fragment_count := int(inventory.get_count("old_bell_fragment"))
	var data: Dictionary = main.build_main_flow_save_data()
	main.queue_free()
	await _settle()

	var main_scene := load(MAIN_PATH) as PackedScene
	var fresh_main: Node = main_scene.instantiate()
	root.add_child(fresh_main)
	await _settle()
	fresh_main.apply_main_flow_save_data(data)
	await _settle()
	_expect(String(fresh_main.get_current_gameplay_scene_id()) == "player_yard", "Fresh Main should resume the yard scene")
	if _has_failed:
		return
	var fresh_yard: Node = fresh_main.get_current_gameplay_scene()
	var fresh_old_well: Node = fresh_yard.get_node_or_null("OldWell")
	var fresh_inventory: Node = fresh_yard.get_node_or_null("InventoryManager")
	var fresh_player: Node = fresh_yard.get_node_or_null("Player")
	_expect(fresh_old_well != null, "Fresh yard should include OldWell")
	_expect(fresh_inventory != null, "Fresh yard should include InventoryManager")
	_expect(fresh_player != null, "Fresh yard should include Player")
	if _has_failed:
		return
	_expect(int(fresh_inventory.get_count("seed_turnip")) == saved_seed_count, "Saved turnip seed reward should persist")
	_expect(int(fresh_inventory.get_count("old_bell_fragment")) == saved_fragment_count, "Saved bell fragment reward should persist")
	fresh_old_well.on_interact(fresh_player)
	await _settle()
	_expect(int(fresh_inventory.get_count("seed_turnip")) == saved_seed_count, "Restored old well should not grant seeds after save resume")
	_expect(int(fresh_inventory.get_count("old_bell_fragment")) == saved_fragment_count, "Restored old well should not grant bell fragment after save resume")


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
			_fail("Restoration reward loop validation timed out")
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
