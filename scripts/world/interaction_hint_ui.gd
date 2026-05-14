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

func _on_nearest_interactable_changed(hint: String) -> void:
	if hint.is_empty():
		hide_hint()
	else:
		show_hint(hint)