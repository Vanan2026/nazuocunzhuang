extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const TEST_SAVE_PATH := "user://persistent_main_flow_test.json"
const WATCHDOG_TIMEOUT_SECONDS := 35.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: persistent main flow initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	_remove_test_save()
	var main_scene = load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main = main_scene.instantiate()
	root.add_child(main)
	await process_frame
	await process_frame

	_expect(main.has_method("get_current_gameplay_scene_id"), "Main should expose current scene id")
	_expect(main.has_method("get_current_gameplay_scene"), "Main should expose current gameplay scene")
	_expect(main.has_method("sync_current_scene_state"), "Main should sync current scene state")
	_expect(main.has_method("apply_shared_state_to_current_scene"), "Main should apply shared state to current scene")
	_expect(main.has_method("build_main_flow_save_data"), "Main should build main-flow save data")
	_expect(main.get_node_or_null("SceneRouter") != null, "Main should own SceneRouter")
	_expect(main.get_node_or_null("QuestManager") != null, "Main should own QuestManager")
	_expect(main.get_node_or_null("InventoryManager") != null, "Main should own persistent InventoryManager")
	_expect(main.get_node_or_null("GameState") != null, "Main should own persistent GameState")
	if _has_failed:
		return

	_expect(String(main.get_current_gameplay_scene_id()) == "player_house", "Main should start at player_house")
	var house = main.get_current_gameplay_scene()
	_expect(house != null and house.name == "PlayerHouse", "Main should instantiate PlayerHouse")
	var house_door = house.get_node_or_null("DoorToYard")
	_expect(house_door != null, "PlayerHouse should include DoorToYard")
	_expect(String(house_door.get("target_scene_id")) == "player_yard", "DoorToYard should route by scene id")
	_expect(String(house_door.get("target_spawn_id")) == "from_house", "DoorToYard should target yard spawn")
	if _has_failed:
		return

	house_door.on_interact(house.get_node_or_null("Player"))
	await _settle_route()
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "DoorToYard should route to player_yard")
	var yard = main.get_current_gameplay_scene()
	_expect(yard != null and yard.name == "PlayerYard", "Main should instantiate PlayerYard")
	_expect(_player_is_at_spawn(yard, "from_house"), "Player should land at yard spawn from_house")
	if _has_failed:
		return

	var shared_inventory = main.get_node("InventoryManager")
	var shared_game_state = main.get_node("GameState")
	var shared_time = main.get_node("TimeManager")
	var shared_quests = main.get_node("QuestManager")
	var shared_save = main.get_node("SaveManager")

	shared_time.hour = 14
	shared_time.minute = 0
	shared_time.call("_update_time_block", false)
	main.apply_shared_state_to_current_scene()
	await process_frame

	var player = yard.get_node_or_null("Player")
	var mailbox = yard.get_node_or_null("Mailbox")
	var bulletin = yard.get_node_or_null("BulletinBoard")
	var wood_pile = yard.get_node_or_null("WoodPile")
	var stone_pile = yard.get_node_or_null("StonePile")
	var old_well = yard.get_node_or_null("OldWell")
	var garden_bench = yard.get_node_or_null("GardenBenchRepair")
	var village_sign = yard.get_node_or_null("VillageSignRepair")
	var forest_gate = yard.get_node_or_null("ForestTrailGate")
	var required_yard_nodes = {
		"Player": player,
		"Mailbox": mailbox,
		"BulletinBoard": bulletin,
		"WoodPile": wood_pile,
		"StonePile": stone_pile,
		"OldWell": old_well,
		"GardenBenchRepair": garden_bench,
		"VillageSignRepair": village_sign,
		"ForestTrailGate": forest_gate,
	}
	for pair in required_yard_nodes.keys():
		var node: Node = required_yard_nodes[pair]
		_expect(node != null, "PlayerYard missing node: %s" % pair)
		if _has_failed:
			return

	mailbox.on_interact(player)
	await process_frame
	bulletin.on_interact(player)
	await process_frame
	wood_pile.on_interact(player)
	stone_pile.on_interact(player)
	shared_game_state.set_player_money(500)
	main.apply_shared_state_to_current_scene()
	await process_frame
	old_well.on_interact(player)
	await process_frame
	garden_bench.on_interact(player)
	await process_frame
	village_sign.on_interact(player)
	await process_frame
	bulletin.on_interact(player)
	await process_frame
	main.sync_current_scene_state()
	await process_frame

	_expect(shared_game_state.is_restored("old_well"), "Shared GameState should keep old well restored")
	_expect(shared_game_state.is_restored("garden_bench"), "Shared GameState should keep garden bench restored")
	_expect(shared_game_state.is_restored("village_sign"), "Shared GameState should keep village sign restored")
	_expect(bool(shared_game_state.get_flag("read_mailbox_day1", false)), "Mailbox should set first-week read flag")
	_expect(bool(shared_game_state.get_flag("read_bulletin_day1", false)), "Bulletin should set first-week read flag")
	_expect(bool(shared_game_state.get_flag("heard_forest_edge_notice", false)), "Bulletin should set forest notice flag after sign repair")
	_expect(shared_quests.has_method("get_first_week_progress"), "QuestManager should expose first-week progress")
	_expect(int(shared_quests.get_first_week_progress().get("completed_count", 0)) >= 6, "First-week quest should progress through yard repairs")
	if _has_failed:
		return

	forest_gate.on_interact(player)
	await _settle_route()
	_expect(String(main.get_current_gameplay_scene_id()) == "forest_edge", "ForestTrailGate should route to forest_edge")
	var forest = main.get_current_gameplay_scene()
	_expect(forest != null and forest.name == "ForestEdge", "Main should instantiate ForestEdge")
	_expect(_player_is_at_spawn(forest, "from_yard"), "Player should land at ForestEdge spawn from_yard")
	if _has_failed:
		return

	var schedule_director = forest.get_node_or_null("ScheduleDirector")
	var mika = forest.get_node_or_null("NPCs/Mika")
	var quiet_shrine = forest.get_node_or_null("QuietShrine")
	var fallen_branch = forest.get_node_or_null("FallenBranchBundle")
	var back_to_yard = forest.get_node_or_null("BackToYard")
	_expect(schedule_director != null, "ForestEdge should include ScheduleDirector")
	_expect(mika != null, "ForestEdge should include Mika")
	_expect(quiet_shrine != null, "ForestEdge should include QuietShrine")
	_expect(fallen_branch != null, "ForestEdge should include FallenBranchBundle")
	_expect(back_to_yard != null, "ForestEdge should include BackToYard")
	if _has_failed:
		return

	schedule_director.apply_schedule("afternoon")
	var mika_assignment: Dictionary = schedule_director.get_current_assignment("mika")
	_expect(String(mika_assignment.get("scene_id", "")) == "forest_edge", "Mika should have afternoon ForestEdge assignment")
	_expect(bool(mika.visible), "Mika should be visible at ForestEdge in afternoon")
	quiet_shrine.on_interact(forest.get_node_or_null("Player"))
	await process_frame
	mika.on_interact(forest.get_node_or_null("Player"))
	await process_frame
	fallen_branch.on_interact(forest.get_node_or_null("Player"))
	await process_frame
	main.sync_current_scene_state()
	await process_frame
	_expect(bool(shared_game_state.get_flag("visited_forest_edge", false)), "ForestEdge shrine should persist visited_forest_edge")
	_expect(bool(shared_game_state.get_flag("heard_npc_forest_edge", false)), "Mika should persist NPC forest rumor flag")
	_expect(int(shared_inventory.get_count("wood")) >= 18, "ForestEdge wood pickup should persist to shared inventory")
	_expect(bool(shared_quests.is_first_week_complete()), "First-week quest should complete after ForestEdge discovery")
	if _has_failed:
		return

	back_to_yard.on_interact(forest.get_node_or_null("Player"))
	await _settle_route()
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "BackToYard should route back to player_yard")
	yard = main.get_current_gameplay_scene()
	_expect(_player_is_at_spawn(yard, "from_forest_edge"), "Player should land at yard spawn from_forest_edge")
	var yard_inventory = yard.get_node_or_null("InventoryManager")
	_expect(yard_inventory != null and int(yard_inventory.get_count("wood")) >= 18, "Returned yard should receive shared inventory")

	var save_data: Dictionary = main.build_main_flow_save_data()
	_expect(save_data.has("scene"), "Main-flow save data should include scene")
	_expect(save_data.has("quests"), "Main-flow save data should include quests")
	_expect(String(save_data.get("scene", {}).get("current_scene_id", "")) == "player_yard", "Save data should keep current scene id")
	_expect(bool(save_data.get("quests", {}).get("first_week_restore_path", {}).get("completed", false)), "Save data should keep first-week completion")
	_expect(bool(shared_save.save_game(main, TEST_SAVE_PATH)), "Persistent main flow should save through Main")
	shared_game_state.flags.clear()
	shared_quests.quest_states.clear()
	_expect(bool(shared_save.load_game(main, TEST_SAVE_PATH)), "Persistent main flow should load through Main")
	_expect(bool(shared_quests.is_first_week_complete()), "Loaded main flow should restore first-week completion")

	_remove_test_save()
	print("OK: persistent main flow runtime validation passed")
	_finish_deferred(0)


func _settle_route() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _player_is_at_spawn(scene: Node, spawn_id: String) -> bool:
	if scene == null:
		return false
	var player = scene.get_node_or_null("Player") as Node2D
	var spawn = _find_spawn(scene, spawn_id)
	return player != null and spawn != null and player.position.distance_to(spawn.position) <= 1.0


func _find_spawn(node: Node, spawn_id: String) -> Node2D:
	if node == null:
		return null
	if node.has_method("get_spawn_id") and String(node.call("get_spawn_id")) == spawn_id and node is Node2D:
		return node as Node2D
	for child in node.get_children():
		var found = _find_spawn(child, spawn_id)
		if found != null:
			return found
	return null


func _remove_test_save() -> void:
	if FileAccess.file_exists(TEST_SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE_PATH))


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	_remove_test_save()
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
			_fail("Persistent main flow validation timed out")
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
