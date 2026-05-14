extends Node

signal relationship_milestone_reached(npc_id: String, level: int)

const RELATIONSHIP_LEVELS = {
    "陌生人": -50,
    "认识": 0,
    "友好": 30,
    "熟悉": 60,
    "亲密": 80
}

var relationships: Dictionary = {}

func _ready() -> void:
    print("[Relationship] 关系系统初始化")

func init_relationship(npc_id: String, value: int = 0) -> void:
    relationships[npc_id] = value

func _get_level_for_value(value: int) -> String:
    if value <= RELATIONSHIP_LEVELS["陌生人"]:
        return "陌生人"
    elif value <= RELATIONSHIP_LEVELS["认识"]:
        return "认识"
    elif value <= RELATIONSHIP_LEVELS["友好"]:
        return "友好"
    elif value <= RELATIONSHIP_LEVELS["熟悉"]:
        return "熟悉"
    else:
        return "亲密"

func get_relationship_level(npc_id: String) -> String:
    var value = relationships.get(npc_id, 0)
    return _get_level_for_value(value)

func modify_relationship(npc_id: String, delta: int) -> void:
    var old_value = relationships.get(npc_id, 0)
    var old_level = _get_level_for_value(old_value)

    var new_value = clamp(old_value + delta, -100, 100)
    relationships[npc_id] = new_value

    var new_level = _get_level_for_value(new_value)

    if old_level != new_level:
        emit_signal("relationship_milestone_reached", npc_id, new_value)
        print("[Relationship] ", npc_id, " 关系提升至 ", new_level)

func get_relationship_value(npc_id: String) -> int:
    return relationships.get(npc_id, 0)