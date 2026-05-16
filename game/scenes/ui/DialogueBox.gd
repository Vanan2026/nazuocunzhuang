class_name DialogueBox
extends CanvasLayer

signal dialogue_closed()

@onready var portrait: TextureRect = get_node_or_null("Panel/Content/Portrait")
@onready var speaker_label: Label = get_node_or_null("Panel/Content/TextColumn/SpeakerLabel")
@onready var line_label: Label = get_node_or_null("Panel/Content/TextColumn/LineLabel")

var dialogue: Dictionary = {}
var line_index: int = 0
var speaker_names: Dictionary = {}


func _ready() -> void:
	visible = false


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


func _ensure_nodes() -> void:
	if portrait == null:
		portrait = get_node_or_null("Panel/Content/Portrait")
	if speaker_label == null:
		speaker_label = get_node_or_null("Panel/Content/TextColumn/SpeakerLabel")
	if line_label == null:
		line_label = get_node_or_null("Panel/Content/TextColumn/LineLabel")


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
