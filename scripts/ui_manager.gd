extends CanvasLayer

signal dialogue_shown
signal dialogue_closed

var dialogue_box: Panel = null
var dialogue_label: Label = null
var speaker_label: Label = null

func _ready() -> void:
    setup_dialogue_ui()

func setup_dialogue_ui() -> void:
    dialogue_box = Panel.new()
    dialogue_box.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
    dialogue_box.offset_top = -200
    dialogue_box.offset_bottom = -20
    dialogue_box.offset_left = 100
    dialogue_box.offset_right = -100
    dialogue_box.visible = false

    var style = StyleBoxFlat.new()
    style.bg_color = Color(0.1, 0.1, 0.1, 0.9)
    style.corner_radius_top_left = 12
    style.corner_radius_top_right = 12
    style.corner_radius_bottom_left = 12
    style.corner_radius_bottom_right = 12
    style.content_margin_left = 20
    style.content_margin_right = 20
    style.content_margin_top = 15
    style.content_margin_bottom = 15
    dialogue_box.add_theme_stylebox_override("panel", style)

    speaker_label = Label.new()
    speaker_label.anchors_preset = Control.PRESET_TOP_LEFT
    speaker_label.offset_left = 30
    speaker_label.offset_top = 10
    speaker_label.offset_right = 200
    speaker_label.offset_bottom = 40
    speaker_label.add_theme_color_override("font_color", Color(1, 0.9, 0.7))

    dialogue_label = Label.new()
    dialogue_label.anchors_preset = Control.PRESET_BOTTOM_WIDE
    dialogue_label.offset_left = 30
    dialogue_label.offset_top = 50
    dialogue_label.offset_right = -30
    dialogue_label.offset_bottom = -10
    dialogue_label.multiline = true
    dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD
    dialogue_label.add_theme_color_override("font_color", Color(0.95, 0.95, 0.9))

    dialogue_box.add_child(speaker_label)
    dialogue_box.add_child(dialogue_label)
    add_child(dialogue_box)

func show_dialogue(speaker: String, text: String) -> void:
    if dialogue_box:
        speaker_label.text = speaker
        dialogue_label.text = text
        dialogue_box.visible = true
        emit_signal("dialogue_shown")

func hide_dialogue() -> void:
    if dialogue_box:
        dialogue_box.visible = false
        emit_signal("dialogue_closed")

func _input(event: InputEvent) -> void:
    if dialogue_box and dialogue_box.visible and event is InputEvent:
        if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
            hide_dialogue()
            get_tree().root.set_input_as_handled()
