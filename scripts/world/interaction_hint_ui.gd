extends CanvasLayer

@export var hint_label_path: NodePath = NodePath("CanvasLayer_UI/InteractionPrompt")
@export var fade_duration: float = 0.15

var hint_label: Label = null
var current_hint: String = ""
var target_alpha: float = 0.0
var current_alpha: float = 0.0

func _ready() -> void:
    hint_label = get_node_or_null(hint_label_path)
    if hint_label == null:
        var canvas = get_node_or_null("CanvasLayer_UI")
        if canvas != null:
            hint_label = canvas.get_node_or_null("InteractionPrompt")
    if hint_label == null:
        hint_label = _create_default_hint_label()
    if hint_label != null:
        hint_label.visible = false
    print("[InteractionHintUI] 初始化完成")

func _process(delta: float) -> void:
    if hint_label == null:
        return
    var speed := fade_duration * 8.0
    current_alpha = lerp(current_alpha, target_alpha, speed * delta)
    hint_label.modulate.a = clamp(current_alpha, 0.0, 1.0)

func show_hint(text: String) -> void:
    if hint_label == null:
        return
    if current_hint != text:
        current_hint = text
        hint_label.text = text
    hint_label.visible = true
    target_alpha = 1.0

func hide_hint() -> void:
    target_alpha = 0.0
    current_hint = ""

func hide_hint_now() -> void:
    hide_hint()
    current_alpha = 0.0
    if hint_label != null:
        hint_label.text = ""
        hint_label.modulate.a = 0.0
        hint_label.visible = false

func _on_nearest_interactable_changed(hint: String) -> void:
    if hint.is_empty():
        hide_hint()
    else:
        show_hint(hint)


func _create_default_hint_label() -> Label:
    var label := Label.new()
    label.name = "InteractionPrompt"
    label.anchor_left = 0.5
    label.anchor_right = 0.5
    label.anchor_top = 1.0
    label.anchor_bottom = 1.0
    label.offset_left = -160.0
    label.offset_right = 160.0
    label.offset_top = -108.0
    label.offset_bottom = -72.0
    label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    label.text = "按 E 交互"
    label.add_theme_font_size_override("font_size", 18)
    label.add_theme_color_override("font_color", Color(0.96, 0.91, 0.78, 1.0))

    var style := StyleBoxFlat.new()
    style.bg_color = Color(0.12, 0.09, 0.06, 0.82)
    style.border_color = Color(0.58, 0.46, 0.26, 0.95)
    style.border_width_left = 2
    style.border_width_top = 2
    style.border_width_right = 2
    style.border_width_bottom = 2
    style.corner_radius_top_left = 6
    style.corner_radius_top_right = 6
    style.corner_radius_bottom_left = 6
    style.corner_radius_bottom_right = 6
    label.add_theme_stylebox_override("normal", style)

    add_child(label)
    return label
