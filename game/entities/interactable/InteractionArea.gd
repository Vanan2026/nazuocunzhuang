class_name InteractionArea
extends Area2D

signal interactable_entered(target: Node)
signal interactable_exited(target: Node)
signal nearest_interactable_changed(target: Node)

var interactables: Array[Node] = []
var nearest_interactable: Node = null


func _ready() -> void:
	area_entered.connect(_on_area_entered)
	area_exited.connect(_on_area_exited)
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)


func get_nearest_interactable() -> Node:
	_refresh_nearest()
	return nearest_interactable


func _on_area_entered(area: Area2D) -> void:
	_track_candidate(area)


func _on_area_exited(area: Area2D) -> void:
	_untrack_candidate(area)


func _on_body_entered(body: Node2D) -> void:
	_track_candidate(body)


func _on_body_exited(body: Node2D) -> void:
	_untrack_candidate(body)


func _track_candidate(candidate: Node) -> void:
	if candidate == owner or candidate == get_parent():
		return
	if not candidate.is_in_group("interactable"):
		return
	if not interactables.has(candidate):
		interactables.append(candidate)
		interactable_entered.emit(candidate)
	_refresh_nearest()


func _untrack_candidate(candidate: Node) -> void:
	if interactables.has(candidate):
		interactables.erase(candidate)
		interactable_exited.emit(candidate)
	_refresh_nearest()


func _refresh_nearest() -> void:
	var previous := nearest_interactable
	nearest_interactable = null
	var nearest_distance := INF
	for candidate in interactables:
		if not is_instance_valid(candidate):
			continue
		if not candidate is Node2D:
			continue
		if not _is_candidate_in_active_region(candidate):
			continue
		var distance := global_position.distance_squared_to((candidate as Node2D).global_position)
		if distance < nearest_distance:
			nearest_distance = distance
			nearest_interactable = candidate
	if previous != nearest_interactable:
		nearest_interactable_changed.emit(nearest_interactable)


func _is_candidate_in_active_region(candidate: Node) -> bool:
	var candidate_region_id := _get_candidate_region_id(candidate)
	if candidate_region_id.is_empty():
		return true
	var region_host := _get_region_host(candidate)
	if region_host == null or not region_host.has_method("get_active_region_id"):
		return true
	return candidate_region_id == String(region_host.call("get_active_region_id"))


func _get_candidate_region_id(candidate: Node) -> String:
	var node := candidate
	while node != null:
		if node.has_meta("outdoor_region_id"):
			return String(node.get_meta("outdoor_region_id"))
		if node.has_meta("region_id"):
			return String(node.get_meta("region_id"))
		node = node.get_parent()
	return ""


func _get_region_host(candidate: Node) -> Node:
	var node := candidate
	while node != null:
		if node.has_method("get_active_region_id"):
			return node
		node = node.get_parent()
	return null
