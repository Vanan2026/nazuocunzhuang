extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const DIALOGUE_BOX_PATH := "res://game/scenes/ui/DialogueBox.tscn"
const CURRENT_OBJECTIVE_CHIP_PATH := "res://game/scenes/ui/CurrentObjectiveChip.tscn"
const DAILY_INTENT_PANEL_PATH := "res://game/scenes/ui/DailyIntentPanel.tscn"
const TIME_WEATHER_HUD_PATH := "res://game/scenes/ui/TimeWeatherHUD.tscn"

const DIALOGUE_TEXTURE_PATH := "res://assets/art/greenfield_p0/ui/ui_dialogue_frame_1024x256.png"
const SURFACE_TEXTURE_PATH := "res://assets/art/greenfield_p0/ui/ui_panel_frame_512x320.png"
const HUD_TEXTURE_PATH := "res://assets/art/greenfield_p0/ui/ui_hud_panel_512x128.png"
const BUTTON_TEXTURE_PATH := "res://assets/art/greenfield_p0/ui/ui_button_256x96.png"

const PRIMARY_TEXT_COLOR := Color(0.33, 0.23, 0.14, 1.0)
const SECONDARY_TEXT_COLOR := Color(0.44, 0.31, 0.19, 1.0)

const WATCHDOG_TIMEOUT_SECONDS := 15.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: ui quiet art pass initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	await _validate_dialogue_box()
	if _has_failed:
		return
	await _validate_current_objective_chip()
	if _has_failed:
		return
	await _validate_daily_intent_panel()
	if _has_failed:
		return
	await _validate_time_weather_hud()
	if _has_failed:
		return

	print("OK: ui quiet art pass runtime validation passed")
	_finish_deferred(0)


func _validate_dialogue_box() -> void:
	var scene := load(DIALOGUE_BOX_PATH) as PackedScene
	_expect(scene != null, "DialogueBox scene should load")
	if _has_failed:
		return
	var dialogue_box := scene.instantiate()
	root.add_child(dialogue_box)
	await _settle()
	var panel := dialogue_box.get_node_or_null("Panel") as PanelContainer
	var speaker_label := dialogue_box.get_node_or_null("Panel/Content/TextColumn/SpeakerLabel") as Label
	var line_label := dialogue_box.get_node_or_null("Panel/Content/TextColumn/LineLabel") as Label
	_expect(panel != null, "DialogueBox should include Panel")
	_expect(speaker_label != null, "DialogueBox should include SpeakerLabel")
	_expect(line_label != null, "DialogueBox should include LineLabel")
	if _has_failed:
		dialogue_box.queue_free()
		return
	_expect(_stylebox_texture_path(panel.get_theme_stylebox("panel")) == DIALOGUE_TEXTURE_PATH, "DialogueBox panel should use the Greenfield dialogue frame")
	_expect(speaker_label.has_theme_color_override("font_color"), "DialogueBox speaker label should override font color")
	_expect(line_label.has_theme_color_override("font_color"), "DialogueBox line label should override font color")
	_expect(_color_close_enough(speaker_label.get_theme_color("font_color"), PRIMARY_TEXT_COLOR), "DialogueBox speaker label should use the quiet primary text tone")
	_expect(_color_close_enough(line_label.get_theme_color("font_color"), SECONDARY_TEXT_COLOR), "DialogueBox line label should use the quiet secondary text tone")
	dialogue_box.queue_free()


func _validate_current_objective_chip() -> void:
	var scene := load(CURRENT_OBJECTIVE_CHIP_PATH) as PackedScene
	_expect(scene != null, "CurrentObjectiveChip scene should load")
	if _has_failed:
		return
	var chip := scene.instantiate()
	root.add_child(chip)
	await _settle()
	var panel := chip.get_node_or_null("Panel") as PanelContainer
	var title_label := chip.get_node_or_null("Panel/Content/TitleLabel") as Label
	var objective_label := chip.get_node_or_null("Panel/Content/ObjectiveLabel") as Label
	var hint_label := chip.get_node_or_null("Panel/Content/HintLabel") as Label
	var progress_label := chip.get_node_or_null("Panel/Content/ProgressLabel") as Label
	_expect(panel != null, "CurrentObjectiveChip should include Panel")
	_expect(title_label != null, "CurrentObjectiveChip should include TitleLabel")
	_expect(objective_label != null, "CurrentObjectiveChip should include ObjectiveLabel")
	_expect(hint_label != null, "CurrentObjectiveChip should include HintLabel")
	_expect(progress_label != null, "CurrentObjectiveChip should include ProgressLabel")
	if _has_failed:
		chip.queue_free()
		return
	_expect(_stylebox_texture_path(panel.get_theme_stylebox("panel")) == HUD_TEXTURE_PATH, "CurrentObjectiveChip should use the Greenfield HUD frame")
	_expect(_color_close_enough(title_label.get_theme_color("font_color"), PRIMARY_TEXT_COLOR), "CurrentObjectiveChip title should use primary text tone")
	_expect(_color_close_enough(objective_label.get_theme_color("font_color"), PRIMARY_TEXT_COLOR), "CurrentObjectiveChip objective should use primary text tone")
	_expect(_color_close_enough(hint_label.get_theme_color("font_color"), SECONDARY_TEXT_COLOR), "CurrentObjectiveChip hint should use secondary text tone")
	_expect(_color_close_enough(progress_label.get_theme_color("font_color"), SECONDARY_TEXT_COLOR), "CurrentObjectiveChip progress should use secondary text tone")
	chip.queue_free()


func _validate_daily_intent_panel() -> void:
	var scene := load(DAILY_INTENT_PANEL_PATH) as PackedScene
	_expect(scene != null, "DailyIntentPanel scene should load")
	if _has_failed:
		return
	var panel_layer := scene.instantiate()
	root.add_child(panel_layer)
	await _settle()
	var panel := panel_layer.get_node_or_null("Panel") as PanelContainer
	var title_label := panel_layer.get_node_or_null("Panel/Content/TitleLabel") as Label
	var status_label := panel_layer.get_node_or_null("Panel/Content/StatusLabel") as Label
	var close_button := panel_layer.get_node_or_null("Panel/Content/CloseButton") as Button
	var choice_buttons := panel_layer.get_node_or_null("Panel/Content/ChoiceButtons") as VBoxContainer
	_expect(panel != null, "DailyIntentPanel should include Panel")
	_expect(title_label != null, "DailyIntentPanel should include TitleLabel")
	_expect(status_label != null, "DailyIntentPanel should include StatusLabel")
	_expect(close_button != null, "DailyIntentPanel should include CloseButton")
	_expect(choice_buttons != null, "DailyIntentPanel should include ChoiceButtons")
	if _has_failed:
		panel_layer.queue_free()
		return
	_expect(_stylebox_texture_path(panel.get_theme_stylebox("panel")) == SURFACE_TEXTURE_PATH, "DailyIntentPanel should use the Greenfield surface frame")
	_expect(_color_close_enough(title_label.get_theme_color("font_color"), PRIMARY_TEXT_COLOR), "DailyIntentPanel title should use primary text tone")
	_expect(_color_close_enough(status_label.get_theme_color("font_color"), SECONDARY_TEXT_COLOR), "DailyIntentPanel status should use secondary text tone")
	_expect(choice_buttons.get_child_count() >= 4, "DailyIntentPanel should build themed intent buttons")
	_expect(_button_texture_path(close_button, "normal") == BUTTON_TEXTURE_PATH, "DailyIntentPanel close button should use the Greenfield button frame")
	if _has_failed:
		panel_layer.queue_free()
		return
	for child in choice_buttons.get_children():
		if child is Button:
			var button := child as Button
			_expect(_button_texture_path(button, "normal") == BUTTON_TEXTURE_PATH, "DailyIntentPanel choice button should use the Greenfield button frame")
			_expect(_color_close_enough(button.get_theme_color("font_color"), PRIMARY_TEXT_COLOR), "DailyIntentPanel choice buttons should use primary text tone")
			if _has_failed:
				panel_layer.queue_free()
				return
	panel_layer.queue_free()


func _validate_time_weather_hud() -> void:
	var scene := load(TIME_WEATHER_HUD_PATH) as PackedScene
	_expect(scene != null, "TimeWeatherHUD scene should load")
	if _has_failed:
		return
	var hud := scene.instantiate()
	root.add_child(hud)
	await _settle()
	var panel := hud.get_node_or_null("Panel") as PanelContainer
	var season_label := hud.get_node_or_null("Panel/Content/SeasonLabel") as Label
	var day_label := hud.get_node_or_null("Panel/Content/DayLabel") as Label
	var time_label := hud.get_node_or_null("Panel/Content/TimeLabel") as Label
	var weather_label := hud.get_node_or_null("Panel/Content/WeatherLabel") as Label
	_expect(panel != null, "TimeWeatherHUD should include Panel")
	_expect(season_label != null, "TimeWeatherHUD should include SeasonLabel")
	_expect(day_label != null, "TimeWeatherHUD should include DayLabel")
	_expect(time_label != null, "TimeWeatherHUD should include TimeLabel")
	_expect(weather_label != null, "TimeWeatherHUD should include WeatherLabel")
	if _has_failed:
		hud.queue_free()
		return
	_expect(_stylebox_texture_path(panel.get_theme_stylebox("panel")) == HUD_TEXTURE_PATH, "TimeWeatherHUD should use the Greenfield HUD frame")
	_expect(_color_close_enough(season_label.get_theme_color("font_color"), PRIMARY_TEXT_COLOR), "TimeWeatherHUD season label should use primary text tone")
	_expect(_color_close_enough(day_label.get_theme_color("font_color"), PRIMARY_TEXT_COLOR), "TimeWeatherHUD day label should use primary text tone")
	_expect(_color_close_enough(time_label.get_theme_color("font_color"), PRIMARY_TEXT_COLOR), "TimeWeatherHUD time label should use primary text tone")
	_expect(_color_close_enough(weather_label.get_theme_color("font_color"), SECONDARY_TEXT_COLOR), "TimeWeatherHUD weather label should use secondary text tone")
	hud.queue_free()


func _stylebox_texture_path(stylebox: StyleBox) -> String:
	var texture_box := stylebox as StyleBoxTexture
	if texture_box == null or texture_box.texture == null:
		return ""
	return String(texture_box.texture.resource_path)


func _button_texture_path(button: Button, state: StringName) -> String:
	var stylebox := button.get_theme_stylebox(state)
	return _stylebox_texture_path(stylebox)


func _color_close_enough(left: Color, right: Color) -> bool:
	return abs(left.r - right.r) <= 0.02 \
		and abs(left.g - right.g) <= 0.02 \
		and abs(left.b - right.b) <= 0.02 \
		and abs(left.a - right.a) <= 0.02


func _settle() -> void:
	await create_timer(0.05).timeout
	await process_frame
	await process_frame


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	_finish_deferred(1)


func _start_watchdog() -> void:
	if _finished:
		return
	_watchdog_timer = Timer.new()
	_watchdog_timer.one_shot = true
	_watchdog_timer.wait_time = WATCHDOG_TIMEOUT_SECONDS
	root.add_child(_watchdog_timer)
	_watchdog_timer.timeout.connect(func() -> void:
		if not _finished:
			_fail("UI quiet art pass validation timed out")
	)
	_watchdog_timer.start()


func _finish_deferred(exit_code: int) -> void:
	if _finished:
		return
	_finished = true
	if _watchdog_timer != null:
		_watchdog_timer.stop()
		_watchdog_timer.queue_free()
		_watchdog_timer = null
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
