extends SceneTree

const WORLD_SCENE := "res://scenes/world/world.tscn"
const REST_SCRIPT := "res://scripts/world/veranda_rest_area.gd"
const EXPECTED_SEAT := Vector2(8110, 8428)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var error := change_scene_to_file(WORLD_SCENE)
	if error != OK:
		_fail("could not load normal world entry: %s" % error)
		return

	await process_frame
	await process_frame
	await physics_frame

	var world := current_scene
	if world == null:
		_fail("normal world entry did not create a current scene")
		return

	var rest := world.get_node_or_null("RegionLoader/Region_HomeArea/YSortWorld/Interactables/BenchRestInteract")
	if rest == null:
		_fail("missing BenchRestInteract in loaded Region_HomeArea")
		return

	var script := rest.get_script() as Script
	if script == null or script.resource_path != REST_SCRIPT:
		_fail("BenchRestInteract is not using veranda rest flow script")
		return

	if not rest.has_method("get_interaction_hint") or rest.get_interaction_hint() != "按 E 坐下休息":
		_fail("BenchRestInteract rest hint is not wired")
		return

	var hint := rest.get_node_or_null("HintLabel") as CanvasItem
	if hint == null:
		_fail("BenchRestInteract is missing HintLabel")
		return

	var player := world.get_node_or_null("RegionLoader/Region_HomeArea/YSortWorld/Player")
	if player == null:
		_fail("normal world entry did not expose the scene player")
		return
	if not player.has_method("try_interact") or not player.has_method("is_resting"):
		_fail("player does not expose rest interaction methods")
		return

	player.global_position = rest.global_position + Vector2(0, 8)
	if player.has_method("_sync_visual_animation"):
		player.call("_sync_visual_animation", true)
	await physics_frame

	if rest.has_method("_on_body_entered"):
		rest.call("_on_body_entered", player)
	if not hint.visible:
		_fail("BenchRestInteract hint does not become visible for the player")
		return

	player.try_interact()
	await process_frame
	if not player.is_resting():
		_fail("player did not enter rest state through try_interact")
		return
	if player.global_position.distance_to(EXPECTED_SEAT) > 0.1:
		_fail("player was not moved to the home-area rest seat anchor: %s" % player.global_position)
		return

	player.try_interact()
	await process_frame
	if not _is_standing_up_or_idle(player):
		_fail("player did not leave rest state through a second interaction")
		return

	print("OK: home-area veranda rest flow validated from normal world entry")
	quit(0)


func _is_standing_up_or_idle(player: Node) -> bool:
	var state := int(player.get("current_state"))
	var state_enum: Dictionary = player.get("State")
	return state == int(state_enum["STANDING_UP"]) or state == int(state_enum["IDLE"])


func _fail(message: String) -> void:
	printerr("FAIL: %s" % message)
	quit(1)
