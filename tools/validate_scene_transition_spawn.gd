extends SceneTree

const EXPECTED_MAIN_SCENE := "res://scenes/world/world.tscn"
const WORLD_SCENE := "res://scenes/world/world.tscn"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var main_scene: String = ProjectSettings.get_setting("application/run/main_scene", "")
	if main_scene != EXPECTED_MAIN_SCENE:
		_fail("project main_scene is %s, expected %s" % [main_scene, EXPECTED_MAIN_SCENE])
		return

	var main_script := FileAccess.get_file_as_string("res://scripts/main.gd")
	if main_script.contains("res://scenes/regions/region_home_area.tscn"):
		_fail("scripts/main.gd still boots Region_HomeArea directly instead of world.tscn")
		return

	var packed := load(WORLD_SCENE) as PackedScene
	if packed == null:
		_fail("could not load %s" % WORLD_SCENE)
		return

	var world := packed.instantiate()
	root.add_child(world)
	current_scene = world

	await process_frame
	await process_frame

	var world_controller := current_scene as Node
	if world_controller == null or not world_controller.has_method("get_region_loader"):
		_fail("world scene root is not a WorldController")
		return

	var loader: Node = world_controller.call("get_region_loader")
	if loader == null:
		_fail("WorldController missing RegionLoader")
		return

	if not loader.call("is_region_loaded", "Region_HomeArea"):
		_fail("Region_HomeArea was not loaded at startup")
		return

	var player := world_controller.call("get_player") as Node2D
	if player == null:
		_fail("WorldController did not spawn a player")
		return

	var home_region := loader.call("get_region", "Region_HomeArea") as Node
	var home_exit := home_region.get_node_or_null("YSortWorld/Interactables/BackyardFarmEntrance")
	if home_exit == null:
		_fail("Region_HomeArea missing BackyardFarmEntrance")
		return
	if str(home_exit.get("target_region_id")) != "Region_BackFarm":
		_fail("BackyardFarmEntrance target_region_id is not Region_BackFarm")
		return
	if str(home_exit.get("target_spawn_id")) != "back_farm_from_home":
		_fail("BackyardFarmEntrance target_spawn_id is not back_farm_from_home")
		return

	home_exit.call("_reset")
	home_exit.call("on_interact", player)
	await process_frame
	await process_frame

	if not loader.call("is_region_loaded", "Region_BackFarm"):
		_fail("Region_BackFarm was not loaded after HomeArea exit")
		return
	if str(loader.call("get_current_region_id")) != "Region_BackFarm":
		_fail("current region after HomeArea exit is %s" % loader.call("get_current_region_id"))
		return

	var back_region := loader.call("get_region", "Region_BackFarm") as Node
	var back_spawn := _find_spawn_marker(back_region, "back_farm_from_home")
	if back_spawn == null:
		_fail("Region_BackFarm missing spawn_id=back_farm_from_home")
		return
	if player.global_position.distance_to(back_spawn.global_position) > 0.5:
		_fail("player did not land at back_farm_from_home: got %s expected %s" % [player.global_position, back_spawn.global_position])
		return

	var back_exit := back_region.get_node_or_null("YSortWorld/Interactables/ExitToHomeArea")
	if back_exit == null:
		_fail("Region_BackFarm missing ExitToHomeArea")
		return

	back_exit.call("_reset")
	back_exit.call("on_interact", player)
	await process_frame
	await process_frame

	if str(loader.call("get_current_region_id")) != "Region_HomeArea":
		_fail("current region after BackFarm return is %s" % loader.call("get_current_region_id"))
		return

	var home_spawn := _find_spawn_marker(home_region, "home_area_from_back_farm")
	if home_spawn == null:
		_fail("Region_HomeArea missing spawn_id=home_area_from_back_farm")
		return
	if player.global_position.distance_to(home_spawn.global_position) > 0.5:
		_fail("player did not land at home_area_from_back_farm: got %s expected %s" % [player.global_position, home_spawn.global_position])
		return

	print("OK: world entry and HomeArea/BackFarm transition spawn validated")
	quit(0)


func _find_spawn_marker(root_node: Node, spawn_id: String) -> Marker2D:
	if root_node == null:
		return null
	if root_node is Marker2D and str(root_node.get_meta("spawn_id", "")) == spawn_id:
		return root_node as Marker2D

	for child in root_node.get_children():
		var marker := _find_spawn_marker(child, spawn_id)
		if marker != null:
			return marker

	return null


func _fail(message: String) -> void:
	printerr("FAIL: %s" % message)
	quit(1)
