class_name DialogueBox
extends CanvasLayer

const GreenfieldUITheme := preload("res://game/scenes/ui/GreenfieldUITheme.gd")

signal dialogue_closed()

@onready var panel: PanelContainer = get_node_or_null("Panel")
@onready var content: HBoxContainer = get_node_or_null("Panel/Content")
@onready var portrait: TextureRect = get_node_or_null("Panel/Content/Portrait")
@onready var text_column: VBoxContainer = get_node_or_null("Panel/Content/TextColumn")
@onready var speaker_label: Label = get_node_or_null("Panel/Content/TextColumn/SpeakerLabel")
@onready var line_label: Label = get_node_or_null("Panel/Content/TextColumn/LineLabel")
@onready var option_row: HBoxContainer = get_node_or_null("Panel/Content/TextColumn/OptionRow")
@onready var gift_selection_panel: PanelContainer = get_node_or_null("GiftSelection")
@onready var gift_title_label: Label = get_node_or_null("GiftSelection/Content/TitleLabel")
@onready var gift_grid: GridContainer = get_node_or_null("GiftSelection/Content/GiftGrid")
@onready var relationship_feedback_panel: PanelContainer = get_node_or_null("RelationshipFeedback")
@onready var feedback_title_label: Label = get_node_or_null("RelationshipFeedback/Content/FeedbackTitleLabel")
@onready var feedback_line_label: Label = get_node_or_null("RelationshipFeedback/Content/FeedbackLineLabel")
@onready var feedback_delta_label: Label = get_node_or_null("RelationshipFeedback/Content/FeedbackDeltaLabel")

@export var inventory_manager_path: NodePath
@export var data_registry_path: NodePath
@export var relationship_manager_path: NodePath

var dialogue: Dictionary = {}
var line_index: int = 0
var speaker_names: Dictionary = {}
var inventory_manager: Node = null
var data_registry: Node = null
var relationship_manager: Node = null


func _ready() -> void:
	visible = false
	if not inventory_manager_path.is_empty():
		inventory_manager = get_node_or_null(inventory_manager_path)
	if not data_registry_path.is_empty():
		data_registry = get_node_or_null(data_registry_path)
	if not relationship_manager_path.is_empty():
		relationship_manager = get_node_or_null(relationship_manager_path)
	_apply_visual_theme()
	_set_gift_selection_visible(false)
	_set_feedback_visible(false)


func bind_managers(next_inventory_manager: Node, next_data_registry: Node, next_relationship_manager: Node = null) -> void:
	inventory_manager = next_inventory_manager
	data_registry = next_data_registry
	relationship_manager = next_relationship_manager
	if data_registry != null and data_registry.has_method("load_all_data") and not bool(data_registry.get("is_loaded")):
		data_registry.load_all_data()


func show_dialogue(next_dialogue: Dictionary, display_context: Dictionary = {}) -> void:
	dialogue = next_dialogue.duplicate(true)
	line_index = 0
	speaker_names.clear()
	if display_context.has("npc_name"):
		speaker_names[String(dialogue.get("npc_id", ""))] = String(display_context["npc_name"])
	_set_portrait(String(display_context.get("portrait", "")))
	visible = true
	_show_current_line()
	var gift_context := _get_dialogue_gift_context()
	_show_gift_feedback(gift_context)


func advance() -> bool:
	var lines: Array = dialogue.get("lines", [])
	if line_index + 1 >= lines.size():
		close()
		return false
	line_index += 1
	_show_current_line()
	return true


func close() -> void:
	visible = false
	dialogue.clear()
	line_index = 0
	_set_gift_selection_visible(false)
	_set_feedback_visible(false)
	dialogue_closed.emit()


func show_gift_selection(npc_data: Dictionary = {}) -> void:
	_ensure_nodes()
	if gift_grid == null:
		return
	_set_gift_selection_visible(true)
	for child in gift_grid.get_children():
		child.queue_free()
	var records := _get_available_gift_records()
	for record in records:
		var item_id := String(record.get("item_id", ""))
		var count := _get_inventory_count(item_id)
		var button := Button.new()
		button.text = "%s\nx%d" % [String(record.get("name", item_id)), count]
		button.tooltip_text = String(record.get("description", ""))
		button.icon = _load_texture(String(record.get("icon", "")))
		button.expand_icon = true
		button.pressed.connect(_on_gift_button_pressed.bind(item_id))
		GreenfieldUITheme.apply_item_slot(button, false)
		gift_grid.add_child(button)
	if records.is_empty():
		var empty_label := Label.new()
		empty_label.text = "No suitable gifts in the bag."
		GreenfieldUITheme.apply_hint_label(empty_label, 14)
		gift_grid.add_child(empty_label)


func hide_gift_selection() -> void:
	_set_gift_selection_visible(false)


func _show_current_line() -> void:
	_ensure_nodes()
	var lines: Array = dialogue.get("lines", [])
	if lines.is_empty() or line_index >= lines.size():
		close()
		return
	var line: Dictionary = lines[line_index]
	var speaker_id := String(line.get("speaker", dialogue.get("npc_id", "")))
	if speaker_label != null:
		speaker_label.text = String(speaker_names.get(speaker_id, speaker_id))
	if line_label != null:
		line_label.text = String(line.get("text", ""))


func _show_gift_feedback(gift_context: Dictionary) -> void:
	_ensure_nodes()
	if gift_context.is_empty():
		_set_feedback_visible(false)
		return
	_set_feedback_visible(true)
	var item_name := String(gift_context.get("item_name", gift_context.get("item_id", "")))
	var delta := int(gift_context.get("delta", 0))
	if feedback_title_label != null:
		feedback_title_label.text = "Relationship Feedback"
	if feedback_line_label != null:
		if bool(gift_context.get("already_gifted", false)):
			feedback_line_label.text = "Already gifted today: %s" % item_name
		else:
			feedback_line_label.text = String(gift_context.get("feedback_text", "Gift accepted: %s" % item_name))
	if feedback_delta_label != null:
		if delta > 0:
			feedback_delta_label.text = "+%d heart warmth" % delta
		elif delta < 0:
			feedback_delta_label.text = "%d heart warmth" % delta
		else:
			feedback_delta_label.text = "No relationship change"


func _get_dialogue_gift_context() -> Dictionary:
	var context_value: Variant = dialogue.get("context", {})
	if not (context_value is Dictionary):
		return {}
	var context: Dictionary = context_value
	var gift_context_value: Variant = context.get("gift_context", {})
	if gift_context_value is Dictionary:
		return gift_context_value
	return {}


func _get_available_gift_records() -> Array[Dictionary]:
	var records: Array[Dictionary] = []
	if inventory_manager == null or not inventory_manager.has_method("get_inventory_snapshot"):
		return records
	var snapshot: Dictionary = inventory_manager.get_inventory_snapshot()
	for item_id in snapshot.keys():
		var count := int(snapshot[item_id])
		if count <= 0:
			continue
		var item_data := _get_item_data(String(item_id))
		if _is_gift_candidate(item_data):
			records.append(item_data)
	records.sort_custom(func(left: Dictionary, right: Dictionary) -> bool:
		return String(left.get("item_id", "")) < String(right.get("item_id", ""))
	)
	return records


func _is_gift_candidate(item_data: Dictionary) -> bool:
	var category := String(item_data.get("category", ""))
	if category in ["food", "crop", "forage", "fish"]:
		return true
	var raw_tags: Variant = item_data.get("tags", [])
	if raw_tags is Array:
		var tags: Array = raw_tags
		return tags.has("gift") or tags.has("flower") or tags.has("tea")
	return false


func _get_item_data(item_id: String) -> Dictionary:
	if data_registry != null and data_registry.has_method("get_item"):
		var item_data: Dictionary = data_registry.get_item(item_id)
		if not item_data.is_empty():
			return item_data
	return {"item_id": item_id, "name": item_id, "description": "", "category": "", "icon": "", "tags": []}


func _get_inventory_count(item_id: String) -> int:
	if inventory_manager == null or not inventory_manager.has_method("get_count"):
		return 0
	return int(inventory_manager.get_count(item_id))


func _on_gift_button_pressed(item_id: String) -> void:
	if inventory_manager != null and inventory_manager.has_method("set_selected_item"):
		inventory_manager.set_selected_item(item_id)
	_set_gift_selection_visible(false)


func _set_gift_selection_visible(next_visible: bool) -> void:
	if gift_selection_panel != null:
		gift_selection_panel.visible = next_visible


func _set_feedback_visible(next_visible: bool) -> void:
	if relationship_feedback_panel != null:
		relationship_feedback_panel.visible = next_visible


func _set_portrait(path: String) -> void:
	_ensure_nodes()
	if portrait == null:
		return
	portrait.texture = _load_texture(path)
	portrait.visible = portrait.texture != null


func _ensure_nodes() -> void:
	if panel == null:
		panel = get_node_or_null("Panel")
	if content == null:
		content = get_node_or_null("Panel/Content")
	if portrait == null:
		portrait = get_node_or_null("Panel/Content/Portrait")
	if text_column == null:
		text_column = get_node_or_null("Panel/Content/TextColumn")
	if speaker_label == null:
		speaker_label = get_node_or_null("Panel/Content/TextColumn/SpeakerLabel")
	if line_label == null:
		line_label = get_node_or_null("Panel/Content/TextColumn/LineLabel")
	if option_row == null:
		option_row = get_node_or_null("Panel/Content/TextColumn/OptionRow")
	if gift_selection_panel == null:
		gift_selection_panel = get_node_or_null("GiftSelection")
	if gift_title_label == null:
		gift_title_label = get_node_or_null("GiftSelection/Content/TitleLabel")
	if gift_grid == null:
		gift_grid = get_node_or_null("GiftSelection/Content/GiftGrid")
	if relationship_feedback_panel == null:
		relationship_feedback_panel = get_node_or_null("RelationshipFeedback")
	if feedback_title_label == null:
		feedback_title_label = get_node_or_null("RelationshipFeedback/Content/FeedbackTitleLabel")
	if feedback_line_label == null:
		feedback_line_label = get_node_or_null("RelationshipFeedback/Content/FeedbackLineLabel")
	if feedback_delta_label == null:
		feedback_delta_label = get_node_or_null("RelationshipFeedback/Content/FeedbackDeltaLabel")


func _apply_visual_theme() -> void:
	_ensure_nodes()
	GreenfieldUITheme.apply_dialogue_panel(panel)
	GreenfieldUITheme.apply_title_label(speaker_label, 15)
	GreenfieldUITheme.apply_body_label(line_label, 15)
	GreenfieldUITheme.apply_hint_label(line_label, 15)
	GreenfieldUITheme.apply_surface_panel(gift_selection_panel)
	GreenfieldUITheme.apply_surface_panel(relationship_feedback_panel)
	GreenfieldUITheme.apply_title_label(gift_title_label, 15)
	GreenfieldUITheme.apply_title_label(feedback_title_label, 15)
	GreenfieldUITheme.apply_body_label(feedback_line_label, 14)
	GreenfieldUITheme.apply_hint_label(feedback_delta_label, 14)
	if content != null:
		content.add_theme_constant_override("separation", 12)
	if text_column != null:
		text_column.add_theme_constant_override("separation", 4)
	if option_row != null:
		option_row.add_theme_constant_override("separation", 8)
		for child in option_row.get_children():
			var button := child as Button
			if button != null:
				GreenfieldUITheme.apply_button(button, 14, 38.0)


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
