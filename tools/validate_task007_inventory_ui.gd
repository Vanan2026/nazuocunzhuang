extends SceneTree

const DATA_REGISTRY_PATH := "res://game/autoload/DataRegistry.gd"
const INVENTORY_MANAGER_PATH := "res://game/autoload/InventoryManager.gd"
const INVENTORY_UI_PATH := "res://game/scenes/ui/InventoryUI.tscn"
const FARM_PLOT_PATH := "res://game/systems/farming/FarmPlot.tscn"
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"

var _has_failed := false


func _initialize() -> void:
	var data_registry := _new_node(DATA_REGISTRY_PATH)
	var inventory_manager := _new_node(INVENTORY_MANAGER_PATH)
	if _has_failed:
		return
	root.add_child(data_registry)
	root.add_child(inventory_manager)
	data_registry.load_all_data()
	data_registry.validate_all_data()
	inventory_manager.add_item("seed_turnip", 3)
	inventory_manager.add_item("crop_turnip", 2)

	_expect(inventory_manager.has_item("seed_turnip", 3), "inventory should count seed_turnip")
	if _has_failed:
		return
	_expect(inventory_manager.get_items_by_category("seed").has("seed_turnip"), "seed category snapshot should include seed_turnip")
	if _has_failed:
		return
	inventory_manager.set_selected_item("seed_turnip")
	_expect(inventory_manager.get_selected_item_id() == "seed_turnip", "selected item should be seed_turnip")
	if _has_failed:
		return

	var ui_scene: PackedScene = load(INVENTORY_UI_PATH) as PackedScene
	if ui_scene == null:
		_fail("could not load InventoryUI")
		return
	var inventory_ui: Node = ui_scene.instantiate()
	root.add_child(inventory_ui)
	inventory_ui.inventory_manager_path = inventory_ui.get_path_to(inventory_manager)
	inventory_ui.data_registry_path = inventory_ui.get_path_to(data_registry)
	inventory_ui.bind_managers(inventory_manager, data_registry)
	inventory_ui.refresh()

	var selected_name := inventory_ui.get_node_or_null("Panel/Content/Details/SelectedNameLabel")
	var selected_description := inventory_ui.get_node_or_null("Panel/Content/Details/SelectedDescriptionLabel")
	var seed_count := inventory_ui.get_node_or_null("Panel/Content/Summary/SeedCountLabel")
	var crop_count := inventory_ui.get_node_or_null("Panel/Content/Summary/CropCountLabel")
	if selected_name == null or selected_description == null or seed_count == null or crop_count == null:
		_fail("InventoryUI missing expected labels")
		return
	_expect(String(selected_name.text).contains("春萝卜种子"), "selected item name should display")
	if _has_failed:
		return
	_expect(String(selected_description.text).contains("适合春天"), "selected item description should display")
	if _has_failed:
		return
	_expect(String(seed_count.text).contains("3"), "seed count should display")
	if _has_failed:
		return
	_expect(String(crop_count.text).contains("2"), "crop count should display")
	if _has_failed:
		return

	var plot_scene: PackedScene = load(FARM_PLOT_PATH) as PackedScene
	if plot_scene == null:
		_fail("could not load FarmPlot")
		return
	var plot: Node = plot_scene.instantiate()
	root.add_child(plot)
	plot.data_registry_path = plot.get_path_to(data_registry)
	plot.inventory_manager_path = plot.get_path_to(inventory_manager)
	plot.till()
	_expect(inventory_ui.use_selected_on(plot), "InventoryUI should plant selected seed on FarmPlot")
	if _has_failed:
		return
	_expect(plot.get_state_name() == "planted", "FarmPlot should be planted after using selected seed")
	if _has_failed:
		return
	_expect(inventory_manager.get_count("seed_turnip") == 2, "using selected seed should consume one seed")
	if _has_failed:
		return

	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	if yard_scene == null:
		_fail("could not load PlayerYard")
		return
	var yard: Node = yard_scene.instantiate()
	root.add_child(yard)
	var yard_ui := yard.get_node_or_null("InventoryUI")
	if yard_ui == null:
		_fail("PlayerYard missing InventoryUI")
		return
	if not yard_ui.has_method("use_selected_on"):
		_fail("PlayerYard InventoryUI missing use_selected_on")
		return
	var yard_inventory := yard.get_node_or_null("InventoryManager")
	var yard_registry := yard.get_node_or_null("DataRegistry")
	if yard_inventory == null or yard_registry == null:
		_fail("PlayerYard missing inventory/data managers")
		return
	yard_registry.load_all_data()
	yard_inventory.add_item("seed_turnip", 1)
	yard_inventory.set_selected_item("seed_turnip")
	yard_ui.bind_managers(yard_inventory, yard_registry)
	yard_ui.refresh()
	var yard_plot := yard.get_node_or_null("FarmPlots/FarmPlot0")
	yard_plot.till()
	_expect(yard_ui.use_selected_on(yard_plot), "PlayerYard InventoryUI should plant selected seed on plot")
	if _has_failed:
		return

	print("OK: Godot validated Task 007 inventory UI and selected seed FarmPlot flow")
	quit(0)


func _new_node(script_path: String) -> Node:
	var script_resource: Script = load(script_path) as Script
	if script_resource == null:
		_fail("could not load %s" % script_path)
		return null
	var node := script_resource.new() as Node
	if node == null:
		_fail("%s did not instantiate as Node" % script_path)
	return node


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
