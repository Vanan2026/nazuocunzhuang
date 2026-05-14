extends Node2D

var is_swaying: bool = false


func _ready() -> void:
    add_to_group("interactable")


func interact(_interactor: Node) -> void:
    print("[Windchime] sway")
    sway_windchime()


func sway_windchime() -> void:
    if is_swaying:
        return
    is_swaying = true

    var tween := create_tween()
    tween.tween_property(self, "rotation_degrees", 15.0, 0.15).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_SINE)
    tween.tween_property(self, "rotation_degrees", -15.0, 0.3).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)
    tween.tween_property(self, "rotation_degrees", 8.0, 0.2).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)
    tween.tween_property(self, "rotation_degrees", -5.0, 0.15).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)
    tween.tween_property(self, "rotation_degrees", 0.0, 0.1).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_SINE)
    tween.tween_callback(func(): is_swaying = false)
