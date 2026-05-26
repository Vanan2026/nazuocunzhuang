extends SceneTree

const FARM_PLOT_SCENE_PATH := "res://game/systems/farming/FarmPlot.tscn"
const DATA_REGISTRY_PATH := "res://game/autoload/DataRegistry.gd"
const INVENTORY_MANAGER_PATH := "res://game/autoload/InventoryManager.gd"
const WEATHER_MANAGER_PATH := "res://game/autoload/WeatherManager.gd"
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"

var _has_failed := false


func _initialize() -> void:
	var data_registry := _new_node(DATA_REGISTRY_PATH)
	var inventory_manager := _new_node(INVENTORY_MANAGER_PATH)
	var weather_manager := _new_node(WEATHER_MANAGER_PATH)
	if _has_failed:
		return
	root.add_child(data_registry)
	root.add_child(inventory_manager)
	root.add_child(weather_manager)
	data_registry.load_all_data()
	data_registry.validate_all_data()
	inventory_manager.add_item("seed_turnip", 2)

	var farm_plot_scene: PackedScene = load(FARM_PLOT_SCENE_PATH) as PackedScene
	if farm_plot_scene == null:
		_fail("could not load FarmPlot.tscn")
		return
	var plot: Node = farm_plot_scene.instantiate()
	root.add_child(plot)
	plot.data_registry_path = plot.get_path_to(data_registry)
	plot.inventory_manager_path = plot.get_path_to(inventory_manager)
	plot.weather_manager_path = plot.get_path_to(weather_manager)

	_expect(plot.get_state_name() == "empty", "plot should start empty")
	if _has_failed:
		return
	_expect(plot.till(), "till should succeed from empty")
	if _has_failed:
		return
	_expect(plot.get_state_name() == "tilled", "tilled state expected")
	if _has_failed:
		return
	_expect(plot.plant_seed("seed_turnip"), "plant_seed should consume seed_turnip")
	if _has_failed:
		return
	_expect(inventory_manager.get_count("seed_turnip") == 1, "planting should remove one seed")
	if _has_failed:
		return
	_expect(plot.get_state_name() == "planted", "planted state expected")
	if _has_failed:
		return
	_expect(plot.water(), "water should succeed after planting")
	if _has_failed:
		return
	_expect(plot.get_state_name() == "watered", "watered state expected")
	if _has_failed:
		return

	for _i in range(2):
		plot.advance_day(false)
		if plot.get_state_name() != "ready":
			plot.water()
	_expect(plot.get_state_name() == "ready", "turnip should become ready after 2 watered days")
	if _has_failed:
		return
	_expect(plot.harvest(), "harvest should succeed when ready")
	if _has_failed:
		return
	_expect(inventory_manager.get_count("crop_turnip") == 1, "harvest should add crop_turnip")
	if _has_failed:
		return
	_expect(plot.get_state_name() == "empty", "non-regrow crop should reset to empty after harvest")
	if _has_failed:
		return

	inventory_manager.add_item("seed_turnip", 1)
	plot.till()
	plot.plant_seed("seed_turnip")
	weather_manager.set_today_weather("rainy")
	plot.advance_day(weather_manager.should_auto_water_today())
	_expect(plot.growth_days == 1, "rainy auto-water should advance growth")
	if _has_failed:
		return

	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	if yard_scene == null:
		_fail("could not load PlayerYard")
		return
	var yard: Node = yard_scene.instantiate()
	root.add_child(yard)
	var farm_plots := yard.get_node_or_null("FarmPlots")
	if farm_plots == null:
		_fail("PlayerYard missing FarmPlots")
		return
	_expect(farm_plots.get_child_count() == 6, "PlayerYard should contain 6 farm plots")
	if _has_failed:
		return
	for index in range(6):
		var child := farm_plots.get_node_or_null("FarmPlot%d" % index)
		if child == null:
			_fail("missing FarmPlot%d" % index)
			return
		_expect(child.get("plot_index") == index, "FarmPlot%d has wrong plot_index" % index)
		if _has_failed:
			return
		_expect(child.has_method("advance_day"), "FarmPlot%d missing advance_day" % index)
		if _has_failed:
			return

	print("OK: Godot validated Task 006 farm plots, growth, auto-water, and harvest")
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
