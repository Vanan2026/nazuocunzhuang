@tool
extends Node2D
class_name ManualAuthoringRect

@export var rect_size: Vector2 = Vector2(128, 128):
	set(value):
		rect_size = value
		queue_redraw()
@export var fill_color: Color = Color(0.2, 0.7, 1.0, 0.16):
	set(value):
		fill_color = value
		queue_redraw()
@export var outline_color: Color = Color(0.2, 0.7, 1.0, 0.9):
	set(value):
		outline_color = value
		queue_redraw()
@export var outline_width: float = 3.0:
	set(value):
		outline_width = value
		queue_redraw()
@export var label_text: String = "manual":
	set(value):
		label_text = value
		queue_redraw()

func _ready() -> void:
	queue_redraw()

func _draw() -> void:
	if not Engine.is_editor_hint():
		return
	if rect_size.x <= 0.0 or rect_size.y <= 0.0:
		return
	var rect := Rect2(Vector2.ZERO, rect_size)
	draw_rect(rect, fill_color, true)
	draw_rect(rect, outline_color, false, outline_width)
	var cross_color := Color(outline_color.r, outline_color.g, outline_color.b, min(outline_color.a, 0.5))
	draw_line(Vector2.ZERO, rect_size, cross_color, 1.0)
	draw_line(Vector2(rect_size.x, 0.0), Vector2(0.0, rect_size.y), cross_color, 1.0)