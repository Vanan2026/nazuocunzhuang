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
	print("PROGRESS: daily intent NPC follow-up initialize")
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

	_validate_dialogue_manager_daily_intent_conditions(dialogue_manager)
	if _has_failed:
		return
	await _validate_npc_context_uses_selected_daily_intent(registry, dialogue_manager, relationship_manager, game_state, time_manager)
	if _has_failed:
		return
	await _validate_intent_does_not_carry_to_next_day(registry, dialogue_manager, relationship_manager, game_state, time_manager)
	if _has_failed:
		return
	await _validate_main_scene_rumor_does_not_hide_intent()
	if _has_failed:
		return

	print("OK: daily intent NPC follow-up runtime validation passed")
	_finish_deferred(0)


func _validate_dialogue_manager_daily_intent_conditions(dialogue_manager: Node) -> void:
	var base_context := {
		"season": "spring",
		"weather": "sunny",
		"time_block": "morning",
		"flags": {},
		"daily_intent": "",
	}
	var mika_default: Dictionary = dialogue_manager.get_dialogue("mika", base_context)
	_expect(String(mika_default.get("dialogue_id", "")) == "mika_mailbox_hint_01", "Mika should keep mailbox guidance when no daily intent is selected")

	var intent_expectations := {
		"aoi": ["tend_crops", "aoi_daily_intent_tend_crops_01"],
		"mika": ["check_village_notice", "mika_daily_intent_village_notice_01"],
		"hana": ["visit_neighbor", "hana_daily_intent_visit_neighbor_01"],
		"gen": ["gather_repair_material", "gen_daily_intent_repair_material_01"],
	}
	for npc_id in intent_expectations.keys():
		var expected: Array = intent_expectations[npc_id]
		var context := base_context.duplicate(true)
		context["daily_intent"] = String(expected[0])
		var dialogue: Dictionary = dialogue_manager.get_dialogue(String(npc_id), context)
		_expect(String(dialogue.get("dialogue_id", "")) == String(expected[1]), "%s should respond to selected daily intent %s" % [npc_id, expected[0]])
		_expect(dialogue.get("sets_flags", []).is_empty(), "%s daily intent dialogue should not set flags" % npc_id)
		if _has_failed:
			return

	var event_context := base_context.duplicate(true)
	event_context["daily_intent"] = "check_village_notice"
	event_context["flags"] = {"heard_old_well_echo_after_village_clue_day1": true}
	var event_dialogue: Dictionary = dialogue_manager.get_dialogue("mika", event_context)
	_expect(String(event_dialogue.get("dialogue_id", "")) == "mika_old_well_echo_followup", "Event dialogue should still outrank daily intent barks")


func _validate_npc_context_uses_selected_daily_intent(
	registry: Node,
	dialogue_manager: Node,
	relationship_manager: Node,
	game_state: Node,
	time_manager: Node
) -> void:
	var npc := _instantiate_npc("mika", registry, dialogue_manager, relationship_manager, game_state, time_manager)
	var dialogue_box := _instantiate_dialogue_box()
	if _has_failed:
		return
	root.add_child(dialogue_box)
	root.add_child(npc)
	_bind_npc_paths(npc, registry, dialogue_manager, relationship_manager, game_state, time_manager)
	npc.dialogue_box_path = npc.get_path_to(dialogue_box)

	game_state.set_daily_intent("day_1", "check_village_notice")
	var flags_before: Dictionary = game_state.get_save_data().get("flags", {}).duplicate(true)
	npc.on_interact(null)
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(bool(dialogue_box.visible), "NPC interaction should show dialogue")
	_expect(String(dialogue.get("dialogue_id", "")) == "mika_daily_intent_village_notice_01", "NPC should use selected daily intent from GameState context")
	_expect(game_state.get_save_data().get("flags", {}) == flags_before, "Daily intent NPC follow-up should not add quest or reward flags")
	_expect(not dialogue_manager.has_flag("mika_hint_mailbox"), "Daily intent bark should not trigger mailbox hint flags")


func _validate_intent_does_not_carry_to_next_day(
	registry: Node,
	dialogue_manager: Node,
	relationship_manager: Node,
	game_state: Node,
	time_manager: Node
) -> void:
	var npc := _instantiate_npc("mika", registry, dialogue_manager, relationship_manager, game_state, time_manager)
	var dialogue_box := _instantiate_dialogue_box()
	if _has_failed:
		return
	root.add_child(dialogue_box)
	root.add_child(npc)
	_bind_npc_paths(npc, registry, dialogue_manager, relationship_manager, game_state, time_manager)
	npc.dialogue_box_path = npc.get_path_to(dialogue_box)

	game_state.set_daily_intent("day_1", "check_village_notice")
	time_manager.start_next_day()
	npc.on_interact(null)
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(String(dialogue.get("dialogue_id", "")) == "mika_mailbox_hint_01", "Yesterday's daily intent should not carry into the next day")


func _validate_main_scene_rumor_does_not_hide_intent() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load for integrated NPC follow-up")
	if _has_failed:
		return
	var main: Node = main_scene.instantiate()
	root.add_child(main)
	await _settle()

	var house: Node = main.get_current_gameplay_scene()
	var planner: Node = house.get_node_or_null("IntentDesk") if house != null else null
	var panel: Node = house.get_node_or_null("DailyIntentPanel") if house != null else null
	var player: Node = house.get_node_or_null("Player") if house != null else null
	var house_dialogue_box: Node = house.get_node_or_null("DialogueBox") if house != null else null
	_expect(planner != null and panel != null and player != null and house_dialogue_box != null, "Main PlayerHouse should expose daily intent planner nodes")
	if _has_failed:
		return
	planner.on_interact(player)
	await _settle()
	_expect(bool(panel.select_intent("check_village_notice")), "Main planner should select village notice intent")
	await _settle()
	if house_dialogue_box.has_method("close"):
		house_dialogue_box.close()

	main.change_scene("village", "village_default", true)
	await _settle()
	var outdoor: Node = main.get_current_gameplay_scene()
	var mika: Node = outdoor.get_node_or_null("NPCs/Mika") if outdoor != null else null
	var outdoor_player: Node = outdoor.get_node_or_null("Player") if outdoor != null else null
	var dialogue_box: Node = outdoor.get_node_or_null("DialogueBox") if outdoor != null else null
	_expect(mika != null and outdoor_player != null and dialogue_box != null, "Village should expose Mika, player, and DialogueBox")
	if _has_failed:
		return
	mika.on_interact(outdoor_player)
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(String(dialogue.get("dialogue_id", "")) == "mika_daily_intent_village_notice_village_01", "Daily intent NPC follow-up should use the Village-specific reply in Main scene")


func _instantiate_npc(
	npc_id: String,
	registry: Node,
	dialogue_manager: Node,
	relationship_manager: Node,
	game_state: Node,
	time_manager: Node
) -> Node:
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
			_fail("Daily intent NPC follow-up validation timed out")
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
