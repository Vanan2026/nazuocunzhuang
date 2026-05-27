class_name GreenfieldUITheme
extends RefCounted

const GF_THEME := preload("res://ui/theme/GreenfieldTheme.gd")
const PRIMARY_TEXT_COLOR := Color(0.31, 0.21, 0.13, 1.0)
const SECONDARY_TEXT_COLOR := Color(0.45, 0.32, 0.2, 1.0)


static func apply_surface_panel(panel: Control) -> void:
	GF_THEME.apply_paper_panel(panel)


static func apply_hud_panel(panel: Control) -> void:
	GF_THEME.apply_hud_panel(panel)


static func apply_dialogue_panel(panel: Control) -> void:
	GF_THEME.apply_dialogue_panel(panel)


static func apply_button(button: Button, font_size: int = 15, min_height: float = 42.0) -> void:
	GF_THEME.apply_button(button, font_size, min_height)
	if button != null:
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL


static func apply_item_slot(button: Button, selected: bool = false) -> void:
	GF_THEME.apply_item_slot(button, selected)


static func apply_tab_button(button: Button, active: bool = false) -> void:
	GF_THEME.apply_tab_button(button, active)


static func apply_checkbox(check_box: CheckBox, font_size: int = 14) -> void:
	GF_THEME.apply_checkbox(check_box, font_size)


static func apply_slider(slider: HSlider) -> void:
	GF_THEME.apply_slider(slider)


static func apply_title_label(label: Label, font_size: int = 16) -> void:
	GF_THEME.apply_title_label(label, font_size)


static func apply_body_label(label: Label, font_size: int = 15) -> void:
	GF_THEME.apply_body_label(label, font_size)


static func apply_hint_label(label: Label, font_size: int = 14) -> void:
	GF_THEME.apply_hint_label(label, font_size)
