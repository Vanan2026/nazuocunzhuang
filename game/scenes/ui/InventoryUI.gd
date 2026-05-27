class_name InventoryUI
extends CanvasLayer

const GREENFIELD_THEME: Theme = preload("res://ui/theme/greenfield_theme.tres")
const GREENFIELD_UI_THEME := preload("res://game/scenes/ui/GreenfieldUITheme.gd")

const CATEGORIES: Array[Dictionary] = [
	{"id": "all", "label": "All"},
	{"id": "seed", "label": "Seeds"},
	{"id": "crop", "label": "Crops"},
	{"id": "food", "label": "Food"},
	{"id": "material", "label": "Materials"},
	{"id": "gift", "label": "Gifts"},
	{"id": "key", "label": "Key"},
]

@export var inventory_manager_path: NodePath
@export var data_registry_path: NodePath

@onready var panel: PanelContainer = get_node_or_null("Panel")
@onready var title_label: Label = get_node_or_null("Panel/Content/Header/TitleLabel")
@onready var capacity_label: Label = get_node_or_null("Panel/Content/Header/CapacityLabel")
@onready var category_tabs: HBoxContainer = get_node_or_null("Panel/Content/CategoryTabs")
@onready var item_grid: GridContainer = get_node_or_null("Panel/Content/MainRow/InventoryColumn/ItemGrid")
@onready var selected_name_label: Label = get_node_or_null("Panel/Content/MainRow/Details/SelectedNameLabel")
@onready var selected_description_label: Label = get_node_or_null("Panel/Content/MainRow/Details/SelectedDescriptionLabel")
@onready var selected_meta_label: Label = get_node_or_null("Panel/Content/MainRow/Details/SelectedMetaLabel")
@onready var amount_label: Label = get_node_or_null("Panel/Content/MainRow/Details/AmountRow/AmountLabel")
@onready var decrease_button: Button = get_node_or_null("Panel/Content/MainRow/Details/AmountRow/DecreaseButton")
@onready var increase_button: Button = get_node_or_null("Panel/Content/MainRow/Details/AmountRow/IncreaseButton")
@onready var clear_button: Button = get_node_or_null("Panel/Content/MainRow/Details/ActionRow/ClearButton")
@onready var seed_count_label: Label = get_node_or_null("Panel/Content/Footer/Summary/SeedCountLabel")
@onready var crop_count_label: Label = get_node_or_null("Panel/Content/Footer/Summary/CropCountLabel")

var inventory_manager: Node = null
var data_registry: Node = null
var active_category := "all"
var selected_item_id := ""
var selected_amount := 1


func _ready() -> void:
	if not inventory_manager_path.is_empty():
		inventory_manager = get_node_or_null(inventory_manager_path)
	if not data_registry_path.is_empty():
		data_registry = get_node_or_null(data_registry_path)
	bind_managers(inventory_manager, data_registry)
	_apply_greenfield_style()
	refresh()


func bind_managers(next_inventory_manager: Node, next_data_registry: Node) -> void:
	inventory_manager = next_inventory_manager
	data_registry = next_data_registry
	if inventory_manager != null:
		if inventory_manager.has_signal("inventory_changed") and not inventory_manager.inventory_changed.is_connected(_on_inventory_changed):
			inventory_manager.inventory_changed.connect(_on_inventory_changed)
		if inventory_manager.has_signal("selected_item_changed") and not inventory_manager.selected_item_changed.is_connected(_on_selected_item_changed):
			inventory_manager.selected_item_changed.connect(_on_selected_item_changed)
	if data_registry != null and data_registry.has_method("load_all_data") and not bool(data_registry.get("is_loaded")):
		data_registry.load_all_data()


func refresh() -> void:
	_ensure_nodes()
	if item_grid == null or selected_name_label == null or selected_description_label == null:
		return
	_apply_greenfield_style()
	_rebuild_category_tabs()
	_rebuild_item_grid()
	_show_selected_item(selected_item_id)
	_update_summary()


func select_item(item_id: String) -> bool:
	selected_item_id = item_id
	selected_amount = 1
	if inventory_manager != null and inventory_manager.has_method("set_selected_item") and _get_inventory_count(item_id) > 0:
		inventory_manager.set_selected_item(item_id)
	refresh()
	return not item_id.is_empty()


func use_selected_on(target: Node) -> bool:
	if target == null:
		return false
	if target.has_method("plant_selected_seed"):
		return bool(target.plant_selected_seed())
	return false


func set_active_category(category_id: String) -> void:
	active_category = category_id
	refresh()


func increase_amount() -> void:
	var max_count: int = max(_get_inventory_count(selected_item_id), 1)
	selected_amount = int(clamp(selected_amount + 1, 1, max_count))
	_show_selected_item(selected_item_id)


func decrease_amount() -> void:
	selected_amount = max(selected_amount - 1, 1)
	_show_selected_item(selected_item_id)


func _rebuild_category_tabs() -> void:
	if category_tabs == null:
		return
	for child in category_tabs.get_children():
		child.queue_free()
	for category in CATEGORIES:
		var category_id := String(category.get("id", ""))
		var button := Button.new()
		button.text = String(category.get("label", category_id))
		button.pressed.connect(set_active_category.bind(category_id))
		GREENFIELD_UI_THEME.apply_tab_button(button, category_id == active_category)
		category_tabs.add_child(button)


func _rebuild_item_grid() -> void:
	for child in item_grid.get_children():
		child.queue_free()
	var records := _get_inventory_records()
	for record in records:
		var item_id := String(record.get("item_id", ""))
		var count := _get_inventory_count(item_id)
		var button := Button.new()
		button.text = "%s\nx%d" % [String(record.get("name", item_id)), count]
		button.tooltip_text = String(record.get("description", ""))
		button.icon = _load_texture(String(record.get("icon", "")))
		button.expand_icon = true
		button.pressed.connect(_on_item_button_pressed.bind(item_id))
		GREENFIELD_UI_THEME.apply_item_slot(button, item_id == selected_item_id)
		item_grid.add_child(button)


func _get_inventory_records() -> Array[Dictionary]:
	var records: Array[Dictionary] = []
	var source: Dictionary = {}
	if data_registry != null:
		var raw_items: Variant = data_registry.get("items")
		if raw_items is Dictionary:
			source = raw_items
	if source.is_empty():
		var snapshot := _get_inventory_snapshot()
		for item_id in snapshot.keys():
			source[item_id] = _get_item_data(String(item_id))
	for item_id in source.keys():
		var record: Dictionary = source[item_id]
		if _matches_active_category(record):
			records.append(record)
	records.sort_custom(func(left: Dictionary, right: Dictionary) -> bool:
		return String(left.get("item_id", "")) < String(right.get("item_id", ""))
	)
	return records


func _matches_active_category(item_data: Dictionary) -> bool:
	if active_category == "all":
		return true
	var item_category := String(item_data.get("category", ""))
	if active_category == "gift":
		var tags: Array = item_data.get("tags", [])
		return tags.has("gift") or item_category in ["forage", "fish"]
	return item_category == active_category


func _on_item_button_pressed(item_id: String) -> void:
	select_item(item_id)


func _on_clear_selection() -> void:
	selected_item_id = ""
	selected_amount = 1
	if inventory_manager != null and inventory_manager.has_method("set_selected_item"):
		inventory_manager.set_selected_item("")
	refresh()


func _show_selected_item(item_id: String) -> void:
	if item_id.is_empty():
		selected_name_label.text = "No item selected"
		selected_description_label.text = "Select an item to apply to NPCs or a farm plot."
		if selected_meta_label != null:
			selected_meta_label.text = "Category: -   Value: -"
		if amount_label != null:
			amount_label.text = "1"
		return
	var item_data := _get_item_data(item_id)
	var count := _get_inventory_count(item_id)
	selected_name_label.text = String(item_data.get("name", item_id))
	selected_description_label.text = String(item_data.get("description", ""))
	if selected_meta_label != null:
		selected_meta_label.text = "Category: %s   Owned: %d   Value: %d" % [
			String(item_data.get("category", "-")).capitalize(),
			count,
			int(item_data.get("sell_price", 0)),
		]
	if amount_label != null:
		var max_count: int = max(count, 1)
		selected_amount = int(clamp(selected_amount, 1, max_count))
		amount_label.text = "%d" % selected_amount


func _update_summary() -> void:
	var snapshot := _get_inventory_snapshot()
	var owned_count := 0
	for count in snapshot.values():
		owned_count += int(count)
	if capacity_label != null:
		capacity_label.text = "%d / 60" % owned_count
	var seed_count := 0
	var crop_count := 0
	if inventory_manager != null and inventory_manager.has_method("get_items_by_category"):
		for count in inventory_manager.get_items_by_category("seed").values():
			seed_count += int(count)
		for count in inventory_manager.get_items_by_category("crop").values():
			crop_count += int(count)
	seed_count_label.text = "Seed: %d" % seed_count
	crop_count_label.text = "Crop: %d" % crop_count


func _get_item_data(item_id: String) -> Dictionary:
	if data_registry != null and data_registry.has_method("get_item"):
		var item_data: Dictionary = data_registry.get_item(item_id)
		if not item_data.is_empty():
			return item_data
	return {"item_id": item_id, "name": item_id, "description": "", "category": "", "icon": ""}


func _get_inventory_count(item_id: String) -> int:
	if item_id.is_empty() or inventory_manager == null or not inventory_manager.has_method("get_count"):
		return 0
	return int(inventory_manager.get_count(item_id))


func _get_inventory_snapshot() -> Dictionary:
	if inventory_manager != null and inventory_manager.has_method("get_inventory_snapshot"):
		return inventory_manager.get_inventory_snapshot()
	return {}


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


func _ensure_nodes() -> void:
	if panel == null:
		panel = get_node_or_null("Panel")
	if title_label == null:
		title_label = get_node_or_null("Panel/Content/Header/TitleLabel")
	if capacity_label == null:
		capacity_label = get_node_or_null("Panel/Content/Header/CapacityLabel")
	if category_tabs == null:
		category_tabs = get_node_or_null("Panel/Content/CategoryTabs")
	if item_grid == null:
		item_grid = get_node_or_null("Panel/Content/MainRow/InventoryColumn/ItemGrid")
	if selected_name_label == null:
		selected_name_label = get_node_or_null("Panel/Content/MainRow/Details/SelectedNameLabel")
	if selected_description_label == null:
		selected_description_label = get_node_or_null("Panel/Content/MainRow/Details/SelectedDescriptionLabel")
	if selected_meta_label == null:
		selected_meta_label = get_node_or_null("Panel/Content/MainRow/Details/SelectedMetaLabel")
	if amount_label == null:
		amount_label = get_node_or_null("Panel/Content/MainRow/Details/AmountRow/AmountLabel")
	if decrease_button == null:
		decrease_button = get_node_or_null("Panel/Content/MainRow/Details/AmountRow/DecreaseButton")
	if increase_button == null:
		increase_button = get_node_or_null("Panel/Content/MainRow/Details/AmountRow/IncreaseButton")
	if clear_button == null:
		clear_button = get_node_or_null("Panel/Content/MainRow/Details/ActionRow/ClearButton")
	if seed_count_label == null:
		seed_count_label = get_node_or_null("Panel/Content/Footer/Summary/SeedCountLabel")
	if crop_count_label == null:
		crop_count_label = get_node_or_null("Panel/Content/Footer/Summary/CropCountLabel")


func _apply_greenfield_style() -> void:
	_ensure_nodes()
	if panel != null:
		panel.theme = GREENFIELD_THEME
		GREENFIELD_UI_THEME.apply_surface_panel(panel)
	for label in [title_label, selected_name_label]:
		var title := label as Label
		if title != null:
			GREENFIELD_UI_THEME.apply_title_label(title, 17)
	for label in [capacity_label, selected_description_label, selected_meta_label, amount_label, seed_count_label, crop_count_label]:
		var body := label as Label
		if body != null:
			GREENFIELD_UI_THEME.apply_body_label(body, 14)
	if decrease_button != null:
		GREENFIELD_UI_THEME.apply_button(decrease_button, 16, 36.0)
		if not decrease_button.pressed.is_connected(decrease_amount):
			decrease_button.pressed.connect(decrease_amount)
	if increase_button != null:
		GREENFIELD_UI_THEME.apply_button(increase_button, 16, 36.0)
		if not increase_button.pressed.is_connected(increase_amount):
			increase_button.pressed.connect(increase_amount)
	if clear_button != null:
		GREENFIELD_UI_THEME.apply_button(clear_button, 13, 38.0)
		if not clear_button.pressed.is_connected(_on_clear_selection):
			clear_button.pressed.connect(_on_clear_selection)


func _on_inventory_changed() -> void:
	refresh()


func _on_selected_item_changed(item_id: String) -> void:
	selected_item_id = item_id
	refresh()
