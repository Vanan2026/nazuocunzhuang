extends Node

const ACTIVE_WORLD_SCENE := preload("res://scenes/world/world.tscn")


func _ready() -> void:
	print("=== 那座村庄启动 ===")

	var instance := ACTIVE_WORLD_SCENE.instantiate()
	add_child(instance)

	print("主世界已加载：World")
	print("WASD 移动 | E 交互")
