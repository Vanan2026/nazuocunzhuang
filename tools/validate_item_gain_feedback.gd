extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const PLAYER_YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: item gain feedback initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var yard_scene: PackedScene = load(PLAYER_YARD_PATH) as PackedScene
	_expect(yard_scene != null, "PlayerYard scene should load")
	if _has_failed:
		return
	var yard: Node = yard_scene.instantiate()
	root.add_child(yard)
	await process_frame
	await process_frame

	var player: Node = yard.get_node_or_null("Player")
	var dialogue_box: Node = yard.get_node_or_null("DialogueBox")
	var wood_pile: Node = yard.get_node_or_null("WoodPile")
	var farm_plot: Node = yard.get_node_or_null("FarmPlots/FarmPlot0")
	var inventory: Node = yard.get_node_or_null("InventoryManager")
	_expect(player != null, "PlayerYard should include Player")
	_expect(dialogue_box != null, "PlayerYard should include DialogueBox")
	_expect(wood_pile != null, "PlayerYard should include WoodPile")
	_expect(farm_plot != null, "PlayerYard should include FarmPlot0")
	_expect(inventory != null, "PlayerYard should include InventoryManager")
	if _has_failed:
		return

	var before_wood := int(inventory.get_count("wood"))
	wood_pile.on_interact(player)
	await process_frame
	_expect(int(inventory.get_count("wood")) == before_wood + 32, "WoodPile should add wood")
	_expect(bool(dialogue_box.visible), "WoodPile should show item gain feedback")
	_expect(_dialogue_text(dialogue_box).contains("获得"), "WoodPile feedback should mention item gain")
	_expect(_dialogue_text(dialogue_box).contains("x32"), "WoodPile feedback should include gained count")
	if _has_failed:
		return
	dialogue_box.close()
	await process_frame

	inventory.add_item("seed_turnip", 1)
	_expect(farm_plot.till(), "FarmPlot0 should till")
	_expect(farm_plot.plant_seed("seed_turnip"), "FarmPlot0 should plant seed")
	_expect(farm_plot.water(), "FarmPlot0 should water")
	for _day in range(2):
		farm_plot.advance_day(false)
		if String(farm_plot.get_state_name()) != "ready":
			_expect(farm_plot.water(), "FarmPlot0 should be waterable until ready")
	if _has_failed:
		return
	_expect(String(farm_plot.get_state_name()) == "ready", "FarmPlot0 should be ready")
	var before_turnip := int(inventory.get_count("crop_turnip"))
	_expect(farm_plot.harvest(), "FarmPlot0 should harvest")
	await process_frame
	_expect(int(inventory.get_count("crop_turnip")) == before_turnip + 1, "Harvest should add crop_turnip")
	_expect(bool(dialogue_box.visible), "Harvest should show item gain feedback")
	_expect(_dialogue_text(dialogue_box).contains("收获"), "Harvest feedback should mention harvest")
	_expect(_dialogue_text(dialogue_box).contains("x1"), "Harvest feedback should include harvest count")
	if _has_failed:
		return

	print("OK: item gain feedback runtime validation passed")
	_finish_deferred(0)


func _dialogue_text(dialogue_box: Node) -> String:
	var line_label := dialogue_box.get_node_or_null("Panel/Content/TextColumn/LineLabel") as Label
	if line_label == null:
		return ""
	return line_label.text


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
			_fail("Item gain feedback validation timed out")
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
