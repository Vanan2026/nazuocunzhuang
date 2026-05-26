extends SceneTree

const DATA_REGISTRY_PATH := "res://game/autoload/DataRegistry.gd"


func _initialize() -> void:
	var script_resource: Script = load(DATA_REGISTRY_PATH) as Script
	if script_resource == null:
		_fail("could not load %s" % DATA_REGISTRY_PATH)
		return

	var registry: Node = script_resource.new() as Node
	if registry == null:
		_fail("DataRegistry does not instantiate as Node")
		return
	root.add_child(registry)

	if not registry.load_all_data():
		_fail("load_all_data returned false")
		return
	if not registry.validate_all_data():
		_fail("validate_all_data returned false")
		return

	_expect(registry.get_item("seed_turnip").get("name", "") == "春萝卜种子", "seed_turnip item did not load")
	_expect(registry.get_crop("turnip_spring").get("harvest_item_id", "") == "crop_turnip", "turnip_spring crop did not load")
	_expect(registry.get_npc("aoi").get("role", "") == "杂货店店主", "aoi npc did not load")
	_expect(registry.get_recipe("persimmon_riceball").get("result", {}).get("item_id", "") == "food_persimmon_riceball", "persimmon_riceball recipe did not load")
	_expect(registry.get_dialogue("aoi_daily_spring_01").get("npc_id", "") == "aoi", "aoi dialogue did not load")
	_expect(registry.get_npc_schedule("shopkeeper_basic").get("schedule_id", "") == "shopkeeper_basic", "shopkeeper_basic schedule did not load")
	_expect(registry.get_restoration("old_well").get("required_money", -1) == 500, "old_well restoration did not load")

	print("OK: Godot loaded and validated Task 003 DataRegistry")
	quit(0)


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	push_error(message)
	print("FAIL: %s" % message)
	quit(1)
