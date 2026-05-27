class_name HomeArea
extends Node2D

@export_file("*.json") var interaction_points_path := "res://assets/scenes/home_area/scene_home_area_interaction_points.json"
@export var region_id := "home_area"

@onready var interaction_points: Node2D = get_node_or_null("InteractionPoints")
@onready var player_spawn_point: Marker2D = get_node_or_null("PlayerSpawnPoint")


func _ready() -> void:
	set_meta("region_id", region_id)
	if interaction_points != null:
		interaction_points.set_meta("region_id", region_id)


func get_registered_interaction_ids() -> Array[String]:
	var ids: Array[String] = []
	if interaction_points == null:
		return ids
	for child in interaction_points.get_children():
		if child.has_method("get_interaction_hint"):
			ids.append(String(child.get("interactable_id")))
		else:
			var value: String = String(child.get("interactable_id"))
			if not value.is_empty():
				ids.append(value)
	ids.sort()
	return ids


func get_player_spawn_position() -> Vector2:
	if player_spawn_point == null:
		return Vector2.ZERO
	return player_spawn_point.position


func load_interaction_points_data() -> Dictionary:
	if not FileAccess.file_exists(interaction_points_path):
		return {}
	var text := FileAccess.get_file_as_string(interaction_points_path)
	var parsed: Variant = JSON.parse_string(text)
	if parsed is Dictionary:
		return parsed
	return {}
