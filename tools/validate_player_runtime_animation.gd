extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const PLAYER_SCENE := preload("res://game/entities/player/Player.tscn")

var _has_failed := false
var _finished := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var player := PLAYER_SCENE.instantiate()
	root.add_child(player)
	await process_frame
	await process_frame

	var sprite := player.get_node_or_null("PlayerSprite") as AnimatedSprite2D
	_expect(sprite != null, "Player scene should expose AnimatedSprite2D PlayerSprite")
	if _has_failed:
		return
	_expect(sprite.sprite_frames != null, "PlayerSprite should have SpriteFrames")
	if _has_failed:
		return

	var cases := [
		{"direction": Vector2.DOWN, "state": "idle", "expected": "player_idle_down"},
		{"direction": Vector2.RIGHT, "state": "walk", "expected": "player_walk_right"},
		{"direction": Vector2(-1, -1), "state": "walk", "expected": "player_walk_up_left"},
		{"direction": Vector2(-1, -1), "state": "interact", "expected": "player_interact_up_left"},
	]
	for test_case in cases:
		var actual := String(player.call("resolve_animation_name", test_case["direction"], test_case["state"]))
		_expect(actual == String(test_case["expected"]), "expected %s, got %s" % [test_case["expected"], actual])
		if _has_failed:
			return

	player.set("facing_direction", Vector2.RIGHT)
	player.set("velocity", Vector2(32, 0))
	player.call("sync_visual_animation", true)
	_expect(String(sprite.animation) == "player_walk_right", "moving right should select player_walk_right")
	if _has_failed:
		return

	player.set("velocity", Vector2.ZERO)
	player.call("sync_visual_animation", true)
	_expect(String(sprite.animation) == "player_idle_right", "stopping should select player_idle_right")
	if _has_failed:
		return

	var played := bool(player.call("play_interaction_animation"))
	_expect(played, "play_interaction_animation should return true when frames exist")
	if _has_failed:
		return
	_expect(String(sprite.animation) == "player_interact_right", "interact should select player_interact_right")
	if _has_failed:
		return

	print("OK: player runtime animation validation passed")
	_finish_deferred(0)


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


func _finish_deferred(exit_code: int) -> void:
	if _finished:
		return
	_finished = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
