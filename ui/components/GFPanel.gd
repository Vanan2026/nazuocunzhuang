@tool
class_name GFPanel
extends PanelContainer

@export_enum("paper", "wood", "hud", "dialogue") var panel_style := "paper":
	set(value):
		panel_style = value
		_apply_greenfield_style()


func _ready() -> void:
	_apply_greenfield_style()


func _apply_greenfield_style() -> void:
	if not is_inside_tree() and not Engine.is_editor_hint():
		return
	match panel_style:
		"wood":
			GFTheme.apply_wood_panel(self)
		"hud":
			GFTheme.apply_hud_panel(self)
		"dialogue":
			GFTheme.apply_dialogue_panel(self)
		_:
			GFTheme.apply_paper_panel(self)
