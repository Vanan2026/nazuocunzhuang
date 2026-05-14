extends Node3D


@export var camera_path: NodePath = NodePath("InspectorCamera")
@export var raw_root_path: NodePath = NodePath("RawVisualRoot")
@export var fit_padding: float = 1.2
@export var force_solid_debug_material: bool = true


func _ready() -> void:
	var raw_root: Node = get_node_or_null(raw_root_path)
	var cam := get_node_or_null(camera_path) as Camera3D
	if raw_root == null or cam == null:
		return

	var bounds := _compute_bounds(raw_root)
	if bounds.size.length() <= 0.001:
		return

	if force_solid_debug_material:
		_apply_debug_material(raw_root)

	_fit_camera(cam, bounds)


func _compute_bounds(root: Node) -> AABB:
	var found := false
	var merged := AABB()
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var cur: Node = stack.pop_back()
		if cur is MeshInstance3D:
			var mi := cur as MeshInstance3D
			if mi.mesh != null:
				var local := mi.mesh.get_aabb()
				var world := mi.global_transform * local
				if not found:
					merged = world
					found = true
				else:
					merged = merged.merge(world)
		for child: Node in cur.get_children():
			stack.append(child)
	return merged if found else AABB()


func _fit_camera(cam: Camera3D, bounds: AABB) -> void:
	var center: Vector3 = bounds.get_center()
	var radius: float = max(bounds.size.length() * 0.5, 1.0)
	var dir := Vector3(0.72, 0.48, 1.0).normalized()
	var distance: float = clamp(radius * fit_padding * 1.45, 6.0, 55.0)
	print("[RawInspector] bounds_position=", bounds.position, " bounds_size=", bounds.size, " radius=", radius, " camera_distance=", distance)
	cam.global_position = center + dir * distance
	cam.look_at(center, Vector3.UP)
	cam.near = 0.05
	cam.far = max(300.0, distance * 4.0)


func _apply_debug_material(root: Node) -> void:
	var debug_mat: StandardMaterial3D = StandardMaterial3D.new()
	debug_mat.vertex_color_use_as_albedo = false
	debug_mat.albedo_color = Color(0.86, 0.88, 0.9, 1.0)
	debug_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	debug_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	debug_mat.roughness = 1.0
	debug_mat.metallic = 0.0

	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var cur: Node = stack.pop_back()
		if cur is MeshInstance3D:
			(cur as MeshInstance3D).material_override = debug_mat
		for child: Node in cur.get_children():
			stack.append(child)
