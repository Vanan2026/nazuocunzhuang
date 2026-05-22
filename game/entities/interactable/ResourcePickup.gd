class_name ResourcePickup
extends "res://game/entities/interactable/Interactable.gd"

@export var item_id: String = ""
@export var count: int = 1
@export var inventory_manager_path: NodePath
@export var consume_on_pickup: bool = true

var picked: bool = false


func on_interact(interactor: Node) -> void:
	if consume_on_pickup and picked:
		return
	super.on_interact(interactor)
	var inventory_manager := _get_inventory_manager()
	if inventory_manager == null or not inventory_manager.has_method("add_item"):
		push_warning("ResourcePickup missing InventoryManager for %s" % item_id)
		return
	if item_id.is_empty() or count <= 0:
		push_warning("ResourcePickup has invalid item config.")
		return
	inventory_manager.add_item(item_id, count)
	picked = true
	if consume_on_pickup:
		visible = false
		set_deferred("monitoring", false)
		_disable_collision_shapes()


func get_interaction_hint() -> String:
	if consume_on_pickup and picked:
		return ""
	return interaction_hint


func _get_inventory_manager() -> Node:
	var linked := get_node_or_null(inventory_manager_path)
	if linked != null:
		return linked
	var parent_node := get_parent()
	while parent_node != null:
		var fallback := parent_node.get_node_or_null("InventoryManager")
		if fallback != null:
			return fallback
		parent_node = parent_node.get_parent()
	return null


func _disable_collision_shapes() -> void:
	for child in get_children():
		if child is CollisionShape2D:
			child.set_deferred("disabled", true)
