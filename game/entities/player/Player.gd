class_name Player
extends CharacterBody2D

signal interaction_started(target: Node)
signal nearest_interactable_changed(target: Node)

@export var move_speed: float = 140.0

@onready var interaction_area: Area2D = $InteractionArea

var facing_direction: Vector2 = Vector2.DOWN


func _ready() -> void:
	add_to_group("player")
	interaction_area.nearest_interactable_changed.connect(_on_nearest_interactable_changed)


func _physics_process(_delta: float) -> void:
	var input_vector := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if input_vector.length_squared() > 0.0:
		facing_direction = input_vector.normalized()
	velocity = input_vector * move_speed
	move_and_slide()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact"):
		try_interact()


func try_interact() -> void:
	var target: Node = interaction_area.get_nearest_interactable()
	if target == null:
		return
	interaction_started.emit(target)
	if target.has_method("on_interact"):
		target.on_interact(self)


func _on_nearest_interactable_changed(target: Node) -> void:
	nearest_interactable_changed.emit(target)
