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
		var distance := global_position.distance_squared_to((candidate as Node2D).global_position)
		if distance < nearest_distance:
			nearest_distance = distance
			nearest_interactable = candidate
	if previous != nearest_interactable:
		nearest_interactable_changed.emit(nearest_interactable)
