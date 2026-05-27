extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const SETTINGS_SCENE := "res://game/scenes/ui/SettingsScreen.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 18.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Greenfield P0 SettingsScreen runtime initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var packed := load(SETTINGS_SCENE) as PackedScene
	_expect(packed != null, "SettingsScreen scene should load")
	if _has_failed:
		return
	var screen := packed.instantiate()
	root.add_child(screen)
	await _settle()

	_expect(screen.name == "SettingsScreen", "root should be named SettingsScreen")
	_expect(screen.visible == false, "SettingsScreen should start hidden")
	_expect(screen.has_method("open_settings"), "SettingsScreen should expose open_settings")
	_expect(screen.has_method("close_settings"), "SettingsScreen should expose close_settings")
	_expect(screen.has_method("set_section"), "SettingsScreen should expose set_section")
	_expect(screen.has_method("get_settings_snapshot"), "SettingsScreen should expose get_settings_snapshot")
	if _has_failed:
		screen.queue_free()
		return

	screen.open_settings()
	await _settle()
	_expect(screen.visible == true, "open_settings should show the screen")
	_expect(screen.get_node_or_null("Panel") is PanelContainer, "SettingsScreen should include the main paper panel")
	_expect(screen.get_node_or_null("Panel/Content/MainRow/SideTabs/AudioTab") is Button, "SettingsScreen should include Audio tab")
	_expect(screen.get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/AudioSection/MusicRow/MusicSlider") is HSlider, "SettingsScreen should include music slider")
	_expect(screen.get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/DisplaySection/FullscreenCheckBox") is CheckBox, "SettingsScreen should include fullscreen checkbox")
	_expect(screen.get_node_or_null("Panel/Content/MainRow/SettingsPanel/Sections/LanguageSection/LanguageOption") is OptionButton, "SettingsScreen should include language option")

	var preview := screen.get_node_or_null("Panel/Content/MainRow/PreviewPanel/PreviewStack/PreviewTexture") as TextureRect
	_expect(preview != null and preview.texture != null, "SettingsScreen should load the formal preview placeholder texture")

	var music := screen.get_node("Panel/Content/MainRow/SettingsPanel/Sections/AudioSection/MusicRow/MusicSlider") as HSlider
	music.value = 0.33
	_expect(screen.set_section("display") == true, "SettingsScreen should switch to display section")
	await _settle()
	_expect(screen.get_node("Panel/Content/MainRow/SettingsPanel/Sections/DisplaySection").visible == true, "display section should be visible")
	_expect(screen.set_section("language") == true, "SettingsScreen should switch to language section")
	_expect(screen.set_section("missing") == false, "unknown settings section should be rejected")

	var snapshot: Dictionary = screen.get_settings_snapshot()
	_expect(abs(float(snapshot.get("music", 0.0)) - 0.33) < 0.001, "SettingsScreen should read slider values into snapshot")
	_expect(snapshot.has("language"), "SettingsScreen snapshot should include language")
	screen.close_settings()
	await _settle()
	_expect(screen.visible == false, "close_settings should hide the screen")

	screen.queue_free()
	print("OK: Greenfield P0 SettingsScreen runtime validation passed")
	_finish_deferred(0)


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
			_fail("Greenfield P0 SettingsScreen runtime validation timed out")
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
