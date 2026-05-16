extends SceneTree

const TIME_MANAGER_PATH := "res://game/autoload/TimeManager.gd"
const WEATHER_MANAGER_PATH := "res://game/autoload/WeatherManager.gd"
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"

var _has_failed := false


func _initialize() -> void:
	var time_script: Script = load(TIME_MANAGER_PATH) as Script
	var weather_script: Script = load(WEATHER_MANAGER_PATH) as Script
	if time_script == null or weather_script == null:
		_fail("could not load time/weather scripts")
		return

	var time_manager: Node = time_script.new() as Node
	var weather_manager: Node = weather_script.new() as Node
	root.add_child(time_manager)
	root.add_child(weather_manager)

	for method_name in ["get_current_season", "get_date_info", "get_time_text", "advance_minutes", "sleep_to_next_day"]:
		if not time_manager.has_method(method_name):
			_fail("TimeManager missing method %s" % method_name)
			return
	for method_name in ["set_today_weather", "should_auto_water_today", "advance_to_next_day", "get_today_weather"]:
		if not weather_manager.has_method(method_name):
			_fail("WeatherManager missing method %s" % method_name)
			return

	_expect(time_manager.get_current_season() == "spring", "default season should be spring")
	if _has_failed:
		return
	_expect(time_manager.get_date_info().get("day_of_season") == 1, "default day_of_season should be 1")
	if _has_failed:
		return
	_expect(time_manager.get_time_text() == "06:00", "day should start at 06:00")
	if _has_failed:
		return

	time_manager.advance_minutes(180)
	_expect(time_manager.get_date_info().get("block") == "late_morning", "09:00 should be late_morning")
	if _has_failed:
		return
	time_manager.advance_minutes(480)
	_expect(time_manager.get_date_info().get("block") == "evening", "17:00 should be evening")
	if _has_failed:
		return

	weather_manager.set_today_weather("rainy")
	_expect(weather_manager.should_auto_water_today(), "rainy weather should set auto-water flag")
	if _has_failed:
		return
	weather_manager.set_today_weather("sunny")
	_expect(not weather_manager.should_auto_water_today(), "sunny weather should clear auto-water flag")
	if _has_failed:
		return

	weather_manager.set_today_weather("sunny")
	weather_manager.tomorrow_weather = "rainy"
	time_manager.sleep_to_next_day()
	weather_manager.advance_to_next_day(time_manager.get_date_info())
	_expect(time_manager.get_date_info().get("day_of_season") == 2, "sleep should advance to day 2")
	if _has_failed:
		return
	_expect(time_manager.get_time_text() == "06:00", "sleep should reset time to 06:00")
	if _has_failed:
		return
	_expect(weather_manager.get_today_weather() == "rainy", "today weather should become previous tomorrow weather")
	if _has_failed:
		return
	_expect(weather_manager.should_auto_water_today(), "rainy next day should enable auto-water")
	if _has_failed:
		return

	time_manager.day_of_season = 28
	time_manager.sleep_to_next_day()
	_expect(time_manager.get_current_season() == "summer", "day 29 should become summer day 1")
	if _has_failed:
		return
	_expect(time_manager.get_date_info().get("day_of_season") == 1, "season rollover should reset day to 1")
	if _has_failed:
		return

	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	if yard_scene == null:
		_fail("could not load PlayerYard")
		return
	var yard: Node = yard_scene.instantiate()
	root.add_child(yard)
	var hud := yard.get_node_or_null("TimeWeatherHUD")
	if hud == null:
		_fail("PlayerYard missing TimeWeatherHUD")
		return
	if not hud.has_method("refresh"):
		_fail("TimeWeatherHUD missing refresh")
		return
	hud.refresh()
	var season_label := hud.get_node_or_null("Panel/Content/SeasonLabel")
	var weather_label := hud.get_node_or_null("Panel/Content/WeatherLabel")
	if season_label == null or weather_label == null:
		_fail("HUD missing season/weather labels")
		return
	_expect(not String(season_label.text).is_empty(), "season label should display text")
	if _has_failed:
		return
	_expect(not String(weather_label.text).is_empty(), "weather label should display text")
	if _has_failed:
		return

	var bed := yard.get_node_or_null("Bed")
	if bed == null:
		_fail("PlayerYard missing bed")
		return
	var yard_time := yard.get_node_or_null("TimeManager")
	var before_day := int(yard_time.get_date_info().get("day_of_season"))
	bed.on_interact(yard.get_node("Player"))
	var after_day := int(yard_time.get_date_info().get("day_of_season"))
	_expect(after_day == before_day + 1, "bed interaction should advance to next day")
	if _has_failed:
		return

	print("OK: Godot validated Task 005 time, weather, sleep, and HUD")
	quit(0)


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_fail(message)


func _fail(message: String) -> void:
	if _has_failed:
		return
	_has_failed = true
	push_error(message)
	print("FAIL: %s" % message)
	quit(1)
