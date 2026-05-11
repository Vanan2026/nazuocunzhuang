extends Area2D

@export var interaction_hint: String = "按 E 坐下休息"
@export var seat_anchor: Vector2 = Vector2(930, 548)
@export var rest_facing: Vector2 = Vector2.RIGHT


func _ready() -> void:
    add_to_group("interactable")
    if not body_entered.is_connected(_on_body_entered):
        body_entered.connect(_on_body_entered)
    if not body_exited.is_connected(_on_body_exited):
        body_exited.connect(_on_body_exited)
    _show_hint(false)


func on_interact(interactor: Node) -> void:
    if interactor.has_method("is_resting") and interactor.is_resting():
        if interactor.has_method("end_meditation"):
            interactor.end_meditation()
        return

    if interactor.has_method("begin_rest_at"):
        interactor.begin_rest_at(seat_anchor, rest_facing)
    elif interactor.has_method("start_meditation"):
        interactor.start_meditation()

    print("[VerandaRestArea] rest_at_veranda")


func get_interaction_hint() -> String:
    return interaction_hint


func _on_body_entered(body: Node) -> void:
    if body.is_in_group("player"):
        _show_hint(true)


func _on_body_exited(body: Node) -> void:
    if body.is_in_group("player"):
        _show_hint(false)


func _show_hint(show: bool) -> void:
    var hint := get_node_or_null("HintLabel")
    if hint is CanvasItem:
        hint.visible = show
