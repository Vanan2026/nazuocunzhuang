extends Node

const ACTIVE_WORLD_SCENE := preload("res://scenes/world/world.tscn")


func _ready() -> void:
	print("=== 閭ｅ骇鏉戝簞鍚姩 ===")

	var instance := ACTIVE_WORLD_SCENE.instantiate()
	add_child(instance)

	print("涓讳笘鐣屽凡鍔犺浇锛歐orld")
	print("WASD 绉诲姩 | E 浜や簰")
