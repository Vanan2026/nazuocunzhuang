class_name Interactable
extends Area2D

signal interacted(interactor: Node, interactable_id: String)

@export var interactable_id: String = ""
@export var display_name: String = ""
@export var interaction_hint: String = "按 E 查看"
@export_multiline var interaction_text: String = ""

var interaction_count: int = 0


func _ready() -> void:
	add_to_group("interactable")


func on_interact(interactor: Node) -> void:
	interaction_count += 1
	interacted.emit(interactor, interactable_id)
	if not interaction_text.is_empty():
		print("[%s] %s" % [display_name, interaction_text])


func get_interaction_hint() -> String:
	return interaction_hint
