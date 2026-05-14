extends Node2D

func _ready() -> void:
    pass

func interact(interactor: Node) -> void:
    print('[水井] 玩家正在打水...')
    var tween = create_tween()
    tween.tween_interval(0.3)
    tween.tween_callback(print.bind('[水井] 打好了一桶水'))