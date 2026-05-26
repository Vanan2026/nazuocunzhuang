extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const WATCHDOG_TIMEOUT_SECONDS := 25.0
const SCENES := {
	"house": {
		"path": "res://game/scenes/home/PlayerHouse.tscn",
		"root": "RoughEnvironmentSilhouettes",
		"children": ["WarmFloorWash", "PorchDoorMatShape", "WindowLightPatch"],
	},
	"yard": {
		"path": "res://game/scenes/world/PlayerYard.tscn",
		"root": "YardStructure/RoughEnvironmentSilhouettes",
		"children": ["HomePorchApronShape", "MailboxFootpathShape", "GardenSoilPatchShape", "RepairCornerGrassShape", "ForestEdgeBrushShape"],
	},
	"forest": {
		"path": "res://game/scenes/world/ForestEdge.tscn",
		"root": "ForestStructure/RoughEnvironmentSilhouettes",
		"children": ["TreeLineBackShape", "LeafFloorPatchShape", "ShrineRootMassShape", "ReturnTrailBrushShape"],
	},
}

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: rough environment silhouette initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	for scene_key in SCENES.keys():
		await _validate_scene_silhouettes(scene_key, SCENES[scene_key])
		if _has_failed:
			return
	print("OK: rough environment silhouette runtime validation passed")
	_finish_deferred(0)


func _validate_scene_silhouettes(scene_key: String, config: Dictionary) -> void:
	var scene := load(String(config.get("path", ""))) as PackedScene
	_expect(scene != null, "%s scene should load" % scene_key)
	if _has_failed:
		return
	var instance := scene.instantiate()
	root.add_child(instance)
	await process_frame

	var silhouette_root := instance.get_node_or_null(String(config.get("root", "")))
	_expect(silhouette_root != null, "%s should include rough silhouette root" % scene_key)
	if _has_failed:
		instance.queue_free()
		return
	for child_name in config.get("children", []):
		var polygon := silhouette_root.get_node_or_null(String(child_name)) as Polygon2D
		_expect(polygon != null, "%s missing silhouette polygon %s" % [scene_key, child_name])
		if _has_failed:
			break
		_validate_polygon_points(scene_key, String(child_name), polygon)
		if _has_failed:
			break
	instance.queue_free()
	await process_frame


func _validate_polygon_points(scene_key: String, polygon_name: String, polygon: Polygon2D) -> void:
	_expect(bool(polygon.visible), "%s/%s should be visible" % [scene_key, polygon_name])
	_expect(polygon.polygon.size() >= 4, "%s/%s should be a readable area shape" % [scene_key, polygon_name])
	_expect(polygon.color.a >= 0.18 and polygon.color.a <= 0.95, "%s/%s should be visible but non-final blockout alpha" % [scene_key, polygon_name])


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	_finish_deferred(1)


func _start_watchdog() -> void:
	if _finished:
		return
	_watchdog_timer = Timer.new()
	_watchdog_timer.one_shot = true
	_watchdog_timer.wait_time = WATCHDOG_TIMEOUT_SECONDS
	root.add_child(_watchdog_timer)
	_watchdog_timer.timeout.connect(func() -> void:
		if not _finished:
			_fail("rough environment silhouette validation timed out")
	)
	_watchdog_timer.start()


func _finish_deferred(exit_code: int) -> void:
	if _finished:
		return
	_finished = true
	if _watchdog_timer != null:
		_watchdog_timer.stop()
		_watchdog_timer.queue_free()
		_watchdog_timer = null
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
