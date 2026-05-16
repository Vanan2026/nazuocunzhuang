class_name InventoryManager
extends Node

signal inventory_changed()
signal item_added(item_id: String, count: int)
signal item_removed(item_id: String, count: int)
signal selected_item_changed(item_id: String)

var items: Dictionary = {}
var tools: Dictionary = {}
var key_items: Dictionary = {}
var selected_item_id: String = ""


func add_item(item_id: String, count: int = 1) -> void:
	if item_id.is_empty() or count <= 0:
		return
	items[item_id] = get_count(item_id) + count
	item_added.emit(item_id, count)
	inventory_changed.emit()


func remove_item(item_id: String, count: int = 1) -> bool:
	if not has_item(item_id, count):
		return false
	items[item_id] = get_count(item_id) - count
	if items[item_id] <= 0:
		items.erase(item_id)
		if selected_item_id == item_id:
			set_selected_item("")
	item_removed.emit(item_id, count)
	inventory_changed.emit()
	return true


func has_item(item_id: String, count: int = 1) -> bool:
	return get_count(item_id) >= count


func get_count(item_id: String) -> int:
	return int(items.get(item_id, 0))


func set_selected_item(item_id: String) -> bool:
	if not item_id.is_empty() and not has_item(item_id, 1):
		return false
	if selected_item_id == item_id:
		return true
	selected_item_id = item_id
	selected_item_changed.emit(selected_item_id)
	return true


func get_selected_item_id() -> String:
	return selected_item_id


func get_inventory_snapshot() -> Dictionary:
	return items.duplicate(true)


func get_items_by_category(category: String) -> Dictionary:
	var result: Dictionary = {}
	for item_id in items.keys():
		if _matches_category(String(item_id), category):
			result[item_id] = items[item_id]
	return result


func _matches_category(item_id: String, category: String) -> bool:
	match category:
		"seed":
			return item_id.begins_with("seed_")
		"crop":
			return item_id.begins_with("crop_") or item_id == "persimmon"
		"food":
			return item_id.begins_with("food_") or item_id == "rice"
		"material":
			return item_id == "wood" or item_id == "stone"
		_:
			return false
