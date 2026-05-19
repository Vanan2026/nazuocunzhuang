extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 20.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: task010 restoration initialize")
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

	_validate_initial_scene(yard)
	if _has_failed:
		return

	var data_registry := yard.get_node("DataRegistry") as Node
	var game_state := yard.get_node("GameState") as Node
	var old_well := yard.get_node("OldWell") as Node
	var inventory := yard.get_node("InventoryManager") as Node
	var player := yard.get_node("Player") as Node
	var save_manager := yard.get_node("SaveManager") as Node
	var old_well_sprite := old_well.get_node_or_null("OldWellArt")

	data_registry.load_all_data()
	data_registry.validate_all_data()
	await process_frame

	inventory.add_item("wood", 1)
	inventory.add_item("stone", 1)
	game_state.set_player_money(100)
	old_well.on_interact(player)
	await process_frame
	_expect(not game_state.is_restored("old_well"), "Old well should stay broken without enough requirements")
	_expect(not bool(game_state.get_flag("restored_old_well")), "restored_old_well should remain false before requirements met")

	inventory.add_item("wood", 19)
	inventory.add_item("stone", 9)
	game_state.set_player_money(500)
	var emitted := {"value": false}
	var event_bus := yard.get_node("EventBus") as Node
	if event_bus.has_signal("restoration_completed"):
		event_bus.restoration_completed.connect(func(restoration_id: String) -> void:
			if restoration_id == "old_well":
				emitted["value"] = true
		)
	old_well.on_interact(player)
	await process_frame
	_expect(bool(emitted["value"]), "EventBus should emit restoration_completed for old_well")
	_expect(game_state.is_restored("old_well"), "Old well should become restored when requirements are met")
	_expect(bool(game_state.get_flag("yard_water_source")), "Restoration should unlock yard_water_source flag")
	_expect(bool(game_state.get_flag("rumor_old_well_bell")), "Restoration should unlock rumor flag")

	var payload := save_manager.build_runtime_payload(game_state) as Dictionary
	_expect(payload.get("restoration_states", {}).has("old_well"), "Save payload should include old_well")
	_expect(bool(payload.get("restoration_states", {}).get("old_well", false)), "Save payload should mark old_well restored")

	var before := _snapshot_resources(inventory)
	old_well.on_interact(player)
	await process_frame
	var after := _snapshot_resources(inventory)
	_expect(before.get("wood", 0) == after.get("wood", 0), "Repaired well should not consume wood again")
	_expect(before.get("stone", 0) == after.get("stone", 0), "Repaired well should not consume stone again")

	var repaired_path := ""
	if old_well_sprite != null:
		repaired_path = str(old_well_sprite.get("texture_path"))
	_expect(not repaired_path.is_empty(), "Old well sprite should have a visual state set")

	print("OK: Task 010 restoration runtime validation passed")
	_finish_deferred(0)


func _validate_initial_scene(yard: Node) -> void:
	var required_nodes := ["DataRegistry", "GameState", "EventBus", "SaveManager", "OldWell", "InventoryManager", "DialogueBox", "Player"]
	for node_name in required_nodes:
		if yard.get_node_or_null(node_name) == null:
			_fail("PlayerYard missing required node: %s" % node_name)
			return


func _snapshot_resources(inventory: Node) -> Dictionary:
	var result := {}
	result["wood"] = int(inventory.get_count("wood")) if inventory.has_method("get_count") else 0
	result["stone"] = int(inventory.get_count("stone")) if inventory.has_method("get_count") else 0
	return result


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
			_fail("Task 010 restoration validation timed out")
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
