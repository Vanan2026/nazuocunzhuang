extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")

const INVENTORY_SCENE_PATH := "res://game/scenes/ui/InventoryScreen.tscn"
const INVENTORY_MANAGER_SCRIPT := preload("res://game/autoload/InventoryManager.gd")
const DATA_REGISTRY_SCRIPT := preload("res://game/autoload/DataRegistry.gd")
const PAPER_PANEL_TEXTURE_PATH := "res://assets/ui/panels/ui_panel_paper_01.png"
const WATCHDOG_TIMEOUT_SECONDS := 15.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Greenfield P0 Inventory Screen runtime initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var data_registry := DATA_REGISTRY_SCRIPT.new()
	root.add_child(data_registry)
	await _settle()
	_expect(data_registry.load_all_data(), "DataRegistry should load item data")
	_expect(data_registry.validate_all_data(), "DataRegistry should validate item data")
	if _has_failed:
		return

	var inventory_manager := INVENTORY_MANAGER_SCRIPT.new()
	root.add_child(inventory_manager)
	inventory_manager.add_item("seed_turnip", 5)
	inventory_manager.add_item("wood", 9)
	inventory_manager.add_item("crop_turnip", 3)

	var scene := load(INVENTORY_SCENE_PATH) as PackedScene
	_expect(scene != null, "InventoryScreen scene should load")
	if _has_failed:
		return
	var inventory := scene.instantiate()
	_expect(inventory.visible == false, "InventoryScreen should be hidden by default")
	root.add_child(inventory)
	await _settle()
	inventory.call("bind_managers", inventory_manager, data_registry)
	inventory.call("refresh")
	await _settle()

	_validate_structure(inventory)
	if _has_failed:
		return
	_validate_catalog_grid(inventory)
	if _has_failed:
		return
	await _validate_selection_and_amount(inventory)
	if _has_failed:
		return
	await _validate_category_filter(inventory)
	if _has_failed:
		return

	print("OK: Greenfield P0 Inventory Screen runtime validation passed")
	_finish_deferred(0)


func _validate_structure(inventory: Node) -> void:
	var panel := inventory.get_node_or_null("Panel") as PanelContainer
	var tabs := inventory.get_node_or_null("Panel/Content/CategoryTabs") as HBoxContainer
	var grid := inventory.get_node_or_null("Panel/Content/MainRow/InventoryColumn/ItemGrid") as GridContainer
	var details := inventory.get_node_or_null("Panel/Content/MainRow/Details") as VBoxContainer
	_expect(panel != null, "InventoryScreen should include a panel")
	_expect(tabs != null, "InventoryScreen should include category tabs")
	_expect(grid != null, "InventoryScreen should include an item grid")
	_expect(details != null, "InventoryScreen should include a details column")
	if _has_failed:
		return
	_expect(_stylebox_texture_path(panel.get_theme_stylebox("panel")) == PAPER_PANEL_TEXTURE_PATH, "InventoryScreen panel should use paper texture")
	_expect(tabs.get_child_count() >= 7, "InventoryScreen should build all category tabs")


func _validate_catalog_grid(inventory: Node) -> void:
	var grid := inventory.get_node("Panel/Content/MainRow/InventoryColumn/ItemGrid") as GridContainer
	_expect(grid.get_child_count() >= 20, "InventoryScreen should build the data-driven item catalog")
	if _has_failed:
		return
	var found_icon := false
	for child in grid.get_children():
		var button := child as Button
		if button != null and button.icon != null:
			found_icon = true
			break
	_expect(found_icon, "InventoryScreen item buttons should load icons from item data")


func _validate_selection_and_amount(inventory: Node) -> void:
	inventory.call("select_item", "seed_turnip")
	await _settle()
	var name_label := inventory.get_node("Panel/Content/MainRow/Details/SelectedNameLabel") as Label
	var meta_label := inventory.get_node("Panel/Content/MainRow/Details/SelectedMetaLabel") as Label
	var amount_label := inventory.get_node("Panel/Content/MainRow/Details/AmountRow/AmountLabel") as Label
	_expect(name_label.text != "No item selected", "select_item should update selected item label")
	_expect(meta_label.text.contains("Owned: 5"), "select_item should show owned count")
	_expect(amount_label.text == "1", "selected amount should start at 1")
	inventory.call("increase_amount")
	await _settle()
	_expect(amount_label.text == "2", "increase_amount should update amount label")
	inventory.call("decrease_amount")
	await _settle()
	_expect(amount_label.text == "1", "decrease_amount should update amount label")


func _validate_category_filter(inventory: Node) -> void:
	var grid := inventory.get_node("Panel/Content/MainRow/InventoryColumn/ItemGrid") as GridContainer
	var all_count := grid.get_child_count()
	inventory.call("set_active_category", "seed")
	await _settle()
	var seed_count := grid.get_child_count()
	_expect(seed_count > 0, "seed category should show seed records")
	_expect(seed_count < all_count, "seed category should filter the all-item catalog")


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
			_fail("Greenfield P0 Inventory Screen validation timed out")
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
