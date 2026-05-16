class_name EventBus
extends Node

signal day_started(date_info: Dictionary)
signal day_ended(date_info: Dictionary)
signal time_block_changed(block: String)
signal weather_changed(weather_id: String)
signal inventory_changed()
signal item_added(item_id: String, count: int)
signal relationship_changed(npc_id: String, value: int)
signal dialogue_started(npc_id: String)
signal dialogue_finished(npc_id: String)
signal restoration_completed(restoration_id: String)
signal narrative_event_triggered(event_id: String)


func emit_day_started(date_info: Dictionary) -> void:
	day_started.emit(date_info)


func emit_day_ended(date_info: Dictionary) -> void:
	day_ended.emit(date_info)
