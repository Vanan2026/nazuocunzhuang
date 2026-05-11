extends Node

signal game_initialized
signal day_changed(day: int)
signal season_changed(season: String)

var current_day: int = 1
var current_season: String = "spring"
var time_of_day: float = 0.0

var TimeSystem: Node
var EventSystem: Node

func _ready() -> void:
    initialize_systems()

func initialize_systems() -> void:
    if has_node("/root/TimeSystem"):
        TimeSystem = get_node("/root/TimeSystem")
    else:
        var ts = Node.new()
        ts.set_script(load("res://scripts/time_system.gd"))
        ts.name = "TimeSystem"
        add_child(ts)
        TimeSystem = ts
    
    if has_node("/root/EventSystem"):
        EventSystem = get_node("/root/EventSystem")
    else:
        var es = Node.new()
        es.set_script(load("res://scripts/event_system.gd"))
        es.name = "EventSystem"
        add_child(es)
        EventSystem = es
    
    emit_signal("game_initialized")
