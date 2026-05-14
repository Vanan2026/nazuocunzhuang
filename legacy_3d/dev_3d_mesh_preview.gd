extends Node3D

@export_dir var mesh_dir: String = "res://assets/3d/processed"
@export var max_items: int = 24
@export var grid_columns: int = 4
@export var spacing_x: float = 4.0
@export var spacing_z: float = 4.0

@onready var imported_meshes: Node3D = $ImportedMeshes


func _ready() -> void:
	_clear_children()
	var files := _collect_mesh_files(mesh_dir)
	if files.is_empty():
		push_warning("[Dev3DPreview] no mesh files found in %s" % mesh_dir)
		return

	var count: int = mini(files.size(), max_items)
	for i in range(count):
		var path: String = files[i]
		var packed := load(path) as PackedScene
		if packed == null:
			push_warning("[Dev3DPreview] failed to load %s" % path)
			continue
		var instance := packed.instantiate()
		if instance == null:
			push_warning("[Dev3DPreview] failed to instantiate %s" % path)
			continue

		var holder := Node3D.new()
		holder.name = "Mesh_%02d" % i
		imported_meshes.add_child(holder)
		holder.add_child(instance)
		if instance is Node3D:
			(instance as Node3D).position = Vector3.ZERO

		var row: int = i / grid_columns
		var col: int = i % grid_columns
		holder.position = Vector3(col * spacing_x, 0.0, row * spacing_z)

	print("[Dev3DPreview] loaded %d meshes from %s" % [count, mesh_dir])


func _clear_children() -> void:
	for child in imported_meshes.get_children():
		child.queue_free()


func _collect_mesh_files(dir_path: String) -> Array[String]:
	var result: Array[String] = []
	var dir := DirAccess.open(dir_path)
	if dir == null:
		push_warning("[Dev3DPreview] cannot open directory %s" % dir_path)
		return result

	dir.list_dir_begin()
	while true:
		var name := dir.get_next()
		if name == "":
			break
		if dir.current_is_dir():
			continue
		var lower := name.to_lower()
		if lower.ends_with(".glb") or lower.ends_with(".gltf") or lower.ends_with(".tscn"):
			result.append(dir_path.path_join(name))
	dir.list_dir_end()
	result.sort()
	return result
