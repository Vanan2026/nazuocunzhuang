extends SceneTree

const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"

var _has_failed := false


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

	_expect(yard.has_method("advance_farm_plots_for_new_day"), "PlayerYard missing day-advance controller method")
	if _has_failed:
		return
	_expect(yard.has_method("refresh_runtime_ui"), "PlayerYard missing UI refresh method")
	if _has_failed:
		return

	var inventory := yard.get_node_or_null("InventoryManager")
	var registry := yard.get_node_or_null("DataRegistry")
	var weather := yard.get_node_or_null("WeatherManager")
	var bed := yard.get_node_or_null("Bed")
	var inventory_ui := yard.get_node_or_null("InventoryUI")
	var time_hud := yard.get_node_or_null("TimeWeatherHUD")
	var farm_plots := yard.get_node_or_null("FarmPlots")
	var player := yard.get_node_or_null("Player")
	var camera := yard.get_node_or_null("WorldCamera") as Camera2D
	if inventory == null or registry == null or weather == null or bed == null or inventory_ui == null or time_hud == null or farm_plots == null or player == null or camera == null:
		_fail("PlayerYard missing one or more runtime nodes")
		return
	_expect(camera.enabled, "PlayerYard WorldCamera should be enabled for visual checks")
	if _has_failed:
		return

	_expect(inventory.get_count("seed_turnip") >= 3, "PlayerYard should start with starter turnip seeds")
	if _has_failed:
		return
	_expect(inventory.get_selected_item_id() == "seed_turnip", "PlayerYard should preselect seed_turnip")
	if _has_failed:
		return

	var hud_panel := time_hud.get_node_or_null("Panel") as Control
	var inventory_panel := inventory_ui.get_node_or_null("Panel") as Control
	if hud_panel == null or inventory_panel == null:
		_fail("HUD or InventoryUI missing Panel")
		return
	_expect(not hud_panel.get_global_rect().intersects(inventory_panel.get_global_rect()), "HUD and InventoryUI panels should not overlap")
	if _has_failed:
		return

	var ground := yard.get_node_or_null("Ground") as Polygon2D
	if ground == null:
		_fail("PlayerYard missing Ground")
		return
	var ground_rect := _polygon_global_rect(ground)
	for index in range(6):
		var plot := farm_plots.get_node_or_null("FarmPlot%d" % index)
		if plot == null:
			_fail("missing FarmPlot%d" % index)
			return
		var plot_rect := _collision_global_rect(plot)
		_expect(ground_rect.encloses(plot_rect), "FarmPlot%d should fit inside Ground" % index)
		if _has_failed:
			return

	var plot0 := farm_plots.get_node("FarmPlot0")
	player.global_position = plot0.global_position + Vector2(0, -18)
	await physics_frame
	await physics_frame
	player.try_interact()
	await process_frame
	_expect(plot0.get_state_name() == "tilled", "player interaction should till nearby FarmPlot0")
	if _has_failed:
		return
	player.try_interact()
	await process_frame
	_expect(plot0.get_state_name() == "planted", "player interaction should plant selected seed on tilled FarmPlot0")
	if _has_failed:
		return
	player.try_interact()
	await process_frame
	_expect(plot0.get_state_name() == "watered", "player interaction should water planted FarmPlot0")
	if _has_failed:
		return

	weather.set_tomorrow_weather("rainy")
	bed.on_interact(player)
	await process_frame
	_expect(plot0.growth_days == 1, "bed sleep should advance FarmPlot0 growth with rainy auto-water")
	if _has_failed:
		return
	_expect(String(inventory_ui.get_node("Panel/Content/Summary/SeedCountLabel").text).contains(str(inventory.get_count("seed_turnip"))), "InventoryUI seed count should refresh")
	if _has_failed:
		return

	print("OK: Task 007.5 tail completion gate passed for PlayerYard integration and layout")
	quit(0)


func _polygon_global_rect(poly: Polygon2D) -> Rect2:
	var points := poly.polygon
	if points.is_empty():
		return Rect2(poly.global_position, Vector2.ZERO)
	var first := poly.to_global(points[0])
	var rect := Rect2(first, Vector2.ZERO)
	for point in points:
		rect = rect.expand(poly.to_global(point))
	return rect


func _collision_global_rect(node: Node) -> Rect2:
	var shape_node := node.get_node_or_null("CollisionShape2D") as CollisionShape2D
	if shape_node == null or shape_node.shape == null:
		return Rect2((node as Node2D).global_position, Vector2.ZERO)
	var rect := shape_node.shape.get_rect()
	rect.position += shape_node.global_position
	return rect


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	quit(1)
