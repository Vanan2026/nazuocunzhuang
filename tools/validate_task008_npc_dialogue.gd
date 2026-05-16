extends SceneTree

const DATA_REGISTRY_PATH := "res://game/autoload/DataRegistry.gd"
const DIALOGUE_MANAGER_PATH := "res://game/autoload/DialogueManager.gd"
const RELATIONSHIP_MANAGER_PATH := "res://game/autoload/RelationshipManager.gd"
const NPC_SCENE_PATH := "res://game/entities/npc/NPC.tscn"
const DIALOGUE_BOX_PATH := "res://game/scenes/ui/DialogueBox.tscn"
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"

var _has_failed := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var registry := _new_node(DATA_REGISTRY_PATH)
	var dialogue_manager := _new_node(DIALOGUE_MANAGER_PATH)
	var relationship_manager := _new_node(RELATIONSHIP_MANAGER_PATH)
	if _has_failed:
		return
	root.add_child(registry)
	root.add_child(dialogue_manager)
	root.add_child(relationship_manager)
	registry.load_all_data()
	registry.validate_all_data()
	dialogue_manager.bind_registry(registry)
	dialogue_manager.bind_relationship_manager(relationship_manager)

	var rainy_context := {
		"season": "spring",
		"weather": "rainy",
		"time_block": "morning",
	}
	var aoi_dialogue: Dictionary = dialogue_manager.get_dialogue("aoi", rainy_context)
	_expect(String(aoi_dialogue.get("npc_id", "")) == "aoi", "DialogueManager should return aoi dialogue")
	if _has_failed:
		return
	_expect(not aoi_dialogue.get("lines", []).is_empty(), "aoi dialogue should contain lines")
	if _has_failed:
		return

	var mika_dialogue: Dictionary = dialogue_manager.get_dialogue("mika", {
		"season": "spring",
		"weather": "sunny",
		"time_block": "morning",
		"flags": {},
	})
	_expect(String(mika_dialogue.get("dialogue_id", "")) == "mika_mailbox_hint_01", "flag_not_set daily dialogue should outrank fallback for Mika")
	if _has_failed:
		return
	dialogue_manager.start_dialogue("mika", mika_dialogue)
	dialogue_manager.finish_dialogue()
	_expect(dialogue_manager.has_flag("mika_hint_mailbox"), "DialogueManager should apply sets_flags on finish")
	if _has_failed:
		return

	var npc_scene: PackedScene = load(NPC_SCENE_PATH) as PackedScene
	var dialogue_box_scene: PackedScene = load(DIALOGUE_BOX_PATH) as PackedScene
	if npc_scene == null or dialogue_box_scene == null:
		_fail("could not load NPC or DialogueBox scene")
		return
	var npc: Node = npc_scene.instantiate()
	var dialogue_box: Node = dialogue_box_scene.instantiate()
	root.add_child(dialogue_box)
	root.add_child(npc)
	npc.npc_id = "aoi"
	npc.configure_from_data(registry.get_npc("aoi"))
	npc.dialogue_manager_path = npc.get_path_to(dialogue_manager)
	npc.relationship_manager_path = npc.get_path_to(relationship_manager)
	npc.dialogue_box_path = npc.get_path_to(dialogue_box)
	npc.on_interact(null)
	await process_frame
	_expect(relationship_manager.get_relationship("aoi") == 1, "first daily talk should add one relationship point")
	if _has_failed:
		return
	npc.on_interact(null)
	await process_frame
	_expect(relationship_manager.get_relationship("aoi") == 1, "second same-day talk should not add relationship again")
	if _has_failed:
		return
	relationship_manager.reset_daily_social_state()
	npc.on_interact(null)
	await process_frame
	_expect(relationship_manager.get_relationship("aoi") == 2, "relationship should increase again after daily reset")
	if _has_failed:
		return
	_expect(dialogue_box.visible, "DialogueBox should be visible after NPC interaction")
	if _has_failed:
		return

	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	if yard_scene == null:
		_fail("could not load PlayerYard")
		return
	var yard: Node = yard_scene.instantiate()
	root.add_child(yard)
	await process_frame
	await physics_frame
	for npc_id in ["Aoi", "Gen", "Mika"]:
		var resident := yard.get_node_or_null("NPCs/%s" % npc_id)
		_expect(resident != null, "PlayerYard missing NPC %s" % npc_id)
		if _has_failed:
			return

	var hud := yard.get_node_or_null("TimeWeatherHUD")
	_expect(hud != null and hud.has_method("get_weather_icon_path"), "HUD should expose weather icon path helper")
	if _has_failed:
		return
	_expect(_asset_exists(hud.get_weather_icon_path("sunny")), "sunny weather icon should exist")
	if _has_failed:
		return

	var plot := yard.get_node_or_null("FarmPlots/FarmPlot0")
	_expect(plot != null and plot.has_method("get_stage_sprite_path"), "FarmPlot should expose crop stage sprite path helper")
	if _has_failed:
		return
	plot.till()
	plot.plant_seed("seed_turnip")
	_expect(_asset_exists(plot.get_stage_sprite_path()), "planted FarmPlot stage sprite should exist")
	if _has_failed:
		return

	print("OK: Godot validated Task 008 NPC/Dialogue and Batch E runtime integration")
	quit(0)


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


func _asset_exists(path: String) -> bool:
	return ResourceLoader.exists(path) or FileAccess.file_exists(path)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	quit(1)
