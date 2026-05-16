class_name InventoryUI
extends CanvasLayer

@export var inventory_manager_path: NodePath
@export var data_registry_path: NodePath

@onready var item_grid: GridContainer = get_node_or_null("Panel/Content/ItemGrid")
@onready var selected_name_label: Label = get_node_or_null("Panel/Content/Details/SelectedNameLabel")
@onready var selected_description_label: Label = get_node_or_null("Panel/Content/Details/SelectedDescriptionLabel")
@onready var seed_count_label: Label = get_node_or_null("Panel/Content/Summary/SeedCountLabel")
@onready var crop_count_label: Label = get_node_or_null("Panel/Content/Summary/CropCountLabel")

var inventory_manager: Node = null
var data_registry: Node = null


func _ready() -> void:
	if not inventory_manager_path.is_empty():
		inventory_manager = get_node_or_null(inventory_manager_path)
	if not data_registry_path.is_empty():
		data_registry = get_node_or_null(data_registry_path)
	bind_managers(inventory_manager, data_registry)
	refresh()


func bind_managers(next_inventory_manager: Node, next_data_registry: Node) -> void:
	inventory_manager = next_inventory_manager
	data_registry = next_data_registry
	if inventory_manager != null:
		if inventory_manager.has_signal("inventory_changed") and not inventory_manager.inventory_changed.is_connected(_on_inventory_changed):
			inventory_manager.inventory_changed.connect(_on_inventory_changed)
		if inventory_manager.has_signal("selected_item_changed") and not inventory_manager.selected_item_changed.is_connected(_on_selected_item_changed):
			inventory_manager.selected_item_changed.connect(_on_selected_item_changed)


func refresh() -> void:
	_ensure_nodes()
	if item_grid == null or selected_name_label == null or selected_description_label == null or seed_count_label == null or crop_count_label == null:
		return
	_clear_item_grid()

	var snapshot: Dictionary = {}
	if inventory_manager != null and inventory_manager.has_method("get_inventory_snapshot"):
		snapshot = inventory_manager.get_inventory_snapshot()
	var item_ids := snapshot.keys()
	item_ids.sort()
	for item_id in item_ids:
		var button := Button.new()
		button.text = "%s x%d" % [_get_item_name(String(item_id)), int(snapshot[item_id])]
		button.pressed.connect(_on_item_button_pressed.bind(String(item_id)))
		item_grid.add_child(button)

	var clear_button := Button.new()
	clear_button.text = "Clear Selection"
	clear_button.pressed.connect(_on_clear_selection)
	item_grid.add_child(clear_button)

	var selected_item_id := ""
	if inventory_manager != null and inventory_manager.has_method("get_selected_item_id"):
		selected_item_id = String(inventory_manager.get_selected_item_id())
	_show_selected_item(selected_item_id)
	_update_summary()


func select_item(item_id: String) -> bool:
	if inventory_manager == null or not inventory_manager.has_method("set_selected_item"):
		return false
	var changed: bool = inventory_manager.set_selected_item(item_id)
	refresh()
	return changed


func _on_item_button_pressed(item_id: String) -> void:
	select_item(item_id)


func _on_clear_selection() -> void:
	select_item("")


func use_selected_on(target: Node) -> bool:
	if target == null:
		return false
	if target.has_method("plant_selected_seed"):
		return bool(target.plant_selected_seed())
	return false


func _show_selected_item(item_id: String) -> void:
	if item_id.is_empty():
		selected_name_label.text = "No item selected"
		selected_description_label.text = "Select an item to apply to NPCs or a farm plot."
		return
	var item_data := _get_item_data(item_id)
	selected_name_label.text = String(item_data.get("name", item_id))
	selected_description_label.text = String(item_data.get("description", ""))


func _update_summary() -> void:
	var seed_count := 0
	var crop_count := 0
	if inventory_manager != null:
		if inventory_manager.has_method("get_items_by_category"):
			for count in inventory_manager.get_items_by_category("seed").values():
				seed_count += int(count)
			for count in inventory_manager.get_items_by_category("crop").values():
				crop_count += int(count)
	seed_count_label.text = "Seed: %d" % seed_count
	crop_count_label.text = "Crop: %d" % crop_count


func _get_item_name(item_id: String) -> String:
	var item_data := _get_item_data(item_id)
	return String(item_data.get("name", item_id))


func _get_item_data(item_id: String) -> Dictionary:
	if data_registry != null and data_registry.has_method("get_item"):
		var item_data: Dictionary = data_registry.get_item(item_id)
		if not item_data.is_empty():
			return item_data
	return {"name": item_id, "description": ""}


func _clear_item_grid() -> void:
	for child in item_grid.get_children():
		child.queue_free()


func _ensure_nodes() -> void:
	if item_grid == null:
		item_grid = get_node_or_null("Panel/Content/ItemGrid")
	if selected_name_label == null:
		selected_name_label = get_node_or_null("Panel/Content/Details/SelectedNameLabel")
	if selected_description_label == null:
		selected_description_label = get_node_or_null("Panel/Content/Details/SelectedDescriptionLabel")
	if seed_count_label == null:
		seed_count_label = get_node_or_null("Panel/Content/Summary/SeedCountLabel")
	if crop_count_label == null:
		crop_count_label = get_node_or_null("Panel/Content/Summary/CropCountLabel")


func _on_inventory_changed() -> void:
	refresh()


func _on_selected_item_changed(_item_id: String) -> void:
	refresh()
