extends CanvasLayer

signal dialogue_finished

var dialogue_visible: bool = false
var dialogue_box: Panel = null
var name_label: Label = null
var text_label: RichTextLabel = null
var continue_hint: Label = null
var current_speaker: String = ""
var current_text: String = ""
var text_progress: float = 0.0
var text_speed: float = 40.0
var is_displaying_text: bool = false
var can_advance: bool = false

func _ready() -> void:
	_setup_dialogue_ui()
	hide_dialogue()

func _setup_dialogue_ui() -> void:
	dialogue_box = Panel.new()
	dialogue_box.name = "DialogueBox"
	dialogue_box.anchor_left = 0.0
	dialogue_box.anchor_right = 1.0
	dialogue_box.anchor_top = 1.0
	dialogue_box.anchor_bottom = 1.0
	dialogue_box.offset_top = -150.0
	dialogue_box.offset_left = 40.0
	dialogue_box.offset_right = -40.0
	dialogue_box.offset_bottom = -20.0
	dialogue_box.z_index = 500
	
	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.08, 0.06, 0.92)
	style.border_color = Color(0.6, 0.55, 0.4, 1)
	style.border_width_top = 3
	style.border_width_bottom = 3
	style.border_width_left = 3
	style.border_width_right = 3
	style.corner_radius_top_left = 8
	style.corner_radius_top_right = 8
	style.corner_radius_bottom_left = 8
	style.corner_radius_bottom_right = 8
	style.content_margin_left = 20
	style.content_margin_top = 15
	style.content_margin_right = 20
	style.content_margin_bottom = 15
	dialogue_box.add_theme_stylebox_override("panel", style)
	add_child(dialogue_box)
	
	name_label = Label.new()
	name_label.name = "SpeakerName"
	name_label.anchor_right = 1.0
	name_label.anchor_bottom = 0.0
	name_label.offset_top = 0.0
	name_label.offset_bottom = 30.0
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	name_label.add_theme_color_override("font_color", Color(1, 0.9, 0.6))
	name_label.add_theme_font_size_override("font_size", 18)
	dialogue_box.add_child(name_label)
	
	text_label = RichTextLabel.new()
	text_label.name = "DialogueText"
	text_label.anchor_right = 1.0
	text_label.anchor_bottom = 1.0
	text_label.offset_top = 35.0
	text_label.bbcode_enabled = false
	text_label.text = ""
	text_label.fit_content = false
	text_label.scroll_active = false
	text_label.add_theme_color_override("default_color", Color(0.95, 0.92, 0.85))
	text_label.add_theme_font_size_override("normal_font_size", 16)
	dialogue_box.add_child(text_label)
	
	continue_hint = Label.new()
	continue_hint.name = "ContinueHint"
	continue_hint.anchor_left = 1.0
	continue_hint.anchor_right = 1.0
	continue_hint.anchor_top = 1.0
	continue_hint.anchor_bottom = 1.0
	continue_hint.offset_left = -80.0
	continue_hint.offset_top = -30.0
	continue_hint.offset_right = -10.0
	continue_hint.offset_bottom = -5.0
	continue_hint.text = "按 E 继续"
	continue_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	continue_hint.add_theme_color_override("font_color", Color(0.7, 0.65, 0.5))
	continue_hint.add_theme_font_size_override("font_size", 14)
	dialogue_box.add_child(continue_hint)

func show_dialogue(speaker: String, text: String) -> void:
	current_speaker = speaker
	current_text = text
	name_label.text = speaker
	text_label.text = ""
	text_progress = 0.0
	is_displaying_text = true
	can_advance = false
	dialogue_visible = true
	dialogue_box.visible = true
	continue_hint.visible = false
	print("[UIManager] 显示对话: ", speaker, " - ", text)

func hide_dialogue() -> void:
	dialogue_visible = false
	dialogue_box.visible = false
	is_displaying_text = false
	can_advance = false

func _process(delta: float) -> void:
	if not dialogue_visible:
		return
	
	if is_displaying_text:
		text_progress += delta * text_speed
		var displayed_chars = int(text_progress)
		if displayed_chars >= current_text.length():
			text_label.text = current_text
			is_displaying_text = false
			can_advance = true
			continue_hint.visible = true
		else:
			text_label.text = current_text.substr(0, displayed_chars)

func _input(event: InputEvent) -> void:
	if not dialogue_visible:
		return
	if event.is_action_pressed("interact"):
		if is_displaying_text:
			text_label.text = current_text
			is_displaying_text = false
			can_advance = true
			continue_hint.visible = true
		elif can_advance:
			hide_dialogue()
			emit_signal("dialogue_finished")