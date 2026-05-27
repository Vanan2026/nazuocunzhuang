extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const HOME_AREA_SCENE := "res://game/scenes/world/HomeArea.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 18.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Greenfield P0 HomeArea runtime initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var packed := load(HOME_AREA_SCENE) as PackedScene
	_expect(packed != null, "HomeArea scene should load")
	if _has_failed:
		return
	var home_area := packed.instantiate()
	root.add_child(home_area)
	await _settle()

	_expect(home_area.name == "HomeArea", "HomeArea root should be named HomeArea")
	_expect(home_area.get_node_or_null("BaseLayer") is Node2D, "HomeArea should include BaseLayer")
	_expect(home_area.get_node_or_null("BaseLayer/BaseSprite") is Sprite2D, "HomeArea should include BaseSprite under BaseLayer")
	_expect(home_area.get_node_or_null("YSortObjects") is Node2D, "HomeArea should include YSortObjects")
	_expect(home_area.get_node_or_null("ForegroundOcclusion") is Sprite2D, "HomeArea should include ForegroundOcclusion")
	_expect(home_area.get_node_or_null("CollisionLayer") is StaticBody2D, "HomeArea should include CollisionLayer")
	_expect(home_area.get_node_or_null("InteractionPoints") is Node2D, "HomeArea should include InteractionPoints")
	_expect(home_area.get_node_or_null("NavigationRegion2D") is NavigationRegion2D, "HomeArea should include NavigationRegion2D")
	_expect(home_area.get_node_or_null("PlayerSpawnPoint") is Marker2D, "HomeArea should include PlayerSpawnPoint")
	_expect(home_area.get_node_or_null("YSortObjects/Player") != null, "HomeArea should include a player under YSortObjects")
	if _has_failed:
		home_area.queue_free()
		return

	var foreground := home_area.get_node("ForegroundOcclusion") as Sprite2D
	var base := home_area.get_node("BaseLayer/BaseSprite") as Sprite2D
	_expect(base.texture != null and base.texture.get_size() == Vector2(1920, 1080), "BaseSprite should use the full-canvas base texture")
	_expect(foreground.texture != null and foreground.texture.get_size() == Vector2(1920, 1080), "ForegroundOcclusion should use the full-canvas foreground texture")
	_expect(foreground.z_index > base.z_index, "ForegroundOcclusion should render above the base")

	var collision_layer := home_area.get_node("CollisionLayer") as StaticBody2D
	_expect(collision_layer.get_child_count() >= 7, "CollisionLayer should contain house/well/tree/fence blockers")

	var interaction_points := home_area.get_node("InteractionPoints") as Node2D
	var required := {
		"home_door": false,
		"old_well": false,
		"mailbox": false,
		"farm_plot_cluster": false,
	}
	for child in interaction_points.get_children():
		if child is Area2D and child.is_in_group("interactable"):
			var interactable_id := String(child.get("interactable_id"))
			if required.has(interactable_id):
				required[interactable_id] = true
			_expect(child.get_child_count() > 0, "%s should have a collision shape" % child.name)
			_expect(child.has_method("get_interaction_hint"), "%s should expose interaction hints" % child.name)
	for id in required.keys():
		_expect(bool(required[id]), "HomeArea missing interaction point: %s" % id)

	if home_area.has_method("load_interaction_points_data"):
		var data: Dictionary = home_area.load_interaction_points_data()
		_expect(not data.is_empty(), "HomeArea should load interaction point data")
		_expect(String(data.get("coordinate_space", "")) == "shared_full_canvas_origin_top_left", "HomeArea interaction data should use shared canvas coordinates")
	else:
		_fail("HomeArea script should expose load_interaction_points_data")

	home_area.queue_free()
	print("OK: Greenfield P0 HomeArea runtime validation passed")
	_finish_deferred(0)


func _settle() -> void:
	await create_timer(0.05).timeout
	await process_frame
	await process_frame


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
			_fail("Greenfield P0 HomeArea runtime validation timed out")
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
