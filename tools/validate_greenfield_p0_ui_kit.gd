extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")

const PAPER_PANEL_TEXTURE_PATH := "res://assets/ui/panels/ui_panel_paper_01.png"
const BUTTON_TEXTURE_PATH := "res://assets/ui/buttons/ui_button_normal.png"
const SLOT_TEXTURE_PATH := "res://assets/ui/slots/ui_slot_item.png"
const SLOT_SELECTED_TEXTURE_PATH := "res://assets/ui/slots/ui_slot_selected.png"
const TAB_TEXTURE_PATH := "res://assets/ui/tabs/ui_tab_normal.png"

const COMPONENT_SCENES := [
	"res://ui/components/GFPanel.tscn",
	"res://ui/components/GFButton.tscn",
	"res://ui/components/GFItemSlot.tscn",
	"res://ui/components/GFTabBar.tscn",
]
const INVENTORY_SCENE_PATH := "res://game/scenes/ui/InventoryUI.tscn"

const WATCHDOG_TIMEOUT_SECONDS := 15.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Greenfield P0 UI kit runtime initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	await _validate_components()
	if _has_failed:
		return
	await _validate_inventory_scene()
	if _has_failed:
		return
	print("OK: Greenfield P0 UI kit runtime validation passed")
	_finish_deferred(0)


func _validate_components() -> void:
	for scene_path in COMPONENT_SCENES:
		var scene := load(scene_path) as PackedScene
		_expect(scene != null, "%s should load" % scene_path)
		if _has_failed:
			return
		var node := scene.instantiate()
		root.add_child(node)
		await _settle()
		if node is PanelContainer:
			_expect(_stylebox_texture_path(node.get_theme_stylebox("panel")) == PAPER_PANEL_TEXTURE_PATH, "GFPanel should use the paper panel texture")
		elif node is Button:
			var button := node as Button
			if scene_path.ends_with("GFItemSlot.tscn"):
				if button.has_method("set_item"):
					button.call("set_item", "turnip_seed", "Turnip Seed", 3, true)
					await _settle()
				_expect(_button_texture_path(button, "normal") == SLOT_SELECTED_TEXTURE_PATH, "GFItemSlot should use the selected slot texture when selected")
			else:
				_expect(_button_texture_path(button, "normal") == BUTTON_TEXTURE_PATH, "GFButton should use the Greenfield button texture")
		elif node is HBoxContainer:
			if node.has_method("configure_tabs"):
				node.call("configure_tabs", [{"id": "bag", "label": "Bag"}, {"id": "map", "label": "Map"}], "bag")
				await _settle()
			_expect(node.get_child_count() == 2, "GFTabBar should build tab buttons")
			if _has_failed:
				node.queue_free()
				return
			var second_tab := node.get_child(1) as Button
			_expect(second_tab != null, "GFTabBar second child should be a Button")
			if second_tab != null:
				_expect(_button_texture_path(second_tab, "normal") == TAB_TEXTURE_PATH, "inactive GFTabBar tab should use tab texture")
		node.queue_free()


func _validate_inventory_scene() -> void:
	var scene := load(INVENTORY_SCENE_PATH) as PackedScene
	_expect(scene != null, "InventoryUI scene should load")
	if _has_failed:
		return
	var inventory := scene.instantiate()
	root.add_child(inventory)
	await _settle()
	inventory.call("refresh")
	await _settle()

	var panel := inventory.get_node_or_null("Panel") as PanelContainer
	var category_tabs := inventory.get_node_or_null("Panel/Content/CategoryTabs") as HBoxContainer
	var item_grid := inventory.get_node_or_null("Panel/Content/MainRow/InventoryColumn/ItemGrid") as GridContainer
	var selected_name_label := inventory.get_node_or_null("Panel/Content/MainRow/Details/SelectedNameLabel") as Label
	var clear_button := inventory.get_node_or_null("Panel/Content/MainRow/Details/ActionRow/ClearButton") as Button
	_expect(panel != null, "InventoryUI should include a panel")
	_expect(category_tabs != null, "InventoryUI should include category tabs")
	_expect(item_grid != null, "InventoryUI should include an item grid")
	_expect(selected_name_label != null, "InventoryUI should include a selected-name label")
	_expect(clear_button != null, "InventoryUI should include a clear button")
	if _has_failed:
		inventory.queue_free()
		return
	_expect(_stylebox_texture_path(panel.get_theme_stylebox("panel")) == PAPER_PANEL_TEXTURE_PATH, "InventoryUI panel should use the paper panel texture")
	_expect(category_tabs.get_child_count() >= 6, "InventoryUI should build Greenfield category tabs")
	_expect(selected_name_label.text == "No item selected", "InventoryUI should show the empty selection state")
	if clear_button != null:
		_expect(_button_texture_path(clear_button, "normal") == BUTTON_TEXTURE_PATH, "InventoryUI clear button should use Greenfield button texture")
	inventory.queue_free()


func _stylebox_texture_path(stylebox: StyleBox) -> String:
	var texture_box := stylebox as StyleBoxTexture
	if texture_box == null or texture_box.texture == null:
		return ""
	return String(texture_box.texture.resource_path)


func _button_texture_path(button: Button, state: StringName) -> String:
	return _stylebox_texture_path(button.get_theme_stylebox(state))


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
			_fail("Greenfield P0 UI kit validation timed out")
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
