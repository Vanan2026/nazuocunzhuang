extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 30.0

var _output_path := ""
var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: crop identity status cue initialize")
	_parse_args()
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene := load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main := main_scene.instantiate()
	root.add_child(main)
	await _settle()
	main.change_scene("player_yard", "from_house")
	await _settle()

	var yard: Node = main.get_current_gameplay_scene()
	_expect(yard != null and yard.name == "PlayerYard", "Main should load PlayerYard")
	if _has_failed:
		return

	var game_state: Node = yard.get_node_or_null("GameState")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	var plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot1")
	_expect(game_state != null, "Yard should include GameState")
	_expect(inventory != null, "Yard should include InventoryManager")
	_expect(plot != null, "PlayerYard should include FarmPlots/FarmPlot1")
	_expect(plot.has_method("get_crop_status_text"), "FarmPlot should expose get_crop_status_text")
	_expect(plot.has_method("get_crop_display_name"), "FarmPlot should expose get_crop_display_name")
	if _has_failed:
		return

	var cue := plot.get_node_or_null("CropStatusCue") as Label
	_expect(cue != null, "FarmPlot should include CropStatusCue")
	if _has_failed:
		return
	_expect(not cue.visible, "CropStatusCue should stay hidden before a crop is planted")

	_set_pre_strawberry_flags(game_state)
	inventory.add_item("seed_strawberry", 1)
	_expect(inventory.set_selected_item("seed_strawberry"), "Player should be able to select seed_strawberry")
	_expect(plot.till(), "FarmPlot1 should till")
	_expect(plot.plant_seed("seed_strawberry"), "FarmPlot1 should plant seed_strawberry")
	await _settle()
	_expect(cue.visible, "CropStatusCue should become visible after planting")
	_expect(String(cue.text) == String(plot.get_crop_status_text()), "CropStatusCue text should match plot status API")
	_expect(not String(plot.get_crop_display_name()).is_empty(), "CropStatusCue should have a crop display name")
	_expect(String(plot.get_crop_status_text()).length() <= 24, "CropStatusCue should stay compact")
	_expect(plot.water(), "FarmPlot1 should water")
	await _settle()
	_expect(cue.visible, "CropStatusCue should remain visible after watering")
	_expect(String(cue.text) == String(plot.get_crop_status_text()), "CropStatusCue should refresh after watering")
	_expect(String(cue.text).length() <= 24, "Watered CropStatusCue should stay compact")
	if not _capture_if_requested():
		return

	print("OK: crop identity status cue runtime validation passed")
	_finish_deferred(0)


func _set_pre_strawberry_flags(game_state: Node) -> void:
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_restored("old_well", true)
	game_state.set_flag("watered_first_crop_day1", true)
	game_state.set_flag("harvested_first_crop_day1", true)
	game_state.set_flag("shared_first_turnip_day1", true)
	game_state.set_flag("planted_aoi_strawberry_day1", false)


func _settle() -> void:
	await create_timer(0.15).timeout
	await process_frame
	await process_frame


func _parse_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--out="):
			_output_path = arg.trim_prefix("--out=")


func _capture_if_requested() -> bool:
	if _output_path.is_empty():
		return true
	if DisplayServer.get_name() == "headless":
		_fail("crop identity status cue screenshot requires a display server")
		return false
	var image := root.get_texture().get_image()
	if image == null or image.is_empty():
		_fail("crop identity status cue screenshot unavailable")
		return false
	var error := image.save_png(_output_path)
	if error != OK:
		_fail("could not save crop identity status cue screenshot %s: %s" % [_output_path, error])
		return false
	print("OK: saved crop identity status cue screenshot: %s" % _output_path)
	return true


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
			_fail("Crop identity status cue validation timed out")
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
