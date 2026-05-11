extends Node2D

var is_sliced: bool = false

func _ready() -> void:
    add_to_group("interactable")

func interact(interactor: Node) -> void:
    if is_sliced:
        print('[西瓜] 西瓜已经被切开了')
        return
    print('[西瓜] 切开西瓜！红红的果肉看起来很甜')
    is_sliced = true
    slice_watermelon()

func slice_watermelon() -> void:
    var tween = create_tween()
    tween.tween_property(self, "scale", Vector2(1.2, 0.8), 0.2).set_ease(Tween.EASE_OUT)
    tween.tween_callback(print.bind('[西瓜] 获得西瓜片！'))