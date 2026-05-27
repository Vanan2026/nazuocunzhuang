@tool
class_name GFTabBar
extends HBoxContainer

signal tab_selected(tab_id: String)

@export var active_tab_id := "":
	set(value):
		active_tab_id = value
		_apply_greenfield_style()


func _ready() -> void:
	_apply_greenfield_style()


func configure_tabs(tabs: Array, next_active_tab_id: String = "") -> void:
	for child in get_children():
		child.queue_free()
	active_tab_id = next_active_tab_id
	for tab in tabs:
		var tab_id := String(tab.get("id", ""))
		var label := String(tab.get("label", tab_id))
		var button := Button.new()
		button.text = label
		button.set_meta("tab_id", tab_id)
		button.pressed.connect(_on_tab_pressed.bind(tab_id))
		add_child(button)
		GFTheme.apply_tab_button(button, tab_id == active_tab_id)
	_apply_greenfield_style()


func _on_tab_pressed(tab_id: String) -> void:
	active_tab_id = tab_id
	tab_selected.emit(tab_id)


func _apply_greenfield_style() -> void:
	for child in get_children():
		var button := child as Button
		if button != null:
			var tab_id := String(button.get_meta("tab_id", button.text))
			GFTheme.apply_tab_button(button, String(tab_id) == active_tab_id)
