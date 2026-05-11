extends Node

const ACTIVE_WORLD_SCENE := preload("res://scenes/regions/region_home_area.tscn")


func _ready() -> void:
	print("=== 那座村庄启动 ===")

	var instance := ACTIVE_WORLD_SCENE.instantiate()
	add_child(instance)

	print("主世界已加载：Region_HomeArea")
	print("WASD 移动 | E 交互")
