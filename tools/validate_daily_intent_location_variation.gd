extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const DATA_REGISTRY_PATH := "res://game/autoload/DataRegistry.gd"
const DIALOGUE_MANAGER_PATH := "res://game/autoload/DialogueManager.gd"
const RELATIONSHIP_MANAGER_PATH := "res://game/autoload/RelationshipManager.gd"
const GAME_STATE_PATH := "res://game/autoload/GameState.gd"
const TIME_MANAGER_PATH := "res://game/autoload/TimeManager.gd"
const NPC_SCENE_PATH := "res://game/entities/npc/NPC.tscn"
const DIALOGUE_BOX_PATH := "res://game/scenes/ui/DialogueBox.tscn"
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: daily intent location variation initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var registry := _new_node(DATA_REGISTRY_PATH)
	var dialogue_manager := _new_node(DIALOGUE_MANAGER_PATH)
	var relationship_manager := _new_node(RELATIONSHIP_MANAGER_PATH)
	var game_state := _new_node(GAME_STATE_PATH)
	var time_manager := _new_node(TIME_MANAGER_PATH)
	if _has_failed:
		return

	root.add_child(registry)
	root.add_child(dialogue_manager)
	root.add_child(relationship_manager)
	root.add_child(game_state)
	root.add_child(time_manager)
	registry.load_all_data()
	registry.validate_all_data()
	dialogue_manager.bind_registry(registry)
	dialogue_manager.bind_relationship_manager(relationship_manager)

	_validate_dialogue_manager_scene_id_conditions(dialogue_manager)
	if _has_failed:
		return
	await _validate_npc_context_reads_active_region(registry, dialogue_manager, relationship_manager, game_state, time_manager)
	if _has_failed:
		return
	await _validate_main_village_uses_location_specific_reply()
	if _has_failed:
		return

	print("OK: daily intent location variation runtime validation passed")
	_finish_deferred(0)


func _validate_dialogue_manager_scene_id_conditions(dialogue_manager: Node) -> void:
	var village_context := _base_context("check_village_notice", "village")
	var village_dialogue: Dictionary = dialogue_manager.get_daily_intent_dialogue("mika", village_context)
	_expect(String(village_dialogue.get("dialogue_id", "")) == "mika_daily_intent_village_notice_village_01", "Village context should select Mika's location-specific notice reply")

	var generic_context := _base_context("check_village_notice", "")
	var generic_dialogue: Dictionary = dialogue_manager.get_daily_intent_dialogue("mika", generic_context)
	_expect(String(generic_dialogue.get("dialogue_id", "")) == "mika_daily_intent_village_notice_01", "No scene context should keep Mika's generic notice reply")


func _validate_npc_context_reads_active_region(
	registry: Node,
	dialogue_manager: Node,
	relationship_manager: Node,
	game_state: Node,
	time_manager: Node
) -> void:
	var region_root := _FakeOutdoorRegion.new()
	region_root.name = "FakeOutdoorWorld"
	var npc := _instantiate_npc("mika", registry)
	var dialogue_box := _instantiate_dialogue_box()
	if _has_failed:
		return
	root.add_child(region_root)
	region_root.add_child(dialogue_box)
	region_root.add_child(npc)
	_bind_npc_paths(npc, registry, dialogue_manager, relationship_manager, game_state, time_manager)
	npc.dialogue_box_path = npc.get_path_to(dialogue_box)
	game_state.set_daily_intent("day_1", "check_village_notice")

	npc.on_interact(null)
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(String(dialogue.get("dialogue_id", "")) == "mika_daily_intent_village_notice_village_01", "NPC context should read active region from an OutdoorWorld ancestor")


func _validate_main_village_uses_location_specific_reply() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load for location-aware NPC follow-up")
	if _has_failed:
		return
	var main: Node = main_scene.instantiate()
	root.add_child(main)
	await _settle()

	var selected_intent := await _select_daily_intent(main, "check_village_notice")
	if not selected_intent:
		return
	main.change_scene("village", "village_default", true)
	await _settle()
	var outdoor: Node = main.get_current_gameplay_scene()
	var mika: Node = outdoor.get_node_or_null("NPCs/Mika") if outdoor != null else null
	var player: Node = outdoor.get_node_or_null("Player") if outdoor != null else null
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox") if outdoor != null else null
	_expect(outdoor != null and mika != null and player != null and dialogue_box != null, "Village should expose Mika, player, and DialogueBox")
	if _has_failed:
		return
	_expect(String(outdoor.call("get_active_region_id")) == "village", "OutdoorWorld should expose active village region")
	mika.on_interact(player)
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(String(dialogue.get("dialogue_id", "")) == "mika_daily_intent_village_notice_village_01", "Main Village interaction should use location-specific Mika reply")
	_expect(dialogue.get("sets_flags", []).is_empty(), "Location-aware daily intent reply should not set flags or rewards")


func _base_context(intent_id: String, scene_id: String) -> Dictionary:
	return {
		"season": "spring",
		"weather": "sunny",
		"time_block": "morning",
		"flags": {},
		"daily_intent": intent_id,
		"scene_id": scene_id,
	}


func _select_daily_intent(main: Node, intent_id: String) -> bool:
	var house: Node = main.get_current_gameplay_scene()
	var planner: Node = house.get_node_or_null("IntentDesk") if house != null else null
	var player: Node = house.get_node_or_null("Player") if house != null else null
	var panel: Node = house.get_node_or_null("DailyIntentPanel") if house != null else null
	var dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	if not _expect_bool(planner != null and player != null and panel != null and dialogue_box != null, "missing daily intent selection nodes"):
		return false
	planner.on_interact(player)
	await _settle()
	if not bool(panel.select_intent(intent_id)):
		_fail("could not select daily intent %s" % intent_id)
		return false
	await _settle()
	if dialogue_box.has_method("close"):
		dialogue_box.close()
	return true


class _FakeOutdoorRegion:
	extends Node2D
	func get_active_region_id() -> String:
		return "village"


func _instantiate_npc(npc_id: String, registry: Node) -> Node:
	var npc_scene := load(NPC_SCENE_PATH) as PackedScene
	if npc_scene == null:
		_fail("could not load NPC scene")
		return null
	var npc := npc_scene.instantiate()
	if npc == null:
		_fail("could not instantiate NPC scene")
		return null
	npc.npc_id = npc_id
	npc.configure_from_data(registry.get_npc(npc_id))
	return npc


func _bind_npc_paths(
	npc: Node,
	registry: Node,
	dialogue_manager: Node,
	relationship_manager: Node,
	game_state: Node,
	time_manager: Node
) -> void:
	npc.data_registry_path = npc.get_path_to(registry)
	npc.dialogue_manager_path = npc.get_path_to(dialogue_manager)
	npc.relationship_manager_path = npc.get_path_to(relationship_manager)
	npc.game_state_path = npc.get_path_to(game_state)
	npc.time_manager_path = npc.get_path_to(time_manager)


func _instantiate_dialogue_box() -> Node:
	var dialogue_box_scene := load(DIALOGUE_BOX_PATH) as PackedScene
	if dialogue_box_scene == null:
		_fail("could not load DialogueBox scene")
		return null
	var dialogue_box := dialogue_box_scene.instantiate()
	if dialogue_box == null:
		_fail("could not instantiate DialogueBox scene")
	return dialogue_box


func _new_node(script_path: String) -> Node:
	var script_resource: Script = load(script_path) as Script
	if script_resource == null:
		_fail("could not load %s" % script_path)
		return null
	var node := script_resource.new() as Node
	if node == null:
		_fail("%s did not instantiate as Node" % script_path)
	return node


func _settle() -> void:
	await create_timer(0.1).timeout
	await process_frame
	await process_frame


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _expect_bool(condition: bool, message: String) -> bool:
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
			_fail("Daily intent location variation validation timed out")
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
