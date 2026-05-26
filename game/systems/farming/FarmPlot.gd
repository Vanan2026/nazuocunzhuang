class_name FarmPlot
extends "res://game/entities/interactable/Interactable.gd"

signal plot_changed(plot_index: int, state_name: String)
signal crop_planted(plot_index: int, crop_id: String)
signal crop_harvested(plot_index: int, item_id: String, count: int)

enum PlotState {
	EMPTY,
	TILLED,
	PLANTED,
	WATERED,
	READY,
}

@export var plot_index: int = 0
@export var default_crop_id: String = "turnip_spring"
@export var data_registry_path: NodePath
@export var inventory_manager_path: NodePath
@export var weather_manager_path: NodePath

var state: PlotState = PlotState.EMPTY
var crop_id: String = ""
var seed_item_id: String = ""
var harvest_item_id: String = ""
var growth_days: int = 0
var is_watered: bool = false

@onready var state_marker: Polygon2D = get_node_or_null("StateMarker")
@onready var crop_sprite: Sprite2D = get_node_or_null("CropSprite")
@onready var crop_status_cue: Label = get_node_or_null("CropStatusCue")


func _ready() -> void:
	super._ready()
	if interactable_id.is_empty():
		interactable_id = "farm_plot_%d" % plot_index
	display_name = "农田 %d" % (plot_index + 1)
	_update_visual()


func till() -> bool:
	if state != PlotState.EMPTY:
		return false
	state = PlotState.TILLED
	is_watered = false
	growth_days = 0
	_emit_changed()
	return true


func plant_seed(requested_seed_item_id: String = "") -> bool:
	if state != PlotState.TILLED:
		return false
	var registry := _get_data_registry()
	var inventory := _get_inventory_manager()
	if registry == null or inventory == null:
		return false
	var resolved_seed_id := requested_seed_item_id
	if resolved_seed_id.is_empty():
		resolved_seed_id = _find_available_seed_id(registry, inventory)
	if resolved_seed_id.is_empty() or not inventory.has_item(resolved_seed_id, 1):
		return false
	var resolved_crop_id := _find_crop_id_for_seed(registry, resolved_seed_id)
	if resolved_crop_id.is_empty():
		return false
	var crop_data: Dictionary = registry.get_crop(resolved_crop_id)
	if crop_data.is_empty():
		return false
	if not inventory.remove_item(resolved_seed_id, 1):
		return false

	crop_id = resolved_crop_id
	seed_item_id = resolved_seed_id
	harvest_item_id = String(crop_data.get("harvest_item_id", ""))
	growth_days = 0
	is_watered = false
	state = PlotState.PLANTED
	crop_planted.emit(plot_index, crop_id)
	_emit_changed()
	return true


func plant_selected_seed() -> bool:
	var inventory := _get_inventory_manager()
	if inventory == null or not inventory.has_method("get_selected_item_id"):
		return false
	var selected_item_id := String(inventory.get_selected_item_id())
	if selected_item_id.is_empty():
		return false
	return plant_seed(selected_item_id)


func water() -> bool:
	if state != PlotState.PLANTED and state != PlotState.WATERED:
		return false
	is_watered = true
	state = PlotState.WATERED
	_emit_changed()
	return true


func advance_day(auto_water: bool = false) -> void:
	if state != PlotState.PLANTED and state != PlotState.WATERED:
		return
	if auto_water:
		is_watered = true
	if is_watered:
		growth_days += 1
	var crop_data := _get_current_crop_data()
	var grow_days := int(crop_data.get("grow_days", 1))
	if growth_days >= grow_days:
		state = PlotState.READY
		is_watered = false
	else:
		state = PlotState.PLANTED
		is_watered = false
	_emit_changed()


func harvest() -> bool:
	if state != PlotState.READY:
		return false
	var inventory := _get_inventory_manager()
	if inventory == null or harvest_item_id.is_empty():
		return false
	inventory.add_item(harvest_item_id, 1)
	crop_harvested.emit(plot_index, harvest_item_id, 1)

	var crop_data := _get_current_crop_data()
	var regrow_days := int(crop_data.get("regrow_days", 0))
	if regrow_days > 0:
		var grow_days := int(crop_data.get("grow_days", regrow_days))
		growth_days = max(grow_days - regrow_days, 0)
		state = PlotState.PLANTED
		is_watered = false
	else:
		_reset_to_empty()
	_emit_changed()
	return true


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	match state:
		PlotState.EMPTY:
			till()
		PlotState.TILLED:
			if not plant_selected_seed():
				plant_seed()
		PlotState.PLANTED:
			water()
		PlotState.WATERED:
			pass
		PlotState.READY:
			harvest()


func get_interaction_hint() -> String:
	match state:
		PlotState.EMPTY:
			return "按 E 整理土地"
		PlotState.TILLED:
			return "按 E 播种"
		PlotState.PLANTED:
			return "按 E 浇水"
		PlotState.WATERED:
			return "已经浇过水"
		PlotState.READY:
			return "按 E 收获"
		_:
			return interaction_hint


func get_state_name() -> String:
	match state:
		PlotState.EMPTY:
			return "empty"
		PlotState.TILLED:
			return "tilled"
		PlotState.PLANTED:
			return "planted"
		PlotState.WATERED:
			return "watered"
		PlotState.READY:
			return "ready"
		_:
			return "unknown"


func get_save_data() -> Dictionary:
	return {
		"plot_index": plot_index,
		"state": get_state_name(),
		"crop_id": crop_id,
		"seed_item_id": seed_item_id,
		"harvest_item_id": harvest_item_id,
		"growth_days": growth_days,
		"is_watered": is_watered,
	}


func apply_save_data(data: Dictionary) -> void:
	if data.is_empty():
		_reset_to_empty()
		_emit_changed()
		return
	plot_index = int(data.get("plot_index", plot_index))
	state = _state_from_name(String(data.get("state", get_state_name())))
	crop_id = String(data.get("crop_id", ""))
	seed_item_id = String(data.get("seed_item_id", ""))
	harvest_item_id = String(data.get("harvest_item_id", ""))
	growth_days = max(int(data.get("growth_days", 0)), 0)
	is_watered = bool(data.get("is_watered", state == PlotState.WATERED))
	if state == PlotState.EMPTY:
		crop_id = ""
		seed_item_id = ""
		harvest_item_id = ""
		growth_days = 0
		is_watered = false
	_emit_changed()


func get_stage_sprite_path() -> String:
	if crop_id.is_empty():
		return ""
	var crop_data := _get_current_crop_data()
	var stage_sprites: Array = crop_data.get("stage_sprites", [])
	if stage_sprites.is_empty():
		return ""
	var stage_index := _get_stage_index(stage_sprites.size())
	return String(stage_sprites[stage_index])


func get_crop_display_name() -> String:
	var crop_data := _get_current_crop_data()
	var crop_name := String(crop_data.get("name", "")).strip_edges()
	if not crop_name.is_empty():
		return crop_name
	if crop_id.is_empty():
		return ""
	return crop_id.replace("_spring", "").replace("_summer", "").replace("_autumn", "").replace("_winter", "").replace("_", " ").capitalize()


func get_crop_status_text() -> String:
	if crop_id.is_empty():
		return ""
	var display_name := get_crop_display_name()
	if display_name.is_empty():
		return ""
	return "%s %s" % [display_name, _crop_status_label()]


func _reset_to_empty() -> void:
	state = PlotState.EMPTY
	crop_id = ""
	seed_item_id = ""
	harvest_item_id = ""
	growth_days = 0
	is_watered = false


func _state_from_name(state_name: String) -> PlotState:
	match state_name:
		"tilled":
			return PlotState.TILLED
		"planted":
			return PlotState.PLANTED
		"watered":
			return PlotState.WATERED
		"ready":
			return PlotState.READY
		_:
			return PlotState.EMPTY


func _emit_changed() -> void:
	_update_visual()
	plot_changed.emit(plot_index, get_state_name())


func _update_visual() -> void:
	if state_marker == null:
		state_marker = get_node_or_null("StateMarker")
	if state_marker == null:
		return
	match state:
		PlotState.EMPTY:
			state_marker.color = Color(0.47, 0.36, 0.25, 1.0)
		PlotState.TILLED:
			state_marker.color = Color(0.35, 0.25, 0.18, 1.0)
		PlotState.PLANTED:
			state_marker.color = Color(0.42, 0.50, 0.28, 1.0)
		PlotState.WATERED:
			state_marker.color = Color(0.34, 0.43, 0.38, 1.0)
		PlotState.READY:
			state_marker.color = Color(0.68, 0.58, 0.30, 1.0)
	_update_crop_sprite()
	_update_crop_status_cue()


func _update_crop_sprite() -> void:
	if crop_sprite == null:
		crop_sprite = get_node_or_null("CropSprite")
	if crop_sprite == null:
		return
	var sprite_path := get_stage_sprite_path()
	crop_sprite.visible = not sprite_path.is_empty()
	if sprite_path.is_empty():
		crop_sprite.texture = null
		return
	crop_sprite.texture = _load_texture(sprite_path)


func _update_crop_status_cue() -> void:
	if crop_status_cue == null:
		crop_status_cue = get_node_or_null("CropStatusCue")
	if crop_status_cue == null:
		return
	var text := get_crop_status_text()
	crop_status_cue.visible = not text.is_empty()
	crop_status_cue.text = get_crop_status_text()


func _crop_status_label() -> String:
	match state:
		PlotState.PLANTED:
			return "seeded"
		PlotState.WATERED:
			return "watered"
		PlotState.READY:
			return "ready"
		_:
			return ""


func _get_stage_index(stage_count: int) -> int:
	if stage_count <= 1:
		return 0
	if state == PlotState.READY:
		return stage_count - 1
	var crop_data: Dictionary = _get_current_crop_data()
	var grow_days: int = max(int(crop_data.get("grow_days", 1)), 1)
	var ratio: float = clamp(float(growth_days) / float(grow_days), 0.0, 1.0)
	return clamp(int(floor(ratio * float(stage_count - 1))), 0, stage_count - 1)


func _load_texture(path: String) -> Texture2D:
	if path.is_empty():
		return null
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	if FileAccess.file_exists(path):
		var image := Image.load_from_file(path)
		if image != null and not image.is_empty():
			return ImageTexture.create_from_image(image)
	return null


func _get_current_crop_data() -> Dictionary:
	var registry := _get_data_registry()
	if registry == null or crop_id.is_empty():
		return {}
	return registry.get_crop(crop_id)


func _find_available_seed_id(registry: Node, inventory: Node) -> String:
	var default_crop: Dictionary = registry.get_crop(default_crop_id)
	var default_seed := String(default_crop.get("seed_item_id", ""))
	if not default_seed.is_empty() and inventory.has_item(default_seed, 1):
		return default_seed
	for candidate_crop_id in registry.crops.keys():
		var crop_data: Dictionary = registry.crops[candidate_crop_id]
		var candidate_seed := String(crop_data.get("seed_item_id", ""))
		if inventory.has_item(candidate_seed, 1):
			return candidate_seed
	return ""


func _find_crop_id_for_seed(registry: Node, requested_seed_item_id: String) -> String:
	for candidate_crop_id in registry.crops.keys():
		var crop_data: Dictionary = registry.crops[candidate_crop_id]
		if String(crop_data.get("seed_item_id", "")) == requested_seed_item_id:
			return String(candidate_crop_id)
	return ""


func _get_data_registry() -> Node:
	return _get_linked_node(data_registry_path, "DataRegistry")


func _get_inventory_manager() -> Node:
	return _get_linked_node(inventory_manager_path, "InventoryManager")


func _get_weather_manager() -> Node:
	return _get_linked_node(weather_manager_path, "WeatherManager")


func _get_linked_node(path: NodePath, fallback_name: String) -> Node:
	var linked := get_node_or_null(path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null(fallback_name)
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	return null
