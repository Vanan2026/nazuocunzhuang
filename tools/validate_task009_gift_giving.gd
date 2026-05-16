extends SceneTree

const DATA_REGISTRY_PATH := "res://game/autoload/DataRegistry.gd"
const INVENTORY_MANAGER_PATH := "res://game/autoload/InventoryManager.gd"
const RELATIONSHIP_MANAGER_PATH := "res://game/autoload/RelationshipManager.gd"
const DIALOGUE_MANAGER_PATH := "res://game/autoload/DialogueManager.gd"
const TIME_MANAGER_PATH := "res://game/autoload/TimeManager.gd"
const NPC_SCENE_PATH := "res://game/entities/npc/NPC.tscn"
const DIALOGUE_BOX_PATH := "res://game/scenes/ui/DialogueBox.tscn"
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"

var _has_failed := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var registry := _new_node(DATA_REGISTRY_PATH) as Node
	var dialogue_manager := _new_node(DIALOGUE_MANAGER_PATH) as Node
	var relationship_manager := _new_node(RELATIONSHIP_MANAGER_PATH) as Node
	var inventory_manager := _new_node(INVENTORY_MANAGER_PATH) as Node
	var time_manager := _new_node(TIME_MANAGER_PATH) as Node
	var dialogue_box_scene: PackedScene = load(DIALOGUE_BOX_PATH) as PackedScene
	if dialogue_box_scene == null:
		_fail("could not load DialogueBox")
		return

	if _has_failed:
		return

	root.add_child(registry)
	root.add_child(dialogue_manager)
	root.add_child(relationship_manager)
	root.add_child(inventory_manager)
	root.add_child(time_manager)
	var dialogue_box := dialogue_box_scene.instantiate()
	root.add_child(dialogue_box)

	registry.load_all_data()
	registry.validate_all_data()
	dialogue_manager.bind_registry(registry)
	dialogue_manager.bind_relationship_manager(relationship_manager)

	# Scene-level happy path: selected gift increases relationship, consumes gift item, and does not consume again in same day.
	inventory_manager.add_item("food_persimmon_riceball", 1)
	inventory_manager.add_item("food_warm_tea", 1)
	var npc_aoi := _build_npc(
		"aoi",
		registry,
		inventory_manager,
		dialogue_manager,
		relationship_manager,
		dialogue_box,
		time_manager,
	)
	_expect(npc_aoi != null, "Aoi NPC should instantiate for gift interaction test")
	if _has_failed:
		return
	inventory_manager.set_selected_item("food_persimmon_riceball")
	var before_aoi_relationship := int(relationship_manager.get_relationship("aoi"))
	npc_aoi.on_interact(null)
	await process_frame
	var after_first_aoi := int(relationship_manager.get_relationship("aoi"))
	_expect(after_first_aoi > before_aoi_relationship, "Gifting Aoi should increase relationship")
	if _has_failed:
		return
	_expect(int(inventory_manager.get_count("food_persimmon_riceball")) == 0, "Gift should be consumed on first Aoi gift interaction")
	if _has_failed:
		return
	_expect(int(inventory_manager.get_count("food_warm_tea")) == 1, "Aoi should be marked gifted for the day after one gift")
	if _has_failed:
		return
	inventory_manager.set_selected_item("food_warm_tea")
	npc_aoi.on_interact(null)
	await process_frame
	_expect(int(relationship_manager.get_relationship("aoi")) == after_first_aoi, "Second same-day gift should not stack relationship")
	_expect(int(inventory_manager.get_count("food_warm_tea")) == 1, "Same-day second gift should not consume item")
	if _has_failed:
		return

	# Non-gift interaction should still show a normal dialogue flow when nothing selected.
	var inventory_manager_for_dialogue := _new_node(INVENTORY_MANAGER_PATH) as Node
	var relationship_manager_for_dialogue := _new_node(RELATIONSHIP_MANAGER_PATH) as Node
	var dialogue_manager_for_dialogue := _new_node(DIALOGUE_MANAGER_PATH) as Node
	var time_manager_for_dialogue := _new_node(TIME_MANAGER_PATH) as Node
	var dialogue_box_for_dialogue := dialogue_box_scene.instantiate()
	root.add_child(inventory_manager_for_dialogue)
	root.add_child(relationship_manager_for_dialogue)
	root.add_child(dialogue_manager_for_dialogue)
	root.add_child(time_manager_for_dialogue)
	root.add_child(dialogue_box_for_dialogue)
	dialogue_manager_for_dialogue.bind_registry(registry)
	dialogue_manager_for_dialogue.bind_relationship_manager(relationship_manager_for_dialogue)
	var npc_gen := _build_npc(
		"gen",
		registry,
		inventory_manager_for_dialogue,
		dialogue_manager_for_dialogue,
		relationship_manager_for_dialogue,
		dialogue_box_for_dialogue,
		time_manager_for_dialogue,
	)
	_expect(npc_gen != null, "Gen NPC should instantiate for no-gift interaction test")
	if _has_failed:
		return
	var before_gen_relationship := int(relationship_manager_for_dialogue.get_relationship("gen"))
	inventory_manager_for_dialogue.set_selected_item("")
	npc_gen.on_interact(null)
	await process_frame
	_expect(int(relationship_manager_for_dialogue.get_relationship("gen")) == before_gen_relationship + 1, "No-selected NPC interaction should still run normal dialogue path")
	_expect(bool(dialogue_box_for_dialogue.visible), "DialogueBox should be visible after normal NPC interaction")

	# Birthday gift multiplier should be detectable with Task 009 multiplier placeholder rules.
	var inventory_manager_birthday := _new_node(INVENTORY_MANAGER_PATH) as Node
	var relationship_manager_birthday := _new_node(RELATIONSHIP_MANAGER_PATH) as Node
	var dialogue_manager_birthday := _new_node(DIALOGUE_MANAGER_PATH) as Node
	var time_manager_birthday := _new_node(TIME_MANAGER_PATH) as Node
	time_manager_birthday.season_index = 0
	time_manager_birthday.day_of_season = 12
	time_manager_birthday.day = 12
	var dialogue_box_birthday := dialogue_box_scene.instantiate()
	root.add_child(inventory_manager_birthday)
	root.add_child(relationship_manager_birthday)
	root.add_child(dialogue_manager_birthday)
	root.add_child(time_manager_birthday)
	root.add_child(dialogue_box_birthday)
	dialogue_manager_birthday.bind_registry(registry)
	dialogue_manager_birthday.bind_relationship_manager(relationship_manager_birthday)
	inventory_manager_birthday.add_item("food_persimmon_riceball", 1)
	inventory_manager_birthday.set_selected_item("food_persimmon_riceball")
	var npc_aoi_birthday := _build_npc(
		"aoi",
		registry,
		inventory_manager_birthday,
		dialogue_manager_birthday,
		relationship_manager_birthday,
		dialogue_box_birthday,
		time_manager_birthday,
	)
	_expect(npc_aoi_birthday != null, "Aoi NPC should instantiate for birthday multiplier test")
	if _has_failed:
		return
	var before_birthday_relationship := int(relationship_manager_birthday.get_relationship("aoi"))
	npc_aoi_birthday.on_interact(null)
	await process_frame
	var after_birthday_relationship := int(relationship_manager_birthday.get_relationship("aoi"))
	_expect(after_birthday_relationship == before_birthday_relationship + 4, "Birthday gift should apply multiplier (placeholder x2)")
	if _has_failed:
		return

	# PlayerYard integration: scene-level NPC receives gift from scene InventoryManager.
	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	if yard_scene == null:
		_fail("could not load PlayerYard")
		return
	var yard: Node = yard_scene.instantiate()
	root.add_child(yard)
	await process_frame
	await physics_frame
	var yard_inventory := yard.get_node_or_null("InventoryManager")
	var yard_relationship := yard.get_node_or_null("RelationshipManager")
	var aoi_node := yard.get_node_or_null("NPCs/Aoi")
	var yard_dialogue_box := yard.get_node_or_null("DialogueBox")
	_expect(yard_inventory != null, "PlayerYard should include InventoryManager for gift flow")
	_expect(yard_relationship != null, "PlayerYard should include RelationshipManager for gift flow")
	_expect(aoi_node != null, "PlayerYard should include Aoi NPC for gift flow")
	_expect(yard_dialogue_box != null, "PlayerYard should include DialogueBox for gift feedback")
	if _has_failed:
		return
	var before_yard_relationship := int(yard_relationship.get_relationship("aoi"))
	yard_inventory.add_item("food_persimmon_riceball", 1)
	yard_inventory.set_selected_item("food_persimmon_riceball")
	aoi_node.on_interact(null)
	await process_frame
	_expect(int(yard_relationship.get_relationship("aoi")) > before_yard_relationship, "PlayerYard gift interaction should increase Aoi relationship")
	_expect(bool(yard_dialogue_box.visible), "PlayerYard gift interaction should open DialogueBox feedback")
	if _has_failed:
		return

	print("OK: Task 009 gift giving + relationship feedback loop validated")
	quit(0)


func _build_npc(
	npc_id: String,
	registry: Node,
	inventory_manager: Node,
	dialogue_manager: Node,
	relationship_manager: Node,
	dialogue_box: Node,
	time_manager: Node,
) -> Node:
	var npc_scene := load(NPC_SCENE_PATH) as PackedScene
	if npc_scene == null:
		_fail("could not load NPC scene")
		return null
	var npc := npc_scene.instantiate() as Node
	if npc == null:
		_fail("could not instantiate NPC scene")
		return null
	root.add_child(npc)
	npc.npc_id = npc_id
	npc.configure_from_data(registry.get_npc(npc_id))
	npc.inventory_manager_path = npc.get_path_to(inventory_manager)
	npc.data_registry_path = npc.get_path_to(registry)
	npc.dialogue_manager_path = npc.get_path_to(dialogue_manager)
	npc.relationship_manager_path = npc.get_path_to(relationship_manager)
	npc.dialogue_box_path = npc.get_path_to(dialogue_box)
	npc.time_manager_path = npc.get_path_to(time_manager)
	return npc


func _new_node(script_path: String) -> Node:
	var script_resource: Script = load(script_path) as Script
	if script_resource == null:
		_fail("could not load %s" % script_path)
		return null
	var node := script_resource.new() as Node
	if node == null:
		_fail("%s did not instantiate as Node" % script_path)
	return node


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	quit(1)
