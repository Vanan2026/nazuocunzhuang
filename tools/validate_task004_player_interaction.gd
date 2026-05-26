extends SceneTree

const PLAYER_SCENE_PATH := "res://game/entities/player/Player.tscn"
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"
const REQUIRED_ACTIONS: Array[String] = [
	"move_up",
	"move_down",
	"move_left",
	"move_right",
	"interact",
	"use_tool",
	"open_inventory",
	"cancel",
]


func _initialize() -> void:
	for action in REQUIRED_ACTIONS:
		if not InputMap.has_action(action):
			_fail("missing input action %s" % action)
			return

	var player_scene: PackedScene = load(PLAYER_SCENE_PATH) as PackedScene
	if player_scene == null:
		_fail("could not load Player.tscn")
		return
	var player: Node = player_scene.instantiate()
	if not player is CharacterBody2D:
		_fail("Player.tscn root must be CharacterBody2D")
		return
	if not player.has_method("try_interact"):
		_fail("Player is missing try_interact")
		return
	if not player.has_node("InteractionArea"):
		_fail("Player is missing InteractionArea child")
		return
	player.queue_free()

	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	if yard_scene == null:
		_fail("could not load PlayerYard.tscn")
		return
	var yard: Node = yard_scene.instantiate()
	root.add_child(yard)
	var scene_player := yard.get_node_or_null("Player")
	if scene_player == null:
		_fail("PlayerYard is missing Player")
		return
	var interactables := yard.find_children("*", "Area2D", true, false)
	var expected_ids: Array[String] = ["mailbox", "bed", "signboard"]
	for expected_id in expected_ids:
		var found := false
		for interactable in interactables:
			if interactable.get("interactable_id") == expected_id:
				found = true
				if not interactable.has_method("on_interact"):
					_fail("%s does not expose on_interact" % expected_id)
					return
				if String(interactable.get_interaction_hint()).is_empty():
					_fail("%s has empty interaction hint" % expected_id)
					return
		if not found:
			_fail("PlayerYard missing interactable id %s" % expected_id)
			return

	print("OK: Godot loaded Task 004 player, inputs, and PlayerYard interactables")
	quit(0)


func _fail(message: String) -> void:
	push_error(message)
	print("FAIL: %s" % message)
	quit(1)
