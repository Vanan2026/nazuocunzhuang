class_name GFTheme
extends RefCounted

const PAPER_PANEL_TEXTURE: Texture2D = preload("res://assets/ui/panels/ui_panel_paper_01.png")
const WOOD_PANEL_TEXTURE: Texture2D = preload("res://assets/ui/panels/ui_panel_wood_01.png")
const BUTTON_NORMAL_TEXTURE: Texture2D = preload("res://assets/ui/buttons/ui_button_normal.png")
const BUTTON_HOVER_TEXTURE: Texture2D = preload("res://assets/ui/buttons/ui_button_hover.png")
const BUTTON_PRESSED_TEXTURE: Texture2D = preload("res://assets/ui/buttons/ui_button_pressed.png")
const SLOT_TEXTURE: Texture2D = preload("res://assets/ui/slots/ui_slot_item.png")
const SLOT_SELECTED_TEXTURE: Texture2D = preload("res://assets/ui/slots/ui_slot_selected.png")
const TAB_NORMAL_TEXTURE: Texture2D = preload("res://assets/ui/tabs/ui_tab_normal.png")
const TAB_ACTIVE_TEXTURE: Texture2D = preload("res://assets/ui/tabs/ui_tab_active.png")
const CHECKBOX_ON_TEXTURE: Texture2D = preload("res://assets/ui/widgets/ui_checkbox_on.png")
const CHECKBOX_OFF_TEXTURE: Texture2D = preload("res://assets/ui/widgets/ui_checkbox_off.png")

const PRIMARY_TEXT_COLOR := Color(0.31, 0.21, 0.13, 1.0)
const SECONDARY_TEXT_COLOR := Color(0.45, 0.32, 0.2, 1.0)
const MUTED_TEXT_COLOR := Color(0.54, 0.43, 0.29, 1.0)
const SOFT_GREEN := Color(0.42, 0.55, 0.27, 1.0)
const WARNING_RED := Color(0.58, 0.21, 0.16, 1.0)


static func apply_paper_panel(panel: Control) -> void:
	if panel == null:
		return
	panel.add_theme_stylebox_override("panel", build_texture_stylebox(PAPER_PANEL_TEXTURE, 32.0, 24.0, 22.0, 24.0, 22.0))


static func apply_wood_panel(panel: Control) -> void:
	if panel == null:
		return
	panel.add_theme_stylebox_override("panel", build_texture_stylebox(WOOD_PANEL_TEXTURE, 34.0, 24.0, 22.0, 24.0, 22.0))


static func apply_hud_panel(panel: Control) -> void:
	if panel == null:
		return
	panel.add_theme_stylebox_override("panel", build_texture_stylebox(PAPER_PANEL_TEXTURE, 30.0, 18.0, 14.0, 18.0, 14.0))


static func apply_dialogue_panel(panel: Control) -> void:
	if panel == null:
		return
	panel.add_theme_stylebox_override("panel", build_texture_stylebox(PAPER_PANEL_TEXTURE, 32.0, 24.0, 18.0, 24.0, 18.0))


static func apply_button(button: Button, font_size: int = 15, min_height: float = 42.0) -> void:
	if button == null:
		return
	button.add_theme_stylebox_override("normal", build_texture_stylebox(BUTTON_NORMAL_TEXTURE, 24.0, 18.0, 10.0, 18.0, 10.0))
	button.add_theme_stylebox_override("hover", build_texture_stylebox(BUTTON_HOVER_TEXTURE, 24.0, 18.0, 10.0, 18.0, 10.0))
	button.add_theme_stylebox_override("pressed", build_texture_stylebox(BUTTON_PRESSED_TEXTURE, 24.0, 18.0, 10.0, 18.0, 10.0))
	button.add_theme_stylebox_override("focus", build_texture_stylebox(BUTTON_HOVER_TEXTURE, 24.0, 18.0, 10.0, 18.0, 10.0))
	button.add_theme_stylebox_override("disabled", build_texture_stylebox(BUTTON_NORMAL_TEXTURE, 24.0, 18.0, 10.0, 18.0, 10.0, Color(1, 1, 1, 0.58)))
	button.add_theme_color_override("font_color", PRIMARY_TEXT_COLOR)
	button.add_theme_color_override("font_hover_color", PRIMARY_TEXT_COLOR)
	button.add_theme_color_override("font_pressed_color", PRIMARY_TEXT_COLOR)
	button.add_theme_color_override("font_focus_color", PRIMARY_TEXT_COLOR)
	button.add_theme_color_override("font_disabled_color", MUTED_TEXT_COLOR)
	button.add_theme_font_size_override("font_size", font_size)
	button.custom_minimum_size = Vector2(max(button.custom_minimum_size.x, 0.0), max(button.custom_minimum_size.y, min_height))


static func apply_item_slot(button: Button, selected: bool = false) -> void:
	if button == null:
		return
	var texture := SLOT_SELECTED_TEXTURE if selected else SLOT_TEXTURE
	var style := build_texture_stylebox(texture, 18.0, 10.0, 10.0, 10.0, 10.0)
	button.add_theme_stylebox_override("normal", style)
	button.add_theme_stylebox_override("hover", build_texture_stylebox(SLOT_SELECTED_TEXTURE, 18.0, 10.0, 10.0, 10.0, 10.0))
	button.add_theme_stylebox_override("pressed", build_texture_stylebox(SLOT_SELECTED_TEXTURE, 18.0, 10.0, 10.0, 10.0, 10.0))
	button.add_theme_color_override("font_color", PRIMARY_TEXT_COLOR)
	button.add_theme_font_size_override("font_size", 13)
	button.custom_minimum_size = Vector2(84, 84)


static func apply_tab_button(button: Button, active: bool = false) -> void:
	if button == null:
		return
	var normal := TAB_ACTIVE_TEXTURE if active else TAB_NORMAL_TEXTURE
	button.add_theme_stylebox_override("normal", build_texture_stylebox(normal, 18.0, 12.0, 8.0, 12.0, 8.0))
	button.add_theme_stylebox_override("hover", build_texture_stylebox(TAB_ACTIVE_TEXTURE, 18.0, 12.0, 8.0, 12.0, 8.0))
	button.add_theme_stylebox_override("pressed", build_texture_stylebox(TAB_ACTIVE_TEXTURE, 18.0, 12.0, 8.0, 12.0, 8.0))
	button.add_theme_color_override("font_color", PRIMARY_TEXT_COLOR)
	button.add_theme_font_size_override("font_size", 14)
	button.custom_minimum_size = Vector2(118, 44)


static func apply_checkbox(check_box: CheckBox, font_size: int = 14) -> void:
	if check_box == null:
		return
	check_box.add_theme_icon_override("checked", CHECKBOX_ON_TEXTURE)
	check_box.add_theme_icon_override("unchecked", CHECKBOX_OFF_TEXTURE)
	check_box.add_theme_color_override("font_color", PRIMARY_TEXT_COLOR)
	check_box.add_theme_color_override("font_hover_color", PRIMARY_TEXT_COLOR)
	check_box.add_theme_font_size_override("font_size", font_size)
	check_box.custom_minimum_size = Vector2(max(check_box.custom_minimum_size.x, 0.0), max(check_box.custom_minimum_size.y, 36.0))


static func apply_slider(slider: HSlider) -> void:
	if slider == null:
		return
	var rail := StyleBoxFlat.new()
	rail.bg_color = Color(0.54, 0.43, 0.25, 1.0)
	rail.corner_radius_top_left = 4
	rail.corner_radius_top_right = 4
	rail.corner_radius_bottom_left = 4
	rail.corner_radius_bottom_right = 4
	var fill := StyleBoxFlat.new()
	fill.bg_color = SOFT_GREEN
	fill.corner_radius_top_left = 4
	fill.corner_radius_top_right = 4
	fill.corner_radius_bottom_left = 4
	fill.corner_radius_bottom_right = 4
	var grabber := StyleBoxFlat.new()
	grabber.bg_color = Color(0.77, 0.6, 0.28, 1.0)
	grabber.border_width_left = 2
	grabber.border_width_top = 2
	grabber.border_width_right = 2
	grabber.border_width_bottom = 2
	grabber.border_color = Color(0.32, 0.22, 0.13, 1.0)
	grabber.corner_radius_top_left = 8
	grabber.corner_radius_top_right = 8
	grabber.corner_radius_bottom_left = 8
	grabber.corner_radius_bottom_right = 8
	slider.add_theme_stylebox_override("slider", rail)
	slider.add_theme_stylebox_override("grabber_area", fill)
	slider.add_theme_stylebox_override("grabber_area_highlight", fill)
	slider.add_theme_icon_override("grabber", _stylebox_to_texture(grabber, Vector2i(18, 18)))
	slider.add_theme_icon_override("grabber_highlight", _stylebox_to_texture(grabber, Vector2i(20, 20)))
	slider.custom_minimum_size = Vector2(max(slider.custom_minimum_size.x, 220.0), max(slider.custom_minimum_size.y, 28.0))


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


static func build_texture_stylebox(
	texture: Texture2D,
	texture_margin: float,
	content_left: float,
	content_top: float,
	content_right: float,
	content_bottom: float,
	modulate: Color = Color.WHITE
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
	style.modulate_color = modulate
	return style


static func _stylebox_to_texture(style: StyleBoxFlat, size: Vector2i) -> Texture2D:
	var image := Image.create(size.x, size.y, false, Image.FORMAT_RGBA8)
	image.fill(Color(0, 0, 0, 0))
	var center := Vector2(size) * 0.5
	var radius := float(min(size.x, size.y)) * 0.5 - 1.0
	for y in range(size.y):
		for x in range(size.x):
			if Vector2(x, y).distance_to(center) <= radius:
				image.set_pixel(x, y, style.bg_color)
	return ImageTexture.create_from_image(image)
