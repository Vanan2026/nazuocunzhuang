extends CharacterBody2D

@export var npc_id: String = ""
@export var display_name: String = "村民"

var current_dialogue_index: int = 0
var relationship: int = 0
var is_interacting: bool = false

signal npc_interact_requested(npc_id: String)
signal npc_interaction_complete(npc_id: String)

func _ready() -> void:
    add_to_group("npc")
    add_to_group("interactable")

func on_interact(interactor: Node) -> void:
    if is_interacting:
        return
    
    is_interacting = true
    emit_signal("npc_interact_requested", npc_id)
    
    if has_node("/root/NPCManager"):
        get_node("/root/NPCManager").interact(npc_id)
    
    await get_tree().create_timer(0.5).timeout
    is_interacting = false
    emit_signal("npc_interaction_complete", npc_id)

func get_interaction_hint() -> String:
    return "与 " + display_name + " 交谈"

func set_relationship(value: int) -> void:
    relationship = clamp(value, -100, 100)
