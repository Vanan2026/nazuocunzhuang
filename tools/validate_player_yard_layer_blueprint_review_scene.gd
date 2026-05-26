extends SceneTree

const BLUEPRINT_JSON := "res://production/layout_blueprints/player_yard_layer_blueprint.json"
const REVIEW_SCENE := "res://scenes/dev/player_yard_layer_blueprint_review.tscn"

var _failed := false


func _initialize() -> void:
	var blueprint: Dictionary = _load_blueprint()
	var root: Node = _load_review_scene()
	if root != null:
		_validate_root(root, blueprint)
		_validate_canvas(root, blueprint)
		_validate_layers(root, blueprint)
		_validate_object_zones(root, blueprint)
		_validate_npc_points(root, blueprint)
		root.queue_free()
	if _failed:
		quit(1)
	else:
		print("OK: PlayerYard layer blueprint review scene validates in Godot")
		quit(0)


func _fail(message: String) -> void:
	push_error(message)
	_failed = true


func _load_blueprint() -> Dictionary:
	if not FileAccess.file_exists(BLUEPRINT_JSON):
		_fail("Missing blueprint json: %s" % BLUEPRINT_JSON)
		return {}
	var file := FileAccess.open(BLUEPRINT_JSON, FileAccess.READ)
	if file == null:
		_fail("Unable to open blueprint json")
		return {}
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if not (parsed is Dictionary):
		_fail("Blueprint json did not parse as Dictionary")
		return {}
	return parsed as Dictionary


func _load_review_scene() -> Node:
	var packed := load(REVIEW_SCENE) as PackedScene
	if packed == null:
		_fail("Failed to load review scene: %s" % REVIEW_SCENE)
		return null
	var root: Node = packed.instantiate()
	if root == null:
		_fail("Failed to instantiate review scene")
	return root


func _validate_root(root: Node, blueprint: Dictionary) -> void:
	if root.name != "PlayerYardLayerBlueprintReview":
		_fail("Review scene root name mismatch")
	if String(root.get_meta("source_scene", "")) != String(blueprint.get("source_scene", "")):
		_fail("Review scene source_scene metadata mismatch")
	if String(root.get_meta("export_rule", "")) != "full_canvas_shared_origin":
		_fail("Review scene export rule mismatch")
	if bool(root.get_meta("launch_quality_approved", true)):
		_fail("Review scene must not be launch approved")
	if not bool(root.get_meta("human_visual_approval_required", false)):
		_fail("Review scene must require human visual approval")
	var camera := root.get_node_or_null("ReviewCamera") as Camera2D
	if camera == null or not camera.enabled:
		_fail("Review scene missing enabled ReviewCamera")


func _validate_canvas(root: Node, blueprint: Dictionary) -> void:
	var canvas_polygon := root.get_node_or_null("CanvasContract") as Polygon2D
	if canvas_polygon == null:
		_fail("Review scene missing CanvasContract")
		return
	if canvas_polygon.polygon.size() != 4:
		_fail("CanvasContract should be a four-point rectangle")
	var canvas: Dictionary = blueprint.get("canvas_rect", {}) as Dictionary
	var actual_parts := String(root.get_meta("canvas_rect", "")).split(",")
	if actual_parts.size() != 4:
		_fail("Review scene canvas_rect metadata should contain four comma-separated values")
		return
	var expected_values: Array[float] = [
		float(canvas.get("x", 0.0)),
		float(canvas.get("y", 0.0)),
		float(canvas.get("w", 0.0)),
		float(canvas.get("h", 0.0)),
	]
	for index: int in range(4):
		if not is_equal_approx(float(actual_parts[index]), expected_values[index]):
			_fail("Review scene canvas_rect metadata mismatch")
			return
	if not _polygon_contains_point(canvas_polygon.polygon, Vector2(expected_values[0], expected_values[1])):
		_fail("Review scene canvas_rect metadata mismatch")


func _validate_layers(root: Node, blueprint: Dictionary) -> void:
	var legend := root.get_node_or_null("LayerLegend")
	if legend == null:
		_fail("Review scene missing LayerLegend")
		return
	var layers: Array = blueprint.get("layers", []) as Array
	if legend.get_child_count() < layers.size():
		_fail("LayerLegend child count is smaller than blueprint layers")
	for layer_variant: Variant in layers:
		var layer: Dictionary = layer_variant as Dictionary
		var layer_id := String(layer.get("id", ""))
		var found := false
		for child: Node in legend.get_children():
			if String(child.get_meta("layer_id", "")) == layer_id:
				found = true
				break
		if not found:
			_fail("LayerLegend missing layer: %s" % layer_id)


func _validate_object_zones(root: Node, blueprint: Dictionary) -> void:
	var zones_root := root.get_node_or_null("ObjectZones")
	if zones_root == null:
		_fail("Review scene missing ObjectZones")
		return
	var zones: Array = blueprint.get("object_zones", []) as Array
	if zones_root.get_child_count() != zones.size():
		_fail("ObjectZones child count mismatch")
	for zone_variant: Variant in zones:
		var zone: Dictionary = zone_variant as Dictionary
		var zone_id := String(zone.get("id", ""))
		var found_polygon: Polygon2D = null
		for child: Node in zones_root.get_children():
			if String(child.get_meta("object_id", "")) == zone_id:
				found_polygon = child as Polygon2D
				break
		if found_polygon == null:
			_fail("Missing object zone polygon: %s" % zone_id)
			continue
		if found_polygon.polygon.size() != 4:
			_fail("Object zone polygon should have four points: %s" % zone_id)
		if String(found_polygon.get_meta("layer", "")) != String(zone.get("layer", "")):
			_fail("Object zone layer mismatch: %s" % zone_id)


func _validate_npc_points(root: Node, blueprint: Dictionary) -> void:
	var points_root := root.get_node_or_null("NPCStandingPoints")
	if points_root == null:
		_fail("Review scene missing NPCStandingPoints")
		return
	var points: Array = blueprint.get("npc_standing_points", []) as Array
	var point_polygon_count := 0
	for child: Node in points_root.get_children():
		if child is Polygon2D:
			point_polygon_count += 1
	if point_polygon_count != points.size():
		_fail("NPCStandingPoints child count mismatch")
	for point_variant: Variant in points:
		var point: Dictionary = point_variant as Dictionary
		var npc_id := String(point.get("npc_id", ""))
		var time_block := String(point.get("time_block", ""))
		var found_polygon: Polygon2D = null
		for child: Node in points_root.get_children():
			if String(child.get_meta("npc_id", "")) == npc_id and String(child.get_meta("time_block", "")) == time_block:
				found_polygon = child as Polygon2D
				break
		if found_polygon == null:
			_fail("Missing NPC standing point: %s/%s" % [npc_id, time_block])
			continue
		if found_polygon.polygon.size() < 4:
			_fail("NPC standing point should be a visible diamond: %s/%s" % [npc_id, time_block])


func _polygon_contains_point(polygon: PackedVector2Array, point: Vector2) -> bool:
	for vertex: Vector2 in polygon:
		if vertex.is_equal_approx(point):
			return true
	return false
