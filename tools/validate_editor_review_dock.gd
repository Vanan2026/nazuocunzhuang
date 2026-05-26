extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const PLUGIN_SCRIPT_PATH := "res://addons/village_layer_tool/village_layer_tool_plugin.gd"
const PLUGIN_CFG_PATH := "res://addons/village_layer_tool/plugin.cfg"

var _finished := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	if not FileAccess.file_exists(PLUGIN_CFG_PATH):
		_fail("Missing plugin.cfg")
		return
	if not FileAccess.file_exists(PLUGIN_SCRIPT_PATH):
		_fail("Missing village layer tool plugin script")
		return

	var script := load(PLUGIN_SCRIPT_PATH)
	if script == null:
		_fail("Could not load review dock plugin script")
		return
	if not script is GDScript:
		_fail("Plugin script should load as GDScript")
		return

	var source := FileAccess.open(PLUGIN_SCRIPT_PATH, FileAccess.READ)
	if source == null:
		_fail("Could not read plugin source")
		return
	var text := source.get_as_text()
	for snippet in [
		"PROJECT_REVIEW_SCENES",
		"VALIDATION_COMMANDS",
		"_create_review_dock",
		"_open_review_scene",
		"_copy_validation_commands",
		"_refresh_review_status",
	]:
		if not text.contains(snippet):
			_fail("Plugin source missing snippet: %s" % snippet)
			return

	print("OK: editor review dock runtime validation passed")
	_finish_deferred(0)


func _fail(message: String) -> void:
	push_error(message)
	print("FAIL: %s" % message)
	_finish_deferred(1)


func _finish_deferred(exit_code: int) -> void:
	if _finished:
		return
	_finished = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
