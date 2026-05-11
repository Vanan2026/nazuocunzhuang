extends SceneTree

const CASES := [
	{
		"scene": "res://scenes/regions/region_home_back_farm.tscn",
		"spawn_id": "back_farm_from_home_area",
	},
	{
		"scene": "res://scenes/regions/region_home_area.tscn",
		"spawn_id": "home_area_from_back_farm",
	},
]


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	for test_case in CASES:
		await _validate_case(test_case["scene"], test_case["spawn_id"])

	print("OK: scene transition spawn handoff validated")
	quit(0)


func _validate_case(scene_path: String, spawn_id: String) -> void:
	var transition_state := root.get_node_or_null("SceneTransitionState")
	if transition_state == null:
		_fail("missing SceneTransitionState autoload")
		return

	transition_state.set_pending_transition(scene_path, spawn_id, "res://test_source.tscn", "test_exit")
	var error := change_scene_to_file(scene_path)
	if error != OK:
		_fail("could not change scene to %s: %s" % [scene_path, error])
		return

	await process_frame
	await process_frame

	if current_scene == null:
		_fail("current_scene is null after loading %s" % scene_path)
		return

	var player := current_scene.get_node_or_null("YSortWorld/Player") as Node2D
	if player == null:
		_fail("%s missing YSortWorld/Player" % scene_path)
		return

	var marker := _find_spawn_marker(current_scene, spawn_id)
	if marker == null:
		_fail("%s missing spawn_id=%s" % [scene_path, spawn_id])
		return

	if player.global_position.distance_to(marker.global_position) > 0.5:
		_fail(
			"%s player landed at %s, expected %s for spawn_id=%s"
			% [scene_path, player.global_position, marker.global_position, spawn_id]
		)


func _find_spawn_marker(root_node: Node, spawn_id: String) -> Marker2D:
	if root_node is Marker2D and str(root_node.get_meta("spawn_id", "")) == spawn_id:
		return root_node as Marker2D

	for child in root_node.get_children():
		var marker := _find_spawn_marker(child, spawn_id)
		if marker != null:
			return marker

	return null


func _fail(message: String) -> void:
	printerr("FAIL: %s" % message)
	quit(1)
