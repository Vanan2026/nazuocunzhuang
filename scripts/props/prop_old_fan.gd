extends Node2D

var is_running: bool = false
var rotation_speed: float = 720.0

func _ready() -> void:
    add_to_group("interactable")

func interact(interactor: Node) -> void:
    print('[电扇] 打开电扇，凉风习习')
    toggle_fan()

func toggle_fan() -> void:
    is_running = not is_running
    if is_running:
        start_rotation()
    else:
        stop_rotation()

func start_rotation() -> void:
    var fan_blades = get_node_or_null("FanBlades")
    if fan_blades:
        var tween = create_tween().set_loops()
        tween.tween_property(fan_blades, "rotation", TAU, 0.5).set_ease(Tween.EASE_LINEAR).set_trans(Tween.TRANS_LINEAR)

func stop_rotation() -> void:
    var tween = get_tree().create_tween()
    tween.kill()