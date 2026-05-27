@tool
class_name GFButton
extends Button

@export var greenfield_font_size := 15:
	set(value):
		greenfield_font_size = value
		_apply_greenfield_style()

@export var greenfield_min_height := 42.0:
	set(value):
		greenfield_min_height = value
		_apply_greenfield_style()


func _ready() -> void:
	_apply_greenfield_style()


func _apply_greenfield_style() -> void:
	if not is_inside_tree() and not Engine.is_editor_hint():
		return
	GFTheme.apply_button(self, greenfield_font_size, greenfield_min_height)
