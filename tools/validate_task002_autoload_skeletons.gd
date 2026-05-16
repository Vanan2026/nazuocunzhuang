extends SceneTree

const SCRIPT_PATHS: Array[String] = [
	"res://game/autoload/GameState.gd",
	"res://game/autoload/EventBus.gd",
	"res://game/autoload/TimeManager.gd",
	"res://game/autoload/SeasonManager.gd",
	"res://game/autoload/WeatherManager.gd",
	"res://game/autoload/DataRegistry.gd",
	"res://game/autoload/InventoryManager.gd",
	"res://game/autoload/RelationshipManager.gd",
	"res://game/autoload/QuestManager.gd",
	"res://game/autoload/DialogueManager.gd",
	"res://game/autoload/SaveManager.gd",
	"res://game/autoload/SceneRouter.gd",
]


func _initialize() -> void:
	for script_path in SCRIPT_PATHS:
		var script_resource: Script = load(script_path) as Script
		if script_resource == null:
			_fail("could not load %s" % script_path)
			return
		var instance: Object = script_resource.new()
		if not instance is Node:
			_fail("%s does not instantiate as Node" % script_path)
			return
		instance.free()
	print("OK: Godot loaded and instantiated %d Task 002 autoload skeletons" % SCRIPT_PATHS.size())
	quit(0)


func _fail(message: String) -> void:
	push_error(message)
	print("FAIL: %s" % message)
	quit(1)
