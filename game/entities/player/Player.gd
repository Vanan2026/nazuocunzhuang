class_name Player
extends CharacterBody2D

signal interaction_started(target: Node)
signal nearest_interactable_changed(target: Node)

@export var move_speed: float = 140.0

@onready var player_sprite: AnimatedSprite2D = $PlayerSprite
@onready var interaction_area: Area2D = $InteractionArea

var facing_direction: Vector2 = Vector2.DOWN
var _interaction_animation_playing: bool = false


func _ready() -> void:
	add_to_group("player")
	interaction_area.nearest_interactable_changed.connect(_on_nearest_interactable_changed)
	if player_sprite != null and not player_sprite.animation_finished.is_connected(_on_player_sprite_animation_finished):
		player_sprite.animation_finished.connect(_on_player_sprite_animation_finished)
	sync_visual_animation(true)


func _physics_process(_delta: float) -> void:
	var input_vector := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if input_vector.length_squared() > 0.0:
		facing_direction = input_vector.normalized()
	velocity = input_vector * move_speed
	move_and_slide()
	sync_visual_animation()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact"):
		try_interact()


func try_interact() -> void:
	var target: Node = interaction_area.get_nearest_interactable()
	if target == null:
		return
	_hide_interaction_hint_ui()
	play_interaction_animation()
	interaction_started.emit(target)
	if target.has_method("on_interact"):
		target.on_interact(self)
	_hide_interaction_hint_ui()


func _on_nearest_interactable_changed(target: Node) -> void:
	nearest_interactable_changed.emit(target)
	_refresh_interaction_hint_ui(target)


func _refresh_interaction_hint_ui(target: Node) -> void:
	var hint_ui := get_node_or_null("/root/InteractionHintUI")
	if hint_ui == null:
		return
	if target == null:
		_hide_interaction_hint_ui()
		return
	if not target.has_method("get_interaction_hint"):
		_hide_interaction_hint_ui()
		return
	var hint := String(target.get_interaction_hint())
	if hint.is_empty():
		_hide_interaction_hint_ui()
	elif hint_ui.has_method("show_hint"):
		hint_ui.show_hint(hint)


func _hide_interaction_hint_ui() -> void:
	var hint_ui := get_node_or_null("/root/InteractionHintUI")
	if hint_ui == null:
		return
	if hint_ui.has_method("hide_hint_now"):
		hint_ui.hide_hint_now()
	elif hint_ui.has_method("hide_hint"):
		hint_ui.hide_hint()


func resolve_direction_suffix(direction: Vector2) -> String:
	var effective_direction := direction
	if effective_direction.length_squared() <= 0.001:
		effective_direction = facing_direction
	if absf(effective_direction.x) < 0.25:
		return "down" if effective_direction.y >= 0.0 else "up"
	if absf(effective_direction.y) < 0.25:
		return "right" if effective_direction.x >= 0.0 else "left"
	if effective_direction.x >= 0.0 and effective_direction.y >= 0.0:
		return "down_right"
	if effective_direction.x < 0.0 and effective_direction.y >= 0.0:
		return "down_left"
	if effective_direction.x < 0.0 and effective_direction.y < 0.0:
		return "up_left"
	return "up_right"


func resolve_animation_name(direction: Vector2, state: String) -> String:
	var suffix := resolve_direction_suffix(direction)
	return "player_%s_%s" % [state, suffix]


func sync_visual_animation(force_restart: bool = false) -> void:
	if player_sprite == null or player_sprite.sprite_frames == null:
		return
	if _interaction_animation_playing:
		return
	var moving := velocity.length_squared() > 0.01
	var next_animation := resolve_animation_name(facing_direction, "walk" if moving else "idle")
	if not player_sprite.sprite_frames.has_animation(next_animation):
		return
	if force_restart or String(player_sprite.animation) != next_animation or not player_sprite.is_playing():
		player_sprite.play(next_animation)


func play_interaction_animation() -> bool:
	if player_sprite == null or player_sprite.sprite_frames == null:
		return false
	var next_animation := resolve_animation_name(facing_direction, "interact")
	if not player_sprite.sprite_frames.has_animation(next_animation):
		return false
	_interaction_animation_playing = true
	player_sprite.play(next_animation)
	return true


func _on_player_sprite_animation_finished() -> void:
	if not _interaction_animation_playing:
		return
	_interaction_animation_playing = false
	sync_visual_animation(true)
