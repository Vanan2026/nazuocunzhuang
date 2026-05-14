extends CharacterBody3D


enum CharacterMode {
	LOCOMOTION,
	INTERACTING,
	SITTING,
	TRANSITION,
}


@export var move_speed: float = 3.0
@export var gravity_strength: float = 18.0
@export var floor_max_angle_deg: float = 50.0
@export var rotation_lerp_speed: float = 9.0
@export var model_yaw_offset_deg: float = 180.0

@onready var visual_root: Node3D = $VisualRoot

var _mode: int = CharacterMode.LOCOMOTION
var _anim_player: AnimationPlayer = null
var _clip_idle: StringName = &""
var _clip_walk: StringName = &""
var _clip_interact: StringName = &""
var _clip_sit_down: StringName = &""
var _clip_sit_idle: StringName = &""
var _clip_stand_up: StringName = &""
var _q_was_down: bool = false
var _e_was_down: bool = false


func _ready() -> void:
	floor_max_angle = deg_to_rad(floor_max_angle_deg)
	collision_layer = 1
	collision_mask = 6 # floor layer (2) + blocker layer (4)
	_sync_to_preview_spawn()

	_anim_player = _find_animation_player(visual_root)
	if _anim_player != null:
		_bind_clips()
		_anim_player.animation_finished.connect(_on_animation_finished)
		_play_clip(_clip_idle, true)


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity_strength * delta
	else:
		velocity.y = max(velocity.y, -0.05)

	_handle_action_input()

	if _mode == CharacterMode.LOCOMOTION:
		var input_axis := _get_move_axis()
		var move_dir := Vector3(input_axis.x, 0.0, input_axis.y)
		if move_dir.length() > 0.001:
			move_dir = move_dir.normalized()
			velocity.x = move_dir.x * move_speed
			velocity.z = move_dir.z * move_speed
			_rotate_visual_towards(move_dir, delta)
			_play_clip(_clip_walk, true)
		else:
			velocity.x = move_toward(velocity.x, 0.0, move_speed * 8.0 * delta)
			velocity.z = move_toward(velocity.z, 0.0, move_speed * 8.0 * delta)
			_play_clip(_clip_idle, true)
	else:
		velocity.x = move_toward(velocity.x, 0.0, move_speed * 8.0 * delta)
		velocity.z = move_toward(velocity.z, 0.0, move_speed * 8.0 * delta)
		if _mode == CharacterMode.SITTING:
			_play_clip(_clip_sit_idle, true)

	move_and_slide()


func _handle_action_input() -> void:
	var e_down := Input.is_key_pressed(KEY_E)
	var q_down := Input.is_key_pressed(KEY_Q)
	var e_just_pressed := e_down and not _e_was_down
	var q_just_pressed := q_down and not _q_was_down
	_e_was_down = e_down
	_q_was_down = q_down

	if e_just_pressed and _mode == CharacterMode.LOCOMOTION:
		if _play_clip(_clip_interact, false):
			_mode = CharacterMode.INTERACTING

	if q_just_pressed:
		if _mode == CharacterMode.LOCOMOTION:
			if _play_clip(_clip_sit_down, false):
				_mode = CharacterMode.TRANSITION
			else:
				_mode = CharacterMode.SITTING
		elif _mode == CharacterMode.SITTING:
			if _play_clip(_clip_stand_up, false):
				_mode = CharacterMode.TRANSITION
			else:
				_mode = CharacterMode.LOCOMOTION


func _sync_to_preview_spawn() -> void:
	var root: Node = get_parent()
	if root == null:
		return
	var spawn: Marker3D = root.get_node_or_null("PreviewWorld/PlayerSpawn") as Marker3D
	if spawn == null:
		return
	global_position = spawn.global_position + Vector3(0.0, 0.3, 0.0)


func _find_animation_player(root: Node) -> AnimationPlayer:
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var cur: Node = stack.pop_back()
		if cur is AnimationPlayer:
			return cur as AnimationPlayer
		for child: Node in cur.get_children():
			stack.append(child)
	return null


func _bind_clips() -> void:
	var names := _anim_player.get_animation_list()
	_clip_idle = _match_clip(names, "idle")
	_clip_walk = _match_clip(names, "walk")
	_clip_interact = _match_clip(names, "interact")
	_clip_sit_down = _match_clip(names, "sit_down")
	_clip_sit_idle = _match_clip(names, "sit_idle")
	_clip_stand_up = _match_clip(names, "stand_up")

	print(
		"[Protagonist3D] clips idle=%s walk=%s interact=%s sit_down=%s sit_idle=%s stand_up=%s"
		% [_clip_idle, _clip_walk, _clip_interact, _clip_sit_down, _clip_sit_idle, _clip_stand_up]
	)


func _match_clip(names: PackedStringArray, token: String) -> StringName:
	for name: String in names:
		if name.to_lower().contains(token):
			return StringName(name)
	return StringName("")


func _play_clip(clip_name: StringName, should_loop: bool) -> bool:
	if _anim_player == null:
		return false
	if clip_name.is_empty():
		return false
	if _anim_player.current_animation == clip_name and _anim_player.is_playing():
		return true
	var animation: Animation = _anim_player.get_animation(clip_name)
	if animation != null:
		animation.loop_mode = Animation.LOOP_LINEAR if should_loop else Animation.LOOP_NONE
	_anim_player.play(clip_name, 0.15)
	return true


func _rotate_visual_towards(move_dir: Vector3, delta: float) -> void:
	var target_yaw: float = atan2(move_dir.x, move_dir.z) + deg_to_rad(model_yaw_offset_deg)
	visual_root.rotation.y = lerp_angle(visual_root.rotation.y, target_yaw, min(1.0, rotation_lerp_speed * delta))


func _on_animation_finished(anim_name: StringName) -> void:
	if anim_name == _clip_interact:
		_mode = CharacterMode.LOCOMOTION
		_play_clip(_clip_idle, true)
	elif anim_name == _clip_sit_down:
		_mode = CharacterMode.SITTING
		_play_clip(_clip_sit_idle, true)
	elif anim_name == _clip_stand_up:
		_mode = CharacterMode.LOCOMOTION
		_play_clip(_clip_idle, true)


func _get_move_axis() -> Vector2:
	var axis: Vector2 = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if axis.length() > 0.001:
		return axis

	var x := 0.0
	var y := 0.0
	if Input.is_physical_key_pressed(KEY_A):
		x -= 1.0
	if Input.is_physical_key_pressed(KEY_D):
		x += 1.0
	if Input.is_physical_key_pressed(KEY_W):
		y -= 1.0
	if Input.is_physical_key_pressed(KEY_S):
		y += 1.0
	var raw := Vector2(x, y)
	return raw.normalized() if raw.length() > 0.001 else Vector2.ZERO
