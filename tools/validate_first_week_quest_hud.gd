extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 20.0
const REQUIRED_OBJECTIVE_TEXTS: Array[String] = [
	"读邮箱",
	"看公告板",
	"修旧井",
	"给第一块作物浇水",
	"收获第一棵作物",
	"把第一根萝卜送给葵",
	"种下葵送的草莓",
	"修长椅",
	"扶正路牌",
	"读森林边缘公告",
	"去森林边缘",
	"听 Mika 的传闻",
	"去村口看公告",
]
const REQUIRED_OBJECTIVE_IDS: Array[String] = [
	"read_mailbox_day1",
	"read_bulletin_day1",
	"old_well_restored",
	"watered_first_crop_day1",
	"harvested_first_crop_day1",
	"shared_first_turnip_day1",
	"planted_aoi_strawberry_day1",
	"garden_bench_restored",
	"village_sign_restored",
	"heard_forest_edge_notice",
	"visited_forest_edge",
	"heard_npc_forest_edge",
	"read_village_notice_day1",
]

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: first-week quest HUD initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var main_scene = load(MAIN_PATH) as PackedScene
	_expect(main_scene != null, "Main scene should load")
	if _has_failed:
		return

	var main = main_scene.instantiate()
	root.add_child(main)
	await process_frame
	await process_frame

	var hud := main.get_node_or_null("FirstWeekQuestHUD")
	var quest_manager := main.get_node_or_null("QuestManager")
	var game_state := main.get_node_or_null("GameState")
	var scene_router := main.get_node_or_null("SceneRouter")
	_expect(hud != null, "Main should include FirstWeekQuestHUD")
	_expect(quest_manager != null, "Main should include QuestManager")
	_expect(game_state != null, "Main should include GameState")
	_expect(scene_router != null, "Main should include SceneRouter")
	if _has_failed:
		return

	_expect(hud is CanvasLayer, "FirstWeekQuestHUD should render as CanvasLayer")
	_expect(not bool(hud.get("visible")), "FirstWeekQuestHUD should start hidden for normal play")
	_expect(hud.has_method("get_visible_objective_texts"), "FirstWeekQuestHUD should expose visible objective text")
	_expect(hud.has_method("is_objective_complete"), "FirstWeekQuestHUD should expose objective completion checks")
	_expect(hud.has_method("refresh"), "FirstWeekQuestHUD should expose refresh")
	if _has_failed:
		return

	hud.show()
	await process_frame
	_expect(bool(hud.get("visible")), "FirstWeekQuestHUD should still be available as a debug overlay")
	if _has_failed:
		return

	quest_manager.update_first_week_progress(game_state, scene_router)
	hud.refresh()
	await process_frame

	var visible_texts: Array = hud.get_visible_objective_texts()
	for objective_text in REQUIRED_OBJECTIVE_TEXTS:
		_expect(_texts_contain(visible_texts, objective_text), "HUD should show objective text: %s" % objective_text)
	if _has_failed:
		return

	_expect(not bool(hud.is_objective_complete("read_mailbox_day1")), "Mailbox objective should start incomplete")
	_mark_first_week_progress(game_state, scene_router)
	quest_manager.update_first_week_progress(game_state, scene_router)
	hud.refresh()
	await process_frame

	for objective_id in REQUIRED_OBJECTIVE_IDS:
		_expect(bool(hud.is_objective_complete(objective_id)), "HUD should mark complete: %s" % objective_id)
	if _has_failed:
		return

	var progress_label := hud.get_node_or_null("Panel/Content/ProgressLabel") as Label
	_expect(progress_label != null, "HUD should include ProgressLabel")
	_expect(progress_label.text.contains("/"), "HUD progress should show completed/total")
	_expect(progress_label.text.contains("13"), "HUD progress should include all first-week objectives")
	if _has_failed:
		return

	print("OK: first-week quest HUD runtime validation passed")
	_finish_deferred(0)


func _mark_first_week_progress(game_state: Node, scene_router: Node) -> void:
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_flag("watered_first_crop_day1", true)
	game_state.set_flag("harvested_first_crop_day1", true)
	game_state.set_flag("shared_first_turnip_day1", true)
	game_state.set_flag("planted_aoi_strawberry_day1", true)
	game_state.set_flag("heard_forest_edge_notice", true)
	game_state.set_flag("visited_forest_edge", true)
	game_state.set_flag("heard_npc_forest_edge", true)
	game_state.set_flag("read_village_notice_day1", true)
	game_state.set_restored("old_well", true)
	game_state.set_restored("garden_bench", true)
	game_state.set_restored("village_sign", true)
	scene_router.set_current_scene("forest_edge", "from_yard")


func _texts_contain(texts: Array, needle: String) -> bool:
	for text in texts:
		if String(text).contains(needle):
			return true
	return false


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
			_fail("First-week quest HUD validation timed out")
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
