@tool
class_name GFItemSlot
extends Button

@export var selected := false:
	set(value):
		selected = value
		_apply_greenfield_style()

@export var item_id := ""
@export var item_count := 0:
	set(value):
		item_count = value
		_refresh_text()


func _ready() -> void:
	_apply_greenfield_style()
	_refresh_text()


func set_item(next_item_id: String, item_name: String, count: int, is_selected: bool = false) -> void:
	item_id = next_item_id
	item_count = count
	selected = is_selected
	text = "%s\nx%d" % [item_name, item_count]
	tooltip_text = item_name
	_apply_greenfield_style()


func _refresh_text() -> void:
	if not item_id.is_empty() and text.is_empty():
		text = "%s\nx%d" % [item_id, item_count]


func _apply_greenfield_style() -> void:
	if not is_inside_tree() and not Engine.is_editor_hint():
		return
	GFTheme.apply_item_slot(self, selected)
