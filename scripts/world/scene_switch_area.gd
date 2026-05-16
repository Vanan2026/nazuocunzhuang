extends Area2D

@export var target_scene: String = ""
@export var interaction_hint: String = "E 键进入/切换场景"


func _ready() -> void:
	add_to_group("interactable")


func on_interact(_interactor: Node) -> void:
	if target_scene.is_empty():
		push_warning("Scene switch target_scene is not set.")
		return
	get_tree().call_deferred("change_scene_to_file", target_scene)


func get_interaction_hint() -> String:
	return interaction_hint
