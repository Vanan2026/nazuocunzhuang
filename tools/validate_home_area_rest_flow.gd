extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const WORLD_SCENE := "res://scenes/world/world.tscn"
const REST_SCRIPT := "res://scripts/world/veranda_rest_area.gd"
const EXPECTED_SEAT := Vector2(4940, 8020)

var _finishing := false


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

	var rest := world.get_node_or_null("Region_HomeArea/YSortWorld/Interactables/BenchRestInteract")
	if rest == null:
		_fail("missing BenchRestInteract in loaded Region_HomeArea")
		return

	var script := rest.get_script() as Script
	if script == null or script.resource_path != REST_SCRIPT:
		_fail("BenchRestInteract is not using veranda rest flow script")
		return

	if not rest.has_method("get_interaction_hint"):
		_fail("BenchRestInteract rest hint is not wired")
		return
	var rest_hint := str(rest.get_interaction_hint())
	if rest_hint.is_empty() or not rest_hint.contains("E"):
		_fail("BenchRestInteract rest hint is not usable: %s" % rest_hint)
		return

	var hint := rest.get_node_or_null("HintLabel") as CanvasItem
	if hint == null:
		_fail("BenchRestInteract is missing HintLabel")
		return

	var player := world.get_node_or_null("Region_HomeArea/YSortWorld/Player")
	if player == null:
		_fail("normal world entry did not expose the scene player")
		return
	if not player.has_method("try_interact") or not player.has_method("is_resting"):
		_fail("player does not expose rest interaction methods")
		return
	if not _validate_directional_rest_animations(player):
		return

	player.global_position = rest.global_position + Vector2(0, 8)
	if player.has_method("_sync_visual_animation"):
		player.call("_sync_visual_animation", true)
	await physics_frame

	if rest.has_method("_on_body_entered"):
		rest.call("_on_body_entered", player)
	var hint_ui := root.get_node_or_null("InteractionHintUI")
	if hint_ui != null:
		if player.has_method("_update_nearest_interaction_hint"):
			player.call("_update_nearest_interaction_hint")
		if hint.visible:
			_fail("BenchRestInteract local HintLabel should stay hidden when the autoload prompt is active")
			return
		if str(hint_ui.get("current_hint")) != rest_hint:
			_fail("autoload interaction hint did not show the rest hint: %s" % str(hint_ui.get("current_hint")))
			return
	elif not hint.visible:
		_fail("BenchRestInteract fallback HintLabel does not become visible for the player")
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
	player = null
	hint = null
	rest = null
	world = null
	_finish_deferred(0)


func _is_standing_up_or_idle(player: Node) -> bool:
	var state := int(player.get("current_state"))
	var state_enum: Dictionary = player.get("State")
	return state == int(state_enum["STANDING_UP"]) or state == int(state_enum["IDLE"])


func _validate_directional_rest_animations(player: Node) -> bool:
	var sprite := player.get_node_or_null("PlayerSprite") as AnimatedSprite2D
	if sprite == null or sprite.sprite_frames == null:
		_fail("player is missing AnimatedSprite2D SpriteFrames")
		return false

	var state_enum: Dictionary = player.get("State")
	var cases := [
		{"state": int(state_enum["SITTING_DOWN"]), "facing": Vector2.RIGHT, "animation": "player_sit_down_side"},
		{"state": int(state_enum["SITTING_DOWN"]), "facing": Vector2.DOWN, "animation": "player_sit_down_down"},
		{"state": int(state_enum["SITTING_DOWN"]), "facing": Vector2.UP, "animation": "player_sit_down_up"},
		{"state": int(state_enum["SITTING"]), "facing": Vector2.RIGHT, "animation": "player_sit_idle_side"},
		{"state": int(state_enum["SITTING"]), "facing": Vector2.DOWN, "animation": "player_sit_idle_down"},
		{"state": int(state_enum["SITTING"]), "facing": Vector2.UP, "animation": "player_sit_idle_up"},
		{"state": int(state_enum["STANDING_UP"]), "facing": Vector2.RIGHT, "animation": "player_stand_up_side"},
		{"state": int(state_enum["STANDING_UP"]), "facing": Vector2.DOWN, "animation": "player_stand_up_down"},
		{"state": int(state_enum["STANDING_UP"]), "facing": Vector2.UP, "animation": "player_stand_up_up"},
	]

	for test_case in cases:
		var expected := str(test_case["animation"])
		if not sprite.sprite_frames.has_animation(expected):
			_fail("missing directional rest animation: %s" % expected)
			return false
		player.set("current_state", int(test_case["state"]))
		player.set("facing_direction", test_case["facing"])
		if player.has_method("_sync_visual_animation"):
			player.call("_sync_visual_animation", true)
		if str(sprite.animation) != expected:
			_fail("rest facing %s selected %s instead of %s" % [test_case["facing"], sprite.animation, expected])
			return false

	player.set("current_state", int(state_enum["IDLE"]))
	player.set("facing_direction", Vector2.RIGHT)
	if player.has_method("_sync_visual_animation"):
		player.call("_sync_visual_animation", true)
	return true


func _fail(message: String) -> void:
	printerr("FAIL: %s" % message)
	_finish_deferred(1)


func _finish_deferred(exit_code: int) -> void:
	if _finishing:
		return
	_finishing = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
