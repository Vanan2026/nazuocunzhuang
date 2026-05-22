extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const HOUSE_PATH := "res://game/scenes/home/PlayerHouse.tscn"
const YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"
const FOREST_PATH := "res://game/scenes/world/ForestEdge.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: main flow playable initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var configured_main := String(ProjectSettings.get_setting("application/run/main_scene", ""))
	_expect(configured_main == MAIN_PATH, "project main_scene should launch the game Main scene")
	if _has_failed:
		return

	await _validate_main_and_house()
	if _has_failed:
		return

	await _validate_yard_flow()
	if _has_failed:
		return

	await _validate_forest_edge_flow()
	if _has_failed:
		return

	print("OK: main flow playable runtime validation passed")
	_finish_deferred(0)


func _validate_main_and_house() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	var house_scene := load(HOUSE_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	_expect(house_scene != null, "PlayerHouse should load")
	if _has_failed:
		return

	var main := main_scene.instantiate()
	root.add_child(main)
	await process_frame
	_expect(main.get_node_or_null("PlayerHouse") != null, "Main should start inside PlayerHouse")
	main.queue_free()
	await process_frame

	var house := house_scene.instantiate()
	root.add_child(house)
	await process_frame
	var door := house.get_node_or_null("DoorToYard")
	_expect(door != null, "PlayerHouse should include DoorToYard")
	_expect(String(door.get("target_scene")) == YARD_PATH, "DoorToYard should target PlayerYard")
	house.queue_free()
	await process_frame


func _validate_yard_flow() -> void:
	var yard_scene := load(YARD_PATH) as PackedScene
	_expect(yard_scene != null, "PlayerYard should load")
	if _has_failed:
		return

	var yard := yard_scene.instantiate()
	root.add_child(yard)
	await process_frame
	await process_frame

	var registry := yard.get_node_or_null("DataRegistry")
	var inventory := yard.get_node_or_null("InventoryManager")
	var game_state := yard.get_node_or_null("GameState")
	var dialogue_box := yard.get_node_or_null("DialogueBox")
	var time_manager := yard.get_node_or_null("TimeManager")
	var schedule_director := yard.get_node_or_null("ScheduleDirector")
	var bulletin := yard.get_node_or_null("BulletinBoard")
	var forest_gate := yard.get_node_or_null("ForestTrailGate")
	var player := yard.get_node_or_null("Player")
	var garden_bench := yard.get_node_or_null("GardenBenchRepair")
	var village_sign := yard.get_node_or_null("VillageSignRepair")

	for pair in {
		"DataRegistry": registry,
		"InventoryManager": inventory,
		"GameState": game_state,
		"DialogueBox": dialogue_box,
		"TimeManager": time_manager,
		"ScheduleDirector": schedule_director,
		"BulletinBoard": bulletin,
		"ForestTrailGate": forest_gate,
		"Player": player,
		"GardenBenchRepair": garden_bench,
		"VillageSignRepair": village_sign,
	}.keys():
		var node: Node = {
			"DataRegistry": registry,
			"InventoryManager": inventory,
			"GameState": game_state,
			"DialogueBox": dialogue_box,
			"TimeManager": time_manager,
			"ScheduleDirector": schedule_director,
			"BulletinBoard": bulletin,
			"ForestTrailGate": forest_gate,
			"Player": player,
			"GardenBenchRepair": garden_bench,
			"VillageSignRepair": village_sign,
		}[pair]
		_expect(node != null, "PlayerYard missing main-flow node: %s" % pair)
		if _has_failed:
			return

	_expect(registry.has_method("get_npc_schedule"), "DataRegistry should expose npc schedule lookup")
	_expect(registry.get_npc_schedule("shopkeeper_basic").size() > 0, "shopkeeper_basic schedule should load")
	_expect(schedule_director.has_method("apply_schedule"), "ScheduleDirector should apply schedules")
	_expect(schedule_director.has_method("get_current_assignment"), "ScheduleDirector should expose current assignment")
	if _has_failed:
		return

	time_manager.hour = 14
	time_manager.minute = 0
	time_manager.call("_update_time_block", false)
	schedule_director.apply_schedule()
	var aoi_assignment: Dictionary = schedule_director.get_current_assignment("aoi")
	_expect(String(aoi_assignment.get("time_block", "")) == "afternoon", "Aoi should resolve an afternoon schedule")
	_expect(String(aoi_assignment.get("scene_id", "")) == "player_yard", "Aoi should have a yard afternoon schedule for MVP")
	if _has_failed:
		return

	bulletin.on_interact(player)
	await process_frame
	_expect(bool(dialogue_box.visible), "BulletinBoard should open bulletin rumors")
	_expect(_dialogue_contains(dialogue_box.dialogue, "公告"), "BulletinBoard dialogue should read as a bulletin")
	dialogue_box.close()
	if _has_failed:
		return

	inventory.add_item("wood", 12)
	inventory.add_item("stone", 4)
	game_state.set_player_money(500)
	garden_bench.on_interact(player)
	await process_frame
	_expect(game_state.is_restored("garden_bench"), "Garden bench should be restorable")
	village_sign.on_interact(player)
	await process_frame
	_expect(game_state.is_restored("village_sign"), "Village sign should be restorable")
	_expect(bool(game_state.get_flag("forest_edge_hint", false)), "Village sign should unlock a forest edge hint flag")
	_expect(String(forest_gate.get("target_scene")) == FOREST_PATH, "ForestTrailGate should target ForestEdge")

	yard.queue_free()
	await process_frame


func _validate_forest_edge_flow() -> void:
	var forest_scene := load(FOREST_PATH) as PackedScene
	_expect(forest_scene != null, "ForestEdge should load")
	if _has_failed:
		return

	var forest := forest_scene.instantiate()
	root.add_child(forest)
	await process_frame
	await process_frame

	var inventory := forest.get_node_or_null("InventoryManager")
	var game_state := forest.get_node_or_null("GameState")
	var player := forest.get_node_or_null("Player")
	var back_to_yard := forest.get_node_or_null("BackToYard")
	var fallen_branch := forest.get_node_or_null("FallenBranchBundle")
	var quiet_shrine := forest.get_node_or_null("QuietShrine")

	for pair in {
		"InventoryManager": inventory,
		"GameState": game_state,
		"Player": player,
		"BackToYard": back_to_yard,
		"FallenBranchBundle": fallen_branch,
		"QuietShrine": quiet_shrine,
	}.keys():
		var node: Node = {
			"InventoryManager": inventory,
			"GameState": game_state,
			"Player": player,
			"BackToYard": back_to_yard,
			"FallenBranchBundle": fallen_branch,
			"QuietShrine": quiet_shrine,
		}[pair]
		_expect(node != null, "ForestEdge missing node: %s" % pair)
		if _has_failed:
			return

	_expect(String(back_to_yard.get("target_scene")) == YARD_PATH, "BackToYard should target PlayerYard")
	fallen_branch.on_interact(player)
	_expect(int(inventory.get_count("wood")) >= 18, "ForestEdge should provide repair wood")
	quiet_shrine.on_interact(player)
	_expect(bool(game_state.get_flag("visited_forest_edge", false)), "ForestEdge discovery should set visited_forest_edge")

	forest.queue_free()
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
			_fail("Main flow playable validation timed out")
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
