extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const MAIN_PATH := "res://game/scenes/Main.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0
const REQUIRED_OBJECTIVE_TEXTS: Array[String] = [
	"读邮箱",
	"看公告板",
	"修旧井",
	"修长椅",
	"扶正路牌",
	"去森林边缘",
	"听 Mika 的传闻",
]

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: quest journal UI initialize")
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

	var journal := main.get_node_or_null("QuestJournalUI")
	var quest_manager := main.get_node_or_null("QuestManager")
	var game_state := main.get_node_or_null("GameState")
	var scene_router := main.get_node_or_null("SceneRouter")
	_expect(InputMap.has_action("open_journal"), "project should expose open_journal input action")
	_expect(journal != null, "Main should include QuestJournalUI")
	_expect(quest_manager != null, "Main should include QuestManager")
	_expect(game_state != null, "Main should include GameState")
	_expect(scene_router != null, "Main should include SceneRouter")
	if _has_failed:
		return

	_expect(journal is CanvasLayer, "QuestJournalUI should render as CanvasLayer")
	_expect(not bool(journal.get("visible")), "QuestJournalUI should start hidden")
	_expect(journal.has_method("bind_quest_manager"), "QuestJournalUI should bind QuestManager")
	_expect(journal.has_method("toggle_journal"), "QuestJournalUI should expose toggle_journal")
	_expect(journal.has_method("show_journal"), "QuestJournalUI should expose show_journal")
	_expect(journal.has_method("hide_journal"), "QuestJournalUI should expose hide_journal")
	_expect(journal.has_method("get_current_goal_text"), "QuestJournalUI should expose current goal text")
	_expect(journal.has_method("get_visible_objective_texts"), "QuestJournalUI should expose objective texts")
	if _has_failed:
		return

	quest_manager.update_first_week_progress(game_state, scene_router)
	journal.show_journal()
	await process_frame
	_expect(bool(journal.get("visible")), "show_journal should make the panel visible")
	_expect(String(journal.get_current_goal_text()).contains("读邮箱"), "Initial current goal should be read mailbox")
	var visible_texts: Array = journal.get_visible_objective_texts()
	for objective_text in REQUIRED_OBJECTIVE_TEXTS:
		_expect(_texts_contain(visible_texts, objective_text), "Journal should show objective text: %s" % objective_text)
	if _has_failed:
		return

	game_state.set_flag("read_mailbox_day1", true)
	quest_manager.update_first_week_progress(game_state, scene_router)
	journal.refresh()
	await process_frame
	_expect(String(journal.get_current_goal_text()).contains("看公告板"), "Current goal should advance after mailbox")
	if _has_failed:
		return

	_mark_first_week_complete(game_state, scene_router)
	quest_manager.update_first_week_progress(game_state, scene_router)
	journal.refresh()
	await process_frame
	_expect(String(journal.get_current_goal_text()).contains("第一周主线已完成"), "Completed journal should show completion text")
	journal.toggle_journal()
	await process_frame
	_expect(not bool(journal.get("visible")), "toggle_journal should hide visible panel")
	journal.toggle_journal()
	await process_frame
	_expect(bool(journal.get("visible")), "toggle_journal should show hidden panel")
	if _has_failed:
		return

	print("OK: quest journal UI runtime validation passed")
	_finish_deferred(0)


func _mark_first_week_complete(game_state: Node, scene_router: Node) -> void:
	game_state.set_flag("read_mailbox_day1", true)
	game_state.set_flag("read_bulletin_day1", true)
	game_state.set_flag("heard_forest_edge_notice", true)
	game_state.set_flag("visited_forest_edge", true)
	game_state.set_flag("heard_npc_forest_edge", true)
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
			_fail("Quest journal UI validation timed out")
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
