class_name NPC
extends "res://game/entities/interactable/Interactable.gd"

@export var npc_id: String = ""
@export var sprite_texture_path: String = ""
@export var portrait_texture_path: String = ""
@export var inventory_manager_path: NodePath
@export var data_registry_path: NodePath
@export var dialogue_manager_path: NodePath
@export var relationship_manager_path: NodePath
@export var dialogue_box_path: NodePath
@export var time_manager_path: NodePath
@export var weather_manager_path: NodePath
@export var birthday_gift_multiplier: int = 2

@onready var sprite: Sprite2D = get_node_or_null("Sprite2D")
@onready var name_label: Label = get_node_or_null("NameLabel")

var npc_data: Dictionary = {}


func _ready() -> void:
	super._ready()
	if interactable_id.is_empty() and not npc_id.is_empty():
		interactable_id = npc_id
	if interaction_hint.is_empty():
		interaction_hint = "Talk"
	var registry := _get_data_registry()
	if registry != null and registry.has_method("get_npc") and not npc_id.is_empty():
		configure_from_data(registry.get_npc(npc_id))
	_apply_visual()


func configure_from_data(data: Dictionary) -> void:
	npc_data = data.duplicate(true)
	if npc_data.is_empty():
		return
	npc_id = String(npc_data.get("npc_id", npc_id))
	interactable_id = npc_id
	display_name = String(npc_data.get("name", display_name))
	portrait_texture_path = String(npc_data.get("portrait", portrait_texture_path))
	if sprite_texture_path.is_empty():
		sprite_texture_path = "res://assets/art/characters/npc/npc_%s_idle_down_128.png" % npc_id
	_apply_visual()


func on_interact(interactor: Node) -> void:
	super.on_interact(interactor)
	var dialogue_manager := _get_dialogue_manager()
	var relationship_manager := _get_relationship_manager()
	var inventory_manager := _get_inventory_manager()

	if _try_gift_interaction(inventory_manager, relationship_manager, dialogue_manager):
		return

	if dialogue_manager == null or not dialogue_manager.has_method("get_dialogue"):
		return

	var context := _build_dialogue_context()
	var dialogue: Dictionary = dialogue_manager.get_dialogue(npc_id, context)
	dialogue_manager.start_dialogue(npc_id, dialogue)
	_apply_first_talk_relationship(relationship_manager)
	var dialogue_box := _get_dialogue_box()
	if dialogue_box != null and dialogue_box.has_method("show_dialogue"):
		dialogue_box.show_dialogue(dialogue, {
			"npc_name": display_name,
			"portrait": portrait_texture_path,
		})


func get_interaction_hint() -> String:
	if display_name.is_empty():
		return "Talk"
	return "Talk to %s" % display_name


func _build_dialogue_context() -> Dictionary:
	var context := {
		"season": "spring",
		"weather": "sunny",
		"time_block": "morning",
	}
	var time_manager := _get_time_manager()
	if time_manager != null and time_manager.has_method("get_date_info"):
		var date_info: Dictionary = time_manager.get_date_info()
		context["season"] = String(date_info.get("season", context["season"]))
		context["time_block"] = String(date_info.get("block", context["time_block"]))
	var weather_manager := _get_weather_manager()
	if weather_manager != null and weather_manager.has_method("get_weather_info"):
		var weather_info: Dictionary = weather_manager.get_weather_info()
		context["weather"] = String(weather_info.get("today", context["weather"]))
	return context


func _try_gift_interaction(inventory_manager: Node, relationship_manager: Node, dialogue_manager: Node) -> bool:
	if inventory_manager == null or dialogue_manager == null:
		return false
	if not inventory_manager.has_method("get_selected_item_id"):
		return false
	var selected_item_id := _get_selected_item_id(inventory_manager)
	if selected_item_id.is_empty():
		return false
	if not inventory_manager.has_method("has_item") or not inventory_manager.has_item(selected_item_id, 1):
		return false
	var data_registry := _get_data_registry()
	if data_registry == null or not data_registry.has_method("get_item"):
		return false
	var item_data: Dictionary = data_registry.get_item(selected_item_id)
	if item_data.is_empty():
		return false
	var gift_context: Dictionary = _evaluate_gift(selected_item_id, item_data, inventory_manager, relationship_manager)
	if gift_context.is_empty():
		return false

	var dialogue: Dictionary = _build_gift_dialogue(item_data, gift_context)
	dialogue_manager.start_dialogue(npc_id, dialogue)
	var dialogue_box := _get_dialogue_box()
	if dialogue_box != null and dialogue_box.has_method("show_dialogue"):
		dialogue_box.show_dialogue(dialogue, {
			"npc_name": display_name,
			"portrait": portrait_texture_path,
		})
	return true


func _evaluate_gift(item_id: String, item_data: Dictionary, inventory_manager: Node, relationship_manager: Node) -> Dictionary:
	var item_name := String(item_data.get("name", item_id))
	if relationship_manager == null or not relationship_manager.has_method("has_gifted_today") or not relationship_manager.has_method("mark_gifted_today"):
		return {}
	if relationship_manager.has_gifted_today(npc_id):
		return {
			"item_id": item_id,
			"item_name": item_name,
			"delta": 0,
			"already_gifted": true,
		}

	if not inventory_manager.has_method("remove_item"):
		return {}
	if not inventory_manager.remove_item(item_id, 1):
		return {}

	var likes := _as_string_array(npc_data.get("likes", []))
	var dislikes := _as_string_array(npc_data.get("dislikes", []))
	var item_tags := _as_string_array(item_data.get("tags", []))
	var match_count := _count_matching_tags(item_tags, likes)
	var disfavor_count := _count_matching_tags(item_tags, dislikes)

	var delta := 0
	if match_count > 0:
		delta += 1 + match_count
	elif disfavor_count > 0:
		delta -= 1 + disfavor_count

	if delta > 0 and _is_npc_birthday_today():
		delta *= max(1, birthday_gift_multiplier)

	if relationship_manager.has_method("add_relationship"):
		relationship_manager.add_relationship(npc_id, delta)
	relationship_manager.mark_gifted_today(npc_id)

	return {
		"item_id": item_id,
		"item_name": item_name,
		"delta": delta,
		"match_count": match_count,
		"disfavor_count": disfavor_count,
		"already_gifted": false,
	}


func _build_gift_dialogue(item_data: Dictionary, gift_context: Dictionary) -> Dictionary:
	var item_name := String(item_data.get("name", String(gift_context.get("item_id", ""))))
	var delta := int(gift_context.get("delta", 0))
	var line := ""
	var line_text_suffix := "The gift was accepted."
	if bool(gift_context.get("already_gifted", false)):
		line = "%s says: You already gave a gift today." % display_name
	elif delta > 0:
		line = "%s smiles and takes the %s." % [display_name, item_name]
		line_text_suffix = "Our relationship feels warmer."
	elif delta < 0:
		line = "%s accepts the %s, but looks a little hesitant." % [display_name, item_name]
		line_text_suffix = "The relationship feels a little colder."
	else:
		line = "%s thanks you for the %s." % [display_name, item_name]
		line_text_suffix = "It is a kind little gift."
	line += " " + line_text_suffix

	return {
		"dialogue_id": "%s_gift_runtime" % npc_id,
		"npc_id": npc_id,
		"type": "event",
		"priority": 99,
		"conditions": {},
		"lines": [{"speaker": npc_id, "text": line}],
		"sets_flags": [],
		"context": {"gift_context": gift_context.duplicate(true)},
	}


func _get_selected_item_id(inventory_manager: Node) -> String:
	if inventory_manager == null or not inventory_manager.has_method("get_selected_item_id"):
		return ""
	return String(inventory_manager.get_selected_item_id())


func _count_matching_tags(candidate_tags: Array, target_tags: Array) -> int:
	var count := 0
	var normalized_target := _as_string_array(target_tags)
	for tag in candidate_tags:
		var lower_tag := String(tag).to_lower()
		if normalized_target.has(lower_tag):
			count += 1
	return count


func _as_string_array(value: Variant) -> Array:
	var result: Array = []
	if not (value is Array):
		return result
	for item in value:
		var item_text := String(item).strip_edges().to_lower()
		if not item_text.is_empty():
			result.append(item_text)
	return result


func _is_npc_birthday_today() -> bool:
	if npc_data.is_empty():
		return false
	var birthday: Dictionary = {}
	if npc_data.has("birthday") and npc_data["birthday"] is Dictionary:
		birthday = npc_data["birthday"]
	if birthday.is_empty():
		return false
	var birthday_season := String(birthday.get("season", ""))
	var birthday_day := int(birthday.get("day", 0))
	if birthday_season.is_empty() or birthday_day <= 0:
		return false
	var date_manager := _get_time_manager()
	if date_manager == null or not date_manager.has_method("get_date_info"):
		return false
	var date_info: Dictionary = date_manager.get_date_info()
	var today_season := String(date_info.get("season", ""))
	var today_day := int(date_info.get("day", int(date_info.get("day_of_season", 0))))
	return birthday_season == today_season and birthday_day == today_day


func _apply_first_talk_relationship(relationship_manager: Node) -> void:
	if relationship_manager == null:
		return
	if relationship_manager.has_method("has_talked_today") and relationship_manager.has_method("mark_talked_today") and relationship_manager.has_talked_today(npc_id):
		return
	if relationship_manager.has_method("add_relationship"):
		relationship_manager.add_relationship(npc_id, 1)
	if relationship_manager.has_method("mark_talked_today"):
		relationship_manager.mark_talked_today(npc_id)


func _apply_visual() -> void:
	if name_label == null:
		name_label = get_node_or_null("NameLabel")
	if name_label != null:
		name_label.text = display_name
	if sprite == null:
		sprite = get_node_or_null("Sprite2D")
	if sprite == null or sprite_texture_path.is_empty():
		return
	sprite.texture = _load_texture(sprite_texture_path)


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


func _get_data_registry() -> Node:
	return _get_linked_node(data_registry_path, "DataRegistry")


func _get_inventory_manager() -> Node:
	return _get_linked_node(inventory_manager_path, "InventoryManager")


func _get_dialogue_manager() -> Node:
	return _get_linked_node(dialogue_manager_path, "DialogueManager")


func _get_relationship_manager() -> Node:
	return _get_linked_node(relationship_manager_path, "RelationshipManager")

func _get_dialogue_box() -> Node:
	return _get_linked_node(dialogue_box_path, "DialogueBox")


func _get_time_manager() -> Node:
	return _get_linked_node(time_manager_path, "TimeManager")


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
