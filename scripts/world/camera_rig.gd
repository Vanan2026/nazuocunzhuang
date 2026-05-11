extends Camera2D

@export var target_path: NodePath
@export var follow_speed: float = 6.0

@onready var target: Node2D = get_node_or_null(target_path) as Node2D


func _ready() -> void:
    if target != null:
        global_position = target.global_position


func _process(delta: float) -> void:
    if target == null:
        return

    var t := 1.0 - exp(-follow_speed * delta)
    global_position = global_position.lerp(target.global_position, t)
