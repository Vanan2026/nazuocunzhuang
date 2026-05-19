extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")

const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"

var _has_failed := false
var _finishing := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	if yard_scene == null:
		_fail("could not load PlayerYard")
		return
	var yard: Node = yard_scene.instantiate()
	root.add_child(yard)
	await process_frame
	await physics_frame
	await process_frame

	for node_path in ["Mailbox", "Signboard", "OldWell", "Bench"]:
		var prop := yard.get_node_or_null(node_path)
		_expect(prop != null, "PlayerYard missing %s" % node_path)
		if _has_failed:
			return
		_expect(prop.is_in_group("interactable"), "%s should be interactable" % node_path)
		if _has_failed:
			return

	var checks := {
		"Mailbox/MailboxArt": "res://assets/art/props/region_home_area_prop_mailbox_v001.png",
		"Signboard/SignboardArt": "res://assets/art/props/region_home_area_prop_road_sign_v001.png",
		"OldWell/OldWellArt": "res://assets/art/props/region_home_area_prop_well_broken_v001.png",
		"Bench/BenchArt": "res://assets/art/props/region_home_area_prop_bench_v001.png",
	}
	for sprite_path in checks.keys():
		var sprite := yard.get_node_or_null(sprite_path) as Sprite2D
		_expect(sprite != null, "missing runtime art sprite %s" % sprite_path)
		if _has_failed:
			return
		if sprite.has_method("refresh_texture"):
			sprite.refresh_texture()
		_expect(sprite.texture != null, "runtime art sprite should load texture: %s" % sprite_path)
		if _has_failed:
			return
		_expect(_asset_exists(String(checks[sprite_path])), "runtime art file missing for %s" % sprite_path)
		if _has_failed:
			return

	for marker_path in ["Mailbox/MailboxMarker", "Signboard/SignboardMarker"]:
		var marker := yard.get_node_or_null(marker_path) as CanvasItem
		_expect(marker != null and not marker.visible, "old marker should be hidden after art landing: %s" % marker_path)
		if _has_failed:
			return

	var ground := yard.get_node_or_null("Ground") as Polygon2D
	if ground == null:
		_fail("PlayerYard missing Ground")
		return
	var ground_rect := _polygon_global_rect(ground)
	for prop_path in ["Mailbox", "Signboard", "OldWell", "Bench"]:
		var prop_node := yard.get_node(prop_path) as Node2D
		_expect(ground_rect.has_point(prop_node.global_position), "%s should be inside Ground" % prop_path)
		if _has_failed:
			return

	print("OK: Godot validated Art Landing Pass 1 runtime props in PlayerYard")
	_finish_deferred(0)


func _polygon_global_rect(poly: Polygon2D) -> Rect2:
	var points := poly.polygon
	if points.is_empty():
		return Rect2(poly.global_position, Vector2.ZERO)
	var first := poly.to_global(points[0])
	var rect := Rect2(first, Vector2.ZERO)
	for point in points:
		rect = rect.expand(poly.to_global(point))
	return rect


func _asset_exists(path: String) -> bool:
	return ResourceLoader.exists(path) or FileAccess.file_exists(path)


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

func _finish_deferred(exit_code: int) -> void:
	if _finishing:
		return
	_finishing = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
