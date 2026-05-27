extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const HUD_SCENE := "res://game/scenes/ui/HUD.tscn"
const PLAYER_YARD_SCENE := "res://game/scenes/world/PlayerYard.tscn"
const PAPER_PANEL_TEXTURE_PATH := "res://assets/ui/panels/ui_panel_paper_01.png"
const SLOT_SELECTED_TEXTURE_PATH := "res://assets/ui/slots/ui_slot_selected.png"
const WATCHDOG_TIMEOUT_SECONDS := 20.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: Greenfield P0 HUD runtime initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	await _validate_canonical_hud_scene()
	if _has_failed:
		return
	await _validate_player_yard_hud_connection()
	if _has_failed:
		return
	print("OK: Greenfield P0 HUD runtime validation passed")
	_finish_deferred(0)


func _validate_canonical_hud_scene() -> void:
	var scene := load(HUD_SCENE) as PackedScene
	_expect(scene != null, "HUD scene should load")
	if _has_failed:
		return
	var hud := scene.instantiate()
	root.add_child(hud)
	await _settle()
	_validate_hud_node(hud, "canonical HUD")
	hud.queue_free()


func _validate_player_yard_hud_connection() -> void:
	var scene := load(PLAYER_YARD_SCENE) as PackedScene
	_expect(scene != null, "PlayerYard scene should load")
	if _has_failed:
		return
	var yard := scene.instantiate()
	root.add_child(yard)
	await _settle()
	await _settle()
	var hud := yard.get_node_or_null("TimeWeatherHUD")
	_expect(hud != null, "PlayerYard should include TimeWeatherHUD")
	if _has_failed:
		yard.queue_free()
		return
	if hud.has_method("refresh"):
		hud.refresh()
	await _settle()
	_validate_hud_node(hud, "PlayerYard HUD")
	var coin_label := hud.get_node_or_null("StatusPanel/Content/CoinRow/CoinLabel") as Label
	var energy_label := hud.get_node_or_null("StatusPanel/Content/EnergyRow/EnergyLabel") as Label
	var slots := hud.get_node_or_null("HotbarPanel/Slots") as HBoxContainer
	_expect(coin_label != null and coin_label.text == "500", "PlayerYard HUD should show GameState money")
	_expect(energy_label != null and energy_label.text == "100 / 100", "PlayerYard HUD should show GameState energy")
	_expect(slots != null and slots.get_child_count() == 8, "PlayerYard HUD should build eight hotbar slots")
	if slots != null and slots.get_child_count() > 0:
		var first_slot := slots.get_child(0) as Button
		_expect(first_slot != null, "first hotbar slot should be a Button")
		if first_slot != null:
			_expect(_button_texture_path(first_slot, "normal") == SLOT_SELECTED_TEXTURE_PATH, "selected hotbar slot should use selected slot texture")
	yard.queue_free()


func _validate_hud_node(hud: Node, context: String) -> void:
	var top_panel := hud.get_node_or_null("Panel") as PanelContainer
	var status_panel := hud.get_node_or_null("StatusPanel") as PanelContainer
	var hotbar_panel := hud.get_node_or_null("HotbarPanel") as PanelContainer
	var season_label := hud.get_node_or_null("Panel/Content/SeasonLabel") as Label
	var weather_label := hud.get_node_or_null("Panel/Content/WeatherLabel") as Label
	var coin_label := hud.get_node_or_null("StatusPanel/Content/CoinRow/CoinLabel") as Label
	var energy_label := hud.get_node_or_null("StatusPanel/Content/EnergyRow/EnergyLabel") as Label
	var slots := hud.get_node_or_null("HotbarPanel/Slots") as HBoxContainer
	_expect(top_panel != null, "%s should include time/weather panel" % context)
	_expect(status_panel != null, "%s should include status panel" % context)
	_expect(hotbar_panel != null, "%s should include hotbar panel" % context)
	_expect(season_label != null and not season_label.text.is_empty(), "%s should show season/date" % context)
	_expect(weather_label != null and not weather_label.text.is_empty(), "%s should show weather" % context)
	_expect(coin_label != null and not coin_label.text.is_empty(), "%s should show money" % context)
	_expect(energy_label != null and not energy_label.text.is_empty(), "%s should show energy" % context)
	_expect(slots != null, "%s should include hotbar slots" % context)
	if _has_failed:
		return
	_expect(_stylebox_texture_path(top_panel.get_theme_stylebox("panel")) == PAPER_PANEL_TEXTURE_PATH, "%s time panel should use paper HUD style" % context)
	_expect(_stylebox_texture_path(status_panel.get_theme_stylebox("panel")) == PAPER_PANEL_TEXTURE_PATH, "%s status panel should use paper HUD style" % context)
	_expect(_stylebox_texture_path(hotbar_panel.get_theme_stylebox("panel")) == PAPER_PANEL_TEXTURE_PATH, "%s hotbar panel should use paper HUD style" % context)
	_expect(top_panel.position.y <= 24.0, "%s time panel should stay near the top edge" % context)
	_expect(status_panel.position.y <= 24.0, "%s status panel should stay near the top edge" % context)
	_expect(hotbar_panel.position.y >= 940.0, "%s hotbar should stay near the bottom edge" % context)


func _stylebox_texture_path(stylebox: StyleBox) -> String:
	var texture_box := stylebox as StyleBoxTexture
	if texture_box == null or texture_box.texture == null:
		return ""
	return String(texture_box.texture.resource_path)


func _button_texture_path(button: Button, state: StringName) -> String:
	return _stylebox_texture_path(button.get_theme_stylebox(state))


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
			_fail("Greenfield P0 HUD runtime validation timed out")
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
