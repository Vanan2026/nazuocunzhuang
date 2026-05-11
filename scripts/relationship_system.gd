extends Node

signal relationship_milestone_reached(npc_id: String, level: int)

const RELATIONSHIP_LEVELS = {
    "陌生人": -50,
    "认识": 0,
    "友好": 30,
    "熟识": 60,
    "信赖": 80
}

var relationships: Dictionary = {}

func _ready() -> void:
    print("[Relationship] 关系系统初始化")

func init_relationship(npc_id: String, value: int = 0) -> void:
    relationships[npc_id] = value

func get_relationship_level(npc_id: String) -> String:
    var value = relationships.get(npc_id, 0)
    
    if value <= RELATIONSHIP_LEVELS["陌生人"]:
        return "陌生人"
    elif value <= RELATIONSHIP_LEVELS["认识"]:
        return "认识"
    elif value <= RELATIONSHIP_LEVELS["友好"]:
        return "友好"
    elif value <= RELATIONSHIP_LEVELS["熟识"]:
        return "熟识"
    else:
        return "信赖"

func modify_relationship(npc_id: String, delta: int) -> void:
    var old_value = relationships.get(npc_id, 0)
    var new_value = clamp(old_value + delta, -100, 100)
    relationships[npc_id] = new_value
    
    var old_level = get_relationship_level(npc_id)
    var new_level = get_relationship_level(npc_id)
    
    if old_level != new_level:
        emit_signal("relationship_milestone_reached", npc_id, new_value)
        print("[Relationship] ", npc_id, " 关系提升至: ", new_level)

func get_relationship_value(npc_id: String) -> int:
    return relationships.get(npc_id, 0)
