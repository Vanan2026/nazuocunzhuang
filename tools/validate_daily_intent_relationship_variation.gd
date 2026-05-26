extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const DATA_REGISTRY_PATH := "res://game/autoload/DataRegistry.gd"
const DIALOGUE_MANAGER_PATH := "res://game/autoload/DialogueManager.gd"
const RELATIONSHIP_MANAGER_PATH := "res://game/autoload/RelationshipManager.gd"
const GAME_STATE_PATH := "res://game/autoload/GameState.gd"
const TIME_MANAGER_PATH := "res://game/autoload/TimeManager.gd"
const NPC_SCENE_PATH := "res://game/entities/npc/NPC.tscn"
const DIALOGUE_BOX_PATH := "res://game/scenes/ui/DialogueBox.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: daily intent relationship variation initialize")
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

	_validate_close_neighbor_dialogue(dialogue_manager, relationship_manager)
	if _has_failed:
		return
	_validate_generic_relationship_does_not_hide_daily_intent(dialogue_manager, relationship_manager)
	if _has_failed:
		return
	await _validate_npc_interaction_uses_intent_specific_dialogue(registry, dialogue_manager, relationship_manager, game_state, time_manager)
	if _has_failed:
		return

	print("OK: daily intent relationship variation runtime validation passed")
	_finish_deferred(0)


func _validate_close_neighbor_dialogue(dialogue_manager: Node, relationship_manager: Node) -> void:
	_expect(dialogue_manager.has_method("get_daily_intent_dialogue"), "DialogueManager should expose daily-intent-specific selection")
	if _has_failed:
		return
	var context := _base_context("visit_neighbor")
	var early_dialogue: Dictionary = dialogue_manager.get_daily_intent_dialogue("hana", context)
	_expect(String(early_dialogue.get("dialogue_id", "")) == "hana_daily_intent_visit_neighbor_01", "Low relationship Hana should use the first visit-neighbor daily intent line")
	relationship_manager.add_relationship("hana", 3)
	var close_dialogue: Dictionary = dialogue_manager.get_daily_intent_dialogue("hana", context)
	_expect(String(close_dialogue.get("dialogue_id", "")) == "hana_daily_intent_visit_neighbor_close_01", "Close Hana should use the warmer visit-neighbor daily intent line")
	_expect(close_dialogue.get("sets_flags", []).is_empty(), "Close daily intent line should not set flags or rewards")


func _validate_generic_relationship_does_not_hide_daily_intent(dialogue_manager: Node, relationship_manager: Node) -> void:
	relationship_manager.add_relationship("gen", 3)
	var context := _base_context("gather_repair_material")
	var generic_dialogue: Dictionary = dialogue_manager.get_dialogue("gen", context)
	_expect(String(generic_dialogue.get("dialogue_id", "")) == "gen_relationship_01", "Baseline generic relationship dialogue should still exist")
	var intent_dialogue: Dictionary = dialogue_manager.get_daily_intent_dialogue("gen", context)
	_expect(String(intent_dialogue.get("dialogue_id", "")) == "gen_daily_intent_repair_material_01", "Selected daily intent should not be hidden by generic relationship dialogue")


func _validate_npc_interaction_uses_intent_specific_dialogue(
	registry: Node,
	dialogue_manager: Node,
	relationship_manager: Node,
	game_state: Node,
	time_manager: Node
) -> void:
	var npc := _instantiate_npc("gen", registry)
	var dialogue_box := _instantiate_dialogue_box()
	if _has_failed:
		return
	root.add_child(dialogue_box)
	root.add_child(npc)
	_bind_npc_paths(npc, registry, dialogue_manager, relationship_manager, game_state, time_manager)
	npc.dialogue_box_path = npc.get_path_to(dialogue_box)

	relationship_manager.add_relationship("gen", 3)
	game_state.set_daily_intent("day_1", "gather_repair_material")
	var flags_before: Dictionary = game_state.get_save_data().get("flags", {}).duplicate(true)
	npc.on_interact(null)
	await _settle()
	var dialogue: Dictionary = dialogue_box.get("dialogue")
	_expect(String(dialogue.get("dialogue_id", "")) == "gen_daily_intent_repair_material_01", "NPC interaction should prefer selected daily intent over generic relationship line")
	_expect(game_state.get_save_data().get("flags", {}) == flags_before, "Relationship-aware daily intent interaction should not add quest or reward flags")


func _base_context(intent_id: String) -> Dictionary:
	return {
		"season": "spring",
		"weather": "sunny",
		"time_block": "morning",
		"flags": {},
		"daily_intent": intent_id,
	}


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
			_fail("Daily intent relationship variation validation timed out")
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
