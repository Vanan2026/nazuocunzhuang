extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")

const DATA_REGISTRY_PATH := "res://game/autoload/DataRegistry.gd"
const MAP_SCREEN_PATH := "res://game/scenes/ui/MapScreen.tscn"
const PAPER_PANEL_TEXTURE_PATH := "res://assets/ui/panels/ui_panel_paper_01.png"
const WATCHDOG_TIMEOUT_SECONDS := 15.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Greenfield P0 Map Screen runtime initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var registry := _new_node(DATA_REGISTRY_PATH) as Node
	root.add_child(registry)
	_expect(registry.load_all_data(), "DataRegistry should load maps data")
	_expect(registry.validate_all_data(), "DataRegistry should validate maps data")
	if _has_failed:
		return
	_expect(int(registry.get("maps").size()) >= 10, "DataRegistry should expose at least 10 map records")

	var scene := load(MAP_SCREEN_PATH) as PackedScene
	_expect(scene != null, "MapScreen scene should load")
	if _has_failed:
		return
	var map_screen := scene.instantiate()
	root.add_child(map_screen)
	map_screen.call("bind_managers", registry, null)
	await _settle()

	_validate_initial_structure(map_screen)
	if _has_failed:
		return
	await _validate_open_and_data_generation(map_screen)
	if _has_failed:
		return
	await _validate_selection(map_screen)
	if _has_failed:
		return
	await _validate_close(map_screen)
	if _has_failed:
		return

	print("OK: Greenfield P0 Map Screen runtime validation passed")
	_finish_deferred(0)


func _validate_initial_structure(map_screen: Node) -> void:
	_expect(map_screen.visible == false, "MapScreen should be hidden by default")
	var panel := map_screen.get_node_or_null("Panel") as PanelContainer
	var map_texture := map_screen.get_node_or_null("Panel/Content/MainRow/MapPanel/MapTexture") as TextureRect
	var pins := map_screen.get_node_or_null("Panel/Content/MainRow/MapPanel/Pins") as Control
	var location_list := map_screen.get_node_or_null("Panel/Content/MainRow/LocationList") as VBoxContainer
	var details := map_screen.get_node_or_null("Panel/Content/MainRow/Details") as VBoxContainer
	_expect(panel != null, "MapScreen should include root panel")
	_expect(map_texture != null, "MapScreen should include paper map texture")
	_expect(pins != null, "MapScreen should include pins layer")
	_expect(location_list != null, "MapScreen should include location list")
	_expect(details != null, "MapScreen should include details panel")
	if _has_failed:
		return
	_expect(_stylebox_texture_path(panel.get_theme_stylebox("panel")) == PAPER_PANEL_TEXTURE_PATH, "MapScreen panel should use paper texture")
	_expect(map_texture.texture != null, "MapScreen should load the map background texture")


func _validate_open_and_data_generation(map_screen: Node) -> void:
	map_screen.call("open_map")
	await _settle()
	_expect(map_screen.visible, "open_map should show MapScreen")
	var pins := map_screen.get_node("Panel/Content/MainRow/MapPanel/Pins") as Control
	var location_list := map_screen.get_node("Panel/Content/MainRow/LocationList") as VBoxContainer
	_expect(pins.get_child_count() >= 10, "MapScreen should build numbered pins from maps.json")
	_expect(location_list.get_child_count() >= 10, "MapScreen should build location list from maps.json")
	if _has_failed:
		return
	var first_pin := pins.get_child(0) as Button
	var first_row := location_list.get_child(0) as Button
	_expect(first_pin != null and first_pin.text == "1", "first map pin should show location number")
	_expect(first_row != null and first_row.text.contains("Home Area"), "first location row should show data-driven name")


func _validate_selection(map_screen: Node) -> void:
	_expect(bool(map_screen.call("select_location", "riverside_path")), "select_location should accept data map id")
	await _settle()
	var number_label := map_screen.get_node("Panel/Content/MainRow/Details/SelectedNumberLabel") as Label
	var name_label := map_screen.get_node("Panel/Content/MainRow/Details/SelectedNameLabel") as Label
	var state_label := map_screen.get_node("Panel/Content/MainRow/Details/SelectedStateLabel") as Label
	var hint_label := map_screen.get_node("Panel/Content/MainRow/Details/SelectedHintLabel") as Label
	_expect(number_label.text.contains("06"), "selection should update location number")
	_expect(name_label.text == "Riverside Path", "selection should update location name")
	_expect(state_label.text.contains("Locked"), "selection should show locked state from data")
	_expect(hint_label.text.contains("Restore"), "selection should show travel hint from data")


func _validate_close(map_screen: Node) -> void:
	map_screen.call("close_map")
	await _settle()
	_expect(not map_screen.visible, "close_map should hide MapScreen")


func _new_node(script_path: String) -> Node:
	var script_resource := load(script_path) as Script
	_expect(script_resource != null, "%s should load" % script_path)
	if script_resource == null:
		return null
	var node := script_resource.new() as Node
	_expect(node != null, "%s should instantiate as Node" % script_path)
	return node


func _stylebox_texture_path(stylebox: StyleBox) -> String:
	var texture_box := stylebox as StyleBoxTexture
	if texture_box == null or texture_box.texture == null:
		return ""
	return String(texture_box.texture.resource_path)


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
			_fail("Greenfield P0 Map Screen validation timed out")
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
