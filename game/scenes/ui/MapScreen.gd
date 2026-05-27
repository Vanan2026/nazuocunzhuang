class_name MapScreen
extends CanvasLayer

const GREENFIELD_THEME: Theme = preload("res://ui/theme/greenfield_theme.tres")
const GREENFIELD_UI_THEME := preload("res://game/scenes/ui/GreenfieldUITheme.gd")
const ASSET_PATHS := preload("res://game/systems/assets/GreenfieldAssetPaths.gd")
const MAP_PIXEL_SIZE := Vector2(760.0, 480.0)

@export var data_registry_path: NodePath
@export var game_state_path: NodePath

@onready var panel: PanelContainer = get_node_or_null("Panel")
@onready var title_label: Label = get_node_or_null("Panel/Content/Header/TitleLabel")
@onready var close_button: Button = get_node_or_null("Panel/Content/Header/CloseButton")
@onready var map_panel: PanelContainer = get_node_or_null("Panel/Content/MainRow/MapPanel")
@onready var map_texture: TextureRect = get_node_or_null("Panel/Content/MainRow/MapPanel/MapTexture")
@onready var pins_layer: Control = get_node_or_null("Panel/Content/MainRow/MapPanel/Pins")
@onready var location_list: VBoxContainer = get_node_or_null("Panel/Content/MainRow/LocationList")
@onready var selected_number_label: Label = get_node_or_null("Panel/Content/MainRow/Details/SelectedNumberLabel")
@onready var selected_name_label: Label = get_node_or_null("Panel/Content/MainRow/Details/SelectedNameLabel")
@onready var selected_state_label: Label = get_node_or_null("Panel/Content/MainRow/Details/SelectedStateLabel")
@onready var selected_description_label: Label = get_node_or_null("Panel/Content/MainRow/Details/SelectedDescriptionLabel")
@onready var selected_hint_label: Label = get_node_or_null("Panel/Content/MainRow/Details/SelectedHintLabel")
@onready var selected_npcs_label: Label = get_node_or_null("Panel/Content/MainRow/Details/SelectedNpcsLabel")

var data_registry: Node = null
var game_state: Node = null
var active_map_id := ""


func _ready() -> void:
	if not data_registry_path.is_empty():
		data_registry = get_node_or_null(data_registry_path)
	if not game_state_path.is_empty():
		game_state = get_node_or_null(game_state_path)
	bind_managers(data_registry, game_state)
	_apply_greenfield_style()
	refresh()


func bind_managers(next_data_registry: Node, next_game_state: Node = null) -> void:
	data_registry = next_data_registry
	game_state = next_game_state
	if data_registry != null and data_registry.has_method("load_all_data") and not bool(data_registry.get("is_loaded")):
		data_registry.load_all_data()


func open_map() -> void:
	visible = true
	refresh()


func close_map() -> void:
	visible = false


func refresh() -> void:
	_ensure_nodes()
	if panel == null or pins_layer == null or location_list == null:
		return
	_apply_greenfield_style()
	var locations := _get_map_locations()
	if active_map_id.is_empty() and not locations.is_empty():
		active_map_id = String(locations[0].get("map_id", ""))
	_rebuild_location_list(locations)
	_rebuild_pins(locations)
	_show_location(active_map_id)


func select_location(map_id: String) -> bool:
	active_map_id = map_id
	refresh()
	return not active_map_id.is_empty()


func _get_map_locations() -> Array[Dictionary]:
	if data_registry != null and data_registry.has_method("get_map_locations"):
		return data_registry.get_map_locations(true)
	var raw_maps: Variant = data_registry.get("maps") if data_registry != null else {}
	var records: Array[Dictionary] = []
	if raw_maps is Dictionary:
		for map_id in raw_maps.keys():
			records.append(raw_maps[map_id])
	records.sort_custom(func(left: Dictionary, right: Dictionary) -> bool:
		return int(left.get("location_number", 0)) < int(right.get("location_number", 0))
	)
	return records


func _rebuild_location_list(locations: Array[Dictionary]) -> void:
	for child in location_list.get_children():
		child.queue_free()
	for location in locations:
		var button := Button.new()
		var number := int(location.get("location_number", 0))
		var name := String(location.get("name", ""))
		var lock_text := "Open" if _is_unlocked(location) else "Locked"
		button.text = "%02d  %s  /  %s" % [number, name, lock_text]
		button.tooltip_text = String(location.get("description", ""))
		button.pressed.connect(select_location.bind(String(location.get("map_id", ""))))
		GREENFIELD_UI_THEME.apply_tab_button(button, String(location.get("map_id", "")) == active_map_id)
		location_list.add_child(button)


func _rebuild_pins(locations: Array[Dictionary]) -> void:
	for child in pins_layer.get_children():
		child.queue_free()
	for location in locations:
		var pin := Button.new()
		pin.text = "%d" % int(location.get("location_number", 0))
		pin.tooltip_text = String(location.get("name", ""))
		pin.custom_minimum_size = Vector2(36.0, 36.0)
		pin.size = Vector2(36.0, 36.0)
		pin.position = _pin_position(location)
		pin.modulate = Color(1, 1, 1, 1) if _is_unlocked(location) else Color(0.62, 0.56, 0.48, 0.82)
		pin.pressed.connect(select_location.bind(String(location.get("map_id", ""))))
		GREENFIELD_UI_THEME.apply_button(pin, 15, 36.0)
		pins_layer.add_child(pin)


func _show_location(map_id: String) -> void:
	var location := _get_location(map_id)
	if location.is_empty():
		if selected_number_label != null:
			selected_number_label.text = "--"
		if selected_name_label != null:
			selected_name_label.text = "No location selected"
		if selected_state_label != null:
			selected_state_label.text = "State: -"
		if selected_description_label != null:
			selected_description_label.text = ""
		if selected_hint_label != null:
			selected_hint_label.text = ""
		if selected_npcs_label != null:
			selected_npcs_label.text = "NPCs: -"
		return
	var unlocked := _is_unlocked(location)
	if selected_number_label != null:
		selected_number_label.text = "Location %02d" % int(location.get("location_number", 0))
	if selected_name_label != null:
		selected_name_label.text = String(location.get("name", map_id))
	if selected_state_label != null:
		selected_state_label.text = "State: %s" % ("Unlocked" if unlocked else "Locked")
	if selected_description_label != null:
		selected_description_label.text = String(location.get("description", ""))
	if selected_hint_label != null:
		selected_hint_label.text = String(location.get("travel_hint", ""))
	if selected_npcs_label != null:
		selected_npcs_label.text = "NPCs: %s" % _format_npc_names(location)


func _get_location(map_id: String) -> Dictionary:
	if map_id.is_empty():
		return {}
	if data_registry != null and data_registry.has_method("get_map_location"):
		return data_registry.get_map_location(map_id)
	for location in _get_map_locations():
		if String(location.get("map_id", "")) == map_id:
			return location
	return {}


func _pin_position(location: Dictionary) -> Vector2:
	var raw_position: Variant = location.get("position", [0.5, 0.5])
	if not (raw_position is Array):
		return MAP_PIXEL_SIZE * 0.5 - Vector2(18.0, 18.0)
	var coordinates: Array = raw_position
	var x: float = clamp(float(coordinates[0]), 0.0, 1.0)
	var y: float = clamp(float(coordinates[1]), 0.0, 1.0)
	return Vector2(x * MAP_PIXEL_SIZE.x - 18.0, y * MAP_PIXEL_SIZE.y - 18.0)


func _is_unlocked(location: Dictionary) -> bool:
	if bool(location.get("unlocked", false)):
		return true
	var unlock_flag := String(location.get("unlock_flag", ""))
	if unlock_flag.is_empty() or game_state == null:
		return false
	if game_state.has_method("has_flag"):
		return bool(game_state.has_flag(unlock_flag))
	if game_state.has_method("get_save_data"):
		var save_data: Dictionary = game_state.get_save_data()
		var flags_value: Variant = save_data.get("flags", {})
		if flags_value is Dictionary:
			var flags: Dictionary = flags_value
			return bool(flags.get(unlock_flag, false))
	return false


func _format_npc_names(location: Dictionary) -> String:
	var raw_npcs: Variant = location.get("npc_ids", [])
	if not (raw_npcs is Array) or raw_npcs.is_empty():
		return "-"
	var names: Array[String] = []
	for raw_npc_id in raw_npcs:
		var npc_id := String(raw_npc_id)
		var npc_name := npc_id
		if data_registry != null and data_registry.has_method("get_npc"):
			var npc: Dictionary = data_registry.get_npc(npc_id)
			npc_name = String(npc.get("name", npc_id))
		names.append(npc_name)
	return ", ".join(names)


func _ensure_nodes() -> void:
	if panel == null:
		panel = get_node_or_null("Panel")
	if title_label == null:
		title_label = get_node_or_null("Panel/Content/Header/TitleLabel")
	if close_button == null:
		close_button = get_node_or_null("Panel/Content/Header/CloseButton")
	if map_panel == null:
		map_panel = get_node_or_null("Panel/Content/MainRow/MapPanel")
	if map_texture == null:
		map_texture = get_node_or_null("Panel/Content/MainRow/MapPanel/MapTexture")
	if pins_layer == null:
		pins_layer = get_node_or_null("Panel/Content/MainRow/MapPanel/Pins")
	if location_list == null:
		location_list = get_node_or_null("Panel/Content/MainRow/LocationList")
	if selected_number_label == null:
		selected_number_label = get_node_or_null("Panel/Content/MainRow/Details/SelectedNumberLabel")
	if selected_name_label == null:
		selected_name_label = get_node_or_null("Panel/Content/MainRow/Details/SelectedNameLabel")
	if selected_state_label == null:
		selected_state_label = get_node_or_null("Panel/Content/MainRow/Details/SelectedStateLabel")
	if selected_description_label == null:
		selected_description_label = get_node_or_null("Panel/Content/MainRow/Details/SelectedDescriptionLabel")
	if selected_hint_label == null:
		selected_hint_label = get_node_or_null("Panel/Content/MainRow/Details/SelectedHintLabel")
	if selected_npcs_label == null:
		selected_npcs_label = get_node_or_null("Panel/Content/MainRow/Details/SelectedNpcsLabel")


func _apply_greenfield_style() -> void:
	_ensure_nodes()
	if panel != null:
		panel.theme = GREENFIELD_THEME
		GREENFIELD_UI_THEME.apply_surface_panel(panel)
	if map_panel != null:
		GREENFIELD_UI_THEME.apply_surface_panel(map_panel)
	if map_texture != null:
		map_texture.texture = ASSET_PATHS.load_texture(ASSET_PATHS.UI_MAP_VILLAGE_PAPER)
	for label in [title_label, selected_number_label, selected_name_label]:
		var title := label as Label
		if title != null:
			GREENFIELD_UI_THEME.apply_title_label(title, 17)
	for label in [selected_state_label, selected_description_label, selected_hint_label, selected_npcs_label]:
		var body := label as Label
		if body != null:
			GREENFIELD_UI_THEME.apply_body_label(body, 14)
	if close_button != null:
		GREENFIELD_UI_THEME.apply_button(close_button, 14, 38.0)
		if not close_button.pressed.is_connected(close_map):
			close_button.pressed.connect(close_map)
