class_name SettingsScreen
extends CanvasLayer

const GREENFIELD_THEME: Theme = preload("res://ui/theme/greenfield_theme.tres")
const GREENFIELD_UI_THEME := preload("res://game/scenes/ui/GreenfieldUITheme.gd")
const ASSET_PATHS := preload("res://game/systems/assets/GreenfieldAssetPaths.gd")

const SECTIONS := ["audio", "display", "language", "save"]

@onready var panel: PanelContainer = get_node_or_null("Panel")
@onready var title_label: Label = get_node_or_null("Panel/Content/Header/TitleLabel")
@onready var close_button: Button = get_node_or_null("Panel/Content/Header/CloseButton")
@onready var side_tabs: VBoxContainer = get_node_or_null("Panel/Content/MainRow/SideTabs")
@onready var settings_panel: PanelContainer = get_node_or_null("Panel/Content/MainRow/SettingsPanel")
@onready var preview_panel: PanelContainer = get_node_or_null("Panel/Content/MainRow/PreviewPanel")
@onready var preview_texture: TextureRect = get_node_or_null("Panel/Content/MainRow/PreviewPanel/PreviewStack/PreviewTexture")

@onready var audio_section: VBoxContainer = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/AudioSection")
@onready var display_section: VBoxContainer = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/DisplaySection")
@onready var language_section: VBoxContainer = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/LanguageSection")
@onready var save_section: VBoxContainer = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/SaveSection")

@onready var music_slider: HSlider = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/AudioSection/MusicRow/MusicSlider")
@onready var sfx_slider: HSlider = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/AudioSection/SfxRow/SfxSlider")
@onready var ambience_slider: HSlider = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/AudioSection/AmbienceRow/AmbienceSlider")
@onready var fullscreen_check_box: CheckBox = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/DisplaySection/FullscreenCheckBox")
@onready var soft_light_check_box: CheckBox = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/DisplaySection/SoftLightCheckBox")
@onready var resolution_option: OptionButton = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/DisplaySection/ResolutionOption")
@onready var language_option: OptionButton = get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/LanguageSection/LanguageOption")
@onready var save_button: Button = get_node_or_null("Panel/Content/Footer/SaveButton")
@onready var cancel_button: Button = get_node_or_null("Panel/Content/Footer/CancelButton")

var active_section := "audio"
var settings := {
	"music": 0.74,
	"sfx": 0.68,
	"ambience": 0.62,
	"fullscreen": false,
	"soft_light": true,
	"resolution": "1920x1080",
	"language": "zh_CN",
}


func _ready() -> void:
	_ensure_nodes()
	_apply_greenfield_style()
	_populate_options()
	_apply_settings_to_controls()
	set_section(active_section)


func open_settings() -> void:
	visible = true
	_apply_greenfield_style()
	_apply_settings_to_controls()


func close_settings() -> void:
	visible = false


func set_section(section_id: String) -> bool:
	if not SECTIONS.has(section_id):
		return false
	active_section = section_id
	_set_section_visible(audio_section, section_id == "audio")
	_set_section_visible(display_section, section_id == "display")
	_set_section_visible(language_section, section_id == "language")
	_set_section_visible(save_section, section_id == "save")
	_refresh_tabs()
	return true


func get_settings_snapshot() -> Dictionary:
	_read_controls_to_settings()
	return settings.duplicate(true)


func apply_settings(next_settings: Dictionary) -> void:
	for key in settings.keys():
		if next_settings.has(key):
			settings[key] = next_settings[key]
	_apply_settings_to_controls()


func _populate_options() -> void:
	if resolution_option != null and resolution_option.item_count == 0:
		for label in ["1280x720", "1600x900", "1920x1080"]:
			resolution_option.add_item(label)
	if language_option != null and language_option.item_count == 0:
		for label in ["简体中文", "English", "日本語"]:
			language_option.add_item(label)


func _apply_settings_to_controls() -> void:
	if music_slider != null:
		music_slider.value = float(settings.get("music", 0.74))
	if sfx_slider != null:
		sfx_slider.value = float(settings.get("sfx", 0.68))
	if ambience_slider != null:
		ambience_slider.value = float(settings.get("ambience", 0.62))
	if fullscreen_check_box != null:
		fullscreen_check_box.button_pressed = bool(settings.get("fullscreen", false))
	if soft_light_check_box != null:
		soft_light_check_box.button_pressed = bool(settings.get("soft_light", true))
	_select_option_by_text(resolution_option, String(settings.get("resolution", "1920x1080")))
	_select_language()


func _read_controls_to_settings() -> void:
	if music_slider != null:
		settings["music"] = music_slider.value
	if sfx_slider != null:
		settings["sfx"] = sfx_slider.value
	if ambience_slider != null:
		settings["ambience"] = ambience_slider.value
	if fullscreen_check_box != null:
		settings["fullscreen"] = fullscreen_check_box.button_pressed
	if soft_light_check_box != null:
		settings["soft_light"] = soft_light_check_box.button_pressed
	if resolution_option != null:
		settings["resolution"] = resolution_option.get_item_text(resolution_option.selected)
	if language_option != null:
		var selected_text := language_option.get_item_text(language_option.selected)
		settings["language"] = _language_id_from_label(selected_text)


func _select_language() -> void:
	var language_id := String(settings.get("language", "zh_CN"))
	var label := "简体中文"
	if language_id == "en":
		label = "English"
	elif language_id == "ja":
		label = "日本語"
	_select_option_by_text(language_option, label)


func _select_option_by_text(option: OptionButton, label: String) -> void:
	if option == null:
		return
	for index in range(option.item_count):
		if option.get_item_text(index) == label:
			option.select(index)
			return


func _language_id_from_label(label: String) -> String:
	if label == "English":
		return "en"
	if label == "日本語":
		return "ja"
	return "zh_CN"


func _set_section_visible(section: Control, should_show: bool) -> void:
	if section != null:
		section.visible = should_show


func _refresh_tabs() -> void:
	if side_tabs == null:
		return
	for child in side_tabs.get_children():
		if child is Button:
			var button := child as Button
			var section_id := String(button.get_meta("section_id", ""))
			GREENFIELD_UI_THEME.apply_tab_button(button, section_id == active_section)


func _apply_greenfield_style() -> void:
	_ensure_nodes()
	if panel != null:
		panel.theme = GREENFIELD_THEME
		GREENFIELD_UI_THEME.apply_surface_panel(panel)
	if settings_panel != null:
		GREENFIELD_UI_THEME.apply_surface_panel(settings_panel)
	if preview_panel != null:
		GREENFIELD_UI_THEME.apply_surface_panel(preview_panel)
	if preview_texture != null:
		preview_texture.texture = ASSET_PATHS.load_texture(ASSET_PATHS.UI_SETTINGS_PAPER_PREVIEW)
	for label in _collect_labels():
		GREENFIELD_UI_THEME.apply_body_label(label, 14)
	if title_label != null:
		GREENFIELD_UI_THEME.apply_title_label(title_label, 18)
	for slider in [music_slider, sfx_slider, ambience_slider]:
		var typed_slider := slider as HSlider
		if typed_slider != null:
			GREENFIELD_UI_THEME.apply_slider(typed_slider)
	for check_box in [fullscreen_check_box, soft_light_check_box]:
		var typed_check_box := check_box as CheckBox
		if typed_check_box != null:
			GREENFIELD_UI_THEME.apply_checkbox(typed_check_box, 14)
	for button in [close_button, save_button, cancel_button]:
		var typed_button := button as Button
		if typed_button != null:
			GREENFIELD_UI_THEME.apply_button(typed_button, 14, 40.0)
	if close_button != null and not close_button.pressed.is_connected(close_settings):
		close_button.pressed.connect(close_settings)
	if cancel_button != null and not cancel_button.pressed.is_connected(close_settings):
		cancel_button.pressed.connect(close_settings)
	if save_button != null and not save_button.pressed.is_connected(_on_save_pressed):
		save_button.pressed.connect(_on_save_pressed)
	_connect_tabs()
	_refresh_tabs()


func _collect_labels() -> Array[Label]:
	var labels: Array[Label] = []
	for node_path in [
		"Panel/Content/MainRow/SettingsPanel/Sections/AudioSection/AudioTitle",
		"Panel/Content/MainRow/SettingsPanel/Sections/AudioSection/MusicRow/MusicLabel",
		"Panel/Content/MainRow/SettingsPanel/Sections/AudioSection/SfxRow/SfxLabel",
		"Panel/Content/MainRow/SettingsPanel/Sections/AudioSection/AmbienceRow/AmbienceLabel",
		"Panel/Content/MainRow/SettingsPanel/Sections/DisplaySection/DisplayTitle",
		"Panel/Content/MainRow/SettingsPanel/Sections/DisplaySection/ResolutionLabel",
		"Panel/Content/MainRow/SettingsPanel/Sections/LanguageSection/LanguageTitle",
		"Panel/Content/MainRow/SettingsPanel/Sections/LanguageSection/LanguageLabel",
		"Panel/Content/MainRow/SettingsPanel/Sections/SaveSection/SaveTitle",
		"Panel/Content/MainRow/SettingsPanel/Sections/SaveSection/SaveHintLabel",
		"Panel/Content/MainRow/PreviewPanel/PreviewStack/PreviewLabel",
	]:
		var label := get_node_or_null(node_path) as Label
		if label != null:
			labels.append(label)
	return labels


func _connect_tabs() -> void:
	if side_tabs == null:
		return
	for child in side_tabs.get_children():
		if child is Button:
			var button := child as Button
			var section_id := String(button.get_meta("section_id", ""))
			if not button.pressed.is_connected(set_section.bind(section_id)):
				button.pressed.connect(set_section.bind(section_id))


func _on_save_pressed() -> void:
	_read_controls_to_settings()
	close_settings()


func _ensure_nodes() -> void:
	if panel == null:
		panel = get_node_or_null("Panel")
	if title_label == null:
		title_label = get_node_or_null("Panel/Content/Header/TitleLabel")
	if close_button == null:
		close_button = get_node_or_null("Panel/Content/Header/CloseButton")
	if side_tabs == null:
		side_tabs = get_node_or_null("Panel/Content/MainRow/SideTabs")
	if settings_panel == null:
		settings_panel = get_node_or_null("Panel/Content/MainRow/SettingsPanel")
	if preview_panel == null:
		preview_panel = get_node_or_null("Panel/Content/MainRow/PreviewPanel")
	if preview_texture == null:
		preview_texture = get_node_or_null("Panel/Content/MainRow/PreviewPanel/PreviewStack/PreviewTexture")
