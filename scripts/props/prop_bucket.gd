extends Node2D

func _ready() -> void:
    add_to_group("interactable")

func interact(interactor: Node) -> void:
    print('[木桶] 木桶里有清凉的底水')
    var tween = create_tween()
    tween.tween_property(self, "position:y", position.y - 5, 0.1)
    tween.tween_property(self, "position:y", position.y, 0.1)