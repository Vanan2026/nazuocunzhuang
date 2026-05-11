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
        Input.get_axis("ui_left", "ui_right"),
        Input.get_axis("ui_up", "ui_down")
    ).normalized()

    if input_direction != Vector2.ZERO:
        facing_direction = input_direction
        is_moving = true
        velocity = input_direction * SPEED
        current_state = State.WALKING
    else:
        is_moving = false
        velocity = Vector2.ZERO
        current_state = State.IDLE

    move_and_slide()
    _constrain_to_walkable_zone()
    _sync_visual_scale()
    _sync_visual_animation()
    emit_signal("state_changed", current_state)


func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("interact"):
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

    show_interaction_hint()


func interact_with(target: Node) -> void:
    current_state = State.INTERACTING
    _interact_lock_remaining = INTERACT_LOCK_DURATION
    _sync_visual_animation(true)
    emit_signal("interaction_started", target)

    if target.has_method("on_interact"):
        target.on_interact(self)


func show_interaction_hint() -> void:
    print("[Player] 没有可交互的对象")


func start_meditation() -> void:
    current_state = State.SITTING_DOWN
    velocity = Vector2.ZERO
    _sync_visual_animation(true)
    emit_signal("state_changed", current_state)
    print("[Player] 开始冥想...")


func end_meditation() -> void:
    if current_state == State.SITTING_DOWN or current_state == State.SITTING or current_state == State.MEDITATING:
        current_state = State.STANDING_UP
    else:
        current_state = State.IDLE
    _sync_visual_animation(true)
    emit_signal("state_changed", current_state)
    print("[Player] 结束冥想")


func begin_rest_at(rest_position: Vector2, rest_facing: Vector2 = Vector2.RIGHT) -> void:
    global_position = rest_position
    if rest_facing != Vector2.ZERO:
        facing_direction = rest_facing.normalized()
    start_meditation()


func is_resting() -> bool:
    return current_state == State.SITTING_DOWN or current_state == State.SITTING or current_state == State.STANDING_UP or current_state == State.MEDITATING


func get_facing_tile() -> Vector2i:
    var tile_pos := global_position / 48
    return Vector2i(tile_pos) + Vector2i(facing_direction)


func _constrain_to_walkable_zone() -> void:
    if _walkable_zone == null:
        return
    if not _walkable_zone.has_method("contains_global_point"):
        return
    if not _walkable_zone.has_method("closest_global_point"):
        return

    var foot_point := global_position
    var in_walkable: Variant = _walkable_zone.call("contains_global_point", foot_point)
    if in_walkable is bool and in_walkable:
        return

    var corrected: Variant = _walkable_zone.call("closest_global_point", foot_point)
    if corrected is Vector2:
        global_position = corrected
        velocity = Vector2.ZERO


func _apply_pending_scene_spawn() -> void:
    var transition_state := get_node_or_null("/root/SceneTransitionState")
    if transition_state == null or not transition_state.has_method("consume_spawn_id_for_scene"):
        return

    var current_scene_path := ""
    if get_tree().current_scene != null:
        current_scene_path = get_tree().current_scene.scene_file_path

    var spawn_id: Variant = transition_state.call("consume_spawn_id_for_scene", current_scene_path)
    if not (spawn_id is String) or spawn_id.is_empty():
        return

    var root := get_tree().current_scene
    var marker := _find_spawn_marker(root, spawn_id)
    if marker == null:
        push_warning("Missing player spawn marker: %s" % spawn_id)
        return

    global_position = marker.global_position


func _find_spawn_marker(root: Node, spawn_id: String) -> Marker2D:
    if root == null:
        return null
    if root is Marker2D and str(root.get_meta("spawn_id", "")) == spawn_id:
        return root as Marker2D

    for child in root.get_children():
        var marker := _find_spawn_marker(child, spawn_id)
        if marker != null:
            return marker

    return null


func _sync_visual_scale() -> void:
    var resolved_scale := visual_base_scale
    if depth_scale_enabled:
        var denom: float = max(1.0, depth_y_near - depth_y_far)
        var t: float = clamp((global_position.y - depth_y_far) / denom, 0.0, 1.0)
        resolved_scale *= lerp(depth_scale_far, depth_scale_near, t)

    _resolved_visual_scale = resolved_scale
    if player_sprite != null:
        player_sprite.scale = Vector2(resolved_scale, resolved_scale)
        player_sprite.position = -sprite_foot_anchor * resolved_scale

    if shadow_sprite != null:
        shadow_sprite.scale = Vector2(resolved_scale, resolved_scale)
        shadow_sprite.position = Vector2(0.0, -6.0 * resolved_scale)


func _sync_visual_animation(force_restart: bool = false) -> void:
    if player_sprite == null:
        return
    if player_sprite.sprite_frames == null:
        return

    var anim := _resolve_animation_name()
    if not player_sprite.sprite_frames.has_animation(anim):
        anim = StringName("player_idle_down")
    player_sprite.speed_scale = _resolve_animation_speed_scale(anim)

    if force_restart or _last_animation != anim:
        player_sprite.play(anim)
        _last_animation = anim
        _apply_walk_visual_offset(anim)
        return

    if not player_sprite.is_playing():
        player_sprite.play(anim)

    _apply_walk_visual_offset(anim)


func _resolve_animation_speed_scale(anim: StringName) -> float:
    var name := String(anim)
    if name == "player_walk_left" or name == "player_walk_right":
        return 1.0
    if name.begins_with("player_walk_"):
        return 0.95
    return 1.0


func _apply_walk_visual_offset(anim: StringName) -> void:
    if player_sprite == null:
        return

    var base_sprite_position := -sprite_foot_anchor * _resolved_visual_scale
    var base_shadow_position := Vector2(0.0, -6.0 * _resolved_visual_scale)
    var name := String(anim)
    if not name.begins_with("player_walk_"):
        player_sprite.position = base_sprite_position
        if shadow_sprite != null:
            shadow_sprite.position = base_shadow_position
            shadow_sprite.self_modulate.a = 0.52
        return

    var frame := player_sprite.frame % 8
    var lift_values: Array[float] = [0.0, -1.2, -2.0, -1.2, 0.0, -1.2, -2.0, -1.2]
    var lift: float = lift_values[frame] * _resolved_visual_scale
    var sway: float = 0.0
    if name == "player_walk_down" or name == "player_walk_up":
        var sway_values: Array[float] = [-0.6, 0.0, 0.6, 0.0, -0.6, 0.0, 0.6, 0.0]
        sway = sway_values[frame] * _resolved_visual_scale

    player_sprite.position = base_sprite_position + Vector2(sway, lift)
    if shadow_sprite != null:
        shadow_sprite.position = base_shadow_position + Vector2(0.0, -lift * 0.25)
        shadow_sprite.self_modulate.a = 0.48 + clamp(-lift / max(1.0, _resolved_visual_scale), 0.0, 2.0) * 0.015


func _resolve_animation_name() -> StringName:
    var suffix := _resolve_facing_suffix()
    match current_state:
        State.WALKING:
            return StringName("player_walk_" + suffix)
        State.INTERACTING:
            return StringName("player_interact_" + suffix)
        State.SITTING_DOWN:
            return &"player_sit_down_side"
        State.SITTING, State.MEDITATING:
            return &"player_sit_idle_side"
        State.STANDING_UP:
            return &"player_stand_up_side"
        _:
            return StringName("player_idle_" + suffix)


func _resolve_facing_suffix() -> String:
    if abs(facing_direction.x) > abs(facing_direction.y):
        if facing_direction.x >= 0.0:
            return "right"
        return "left"
    if facing_direction.y < 0.0:
        return "up"
    return "down"


func _on_player_sprite_animation_finished() -> void:
    if current_state == State.SITTING_DOWN:
        current_state = State.SITTING
        _sync_visual_animation(true)
        emit_signal("state_changed", current_state)
    elif current_state == State.STANDING_UP:
        current_state = State.IDLE
        _sync_visual_animation(true)
        emit_signal("state_changed", current_state)
