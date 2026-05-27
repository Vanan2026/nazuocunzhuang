extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")

const DATA_REGISTRY_PATH := "res://game/autoload/DataRegistry.gd"
const INVENTORY_MANAGER_PATH := "res://game/autoload/InventoryManager.gd"
const RELATIONSHIP_MANAGER_PATH := "res://game/autoload/RelationshipManager.gd"
const DIALOGUE_MANAGER_PATH := "res://game/autoload/DialogueManager.gd"
const TIME_MANAGER_PATH := "res://game/autoload/TimeManager.gd"
const NPC_SCENE_PATH := "res://game/entities/npc/NPC.tscn"
const DIALOGUE_SCREEN_PATH := "res://game/scenes/ui/DialogueScreen.tscn"
const PAPER_PANEL_TEXTURE_PATH := "res://assets/ui/panels/ui_panel_paper_01.png"
const WATCHDOG_TIMEOUT_SECONDS := 15.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Greenfield P0 Dialogue + Gift runtime initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var registry := _new_node(DATA_REGISTRY_PATH) as Node
	var inventory_manager := _new_node(INVENTORY_MANAGER_PATH) as Node
	var relationship_manager := _new_node(RELATIONSHIP_MANAGER_PATH) as Node
	var dialogue_manager := _new_node(DIALOGUE_MANAGER_PATH) as Node
	var time_manager := _new_node(TIME_MANAGER_PATH) as Node
	root.add_child(registry)
	root.add_child(inventory_manager)
	root.add_child(relationship_manager)
	root.add_child(dialogue_manager)
	root.add_child(time_manager)
	_expect(registry.load_all_data(), "DataRegistry should load gifts data")
	_expect(registry.validate_all_data(), "DataRegistry should validate gifts data")
	dialogue_manager.bind_registry(registry)
	dialogue_manager.bind_relationship_manager(relationship_manager)
	if _has_failed:
		return

	inventory_manager.add_item("food_persimmon_riceball", 1)
	inventory_manager.add_item("food_warm_tea", 1)
	inventory_manager.add_item("wildflower_spring", 1)

	var dialogue_screen := _instantiate_dialogue_screen()
	if _has_failed:
		return
	root.add_child(dialogue_screen)
	dialogue_screen.call("bind_managers", inventory_manager, registry, relationship_manager)
	await _settle()

	_validate_structure(dialogue_screen)
	if _has_failed:
		return
	await _validate_gift_selection(dialogue_screen)
	if _has_failed:
		return
	await _validate_relationship_feedback(dialogue_screen, registry)
	if _has_failed:
		return
	await _validate_npc_uses_gifts_data(registry, inventory_manager, relationship_manager, dialogue_manager, dialogue_screen, time_manager)
	if _has_failed:
		return

	print("OK: Greenfield P0 Dialogue + Gift runtime validation passed")
	_finish_deferred(0)


func _validate_structure(dialogue_screen: Node) -> void:
	_expect(dialogue_screen.visible == false, "DialogueScreen should be hidden by default")
	var panel := dialogue_screen.get_node_or_null("Panel") as PanelContainer
	var portrait := dialogue_screen.get_node_or_null("Panel/Content/Portrait") as TextureRect
	var option_row := dialogue_screen.get_node_or_null("Panel/Content/TextColumn/OptionRow") as HBoxContainer
	var gift_selection := dialogue_screen.get_node_or_null("GiftSelection") as PanelContainer
	var gift_grid := dialogue_screen.get_node_or_null("GiftSelection/Content/GiftGrid") as GridContainer
	var feedback := dialogue_screen.get_node_or_null("RelationshipFeedback") as PanelContainer
	_expect(panel != null, "DialogueScreen should include dialogue panel")
	_expect(portrait != null, "DialogueScreen should include portrait texture")
	_expect(option_row != null and option_row.get_child_count() >= 3, "DialogueScreen should include talk/gift/close options")
	_expect(gift_selection != null, "DialogueScreen should include GiftSelection panel")
	_expect(gift_grid != null, "DialogueScreen should include GiftGrid")
	_expect(feedback != null, "DialogueScreen should include RelationshipFeedback panel")
	if _has_failed:
		return
	_expect(_stylebox_texture_path(panel.get_theme_stylebox("panel")) == PAPER_PANEL_TEXTURE_PATH, "DialogueScreen panel should use paper texture")
	_expect(gift_selection.visible == false, "GiftSelection should start hidden")
	_expect(feedback.visible == false, "RelationshipFeedback should start hidden")


func _validate_gift_selection(dialogue_screen: Node) -> void:
	dialogue_screen.call("show_gift_selection", {})
	await _settle()
	var gift_selection := dialogue_screen.get_node("GiftSelection") as PanelContainer
	var gift_grid := dialogue_screen.get_node("GiftSelection/Content/GiftGrid") as GridContainer
	_expect(gift_selection.visible, "show_gift_selection should reveal GiftSelection")
	_expect(gift_grid.get_child_count() >= 3, "GiftSelection should build available gift buttons from inventory")
	if _has_failed:
		return
	var found_icon := false
	for child in gift_grid.get_children():
		var button := child as Button
		if button != null and button.icon != null:
			found_icon = true
			break
	_expect(found_icon, "GiftSelection buttons should load item icons")
	dialogue_screen.call("hide_gift_selection")
	await _settle()
	_expect(not gift_selection.visible, "hide_gift_selection should hide GiftSelection")


func _validate_relationship_feedback(dialogue_screen: Node, registry: Node) -> void:
	var gift_rule: Dictionary = registry.get_gift_response("aoi", "food_persimmon_riceball")
	var dialogue := {
		"dialogue_id": "p0_dialogue_gift_runtime",
		"npc_id": "aoi",
		"type": "event",
		"priority": 99,
		"conditions": {},
		"lines": [{"speaker": "aoi", "text": "Thank you for thinking of me."}],
		"sets_flags": [],
		"context": {"gift_context": {
			"item_id": "food_persimmon_riceball",
			"item_name": "Persimmon riceball",
			"delta": int(gift_rule.get("relationship_delta", 0)),
			"feedback_text": String(gift_rule.get("feedback_text", "")),
			"already_gifted": false,
		}},
	}
	dialogue_screen.call("show_dialogue", dialogue, {
		"npc_name": "Aoi",
		"portrait": String(registry.get_npc("aoi").get("portrait", "")),
	})
	await _settle()
	var feedback := dialogue_screen.get_node("RelationshipFeedback") as PanelContainer
	var feedback_line := dialogue_screen.get_node("RelationshipFeedback/Content/FeedbackLineLabel") as Label
	var feedback_delta := dialogue_screen.get_node("RelationshipFeedback/Content/FeedbackDeltaLabel") as Label
	var portrait := dialogue_screen.get_node("Panel/Content/Portrait") as TextureRect
	_expect(dialogue_screen.visible, "show_dialogue should reveal DialogueScreen")
	_expect(feedback.visible, "gift dialogue should reveal RelationshipFeedback")
	_expect(feedback_line.text.contains("sweet riceball"), "RelationshipFeedback should use gifts.json feedback text")
	_expect(feedback_delta.text.contains("+2"), "RelationshipFeedback should show gifts.json relationship delta")
	_expect(portrait.texture != null, "DialogueScreen should load NPC portrait")


func _validate_npc_uses_gifts_data(
	registry: Node,
	inventory_manager: Node,
	relationship_manager: Node,
	dialogue_manager: Node,
	dialogue_screen: Node,
	time_manager: Node,
) -> void:
	inventory_manager.set_selected_item("food_persimmon_riceball")
	var npc_scene := load(NPC_SCENE_PATH) as PackedScene
	_expect(npc_scene != null, "NPC scene should load")
	if _has_failed:
		return
	var npc := npc_scene.instantiate() as Node
	root.add_child(npc)
	npc.npc_id = "aoi"
	npc.configure_from_data(registry.get_npc("aoi"))
	npc.inventory_manager_path = npc.get_path_to(inventory_manager)
	npc.data_registry_path = npc.get_path_to(registry)
	npc.dialogue_manager_path = npc.get_path_to(dialogue_manager)
	npc.relationship_manager_path = npc.get_path_to(relationship_manager)
	npc.dialogue_box_path = npc.get_path_to(dialogue_screen)
	npc.time_manager_path = npc.get_path_to(time_manager)
	var before_relationship := int(relationship_manager.get_relationship("aoi"))
	npc.on_interact(null)
	await _settle()
	_expect(int(relationship_manager.get_relationship("aoi")) == before_relationship + 2, "NPC gift should apply gifts.json relationship delta")
	_expect(int(inventory_manager.get_count("food_persimmon_riceball")) == 0, "NPC gift should consume the selected item")
	var feedback := dialogue_screen.get_node("RelationshipFeedback") as PanelContainer
	_expect(feedback.visible, "NPC gift should show RelationshipFeedback through DialogueScreen")


func _instantiate_dialogue_screen() -> Node:
	var scene := load(DIALOGUE_SCREEN_PATH) as PackedScene
	_expect(scene != null, "DialogueScreen scene should load")
	if scene == null:
		return null
	return scene.instantiate()


func _new_node(script_path: String) -> Node:
	var script_resource := load(script_path) as Script
	_expect(script_resource != null, "%s should load" % script_path)
	if script_resource == null:
		return null
	var node := script_resource.new() as Node
	_expect(node != null, "%s should instantiate as Node" % script_path)
	return node


func _stylebox_texture_path(stylebox: StyleBox) -> String:
	var texture_box := stylebox as StyleBoxTexture
	if texture_box == null or texture_box.texture == null:
		return ""
	return String(texture_box.texture.resource_path)


func _settle() -> void:
	await create_timer(0.05).timeout
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
			_fail("Greenfield P0 Dialogue + Gift validation timed out")
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
