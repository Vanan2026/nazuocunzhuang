class_name DataRegistry
extends Node

signal data_loaded()
signal data_validation_failed(message: String)

const DATA_FILES: Dictionary = {
	"items": {"path": "res://game/data/items.json", "id_key": "item_id"},
	"crops": {"path": "res://game/data/crops.json", "id_key": "crop_id"},
	"npcs": {"path": "res://game/data/npcs.json", "id_key": "npc_id"},
	"dialogues": {"path": "res://game/data/dialogues.json", "id_key": "dialogue_id"},
	"rumors": {"path": "res://game/data/rumors.json", "id_key": "rumor_id"},
	"recipes": {"path": "res://game/data/recipes.json", "id_key": "recipe_id"},
	"restoration_targets": {"path": "res://game/data/restoration_targets.json", "id_key": "restoration_id"},
}

const VALID_SEASONS: Array[String] = ["spring", "summer", "autumn", "winter"]
const FORBIDDEN_FIELD_TERMS: Array[String] = [
	"com" + "bat",
	"mon" + "ster",
	"dam" + "age",
	"wea" + "pon",
	"h" + "p",
	"ki" + "ll",
	"lo" + "ot",
]

var items: Dictionary = {}
var crops: Dictionary = {}
var npcs: Dictionary = {}
var dialogues: Dictionary = {}
var rumors: Dictionary = {}
var recipes: Dictionary = {}
var restoration_targets: Dictionary = {}
var validation_errors: Array[String] = []
var is_loaded: bool = false


func _ready() -> void:
	if load_all_data():
		validate_all_data()


func load_all_data() -> bool:
	_clear_data()
	for collection_name in DATA_FILES.keys():
		var config: Dictionary = DATA_FILES[collection_name]
		var records: Variant = _read_json_array(config["path"])
		if not records is Array:
			return false
		var indexed: Dictionary = _index_records(records, config["id_key"], collection_name)
		if not validation_errors.is_empty():
			return false
		_set_collection(collection_name, indexed)
	is_loaded = true
	return true


func validate_all_data() -> bool:
	validation_errors.clear()
	_validate_items()
	_validate_crops()
	_validate_npcs()
	_validate_dialogues()
	_validate_rumors()
	_validate_recipes()
	_validate_restoration_targets()

	if validation_errors.is_empty():
		print("DataRegistry validation OK: %d items, %d crops, %d npcs, %d dialogues, %d rumors, %d recipes, %d restorations" % [
			items.size(),
			crops.size(),
			npcs.size(),
			dialogues.size(),
			rumors.size(),
			recipes.size(),
			restoration_targets.size(),
		])
		data_loaded.emit()
		return true

	var message := "DataRegistry validation failed: %s" % "; ".join(validation_errors)
	push_error(message)
	data_validation_failed.emit(message)
	return false


func get_item(item_id: String) -> Dictionary:
	return items.get(item_id, {})


func get_crop(crop_id: String) -> Dictionary:
	return crops.get(crop_id, {})


func get_npc(npc_id: String) -> Dictionary:
	return npcs.get(npc_id, {})


func get_recipe(recipe_id: String) -> Dictionary:
	return recipes.get(recipe_id, {})


func get_dialogue(dialogue_id: String) -> Dictionary:
	return dialogues.get(dialogue_id, {})


func get_rumor(rumor_id: String) -> Dictionary:
	return rumors.get(rumor_id, {})


func get_restoration(restoration_id: String) -> Dictionary:
	return restoration_targets.get(restoration_id, {})


func has_item(item_id: String) -> bool:
	return items.has(item_id)


func _clear_data() -> void:
	items.clear()
	crops.clear()
	npcs.clear()
	dialogues.clear()
	rumors.clear()
	recipes.clear()
	restoration_targets.clear()
	validation_errors.clear()
	is_loaded = false


func _read_json_array(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		_add_error("missing data file: %s" % path)
		return null
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_add_error("could not open data file: %s" % path)
		return null
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if not parsed is Array:
		_add_error("%s must contain a JSON array" % path)
		return null
	return parsed


func _index_records(records: Array, id_key: String, collection_name: String) -> Dictionary:
	var indexed: Dictionary = {}
	for index in records.size():
		var record: Variant = records[index]
		if not record is Dictionary:
			_add_error("%s[%d] must be a dictionary" % [collection_name, index])
			continue
		if not record.has(id_key):
			_add_error("%s[%d] missing id field %s" % [collection_name, index, id_key])
			continue
		var record_id := String(record[id_key])
		if record_id.is_empty():
			_add_error("%s[%d] has empty %s" % [collection_name, index, id_key])
			continue
		if indexed.has(record_id):
			_add_error("%s has duplicate id %s" % [collection_name, record_id])
			continue
		indexed[record_id] = record
	return indexed


func _set_collection(collection_name: String, indexed: Dictionary) -> void:
	match collection_name:
		"items":
			items = indexed
		"crops":
			crops = indexed
		"npcs":
			npcs = indexed
		"dialogues":
			dialogues = indexed
		"rumors":
			rumors = indexed
		"recipes":
			recipes = indexed
		"restoration_targets":
			restoration_targets = indexed


func _validate_items() -> void:
	for item_id in items.keys():
		var item: Dictionary = items[item_id]
		_require_fields(item, ["item_id", "name", "category", "description", "stackable", "max_stack", "sell_price", "tags", "icon"], "item %s" % item_id)
		_require_non_empty_name(item, "item %s" % item_id)
		_reject_forbidden_fields(item, "item %s" % item_id)


func _validate_crops() -> void:
	for crop_id in crops.keys():
		var crop: Dictionary = crops[crop_id]
		_require_fields(crop, ["crop_id", "seed_item_id", "harvest_item_id", "name", "allowed_seasons", "grow_days", "regrow_days", "water_required", "stages", "stage_sprites"], "crop %s" % crop_id)
		_require_non_empty_name(crop, "crop %s" % crop_id)
		_reject_forbidden_fields(crop, "crop %s" % crop_id)
		if not items.has(crop.get("seed_item_id", "")):
			_add_error("crop %s references missing seed item %s" % [crop_id, crop.get("seed_item_id", "")])
		if not items.has(crop.get("harvest_item_id", "")):
			_add_error("crop %s references missing harvest item %s" % [crop_id, crop.get("harvest_item_id", "")])
		for season in crop.get("allowed_seasons", []):
			if not VALID_SEASONS.has(String(season)):
				_add_error("crop %s has invalid season %s" % [crop_id, season])


func _validate_npcs() -> void:
	for npc_id in npcs.keys():
		var npc: Dictionary = npcs[npc_id]
		_require_fields(npc, ["npc_id", "name", "role", "birthday", "home_scene", "default_scene", "portrait", "likes", "dislikes", "schedule_id", "heart_events"], "npc %s" % npc_id)
		_require_non_empty_name(npc, "npc %s" % npc_id)
		_reject_forbidden_fields(npc, "npc %s" % npc_id)
		var birthday: Dictionary = npc.get("birthday", {})
		if not VALID_SEASONS.has(String(birthday.get("season", ""))):
			_add_error("npc %s has invalid birthday season" % npc_id)
		var day := int(birthday.get("day", 0))
		if day < 1 or day > 28:
			_add_error("npc %s has invalid birthday day %d" % [npc_id, day])


func _validate_dialogues() -> void:
	for dialogue_id in dialogues.keys():
		var dialogue: Dictionary = dialogues[dialogue_id]
		_require_fields(dialogue, ["dialogue_id", "npc_id", "type", "priority", "conditions", "lines", "sets_flags"], "dialogue %s" % dialogue_id)
		_reject_forbidden_fields(dialogue, "dialogue %s" % dialogue_id)
		if not npcs.has(dialogue.get("npc_id", "")):
			_add_error("dialogue %s references missing npc %s" % [dialogue_id, dialogue.get("npc_id", "")])
		if dialogue.get("lines", []).is_empty():
			_add_error("dialogue %s has no lines" % dialogue_id)


func _validate_rumors() -> void:
	for rumor_id in rumors.keys():
		var rumor: Dictionary = rumors[rumor_id]
		_require_fields(rumor, ["rumor_id", "source", "priority", "conditions", "text", "sets_flags"], "rumor %s" % rumor_id)
		_reject_forbidden_fields(rumor, "rumor %s" % rumor_id)
		var source := String(rumor.get("source", ""))
		if source not in ["mailbox", "bulletin", "npc"]:
			_add_error("rumor %s has invalid source %s" % [rumor_id, source])
		if String(rumor.get("text", "")).strip_edges().is_empty():
			_add_error("rumor %s has empty text" % rumor_id)
		if not (rumor.get("conditions", {}) is Dictionary):
			_add_error("rumor %s conditions must be a dictionary" % rumor_id)
		if not (rumor.get("sets_flags", []) is Array):
			_add_error("rumor %s sets_flags must be an array" % rumor_id)


func _validate_recipes() -> void:
	for recipe_id in recipes.keys():
		var recipe: Dictionary = recipes[recipe_id]
		_require_fields(recipe, ["recipe_id", "name", "ingredients", "result", "energy_restore", "tags", "unlock_condition"], "recipe %s" % recipe_id)
		_require_non_empty_name(recipe, "recipe %s" % recipe_id)
		_reject_forbidden_fields(recipe, "recipe %s" % recipe_id)
		for ingredient in recipe.get("ingredients", []):
			var item_id := String(ingredient.get("item_id", ""))
			if not items.has(item_id):
				_add_error("recipe %s references missing ingredient %s" % [recipe_id, item_id])
		var result_item_id := String(recipe.get("result", {}).get("item_id", ""))
		if not items.has(result_item_id):
			_add_error("recipe %s references missing result item %s" % [recipe_id, result_item_id])


func _validate_restoration_targets() -> void:
	for restoration_id in restoration_targets.keys():
		var target: Dictionary = restoration_targets[restoration_id]
		_require_fields(target, ["restoration_id", "name", "description", "required_items", "required_money", "required_flags", "unlocks", "visual_states"], "restoration %s" % restoration_id)
		_require_non_empty_name(target, "restoration %s" % restoration_id)
		_reject_forbidden_fields(target, "restoration %s" % restoration_id)
		for required_item in target.get("required_items", []):
			var item_id := String(required_item.get("item_id", ""))
			if not items.has(item_id):
				_add_error("restoration %s references missing item %s" % [restoration_id, item_id])


func _require_fields(record: Dictionary, fields: Array[String], context: String) -> void:
	for field in fields:
		if not record.has(field):
			_add_error("%s missing required field %s" % [context, field])


func _require_non_empty_name(record: Dictionary, context: String) -> void:
	if String(record.get("name", "")).strip_edges().is_empty():
		_add_error("%s has empty name" % context)


func _reject_forbidden_fields(value: Variant, context: String) -> void:
	if value is Dictionary:
		for key in value.keys():
			var lowered := String(key).to_lower()
			for term in FORBIDDEN_FIELD_TERMS:
				if lowered.contains(term):
					_add_error("%s contains forbidden field %s" % [context, key])
			_reject_forbidden_fields(value[key], "%s.%s" % [context, key])
	elif value is Array:
		for child in value:
			_reject_forbidden_fields(child, context)


func _add_error(message: String) -> void:
	validation_errors.append(message)
	data_validation_failed.emit(message)
