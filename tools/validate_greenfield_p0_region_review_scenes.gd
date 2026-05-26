extends SceneTree

const REGION_IDS: Array[String] = [
	"home_area",
	"village",
	"back_farm",
	"forest_edge",
	"orchard",
	"pond",
	"mountain_path",
	"mountain_hut",
	"mountain",
	"cliff_view",
]
const BATCH_A_REGION_IDS: Array[String] = ["home_area", "village", "back_farm"]
const WORLD_LAYOUT_SCENE := "greenfield_p0_world_layout_review"
const SCENE_ROOT := "res://scenes/dev/greenfield_p0_reviews/"
const REQUIRED_LAYERS: Array[String] = [
	"BaseGround",
	"TerrainDetails",
	"BehindPlayerStructures",
	"YSortPropsStructures",
	"ShadowOverlay",
	"ForegroundOcclusion",
	"LightWeatherOverlaySpring",
]

var _failed := false


func _initialize() -> void:
	for region_id: String in REGION_IDS:
		_validate_region_scene(region_id)
	_validate_batch_scene("greenfield_p0_region_review_batch_a", BATCH_A_REGION_IDS)
	_validate_batch_scene("greenfield_p0_region_review_all", REGION_IDS)
	_validate_world_layout_scene()
	if _failed:
		quit(1)
	else:
		print("OK: greenfield P0 region review scenes validate in Godot")
		quit(0)


func _fail(message: String) -> void:
	push_error(message)
	_failed = true


func _load_scene(path: String) -> Node:
	var packed: PackedScene = load(path) as PackedScene
	if packed == null:
		_fail("Failed to load scene: %s" % path)
		return null
	var instance: Node = packed.instantiate()
	if instance == null:
		_fail("Failed to instantiate scene: %s" % path)
	return instance


func _validate_region_scene(region_id: String) -> void:
	var path := SCENE_ROOT + "greenfield_p0_region_review_%s.tscn" % region_id
	var root := _load_scene(path)
	if root == null:
		return
	if String(root.get_meta("package_id", "")) != "greenfield_p0_base_asset_pack_v001":
		_fail("%s package metadata mismatch" % region_id)
	if String(root.get_meta("region_id", "")) != region_id:
		_fail("%s region metadata mismatch" % region_id)
	if bool(root.get_meta("launch_quality_approved", true)):
		_fail("%s must not be launch approved" % region_id)
	if not bool(root.get_meta("human_visual_approval_required", false)):
		_fail("%s must require human visual approval" % region_id)
	var camera := root.get_node_or_null("ReviewCamera") as Camera2D
	if camera == null or not camera.enabled:
		_fail("%s missing enabled ReviewCamera" % region_id)
	var stack := root.get_node_or_null("RuntimeLayerStack")
	if stack == null:
		_fail("%s missing RuntimeLayerStack" % region_id)
		root.queue_free()
		return
	for layer_name: String in REQUIRED_LAYERS:
		var sprite := stack.get_node_or_null(layer_name) as Sprite2D
		if sprite == null:
			_fail("%s missing layer %s" % [region_id, layer_name])
		elif sprite.texture == null:
			_fail("%s layer %s missing texture" % [region_id, layer_name])
	var anchors := root.get_node_or_null("ReviewAnchors")
	if anchors == null or anchors.get_child_count() < 5:
		_fail("%s missing review anchors" % region_id)
	root.queue_free()


func _validate_batch_scene(scene_name: String, region_ids: Array[String]) -> void:
	var root := _load_scene(SCENE_ROOT + scene_name + ".tscn")
	if root == null:
		return
	if bool(root.get_meta("launch_quality_approved", true)):
		_fail("%s must not be launch approved" % scene_name)
	var previews := root.get_node_or_null("RegionPreviews")
	if previews == null:
		_fail("%s missing RegionPreviews" % scene_name)
		root.queue_free()
		return
	for region_id: String in region_ids:
		var node := previews.get_node_or_null(region_id)
		if node == null:
			_fail("%s missing region %s" % [scene_name, region_id])
			continue
		var sprite := node.get_node_or_null("PaintedSource") as Sprite2D
		if sprite == null or sprite.texture == null:
			_fail("%s missing painted source texture for %s" % [scene_name, region_id])
	root.queue_free()


func _validate_world_layout_scene() -> void:
	var root := _load_scene(SCENE_ROOT + WORLD_LAYOUT_SCENE + ".tscn")
	if root == null:
		return
	if String(root.get_meta("package_id", "")) != "greenfield_p0_base_asset_pack_v001":
		_fail("world layout package metadata mismatch")
	if String(root.get_meta("status", "")) != "review_candidate":
		_fail("world layout status must be review_candidate")
	if bool(root.get_meta("launch_quality_approved", true)):
		_fail("world layout must not be launch approved")
	var connections := root.get_node_or_null("Connections")
	if connections == null or connections.get_child_count() < 12:
		_fail("world layout missing connection lines")
	var tiles := root.get_node_or_null("RegionTiles")
	if tiles == null:
		_fail("world layout missing RegionTiles")
		root.queue_free()
		return
	for region_id: String in REGION_IDS:
		var tile := tiles.get_node_or_null(region_id)
		if tile == null:
			_fail("world layout missing region %s" % region_id)
			continue
		if String(tile.get_meta("region_id", "")) != region_id:
			_fail("world layout region metadata mismatch for %s" % region_id)
		var sprite := tile.get_node_or_null("PaintedSource") as Sprite2D
		if sprite == null or sprite.texture == null:
			_fail("world layout missing painted source texture for %s" % region_id)
		var sockets := tile.get_node_or_null("Sockets")
		if sockets == null:
			_fail("world layout missing sockets for %s" % region_id)
	root.queue_free()
