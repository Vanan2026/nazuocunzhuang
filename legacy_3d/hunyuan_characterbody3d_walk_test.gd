extends CharacterBody3D


@export var move_speed: float = 3.2
@export var gravity_strength: float = 18.0
@export var floor_max_angle_deg: float = 48.0
@export var waypoint_wait_seconds: float = 0.35

@onready var nav_agent: NavigationAgent3D = $NavigationAgent3D

var _waypoints: Array[Vector3] = []
var _waypoint_index: int = 0
var _wait_timer: float = 0.0


func _ready() -> void:
	_sync_to_preview_spawn()
	floor_max_angle = deg_to_rad(floor_max_angle_deg)
	collision_layer = 1
	collision_mask = 6 # floor layer (2) + blocker layer (4)

	_collect_waypoints()
	_configure_agent()
	_set_next_target(true)
	_log_contract()


func _sync_to_preview_spawn() -> void:
	var root: Node = get_parent()
	var spawn: Marker3D = root.get_node_or_null("PreviewWorld/PlayerSpawn") as Marker3D
	if spawn == null:
		return
	global_position = spawn.global_position + Vector3(0.0, 0.3, 0.0)


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity_strength * delta
	else:
		velocity.y = max(velocity.y, -0.05)

	if nav_agent.is_navigation_finished():
		velocity.x = move_toward(velocity.x, 0.0, move_speed * 6.0 * delta)
		velocity.z = move_toward(velocity.z, 0.0, move_speed * 6.0 * delta)
		_wait_timer += delta
		if _wait_timer >= waypoint_wait_seconds:
			_set_next_target()
	else:
		_wait_timer = 0.0
		var next_pos: Vector3 = nav_agent.get_next_path_position()
		var to_next: Vector3 = next_pos - global_position
		to_next.y = 0.0
		var dir: Vector3 = to_next.normalized() if to_next.length() > 0.001 else Vector3.ZERO
		velocity.x = dir.x * move_speed
		velocity.z = dir.z * move_speed
		if dir != Vector3.ZERO:
			look_at(global_position + dir, Vector3.UP)

	move_and_slide()


func _collect_waypoints() -> void:
	var root: Node = get_parent()
	var marker_nodes: Array[Marker3D] = []
	for child: Node in root.get_children():
		if child is Marker3D and child.name.begins_with("Waypoint_"):
			marker_nodes.append(child as Marker3D)
	marker_nodes.sort_custom(func(a: Marker3D, b: Marker3D) -> bool:
		return a.name < b.name
	)
	for marker: Marker3D in marker_nodes:
		_waypoints.append(marker.global_position)
	if not _waypoints.is_empty():
		var avg_y := 0.0
		for p in _waypoints:
			avg_y += p.y
		avg_y /= float(_waypoints.size())
		if abs(avg_y - global_position.y) > 1.5:
			_waypoints.clear()

	if _waypoints.size() < 2:
		# Fallback keeps the test scene runnable even if markers are removed.
		_waypoints = [
			global_position + Vector3(-2.5, 0.0, -2.0),
			global_position + Vector3(2.8, 0.0, -1.6),
			global_position + Vector3(2.2, 0.0, 2.4),
			global_position + Vector3(-2.0, 0.0, 2.6),
		]


func _configure_agent() -> void:
	nav_agent.path_desired_distance = 0.2
	nav_agent.target_desired_distance = 0.35
	nav_agent.avoidance_enabled = false


func _set_next_target(immediate: bool = false) -> void:
	if _waypoints.is_empty():
		return
	if not immediate:
		_waypoint_index = (_waypoint_index + 1) % _waypoints.size()
	nav_agent.target_position = _waypoints[_waypoint_index]
	_wait_timer = 0.0


func _log_contract() -> void:
	print(
		"[WalkTest] floor_max_angle_deg=%.2f layer=%d mask=%d nav_map_set=%s waypoints=%d"
		% [rad_to_deg(floor_max_angle), collision_layer, collision_mask, str(nav_agent.get_navigation_map() != RID()), _waypoints.size()]
	)
