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
	var aoi = yard.get_node_or_null("NPCs/Aoi")
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
		"Aoi": aoi,
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
	var farm_plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot0")
	var yard_inventory_for_farm: Node = yard.get_node_or_null("InventoryManager")
	_expect(farm_plot != null, "PlayerYard should include FarmPlot0 for first-week farming step")
	_expect(yard_inventory_for_farm != null, "PlayerYard should include InventoryManager for first-week farming step")
	if _has_failed:
		return
	if yard_inventory_for_farm.has_method("set_selected_item"):
		yard_inventory_for_farm.set_selected_item("seed_turnip")
	_expect(farm_plot.till(), "First-week FarmPlot0 should till after old well repair")
	_expect(farm_plot.plant_seed("seed_turnip"), "First-week FarmPlot0 should plant after old well repair")
	_expect(farm_plot.water(), "First-week FarmPlot0 should water after old well repair")
	for _day in range(2):
		farm_plot.advance_day(false)
		if String(farm_plot.get_state_name()) != "ready":
			_expect(farm_plot.water(), "First-week FarmPlot0 should stay waterable until harvest")
	if _has_failed:
		return
	_expect(String(farm_plot.get_state_name()) == "ready", "First-week FarmPlot0 should mature before yard repairs continue")
	_expect(farm_plot.harvest(), "First-week FarmPlot0 should harvest before yard repairs continue")
	await process_frame
	_expect(int(yard_inventory_for_farm.get_count("crop_turnip")) >= 1, "First harvest should add a turnip before Aoi share")
	_expect(yard_inventory_for_farm.set_selected_item("crop_turnip"), "First harvested turnip should be selectable for Aoi share")
	aoi.on_interact(player)
	await process_frame
	main.sync_current_scene_state()
	_expect(bool(shared_game_state.get_flag("shared_first_turnip_day1", false)), "Aoi share should persist before yard repairs continue")
	if _has_failed:
		return
	var strawberry_plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot1")
	_expect(strawberry_plot != null, "PlayerYard should include FarmPlot1 for Aoi strawberry follow-up")
	if _has_failed:
		return
	_expect(int(yard_inventory_for_farm.get_count("seed_strawberry")) >= 1, "Aoi share should grant a strawberry seed before the second plot follow-up")
	_expect(yard_inventory_for_farm.set_selected_item("seed_strawberry"), "Aoi strawberry seed should be selectable")
	_expect(strawberry_plot.till(), "FarmPlot1 should till for Aoi strawberry follow-up")
	_expect(strawberry_plot.plant_seed("seed_strawberry"), "FarmPlot1 should plant Aoi strawberry seed")
	_expect(strawberry_plot.water(), "FarmPlot1 should water Aoi strawberry seed")
	await process_frame
	main.sync_current_scene_state()
	_expect(bool(shared_game_state.get_flag("planted_aoi_strawberry_day1", false)), "Aoi strawberry planting should persist before yard repairs continue")
	if _has_failed:
		return
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
	_expect(not bool(shared_quests.is_first_week_complete()), "First-week quest should wait for the Village notice bridge after ForestEdge discovery")
	_expect(String(shared_quests.get_current_first_week_objective_id()) == "read_village_notice_day1", "Village notice should be the final light first-week bridge")
	if _has_failed:
		return

	back_to_yard.on_interact(forest.get_node_or_null("Player"))
	await _settle_route()
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "BackToYard should route back to player_yard")
	yard = main.get_current_gameplay_scene()
	_expect(_player_is_at_spawn(yard, "from_forest_edge"), "Player should land at yard spawn from_forest_edge")
	var yard_inventory = yard.get_node_or_null("InventoryManager")
	_expect(yard_inventory != null and int(yard_inventory.get_count("wood")) >= 18, "Returned yard should receive shared inventory")
	if _has_failed:
		return

	main.change_scene("village", "village_default")
	await _settle_route()
	var outdoor_village: Node = main.get_current_gameplay_scene()
	_expect(outdoor_village != null and outdoor_village.has_method("get_active_region_id"), "Village bridge should keep using OutdoorWorld")
	_expect(String(main.get_current_gameplay_scene_id()) == "village", "Main should expose village scene id for the bridge")
	_expect(String(outdoor_village.call("get_active_region_id")) == "village", "OutdoorWorld should activate village for the bridge")
	if _has_failed:
		return
	var village_section: Node = outdoor_village.get_node_or_null("Village")
	var village_notice: Node = null
	var village_return: Node = null
	if village_section != null:
		village_notice = village_section.get_node_or_null("VillageNotice")
		village_return = village_section.get_node_or_null("VillageReturnPath")
	_expect(village_notice != null, "Village should include VillageNotice for first-week bridge")
	_expect(village_return != null, "Village should include VillageReturnPath after the bridge")
	if _has_failed:
		return
	village_notice.on_interact(outdoor_village.get_node_or_null("Player"))
	await _settle_route()
	main.sync_current_scene_state()
	await process_frame
	shared_quests.update_first_week_progress(shared_game_state, main.get_node_or_null("SceneRouter"))
	_expect(bool(shared_game_state.get_flag("read_village_notice_day1", false)), "VillageNotice should persist the first-week bridge flag")
	_expect(bool(shared_quests.is_first_week_complete()), "First-week quest should complete after reading the Village notice")
	if _has_failed:
		return
	village_return.on_interact(outdoor_village.get_node_or_null("Player"))
	await _settle_route()
	_expect(String(main.get_current_gameplay_scene_id()) == "player_yard", "VillageReturnPath should route back to player_yard")
	yard = main.get_current_gameplay_scene()
	_expect(_player_is_at_spawn(yard, "from_house"), "Player should land at yard spawn from_house after returning from Village")

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
