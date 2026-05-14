extends Node3D


@export var hide_preview_modules: bool = true
@export var force_double_sided_unshaded: bool = true


func _ready() -> void:
	if hide_preview_modules:
		var preview_modules: Node3D = get_node_or_null("PreviewWorld/ImportedVisualRoot") as Node3D
		if preview_modules != null:
			preview_modules.visible = false

	if force_double_sided_unshaded:
		_apply_debug_material($RawVisualRoot)


func _apply_debug_material(root: Node) -> void:
	var debug_mat := StandardMaterial3D.new()
	debug_mat.vertex_color_use_as_albedo = true
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
