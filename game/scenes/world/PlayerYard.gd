class_name PlayerYard
extends Node2D

@export var starter_seed_item_id: String = "seed_turnip"
@export var starter_seed_count: int = 6
@export var aoi_turnip_reward_item_id: String = "seed_strawberry"
@export var aoi_turnip_reward_count: int = 1

const VILLAGE_SOFT_CLUE_FLAG: String = "found_village_soft_clue_day1"
const VILLAGE_RETURN_FLAG: String = "returned_from_village_day1"
const VILLAGE_OLD_WELL_ECHO_FLAG: String = "heard_old_well_echo_after_village_clue_day1"

@onready var data_registry: Node = get_node_or_null("DataRegistry")
@onready var inventory_manager: Node = get_node_or_null("InventoryManager")
@onready var weather_manager: Node = get_node_or_null("WeatherManager")
@onready var time_manager: Node = get_node_or_null("TimeManager")
@onready var dialogue_manager: Node = get_node_or_null("DialogueManager")
@onready var relationship_manager: Node = get_node_or_null("RelationshipManager")
@onready var rumor_manager: Node = get_node_or_null("RumorManager")
@onready var game_state: Node = get_node_or_null("GameState")
@onready var save_manager: Node = get_node_or_null("SaveManager")
@onready var time_weather_hud: Node = get_node_or_null("TimeWeatherHUD")
@onready var inventory_ui: Node = get_node_or_null("InventoryUI")
@onready var dialogue_box: Node = get_node_or_null("DialogueBox")
@onready var farm_plots: Node = get_node_or_null("FarmPlots")
@onready var npcs: Node = get_node_or_null("NPCs")
@onready var bed: Node = get_node_or_null("Bed")
@onready var mailbox: Node = get_node_or_null("Mailbox")
@onready var bulletin_board: Node = get_node_or_null("BulletinBoard")
@onready var old_well: Node = get_node_or_null("OldWell")
@onready var schedule_director: Node = get_node_or_null("ScheduleDirector")
@onready var player: Node = get_node_or_null("Player")


func _ready() -> void:
	_ensure_data_loaded()
	_ensure_starter_inventory()
	_bind_social_managers()
	_bind_rumor_manager()
	_connect_runtime_signals()
	refresh_runtime_ui()


func advance_farm_plots_for_new_day() -> void:
	var auto_water := false
	if weather_manager != null and weather_manager.has_method("should_auto_water_today"):
		auto_water = bool(weather_manager.should_auto_water_today())
	for plot in farm_plots.get_children():
		if plot.has_method("advance_day"):
			plot.advance_day(auto_water)
	refresh_runtime_ui()


func refresh_runtime_ui() -> void:
	if inventory_ui != null:
		if inventory_ui.has_method("bind_managers"):
			inventory_ui.bind_managers(inventory_manager, data_registry)
		if inventory_ui.has_method("refresh"):
			inventory_ui.refresh()
	if time_weather_hud != null and time_weather_hud.has_method("refresh"):
		if time_weather_hud.has_method("bind_managers"):
			time_weather_hud.bind_managers(time_manager, weather_manager)
		time_weather_hud.refresh()


func save_game(path: String = SaveManager.DEFAULT_SAVE_PATH) -> bool:
	if save_manager == null or not save_manager.has_method("save_game"):
		return false
	return bool(save_manager.save_game(self, path))


func load_game(path: String = SaveManager.DEFAULT_SAVE_PATH) -> bool:
	if save_manager == null or not save_manager.has_method("load_game"):
		return false
	var did_load := bool(save_manager.load_game(self, path))
	if did_load:
		refresh_runtime_ui()
	return did_load


func _unhandled_input(_event: InputEvent) -> void:
	if Input.is_action_just_pressed("open_inventory"):
		toggle_inventory_panel()
	elif Input.is_action_just_pressed("debug_save"):
		save_game()
	elif Input.is_action_just_pressed("debug_load"):
		load_game()


func toggle_inventory_panel() -> void:
	if inventory_ui == null:
		return
	inventory_ui.visible = not bool(inventory_ui.visible)
	if inventory_ui.visible and inventory_ui.has_method("refresh"):
		inventory_ui.refresh()


func show_mailbox_rumors() -> void:
	if rumor_manager == null or dialogue_box == null:
		return
	if not rumor_manager.has_method("build_rumor_dialogue"):
		return
	var dialogue: Dictionary = rumor_manager.build_rumor_dialogue("mailbox")
	if dialogue_box.has_method("show_dialogue"):
		dialogue_box.show_dialogue(dialogue, {
			"npc_name": "邮箱",
			"portrait": "",
		})
	if rumor_manager.has_method("mark_dialogue_rumors_seen"):
		rumor_manager.mark_dialogue_rumors_seen(dialogue)


func show_bulletin_rumors() -> Dictionary:
	if bulletin_board != null and bulletin_board.has_method("show_rumors"):
		return bulletin_board.show_rumors()
	if rumor_manager == null or dialogue_box == null:
		return {}
	if not rumor_manager.has_method("build_rumor_dialogue"):
		return {}
	var dialogue: Dictionary = rumor_manager.build_rumor_dialogue("bulletin")
	if dialogue_box.has_method("show_dialogue"):
		dialogue_box.show_dialogue(dialogue, {
			"npc_name": "公告板",
			"portrait": "",
		})
	if rumor_manager.has_method("mark_dialogue_rumors_seen"):
		rumor_manager.mark_dialogue_rumors_seen(dialogue)
	return dialogue


func _ensure_data_loaded() -> void:
	if data_registry == null:
		return
	if data_registry.has_method("load_all_data") and not bool(data_registry.get("is_loaded")):
		data_registry.load_all_data()
	if data_registry.has_method("validate_all_data"):
		data_registry.validate_all_data()


func _ensure_starter_inventory() -> void:
	if inventory_manager == null:
		return
	if inventory_manager.has_method("get_count") and inventory_manager.get_count(starter_seed_item_id) < starter_seed_count:
		var missing_count: int = starter_seed_count - int(inventory_manager.get_count(starter_seed_item_id))
		inventory_manager.add_item(starter_seed_item_id, missing_count)
	if inventory_manager.has_method("set_selected_item"):
		inventory_manager.set_selected_item(starter_seed_item_id)


func _connect_runtime_signals() -> void:
	if bed != null and bed.has_signal("sleep_completed") and not bed.sleep_completed.is_connected(_on_bed_sleep_completed):
		bed.sleep_completed.connect(_on_bed_sleep_completed)
	if mailbox != null and mailbox.has_signal("interacted") and not mailbox.interacted.is_connected(_on_mailbox_interacted):
		mailbox.interacted.connect(_on_mailbox_interacted)
	if old_well != null and old_well.has_signal("interacted") and not old_well.interacted.is_connected(_on_old_well_interacted):
		old_well.interacted.connect(_on_old_well_interacted)
	_connect_farm_plot_progress_signals()
	_connect_npc_progress_signals()
	if time_manager != null and relationship_manager != null:
		if time_manager.has_signal("day_started") and relationship_manager.has_method("reset_daily_social_state"):
			if not time_manager.day_started.is_connected(_on_day_started):
				time_manager.day_started.connect(_on_day_started)


func _connect_farm_plot_progress_signals() -> void:
	if farm_plots == null:
		return
	for plot in farm_plots.get_children():
		if plot.has_signal("plot_changed") and not plot.plot_changed.is_connected(_on_farm_plot_changed):
			plot.plot_changed.connect(_on_farm_plot_changed)
		if plot.has_signal("crop_harvested") and not plot.crop_harvested.is_connected(_on_farm_plot_harvested):
			plot.crop_harvested.connect(_on_farm_plot_harvested)


func _connect_npc_progress_signals() -> void:
	if npcs == null:
		return
	for npc in npcs.get_children():
		if npc.has_signal("gift_given") and not npc.gift_given.is_connected(_on_npc_gift_given):
			npc.gift_given.connect(_on_npc_gift_given)


func _on_bed_sleep_completed(_date_info: Dictionary, _weather_info: Dictionary) -> void:
	advance_farm_plots_for_new_day()


func _on_mailbox_interacted(_interactor: Node, _interactable_id: String) -> void:
	if game_state != null and game_state.has_method("set_flag"):
		game_state.set_flag("read_mailbox_day1", true)
	show_mailbox_rumors()


func _on_old_well_interacted(_interactor: Node, _interactable_id: String) -> void:
	_try_village_clue_old_well_echo()


func _try_village_clue_old_well_echo() -> void:
	if game_state == null or not game_state.has_method("set_flag"):
		return
	if game_state.has_method("is_restored") and not game_state.is_restored("old_well"):
		return
	if game_state.has_method("get_flag"):
		if not bool(game_state.get_flag(VILLAGE_SOFT_CLUE_FLAG, false)):
			return
		if not bool(game_state.get_flag(VILLAGE_RETURN_FLAG, false)):
			return
		if bool(game_state.get_flag(VILLAGE_OLD_WELL_ECHO_FLAG, false)):
			return
	game_state.set_flag(VILLAGE_OLD_WELL_ECHO_FLAG, true)
	call_deferred("_show_village_clue_old_well_echo")


func _show_village_clue_old_well_echo() -> void:
	if dialogue_box == null or not dialogue_box.has_method("show_dialogue"):
		return
	var dialogue := {
		"dialogue_id": "village_clue_old_well_echo",
		"npc_id": "system",
		"lines": [
			{
				"speaker": "system",
				"text": "井边很安静，只在风停下来的时候轻轻响了一下。旧枫树小牌上的字，像是在提醒你明天再问问美香。",
			},
		],
	}
	dialogue_box.show_dialogue(dialogue, {"npc_name": "旧水井", "portrait": ""})


func _on_farm_plot_changed(_plot_index: int, state_name: String) -> void:
	if state_name != "watered":
		return
	_mark_first_week_crop_watered()
	_mark_aoi_strawberry_planted(_plot_index, state_name)


func _mark_first_week_crop_watered() -> void:
	if game_state == null or not game_state.has_method("set_flag"):
		return
	if game_state.has_method("is_restored") and not game_state.is_restored("old_well"):
		return
	if game_state.has_method("get_flag") and bool(game_state.get_flag("watered_first_crop_day1", false)):
		return
	game_state.set_flag("watered_first_crop_day1", true)
	if inventory_manager != null and inventory_manager.has_method("set_selected_item"):
		inventory_manager.set_selected_item("")


func _mark_aoi_strawberry_planted(plot_index: int, state_name: String) -> void:
	if state_name != "watered":
		return
	if game_state == null or not game_state.has_method("set_flag"):
		return
	if plot_index != 1:
		return
	if game_state.has_method("is_restored") and not game_state.is_restored("old_well"):
		return
	if game_state.has_method("get_flag"):
		if not bool(game_state.get_flag("shared_first_turnip_day1", false)):
			return
		if bool(game_state.get_flag("planted_aoi_strawberry_day1", false)):
			return
	var plot := _get_farm_plot_by_index(plot_index)
	if plot == null:
		return
	if String(plot.get("seed_item_id")) != "seed_strawberry":
		return
	if String(plot.get("crop_id")) != "strawberry_spring":
		return
	game_state.set_flag("planted_aoi_strawberry_day1", true)
	if inventory_manager != null and inventory_manager.has_method("set_selected_item"):
		inventory_manager.set_selected_item("")


func _get_farm_plot_by_index(plot_index: int) -> Node:
	if farm_plots == null:
		return null
	for plot in farm_plots.get_children():
		if int(plot.get("plot_index")) == plot_index:
			return plot
	return null


func _on_farm_plot_harvested(_plot_index: int, item_id: String, count: int) -> void:
	_show_item_gain_feedback(item_id, count)
	_mark_first_week_crop_harvested()


func _mark_first_week_crop_harvested() -> void:
	if game_state == null or not game_state.has_method("set_flag"):
		return
	if game_state.has_method("is_restored") and not game_state.is_restored("old_well"):
		return
	if game_state.has_method("get_flag"):
		if not bool(game_state.get_flag("watered_first_crop_day1", false)):
			return
		if bool(game_state.get_flag("harvested_first_crop_day1", false)):
			return
	game_state.set_flag("harvested_first_crop_day1", true)


func _on_npc_gift_given(npc_id: String, item_id: String, _delta: int, already_gifted: bool) -> void:
	if already_gifted:
		return
	if npc_id != "aoi" or item_id != "crop_turnip":
		return
	_mark_first_week_turnip_shared()


func _mark_first_week_turnip_shared() -> void:
	if game_state == null or not game_state.has_method("set_flag"):
		return
	if game_state.has_method("is_restored") and not game_state.is_restored("old_well"):
		return
	if game_state.has_method("get_flag"):
		if not bool(game_state.get_flag("watered_first_crop_day1", false)):
			return
		if not bool(game_state.get_flag("harvested_first_crop_day1", false)):
			return
		if bool(game_state.get_flag("shared_first_turnip_day1", false)):
			return
	game_state.set_flag("shared_first_turnip_day1", true)
	_grant_aoi_turnip_thanks_reward()
	_show_aoi_turnip_thanks_feedback()


func _grant_aoi_turnip_thanks_reward() -> void:
	if inventory_manager == null or not inventory_manager.has_method("add_item"):
		return
	if aoi_turnip_reward_item_id.is_empty() or aoi_turnip_reward_count <= 0:
		return
	inventory_manager.add_item(aoi_turnip_reward_item_id, aoi_turnip_reward_count)
	if inventory_ui != null and inventory_ui.has_method("refresh"):
		inventory_ui.refresh()


func _show_aoi_turnip_thanks_feedback() -> void:
	if dialogue_box == null or not dialogue_box.has_method("show_dialogue"):
		return
	var reward_name := _get_item_display_name(aoi_turnip_reward_item_id)
	var dialogue := {
		"dialogue_id": "aoi_turnip_thanks_reward",
		"npc_id": "aoi",
		"lines": [
			{
				"speaker": "aoi",
				"text": "葵收下春萝卜，回赠了%s x%d。她说：下次也可以试试草莓。" % [reward_name, aoi_turnip_reward_count],
			},
		],
	}
	dialogue_box.show_dialogue(dialogue, {"npc_name": "葵", "portrait": ""})


func _show_item_gain_feedback(item_id: String, count: int) -> void:
	if dialogue_box == null or not dialogue_box.has_method("show_dialogue"):
		return
	var item_name := _get_item_display_name(item_id)
	var dialogue := {
		"dialogue_id": "harvest_gain_%s" % item_id,
		"npc_id": "system",
		"lines": [
			{
				"speaker": "system",
				"text": "收获：%s x%d，已经放进背包。" % [item_name, count],
			},
		],
	}
	dialogue_box.show_dialogue(dialogue, {"npc_name": "背包", "portrait": ""})


func _get_item_display_name(item_id: String) -> String:
	if data_registry != null and data_registry.has_method("get_item"):
		var item_data: Dictionary = data_registry.get_item(item_id)
		var item_name := String(item_data.get("name", ""))
		if not item_name.is_empty():
			return item_name
	return item_id


func _on_day_started(_date_info: Dictionary) -> void:
	if relationship_manager != null and relationship_manager.has_method("reset_daily_social_state"):
		relationship_manager.reset_daily_social_state()
	if rumor_manager != null and rumor_manager.has_method("refresh_daily_rumors"):
		rumor_manager.refresh_daily_rumors()
	if schedule_director != null and schedule_director.has_method("apply_schedule"):
		schedule_director.apply_schedule()


func _bind_social_managers() -> void:
	if dialogue_manager != null:
		if dialogue_manager.has_method("bind_registry"):
			dialogue_manager.bind_registry(data_registry)
		if dialogue_manager.has_method("bind_relationship_manager"):
			dialogue_manager.bind_relationship_manager(relationship_manager)


func _bind_rumor_manager() -> void:
	if rumor_manager == null:
		return
	if rumor_manager.has_method("bind_registry"):
		rumor_manager.bind_registry(data_registry)
	if rumor_manager.has_method("bind_game_state"):
		rumor_manager.bind_game_state(game_state)
	if rumor_manager.has_method("bind_time_manager"):
		rumor_manager.bind_time_manager(time_manager)
	if rumor_manager.has_method("bind_weather_manager"):
		rumor_manager.bind_weather_manager(weather_manager)
