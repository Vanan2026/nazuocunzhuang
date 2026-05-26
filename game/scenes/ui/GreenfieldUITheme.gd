class_name GreenfieldUITheme
extends RefCounted

const SURFACE_PANEL_TEXTURE: Texture2D = preload("res://assets/art/greenfield_p0/ui/ui_panel_frame_512x320.png")
const HUD_PANEL_TEXTURE: Texture2D = preload("res://assets/art/greenfield_p0/ui/ui_hud_panel_512x128.png")
const DIALOGUE_PANEL_TEXTURE: Texture2D = preload("res://assets/art/greenfield_p0/ui/ui_dialogue_frame_1024x256.png")
const BUTTON_TEXTURE: Texture2D = preload("res://assets/art/greenfield_p0/ui/ui_button_256x96.png")

const PRIMARY_TEXT_COLOR := Color(0.33, 0.23, 0.14, 1.0)
const SECONDARY_TEXT_COLOR := Color(0.44, 0.31, 0.19, 1.0)
const BUTTON_HOVER_TINT := Color(1.0, 0.985, 0.95, 1.0)
const BUTTON_PRESSED_TINT := Color(0.965, 0.94, 0.89, 1.0)


static func apply_surface_panel(panel: Control) -> void:
	if panel == null:
		return
	panel.add_theme_stylebox_override("panel", _build_stylebox(
		SURFACE_PANEL_TEXTURE,
		26.0,
		22.0,
		18.0,
		22.0,
		18.0
	))


static func apply_hud_panel(panel: Control) -> void:
	if panel == null:
		return
	panel.add_theme_stylebox_override("panel", _build_stylebox(
		HUD_PANEL_TEXTURE,
		20.0,
		18.0,
		12.0,
		18.0,
		12.0
	))


static func apply_dialogue_panel(panel: Control) -> void:
	if panel == null:
		return
	panel.add_theme_stylebox_override("panel", _build_stylebox(
		DIALOGUE_PANEL_TEXTURE,
		24.0,
		22.0,
		14.0,
		22.0,
		14.0
	))


static func apply_button(button: Button, font_size: int = 15, min_height: float = 42.0) -> void:
	if button == null:
		return
	button.add_theme_stylebox_override("normal", _build_button_stylebox(Color.WHITE))
	button.add_theme_stylebox_override("hover", _build_button_stylebox(BUTTON_HOVER_TINT))
	button.add_theme_stylebox_override("pressed", _build_button_stylebox(BUTTON_PRESSED_TINT))
	button.add_theme_stylebox_override("focus", _build_button_stylebox(BUTTON_HOVER_TINT))
	button.add_theme_stylebox_override("disabled", _build_button_stylebox(Color(1.0, 1.0, 1.0, 0.86)))
	button.add_theme_color_override("font_color", PRIMARY_TEXT_COLOR)
	button.add_theme_color_override("font_hover_color", PRIMARY_TEXT_COLOR)
	button.add_theme_color_override("font_pressed_color", PRIMARY_TEXT_COLOR)
	button.add_theme_color_override("font_focus_color", PRIMARY_TEXT_COLOR)
	button.add_theme_color_override("font_disabled_color", SECONDARY_TEXT_COLOR)
	button.add_theme_font_size_override("font_size", font_size)
	button.custom_minimum_size = Vector2(max(button.custom_minimum_size.x, 0.0), max(button.custom_minimum_size.y, min_height))
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL


static func apply_title_label(label: Label, font_size: int = 16) -> void:
	if label == null:
		return
	label.add_theme_color_override("font_color", PRIMARY_TEXT_COLOR)
	label.add_theme_font_size_override("font_size", font_size)


static func apply_body_label(label: Label, font_size: int = 15) -> void:
	if label == null:
		return
	label.add_theme_color_override("font_color", PRIMARY_TEXT_COLOR)
	label.add_theme_font_size_override("font_size", font_size)


static func apply_hint_label(label: Label, font_size: int = 14) -> void:
	if label == null:
		return
	label.add_theme_color_override("font_color", SECONDARY_TEXT_COLOR)
	label.add_theme_font_size_override("font_size", font_size)


static func _build_button_stylebox(tint: Color) -> StyleBoxTexture:
	var style := _build_stylebox(BUTTON_TEXTURE, 22.0, 18.0, 10.0, 18.0, 10.0)
	style.modulate_color = tint
	return style


static func _build_stylebox(
	texture: Texture2D,
	texture_margin: float,
	content_left: float,
	content_top: float,
	content_right: float,
	content_bottom: float
) -> StyleBoxTexture:
	var style := StyleBoxTexture.new()
	style.texture = texture
	style.texture_margin_left = texture_margin
	style.texture_margin_top = texture_margin
	style.texture_margin_right = texture_margin
	style.texture_margin_bottom = texture_margin
	style.content_margin_left = content_left
	style.content_margin_top = content_top
	style.content_margin_right = content_right
	style.content_margin_bottom = content_bottom
	return style
