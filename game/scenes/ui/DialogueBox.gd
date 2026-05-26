class_name DialogueBox
extends CanvasLayer

const GreenfieldUITheme := preload("res://game/scenes/ui/GreenfieldUITheme.gd")

signal dialogue_closed()

@onready var panel: PanelContainer = get_node_or_null("Panel")
@onready var content: HBoxContainer = get_node_or_null("Panel/Content")
@onready var portrait: TextureRect = get_node_or_null("Panel/Content/Portrait")
@onready var text_column: VBoxContainer = get_node_or_null("Panel/Content/TextColumn")
@onready var speaker_label: Label = get_node_or_null("Panel/Content/TextColumn/SpeakerLabel")
@onready var line_label: Label = get_node_or_null("Panel/Content/TextColumn/LineLabel")

var dialogue: Dictionary = {}
var line_index: int = 0
var speaker_names: Dictionary = {}


func _ready() -> void:
	visible = false
	_apply_visual_theme()


func show_dialogue(next_dialogue: Dictionary, display_context: Dictionary = {}) -> void:
	dialogue = next_dialogue.duplicate(true)
	line_index = 0
	speaker_names.clear()
	if display_context.has("npc_name"):
		speaker_names[String(dialogue.get("npc_id", ""))] = String(display_context["npc_name"])
	_set_portrait(String(display_context.get("portrait", "")))
	visible = true
	_show_current_line()


func advance() -> bool:
	var lines: Array = dialogue.get("lines", [])
	if line_index + 1 >= lines.size():
		close()
		return false
	line_index += 1
	_show_current_line()
	return true


func close() -> void:
	visible = false
	dialogue.clear()
	line_index = 0
	dialogue_closed.emit()


func _show_current_line() -> void:
	_ensure_nodes()
	var lines: Array = dialogue.get("lines", [])
	if lines.is_empty() or line_index >= lines.size():
		close()
		return
	var line: Dictionary = lines[line_index]
	var speaker_id := String(line.get("speaker", dialogue.get("npc_id", "")))
	if speaker_label != null:
		speaker_label.text = String(speaker_names.get(speaker_id, speaker_id))
	if line_label != null:
		line_label.text = String(line.get("text", ""))


func _set_portrait(path: String) -> void:
	_ensure_nodes()
	if portrait == null:
		return
	portrait.texture = _load_texture(path)
	portrait.visible = portrait.texture != null


func _ensure_nodes() -> void:
	if panel == null:
		panel = get_node_or_null("Panel")
	if content == null:
		content = get_node_or_null("Panel/Content")
	if portrait == null:
		portrait = get_node_or_null("Panel/Content/Portrait")
	if text_column == null:
		text_column = get_node_or_null("Panel/Content/TextColumn")
	if speaker_label == null:
		speaker_label = get_node_or_null("Panel/Content/TextColumn/SpeakerLabel")
	if line_label == null:
		line_label = get_node_or_null("Panel/Content/TextColumn/LineLabel")


func _apply_visual_theme() -> void:
	_ensure_nodes()
	GreenfieldUITheme.apply_dialogue_panel(panel)
	GreenfieldUITheme.apply_title_label(speaker_label, 15)
	GreenfieldUITheme.apply_body_label(line_label, 15)
	GreenfieldUITheme.apply_hint_label(line_label, 15)
	if content != null:
		content.add_theme_constant_override("separation", 12)
	if text_column != null:
		text_column.add_theme_constant_override("separation", 4)


func _load_texture(path: String) -> Texture2D:
	if path.is_empty():
		return null
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	if FileAccess.file_exists(path):
		var image := Image.load_from_file(path)
		if image != null and not image.is_empty():
			return ImageTexture.create_from_image(image)
	return null
