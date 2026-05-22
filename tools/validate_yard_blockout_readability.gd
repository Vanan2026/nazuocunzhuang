extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const YARD_PATH := "res://game/scenes/world/PlayerYard.tscn"
const WATCHDOG_TIMEOUT_SECONDS := 25.0

var _has_failed := false
var _finished := false
var _watchdog_timer: Timer = null


func _initialize() -> void:
	print("PROGRESS: yard blockout readability initialize")
	call_deferred("_start_watchdog")
	call_deferred("_run")


func _run() -> void:
	var yard_scene := load(YARD_PATH) as PackedScene
	_expect(yard_scene != null, "PlayerYard scene should load")
	if _has_failed:
		return

	var yard := yard_scene.instantiate()
	root.add_child(yard)
	await process_frame
	await process_frame
	await process_frame

	await _validate_default_ui_state(yard)
	if _has_failed:
		return
	_validate_layout_relationships(yard)
	if _has_failed:
		return
	_validate_npc_scale(yard)
	if _has_failed:
		return
	await _validate_npc_schedule_readability(yard)
	if _has_failed:
		return

	print("OK: yard blockout readability runtime validation passed")
	_finish_deferred(0)


func _validate_default_ui_state(yard: Node) -> void:
	var inventory_ui := yard.get_node_or_null("InventoryUI")
	var dialogue_box := yard.get_node_or_null("DialogueBox")
	var legacy_gate := yard.get_node_or_null("BackToOldWorld") as Area2D
	var bed := yard.get_node_or_null("Bed") as Area2D
	_expect(inventory_ui != null, "PlayerYard should include InventoryUI")
	_expect(dialogue_box != null, "PlayerYard should include DialogueBox")
	_expect(legacy_gate != null, "PlayerYard should keep the legacy gate node explicit")
	_expect(bed != null, "PlayerYard should keep the legacy bed node explicit")
	if _has_failed:
		return
	_expect(not bool(inventory_ui.get("visible")), "InventoryUI should start hidden in normal play")
	_expect(not bool(dialogue_box.get("visible")), "DialogueBox should start hidden")
	var dialogue_panel := dialogue_box.get_node_or_null("Panel") as Control
	_expect(dialogue_panel != null, "DialogueBox should include a compact panel")
	if _has_failed:
		return
	_expect(dialogue_panel.offset_top >= 580.0, "DialogueBox should sit at the bottom edge")
	_expect(dialogue_panel.offset_right <= 640.0, "DialogueBox should leave lower-middle playfield clear")
	_expect(dialogue_panel.offset_bottom - dialogue_panel.offset_top <= 132.0, "DialogueBox should stay compact")
	_expect(not bool(legacy_gate.visible), "BackToOldWorld should be hidden from normal yard play")
	_expect(not bool(legacy_gate.monitoring), "BackToOldWorld should not monitor interactions in normal yard play")
	_expect(not bool(bed.visible), "Bed should not render in the yard now that Main starts in PlayerHouse")
	_expect(not bool(bed.monitoring), "Bed should not monitor yard interactions now that sleep belongs indoors")
	_expect(yard.has_method("toggle_inventory_panel"), "PlayerYard should expose inventory panel toggling")
	if _has_failed:
		return
	yard.toggle_inventory_panel()
	await process_frame
	_expect(bool(inventory_ui.get("visible")), "toggle_inventory_panel should show InventoryUI")
	yard.toggle_inventory_panel()
	await process_frame
	_expect(not bool(inventory_ui.get("visible")), "toggle_inventory_panel should hide InventoryUI")


func _validate_layout_relationships(yard: Node) -> void:
	var structure := yard.get_node_or_null("YardStructure")
	_expect(structure != null, "PlayerYard should include YardStructure blockout zones")
	if _has_failed:
		return
	var route_network := structure.get_node_or_null("RoutePathNetwork")
	_expect(route_network != null, "YardStructure should include a first-week route path network")
	if _has_failed:
		return
	for path_name in [
		"MailboxNoticeRepairPath",
		"RepairForestPath",
		"FarmBranchPath",
		"ResourceBranchPath",
	]:
		_expect(route_network.get_node_or_null(path_name) != null, "RoutePathNetwork missing path: %s" % path_name)
		if _has_failed:
			return
	for zone_name in [
		"HomeApproachZone",
		"SocialNoticeZone",
		"FarmGardenZone",
		"RepairYardZone",
		"ForestTrailZone",
		"ResourceStagingZone",
	]:
		_expect(structure.get_node_or_null(zone_name) != null, "YardStructure missing zone: %s" % zone_name)
		if _has_failed:
			return

	var spawn := yard.get_node_or_null("SpawnFromHouse") as Node2D
	var mailbox := yard.get_node_or_null("Mailbox") as Node2D
	var bulletin := yard.get_node_or_null("BulletinBoard") as Node2D
	var farm_plots := yard.get_node_or_null("FarmPlots") as Node2D
	var old_well := yard.get_node_or_null("OldWell") as Node2D
	var bench := yard.get_node_or_null("GardenBenchRepair") as Node2D
	var sign := yard.get_node_or_null("VillageSignRepair") as Node2D
	var forest_gate := yard.get_node_or_null("ForestTrailGate") as Node2D
	for pair in {
		"SpawnFromHouse": spawn,
		"Mailbox": mailbox,
		"BulletinBoard": bulletin,
		"FarmPlots": farm_plots,
		"OldWell": old_well,
		"GardenBenchRepair": bench,
		"VillageSignRepair": sign,
		"ForestTrailGate": forest_gate,
	}.keys():
		var node: Node = {
			"SpawnFromHouse": spawn,
			"Mailbox": mailbox,
			"BulletinBoard": bulletin,
			"FarmPlots": farm_plots,
			"OldWell": old_well,
			"GardenBenchRepair": bench,
			"VillageSignRepair": sign,
			"ForestTrailGate": forest_gate,
		}[pair]
		_expect(node != null, "PlayerYard missing layout node: %s" % pair)
		if _has_failed:
			return

	_expect(spawn.position.distance_to(mailbox.position) <= 80.0, "first yard step should put mailbox near house spawn")
	_expect(mailbox.position.distance_to(bulletin.position) >= 56.0, "mailbox and bulletin should read as separate first-week stops")
	_expect(farm_plots.position.x < old_well.position.x - 140.0, "farm block should sit away from repair well block")
	_expect(forest_gate.position.x > bulletin.position.x + 170.0, "forest trail should read as an east-side route beyond the notice area")
	_expect(bench.position.y > old_well.position.y + 36.0, "bench repair should sit below the well in the repair yard")
	_expect(sign.position.distance_to(forest_gate.position) <= 72.0, "village sign repair should visually point toward the forest trail gate")


func _validate_npc_scale(yard: Node) -> void:
	var npc_root := yard.get_node_or_null("NPCs")
	_expect(npc_root != null, "PlayerYard should include NPCs")
	if _has_failed:
		return
	for npc in npc_root.get_children():
		var sprite := npc.get_node_or_null("Sprite2D") as Sprite2D
		_expect(sprite != null, "%s should include Sprite2D" % npc.name)
		if _has_failed:
			return
		_expect(sprite.scale.x <= 0.55 and sprite.scale.y <= 0.55, "%s sprite should match player-scale blockout" % npc.name)


func _validate_npc_schedule_readability(yard: Node) -> void:
	var schedule_director := yard.get_node_or_null("ScheduleDirector")
	var npc_root := yard.get_node_or_null("NPCs")
	var hana := yard.get_node_or_null("NPCs/Hana")
	_expect(schedule_director != null, "PlayerYard should include ScheduleDirector")
	_expect(npc_root != null, "PlayerYard should include NPC root")
	_expect(hana != null, "PlayerYard should include Hana so morning yard is not empty")
	if _has_failed:
		return

	schedule_director.apply_schedule("morning")
	await process_frame
	_expect(bool(hana.visible), "Hana should occupy the yard in the morning block")
	var morning_visible_count := 0
	for npc in npc_root.get_children():
		if bool(npc.visible):
			morning_visible_count += 1
	_expect(morning_visible_count == 1, "morning yard should not be crowded with off-schedule NPCs")

	schedule_director.apply_schedule("late_morning")
	await process_frame
	var visible_npcs: Array[Node2D] = []
	for npc in npc_root.get_children():
		if npc is Node2D and bool(npc.visible):
			visible_npcs.append(npc as Node2D)
	_expect(visible_npcs.size() >= 3, "late morning should place several readable villagers in the yard")
	for left_index in range(visible_npcs.size()):
		for right_index in range(left_index + 1, visible_npcs.size()):
			var left := visible_npcs[left_index]
			var right := visible_npcs[right_index]
			_expect(left.position.distance_to(right.position) >= 64.0, "visible NPC schedule positions should not overlap: %s/%s" % [left.name, right.name])


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
			_fail("Yard blockout readability validation timed out")
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
