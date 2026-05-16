extends CharacterBody2D

const SPEED: float = 82.0
const INTERACTION_RANGE: float = 64.0
const INVALID_NODE_PATH: NodePath = NodePath("")
const INTERACT_LOCK_DURATION: float = 0.18

enum State { IDLE, WALKING, INTERACTING, SITTING_DOWN, SITTING, STANDING_UP, MEDITATING }
var current_state: State = State.IDLE

var facing_direction: Vector2 = Vector2.DOWN
var is_moving: bool = false
@export var walkable_zone_path: NodePath = INVALID_NODE_PATH
@export var visual_base_scale: float = 1.0
@export var depth_scale_enabled: bool = false
@export var depth_y_far: float = 456.0
@export var depth_y_near: float = 706.0
@export var depth_scale_far: float = 0.90
@export var depth_scale_near: float = 1.15
@export var sprite_frame_size: Vector2 = Vector2(192, 288)
@export var sprite_foot_anchor: Vector2 = Vector2(96, 280)

signal interaction_started(target: Node)
signal interaction_ended(target: Node)
signal state_changed(new_state: State)

@onready var animation_player: AnimationPlayer = $AnimationPlayer if has_node("AnimationPlayer") else null
@onready var interaction_area: Area2D = $InteractionArea if has_node("InteractionArea") else null
@onready var player_sprite: AnimatedSprite2D = $PlayerSprite as AnimatedSprite2D
@onready var shadow_sprite: Sprite2D = $ShadowSprite as Sprite2D

var _walkable_zone: Node = null
var _last_animation: StringName = &""
var _interact_lock_remaining: float = 0.0
var _resolved_visual_scale: float = 1.0
var _current_hint: String = ""

func _ready() -> void:
	add_to_group("player")
	add_to_group("interactable")
	if walkable_zone_path != INVALID_NODE_PATH:
		_walkable_zone = get_node_or_null(walkable_zone_path)
	if player_sprite != null and not player_sprite.animation_finished.is_connected(_on_player_sprite_animation_finished):
		player_sprite.animation_finished.connect(_on_player_sprite_animation_finished)
	_apply_pending_scene_spawn()
	_sync_visual_scale()
	_sync_visual_animation(true)

func _apply_pending_scene_spawn() -> void:
	if has_meta("pending_scene_spawn"):
		global_position = get_meta("pending_scene_spawn")
		remove_meta("pending_scene_spawn")

func _physics_process(delta: float) -> void:
	if current_state == State.SITTING_DOWN or current_state == State.SITTING or current_state == State.STANDING_UP or current_state == State.MEDITATING:
		velocity = Vector2.ZERO
		_sync_visual_scale()
		_sync_visual_animation()
		return

	if _interact_lock_remaining > 0.0:
		_interact_lock_remaining = max(0.0, _interact_lock_remaining - delta)
		velocity = Vector2.ZERO
		current_state = State.INTERACTING
		_sync_visual_animation()
		emit_signal("state_changed", current_state)
		return

	var input_direction := Vector2(
		_axis_strength("move_left", "ui_left", "move_right", "ui_right"),
		_axis_strength("move_up", "ui_up", "move_down", "ui_down")
	).normalized()

	velocity = input_direction * SPEED
	facing_direction = input_direction if input_direction != Vector2.ZERO else facing_direction
	is_moving = input_direction != Vector2.ZERO

	if is_moving:
		current_state = State.WALKING
	else:
		current_state = State.IDLE

	move_and_slide()
	_update_nearest_interaction_hint()
	_sync_visual_scale()
	_sync_visual_animation()
	emit_signal("state_changed", current_state)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact"):
		print("[Player] 交互键按下")
		try_interact()
	elif event.is_action_pressed("ui_cancel"):
		if is_resting():
			end_meditation()
		else:
			emit_signal("interaction_ended", null)


func try_interact() -> void:
	if interaction_area:
		var targets := interaction_area.get_overlapping_bodies()
		for target in targets:
			if target.is_in_group("interactable") and target != self:
				interact_with(target)
				return

	var nearby_interactables := get_tree().get_nodes_in_group("interactable")

	for interactable in nearby_interactables:
		if interactable is Area2D and interactable.has_method("get_interaction_hint"):
			var dist := global_position.distance_to(interactable.global_position)
			if dist < INTERACTION_RANGE:
				interact_with(interactable)
				return

	_update_nearest_interaction_hint()
	show_interaction_hint()


func interact_with(target: Node) -> void:
	emit_signal("interaction_started", target)

	if target.has_method("on_interact"):
		target.on_interact(self)

	if is_resting():
		return

	current_state = State.INTERACTING
	_interact_lock_remaining = INTERACT_LOCK_DURATION
	_sync_visual_animation(true)


func show_interaction_hint() -> void:
	if _current_hint.is_empty():
		print("[Player] 没有可交互的对象")


func _update_hint_ui(hint: String) -> void:
	_current_hint = hint
	var hint_ui = get_node_or_null("/root/InteractionHintUI")
	if hint_ui != null and hint_ui.has_method("show_hint"):
		if hint.is_empty():
			hint_ui.hide_hint()
		else:
			hint_ui.show_hint(hint)


func _update_nearest_interaction_hint() -> void:
	var nearest_hint := ""
	var nearest_dist := INTERACTION_RANGE

	for interactable in get_tree().get_nodes_in_group("interactable"):
		if interactable == self:
			continue
		if not (interactable is Area2D):
			continue
		if not interactable.has_method("get_interaction_hint"):
			continue
		var dist := global_position.distance_to(interactable.global_position)
		if dist <= nearest_dist:
			nearest_dist = dist
			nearest_hint = interactable.get_interaction_hint()

	_update_hint_ui(nearest_hint)


func _axis_strength(negative_action: StringName, negative_fallback: StringName, positive_action: StringName, positive_fallback: StringName) -> float:
	var negative := Input.get_action_strength(negative_action)
	if negative == 0.0:
		negative = Input.get_action_strength(negative_fallback)
	var positive := Input.get_action_strength(positive_action)
	if positive == 0.0:
		positive = Input.get_action_strength(positive_fallback)
	return positive - negative


func start_meditation() -> void:
	current_state = State.SITTING_DOWN
	velocity = Vector2.ZERO
	_sync_visual_scale()
	_sync_visual_animation()
	emit_signal("state_changed", current_state)


func begin_rest_at(anchor: Vector2, facing: Vector2 = Vector2.RIGHT) -> void:
	global_position = anchor
	facing_direction = facing.normalized() if facing != Vector2.ZERO else Vector2.RIGHT
	start_meditation()


func end_meditation() -> void:
	current_state = State.STANDING_UP
	_sync_visual_animation()
	emit_signal("state_changed", current_state)


func is_resting() -> bool:
	return current_state == State.SITTING_DOWN or current_state == State.SITTING or current_state == State.STANDING_UP or current_state == State.MEDITATING


func _sync_visual_scale() -> void:
	if depth_scale_enabled:
		var y_ratio = clamp((global_position.y - depth_y_far) / (depth_y_near - depth_y_far), 0.0, 1.0)
		_resolved_visual_scale = lerp(depth_scale_far, depth_scale_near, y_ratio) * visual_base_scale
	else:
		_resolved_visual_scale = visual_base_scale

	scale = Vector2(_resolved_visual_scale, _resolved_visual_scale)

	if shadow_sprite != null:
		shadow_sprite.scale = Vector2(1.0 / _resolved_visual_scale, 1.0)


func _sync_visual_animation(force_restart: bool = false) -> void:
	if player_sprite == null:
		return

	var new_animation: StringName
	var should_flip_h: bool = false

	match current_state:
		State.WALKING:
			if facing_direction.x < -0.1:
				if facing_direction.y < -0.1:
					new_animation = &"player_walk_up_left"
				elif facing_direction.y > 0.1:
					new_animation = &"player_walk_down_left"
				else:
					new_animation = &"player_walk_left"
			elif facing_direction.x > 0.1:
				if facing_direction.y < -0.1:
					new_animation = &"player_walk_up_right"
				elif facing_direction.y > 0.1:
					new_animation = &"player_walk_down_right"
				else:
					new_animation = &"player_walk_right"
			elif facing_direction.y < 0.0:
				new_animation = &"player_walk_up"
			else:
				new_animation = &"player_walk_down"
		State.INTERACTING:
			if facing_direction.x < -0.1:
				if facing_direction.y < -0.1:
					new_animation = &"player_interact_up_left"
				elif facing_direction.y > 0.1:
					new_animation = &"player_interact_down_left"
				else:
					new_animation = &"player_interact_left"
			elif facing_direction.x > 0.1:
				if facing_direction.y < -0.1:
					new_animation = &"player_interact_up_right"
				elif facing_direction.y > 0.1:
					new_animation = &"player_interact_down_right"
				else:
					new_animation = &"player_interact_right"
			elif facing_direction.y < 0.0:
				new_animation = &"player_interact_up"
			else:
				new_animation = &"player_interact_down"
		State.SITTING_DOWN:
			new_animation = _rest_animation(&"player_sit_down")
		State.SITTING:
			new_animation = _rest_animation(&"player_sit_idle")
		State.STANDING_UP:
			new_animation = _rest_animation(&"player_stand_up")
		State.MEDITATING:
			new_animation = _rest_animation(&"player_sit_idle")
		_:
			if facing_direction.x < -0.1:
				if facing_direction.y < -0.1:
					new_animation = &"player_idle_up_left"
				elif facing_direction.y > 0.1:
					new_animation = &"player_idle_down_left"
				else:
					new_animation = &"player_idle_left"
			elif facing_direction.x > 0.1:
				if facing_direction.y < -0.1:
					new_animation = &"player_idle_up_right"
				elif facing_direction.y > 0.1:
					new_animation = &"player_idle_down_right"
				else:
					new_animation = &"player_idle_right"
			elif facing_direction.y < 0.0:
				new_animation = &"player_idle_up"
			else:
				new_animation = &"player_idle_down"

	if _last_animation != new_animation or force_restart:
		_last_animation = new_animation
		if player_sprite.sprite_frames != null and player_sprite.sprite_frames.has_animation(new_animation):
			player_sprite.play(new_animation)
		else:
			print("[Player] 动画不存在: ", new_animation)


func _rest_animation(prefix: StringName) -> StringName:
	var direction_suffix := "side"
	if abs(facing_direction.y) > abs(facing_direction.x) and facing_direction.y < -0.1:
		direction_suffix = "up"
	elif abs(facing_direction.y) > abs(facing_direction.x) and facing_direction.y > 0.1:
		direction_suffix = "down"
	return StringName("%s_%s" % [String(prefix), direction_suffix])


func _on_player_sprite_animation_finished() -> void:
	match current_state:
		State.SITTING_DOWN:
			current_state = State.SITTING
		State.STANDING_UP:
			current_state = State.IDLE

	_sync_visual_animation()
	emit_signal("state_changed", current_state)
